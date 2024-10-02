#!/bin/bash

shopt -s expand_aliases
alias kubectl='minikube kubectl --'

IMAGE_NAME="publisher"
IMAGE_TAG="latest"

minikube_status=$(minikube status --format '{{.Host}}')

if [ "$minikube_status" == "Running" ]; then
  echo "Minikube is already running."
else
  echo "Minikube is not running. Starting Minikube..."
  minikube start
fi

docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

kubectl delete deployment ${IMAGE_NAME}-deployment
minikube ssh -- docker rmi ${IMAGE_NAME}:${IMAGE_TAG}

minikube image load ${IMAGE_NAME}:${IMAGE_TAG}
echo "Docker image ${IMAGE_NAME}:${IMAGE_TAG} added to Minikube cache"

kubectl rollout restart deployment ${IMAGE_NAME}-deployment

echo "All images in minikube:"
minikube ssh -- docker images
