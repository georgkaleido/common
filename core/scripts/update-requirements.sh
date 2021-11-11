#!/usr/bin/env bash

# Execute this script from core/

set -e

if [[ -z "${FURY_AUTH_TOKEN}" ]]; then
  echo "FURY_AUTH_TOKEN environment variable not set!"
  exit 1
fi

extra_index_url="https://${FURY_AUTH_TOKEN}:@deps.kaleido.ai/pypi/"

echo "Checking for new version of pip-tools."
pip install -U "pip-tools<7.0.0"

echo "Updating requirements-deploy.txt. This may take a while..."
pip-compile -U requirements-deploy.in -o requirements-deploy.txt --extra-index-url ${extra_index_url} --no-emit-index-url --no-header
# add --extra-index-url to beginning of file
sed -i '1s/^/--extra-index-url https:\/\/\${FURY_AUTH_TOKEN}:@deps.kaleido.ai\/pypi\/\n\n/' requirements-deploy.txt
echo "Successfully updated requirements-deploy.txt"

echo "Removing torch,torchvision and torchtext dependencies from requirements-deploy.txt as already shipped in base image."
# remove torch, torchvision dependencies from deployment dependencies as we have them in base image
sed -i '/torch==/d' requirements-deploy.txt
sed -i '/torchvision==/d' requirements-deploy.txt
sed -i '/torchtext==/d' requirements-deploy.txt

echo "Updating requirements-dev.txt. This may take a while..."
pip-compile -U requirements-deploy.in requirements-dev.in -o requirements-dev.txt --extra-index-url ${extra_index_url} --no-emit-index-url --no-header
# add --extra-index-url to beginning of file
sed -i '1s/^/--extra-index-url https:\/\/\${FURY_AUTH_TOKEN}:@deps.kaleido.ai\/pypi\/\n\n/' requirements-dev.txt
echo "Successfully updated requirements-dev.txt"

echo "Updating requirements-train.txt. This may take a while..."
pip-compile -U requirements.in requirements-train.in -o requirements-train.txt --extra-index-url ${extra_index_url} --no-emit-index-url --no-header
# add --extra-index-url to beginning of file
sed -i '1s/^/--extra-index-url https:\/\/\${FURY_AUTH_TOKEN}:@deps.kaleido.ai\/pypi\/\n\n/' requirements-train.txt
echo "Successfully updated requirements-train.txt"

echo "Removing torch,torchvision and torchtext dependencies from requirements-train.txt as already shipped in base image."
# remove torch, torchvision dependencies from deployment dependencies as we have them in base image
sed -i '/torch==/d' requirements-train.txt
sed -i '/torchvision==/d' requirements-train.txt
sed -i '/torchtext==/d' requirements-train.txt


echo "Updating requirements-eval.txt. This may take a while..."
pip-compile -U requirements.in requirements-eval.in -o requirements-eval.txt --extra-index-url ${extra_index_url} --no-emit-index-url --no-header
# add --extra-index-url to beginning of file
sed -i '1s/^/--extra-index-url https:\/\/\${FURY_AUTH_TOKEN}:@deps.kaleido.ai\/pypi\/\n\n/' requirements-eval.txt
echo "Successfully updated requirements-eval.txt"

echo "Removing torch,torchvision and torchtext dependencies from requirements-eval.txt as already shipped in base image."
# remove torch, torchvision dependencies from deployment dependencies as we have them in base image
sed -i '/torch==/d' requirements-eval.txt
sed -i '/torchvision==/d' requirements-eval.txt
sed -i '/torchtext==/d' requirements-eval.txt
