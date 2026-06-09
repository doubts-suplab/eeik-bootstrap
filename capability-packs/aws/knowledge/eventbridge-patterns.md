# Amazon EventBridge Event-Driven Patterns

**Type**: Architecture Pattern  
**Stack**: EventBridge, Lambda, SQS, SNS, CDK

---

## EventBridge vs SNS vs SQS Decision

```
Need pub/sub to multiple consumers with filtering?  → EventBridge
Need simple fan-out to known subscribers?           → SNS
Need guaranteed processing (queue + worker)?        → SQS
Need ordered processing?                            → SQS FIFO or Kinesis
Need scheduled events?                              → EventBridge Scheduler
```

---

## Pattern 1: Domain Event Bus

One custom event bus per bounded context — prevents cross-context coupling.

```typescript
// CDK
const orderEventBus = new events.EventBus(this, 'OrderEventBus', {
  eventBusName: `${props.projectName}-orders-${props.environment}`,
});

// Resource policy — allow other accounts to publish (multi-account)
orderEventBus.addToResourcePolicy(new iam.PolicyStatement({
  sid: 'AllowInventoryAccount',
  principals: [new iam.AccountPrincipal(props.inventoryAccountId)],
  actions: ['events:PutEvents'],
  resources: [orderEventBus.eventBusArn],
}));
```

---

## Pattern 2: Event Routing with Rules

```typescript
// Route order.placed events to inventory and notification services
new events.Rule(this, 'OrderPlacedRule', {
  eventBus: orderEventBus,
  ruleName: 'order-placed-to-inventory',
  eventPattern: {
    source: ['com.mycompany.orders'],
    detailType: ['order.placed'],
    detail: {
      // Content-based filtering — only high-value orders to priority queue
      amount: [{ numeric: ['>', 1000] }],
    },
  },
  targets: [
    new targets.SqsQueue(inventoryQueue, {
      message: events.RuleTargetInput.fromEventPath('$.detail'),
      deadLetterQueue: inventoryDlq,
      retryAttempts: 3,
    }),
  ],
});
```

---

## Pattern 3: Structured Event Schema

Register schemas to enable type-safe consumers:

```typescript
// CDK — register schema
new eventschemas.CfnSchema(this, 'OrderPlacedSchema', {
  registryName: 'com.mycompany.orders',
  schemaName: 'order.placed',
  type: 'OpenApi3',
  content: JSON.stringify({
    openapi: '3.0.0',
    info: { title: 'OrderPlaced', version: '1' },
    paths: {},
    components: {
      schemas: {
        'order.placed': {
          type: 'object',
          required: ['orderId', 'customerId', 'amount', 'currency', 'timestamp'],
          properties: {
            orderId:    { type: 'string', format: 'uuid' },
            customerId: { type: 'string', format: 'uuid' },
            amount:     { type: 'number', minimum: 0 },
            currency:   { type: 'string', pattern: '^[A-Z]{3}$' },
            timestamp:  { type: 'string', format: 'date-time' },
          },
        },
      },
    },
  }),
});
```

```python
# Python — publish typed event
import boto3
import json
from datetime import datetime, timezone

events_client = boto3.client('events')

def publish_order_placed(order: Order) -> None:
    response = events_client.put_events(
        Entries=[{
            'Source': 'com.mycompany.orders',
            'DetailType': 'order.placed',
            'EventBusName': os.environ['ORDER_EVENT_BUS_NAME'],
            'Detail': json.dumps({
                'orderId':    str(order.id),
                'customerId': str(order.customer_id),
                'amount':     float(order.amount),
                'currency':   order.currency,
                'timestamp':  datetime.now(timezone.utc).isoformat(),
            }),
            'Time': datetime.now(timezone.utc),
        }]
    )

    if response['FailedEntryCount'] > 0:
        raise EventPublishError(f"Failed to publish order.placed: {response['Entries']}")

    logger.info("event_published", detail_type="order.placed", order_id=str(order.id))
```

---

## Pattern 4: EventBridge Scheduler (Replace Cron Lambda)

Replace CloudWatch Events cron with EventBridge Scheduler for flexible schedules:

```typescript
new scheduler.CfnSchedule(this, 'DailyReportSchedule', {
  name: 'daily-revenue-report',
  scheduleExpression: 'cron(0 7 * * ? *)',   // 7am UTC daily
  flexibleTimeWindow: { mode: 'FLEXIBLE', maximumWindowInMinutes: 30 },
  target: {
    arn: reportLambda.functionArn,
    roleArn: schedulerRole.roleArn,
    retryPolicy: {
      maximumRetryAttempts: 2,
      maximumEventAgeInSeconds: 3600,
    },
    deadLetterConfig: { arn: dlq.queueArn },
  },
  state: 'ENABLED',
  groupName: `${props.projectName}-${props.environment}`,
});
```

---

## Dead Letter Queue Pattern

Every EventBridge rule target must have a DLQ:

```typescript
const dlq = new sqs.Queue(this, 'EventDlq', {
  queueName: `${targetName}-dlq`,
  retentionPeriod: cdk.Duration.days(14),
  encryption: sqs.QueueEncryption.KMS_MANAGED,
});

// CloudWatch alarm on DLQ
new cloudwatch.Alarm(this, 'DlqAlarm', {
  metric: dlq.metricApproximateNumberOfMessagesVisible(),
  threshold: 1,
  evaluationPeriods: 1,
  alarmDescription: `${targetName} DLQ has messages — check Lambda errors`,
  treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING,
});
```

---

## Rules

- One custom event bus per bounded context — never use the default bus for application events
- Always register schemas — enables code generation and contract testing
- DLQ + alarm on every rule target — no silent failures
- Set `retryAttempts` explicitly — default is 0 (no retry)
- Use `EventBridge Scheduler` for cron, not CloudWatch Events (Scheduler has better retry, DLQ, timezone support)
- Never put >256KB of data in an event — use S3 reference pattern (store payload in S3, put S3 key in event)
