# Contributing

## Setup

Setup a virtual environment:

```sh
# Create virtual environment in a new `.venv/` folder:
python3 -m venv .venv
# Activate virtual environment (do this every time you open a new shell):
source .venv/bin/activate
```

In the virtual environment, install all dependencies:

```sh
# NOT RECOMMENDED:
# Install frozen dependencies:
python3 -m pip install -r requirements.txt
# RECOMMENDED:
# Install newest dependency versions and also tell your python environment about
# this project:
python3 -m pip install -e .
```

## Tests

Run unittests:

```sh
python3 -m unittest discover tests/unittests/
# If this doesn't work, try the following:
PYTHONPATH=src python3 -m unittest discover tests/unittests/
```

## Building

Install the `build` package: `python3 -m pip install --upgrade build`, then run:

```sh
python3 -m build
```

## Deployment

Deployment is handled by GitHub actions. For a new version, create a new tag on
the main branch `git tag v1.2.3`, and push it with `git push origin v1.2.3`.
Make sure `1.2.3` is the same as the version in `pyproject.toml`! Make sure this
is a version that was not yet published to PyPI! 

The workflow publishes to PyPI and also creates a GitHub release with the built
distribution files. You can also create a GitHub release manually, the
associated tag triggers the same workflow, and the distribution files are then
added to the release automatically.

### Standalone Binaries

To create standalone binaries `pyinstaller` is used. It can be installed with
`pip install -e ".[deployment]"`. On first usage, pyinstaller creates a `.spec`
file which stores most of the command line parameters. The commands used to
create the files are listed here:

```sh
pyinstaller --name mnemonic_crypt --distpath bin --onefile --add-data src/mnemonic_crypt/wordlists/:mnemonic_crypt/wordlists/ src/mnemonic_crypt/__main__.py
pyinstaller --name mnemonic_crypt_gui --distpath bin --onefile --add-data src/mnemonic_crypt/wordlists/:mnemonic_crypt/wordlists/ src/mnemonic_crypt/gui/__main__.py
```

With the spec files, a very succinct command then achieves the same result, see
the `.github/workflows/` directory for exact usage.
