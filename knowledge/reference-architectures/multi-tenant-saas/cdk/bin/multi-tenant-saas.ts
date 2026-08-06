#!/usr/bin/env node
import 'source-map-support/register';
import { App } from 'aws-cdk-lib';
import { MultiTenantSaasStack } from '../lib/multi-tenant-saas-stack';

const app = new App();
new MultiTenantSaasStack(app, 'MultiTenantSaas', {
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION ?? 'eu-west-1' },
  description: 'Multi-Tenant SaaS reference architecture (EEIK knowledge/reference-architectures)',
});
