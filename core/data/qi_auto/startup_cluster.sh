#!/bin/bash
set -e

# Naming
CLUSTER_NAME=trimap-qi-auto

# Create images
python -m kaleido_utils.gce.create_and_upload_docker -i ${CLUSTER_NAME}-initialization -r /home/jerome/Workspace/removebg/kaleido-removebg/core/ -f ./data/qi_auto/Dockerfile.initialization -t v2
python -m kaleido_utils.gce.create_and_upload_docker -i ${CLUSTER_NAME}-trainer -r /home/jerome/Workspace/removebg/kaleido-removebg/core/ -f ./data/qi_auto/Dockerfile.trainer -t v2
python -m kaleido_utils.gce.create_and_upload_docker -i ${CLUSTER_NAME}-postprocessing -r /home/jerome/Workspace/removebg/kaleido-removebg/core/ -f ./data/qi_auto/Dockerfile.postprocessing -t v2

# Create cluster
gcloud container clusters create ${CLUSTER_NAME} --machine-type=n1-standard-4 --zone=europe-west4-b --num-nodes=1 --scopes=storage-rw --release-channel=rapid --cluster-version=1.21

# Create gpu pool
gcloud container node-pools create gpu-pool --cluster ${CLUSTER_NAME} --accelerator type=nvidia-tesla-v100,count=1 --machine-type=custom-12-79872 --zone=europe-west4-b --num-nodes=0 --enable-autoscaling --min-nodes 0 --max-nodes 1 --scopes=storage-rw

# Create gpu pool for tests purpose
#gcloud container node-pools create gpu-pool-training --cluster ${CLUSTER_NAME} --preemptible --accelerator type=nvidia-tesla-t4,count=1 --machine-type=n1-standard-4 --zone=europe-west4-b --num-nodes=1 --scopes=storage-rw --node-labels=goal=training
#gcloud container node-pools create gpu-pool-postprocessing --cluster ${CLUSTER_NAME} --preemptible --accelerator type=nvidia-tesla-t4,count=1 --machine-type=n1-standard-4 --zone=europe-west4-b --num-nodes=1 --scopes=storage-rw --node-labels=goal=postprocessing

# Install nvidia driver
#kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/cos/daemonset-preloaded.yaml
#kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/cos/daemonset-nvidia-v450.yaml
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/cos/daemonset-nvidia-mig.yaml

# Give default service account roles to list/create/delete/etc jobs
kubectl create role pod-manager --verb=get --verb=list --verb=watch  --verb=update --verb=delete --verb=create --verb=patch --resource=pods,services,deployments,jobs
kubectl create rolebinding default-pod-manager --role=pod-manager --serviceaccount=default:default --namespace=default

# Launch jobs
#kubectl apply -f job_initialization.yaml
#kubectl apply -f job_termination.yaml
#kubectl apply -f job_postprocessing.yaml
