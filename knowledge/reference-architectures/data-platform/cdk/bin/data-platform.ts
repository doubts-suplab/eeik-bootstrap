#!/usr/bin/env node
import 'source-map-support/register';
import { App } from 'aws-cdk-lib';
import { DataPlatformStack } from '../lib/data-platform-stack';

const app = new App();
new DataPlatformStack(app, 'DataPlatform', {
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION ?? 'eu-west-1' },
  description: 'Data Platform reference architecture (EEIK knowledge/reference-architectures)',
});
