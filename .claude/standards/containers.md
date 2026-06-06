# Container Standards

> Mandatory standards for all Docker, container, and Kubernetes configuration. Enforced by `containerisation-helper`, `devsecops-engineer`, and `code-reviewer` agents.

---

## Dockerfile Standards

### Base Images
- Use specific version tags — never `latest`
- Java services: `eclipse-temurin:21-jre-alpine` (runtime), `eclipse-temurin:21-jdk-alpine` (build stage)
- Python services: `python:3.12-slim`
- Node.js services: `node:20-alpine`
- Prefer Alpine-based images for smaller attack surface

### Multi-Stage Builds (Mandatory for all compiled languages)
```dockerfile
# Stage 1: Build
FROM eclipse-temurin:21-jdk-alpine AS build
WORKDIR /workspace
COPY mvnw pom.xml ./
COPY .mvn .mvn
RUN ./mvnw dependency:go-offline -B
COPY src src
RUN ./mvnw package -DskipTests -B

# Stage 2: Runtime (no build tools)
FROM eclipse-temurin:21-jre-alpine
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
WORKDIR /app
COPY --from=build --chown=appuser:appgroup /workspace/target/*.jar app.jar
USER appuser
EXPOSE 8080
ENTRYPOINT ["java", "-XX:MaxRAMPercentage=75.0", "-XX:+UseContainerSupport", "-jar", "app.jar"]
```

### Security Requirements
- **Never run as root** — always create and switch to a non-root user
- **Never use `ADD` with URLs** — use `COPY` or multi-stage with explicit downloads
- Use `.dockerignore` to exclude: `.git`, `target/`, `node_modules/`, `*.env`, `*.key`
- Label images with OCI standard labels:

```dockerfile
LABEL org.opencontainers.image.source="https://github.com/{org}/{repo}"
LABEL org.opencontainers.image.revision="${GIT_SHA}"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
```

---

## JVM Container Configuration

```dockerfile
ENV JAVA_OPTS="-XX:MaxRAMPercentage=75.0 \
               -XX:+UseContainerSupport \
               -XX:+HeapDumpOnOutOfMemoryError \
               -XX:HeapDumpPath=/tmp/heapdump.hprof \
               -Djava.security.egd=file:/dev/./urandom"
```

- `MaxRAMPercentage=75.0` — leaves 25% for non-heap (metaspace, threads, off-heap)
- `UseContainerSupport` — reads `cgroup` limits rather than host memory
- Never set `-Xmx` and `-XX:MaxRAMPercentage` together

---

## Docker Compose (Local Development)

```yaml
services:
  app:
    build: .
    ports: ["8080:8080"]
    environment:
      SPRING_PROFILES_ACTIVE: local
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/mydb
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "-q", "-O-", "http://localhost:8080/actuator/health"]
      interval: 10s
      timeout: 5s
      retries: 5

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: localpassword
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser"]
      interval: 5s
      retries: 10
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## Kubernetes Standards

### Resource Limits (Mandatory)
Every container must have `requests` and `limits`:

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### Health Probes (Mandatory)
```yaml
readinessProbe:
  httpGet:
    path: /actuator/health/readiness
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 5
livenessProbe:
  httpGet:
    path: /actuator/health/liveness
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3
```

### Security Context
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop: ["ALL"]
```

---

## Image Scanning

- Scan all images with Trivy before pushing to production registry
- Block images with `CRITICAL` vulnerabilities
- Review and remediate `HIGH` vulnerabilities within 14 days
- Generate SBOM with Syft for all production images
