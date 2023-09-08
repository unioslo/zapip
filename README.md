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
    $ touch zapipsite/settings/local.py

## Development

    python manage.py migrate
    # python manage.py loaddata testdata
    # python manage.py createsuperuser
    python manage.py runserver

## Testing

    python manage.py test

## Static Type Analysis

Use [mypy](http://mypy-lang.org/) to run static type checks using type hints.

    $ PYTHONPATH=. mypy .  # Generate a problem report.

## Docker

A `Containerfile` is provided for application deployment purposes. It is not meant to be used for development.

`update-harbor-image.sh` is a utility script for building and uploading a Docker image to our private image repository `harbor.uio.no`.

It expects you to be logged in:

    podman login harbor.uio.no

## Deployment

See the [zapip-deploy repository](https://github.uio.no/IT-INT/zapip-deploy).

## API gateway configuration

This application expects to be proxied by an API gateway, which should take the role
of managing per-application API keys and telling Zapip about the authenticated
application via HTTP headers. The gateway should also autenticate itself.

In Gravitee, this can be done by applying a *Transform Headers* policy with scope *REQUEST*,
adding the following headers:

| Name               | Value                                |
|--------------------|--------------------------------------|
| X-Api              | {#context.attributes['api']}         |
| X-Api-Subscription | {#context.attributes['user-id']}     |
| X-Api-Application  | {#context.attributes['application']} |
| X-Zapip-Api-Key    | {#properties['zapip-api-key']}       |

`X-Zapip-Api-Key` authenticates the gateway, and is checked against the setting `HEADER_AUTH` in Django.

Zapip also expects to see a request ID in `X-Gravitee-Transaction-Id`. This may be
overridden with the setting `LOG_REQUEST_ID_HEADER`.
