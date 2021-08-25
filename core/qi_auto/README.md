# Automated QI training
These scripts aim at automating most of the QI training.

The only manual step left is to look at the result of the evaluation between the 22nd and the end of each month.
The metrics can be found each month in a bucket:
```bazaar
gs://kaleido-train-checkpoints/removebg/trimap-qi-auto/YYYY-MM-DD_qi/YYYY_MM_DD_eval.zip
# YYYY-MM-DD_qi has the date when the training started. (beginning of the month)
# YYYY_MM_DD_eval.zip has the date when the evaluation was performed. (end of the month)
```

From the evaluation metrics, a human should decide whether the new checkpoint should be considered a new best.<br/>
If so, it has to be copied with the following command:
```
gsutil cp gs://kaleido-train-checkpoints/removebg/trimap-qi-auto/candidate_best/trimap513-deeplab-res2net.pth.tar gs://kaleido-train-checkpoints/removebg/trimap-qi-auto/latest_best/trimap513-deeplab-res2net.pth.tar
```

## Setup

Create kubernetes cluster with [startup_cluster.sh](./data/qi_auto/startup_cluster.sh).

This cluster is composed 2 nodes by:
- Controller: non-preemptible VM `n1-standard-4` without GPU
- Worker: non-preemptible VM `custom-12-79872` with 1x `nvidia-tesla-v100`
  - Autoscaling is enabled

## Initialization
The initialization is performed by the script [initialization.py](./qi_auto/initialization.py).

This script is scheduled once a month at **3am of the first day of the month** by [job_initialization.yaml](./data/qi_auto/job_initialization.yaml). It will run on the controller node.

It does the following tasks:
- Grab latest best checkpoint
  - from `gs://kaleido-train-checkpoints/removebg/trimap-qi-auto/latest_best/trimap513-deeplab-res2net.pth.tar`
- Fetch metadata for train+valid dataset
  - Uploaded to `gs://kaleido-train-checkpoints/removebg/trimap-qi-auto/YYYY-MM-DD_qi/trimap_dataset_train.json`
- Fetch metadata for test dataset
  - Uploaded to `gs://kaleido-train-checkpoints/removebg/trimap-qi-auto/YYYY-MM-DD_qi/trimap_dataset_test.json`
- Create a kubernetes job configuration `job_trimap.yaml`
  - Based on [`template_job_trimap.yaml`](./data/qi_auto/template_job_trimap.yaml)
  - Uploaded to `gs://kaleido-train-checkpoints/removebg/trimap-qi-auto/YYYY-MM-DD_qi/job.yaml`
- Start kubernetes job with `job_trimap.yaml`

The script has to be configured with valid authentication credentials:
- "--danni_user=[...]"
- "--danni_token=[...]"

## Training
The training is performed by the script [removebg-train-trimap-cloud-qi.py](./bin/removebg-train-trimap-cloud-qi.py).

The script is scheduled at the end of the initialization. It will be run on the worker node.

Its result will be uploaded to a bucket `gs://kaleido-train-checkpoints/removebg/trimap-qi-auto/YYYY_MM_DD_qi`

## Termination
The termination is performed by the script [termination.py](./qi_auto/termination.py).

This script is scheduled once a month at **3am of the 21st day of the month** by [job_termination.yaml](./data/qi_auto/job_termination.yaml). It will run on the controller node.

It does the following tasks:
- Get the name of the last QI training
- Fetch the job configuration `job.yaml` on the bucket
- Stop the job


## Post Processing
The termination is performed by the script [postprocessing.py](./qi_auto/postprocessing.py).

This script is scheduled once a month at **3:30am of the 21st day of the month** by [job_postprocessing.yaml](./data/qi_auto/job_postprocessing.yaml). It will run on the worker node.

It does the following tasks:
- Get the name of the last QI training
- Grab the best checkpoint from this training
  - From `gs://kaleido-train-checkpoints/removebg/trimap-qi-auto/YYYY_MM_DD_qi/best.ckpt`
- Strip the checkpoint from the training artifacts and rename it as `trimap513-deeplab-res2net.pth.tar`
  - Uploaded to `gs://kaleido-train-checkpoints/removebg/trimap-qi-auto/candidate_best/trimap513-deeplab-res2net.pth.tar`
- Grab and test dataset metadata and download dataset
  - from `gs://kaleido-train-checkpoints/removebg/trimap-qi-auto/YYYY-MM-DD_qi/trimap_dataset_test.json`
- Download `kaleido-models`
  - from `gs://kaleido-train-checkpoints/removebg/trimap-qi-auto/latest_best/`
- Run evaluation on test dataset with [removebg-demo](./bin/removebg-demo.py)
  - With both old and new checkpoint
- Compute evaluation metrics
- Upload metrics on bucket
  - To `gs://kaleido-train-checkpoints/removebg/trimap-qi-auto/YYYY-MM-DD_qi/YYYY_MM_DD_eval.zip`

The script has to be configured with valid authentication credentials:
- "--danni_user=[...]"
- "--danni_token=[...]"
