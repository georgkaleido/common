# Standard import
import os
import subprocess
import torch
from collections import OrderedDict
import argparse
from datetime import datetime
import logging
import shutil
import re

# Local imports
from bin.dataset_fetch import fetch_dataset
from qi_auto.utilities import Bucket, run_bash


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


def strip_checkpoint(path, skip=6, only_state_dict=True, rename=None):
    # Load
    checkpoint = torch.load(path)
    # Strip away 'model.'
    checkpoint['state_dict'] = OrderedDict(
        [(k[skip:], v) for k, v in dict(checkpoint['state_dict']).items()])
    # Keep only state_dict
    if only_state_dict:
        checkpoint_new = OrderedDict()
        checkpoint_new['state_dict'] = checkpoint['state_dict']
        checkpoint = checkpoint_new

    # Save stripped checkpoint
    torch.save(checkpoint, path)

    # Optionally rename it
    if rename:
        os.rename(path, rename)


def main():

    parser = argparse.ArgumentParser(description='Train trimap.')
    parser.add_argument('--danni_user', required=True, type=str, help='danni user.')
    parser.add_argument('--danni_token', required=True, type=str, help='danni password.')
    parser.add_argument('--skip_existing', action="store_true", help='Skip steps when the file already exists on the bucket')
    args = parser.parse_args()

    # Make string with today's date
    str_today = datetime.today().strftime('%Y-%m-%d')
    str_this_month = datetime.today().strftime('%Y-%m')

    # Initialize Bucket
    bucket_name = "kaleido-train-checkpoints"
    bucket = Bucket(bucket_name)

    # Get job.yaml
    logging.info("Get job.yaml")
    # List folders in bucket
    qi_bucket_main_path = os.path.join("removebg", "trimap-qi-auto")
    dir_list = bucket.list_folders(qi_bucket_main_path, str_this_month)
    # Remove entries which are not in the format YYYY-MM-DD_qi
    new_dir_list = []
    pattern = r"^\d\d\d\d-\d\d-\d\d\_qi$"
    for directory in dir_list:
        result = re.match(pattern, directory)
        if result:
            new_dir_list.append(directory)
    dir_list = new_dir_list

    if not dir_list:
        raise RuntimeError(f"No entry found matching the pattern 'YYYY-MM-DD_qi', in bucket: {qi_bucket_main_path}")

    # Sort list
    dir_list.sort()

    # Get most recent
    qi_bucket_name = dir_list[-1]
    qi_bucket_path = os.path.join(qi_bucket_main_path, qi_bucket_name)

    # Grab best checkpoint
    logging.info("Grab best checkpoint")
    best_checkpoint_blob_path = os.path.join(qi_bucket_path, "best.ckpt")
    best_checkpoint_local_path = "./best.ckpt"
    normalized_best_checkpoint_local_path = "./trimap513-deeplab-res2net.pth.tar"
    normalized_best_checkpoint_blob_path = "removebg/trimap-qi-auto/candidate_best/trimap513-deeplab-res2net.pth.tar"

    if args.skip_existing and bucket.exists(normalized_best_checkpoint_blob_path):
        logging.info(f"Skipping this step because file already exists: {normalized_best_checkpoint_blob_path}")
    else:
        if not os.path.exists("./best.ckpt"):
            bucket.download(blob_path=best_checkpoint_blob_path,
                            local_path=best_checkpoint_local_path)
        else:
            logging.info(f"Local best checkpoint already exists : {best_checkpoint_local_path}")

        # Strip away the useless parts of the checkpoint
        logging.info(f"Strip {best_checkpoint_local_path}")
        logging.info(f"Rename {best_checkpoint_local_path} to {normalized_best_checkpoint_local_path}")
        strip_checkpoint(path=best_checkpoint_local_path,
                         rename=normalized_best_checkpoint_local_path)

        # Upload it to a bucket
        bucket.upload(local_path=normalized_best_checkpoint_local_path,
                      blob_path=normalized_best_checkpoint_blob_path)

    if args.skip_existing and os.path.exists(normalized_best_checkpoint_local_path):
        logging.info(f"Local best checkpoint already exists : {normalized_best_checkpoint_local_path}")
    else:
        bucket.download(blob_path=normalized_best_checkpoint_blob_path,
                        local_path=normalized_best_checkpoint_local_path)

    # Grab test dataset metadata
    test_dataset_metadata_blob_path = os.path.join(qi_bucket_path, "trimap_dataset_test.json")
    test_dataset_metadata_local_path = "./trimap_dataset_test.json"
    bucket.download(test_dataset_metadata_blob_path, test_dataset_metadata_local_path)

    # Download test dataset
    logging.info("Download test dataset")
    test_dataset_local_path = "./test_dataset"
    os.makedirs(test_dataset_local_path, exist_ok=True)
    fetch_dataset(test_dataset_metadata_local_path, test_dataset_local_path)

    # Download kaleido-models checkpoints
    kaleido_models_local_path = "./kaleido-models"
    kaleido_models_blob_path = os.path.join(qi_bucket_main_path, "latest_best")
    bucket.download_directory(kaleido_models_blob_path, kaleido_models_local_path)

    # Perform test with old model
    logging.info("Perform test with old model")
    str_command_line = f"python -m bin.removebg-demo {test_dataset_local_path} "\
                       f"--path_networks {kaleido_models_local_path} "\
                       f"--path_parent test --evaluate --evaluate_file old.json --caption old --skip"
    run_bash(str_command_line)

    # Copy kaleido-models and replace old trimap weights with new ones
    kaleido_models_new_local_path = f"{kaleido_models_local_path}_new"
    shutil.copytree(kaleido_models_local_path, kaleido_models_new_local_path)

    # Switch new model in kaleido-models
    kaleido_models_new_trimap_model_path = os.path.join(kaleido_models_new_local_path, "trimap513-deeplab-res2net.pth.tar")
    os.rename(normalized_best_checkpoint_local_path, kaleido_models_new_trimap_model_path)

    # Perform test with new model
    logging.info("Perform test with new model")
    str_command_line = f"python -m bin.removebg-demo {test_dataset_local_path} "\
                       f"--path_networks {kaleido_models_new_local_path} "\
                       f"--path_parent test --evaluate --evaluate_file new.json --caption new --skip"
    run_bash(str_command_line)

    # Launch evaluation
    logging.info("Launch evaluation")
    evaluation_local_path = os.path.join(".", f"{str_today}_eval")
    str_command_line = f"python -m eval.plot_results old.json new.json "\
                       f"--out {evaluation_local_path} "\
                       f" --samples 25 --minimum_samples 10"
    run_bash(str_command_line)

    # Zip evaluation results
    logging.info("Zipping evaluation")
    zip_path = f"{evaluation_local_path}.zip"
    zip_name = os.path.basename(evaluation_local_path)
    zip_filename = f"{zip_name}.zip"
    print(f"Create archive {zip_filename}")
    shutil.make_archive(zip_name, 'zip', root_dir=evaluation_local_path)
    print(f"Move archive {zip_filename} to {zip_path}")
    os.rename(zip_filename, zip_path)

    # Upload evaluation
    evaluation_blob_path = os.path.join(qi_bucket_path, zip_filename)
    bucket.upload(zip_path, evaluation_blob_path)


if __name__ == '__main__':
    main()
