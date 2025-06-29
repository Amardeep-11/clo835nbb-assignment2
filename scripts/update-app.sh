#!/bin/bash
set -e

# Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
ECR_REPOSITORY_NAME="clo835-app"
NEW_VERSION=${1:-v2}

echo "Updating CLO835 Application to Version: $NEW_VERSION"

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME"

echo "AWS Account ID: $AWS_ACCOUNT_ID"
echo "ECR Repository URI: $ECR_REPOSITORY_URI"

# Login to ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPOSITORY_URI

# Build and push new application image
echo "Building new application image..."
docker build -t $ECR_REPOSITORY_URI:$NEW_VERSION -f Dockerfile .

echo "Pushing new application image to ECR..."
docker push $ECR_REPOSITORY_URI:$NEW_VERSION

# Update the deployment with new image
echo "Updating deployment with new image..."
kubectl set image deployment/app-deployment flask-app=$ECR_REPOSITORY_URI:$NEW_VERSION -n clo835-app

# Wait for rollout to complete
echo "Waiting for rollout to complete..."
kubectl rollout status deployment/app-deployment -n clo835-app

echo "Application updated successfully to version $NEW_VERSION!"
echo "Application is accessible at: http://<EC2_PUBLIC_IP>:30080" 