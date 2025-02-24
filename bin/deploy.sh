#!/bin/bash

AWS_REGION="ap-northeast-1"
IMAGE_TAG="latest"
TASK_NAME="auto-trade-task"

source .env.production

cd frontend
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO_FRONTEND
docker build --platform=linux/x86_64 -t $ECR_REPO_FRONTEND:$IMAGE_TAG .
docker push $ECR_REPO_FRONTEND:$IMAGE_TAG
docker rmi $ECR_REPO_FRONTEND:$IMAGE_TAG

cd ../backend
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO_BACKEND
docker build --platform=linux/x86_64 -t $ECR_REPO_BACKEND:$IMAGE_TAG .
docker push $ECR_REPO_BACKEND:$IMAGE_TAG
docker rmi $ECR_REPO_BACKEND:$IMAGE_TAG

cd ..
echo "Deployment completed!"

    