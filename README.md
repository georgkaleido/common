# remove.bg Core and API

This repository contains the remove.bg [Core](core) and [API](api). The remove.bg website can be found at [remove-bg/remove-bg-web](https://github.com/remove-bg/remove-bg-web).

## 🚧 Initial Setup

1) It is recommended to use [`asdf`](https://asdf-vm.com/) to manage your dependency versions. A
   [`.tool-versions`](.tool-versions) file for `asdf` can be found in this repository.

1) Generate a [_Full Access Token_](https://gemfury.com/help/tokens/) (not a _Deploy Token_) in your personal Gemfury
   account (which needs to be linked to the [Kaleido GemFury account](https://manage.fury.io/manage/kaleido/)). You can
   read about [GemFury in 📝 Notion](https://www.notion.so/kaleidoai/GemFury-374c03b9452c4c839d9efb6276369bed).

1) Generate a [_Personal Access Token_](https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token)
   in your personal GitHub account (which needs to be a member of the [Kaleido `remove-bg` organization](https://github.com/remove-bg).

1) Prepare your NPM token (`npm token list` or take it from `~/.npmrc`). This is different from your GemFury token but
   is required for NPM to access NodeJS packages hosted on [Kaleido's GemFury account](https://manage.fury.io/manage/kaleido/).

## 🐳  Docker

_This repository makes use of Docker BuildKit and therefore requires at least [Docker API 1.39](https://docs.docker.com/engine/api/v1.39/),
which means at least Docker daemon version 18.09._

Refer to the [Docker documentation in Notion](https://www.notion.so/kaleidoai/Docker-3c26c83098a84644bbe14194e5725280) as well
as the [`docker-compose.yml`](docker-compose.yml) file for more details.

To build and run this application locally via Docker, simply use `docker-compose` from the root of the repository. The optional
`--build` flag will build the image locally and then run it. Note that you need to prepend all enviornment variables for the
Docker images to build successfully.

```bash
FURY_AUTH_TOKEN=[your GemFury token] GITHUB_AUTH_TOKEN=[your GitHub Access token] NPM_TOKEN=[your NPM token] docker-compose up [--build]
```

To stop everything, use the `down` command. Note that the optional `-v` flag deletes all volumes, including the rabbitmq queue.

```bash
docker-compose down [-v]
```

To run commands in the application container, simply use `docker-compose exec`:

```bash
# docker-compose exec api [command goes here]
docker-compose exec api ls
```

### Manual Build

To manually build the Docker images on your local machine, you will need to pass [a GemFury token](https://gemfury.com/help/tokens/) as well
as a [GitHub auth token](https://github.com/settings/tokens) (`repo` scope) and an NPM token to the `docker build` command. To do this, store
your Gemfury auth token for example in `fury_auth_token.txt`, your GitHub auth token in `github_auth_token.txt` and the NPM token in `npm_token.txt`.

Then run the following commands to create both the API and Core images (adjust the image name and tag to your needs):

```bash
docker build \
    --secret id=fury_auth_token,src=fury_auth_token.txt \
    --secret id=github_auth_token,src=github_auth_token.txt \
    --tag eu.gcr.io/removebg-226919/removebg-core:1.0.0 \
    core

docker build \
    --secret id=npm_token,src=npm_token.txt \
    --tag eu.gcr.io/removebg-226919/removebg-api:1.0.0 \
    api
```

If you're building a Docker image purely for local development, you can instead pass normal `--build-arg`s for simplicity:

```bash
docker build \
  --build-arg FURY_AUTH_TOKEN="[your token]" \
  --build-arg GITHUB_AUTH_TOKEN="[your token]" \
  --build-arg NPM_TOKEN="[your token]" \
  [...]
```

> ⚠️ _Note that images built with `--build-arg *_AUTH_TOKEN=[token]` should **never** be used in production because they leak those credentials!_

## ⚙️ Components

### API

`//TODO: describe api`

### Core

`//TODO: describe core`

`//TODO: describe requirements_*.in and how it translates to *.txt`

`//TODO: move this to new repository after the library is split`

After all prerequisites are satisfied, you can create a source distribution in the [dist](core/dist) directory
with this command.

```bash
python setup.py sdist
```

Use `bdist` to build a binary distribution, `bdist_wheel` to build a binary wheel.

## 📝 Changelog

See [CHANGELOG](CHANGELOG.md).

## 🧱 Build Pipeline

This project is built on [CircleCI](https://app.circleci.com/pipelines/github/remove-bg/kaleido-removebg).

Docker images are being pushed to `eu.gcr.io/removebg-226919/removebg-core` and `eu.gcr.io/removebg-226919/removebg-api` for tagged builds.

### CircleCI Environment Variables

- `CACHE_VERSION`: `2` (increment to update cache)
- `DOCKER_IMAGE_NAME`: `eu.gcr.io/removebg-226919/removebg` (base image name, `-core` and `-api` are appended automatically)
- `GKE_CLUSTER`: `removebg-app` (which GKE cluster the app will be deployed to)
- `GKE_KUBERNETES_VERSION`: `1.20.8` (used by `kubeval` to validate K8s config)

## 🚚 Release Process

For the [GPU Compute Capability levels](https://arnon.dk/matching-sm-architectures-arch-and-gencode-for-various-nvidia-cards/)
that should be built for the `core` image, edit the [`docker-build.yml`](core/docker-build.yml) file.

Create a [new release on GitHub](https://github.com/remove-bg/kaleido-removebg/releases).

Make sure to stick to SemVer tag names (e.g. `1.0.0`, no prefix).

Tagged releases are deployed automatically to the production environment for both the API and Core images. There is no need to write
a Description for released versions, as this is filled automatically by the CD process. A [CHANGELOG.md](CHANGELOG.md) file is also
generated automatically.

## :clipboard: Testing

### How to run tests locally
1. Start api, core and rabbitmq via the following docker-compose command:
```bash
COMPUTE_CAPABILITY=[your GPU compute capability] DOCKER_BUILDKIT=1 FURY_AUTH_TOKEN=[your GemFury token] GITHUB_AUTH_TOKEN=[your GitHub Access token]  docker-compose up --build
```
2. Execute tests as the following:
```bash
# change to test directory
cd core/test/
pytest --ignore core
```

### How to run tests locally on a machine without GPU
1. Edit `docker-compose.yml`, and comment out line 79 : `runtime: nvidia`
2. Start api, core and rabbitmq via the following docker-compose command:
```bash
COMPUTE_DEVICE="cpu" COMPUTE_CAPABILITY=75 DOCKER_BUILDKIT=1 FURY_AUTH_TOKEN=[your GemFury token] GITHUB_AUTH_TOKEN=[your GitHub Access token]  docker-compose up --build
```
3. If the docker build fails on `pip install` command, edit Dockerfile as follows:
```
RUN --mount=type=secret,id=fury_auth_token,mode=0444 \
    if [ -f /run/secrets/fury_auth_token ]; then export FURY_AUTH_TOKEN="$(cat /run/secrets/fury_auth_token)"; fi \
 #&& pip install --user --progress-bar off -r requirements-deploy.txt
 && pip install --no-cache-dir --user --progress-bar off -r requirements-deploy.txt
```
5. Execute tests as the following:
```bash
# change to test directory
cd core/test/
pytest --ignore core
```

### How to run core tests locally

1. Make rabbitmq port available by uncommenting the rabbitmq service port section in `docker-compose.yaml`
2. Start core and rabbitmq via the following docker-compose command:
```bash
COMPUTE_CAPABILITY=[your GPU compute capability] DOCKER_BUILDKIT=1 FURY_AUTH_TOKEN=[your GemFury token] GITHUB_AUTH_TOKEN=[your GitHub Access token]  docker-compose up --build core rabbitmq
```
3. Set the following environment variables in your shell:
```bash
REQUEST_QUEUE=remove_bg
RABBITMQ_HOST=127.0.0.1
RABBITMQ_PORT=5672
RABBITMQ_USER=rabbitmq
RABBITMQ_PASSWORD=rabbitmq
```
4. Execute tests as the following:
```bash
# change to test directory
cd core/test/
pytest core/
```
