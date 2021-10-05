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
import glob

# Local imports
from bin.dataset_fetch import fetch_dataset
from qi_auto.utilities import Bucket, run_bash, compute_days_between_dates


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
    parser.add_argument('--max_day_delta',
                        default=9*7,
                        type=int,
                        help=f"Evaluate trainings with less than this maximum number of days since training start. Default {9*7}")
    args = parser.parse_args()

    assert "GITHUB_AUTH_TOKEN" in os.environ, "Could not find environment variable GITHUB_AUTH_TOKEN"

    # Make string with today's date
    str_today = datetime.today().strftime('%Y-%m-%d')

    # Initialize Bucket
    bucket_name = "kaleido-train-checkpoints"
    bucket = Bucket(bucket_name)

    # List folders in bucket
    qi_bucket_main_path = os.path.join("removebg", "trimap-qi-auto")
    dir_list = bucket.list_folders(qi_bucket_main_path, "202")
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
    dir_list.sort(reverse=True)

    # Get latest qi training
    latest_qi_bucket_name = dir_list[0]
    latest_qi_bucket_path = os.path.join(qi_bucket_main_path, latest_qi_bucket_name)
    logging.info(f"Latest qi training: {latest_qi_bucket_path}")
    # Grab test dataset metadata
    test_dataset_metadata_blob_path = os.path.join(latest_qi_bucket_path, "trimap_dataset_test.json")
    test_dataset_metadata_local_path = "./trimap_dataset_test.json"
    bucket.download(test_dataset_metadata_blob_path, test_dataset_metadata_local_path)

    # Download latest checkpoint from github
    logging.info("Download latest checkpoints from github")
    models_pattern = "^(identifier-mobilenetv2-c9\..+|matting-fba\..+|shadowgen256_car\..+|trimap513-deeplab-res2net\..+)$"
    kaleido_models_local_path = "./kaleido-models"
    os.makedirs(kaleido_models_local_path, exist_ok=True)
    run_bash(f'./scripts/fetch-models.sh "{models_pattern}" "{kaleido_models_local_path}"', realtime_output=False)

    # Download test dataset
    logging.info("Download test dataset")
    test_dataset_local_path = "./test_dataset"
    os.makedirs(test_dataset_local_path, exist_ok=True)
    fetch_dataset(test_dataset_metadata_local_path, test_dataset_local_path)

    # Perform test with reference model
    logging.info("Perform test with reference model")
    str_command_line = f"python -m bin.removebg-demo {test_dataset_local_path} " \
                       f"--path_networks {kaleido_models_local_path} " \
                       f"--path_parent test --evaluate --evaluate_file reference.json --caption reference --skip"
    run_bash(str_command_line)

    # Loop through list of trainings and evaluate the ones between min_day_delta and max_day_delta
    metric_dict = {}
    max_day_delta = args.max_day_delta
    for qi_bucket_name in dir_list:
        logging.info(f"Processing {qi_bucket_name}")
        # Get date
        qi_date_str = qi_bucket_name[:10]
        days_delta = compute_days_between_dates(qi_date_str, str_today)
        # Stop loop if the delta is further than max_day_delta
        if days_delta > max_day_delta:
            break

        qi_bucket_path = os.path.join(qi_bucket_main_path, qi_bucket_name)

        # Grab best checkpoint
        logging.info("Grab best checkpoint")
        best_checkpoint_blob_path = os.path.join(qi_bucket_path, "best.ckpt")
        best_checkpoint_local_path = "./best.ckpt"
        normalized_best_checkpoint_local_path = "./trimap513-deeplab-res2net.pth.tar"
        normalized_best_checkpoint_blob_path = os.path.join(qi_bucket_path, "trimap513-deeplab-res2net.pth.tar")

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

        # Copy kaleido-models and replace old trimap weights with new ones
        kaleido_models_new_local_path = f"{kaleido_models_local_path}_{qi_date_str}"
        shutil.copytree(kaleido_models_local_path, kaleido_models_new_local_path)

        # Copy model of current qi into YYYY-MM-DD_kaleido-models
        kaleido_models_new_trimap_model_path = os.path.join(kaleido_models_new_local_path, "trimap513-deeplab-res2net.pth.tar")
        os.rename(normalized_best_checkpoint_local_path, kaleido_models_new_trimap_model_path)

        # Perform test with new model
        logging.info("Perform test with qi model")
        str_command_line = f"python -m bin.removebg-demo {test_dataset_local_path} "\
                           f"--path_networks {kaleido_models_new_local_path} "\
                           f"--path_parent test --evaluate --evaluate_file {qi_date_str}.json --caption {qi_date_str} --skip"
        run_bash(str_command_line)

        # Launch evaluation
        logging.info("Launch evaluation")
        evaluation_local_path = os.path.join(".", f"{str_today}_eval_{qi_date_str}")
        str_command_line = f"python -m eval.plot_results reference.json {qi_date_str}.json "\
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

        metric_file = glob.glob(f"{evaluation_local_path}/*_test_dataset.png")[0]

        metric_dict[qi_bucket_name] = metric_file

    # Upload summary metric
    summary_evaluation_blob_path = os.path.join(qi_bucket_main_path, f"{str_today}_eval_summary")
    for qi_bucket_name, metric_file in metric_dict.items():
        file_blob_path = os.path.join(summary_evaluation_blob_path, f"{qi_bucket_name}.png")
        bucket.upload(metric_file, file_blob_path)


if __name__ == '__main__':
    main()
