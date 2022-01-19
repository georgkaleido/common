# syntax = docker/dockerfile:1.2

# Node base image https://hub.docker.com/_/node/
FROM node:14.18.3

# Maintainer
LABEL maintainer="Kaleido AI <ops@kaleido.ai>"

# Application directory
WORKDIR /app/

# Required to prevent warnings
ARG DEBIAN_FRONTEND=noninteractive
ARG DEBCONF_NONINTERACTIVE_SEEN=true

# Add Tini
ENV TINI_VERSION v0.19.0
ADD --chmod=755 https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /bin/tini

# Configure user
RUN useradd --create-home --user-group app \
 && chown app:app /app \
 && chmod 755 /bin/tini

# Copy just package.json and yarn.lock
COPY --chown=app:app package.json yarn.lock ./

# Change user
USER app

# Yarn
ARG NPM_TOKEN
RUN --mount=type=secret,id=npm_token,mode=0444 \
    if [ -f /run/secrets/npm_token ]; then export NPM_TOKEN="$(cat /run/secrets/npm_token)"; fi \
 && npm config set registry https://npm-proxy.fury.io/kaleido/ \
 && npm config set always-auth true \
 && echo '//npm-proxy.fury.io/kaleido/:_authToken=${NPM_TOKEN}' >> ~/.npmrc \
 && yarn install --immutable --frozen-lockfile --production --non-interactive --check-files \
 && rm ~/.npmrc

# Copy app
COPY --chown=app:app . .

# Build arguments
ARG VCS_REF=main \
    BUILD_DATE="" \
    VERSION="${VCS_REF}"

# http://label-schema.orgx/rc1/
LABEL org.label-schema.schema-version "1.0"
LABEL org.label-schema.name           "remove-bg-api"
LABEL org.label-schema.vendor         "Kaleido AI"
LABEL org.label-schema.version        "${VERSION}"
LABEL org.label-schema.build-date     "${BUILD_DATE}"
LABEL org.label-schema.description    "remove.bg API"
LABEL org.label-schema.vcs-url        "https://github.com/remove-bg/kaleido-removebg#api"
LABEL org.label-schema.vcs-ref        "${VCS_REF}"

# Expose environment variables to app
ENV VCS_REF="${VCS_REF}" \
    BUILD_DATE="${BUILD_DATE}" \
    VERSION="${VERSION}"

# Switch back to app user
USER app

# Configure Node environment
ENV NODE_ENV="production" \
    API_PORT="9443" \
    API_SSL="true" \
    API_SSL_CRT="ssl/development.crt" \
    API_SSL_KEY="ssl/development.key" \
    API_SSL_PASS="development" \
    NODE_OPTIONS="--max_old_space_size=4096"

# Ports used by the listener
EXPOSE 9443

# Entrypoint and Command
ENTRYPOINT ["/bin/tini", "--"]
CMD [ "node", "src/index.js" ]
