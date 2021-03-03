#!/bin/sh

set -ex

GIT_BRANCH=`git rev-parse --abbrev-ref HEAD`
GIT_SHA=`git rev-parse --short HEAD`
REPO="harbor.uio.no"
PROJECT="it-usit-int-drift"
APP_NAME="zapip"
CONTAINER="${REPO}/${PROJECT}/${APP_NAME}"
IMAGE_TAG="${CONTAINER}:${GIT_BRANCH}-${GIT_SHA}"

echo "Generating .dockerignore"
echo ".*
*" > .dockerignore
git ls-tree --name-only HEAD | sed 's/^/!/' >> .dockerignore
echo "zapipsite/settings/local.py" >> .dockerignore

if command -v podman > /dev/null 2>&1; then
  BUILDER=$(command -v podman)
elif command -v docker > /dev/null 2>&1; then
  BUILDER=$(command -v docker)
else
  echo "Missing podman or docker CLI tools"
  exit 1
fi
echo "Will build using $BUILDER"

echo "Building $IMAGE_TAG"
$BUILDER build --format docker --no-cache -t $IMAGE_TAG .

echo "Pushing $IMAGE_TAG"
$BUILDER push $IMAGE_TAG

if [ $GIT_BRANCH = "master" ]; then
  echo "On master branch, setting $IMAGE_TAG as $CONTAINER:latest"
  $BUILDER tag $IMAGE_TAG $CONTAINER:latest
  $BUILDER push $CONTAINER:latest
fi
