#!/bin/bash
set -e

# Naming for docker images
IMAGE_NAME=trimap-qi-auto

# Create images
python -m kaleido_utils.gce.create_and_upload_docker -i ${IMAGE_NAME}-initialization -r /home/${USER}/Workspace/removebg/kaleido-removebg/core/ -f ./data/qi_auto/Dockerfile.initialization -t v6
python -m kaleido_utils.gce.create_and_upload_docker -i ${IMAGE_NAME}-trainer -r /home/${USER}/Workspace/removebg/kaleido-removebg/core/ -f ./data/qi_auto/Dockerfile.trainer -t v6
python -m kaleido_utils.gce.create_and_upload_docker -i ${IMAGE_NAME}-postprocessing -r /home/${USER}/Workspace/removebg/kaleido-removebg/core/ -f ./data/qi_auto/Dockerfile.postprocessing -t v6
#python -m kaleido_utils.gce.create_and_upload_docker -i ${IMAGE_NAME}-batch-evaluation -r /home/${USER}/Workspace/removebg/kaleido-removebg/core/ -f ./data/qi_auto/Dockerfile.batch_evaluation -t v1

# Naming for cluster
CLUSTER_NAME=trimap-qi-auto-spot

# Create cluster
gcloud container clusters create ${CLUSTER_NAME} --machine-type=n1-standard-4 --zone=europe-west4-b --num-nodes=1 --scopes=storage-rw --release-channel=rapid --cluster-version=1.21

# Create gpu pool
# "beta" is necessary for now because --spot is only available as a preview for now (25.01.2022)
gcloud beta container node-pools create gpu-pool --cluster ${CLUSTER_NAME} --accelerator type=nvidia-tesla-v100,count=1 --machine-type=custom-12-79872 --zone=europe-west4-b --num-nodes=0 --enable-autoscaling --min-nodes 0 --max-nodes 6 --scopes=storage-rw --spot

# Create gpu pool for tests purpose
#gcloud container node-pools create gpu-pool-training --cluster ${CLUSTER_NAME} --preemptible --accelerator type=nvidia-tesla-t4,count=1 --machine-type=n1-standard-4 --zone=europe-west4-b --num-nodes=1 --scopes=storage-rw --node-labels=goal=training
#gcloud container node-pools create gpu-pool-postprocessing --cluster ${CLUSTER_NAME} --preemptible --accelerator type=nvidia-tesla-t4,count=1 --machine-type=n1-standard-4 --zone=europe-west4-b --num-nodes=1 --scopes=storage-rw --node-labels=goal=postprocessing

# Install nvidia driver
#kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/cos/daemonset-preloaded.yaml
#kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/cos/daemonset-nvidia-v450.yaml
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/cos/daemonset-nvidia-mig.yaml

# Give default service account roles to list/create/delete/etc jobs
kubectl create role pod-manager --verb=get --verb=list --verb=watch  --verb=update --verb=delete --verb=create --verb=patch --resource=pods,services,deployments,jobs,persistentvolumeclaims
kubectl create rolebinding default-pod-manager --role=pod-manager --serviceaccount=default:default --namespace=default

# Apply secrets
# Manual task: copy secret_auth_example.yaml as secret_auth.yaml, and fill the secret values
# secret_auth.yaml should never be uploaded to git
kubectl apply -f secret_auth.yaml

# Apply storage class
kubectl apply -f storage_class.yaml

# Launch jobs
#kubectl apply -f job_initialization.yaml
#kubectl apply -f job_termination.yaml
#kubectl apply -f job_postprocessing.yaml
