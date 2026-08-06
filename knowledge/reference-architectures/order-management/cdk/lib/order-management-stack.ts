import { Duration, RemovalPolicy, Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as msk from 'aws-cdk-lib/aws-msk';
import * as logs from 'aws-cdk-lib/aws-logs';
import { ApplicationLoadBalancedFargateService } from 'aws-cdk-lib/aws-ecs-patterns';

/**
 * Order Management reference architecture — infrastructure.
 *
 * Event-driven order lifecycle on ECS Fargate, Aurora PostgreSQL (order aggregate + transactional
 * outbox), and MSK (Kafka) as the domain-event backbone. Mirrors the components in ../reference.yaml:
 * Order API (commands), Order Read Model (CQRS on a replica), Inventory + Payment saga participants.
 *
 * This is a reference skeleton: representative L2/L3 constructs with production-shaped defaults
 * (isolated DB subnets, encryption, right-sized removal policies). Wire real container images and
 * secrets before deploying.
 */
export class OrderManagementStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // ── Network: public ALB tier, private app tier, isolated data tier ──────────────
    const vpc = new ec2.Vpc(this, 'Vpc', {
      maxAzs: 3,
      natGateways: 1,
      subnetConfiguration: [
        { name: 'public', subnetType: ec2.SubnetType.PUBLIC, cidrMask: 24 },
        { name: 'app', subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS, cidrMask: 24 },
        { name: 'data', subnetType: ec2.SubnetType.PRIVATE_ISOLATED, cidrMask: 24 },
      ],
    });

    // ── Order store: Aurora PostgreSQL (writer + reader for the CQRS read side) ──────
    const db = new rds.DatabaseCluster(this, 'OrderStore', {
      engine: rds.DatabaseClusterEngine.auroraPostgres({
        version: rds.AuroraPostgresEngineVersion.VER_16_4,
      }),
      vpc,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_ISOLATED },
      writer: rds.ClusterInstance.serverlessV2('writer'),
      readers: [rds.ClusterInstance.serverlessV2('reader', { scaleWithWriter: true })],
      serverlessV2MinCapacity: 0.5,
      serverlessV2MaxCapacity: 8,
      storageEncrypted: true,
      defaultDatabaseName: 'orders',
      removalPolicy: RemovalPolicy.SNAPSHOT,
    });

    // ── Event backbone: MSK (Kafka). Topic-per-aggregate; Avro via Schema Registry ───
    const mskSg = new ec2.SecurityGroup(this, 'MskSg', { vpc, description: 'MSK brokers' });
    const kafka = new msk.CfnCluster(this, 'EventBackbone', {
      clusterName: 'order-events',
      kafkaVersion: '3.6.0',
      numberOfBrokerNodes: 3,
      brokerNodeGroupInfo: {
        instanceType: 'kafka.m5.large',
        clientSubnets: vpc.selectSubnets({ subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS }).subnetIds,
        securityGroups: [mskSg.securityGroupId],
        storageInfo: { ebsStorageInfo: { volumeSize: 100 } },
      },
      encryptionInfo: { encryptionInTransit: { clientBroker: 'TLS', inCluster: true } },
    });

    // ── Compute: one ECS cluster, one Fargate service per bounded context ────────────
    const cluster = new ecs.Cluster(this, 'Cluster', { vpc, containerInsights: true });

    const service = (name: string, image: string, publicApi = false) => {
      const logGroup = new logs.LogGroup(this, `${name}Logs`, {
        retention: logs.RetentionDays.ONE_MONTH,
        removalPolicy: RemovalPolicy.DESTROY,
      });
      if (publicApi) {
        // Public command API behind an ALB.
        return new ApplicationLoadBalancedFargateService(this, name, {
          cluster,
          cpu: 512,
          memoryLimitMiB: 1024,
          desiredCount: 2,
          taskImageOptions: {
            image: ecs.ContainerImage.fromRegistry(image),
            containerPort: 8080,
            environment: {
              SPRING_PROFILES_ACTIVE: 'prod',
              KAFKA_BOOTSTRAP: kafka.attrBootstrapBrokerStringTls ?? '',
            },
            secrets: {
              DB_SECRET: ecs.Secret.fromSecretsManager(db.secret!),
            },
            logDriver: ecs.LogDrivers.awsLogs({ streamPrefix: name, logGroup }),
          },
          healthCheckGracePeriod: Duration.seconds(60),
          publicLoadBalancer: true,
        });
      }
      // Internal saga participants / read model (no public ingress).
      const taskDef = new ecs.FargateTaskDefinition(this, `${name}Task`, { cpu: 512, memoryLimitMiB: 1024 });
      taskDef.addContainer(name, {
        image: ecs.ContainerImage.fromRegistry(image),
        environment: { SPRING_PROFILES_ACTIVE: 'prod', KAFKA_BOOTSTRAP: kafka.attrBootstrapBrokerStringTls ?? '' },
        secrets: { DB_SECRET: ecs.Secret.fromSecretsManager(db.secret!) },
        logging: ecs.LogDrivers.awsLogs({ streamPrefix: name, logGroup }),
      });
      const svc = new ecs.FargateService(this, name, { cluster, taskDefinition: taskDef, desiredCount: 2 });
      db.connections.allowDefaultPortFrom(svc);
      return svc;
    };

    const orderApi = service('OrderApi', 'REPLACE_ME/order-api:latest', true);
    db.connections.allowDefaultPortFrom(orderApi.service);
    service('OrderReadModel', 'REPLACE_ME/order-read:latest');
    service('InventoryService', 'REPLACE_ME/inventory:latest');
    service('PaymentService', 'REPLACE_ME/payment:latest');
  }
}
