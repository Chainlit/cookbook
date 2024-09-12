#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { AwsEcsCdkDeploymentStack } from '../lib/aws-ecs-cdk-deployment-stack';

const app = new cdk.App();
new AwsEcsCdkDeploymentStack(app, 'AwsEcsCdkDeploymentStack', {});