import { RemovalPolicy, Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as glue from 'aws-cdk-lib/aws-glue';
import * as athena from 'aws-cdk-lib/aws-athena';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as msk from 'aws-cdk-lib/aws-msk';

/**
 * Data Platform reference architecture — infrastructure.
 *
 * A medallion lakehouse: MSK ingests streams, Spark/Glue writes bronze→silver→gold on S3, cataloged in
 * Glue and queried with Athena; dbt owns the silver→gold SQL and Airflow (MWAA) orchestrates. This
 * stack provisions the durable substrate — the three lakehouse buckets, the Glue database + crawlers,
 * the Athena workgroup, and the MSK backbone. Compute jobs (Glue jobs, the MWAA env, dbt) are deployed
 * on top. Mirrors ../reference.yaml.
 */
export class DataPlatformStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // ── Medallion lakehouse: one bucket per zone, encrypted, private, versioned ──────
    const zone = (name: string) =>
      new s3.Bucket(this, `${name}Zone`, {
        bucketName: undefined,
        encryption: s3.BucketEncryption.S3_MANAGED,
        blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
        versioned: true,
        enforceSSL: true,
        removalPolicy: RemovalPolicy.RETAIN,
        lifecycleRules: [{ transitions: [], expiration: undefined }],
      });
    const bronze = zone('Bronze'); // raw, append-only, as-ingested
    const silver = zone('Silver'); // cleaned, conformed, deduplicated
    const gold = zone('Gold');     // curated marts (dbt outputs), Athena-served
    const athenaResults = zone('AthenaResults');

    // ── Catalog: a Glue database + a crawler per zone keeps schemas discoverable ──────
    const db = new glue.CfnDatabase(this, 'LakehouseDb', {
      catalogId: this.account,
      databaseInput: { name: 'lakehouse' },
    });

    const crawlerRoleArn = `arn:aws:iam::${this.account}:role/service-role/AWSGlueServiceRole-lakehouse`;
    const crawler = (name: string, bucket: s3.Bucket, prefix: string) =>
      new glue.CfnCrawler(this, `${name}Crawler`, {
        role: crawlerRoleArn,
        databaseName: 'lakehouse',
        targets: { s3Targets: [{ path: `s3://${bucket.bucketName}/${prefix}/` }] },
        schemaChangePolicy: { updateBehavior: 'UPDATE_IN_DATABASE', deleteBehavior: 'LOG' },
        tablePrefix: `${prefix}_`,
      });
    crawler('Bronze', bronze, 'bronze').addDependency(db);
    crawler('Silver', silver, 'silver').addDependency(db);
    crawler('Gold', gold, 'gold').addDependency(db);

    // ── Query: an Athena workgroup with results landing in its own bucket ────────────
    new athena.CfnWorkGroup(this, 'AnalyticsWorkgroup', {
      name: 'lakehouse-analytics',
      recursiveDeleteOption: true,
      workGroupConfiguration: {
        enforceWorkGroupConfiguration: true,
        resultConfiguration: {
          outputLocation: `s3://${athenaResults.bucketName}/results/`,
          encryptionConfiguration: { encryptionOption: 'SSE_S3' },
        },
      },
    });

    // ── Ingestion backbone: MSK (Kafka). Producers land raw events into bronze ───────
    const vpc = new ec2.Vpc(this, 'Vpc', { maxAzs: 3, natGateways: 1 });
    const mskSg = new ec2.SecurityGroup(this, 'MskSg', { vpc, description: 'MSK brokers' });
    new msk.CfnCluster(this, 'IngestBackbone', {
      clusterName: 'lakehouse-ingest',
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
  }
}
