FROM harbor.uio.no/mirrors/docker.io/library/python:3.10-slim

LABEL no.uio.contact=bnt-int@usit.uio.no

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg2 \
    less \
    nano \
    git \
    && rm -rf /var/lib/apt/lists/*

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN pip3 install poetry gunicorn

RUN mkdir /zapip
WORKDIR /zapip
COPY pyproject.toml /zapip
COPY poetry.lock /zapip
RUN poetry install --no-dev --no-interaction

COPY . /zapip

# Collect static files from django
RUN python manage.py collectstatic --no-input

# Support arbitrarily assigned UIDs by making the root group
# the owner of our directory.
RUN chgrp -R 0 /zapip && \
    chmod -R g=u /zapip
