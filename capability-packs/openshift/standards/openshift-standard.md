# OpenShift Engineering Standard

Version: OCP 4.14+ | Tekton 0.55+ | ArgoCD 2.9+ | operator-sdk 1.33+

---

## Golden Rules

| # | Rule | Enforcement |
|---|------|-------------|
| O01 | Never run as root — OCP will reject it under restricted-v2 SCC | CI manifest lint |
| O02 | Test with non-root UID locally before pushing: `podman run --user 1000680000` | Dev workflow |
| O03 | Use Routes not Ingress for OCP-specific TLS features | Code review |
| O04 | Secrets in OpenShift Secrets or Vault — never in ConfigMaps or env | Code review |
| O05 | All deployments managed via GitOps (ArgoCD Application) in prod | Architecture |
| O06 | Resource requests AND limits on every container | CI manifest lint |
| O07 | Liveness + readiness probes on every container | CI manifest lint |
| O08 | ImageStreams for internal builds — never `latest` tag in production | Code review |
| O09 | Operators for stateful workloads — never manage stateful sets manually | Architecture |
| O10 | Pipeline-as-code — no manual `oc apply` in production | CI/CD policy |

---

## Namespace Strategy

```
{project}-dev        ← dev environment
{project}-test       ← integration test
{project}-staging    ← pre-production
{project}-prod       ← production
{project}-cicd       ← pipelines, ArgoCD apps
```

Apply RBAC consistently:
- `edit` role for CI service accounts
- `view` role for monitoring service accounts
- Custom roles for application service accounts (least privilege)

---

## SCC Decision Tree

```
Does the container need to run as root?
  YES → Do you control the image?
          YES → Fix the Dockerfile: use non-root user + fsGroup
          NO  → Request anyuid SCC with security justification
  NO  → Use restricted-v2 (default, most secure)

Does the container need privileged access?
  YES → Operator/DaemonSet use case only; never application workloads
  NO  → restricted-v2
```

```bash
# Audit SCCs in use across a namespace
oc get pods -n <ns> -o custom-columns='NAME:.metadata.name,SCC:.metadata.annotations.openshift\.io/scc'
```

---

## Image Management

```yaml
# Build once, promote across environments with ImageStream tags
# In cicd namespace:
apiVersion: image.openshift.io/v1
kind: ImageStream
metadata:
  name: my-app
  namespace: my-app-cicd

---
# Tag promotion (not rebuild):
# oc tag my-app-cicd/my-app:1.2.3 my-app-prod/my-app:stable
```

- Build in CICD namespace; promote tags to app namespaces
- Never rebuild the image per environment — tag and promote
- Use `sha256` digests in production deployments, not mutable tags

---

## Resource Requirements

```yaml
resources:
  requests:
    cpu: 250m
    memory: 512Mi
  limits:
    cpu: 1000m         # 4× request — headroom for burst
    memory: 1Gi        # Same as request for memory (OOM-killable otherwise)
```

Rules:
- Memory limit = memory request (memory is not compressible)
- CPU limit = 2–4× CPU request (CPU is compressible — throttle not kill)
- Set namespace `LimitRange` and `ResourceQuota` — never let workloads run unbounded

---

## Health Probes

```yaml
livenessProbe:
  httpGet: { path: /actuator/health/liveness, port: 8080 }
  initialDelaySeconds: 60
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet: { path: /actuator/health/readiness, port: 8080 }
  initialDelaySeconds: 30
  periodSeconds: 5
  failureThreshold: 3
```

- Spring Boot: use `/actuator/health/liveness` and `/actuator/health/readiness`
- Quarkus: `/q/health/live` and `/q/health/ready`
- Never use the same endpoint for both probes

---

## OpenShift Pipelines Structure

```
tekton/
├── tasks/              ← custom Tasks (reusable)
├── pipelines/          ← Pipeline definitions
├── triggers/           ← EventListener, TriggerTemplate, TriggerBinding
└── workspaces/         ← PVC templates for pipeline workspaces
```

Use `ClusterTask` for standard steps (git-clone, maven, buildah, deploy) — don't rewrite them.
