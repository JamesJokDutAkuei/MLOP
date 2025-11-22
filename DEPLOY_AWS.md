# 🚀 Deploy to AWS ECS (More Control)

## Prerequisites
```bash
# Install AWS CLI
brew install awscli

# Configure AWS credentials
aws configure
# Enter: AWS Access Key, Secret Key, Region (us-east-1), Output format (json)

# Install AWS CDK (optional, for infrastructure-as-code)
npm install -g aws-cdk
```

## Step 1: Create ECR Repository
```bash
# Create Docker registry
aws ecr create-repository --repository-name mlop-api --region us-east-1
aws ecr create-repository --repository-name mlop-ui --region us-east-1

# Get login token
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
```

## Step 2: Push Docker Images
```bash
# Build and tag API image
docker build -t mlop-api:latest -f deploy/Dockerfile.api .
docker tag mlop-api:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/mlop-api:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/mlop-api:latest

# Build and tag UI image
docker build -t mlop-ui:latest -f deploy/Dockerfile.ui .
docker tag mlop-ui:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/mlop-ui:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/mlop-ui:latest
```

## Step 3: Create ECS Cluster
```bash
# Create cluster
aws ecs create-cluster --cluster-name mlop-cluster --region us-east-1

# Create CloudWatch log group
aws logs create-log-group --log-group-name /ecs/mlop --region us-east-1
```

## Step 4: Create Task Definition
```bash
# Register task definition for API
aws ecs register-task-definition --cli-input-json file://aws-api-task.json

# Register task definition for UI
aws ecs register-task-definition --cli-input-json file://aws-ui-task.json
```

## Step 5: Create ECS Service
```bash
# Create service for API
aws ecs create-service \
  --cluster mlop-cluster \
  --service-name mlop-api-service \
  --task-definition mlop-api:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}" \
  --region us-east-1

# Create service for UI
aws ecs create-service \
  --cluster mlop-cluster \
  --service-name mlop-ui-service \
  --task-definition mlop-ui:1 \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}" \
  --region us-east-1
```

## Step 6: Setup Application Load Balancer
```bash
# Create load balancer
aws elbv2 create-load-balancer \
  --name mlop-alb \
  --subnets subnet-12345 subnet-67890 \
  --security-groups sg-12345 \
  --scheme internet-facing \
  --type application \
  --region us-east-1

# Create target group for API
aws elbv2 create-target-group \
  --name mlop-api-targets \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-12345 \
  --region us-east-1

# Create listener
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:... \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:... \
  --region us-east-1
```

## Monitoring
```bash
# View running tasks
aws ecs list-tasks --cluster mlop-cluster --region us-east-1

# View service details
aws ecs describe-services --cluster mlop-cluster --services mlop-api-service --region us-east-1

# View logs
aws logs tail /ecs/mlop --follow
```

## Cleanup
```bash
# Delete service
aws ecs delete-service --cluster mlop-cluster --service mlop-api-service --force

# Delete cluster
aws ecs delete-cluster --cluster mlop-cluster

# Delete ECR repositories
aws ecr delete-repository --repository-name mlop-api --force
aws ecr delete-repository --repository-name mlop-ui --force
```

---

**Why AWS ECS is harder:**
- More services to configure (ECR, ECS, ALB, Security Groups, VPC, IAM)
- Requires understanding AWS networking
- More moving parts = more things to break

**Use AWS ECS if you need:**
- Long-running services (Kubernetes-like control)
- Persistent storage
- Complex networking
- Enterprise features
