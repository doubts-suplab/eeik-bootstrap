# Architecture Extractor

## Purpose

Infer the architecture style and patterns from an existing codebase by reading the source code structure.

Called by Step 3 of `analyze-project.md`.

---

## Style Detection Rules

### Hexagonal / DDD → `microservices`

```
Signal: ALL of these packages present:
  src/main/java/.../domain/
  src/main/java/.../application/
  src/main/java/.../infrastructure/
  src/main/java/.../web/ OR .../api/ OR .../controller/

Confidence: HIGH
Pattern also implies: [ddd]
```

### Flat Layered → `modular-monolith`

```
Signal: ALL of these packages, without domain/:
  src/main/java/.../controller/ OR .../web/
  src/main/java/.../service/
  src/main/java/.../repository/ OR .../dao/

Confidence: MEDIUM
Note: Could also be a monolith — check for multiple bounded contexts
```

### Serverless → `serverless`

```
Signal: ONE of:
  serverless.yml at root
  src/main/java/.../handler/ with *Handler.java classes (Lambda)
  src/ contains functions/ directory (SAM)
  package.json with "serverless" dependency

Confidence: HIGH
```

### Agentic → `agentic`

```
Signal: ONE of:
  src/ contains agents/, graphs/, nodes/ directories (Python)
  langgraph in requirements.txt or pyproject.toml
  *Agent.py or *Graph.py classes present

Confidence: HIGH
Also sets: ai.enabled = true, ai.framework = langgraph
```

### Event-Driven → `event-driven`

```
Signal: BOTH of:
  Kafka or EventBridge in dependencies
  Consumer/Producer/Listener classes (>3 event handlers)
  No single REST controller entry point

Confidence: MEDIUM (often combined with microservices)
```

---

## Pattern Detection Rules

### DDD Patterns

```
Pattern: ddd
Signal: domain/ package with model/ and event/ subdirectories
Files: *Aggregate.java, *ValueObject.java, *DomainEvent.java
Confidence: HIGH if all three present, MEDIUM if partial
```

```
Pattern: cqrs
Signal: command/ and query/ packages in application layer
Files: *Command.java + *CommandHandler.java
       *Query.java + *QueryHandler.java
Confidence: HIGH
```

```
Pattern: saga
Signal: *Saga.java or *SagaState.java classes
Confidence: HIGH
```

```
Pattern: outbox
Signal: OutboxEvent.java in persistence/ OR outbox_events migration SQL
Confidence: HIGH
```

### API Gateway Pattern

```
Pattern: api-gateway
Signal: ApiGateway CDK stack OR serverless.yml with http events
CDK: new apigateway.RestApi(...) or new apigwv2.HttpApi(...)
Confidence: HIGH
```

### Strangler Fig

```
Pattern: strangler-fig
Signal: integration/ or legacy-adapter/ package alongside domain/
Files: *LegacyAdapter.java, *StranglerFacade.java
Or: README mentions "strangler fig" or "legacy integration"
Confidence: MEDIUM
```

---

## API Style Detection

```
rest:
  @RestController annotations in Java
  @app.get/@app.post decorators in Python (FastAPI)
  Confidence: HIGH

graphql:
  graphql-spring-boot-starter in pom.xml
  graphene or strawberry in requirements.txt
  *.graphqls schema files
  Confidence: HIGH

grpc:
  grpc-java or grpc-spring-boot-starter
  *.proto files present
  Confidence: HIGH

event:
  No REST/GraphQL controllers
  Only @KafkaListener or @SqsListener
  Confidence: MEDIUM
```
