# Standard import
import os
import logging
import re
import argparse
from datetime import datetime

# Local imports
from qi_auto.utilities import Bucket, run_bash, compute_days_between_dates


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


def main():

    parser = argparse.ArgumentParser(description='Terminate trainings.')
    parser.add_argument('--min_day_delta',
                        default=8*7,
                        type=int,
                        help=f"Stop jobs with more than this minimum number of days since training start. Default {8*7}")
    parser.add_argument('--max_day_delta',
                        default=10*7,
                        type=int,
                        help=f"Stop jobs with less than this maximum number of days since training start. Default {10*7}")
    args = parser.parse_args()

    # Initialize Bucket
    bucket_name = "kaleido-train-checkpoints"
    bucket = Bucket(bucket_name)

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
        raise RuntimeError(f"No entry found matching the pattern 'YYYY-MM-DD_qi', in bucket: {qi_bucket_main_path}")

    # Sort list in descending order
    dir_list.sort(reverse=True)

    # Loop through list of jobs and stop the ones between min_day_delta and max_day_delta
    min_day_delta = args.min_day_delta
    max_day_delta = args.max_day_delta
    # Make string with today's date
    str_today = datetime.today().strftime('%Y-%m-%d')
    for qi_bucket_name in dir_list:
        # Get date
        qi_date_str = qi_bucket_name[:10]
        days_delta = compute_days_between_dates(qi_date_str, str_today)

        # Stop loop if the delta is further than max_day_delta, because they should have already been stopped
        if days_delta > max_day_delta:
            break
        # Only stop the jobs above the min_day_delta threshold
        elif days_delta > min_day_delta:
            # qi_bucket_name = dir_list[-1]
            qi_bucket_path = os.path.join(qi_bucket_main_path, qi_bucket_name)
            # Build path to job.yaml on bucket
            job_blob_path = os.path.join(qi_bucket_path, "job.yaml")
            job_local_path = f"./job_{qi_bucket_name}.yaml"
            bucket.download(job_blob_path, job_local_path)

            # Stop training job
            logging.info("Stop kubernetes job")
            str_command_line = f"kubectl delete -f {job_local_path}"
            run_bash(str_command_line)


if __name__ == '__main__':
    main()
