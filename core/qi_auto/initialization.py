# Standard import
import logging
import os
from datetime import datetime

# Local imports
from bin.dataset_fetch_metadata import dataset_fetch_metadata
from qi_auto.utilities import Bucket, run_bash

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S"
)


def main():

    assert "DANNI_USER" in os.environ, "Could not find environment variable DANNI_USER"
    assert "DANNI_TOKEN" in os.environ, "Could not find environment variable DANNI_TOKEN"

    # Make string with today's date and qi directory name
    str_today = datetime.today().strftime("%Y-%m-%d")
    str_today_qi = f"{str_today}_qi"

    # Initialize Bucket
    bucket_name = "kaleido-train-checkpoints"
    bucket = Bucket(bucket_name)

    # Fetch metadata for train+valid/test dataset
    for split in ["train", "test"]:
        metadata_blob_path = os.path.join(
            "removebg", "trimap-qi-auto", str_today_qi, f"trimap_dataset_{split}.json"
        )
        if "train" == split:
            train_metadata_blob_path = metadata_blob_path
        logging.info(f"Fetch dataset metadata from Danni for {split} split")
        metadata_local_path = f"./trimap_dataset_{split}.json"
        dataset_fetch_metadata(
            user=os.environ["DANNI_USER"],
            token=os.environ["DANNI_TOKEN"],
            metadata_output_path=metadata_local_path,
            max_pages=None,
            test_split=("test" == split),
        )

        # Upload metadata to bucket
        bucket.upload(local_path=metadata_local_path, blob_path=metadata_blob_path)

    # Create job.yaml from template
    logging.info("Create job.yaml from template")
    # Load template
    with open("./data/qi_auto/template_job_trimap.yaml", "r") as f:
        job_template = f.read()
    # Insert arguments
    job = job_template.replace("[{DATE}]", f"{str_today}")
    job = job.replace("[{NAME}]", str_today_qi)
    job = job.replace("[{DANNI_METADATA_PATH}]", f"gs://{bucket_name}/{train_metadata_blob_path}")
    # Write job.yaml
    job_local_path = "./job_trimap.yaml"
    with open(job_local_path, "w") as f:
        f.write(job)

    # Save job.yaml in bucket
    job_blob_path = os.path.join("removebg", "trimap-qi-auto", str_today_qi, f"job.yaml")
    bucket.upload(local_path=job_local_path, blob_path=job_blob_path)

    # Start job
    logging.info("Start kubernetes job")
    str_command_line = f"kubectl apply -f {job_local_path}"
    run_bash(str_command_line)


if __name__ == "__main__":
    main()
