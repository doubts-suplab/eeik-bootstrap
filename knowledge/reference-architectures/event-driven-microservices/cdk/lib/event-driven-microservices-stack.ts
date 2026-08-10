import { RemovalPolicy, Stack, StackProps, Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as msk from 'aws-cdk-lib/aws-msk';
import * as logs from 'aws-cdk-lib/aws-logs';
import { ApplicationLoadBalancedFargateService } from 'aws-cdk-lib/aws-ecs-patterns';

/**
 * Event-Driven Microservices reference architecture — infrastructure.
 *
 * Spring Boot services on ECS Fargate communicate over an Amazon MSK (Kafka) backbone. Each service
 * owns a private Aurora PostgreSQL schema and publishes domain events via the transactional outbox
 * (state + event in one DB transaction — no dual-write). Sagas coordinate multi-service workflows with
 * compensations; CQRS query services build read projections from events. The infra provides the Kafka
 * backbone, per-service data stores, and a paved edge. Mirrors ../reference.yaml.
 */
export class EventDrivenMicroservicesStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const vpc = new ec2.Vpc(this, 'Vpc', { maxAzs: 3, natGateways: 1 });

    // ── Event backbone: Amazon MSK (Kafka) ───────────────────────────────────────────
    const cluster = new msk.CfnCluster(this, 'EventBackbone', {
      clusterName: 'order-events',
      kafkaVersion: '3.6.0',
      numberOfBrokerNodes: 3,
      brokerNodeGroupInfo: {
        instanceType: 'kafka.m5.large',
        clientSubnets: vpc.selectSubnets({ subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS }).subnetIds,
        storageInfo: { ebsStorageInfo: { volumeSize: 100 } },
      },
      encryptionInfo: { encryptionInTransit: { clientBroker: 'TLS', inCluster: true } },
    });

    // ── Per-service write store (private Aurora; each service owns its schema) ────────
    const db = new rds.DatabaseCluster(this, 'ServiceStore', {
      engine: rds.DatabaseClusterEngine.auroraPostgres({
        version: rds.AuroraPostgresEngineVersion.VER_16_4,
      }),
      vpc,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_ISOLATED },
      writer: rds.ClusterInstance.serverlessV2('writer'),
      serverlessV2MinCapacity: 0.5,
      serverlessV2MaxCapacity: 8,
      storageEncrypted: true,
      removalPolicy: RemovalPolicy.SNAPSHOT,
    });

    // ── Paved edge: Spring Cloud Gateway on Fargate (north-south entry) ───────────────
    const ecsCluster = new ecs.Cluster(this, 'Cluster', { vpc, containerInsights: true });
    const gateway = new ApplicationLoadBalancedFargateService(this, 'Edge', {
      cluster: ecsCluster,
      cpu: 512,
      memoryLimitMiB: 1024,
      desiredCount: 2,
      publicLoadBalancer: true,
      taskImageOptions: {
        image: ecs.ContainerImage.fromRegistry('public.ecr.aws/docker/library/eclipse-temurin:21-jre'),
        containerPort: 8080,
        environment: {
          KAFKA_BOOTSTRAP: cluster.attrArn,   // resolve to broker string at deploy time
          DB_CLUSTER: db.clusterEndpoint.hostname,
        },
        logDriver: ecs.LogDrivers.awsLogs({
          streamPrefix: 'edge',
          logRetention: logs.RetentionDays.ONE_MONTH,
        }),
      },
      healthCheckGracePeriod: Duration.seconds(90),
    });
    gateway.targetGroup.configureHealthCheck({ path: '/actuator/health' });

    db.connections.allowDefaultPortFrom(gateway.service, 'edge → service store');
  }
}
