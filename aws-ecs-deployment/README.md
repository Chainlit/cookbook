---
title: 'Deploying Chainlit Apps to AWS ECS'
tags: ['AWS', 'ECS', 'deployment']
---

# Deploying Chainlit Apps to AWS ECS

This repository provides a step-by-step guide to deploying Chainlit applications on AWS Elastic Container Service (ECS).

## Simple Function Explanation

The `app.py` in this repository defines a simple Chainlit application that responds to chat start events and messages. When a chat starts, it sends a "Hello world from AWS!" message. Upon receiving a message, it echoes back with a predefined message about the app's deployment demonstration on AWS ECS.

## Quickstart

To get started with deploying your Chainlit app to AWS ECS, follow these steps:

### Prerequisites

- Python ≥ 3.9
- AWS account
- Docker installed

### Step 1: AWS Account and Credentials

Create an AWS account and configure your AWS CLI following [this AWS blog post](https://aws.amazon.com/blogs/aws/new-users-guide-to-configuring-the-aws-cli/).

### Step 2: Clone the Repository

If you don't have an existing Chainlit project, clone this repository:
    
```shell
git clone https://github.com/Chainlit/cookbook.git chainlit-cookbook
cd chainlit-cookbook/aws-ecs-deployment
```

### Step 3: Dockerize Your Application

Create a `Dockerfile` with the following content:

```dockerfile
# Use an appropriate base image, e.g., python:3.10-slim
FROM python:3.10-slim
# Set environment variables
ENV PYTHONUNBUFFERED 1
# Set the working directory
WORKDIR /app
# Install dependencies
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt
Copy application code
COPY . /app/
Expose the port the app runs on
EXPOSE 8080
# Command to run the app
CMD ["python", "-m", "chainlit", "run", "app.py", "-h", "--port", "8080"]
```

Note: If you’re on Mac M1, use `FROM --platform=linux/amd64 python:3.9-slim` as the first line.

### Step 4: Build and Run Locally

Build the Docker image and run it locally to ensure everything is working:

```shell
docker build -t chainlit-app:latest .
docker run -p 8080:8080 chainlit-app:latest
```

Navigate to `localhost:8080` in your browser to see the app running.

### Step 5: Push to AWS ECR

Create an ECR repository and push your Docker image following the instructions provided in the AWS ECR console.

### Step 6: Create ECS Task and Service

1. Create a new ECS cluster.
2. Create a task definition with the Docker image.
3. Create a service within the cluster to run the task.
4. Ensure the security groups allow traffic on port 8080.

### Step 7: Access Your Deployed Application

Once the service is running, find the public IP of the task and navigate to `http://<public-ip>:8080` to access your deployed Chainlit app.

## Next Steps

- Connect the app to a custom domain.
- Set up a Load Balancer for better performance and high availability.
- Secure the app with an SSL certificate using AWS Certificate Manager.
- Set up a CI/CD pipeline to automate the deployment process.
---

For more details, visit the [Chainlit GitHub repository](https://github.com/Chainlit/chainlit) and check out the [tutorial blog post](https://ankushgarg.super.site/how-to-deploy-your-chatgpt-like-app-with-chainlit-and-aws-ecs).

