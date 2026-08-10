#!/usr/bin/env node
import 'source-map-support/register';
import { App } from 'aws-cdk-lib';
import { MultiAgentAiPlatformStack } from '../lib/multi-agent-ai-platform-stack';

const app = new App();
new MultiAgentAiPlatformStack(app, 'MultiAgentAiPlatform', {
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION ?? 'eu-west-1' },
  description: 'Multi-Agent AI Platform reference architecture (EEIK knowledge/reference-architectures)',
});
