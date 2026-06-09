# eeik-managed pack=core
# Security Baseline Standard

**Applies To:** All projects  
**Enforced By:** `security-auditor` agent, `/security-scan` command, CI/CD gate  
**Minimum Bar:** Standard governance profile

---

## 1. Secrets Management

| Rule | Implementation |
|------|---------------|
| No secrets in source code | AWS Secrets Manager or environment variables |
| No secrets in `.env` files committed to VCS | `.env` in `.gitignore`; use `.env.example` with dummy values |
| No AWS credentials in code or environment | IAM roles (ECS task role, Lambda execution role) |
| Secrets rotated on schedule | AWS Secrets Manager rotation Lambda |
| Secret names follow convention | `/env/service-name/secret-name` |

---

## 2. Dependency Security

| Rule | Tool |
|------|------|
| Scan dependencies for CVEs on every build | OWASP Dependency Check or Snyk |
| No HIGH or CRITICAL CVEs in production dependencies | CI gate — fail build |
| Dependencies pinned to exact versions | `pom.xml` explicit versions; no `LATEST` |
| Container base images scanned | Trivy or ECR scanning |

---

## 3. IAM Least Privilege

```
Every IAM role must:
  - Declare only the actions it actually uses
  - Scope resources to specific ARNs — no "*" on sensitive actions
  - Use separate roles per service — never share task roles
  - Have no inline policies — use managed policies for auditability
```

**CDK Example — correct pattern:**

```typescript
// ✅ Least-privilege: only allow read from a specific bucket
const bucket = new s3.Bucket(this, 'DocumentBucket');

taskRole.addToPolicy(new iam.PolicyStatement({
  effect: iam.Effect.ALLOW,
  actions: ['s3:GetObject'],       // specific action
  resources: [bucket.arnForObjects('documents/*')],  // specific scope
}));
```

---

## 4. Network Security

| Rule | Implementation |
|------|---------------|
| No public subnets for application workloads | Private subnets only; public subnets for ALB only |
| Database not directly internet-accessible | Isolated subnets; Security Groups restrict to app tier |
| All inter-service traffic within VPC | VPC endpoints for AWS services; no internet egress for data |
| TLS everywhere | ALB HTTPS listener; certificate via ACM |
| WAF on all public-facing APIs | AWS WAF attached to ALB or API Gateway |

---

## 5. Data Protection

| Rule | Applies To |
|------|-----------|
| Encryption at rest | All S3 buckets (SSE-S3 minimum, SSE-KMS for sensitive data) |
| Encryption at rest | All RDS/Aurora instances (AES-256) |
| Encryption at rest | All EBS volumes |
| Encryption in transit | TLS 1.2+ for all API traffic |
| PII masked in logs | Never log email, name, DOB, card number, NI number in plaintext |
| CloudTrail enabled | All accounts — audit trail for all API calls |

---

## 6. OWASP Top 10 Checklist

For every REST API endpoint, verify:

| OWASP | Check |
|-------|-------|
| A01 Broken Access Control | Authentication required? Authorisation checked at right layer? |
| A02 Cryptographic Failures | No weak ciphers (MD5, SHA1); TLS enforced |
| A03 Injection | Parameterised queries only; no eval/exec of user input |
| A04 Insecure Design | Threat model reviewed for sensitive flows |
| A05 Security Misconfiguration | Actuator endpoints secured; debug off in prod; stack traces hidden |
| A06 Vulnerable Components | OWASP Dependency Check passing |
| A07 Auth Failures | JWT expiry enforced; no long-lived tokens; session invalidation |
| A08 Software Integrity | Dependency hashes verified; SBOM produced |
| A09 Logging Failures | All auth events logged; no sensitive data in logs |
| A10 SSRF | External URL inputs validated against allowlist |

---

## 7. Spring Boot Security Baseline (Java projects)

```yaml
# application.yaml — minimum required security config

management:
  endpoints:
    web:
      exposure:
        include: health,info    # ← only expose health and info
  endpoint:
    health:
      show-details: never       # ← hide stack details

server:
  error:
    include-stacktrace: never   # ← hide stack traces from responses
    include-message: never

spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: ${JWT_ISSUER_URI}   # ← from environment
```
