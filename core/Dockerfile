# syntax = docker/dockerfile:1.2

# Define build arguments
ARG PYTORCH_IMAGE_TAG=20.11

# Pytorch base image
FROM nvcr.io/nvidia/pytorch:${PYTORCH_IMAGE_TAG}-py3

# Maintainer
LABEL maintainer="Kaleido AI <ops@kaleido.ai>"

# Required to prevent warnings
ARG DEBIAN_FRONTEND=noninteractive
ARG DEBCONF_NONINTERACTIVE_SEEN=true

# Install libGL
RUN apt-get update \
 && apt-get install -y --no-install-recommends --fix-missing \
       libgl1-mesa-dev \
       libgl1-mesa-glx \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Change workdir
WORKDIR /app/

# Define package versions

# https://github.com/remove-bg/kaleido-models
ARG KALEIDO_MODELS_VERSION=1.1.4
# https://github.com/remove-bg/downscale-area-cuda/
ARG CUDA_DOWNSCALE_VERSION=v3.0.4
# https://github.com/remove-bg/connected-component-labeling-cuda
ARG CUDA_CCL_VERSION=v3.0.4
# https://github.com/remove-bg/kaleido-core-lib
ARG KALEIDO_CORE_PY_VERSION=1.3.11
# https://github.com/remove-bg/kaleido-core-shadowgen
ARG SHADOWGEN_CORE_PY_VERSION=1.4.2
# https://github.com/remove-bg/kaleido-core-removebg
ARG REMOVEBG_CORE_PY_VERSION=1.0.0


# Install required python packages
RUN --mount=type=secret,id=fury_auth_token --mount=type=cache,target=/root/.cache/pip pip install \
      --progress-bar off --extra-index-url https://$(cat /run/secrets/fury_auth_token):@deps.kaleido.ai/pypi/ \
        kaleido-core==${KALEIDO_CORE_PY_VERSION} \
        removebg-core==${REMOVEBG_CORE_PY_VERSION} \
        shadowgen-core==${SHADOWGEN_CORE_PY_VERSION}

# Install models
RUN --mount=type=secret,id=github_auth_token \
 mkdir -p networks-trained cuda_modules/ccl cuda_modules/downscale \
 && curl -L -H "Authorization: token $(cat /run/secrets/github_auth_token)" --output - \
    https://api.github.com/repos/remove-bg/kaleido-models/tarball/${KALEIDO_MODELS_VERSION} | \
    tar -xz --strip-components=1 -C /tmp && cd /tmp \
 && mv identifier-mobilenetv2-c9.* \
       matting-fba.* \
       shadowgen256_car.* \
       trimap513-deeplab-res2net.* \
    /app/networks-trained/ \
 && curl -L -H "Authorization: token $(cat /run/secrets/github_auth_token)" --output - \
    https://api.github.com/repos/remove-bg/connected-component-labeling-cuda/tarball/${CUDA_CCL_VERSION} | \
    tar -xz --strip-components=1 -C /app/cuda_modules/ccl/ \
 && curl -L -H "Authorization: token $(cat /run/secrets/github_auth_token)" --output - \
    https://api.github.com/repos/remove-bg/downscale-area-cuda/tarball/${CUDA_DOWNSCALE_VERSION} | \
    tar -xz --strip-components=1 -C /app/cuda_modules/downscale/ \
 && rm -rf /tmp/*

# Requested Compute Capability
ARG COMPUTE_CAPABILITY=75

RUN /app/cuda_modules/ccl/python/ccl_package/install.sh ${COMPUTE_CAPABILITY} \
 && /app/cuda_modules/downscale/python/da_package/install.sh ${COMPUTE_CAPABILITY}

# Copy files
COPY liveness.sh /app/

# Build arguments
ARG VCS_REF=main
ARG BUILD_DATE=""
ARG VERSION="${VCS_REF}"

# http://label-schema.org/rc1/
LABEL org.label-schema.schema-version "1.0"
LABEL org.label-schema.name           "removebg-core"
LABEL org.label-schema.vendor         "Kaleido AI"
LABEL org.label-schema.version        "${VERSION}"
LABEL org.label-schema.build-date     "${BUILD_DATE}"
LABEL org.label-schema.description    "Remove.bg Core"
LABEL org.label-schema.vcs-url        "https://github.com/remove-bg/kaleido-core-removebg"
LABEL org.label-schema.vcs-ref        "${VCS_REF}"

# Expose environment variables to app
ENV VCS_REF="${VCS_REF}"
ENV BUILD_DATE="${BUILD_DATE}"
ENV VERSION="${VERSION}"

# Entrypoint and Command
ENTRYPOINT [ "/usr/local/bin/nvidia_entrypoint.sh" ]
CMD [ "removebg-server.py" ]
