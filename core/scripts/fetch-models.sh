#!/usr/bin/env bash

#KALEIDO_MODELS_FILES="^(identifier-mobilenetv2-c9\..+|matting-fba\..+|shadowgen256_car\..+|trimap513-deeplab-res2net\..+)$"
KALEIDO_MODELS_FILES="$1"
DEST=$2

if [[ -z "${KALEIDO_MODELS_FILES}" || -z "${DEST}" ]]
then
  echo "Usage: fetch-model.sh \"FilePattern\" DestinationDirectory"
  echo "Example: fetch-model.sh \"^(identifier-mobilenetv2-c9\..+|matting-fba\..+|shadowgen256_car\..+|trimap513-deeplab-res2net\..+)$\" ./models/"
  exit -1
fi

if [[ -z "${GITHUB_AUTH_TOKEN}" ]]
then
  echo
  echo "Error: Environment variable GITHUB_AUTH_TOKEN is not set"
  exit -1
fi

fetch --github-oauth-token="${GITHUB_AUTH_TOKEN}" \
      --repo="https://github.com/remove-bg/kaleido-models" \
      --tag ">=1.0.0" \
      --release-asset="${KALEIDO_MODELS_FILES}" \
      ${DEST}
