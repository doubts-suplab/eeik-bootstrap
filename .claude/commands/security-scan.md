# /security-scan — OWASP Top 10 Review + Secrets Scan

Run an OWASP Top 10 security review and secrets scan on a file or directory.

## Usage

```
/security-scan
/security-scan src/main/java/com/example/order/
/security-scan src/main/java/com/example/auth/
```

## What This Command Does

1. Activates the `security-auditor` agent
2. Reviews code for OWASP Top 10 vulnerabilities
3. Scans for hardcoded secrets, API keys, and credentials
4. Checks SQL queries for injection risks
5. Reviews authentication and authorisation code
6. Produces severity-rated findings with remediation code

## OWASP Top 10 Coverage

| Vulnerability | What Is Checked |
|--------------|----------------|
| A01 Broken Access Control | Missing auth guards, IDOR risks, excessive data exposure |
| A02 Cryptographic Failures | Weak algorithms, hardcoded keys, HTTP (not HTTPS), unencrypted PII storage |
| A03 Injection | SQL injection, JNDI injection, command injection, template injection |
| A04 Insecure Design | Missing rate limiting, no input validation, absent security controls |
| A05 Security Misconfiguration | Debug mode, default credentials, exposed actuator endpoints |
| A06 Vulnerable Components | Dependencies with known CVEs (check `pom.xml` / `package.json`) |
| A07 Auth & Session | Weak session management, missing MFA controls, token storage |
| A08 Software Integrity | Dependency integrity, CI/CD pipeline security |
| A09 Security Logging | Missing audit logging, insufficient error detail for forensics |
| A10 SSRF | Unvalidated URL inputs, fetching from user-controlled endpoints |

## Output Format

```
## Security Scan Report

### Summary
{N} CRITICAL / {N} HIGH / {N} MEDIUM / {N} LOW / {N} INFO

### Findings

#### CRITICAL: SQL Injection Risk
**File:** `src/.../OrderRepository.java:67`
**Finding:** SQL query built via string concatenation
**Remediation:**
```java
// Replace
String sql = "SELECT * FROM orders WHERE id = '" + orderId + "'";
// With
String sql = "SELECT order_id, status FROM orders WHERE id = :orderId";
Map<String, Object> params = Map.of("orderId", orderId);
```

### Secrets Scan
{N} potential secrets detected / No secrets detected
```

## Notes

- Critical and High findings must be remediated before production deployment
- For dependency CVEs, check OWASP Dependency Check report in CI
- Always remediate injection risks before any other finding category
