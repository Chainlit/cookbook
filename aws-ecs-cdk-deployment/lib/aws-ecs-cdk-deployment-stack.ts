import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecrAssets from 'aws-cdk-lib/aws-ecr-assets';
import * as ecs_patterns from 'aws-cdk-lib/aws-ecs-patterns';


export class AwsEcsCdkDeploymentStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create a VPC
    const vpc = new ec2.Vpc(this, 'MyVPC', { 
      maxAzs: 2
    });

    // Create an ECS cluster
    const cluster = new ecs.Cluster(this, 'MyCluster', {
      vpc: vpc
    });

    // Build and push the Docker image to ECR
    const image = new ecrAssets.DockerImageAsset(this, 'MyDockerImage', {
      directory: '.',
      // If you are using an ARM-based machine (e.g. Apple M1), you can specify the platform as follows:
      // platform: ecrAssets.Platform.LINUX_AMD64,
      // buildArgs: {
      //   DOCKER_DEFAULT_PLATFORM: 'linux/amd64'
      // }
    });

    // Create an Fargate service
    new ecs_patterns.ApplicationLoadBalancedFargateService(this, 'MyFargateService', {
      cluster: cluster,
      cpu: 256,
      desiredCount: 1,
      taskImageOptions: {
        image: ecs.ContainerImage.fromDockerImageAsset(image),
        containerPort: 8080,
        },
      memoryLimitMiB: 512,
      publicLoadBalancer: true
    });

    // Output the URI of the Docker image
    new cdk.CfnOutput(this, 'ImageUri', {
      value: image.imageUri,
      description: 'The URI of the Docker image',
    });
  }
}
