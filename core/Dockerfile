# syntax = docker/dockerfile:1.2

# Pytorch base image
FROM nvidia/cuda:11.3.1-cudnn8-runtime-ubuntu20.04

# Maintainer
LABEL maintainer="Kaleido AI <ops@kaleido.ai>"

# Change workdir
WORKDIR /app/

# Required to prevent warnings
ARG DEBIAN_FRONTEND=noninteractive
ARG DEBCONF_NONINTERACTIVE_SEEN=true

# Build dependencies (will be uninstalled later)
ARG BUILD_DEPENDENCIES="curl python3-pip jq"
ARG GITHUB_FETCH_VERSION="v0.4.2"

# Install dependencies and configure user
RUN apt-get update \
 && apt-get install -y --no-install-recommends --fix-missing \
      ${BUILD_DEPENDENCIES} \
      libswscale-dev \
      libtbb2 \
      libtbb-dev \
      libjpeg-dev \
      libpng-dev \
      libtiff-dev \
      libavformat-dev \
      libpq-dev \
      libgl1-mesa-dev \
      libgl1-mesa-glx \
      python3.8-minimal \
      python3-pkg-resources \
 && curl -Lo /usr/bin/fetch https://github.com/gruntwork-io/fetch/releases/download/${GITHUB_FETCH_VERSION}/fetch_linux_$(dpkg --print-architecture) \
 && chmod +x /usr/bin/fetch \
 && useradd --create-home --user-group app \
 && chown app:app /app

# Add PATH for python binaries
ENV PATH="/home/app/.local/bin:${PATH}"

# Change user
USER app

# Add requirements
COPY --chown=app:app requirements-deploy.txt .

# Install Python project dependencies
ARG FURY_AUTH_TOKEN
RUN --mount=type=secret,id=fury_auth_token,mode=0444 \
    if [ -f /run/secrets/fury_auth_token ]; then export FURY_AUTH_TOKEN="$(cat /run/secrets/fury_auth_token)"; fi \
 && pip install --user --progress-bar off -r requirements-deploy.txt

# https://github.com/remove-bg/downscale-area-cuda/
ARG CUDA_DOWNSCALE_VERSION="3.0.7"
# https://github.com/remove-bg/connected-component-labeling-cuda/
ARG CUDA_CCL_VERSION="3.0.5"
# Requested Compute Capability
ARG COMPUTE_CAPABILITY="75"

RUN --mount=type=secret,id=fury_auth_token,mode=0444 \
    if [ -f /run/secrets/fury_auth_token ]; then export FURY_AUTH_TOKEN="$(cat /run/secrets/fury_auth_token)"; fi \
 && pip install --user --progress-bar off --extra-index-url https://${FURY_AUTH_TOKEN}:@deps.kaleido.ai/pypi/ \
     "downscale-area==${CUDA_DOWNSCALE_VERSION}+cc${COMPUTE_CAPABILITY}" \
     "connected-component-labeling==${CUDA_CCL_VERSION}+cc${COMPUTE_CAPABILITY}"

# Add Kaleido Models
ARG GITHUB_AUTH_TOKEN

# Add models file description
COPY --chown=app:app kaleido-models.yml .

RUN --mount=type=secret,id=github_auth_token,mode=0444 \
    if [ -f /run/secrets/github_auth_token ]; then export GITHUB_AUTH_TOKEN="$(cat /run/secrets/github_auth_token)"; fi \
 && pip install yq \
 && mkdir networks-trained \
 && export KALEIDO_MODELS_VERSION=$(yq -r ".version" kaleido-models.yml) \
 && yq -rc '.files | .[] | [.name, .hash] | @tsv' kaleido-models.yml > kaleido-models.tsv \
 && while IFS=$'\n' read -r line ; do \
      fetch --github-oauth-token="${GITHUB_AUTH_TOKEN}"                 \
            --repo="https://github.com/remove-bg/kaleido-models"        \
            --tag="${KALEIDO_MODELS_VERSION}"                           \
            --release-asset="$(echo $line | awk '{print $1}')"          \
            --release-asset-checksum="$(echo $line | awk '{print $2}')" \
            --release-asset-checksum-algo="sha256"                      \
      networks-trained/ ; \
    done <kaleido-models.tsv \
 && pip uninstall -y yq \
 && rm kaleido-models.yml kaleido-models.tsv


########################################################################################################################
# TODO: Remove this, once this ticket is resolved:
# https://www.notion.so/kaleidoai/Split-kaleido-removebg-into-service-and-library-f3b8394d449a4505afff9636078e88c0
#
# The library should then be installed only through the requirements.txt file.
#
# If REMOVEBG_CORE_PY_VERSION=main, it installs the latest version of the library. If REMOVEBG_CORE_PY_VERSION is
# set to a version number, it installs the specified version of the library instead.
########################################################################################################################

# # https://github.com/remove-bg/kaleido-core-removebg
# ARG REMOVEBG_CORE_PY_VERSION=main
#
# # Install required python packages
# RUN --mount=type=secret,id=fury_auth_token,mode=0444 --mount=type=cache,target=/root/.cache/pip pip install \
#       --progress-bar off --extra-index-url https://$(cat /run/secrets/fury_auth_token):@deps.kaleido.ai/pypi/ \
#         removebg-core$([ ${REMOVEBG_CORE_PY_VERSION} = "main" ] && echo "" || echo "==${REMOVEBG_CORE_PY_VERSION}")
########################################################################################################################

# Manually copy removebg-core library
RUN mkdir removebg
COPY --chown=app:app removebg/models removebg/models
COPY --chown=app:app removebg/*.py removebg/

# Remove build dependencies
USER root
RUN apt-get purge -y ${BUILD_DEPENDENCIES} \
 && apt-get autoremove -y \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /usr/bin/fetch

# Copy application
COPY --chown=app:app bin/removebg-server.py bin/
COPY --chown=app:app liveness.sh .

# Build arguments
ARG VCS_REF=main \
    BUILD_DATE="" \
    VERSION="${VCS_REF}"

# http://label-schema.org/rc1/
LABEL org.label-schema.schema-version "1.0"
LABEL org.label-schema.name           "kaleido-removebg-core"
LABEL org.label-schema.vendor         "Kaleido AI"
LABEL org.label-schema.version        "${VERSION}"
LABEL org.label-schema.build-date     "${BUILD_DATE}"
LABEL org.label-schema.description    "remove.bg Core"
LABEL org.label-schema.vcs-url        "https://github.com/remove-bg/kaleido-removebg#core"
LABEL org.label-schema.vcs-ref        "${VCS_REF}"

# Expose environment variables to app
ENV VCS_REF="${VCS_REF}" \
    BUILD_DATE="${BUILD_DATE}" \
    VERSION="${VERSION}"

# Application configuration
ENV PYTHONUNBUFFERED="true" \
    PYTHONPATH="${PYTHONPATH}:../" \
    NVIDIA_VISIBLE_DEVICES="all"

# Switch back to app user
USER app

# Entrypoint and Command
ENTRYPOINT ["python3.8", "-m"]
CMD ["bin.removebg-server"]
