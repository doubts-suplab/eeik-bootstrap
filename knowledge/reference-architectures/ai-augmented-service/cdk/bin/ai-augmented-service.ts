#!/usr/bin/env node
import 'source-map-support/register';
import { App } from 'aws-cdk-lib';
import { AiAugmentedServiceStack } from '../lib/ai-augmented-service-stack';

const app = new App();
new AiAugmentedServiceStack(app, 'AiAugmentedService', {
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION ?? 'eu-west-1' },
  description: 'AI-Augmented Service reference architecture (EEIK knowledge/reference-architectures)',
});
