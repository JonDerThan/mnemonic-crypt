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
