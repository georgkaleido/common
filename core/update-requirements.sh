#!/usr/bin/env bash

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
# add --extra-index-url and install requirements (pip, setuptools, wheel) to beginning of file
sed -i '1s/^/--extra-index-url https:\/\/\${FURY_AUTH_TOKEN}:@deps.kaleido.ai\/pypi\/\npip>=21.0.0<22.0.0\nsetuptools>=52.0.0,<53.0.0\nwheel>=0.36<0.37\n\n/' requirements-deploy.txt
echo "Successfully updated requirements.txt"

echo "Updating requirements-dev.txt. This may take a while..."
pip-compile -U requirements-deploy.in requirements-dev.in -o requirements-dev.txt --extra-index-url ${extra_index_url} --no-emit-index-url --no-header
# add --extra-index-url and install requirements (pip, setuptools, wheel) to beginning of file
sed -i '1s/^/--extra-index-url https:\/\/\${FURY_AUTH_TOKEN}:@deps.kaleido.ai\/pypi\/\npip>=21.0.0<22.0.0\nsetuptools>=52.0.0,<53.0.0\nwheel>=0.36<0.37\n\n/' requirements-dev.txt
echo "Successfully updated requirements-dev.txt"
