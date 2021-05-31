# syntax = docker/dockerfile:1.2

# Node base image https://hub.docker.com/_/node/
FROM node:14.17.0-alpine

# Maintainer
LABEL maintainer="Kaleido AI <ops@kaleido.ai>"

# Application directory
WORKDIR /srv/

# Copy just package.json and yarn.lock
COPY package.json .
COPY yarn.lock .
COPY .yarnrc .
COPY .npmrc .

# Yarn
ARG NPM_TOKEN
RUN --mount=type=secret,id=npm_token \
    if [ -f /run/secrets/npm_token ]; then export TOKEN="$(cat /run/secrets/npm_token)"; \
    else export TOKEN="${NPM_TOKEN}"; fi \
 && echo '//npm-proxy.fury.io/kaleido/:_authToken=${NPM_TOKEN}' >> .npmrc \
 && NPM_TOKEN=${TOKEN} yarn install --immutable --frozen-lockfile --non-interactive --check-file

# Copy app
COPY . .

# Build arguments
ARG VCS_REF=main
ARG BUILD_DATE=""
ARG VERSION="${VCS_REF}"

# http://label-schema.orgx/rc1/
LABEL org.label-schema.schema-version "1.0"
LABEL org.label-schema.name           "kaleido-api"
LABEL org.label-schema.vendor         "Kaleido AI"
LABEL org.label-schema.version        "${VERSION}"
LABEL org.label-schema.build-date     "${BUILD_DATE}"
LABEL org.label-schema.description    "Remove.bg API"
LABEL org.label-schema.vcs-url        "https://github.com/remove-bg/kaleido-api"
LABEL org.label-schema.vcs-ref        "${VCS_REF}"

# Expose build variables to app
ENV VCS_REF="${VCS_REF}"
ENV BUILD_DATE="${BUILD_DATE}"
ENV VERSION="${VERSION}"

# Configure Node environment
ENV NODE_ENV="production"
ENV API_PORT=9443
ENV API_SSL=true

# Ports used by the listener
EXPOSE 9443

# Application start
CMD [ "node", "src/index.js" ]
