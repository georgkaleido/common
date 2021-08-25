# Standard import
import os
from google.cloud import storage
import logging
import subprocess

# logging.basicConfig(
#     format='%(asctime)s %(levelname)-8s %(message)s',
#     level=logging.INFO,
#     datefmt='%Y-%m-%d %H:%M:%S')


def run_bash(cmd_str, realtime_output=True):
    logging.info(f"Running shell command:\n> {cmd_str}")
    process = subprocess.Popen(cmd_str, shell=True, stderr=subprocess.PIPE, encoding="UTF-8")

    if realtime_output:
        # Print output of command in real time
        logging.info(f"Output of shell command:")
        while True:
            out = process.stderr.readline()
            if out == '' and process.poll() is not None:
                break
            if out != '':
                logging.info(out.strip())
    else:
        # Print output of command once it is finished
        shell_output = process.communicate()[0]
        if shell_output:
            logging.info(f"Output of shell command:\n{shell_output}")

    return_code = process.returncode
    if 0 != return_code:
        logging.info(f"Return code of shell command = {return_code}")
        raise RuntimeError(f"Below shell command failed with return_code={return_code}\n{cmd_str}")


class Bucket:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.client = storage.Client()
        self.bucket = self.client.get_bucket(bucket_name)

    @staticmethod
    def human_readable_bucket_name(path):
        return path.replace('/b/', 'gs://').replace('/o/', '/').replace('%2F', '/')

    def download(self, blob_path, local_path):
        blob = self.bucket.blob(blob_path)

        dir_local_path = os.path.dirname(local_path)

        if blob.exists():
            # Create destination folder
            os.makedirs(dir_local_path, exist_ok=True)
            logging.info(f"Downloading file from bucket {self.human_readable_bucket_name(blob.path)} to {local_path}")
            blob.download_to_filename(local_path)
        else:
            raise RuntimeError(f"No file exists at {self.human_readable_bucket_name(blob.path)}")

    def download_directory(self, bucket_path, local_path):
        blobs = self.bucket.list_blobs(prefix=bucket_path)  # Get list of files
        os.makedirs(local_path, exist_ok=True)
        for blob in blobs:
            if blob.name.endswith("/"):
                continue
            file_name = os.path.basename(blob.name)
            file_local_path = os.path.join(local_path, file_name)
            logging.info(f"Downloading file from bucket {self.human_readable_bucket_name(blob.path)} to {file_local_path}")
            blob.download_to_filename(file_local_path)

    def upload(self, local_path, blob_path):
        tmp_blob_path = f"{blob_path}.tmp"
        tmp_blob = self.bucket.blob(tmp_blob_path)
        if os.path.exists(local_path):
            # Upload is done on a tmp file first, to limit the risk of corruption if the node is taken down during copy
            logging.info(f"Uploading file to bucket {self.human_readable_bucket_name(tmp_blob.path)} from {local_path}")
            tmp_blob.upload_from_filename(local_path)
            logging.info(f"Rename bucket file from {self.human_readable_bucket_name(tmp_blob.path)} to {blob_path}")
            tmp_blob = self.bucket.rename_blob(tmp_blob, blob_path)
        else:
            raise RuntimeError(f"File does not exist: {local_path}")

    def exists(self, blob_path):
        blob = self.bucket.blob(blob_path)
        return blob.exists()

    def rename(self, current_path, new_path):
        blob = self.bucket.blob(current_path)
        self.bucket.rename_blob(blob, new_path)

    def list_folders(self, path, dir_prefix=""):
        prefix = os.path.join(path, dir_prefix)
        blob_list = list(self.bucket.list_blobs(prefix=prefix))
        formatted_path = os.path.join(f"gs://{self.bucket_name}", path)
        blob_list = [self.human_readable_bucket_name(b.path) for b in blob_list]
        dir_list = [os.path.dirname(b.replace(f"{formatted_path}/", "")) for b in blob_list]
        # remove duplicate
        dir_list = list(dict.fromkeys(dir_list))
        return dir_list
