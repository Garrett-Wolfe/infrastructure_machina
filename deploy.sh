#!/bin/bash

shopt -s expand_aliases
alias kubectl='minikube kubectl --'


minikube_status=$(minikube status --format '{{.Host}}')
if [ "$minikube_status" == "Running" ]; then
  echo "Minikube is already running."
else
  echo "Minikube is not running. Starting Minikube..."
  minikube start
fi

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

CONFIG_YAML="k8s/configmaps/redis-config.yaml"
REDIS_YAML="k8s/deployments/redis-deployment.yaml"
PUB_YAML="k8s/deployments/publisher-deployment.yaml"
SUB_YAML="k8s/deployments/subscriber-deployment.yaml"

echo "Applying yaml with kubectl"
kubectl apply -f $CONFIG_YAML
kubectl apply -f $REDIS_YAML
kubectl apply -f $PUB_YAML
kubectl apply -f $SUB_YAML


MINIKUBE_IP=$(minikube ip)
SERVICE_PORT=$(kubectl get svc subscriber-service -o jsonpath='{.spec.ports[0].nodePort}')

echo "Waiting for the subscriber service to be ready..."
until kubectl get svc subscriber-service &> /dev/null; do
  echo "Waiting for subscriber-service to be ready..."
  sleep 3
done

echo "Service is available at http://$MINIKUBE_IP:$SERVICE_PORT/"
xdg-open "http://$MINIKUBE_IP:$SERVICE_PORT/" || echo "Open the browser at http://$MINIKUBE_IP:$SERVICE_PORT/"
