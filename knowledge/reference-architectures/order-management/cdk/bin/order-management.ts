#!/usr/bin/env node
import 'source-map-support/register';
import { App } from 'aws-cdk-lib';
import { OrderManagementStack } from '../lib/order-management-stack';

const app = new App();
new OrderManagementStack(app, 'OrderManagement', {
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION ?? 'eu-west-1' },
  description: 'Order Management reference architecture (EEIK knowledge/reference-architectures)',
});
