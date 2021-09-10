# syntax = docker/dockerfile:1.2

# Pytorch base image
FROM nvcr.io/nvidia/pytorch:21.02-py3

# Maintainer
LABEL maintainer="Kaleido AI <ops@kaleido.ai>"

# Change workdir
WORKDIR /app/

# Required to prevent warnings
ARG DEBIAN_FRONTEND=noninteractive
ARG DEBCONF_NONINTERACTIVE_SEEN=true

# Build dependencies (will be uninstalled later)
ARG BUILD_DEPENDENCIES="pkg-config meson ninja-build texinfo yasm nasm autoconf automake build-essential cmake"
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
 && curl -Lo /usr/bin/fetch https://github.com/gruntwork-io/fetch/releases/download/${GITHUB_FETCH_VERSION}/fetch_linux_$(dpkg --print-architecture) \
 && chmod +x /usr/bin/fetch \
 && useradd --create-home --user-group app \
 && chown app:app /app

# Add PATH for python binaries
ENV PATH="/home/app/.local/bin:${PATH}"

# Add requirements
COPY --chown=app:app requirements-deploy.txt .

# Change user
USER app

# Install Python project dependencies
ARG FURY_AUTH_TOKEN
RUN --mount=type=secret,id=fury_auth_token,mode=0444 \
    if [ -f /run/secrets/fury_auth_token ]; then export FURY_AUTH_TOKEN="$(cat /run/secrets/fury_auth_token)"; fi \
 && pip install --user --progress-bar off -r requirements-deploy.txt


########################################################################################################################
# TODO: Remove this, once this ticket is resolved:
# https://www.notion.so/kaleidoai/Split-kaleido-removebg-into-service-and-library-f3b8394d449a4505afff9636078e88c0
#
# The library should then be installed only through the requirements.txt file.
#
# If REMOVEBG_CORE_PY_VERSION=main, it installs the latest version of the library. If REMOVEBG_CORE_PY_VERSION is
# set to a version number, it installs the specified version of the library instead.
########################################################################################################################

# https://github.com/remove-bg/kaleido-core-removebg
ARG REMOVEBG_CORE_PY_VERSION=main

# Install required python packages
RUN --mount=type=secret,id=fury_auth_token,mode=0444 --mount=type=cache,target=/root/.cache/pip pip install \
      --progress-bar off --extra-index-url https://$(cat /run/secrets/fury_auth_token):@deps.kaleido.ai/pypi/ \
        removebg-core$([[ ${REMOVEBG_CORE_PY_VERSION} = "main" ]] && echo "" || echo "==${REMOVEBG_CORE_PY_VERSION}")
########################################################################################################################


# https://github.com/remove-bg/kaleido-models
ARG KALEIDO_MODELS_VERSION="1.7.0"
ARG KALEIDO_MODELS_FILES="^(identifier-mobilenetv2-c9\..+|matting-fba\..+|shadowgen256_car\..+|trimap513-deeplab-res2net\..+)$"

# https://github.com/remove-bg/downscale-area-cuda/
ARG CUDA_DOWNSCALE_VERSION="v3.0.4"
# https://github.com/remove-bg/connected-component-labeling-cuda/
ARG CUDA_CCL_VERSION="v3.0.4"
# Requested Compute Capability
ARG COMPUTE_CAPABILITY="75"

# Add Kaleido Models
ARG GITHUB_AUTH_TOKEN
RUN --mount=type=secret,id=github_auth_token,mode=0444 \
    if [ -f /run/secrets/github_auth_token ]; then export GITHUB_AUTH_TOKEN="$(cat /run/secrets/github_auth_token)"; fi \
 && mkdir networks-trained \
 && mkdir -p /app/cuda_modules/downscale/ \
 && mkdir -p /app/cuda_modules/ccl/ \
 && fetch --github-oauth-token="${GITHUB_AUTH_TOKEN}"          \
          --repo="https://github.com/remove-bg/kaleido-models" \
          --tag="${KALEIDO_MODELS_VERSION}"                    \
          --release-asset="${KALEIDO_MODELS_FILES}"            \
      networks-trained/ \
 && curl -L -H "Authorization: token ${GITHUB_AUTH_TOKEN}" --output - \
    https://api.github.com/repos/remove-bg/connected-component-labeling-cuda/tarball/${CUDA_CCL_VERSION} | \
    tar -xz --strip-components=1 -C /app/cuda_modules/ccl/ \
 && curl -L -H "Authorization: token ${GITHUB_AUTH_TOKEN}" --output - \
    https://api.github.com/repos/remove-bg/downscale-area-cuda/tarball/${CUDA_DOWNSCALE_VERSION} | \
    tar -xz --strip-components=1 -C /app/cuda_modules/downscale/ \
 && /app/cuda_modules/ccl/python/ccl_package/install.sh ${COMPUTE_CAPABILITY} \
 && /app/cuda_modules/downscale/python/da_package/install.sh ${COMPUTE_CAPABILITY}

# Copy application
COPY --chown=app:app bin/removebg-server.py bin/
COPY --chown=app:app liveness.sh .

# Remove build dependencies
USER root
RUN apt-get purge -y ${BUILD_DEPENDENCIES} \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /usr/bin/fetch

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
ENV PYTHONUNBUFFERED="true"
ENV PYTHONPATH="${PYTHONPATH}:../"

# Switch back to app user
USER app

# Entrypoint and Command
ENTRYPOINT [ "/usr/local/bin/nvidia_entrypoint.sh" ]
CMD [ "bin/removebg-server.py" ]
