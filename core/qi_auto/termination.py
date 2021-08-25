# Standard import
import os
import torch
from collections import OrderedDict
import logging
import re

# Local imports
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
    # Initialize Bucket
    bucket_name = "kaleido-train-checkpoints"
    bucket = Bucket(bucket_name)

    # Get job.yaml
    logging.info("Get job.yaml")
    # List folders in bucket
    qi_bucket_main_path = os.path.join("removebg", "trimap-qi-auto")
    dir_list = bucket.list_folders(qi_bucket_main_path)
    # Remove entries which are not in the format YYYY-MM-DD_qi
    new_dir_list = []
    pattern = r"^\d\d\d\d-\d\d-\d\d\_qi$"
    for directory in dir_list:
        result = re.match(pattern, directory)
        if result:
            new_dir_list.append(directory)
    dir_list = new_dir_list

    if not dir_list:
        raise RuntimeError(f"Now entry found matching the pattern 'YYYY-MM-DD_qi', in bucket: {qi_bucket_main_path}")

    # Sort list
    dir_list.sort()

    # Get most recent
    qi_bucket_name = dir_list[-1]
    qi_bucket_path = os.path.join(qi_bucket_main_path, qi_bucket_name)
    # Build path to job.yaml on bucket
    job_blob_path = os.path.join(qi_bucket_path, "job.yaml")
    job_local_path = "./job.yaml"
    bucket.download(job_blob_path, job_local_path)

    # Stop training job
    logging.info("Stop kubernetes job")
    str_command_line = f"kubectl delete -f {job_local_path}"
    run_bash(str_command_line)


if __name__ == '__main__':
    main()
