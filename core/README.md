# kaleido-core-removebg

This `removebg-core` package is [published on GemFury](https://manage.fury.io/dashboard/kaleido/package/pkg_1Pz7bq/)

## 🐳 Docker

In addition to the Python package, this repository also contains a [Docker image](Dockerfile) for `removebg-core`.

For each [release](https://github.com/remove-bg/kaleido-core-removebg/releases), several images are being built
and pushed to the Docker registry.

Configure which Docker images should be built in [`docker-build.yml`](docker-build.yml).

The resulting images will be tagged `[version]-pt[pytorch-version]-cc[compute-compatibility]`.

You can find the list of built images in the release description.

## 🚀 Installation

To use this package, add it to your `requirements.txt`. It depends on the
[`kaleido-core`](https://github.com/remove-bg/kaleido-core-lib) package, so add that before:

```bash
# requirements.txt
--extra-index-url https://${FURY_AUTH_TOKEN}:@deps.kaleido.ai/pypi/
kaleido-core==x.y.z
removebg-core==x.y.z
```

Then pass [your GemFury token](https://gemfury.com/help/tokens/) to the `pip install` command like so (or
have in your system environment).

```bash
FURY_AUTH_TOKEN=<your token> pip install -r requirements.txt
```

## 📝 Changelog

See [ChangeLog](ChangeLog).

## 🧱 Building

After all prerequisites are satisfied, you can create a source distribution in the [dist](dist) directory
with this command.

```bash
python setup.py sdist
```

Use `bdist` to build a binary distribution, `bdist_wheel` to build a binary wheel.

## 🚚 Release Process

- Modify [the versions](https://github.com/remove-bg/kaleido-core-removebg/blob/master/Dockerfile#L29-L38) of the packages
  you want to use in the [`Dockerfile`](Dockerfile). There is generally no need to modify the
  [`REMOVEBG_CORE_PY_VERSION`](https://github.com/remove-bg/kaleido-core-removebg/blob/master/Dockerfile#L38) version, as
  this is being replaced with whatever release version you tag in the next steps.
- Create a [new release on GitHub](https://github.com/remove-bg/kaleido-core-removebg/releases), making
  sure to stick to [SemVer](https://semver.org) tag names (e.g. `1.0.0`, no prefix).
- A release will be created [automatically by CircleCI](https://app.circleci.com/pipelines/github/remove-bg/kaleido-core-removebg)
  and [uploaded to GemFury](https://manage.fury.io/dashboard/kaleido/package/pkg_1Pz7bq/).
- In the `master` branch, run `python setup.py install` to update [`AUTHORS`](AUTHORS) and [`ChangeLog`](ChangeLog)
