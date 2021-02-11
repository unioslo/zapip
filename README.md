# Zapip

Zoom-API-proxy

## Installation

[Poetry](https://python-poetry.org/docs/) is used for dependency management.

    # Make sure poetry is installed, see docs
    poetry shell        # Start a shell, creating a virtual environment.
    poetry install      # Install dependencies from lock file

## Local configuration

Local configuration is read from `zapipsite/settings/local.py`.

    # Make sure a local settings file exists
    $ touch zapipsite/settings/local.py

## Development

    python manage.py migrate
    # python manage.py loaddata testdata
    # python manage.py createsuperuser
    python manage.py runserver

## Testing

    python manage.py test

## Static Type Analysis

Use [mypy](http://mypy-lang.org/) to run static type checks using type hints.

    $ PYTHONPATH=. mypy .  # Generate a problem report.

## Docker

A `Dockerfile` is provided for application deployment purposes. It is not meant to be used for development.

`update-harbor-image.sh` is a utility script for building and uploading a Docker image to our private image repository `harbor.uio.no`.

It expects you to be logged in:

    docker login harbor.uio.no

## Deployment

See the [zapip-deploy repository](https://bitbucket.usit.uio.no/projects/INT/repos/zapip-deploy/browse).
