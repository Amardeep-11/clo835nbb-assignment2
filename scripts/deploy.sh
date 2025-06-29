#!/bin/bash
set -e

# Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
ECR_REPOSITORY_NAME="clo835-app"
APP_VERSION=${1:-v1}

echo "Deploying CLO835 Application Version: $APP_VERSION"

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME"

echo "AWS Account ID: $AWS_ACCOUNT_ID"
echo "ECR Repository URI: $ECR_REPOSITORY_URI"

# Create ECR repository if it doesn't exist
echo "Creating ECR repository..."
aws ecr create-repository --repository-name $ECR_REPOSITORY_NAME --region $AWS_REGION || echo "Repository already exists"

# Login to ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPOSITORY_URI

# Build and push application image
echo "Building application image..."
docker build -t $ECR_REPOSITORY_URI:$APP_VERSION -f Dockerfile .

echo "Pushing application image to ECR..."
docker push $ECR_REPOSITORY_URI:$APP_VERSION

# Update Kubernetes manifests with ECR repository URI
echo "Updating Kubernetes manifests..."
find k8s/ -name "*.yaml" -exec sed -i "s|\${ECR_REPOSITORY_URI}|$ECR_REPOSITORY_URI|g" {} \;

# Deploy to Kubernetes
echo "Deploying to Kubernetes..."

# Create namespace
kubectl apply -f k8s/namespace.yaml

# Deploy MySQL
kubectl apply -f k8s/mysql-configmap.yaml
kubectl apply -f k8s/mysql-deployment.yaml
kubectl apply -f k8s/mysql-service.yaml

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/mysql-deployment -n clo835-app

# Deploy application
kubectl apply -f k8s/app-deployment.yaml
kubectl apply -f k8s/app-service.yaml

# Wait for application to be ready
echo "Waiting for application to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/app-deployment -n clo835-app

echo "Deployment completed successfully!"
echo "Application is accessible at: http://<EC2_PUBLIC_IP>:30080"
echo "To get the EC2 public IP, run: kubectl get nodes -o wide" 