# Project 7: API Gateway - Complete Reference Guide & Resource Library
## APIs, OAuth2, SPIFFE, DevSecOps Standards & Implementation Resources

---

## SECTION 1: STANDARDS & FRAMEWORKS

### OAuth 2.0 Standards

**RFC 6749: The OAuth 2.0 Authorization Framework**
- Authorization Code Grant (most secure for web apps)
- Client Credentials Grant (service-to-service)
- Implicit Grant (legacy, browser-based)
- Resource Owner Password Credentials (legacy, not recommended)

**RFC 6750: The OAuth 2.0 Bearer Token Usage**
- How to use access tokens in API requests
- Format: `Authorization: Bearer <token>`

**RFC 7636: Proof Key for Public Clients (PKCE)**
- Protection against authorization code interception attacks
- Mandatory for mobile/single-page apps

**RFC 7662: OAuth 2.0 Token Introspection**
- How to validate/revoke tokens
- Standard endpoint: POST /introspect

---

### OpenID Connect (OIDC)

**OIDC = OAuth2 + Identity Layer**
- Extends OAuth2 with authentication
- Adds ID Token (signed JWT with user identity)
- Adds /userinfo endpoint
- Standard discovery endpoint: /.well-known/openid-configuration

**OIDC Flows:**
- Authorization Code (with form_post)
- Implicit (legacy)
- Hybrid (combination)

---

### SPIFFE (Secure Production Identity Framework for Everyone)

**SPIFFE = Workload Identity Standard**
- SPIFFE ID format: `spiffe://trust-domain/path/to/service`
- SVID = SPIFFE Verifiable Identity Document (X.509 certificate)
- Issued by SPIRE (runtime environment)

**SPIFFE Security Properties:**
- Automatic identity provisioning
- Short-lived credentials (1 hour default)
- Automatic rotation (no manual key management)
- mTLS for service-to-service (mutual authentication)
- Works across clouds (AWS, GCP, Kubernetes, VM, bare metal)

---

## SECTION 2: TOOLS & LIBRARIES

### OAuth2/OIDC Implementations

**Open-Source:**
- Keycloak (full-featured identity platform, Java)
- Hydra (lightweight OAuth2/OIDC server, Go)
- Dex (OpenID Connect provider, Go)
- Authelia (simple identity server, Go)
- FusionAuth (commercial-grade open source, Java)

**Commercial:**
- Auth0 ($1K-$50K/month)
- Okta ($2K-$100K+/month)
- Azure AD B2C ($0.6-$6/monthly active user)
- Google Cloud Identity ($4-$8/month)

**Libraries:**
- Python: python-oauth2, authlib
- Go: ory/hydra, dex
- Node.js: openid-client, passport.js
- Java: Spring Security OAuth2, Keycloak
- Rust: actix-web + oauth2 crate

---

### SPIFFE/SPIRE

**SPIRE (runtime for issuing SVIDs)**
- Open-source (CNCF sandbox)
- Server + Agents
- Kubernetes native support
- AWS EC2, GCP, VM attestation

**SPIFFE Libraries:**
- go-spiffe (Go SDK)
- java-spiffe (Java SDK)
- python-spiffe (Python SDK)
- js-spiffe (Node.js SDK)

---

### API Gateway Platforms

**Open-Source:**
- Kong (Lua-based, extensible)
- Traefik (cloud-native, dynamic)
- Envoy (C++, high-performance)
- Tyk (Go, Kubernetes-native)

**Commercial:**
- AWS API Gateway ($35K-$500K+/year)
- Azure API Management ($0.75-$40+/month)
- Google Cloud Apigee ($5-$100K+/month)
- Mulesoft ($30K-$500K+/year)

---

### Authorization (Policy Engines)

**Open Policy Agent (OPA)**
- Language: Rego
- RBAC, ABAC, attribute-based policies
- Decoupled from application
- Used by Netflix, Twilio, Cloudflare

**Alternatives:**
- Casbin (Go, role-based)
- Keto (Ory, relationship-based)
- Cedar (Amazon, attribute-based)

---

## SECTION 3: BEST PRACTICES

### API Security Checklist

- [ ] HTTPS/TLS 1.2+ (enforce HTTPS everywhere)
- [ ] OAuth2/OIDC (human user authentication)
- [ ] SPIFFE (service-to-service identity)
- [ ] Rate limiting (prevent abuse, DoS)
- [ ] Input validation (prevent injection attacks)
- [ ] Output encoding (prevent XSS)
- [ ] CORS properly configured (only trusted origins)
- [ ] CSRF tokens (state-changing operations)
- [ ] Audit logging (who did what, when)
- [ ] Secrets management (no hardcoded credentials)
- [ ] API versioning (backward compatibility)
- [ ] Error handling (don't expose internals)
- [ ] Performance monitoring (detect anomalies)
- [ ] Incident response (breach procedures)

---

### Token Security Best Practices

**Access Tokens:**
- Short-lived (15-60 minutes)
- Signed with private key (RSA-256, ES-256)
- Include user ID, scopes, expiration
- Never store sensitive data in token
- Validate signature + expiration

**Refresh Tokens:**
- Long-lived (7-365 days)
- Stored securely (httpOnly cookies or secure storage)
- Can be revoked
- Rotated on use (refresh token rotation)
- Keep track of issued tokens

**Token Revocation:**
- Maintain blacklist (Redis, memory)
- Check before token validation
- Clear on user logout
- Expire automatically (token expiration)

---

### Rate Limiting Strategies

**By User:**
- Premium tier: 10,000 req/hour
- Standard tier: 1,000 req/hour
- Free tier: 100 req/hour

**By Endpoint:**
- Login: 5 attempts/minute (brute-force protection)
- Password reset: 3 attempts/hour
- API calls: 1,000 req/minute (default)

**Detection:**
- Distributed rate limiting (across servers)
- Sliding window algorithm (more accurate than fixed windows)
- Graceful degradation (queue requests instead of rejecting)

---

## SECTION 4: SECURITY INCIDENT RESPONSE

### Common API Attacks

**1. Brute Force (Try many passwords)**
- Detection: 5+ failed logins in 1 minute
- Response: Lock account, alert user, increase delay

**2. Credential Stuffing (Use leaked credentials)**
- Detection: Login from unusual location/device
- Response: Force password reset, require MFA

**3. Token Theft (Steal access tokens)**
- Detection: Token used from multiple IPs, unusual patterns
- Response: Revoke tokens, alert user, require re-login

**4. Rate Limit Bypass**
- Detection: Requests exceed published limits
- Response: Block IP/user, alert security team

**5. CORS Misconfiguration**
- Detection: Requests from unexpected origins
- Response: Tighten CORS policies, investigation

---

## SECTION 5: COMPLIANCE & REGULATIONS

### API Data Protection

**GDPR (EU):**
- User consent required for data collection
- Right to be forgotten (delete user data)
- Data breach notification within 72 hours
- Privacy by design

**HIPAA (Healthcare):**
- Encrypt all data in transit (TLS 1.2+)
- Encrypt sensitive data at rest
- Audit logging of all access
- User authentication mandatory

**PCI-DSS (Payment Card):**
- No cardholder data in logs/responses
- TLS for all transmissions
- Strong authentication (MFA)
- Regular security assessments

---

## SECTION 6: PERFORMANCE OPTIMIZATION

### Caching Strategies

**Token Caching:**
- Store validated tokens in Redis (5-10 min TTL)
- Avoid repeated signature validation
- Monitor cache hit rate (should be >90%)

**Policy Caching:**
- Cache authorization decisions (5-30 min)
- Invalidate on policy changes
- Per-user cache (not global!)

---

### Latency Optimization

**Token Validation Latency:**
- Target: <50ms (99th percentile)
- Without caching: 100-200ms (signature validation)
- With caching: <10ms (memory lookup)

**Authorization Latency:**
- OPA evaluation: 10-50ms
- Cache hit: <1ms
- Network round-trip: varies (50-200ms)

---

## SECTION 7: LEARNING RESOURCES

### Books

- "OAuth 2.0 in Action" - Justin Richer, Antonio Sanso
- "Microservices Security in Action" - Prabath Siriwardena
- "Zero Trust Networks" - Evan Gilman, Doug Barth

### Online Courses

- OAuth2/OIDC basics (OAuth2.com)
- SPIFFE/SPIRE tutorials (spiffe.io)
- Kubernetes API security (Linux Academy)

### Standards Documents

- RFC 6749 (OAuth 2.0)
- OIDC Core Spec
- SPIFFE Specification
- OWASP API Security Top 10

---

**Document Version:** 1.0  
**Standards Covered:** OAuth2, OIDC, SPIFFE  
**Tools Documented:** 30+  
**Best Practices:** 50+  
**Compliance Frameworks:** 3 (GDPR, HIPAA, PCI-DSS)  
**Status:** Complete Reference Guide
