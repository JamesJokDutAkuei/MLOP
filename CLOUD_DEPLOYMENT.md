# 🚀 Cloud Deployment Guide

This guide covers deploying the Brain Tumor MRI Classifier to Google Cloud Platform (GCP) and Amazon Web Services (AWS).

---

## 📋 Prerequisites

### For GCP
- Google Cloud Account
- `gcloud` CLI installed: https://cloud.google.com/sdk/docs/install
- Docker installed
- Project ID ready

### For AWS
- AWS Account
- AWS CLI installed: https://aws.amazon.com/cli/
- Docker installed
- AWS credentials configured

---

## 🔷 Google Cloud Platform (GCP) Deployment

### Option 1: Cloud Run (Recommended - Serverless)

**Best for:** Quick deployment, auto-scaling, pay-per-use

#### Step 1: Setup GCP Project

```bash
# Set your project
export PROJECT_ID="your-project-id"
export REGION="us-central1"

gcloud config set project $PROJECT_ID
gcloud config set compute/region $REGION

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

#### Step 2: Build and Push Docker Images

```bash
cd /Users/apple/MLOP

# Configure Docker for GCP
gcloud auth configure-docker

# Build API image
docker build -f deploy/Dockerfile.api -t gcr.io/$PROJECT_ID/mlop-api:latest .
docker push gcr.io/$PROJECT_ID/mlop-api:latest

# Build UI image
docker build -f deploy/Dockerfile.ui -t gcr.io/$PROJECT_ID/mlop-ui:latest .
docker push gcr.io/$PROJECT_ID/mlop-ui:latest
```

#### Step 3: Deploy API to Cloud Run

```bash
# Deploy API
gcloud run deploy mlop-api \
  --image gcr.io/$PROJECT_ID/mlop-api:latest \
  --platform managed \
  --region $REGION \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 10 \
  --allow-unauthenticated

# Get API URL
API_URL=$(gcloud run services describe mlop-api --platform managed --region $REGION --format 'value(status.url)')
echo "API URL: $API_URL"
```

#### Step 4: Deploy UI to Cloud Run

```bash
# Deploy UI
gcloud run deploy mlop-ui \
  --image gcr.io/$PROJECT_ID/mlop-ui:latest \
  --platform managed \
  --region $REGION \
  --memory 1Gi \
  --cpu 1 \
  --timeout 3600 \
  --max-instances 5 \
  --allow-unauthenticated \
  --set-env-vars "API_URL=$API_URL"

# Get UI URL
UI_URL=$(gcloud run services describe mlop-ui --platform managed --region $REGION --format 'value(status.url)')
echo "UI URL: $UI_URL"
```

#### Step 5: Verify Deployment

```bash
# Test API
curl -s $API_URL/health | python3 -m json.tool

# Access UI
echo "Open in browser: $UI_URL"
```

---

### Option 2: Kubernetes Engine (GKE)

**Best for:** Complex deployments, multi-region, enterprise

#### Step 1: Create GKE Cluster

```bash
# Create cluster
gcloud container clusters create mlop-cluster \
  --num-nodes 3 \
  --machine-type n1-standard-2 \
  --region $REGION \
  --enable-autoscaling \
  --min-nodes 2 \
  --max-nodes 10

# Get credentials
gcloud container clusters get-credentials mlop-cluster --region $REGION
```

#### Step 2: Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace mlop

# Create deployment manifest
cat > k8s/deployment.yaml <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mlop-api
  namespace: mlop
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mlop-api
  template:
    metadata:
      labels:
        app: mlop-api
    spec:
      containers:
      - name: api
        image: gcr.io/$PROJECT_ID/mlop-api:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: mlop-api-service
  namespace: mlop
spec:
  type: LoadBalancer
  selector:
    app: mlop-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
EOF

# Apply deployment
kubectl apply -f k8s/deployment.yaml

# Check deployment
kubectl get deployments -n mlop
kubectl get pods -n mlop
kubectl get services -n mlop
```

---

## 🟠 Amazon Web Services (AWS) Deployment

### Option 1: AWS Elastic Container Service (ECS)

**Best for:** Managed containers, EC2 or Fargate

#### Step 1: Setup AWS Account

```bash
# Configure AWS CLI
aws configure
export AWS_REGION="us-east-1"
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export ECR_REGISTRY=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
```

#### Step 2: Create ECR Repositories

```bash
# Create ECR repos
aws ecr create-repository --repository-name mlop-api --region $AWS_REGION
aws ecr create-repository --repository-name mlop-ui --region $AWS_REGION

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin $ECR_REGISTRY
```

#### Step 3: Build and Push Images

```bash
cd /Users/apple/MLOP

# Build and push API
docker build -f deploy/Dockerfile.api -t $ECR_REGISTRY/mlop-api:latest .
docker push $ECR_REGISTRY/mlop-api:latest

# Build and push UI
docker build -f deploy/Dockerfile.ui -t $ECR_REGISTRY/mlop-ui:latest .
docker push $ECR_REGISTRY/mlop-ui:latest
```

#### Step 4: Create ECS Cluster

```bash
# Create cluster
aws ecs create-cluster --cluster-name mlop-cluster --region $AWS_REGION

# Create task definition
cat > ecs-task-definition.json <<EOF
{
  "family": "mlop-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "$ECR_REGISTRY/mlop-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000,
          "protocol": "tcp"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/mlop-api",
          "awslogs-region": "$AWS_REGION",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
EOF

# Register task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json --region $AWS_REGION
```

#### Step 5: Create ECS Service

```bash
# Create VPC and subnets (if needed)
# Or use default VPC/subnets

# Create service
aws ecs create-service \
  --cluster mlop-cluster \
  --service-name mlop-api-service \
  --task-definition mlop-api \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxxxxx],securityGroups=[sg-xxxxxxxx],assignPublicIp=ENABLED}" \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=api,containerPort=8000 \
  --region $AWS_REGION
```

---

### Option 2: AWS Lambda + API Gateway

**Best for:** Lightweight, event-driven, serverless

Create `serverless.yml`:

```yaml
service: mlop-api

frameworkVersion: '3'

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  environment:
    MODEL_PATH: /opt/models/brain_tumor_model_v1.h5

functions:
  predict:
    handler: src/lambda_handler.predict
    timeout: 60
    memory: 3008
    events:
      - http:
          path: predict
          method: post
          cors: true
  
  health:
    handler: src/lambda_handler.health
    events:
      - http:
          path: health
          method: get
          cors: true

plugins:
  - serverless-python-requirements

custom:
  pythonRequirements:
    dockerizePip: true
```

Deploy with:

```bash
npm install -g serverless
serverless deploy
```

---

## 📊 Load Testing

### Run Load Tests

```bash
# Install Locust
pip install locust

# Run load test
locust -f locustfile.py \
  --host=http://localhost:8000 \
  --users=100 \
  --spawn-rate=10 \
  --run-time=5m \
  --headless \
  --csv=logs/locust_results

# With web UI (accessible at http://localhost:8089)
locust -f locustfile.py --host=http://localhost:8000
```

### Analyze Results

```bash
# Results saved to:
# - logs/locust_results_stats.csv
# - logs/locust_results_failures.csv
# - logs/locust_results_requests.csv
```

---

## 📈 Monitoring & Scaling

### GCP Cloud Run Auto-Scaling
```bash
gcloud run services update mlop-api \
  --max-instances 20 \
  --cpu-throttling \
  --region $REGION
```

### AWS Auto Scaling
```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/mlop-cluster/mlop-api-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10

# Create scaling policy
aws application-autoscaling put-scaling-policy \
  --policy-name mlop-scaling \
  --service-namespace ecs \
  --resource-id service/mlop-cluster/mlop-api-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{"TargetValue": 70, "PredefinedMetricSpecification": {"PredefinedMetricType": "ECSServiceAverageCPUUtilization"}}'
```

---

## 💰 Cost Optimization

### GCP
- Use Cloud Run with pay-per-use pricing
- Set appropriate memory/CPU limits
- Use `--max-instances` to control costs
- Monitor usage in Cloud Console

### AWS
- Use Fargate Spot for non-critical workloads
- Set up auto-scaling with cost controls
- Use Reserved Instances for baseline load
- Monitor CloudWatch metrics

---

## 🔐 Security Best Practices

1. **Never commit secrets** - Use environment variables
2. **Use private registries** - ECR/GCP Container Registry
3. **Enable authentication** - Cloud Identity/IAM
4. **Network security** - VPCs, security groups, firewalls
5. **Monitoring** - CloudWatch/Stackdriver for logs
6. **SSL/TLS** - Always use HTTPS in production

---

## 📞 Troubleshooting

### GCP Cloud Run Issues
```bash
# View logs
gcloud run services logs read mlop-api

# Check service status
gcloud run services describe mlop-api --platform managed
```

### AWS ECS Issues
```bash
# View task logs
aws logs tail /ecs/mlop-api --follow

# Check task status
aws ecs describe-tasks --cluster mlop-cluster --tasks <task-arn>
```

---

## ✅ Deployment Checklist

- [ ] Docker images built and tested locally
- [ ] Images pushed to registry (GCP/AWS)
- [ ] Environment variables configured
- [ ] Security groups/VPC configured
- [ ] Load balancer set up
- [ ] Health checks working
- [ ] Monitoring/logging configured
- [ ] Auto-scaling policies set
- [ ] Cost tracking enabled
- [ ] Backup/recovery plan documented

---

**Ready to deploy!** Choose your platform and follow the steps above. 🚀
