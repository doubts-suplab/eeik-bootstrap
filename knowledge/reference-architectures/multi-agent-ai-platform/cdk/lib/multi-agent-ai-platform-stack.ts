import { RemovalPolicy, Stack, StackProps, Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as logs from 'aws-cdk-lib/aws-logs';
import { ApplicationLoadBalancedFargateService } from 'aws-cdk-lib/aws-ecs-patterns';

/**
 * Multi-Agent AI Platform reference architecture — infrastructure.
 *
 * A FastAPI platform on ECS Fargate hosts a LangGraph supervisor that routes each task to specialist
 * worker agents (research, code, archive). Every agent runs on the HALO runtime *inside* the service
 * (confidence gate, default-deny tool registry, audit, human review) — the supervisor holds no tools.
 * The infra's job is to give the platform a checkpoint store (DynamoDB), least-privilege Bedrock
 * access for the model port, and observability. Mirrors ../reference.yaml.
 */
export class MultiAgentAiPlatformStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const vpc = new ec2.Vpc(this, 'Vpc', { maxAzs: 2, natGateways: 1 });

    // ── Checkpoint store: LangGraph state so long, multi-step runs survive restarts ──
    const checkpoints = new dynamodb.Table(this, 'Checkpoints', {
      partitionKey: { name: 'thread_id', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'checkpoint_id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
      pointInTimeRecovery: true,
      removalPolicy: RemovalPolicy.RETAIN,
    });

    // ── Audit log: append-only record of every governed agent decision (spec §7) ─────
    const audit = new dynamodb.Table(this, 'AuditLog', {
      partitionKey: { name: 'run_id', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'ts', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
      removalPolicy: RemovalPolicy.RETAIN,
    });

    // ── Platform API + supervisor/workers (single service; agents run in-process on HALO) ──
    const cluster = new ecs.Cluster(this, 'Cluster', { vpc, containerInsights: true });

    const service = new ApplicationLoadBalancedFargateService(this, 'PlatformApi', {
      cluster,
      cpu: 1024,
      memoryLimitMiB: 2048,
      desiredCount: 2,
      publicLoadBalancer: true,
      taskImageOptions: {
        image: ecs.ContainerImage.fromRegistry('public.ecr.aws/docker/library/python:3.12-slim'),
        containerPort: 8000,
        environment: {
          CHECKPOINT_TABLE: checkpoints.tableName,
          AUDIT_TABLE: audit.tableName,
          // HALO governance is non-optional: the confidence gate + audit run on every agent call.
          HALO_CONFIDENCE_THRESHOLD: '0.80',
          BEDROCK_REGION: this.region,
        },
        logDriver: ecs.LogDrivers.awsLogs({
          streamPrefix: 'agent-platform',
          logRetention: logs.RetentionDays.ONE_MONTH,
        }),
      },
      healthCheckGracePeriod: Duration.seconds(60),
    });

    // Least-privilege: the platform reads/writes only its own tables …
    checkpoints.grantReadWriteData(service.taskDefinition.taskRole);
    audit.grantWriteData(service.taskDefinition.taskRole); // append-only — no delete/update grant

    // … and may invoke only Bedrock model inference (the HALO LLM port), nothing broader.
    service.taskDefinition.taskRole.addToPrincipalPolicy(
      new iam.PolicyStatement({
        actions: ['bedrock:InvokeModel', 'bedrock:InvokeModelWithResponseStream'],
        resources: [`arn:aws:bedrock:${this.region}::foundation-model/anthropic.*`],
      }),
    );

    service.targetGroup.configureHealthCheck({ path: '/health' });
  }
}
