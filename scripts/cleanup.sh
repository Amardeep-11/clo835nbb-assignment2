#!/bin/bash
set -e

echo "Cleaning up CLO835 Kubernetes deployment..."

# Delete all resources in the namespace
echo "Deleting Kubernetes resources..."
kubectl delete namespace clo835-app --ignore-not-found=true

# Wait for namespace deletion
echo "Waiting for namespace deletion..."
kubectl wait --for=delete namespace/clo835-app --timeout=300s || echo "Namespace already deleted"

# Delete kind cluster
echo "Deleting kind cluster..."
kind delete cluster --name clo835-cluster || echo "Cluster already deleted"

echo "Cleanup completed successfully!" 