import { Duration, RemovalPolicy, Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as cognito from 'aws-cdk-lib/aws-cognito';
import * as events from 'aws-cdk-lib/aws-events';
import * as logs from 'aws-cdk-lib/aws-logs';
import { ApplicationLoadBalancedFargateService } from 'aws-cdk-lib/aws-ecs-patterns';

/**
 * Multi-Tenant SaaS reference architecture — infrastructure.
 *
 * Shared infrastructure, isolated tenants: a Spring Boot modular monolith on ECS Fargate behind an ALB,
 * Cognito identity (a `tenant_id` claim on every token), Aurora PostgreSQL with **row-level security**
 * for data isolation, and an EventBridge bus for cross-module events. The isolation guarantee lives in
 * the database (RLS policies keyed on the tenant claim) — the infra wires identity → app → data so that
 * claim is always present. Mirrors ../reference.yaml.
 */
export class MultiTenantSaasStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const vpc = new ec2.Vpc(this, 'Vpc', { maxAzs: 2, natGateways: 1 });

    // ── Identity: one Cognito pool; each user carries a custom tenant_id claim ───────
    const userPool = new cognito.UserPool(this, 'Identity', {
      selfSignUpEnabled: false,
      signInAliases: { email: true },
      standardAttributes: { email: { required: true, mutable: false } },
      customAttributes: { tenant_id: new cognito.StringAttribute({ mutable: false }) },
      removalPolicy: RemovalPolicy.RETAIN,
    });
    userPool.addClient('WebClient', {
      authFlows: { userSrp: true },
      // The tenant_id claim rides in the ID token; the app sets it as the RLS session variable.
      readAttributes: new cognito.ClientAttributes().withStandardAttributes({ email: true })
        .withCustomAttributes('tenant_id'),
    });

    // ── Data: Aurora PostgreSQL. RLS policies (in Flyway migrations) enforce isolation ─
    const db = new rds.DatabaseCluster(this, 'TenantStore', {
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
      defaultDatabaseName: 'saas',
      removalPolicy: RemovalPolicy.SNAPSHOT,
    });

    // ── Cross-module events: a dedicated bus (metering, provisioning, billing) ────────
    const bus = new events.EventBus(this, 'DomainBus', { eventBusName: 'saas-domain' });

    // ── Compute: the modular monolith behind an ALB ──────────────────────────────────
    const cluster = new ecs.Cluster(this, 'Cluster', { vpc, containerInsights: true });
    const logGroup = new logs.LogGroup(this, 'AppLogs', {
      retention: logs.RetentionDays.ONE_MONTH,
      removalPolicy: RemovalPolicy.DESTROY,
    });

    const app = new ApplicationLoadBalancedFargateService(this, 'App', {
      cluster,
      cpu: 1024,
      memoryLimitMiB: 2048,
      desiredCount: 2,
      taskImageOptions: {
        image: ecs.ContainerImage.fromRegistry('REPLACE_ME/saas-app:latest'),
        containerPort: 8080,
        environment: {
          SPRING_PROFILES_ACTIVE: 'prod',
          COGNITO_USER_POOL_ID: userPool.userPoolId,
          EVENT_BUS_NAME: bus.eventBusName,
          // The app opens each request's tx with SET app.tenant_id = <claim> so RLS policies apply.
          DB_RLS_SESSION_VAR: 'app.tenant_id',
        },
        secrets: { DB_SECRET: ecs.Secret.fromSecretsManager(db.secret!) },
        logDriver: ecs.LogDrivers.awsLogs({ streamPrefix: 'saas-app', logGroup }),
      },
      healthCheckGracePeriod: Duration.seconds(60),
      publicLoadBalancer: true,
    });

    db.connections.allowDefaultPortFrom(app.service);
    bus.grantPutEventsTo(app.taskDefinition.taskRole);
  }
}
