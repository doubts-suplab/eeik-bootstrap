#!/usr/bin/env node
import 'source-map-support/register';
import { App } from 'aws-cdk-lib';
import { EventDrivenMicroservicesStack } from '../lib/event-driven-microservices-stack';

const app = new App();
new EventDrivenMicroservicesStack(app, 'EventDrivenMicroservices', {
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION ?? 'eu-west-1' },
  description: 'Event-Driven Microservices reference architecture (EEIK knowledge/reference-architectures)',
});
