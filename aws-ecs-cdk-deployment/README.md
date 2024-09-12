# Deploying Chainlit Apps to AWS ECS using CDK

This guide provides step-by-step instructions for deploying Chainlit applications on AWS Elastic Container Service (ECS) using the AWS Cloud Development Kit (CDK).

## Prerequisites

- Python ≥ 3.9
- Node.js ≥ 14.x
- AWS account and configured AWS CLI
- AWS CDK CLI installed (`npm install -g aws-cdk`)
- Docker installed

## Quickstart

1. Clone the repository:
   ```
   git clone https://github.com/Chainlit/cookbook.git chainlit-cookbook
   cd chainlit-cookbook/aws-ecs-cdk-deployment
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Bootstrap your AWS account for CDK (if not done before):
   ```
   cdk bootstrap
   ```

4. Deploy the stack:
   ```
   cdk deploy
   ```

5. After deployment, the CDK will output important information including the URL of your deployed application. Look for the output similar to this:
    ```
    Outputs:
    AwsEcsCdkDeploymentStack.MyFargateServiceLoadBalancerDNS = <LoadBalancer-DNS-address>
    AwsEcsCdkDeploymentStack.MyFargateServiceServiceURL = http://<LoadBalancer-DNS-address>
    ```
    The URL you should use to access your application is the one prefixed with http://, which is the value of AwsEcsCdkDeploymentStack.MyFargateServiceServiceURL.

6. Open this URL in your browser to access your Chainlit app.

## Project Structure

```
aws-ecs-cdk-deployment/
├── app.py                 # Chainlit application
├── Dockerfile             # Dockerfile for the application
├── requirements.txt       # Python dependencies
├── cdk.json               # CDK application configuration
├── bin/
│   └── aws_ecs_cdk_deployment.ts  # CDK app entry point
└── lib/
    └── aws_ecs_cdk_deployment_stack.ts  # CDK stack definition
```

## Customization

You can customize the deployment by modifying the `aws_ecs_cdk_deployment_stack.ts` file. Some possible customizations include:

- Adjusting the VPC configuration
- Changing the ECS task definition (CPU, memory)
- Adding custom domain and SSL certificate
- Implementing auto-scaling

## Cleanup

To avoid incurring unnecessary costs, remember to destroy the stack when you're done:

```
cdk destroy
```

## Troubleshooting

- If you encounter issues related to Docker image building on ARM-based machines (e.g., Apple M1), ensure that the `platform` and `buildArgs` in the `DockerImageAsset` construction are set correctly.
- For any deployment errors, check the CloudFormation console in the AWS Management Console for detailed error messages.

## Additional Resources

- [Chainlit Documentation](https://docs.chainlit.io)
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/latest/guide/home.html)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)