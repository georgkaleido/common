#!/usr/bin/env bash

set -e

extra_index_url="https://${FURY_AUTH_TOKEN}:@deps.kaleido.ai/pypi/"

echo "Checking for new version of pip-tools."
pip install -U "pip-tools<7.0.0"

echo "Updating requirements.txt. This may take a while..."
pip-compile -U requirements.in --extra-index-url ${extra_index_url} --no-emit-index-url --no-header
echo "--extra-index-url https://\${FURY_AUTH_TOKEN@Q}:@deps.kaleido.ai/pypi/" >> requirements.txt
echo "Succesfully updated requirements.txt"

echo "Updating requirements-dev.txt. This may take a while..."
pip-compile -U requirements.in requirements-dev.in -o requirements-dev.txt --extra-index-url ${extra_index_url} --no-emit-index-url --no-header
echo $'pip\nwheel\nsetuptools' >> requirements-dev.txt
echo "--extra-index-url https://\${FURY_AUTH_TOKEN@Q}:@deps.kaleido.ai/pypi/" >> requirements-dev.txt
echo "Succesfully updated requirements-dev.txt"
