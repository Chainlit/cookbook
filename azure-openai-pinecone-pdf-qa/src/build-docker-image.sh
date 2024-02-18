#!/bin/bash

# Variables
source ./variables.sh

# Build the docker image
 docker build --platform=linux/arm64 -t $docImageName:$tag -f Dockerfile --build-arg FILENAME=$docAppFile --build-arg PORT=$port .
#docker build --platform=linux/amd64 -t $docImageName:$tag -f Dockerfile --build-arg FILENAME=$docAppFile --build-arg PORT=$port .