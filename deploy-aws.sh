#!/bin/bash

# AWS ECS Deployment Script
# Usage: bash deploy-aws.sh <region> <account-id>

set -e

REGION="${1:-us-east-1}"
AWS_ACCOUNT_ID="${2:$AWS_ACCOUNT_ID}"
ECR_REGISTRY=$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

echo "🚀 Deploying to Amazon Web Services..."
echo "Region: $REGION"
echo "AWS Account: $AWS_ACCOUNT_ID"
echo ""

# Configure AWS
echo "🔐 Configuring AWS CLI..."
aws configure

# Create ECR repositories
echo "📦 Creating ECR repositories..."
aws ecr create-repository --repository-name mlop-api --region $REGION || echo "mlop-api repo exists"
aws ecr create-repository --repository-name mlop-ui --region $REGION || echo "mlop-ui repo exists"

# Login to ECR
echo "🔐 Logging in to ECR..."
aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin $ECR_REGISTRY

# Build and push images
echo "🔨 Building Docker images..."
docker build -f deploy/Dockerfile.api -t $ECR_REGISTRY/mlop-api:latest .
docker build -f deploy/Dockerfile.ui -t $ECR_REGISTRY/mlop-ui:latest .

echo "📤 Pushing images to ECR..."
docker push $ECR_REGISTRY/mlop-api:latest
docker push $ECR_REGISTRY/mlop-ui:latest

# Create CloudWatch logs
echo "📋 Creating CloudWatch log groups..."
aws logs create-log-group --log-group-name /ecs/mlop-api --region $REGION || echo "Log group exists"
aws logs create-log-group --log-group-name /ecs/mlop-ui --region $REGION || echo "Log group exists"

# Create ECS cluster
echo "🔧 Creating ECS cluster..."
aws ecs create-cluster --cluster-name mlop-cluster --region $REGION || echo "Cluster exists"

# Register task definitions
echo "📝 Registering task definitions..."
sed -i "s/ACCOUNT_ID/$AWS_ACCOUNT_ID/g; s/REGION/$REGION/g" aws/ecs-task-definition-api.json
sed -i "s/ACCOUNT_ID/$AWS_ACCOUNT_ID/g; s/REGION/$REGION/g" aws/ecs-task-definition-ui.json

aws ecs register-task-definition \
  --cli-input-json file://aws/ecs-task-definition-api.json \
  --region $REGION

aws ecs register-task-definition \
  --cli-input-json file://aws/ecs-task-definition-ui.json \
  --region $REGION

echo ""
echo "✅ AWS deployment setup complete!"
echo ""
echo "Next steps:"
echo "1. Create ECS services for mlop-api and mlop-ui"
echo "2. Configure load balancers"
echo "3. Set up auto-scaling"
echo ""
echo "💡 View logs:"
echo "   aws logs tail /ecs/mlop-api --follow"
echo "   aws logs tail /ecs/mlop-ui --follow"
