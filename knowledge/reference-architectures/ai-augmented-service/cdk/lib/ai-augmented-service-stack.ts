import { RemovalPolicy, Stack, StackProps, Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as logs from 'aws-cdk-lib/aws-logs';
import { ApplicationLoadBalancedFargateService } from 'aws-cdk-lib/aws-ecs-patterns';

/**
 * AI-Augmented Service reference architecture — infrastructure.
 *
 * A retrieval-augmented FastAPI service on ECS Fargate that answers over enterprise documents with
 * Amazon Bedrock, retrieving from Aurora PostgreSQL + pgvector. Every model decision is governed by the
 * HALO runtime *inside* the service (confidence gate, tool allowlist, audit) — the infra's job is to
 * give it a vector store, a documents bucket, and least-privilege Bedrock access. Mirrors
 * ../reference.yaml.
 */
export class AiAugmentedServiceStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const vpc = new ec2.Vpc(this, 'Vpc', { maxAzs: 2, natGateways: 1 });

    // ── Vector store: Aurora PostgreSQL with the pgvector extension ──────────────────
    const db = new rds.DatabaseCluster(this, 'VectorStore', {
      engine: rds.DatabaseClusterEngine.auroraPostgres({
        version: rds.AuroraPostgresEngineVersion.VER_16_4,
      }),
      vpc,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_ISOLATED },
      writer: rds.ClusterInstance.serverlessV2('writer'),
      serverlessV2MinCapacity: 0.5,
      serverlessV2MaxCapacity: 4,
      storageEncrypted: true,
      defaultDatabaseName: 'knowledge',
      removalPolicy: RemovalPolicy.SNAPSHOT,
    });

    // ── Source documents (the corpus the RAG pipeline ingests + chunks) ──────────────
    const docs = new s3.Bucket(this, 'Documents', {
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      versioned: true,
      removalPolicy: RemovalPolicy.RETAIN,
    });

    // ── FastAPI service on Fargate ───────────────────────────────────────────────────
    const cluster = new ecs.Cluster(this, 'Cluster', { vpc, containerInsights: true });
    const logGroup = new logs.LogGroup(this, 'ServiceLogs', {
      retention: logs.RetentionDays.ONE_MONTH,
      removalPolicy: RemovalPolicy.DESTROY,
    });

    const service = new ApplicationLoadBalancedFargateService(this, 'RagApi', {
      cluster,
      cpu: 512,
      memoryLimitMiB: 1024,
      desiredCount: 2,
      taskImageOptions: {
        image: ecs.ContainerImage.fromRegistry('REPLACE_ME/rag-api:latest'),
        containerPort: 8000,
        environment: {
          DOCUMENTS_BUCKET: docs.bucketName,
          BEDROCK_MODEL_ID: 'anthropic.claude-3-5-sonnet-20240620-v1:0',
          BEDROCK_EMBED_MODEL_ID: 'amazon.titan-embed-text-v2:0',
          // HALO governs every model call in-process; the gate is non-disableable.
          HALO_CONFIDENCE_FLOOR: '0.80',
        },
        secrets: { DB_SECRET: ecs.Secret.fromSecretsManager(db.secret!) },
        logDriver: ecs.LogDrivers.awsLogs({ streamPrefix: 'rag-api', logGroup }),
      },
      healthCheckGracePeriod: Duration.seconds(60),
      publicLoadBalancer: true,
    });

    db.connections.allowDefaultPortFrom(service.service);
    docs.grantRead(service.taskDefinition.taskRole);

    // ── Least-privilege Bedrock access: invoke the two named models, nothing else ────
    service.taskDefinition.taskRole.addToPrincipalPolicy(new iam.PolicyStatement({
      actions: ['bedrock:InvokeModel', 'bedrock:InvokeModelWithResponseStream'],
      resources: [
        `arn:aws:bedrock:${this.region}::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0`,
        `arn:aws:bedrock:${this.region}::foundation-model/amazon.titan-embed-text-v2:0`,
      ],
    }));
  }
}
