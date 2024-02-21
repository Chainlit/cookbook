#!/bin/bash

# Variables
source ./variables.sh

# Print the text
echo "Running the docker Container "

# Run the docker container
#docker run -p $port:$port $docImageName:$tag
docker run -it \
      --rm \
      -p $port:$port \
      -e AZURE_OPENAI_KEY=$AZURE_OPENAI_KEY \
      --name $docImageName \
      $docImageName:$tag