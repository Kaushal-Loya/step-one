# AWS Infrastructure Setup Guide

This guide walks through setting up all required AWS resources for the StepOne AI Content & Design Engine.

## Prerequisites

- AWS Account with admin access
- AWS CLI installed and configured
- Terraform installed (optional, for IaC)

## Step 1: S3 Buckets

### Media Storage Bucket
```bash
aws s3api create-bucket \
    --bucket stepone-media \
    --region us-east-1 \
    --create-bucket-configuration LocationConstraint=us-east-1
```

### CDN Bucket
```bash
aws s3api create-bucket \
    --bucket stepone-media-cdn \
    --region us-east-1 \
    --create-bucket-configuration LocationConstraint=us-east-1
```

### Enable Versioning
```bash
aws s3api put-bucket-versioning \
    --bucket stepone-media \
    --versioning-configuration Status=Enabled
```

### Bucket Policy (for public CDN access)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::stepone-media-cdn/*"
    }
  ]
}
```

## Step 2: MongoDB Atlas

1. Go to https://www.mongodb.com/cloud/atlas
2. Create free account (or sign in)
3. Create new cluster:
   - Name: stepone-cluster
   - Tier: M10 (recommended for production) or M0 (free for dev)
   - Region: us-east-1
4. Create database user:
   - Username: stepone_admin
   - Password: [generate strong password]
   - Role: Atlas Admin
5. Whitelist IP: 0.0.0.0/0 (for development) or specific IP
6. Get connection string:
   ```
   mongodb+srv://stepone_admin:password@stepone-cluster.mongodb.net/stepone_ai?retryWrites=true&w=majority
   ```

## Step 3: Redis ElastiCache

```bash
# Create subnet group
aws elasticache create-cache-subnet-group \
    --cache-subnet-group-name stepone-redis-subnet \
    --cache-subnet-group-description "Subnet group for Redis" \
    --subnet-ids subnet-xxxxx subnet-yyyyy

# Create Redis cluster
aws elasticache create-replication-group \
    --replication-group-id stepone-redis \
    --replication-group-description "Redis for StepOne AI" \
    --cache-node-type cache.t3.micro \
    --engine redis \
    --num-cache-clusters 1 \
    --cache-subnet-group-name stepone-redis-subnet \
    --security-group-ids sg-xxxxx
```

## Step 4: CloudFront Distribution

```bash
aws cloudfront create-distribution \
    --distribution-config file://cloudfront-config.json
```

### cloudfront-config.json
```json
{
  "CallerReference": "stepone-cdn-2026",
  "Comment": "StepOne AI CDN",
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-stepone-media-cdn",
    "ViewerProtocolPolicy": "allow-all",
    "MinTTL": 0,
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {
        "Forward": "none"
      }
    }
  },
  "Origins": {
    "Items": [
      {
        "Id": "S3-stepone-media-cdn",
        "DomainName": "stepone-media-cdn.s3.amazonaws.com",
        "S3OriginConfig": {}
      }
    ],
    "Quantity": 1
  },
  "Enabled": true
}
```

## Step 5: AWS Secrets Manager

Store all sensitive credentials:

```bash
# API Keys
aws secretsmanager create-secret \
    --name stepone/ai/gemini-api-key \
    --secret-string "your-gemini-api-key"

aws secretsmanager create-secret \
    --name stepone/ai/anthropic-api-key \
    --secret-string "your-anthropic-api-key"

# Database credentials
aws secretsmanager create-secret \
    --name stepone/db/mongodb-uri \
    --secret-string "mongodb+srv://..."

# AWS credentials
aws secretsmanager create-secret \
    --name stepone/aws/access-key-id \
    --secret-string "your-access-key-id"

aws secretsmanager create-secret \
    --name stepone/aws/secret-access-key \
    --secret-string "your-secret-access-key"
```

## Step 6: IAM Roles

### EKS Cluster Role
```bash
aws iam create-role \
    --role-name stepone-eks-cluster-role \
    --assume-role-policy-document file://eks-trust-policy.json

aws iam attach-role-policy \
    --role-name stepone-eks-cluster-role \
    --policy-arn arn:aws:iam::aws:policy/AmazonEKSClusterPolicy
```

### EKS Node Role
```bash
aws iam create-role \
    --role-name stepone-eks-node-role \
    --assume-role-policy-document file://node-trust-policy.json

aws iam attach-role-policy \
    --role-name stepone-eks-node-role \
    --policy-arn arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy

aws iam attach-role-policy \
    --role-name stepone-eks-node-role \
    --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly

aws iam attach-role-policy \
    --role-name stepone-eks-node-role \
    --policy-arn arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy
```

## Step 7: EKS Cluster (for Kubernetes deployment)

```bash
# Create cluster
aws eks create-cluster \
    --name stepone-eks \
    --role-arn arn:aws:iam::ACCOUNT_ID:role/stepone-eks-cluster-role \
    --resources-vpc-config subnetIds=subnet-xxxxx,subnet-yyyyy,securityGroupIds=sg-xxxxx

# Create node group
aws eks create-nodegroup \
    --cluster-name stepone-eks \
    --nodegroup-name stepone-node-group \
    --node-role arn:aws:iam::ACCOUNT_ID:role/stepone-eks-node-role \
    --subnets subnet-xxxxx subnet-yyyyy \
    --scaling-config minSize=2,maxSize=5,desiredSize=2 \
    --instance-types t3.medium
```

## Environment Variables Summary

After setup, update your `.env` file with:

```bash
# Database
MONGODB_URI=mongodb+srv://stepone_admin:password@stepone-cluster.mongodb.net/stepone_ai?retryWrites=true&w=majority
MONGODB_DB=stepone_ai
REDIS_URL=redis://stepone-redis.xxxxxx.use1.cache.amazonaws.com:6379/0

# S3
AWS_ACCESS_KEY_ID=AKIAXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxx
AWS_REGION=us-east-1
S3_BUCKET=stepone-media
S3_BUCKET_CDN=stepone-media-cdn

# AI APIs
GEMINI_API_KEY=xxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxx
```

## Cost Estimates (Monthly)

- S3 Storage: ~$20-50 (depending on usage)
- MongoDB Atlas M10: ~$57
- Redis ElastiCache: ~$25 (t3.micro)
- CloudFront: ~$10-20 (depending on traffic)
- EKS: ~$70 (2 x t3.medium nodes)
- Secrets Manager: ~$0.40 per secret

**Total**: ~$180-250/month for production

## Next Steps

Once infrastructure is set up:
1. Update backend/.env with actual credentials
2. Test database connection
3. Test S3 upload/download
4. Proceed to Task 3: Database Schema Implementation
