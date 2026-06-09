# Dockerfile Standard

**Applies To:** All containerised services  
**Runtime:** AWS ECS Fargate (primary), EKS (secondary)

---

## Required Practices

### Multi-Stage Build (Java)

```dockerfile
# Stage 1: Build
FROM eclipse-temurin:21-jdk-alpine AS builder
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn package -DskipTests --no-transfer-progress

# Stage 2: Runtime — minimal image
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app

# ✅ Non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser:appgroup

# ✅ Copy only the JAR — no build tools in final image
COPY --from=builder /app/target/*.jar app.jar

# ✅ Explicit port
EXPOSE 8080

# ✅ JVM flags for containers (Loom-aware)
ENTRYPOINT ["java", \
  "-XX:+UseContainerSupport", \
  "-XX:MaxRAMPercentage=75.0", \
  "-Djava.security.egd=file:/dev/./urandom", \
  "-jar", "app.jar"]
```

### Multi-Stage Build (Python)

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir build && python -m build

FROM python:3.12-slim
WORKDIR /app

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

COPY --from=builder /app/dist/*.whl .
RUN pip install --no-cache-dir *.whl

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Prohibited Patterns

| Pattern | Risk | Alternative |
|---------|------|-------------|
| `RUN apt-get install` in final stage | Large image size | Multi-stage; use distroless |
| `USER root` in final stage | Privilege escalation | Non-root user always |
| `COPY . .` without `.dockerignore` | Secrets in image | Explicit COPY of build output only |
| `FROM python:3-latest` | Unpinned — breaks on new release | Pin to `python:3.12-slim` |
| `ENV SECRET_KEY=abc123` | Secrets in image layer | AWS Secrets Manager at runtime |
| `ENTRYPOINT ["bash", "-c", "..."]` | Shell injection risk | Use JSON exec form |

---

## .dockerignore (Required)

```
.git
.github
.env
*.env
target/
node_modules/
__pycache__/
.pytest_cache/
*.pyc
infrastructure/
docs/
tests/
*.md
```
