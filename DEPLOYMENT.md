# Production Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- AWS account with S3 bucket configured
- MongoDB Atlas or local MongoDB
- Redis instance (local or AWS ElastiCache)
- Gemini API key
- Environment variables configured

## Environment Variables

Create a `.env` file in the project root:

```env
# MongoDB
MONGODB_URI=mongodb://localhost:27017/stepone

# Redis
REDIS_URL=redis://localhost:6379/0

# AWS
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-bucket-name

# Gemini
GEMINI_API_KEY=your_gemini_api_key

# JWT
JWT_SECRET_KEY=your_secret_key_here

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Confidence Threshold
CONFIDENCE_THRESHOLD=0.7
```

## Local Deployment with Docker Compose

1. Build and start all services:
```bash
docker-compose up -d --build
```

2. Services will be available at:
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- MongoDB: localhost:27017
- Redis: localhost:6379

3. View logs:
```bash
docker-compose logs -f backend
docker-compose logs -f celery_worker
docker-compose logs -f frontend
```

4. Stop services:
```bash
docker-compose down
```

## AWS EKS Deployment

### Backend Deployment

1. Build and push Docker image to ECR:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker build -t stepone-backend ./backend
docker tag stepone-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/stepone-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/stepone-backend:latest
```

2. Deploy to EKS using kubectl:
```bash
kubectl apply -f infrastructure/k8s/backend-deployment.yaml
kubectl apply -f infrastructure/k8s/backend-service.yaml
```

### Frontend Deployment

1. Build and push Docker image:
```bash
docker build -t stepone-frontend ./frontend
docker tag stepone-frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/stepone-frontend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/stepone-frontend:latest
```

2. Deploy to EKS:
```bash
kubectl apply -f infrastructure/k8s/frontend-deployment.yaml
kubectl apply -f infrastructure/k8s/frontend-service.yaml
```

### Celery Worker Deployment

Deploy Celery workers as separate pods:
```bash
kubectl apply -f infrastructure/k8s/celery-deployment.yaml
```

## Monitoring and Scaling

### Horizontal Pod Autoscaler

Configure HPA for backend:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Health Checks

Backend health check:
```bash
curl http://localhost:8000/health
```

Celery worker health:
```bash
celery -A app.tasks.processing_tasks inspect active
```

## Security Considerations

1. Use secrets manager for sensitive data (AWS Secrets Manager)
2. Enable HTTPS with TLS certificates
3. Configure network policies for pod-to-pod communication
4. Use IAM roles for service accounts
5. Enable CloudFront CDN for static assets
6. Configure WAF rules for API protection

## Backup and Recovery

- MongoDB: Enable automated backups in Atlas
- S3: Enable versioning and cross-region replication
- Redis: Enable AOF persistence and snapshots
- Application logs: Ship to CloudWatch Logs

## Troubleshooting

### Backend fails to start
- Check environment variables
- Verify MongoDB and Redis connectivity
- Check logs: `docker-compose logs backend`

### Celery tasks not executing
- Verify Redis connection
- Check Celery worker logs
- Ensure tasks are registered correctly

### Frontend build fails
- Check Node.js version (requires 18+)
- Verify API URL in environment
- Check for dependency conflicts

### WebSocket connection issues
- Verify WebSocket endpoint is accessible
- Check firewall/security group rules
- Ensure CORS is configured correctly
