#!/bin/sh

# Load variables
. ./variables.sh

# Login to ACR
echo "Logging in to [$acrName] container registry..."
az acr login --name "$(echo "$acrName" | tr '[:upper:]' '[:lower:]')"

# Retrieve ACR login server
echo "Retrieving login server for the [$acrName] container registry..."
loginServer=$(az acr show --name "$(echo "$acrName" | tr '[:upper:]' '[:lower:]')" --query loginServer --output tsv)

# Push the local docker images to the Azure Container Registry
echo "Pushing the local docker images to the [$acrName] container registry..."
docker tag "$(echo "$docImageName" | tr '[:upper:]' '[:lower:]'):$tag" "$loginServer/$(echo "$docImageName" | tr '[:upper:]' '[:lower:]'):$tag"
docker push "$loginServer/$(echo "$docImageName" | tr '[:upper:]' '[:lower:]'):$tag"