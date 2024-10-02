#!/bin/bash

set -e
shopt -s expand_aliases
alias kubectl='minikube kubectl --'

kubectl delete deployment --all
kubectl delete svc --all


if [ "$1" == "--build-all-apps" ]; then
  echo "Building all apps in ./docker_apps/..."

  # Find all directories that end with '_app' and contain 'build_and_cache.sh'
  for dir in ./docker_apps/*_app; do
    if [ -d "$dir" ] && [ -f "$dir/build_and_cache.sh" ]; then
      echo "Found app directory: $dir"
      echo "Running building app in $dir..."
      (cd "$dir" && ./build_and_cache.sh)
    fi
  done
fi


minikube_status=$(minikube status --format '{{.Host}}')
if [ "$minikube_status" == "Running" ]; then
  echo "Minikube is already running."
else
  echo "Minikube is not running. Starting Minikube..."
  minikube start
fi

CONFIG_YAML="k8s/configmaps/redis-config.yaml"
REDIS_YAML="k8s/deployments/redis-deployment.yaml"
PUB_YAML="k8s/deployments/publisher-deployment.yaml"
SUB_YAML="k8s/deployments/subscriber-deployment.yaml"

echo "Applying yaml with kubectl"
kubectl apply -f $CONFIG_YAML
kubectl apply -f $REDIS_YAML
kubectl apply -f $PUB_YAML
kubectl apply -f $SUB_YAML

echo "Starting Minikube tunnel..."
minikube tunnel > /dev/null 2>&1 &

echo "Waiting for the subscriber service to be ready..."
while [[ -z $(kubectl get svc subscriber-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}') ]]; do
  echo "Waiting for LoadBalancer IP..."
  sleep 3
done

SERVICE_PORT=$(kubectl get svc subscriber-service -o jsonpath='{.spec.ports[0].port}')
SERVICE_IP=$(kubectl get svc subscriber-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "Service is available at http://$SERVICE_IP:$SERVICE_PORT/"
xdg-open "http://$SERVICE_IP:$SERVICE_PORT/" || echo "Open the browser at http://$SERVICE_IP:$SERVICE_PORT/"
