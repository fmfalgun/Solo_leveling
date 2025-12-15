# Project 7: API Gateway - System Architecture & Database Design
## Complete Technical Specifications, System Components & Data Models

---

## ARCHITECTURE OVERVIEW

### Layered Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                           │
│  (Web UI, API Documentation, Developer Portal)                      │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    API GATEWAY LAYER (This Project)                 │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Auth/Authz  │  │ Rate Limit   │  │ Monitoring   │              │
│  │ • OAuth2    │  │ • Token Bkt  │  │ • Prometheus │              │
│  │ • SPIFFE    │  │ • DDoS Mitig │  │ • Logging    │              │
│  │ • Policies  │  │ • Anomaly    │  │ • Tracing    │              │
│  └─────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│              IDENTITY PROVIDERS & SECRET STORES                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ OIDC Servers │  │ HashiCorp    │  │ SPIRE        │              │
│  │ • Google     │  │ Vault        │  │ Server       │              │
│  │ • GitHub     │  │ (Secrets)    │  │ (SVIDs)      │              │
│  │ • Microsoft  │  │              │  │              │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ PostgreSQL   │  │ Redis        │  │ Elasticsearch│              │
│  │ • Users      │  │ • Token Cache│  │ • Audit Logs │              │
│  │ • Policies   │  │ • Sessions   │  │ • Analytics  │              │
│  │ • Audit Log  │  │ • Blacklist  │  │              │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    BACKEND SERVICES                                  │
│         (Your APIs protected by this gateway)                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## DATABASE SCHEMA

### PostgreSQL Tables

```sql
-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),  -- bcrypt hash
    name VARCHAR(255),
    roles JSONB,  -- e.g., ["admin", "developer"]
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- OAuth2 Clients Table
CREATE TABLE oauth2_clients (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    client_secret_hash VARCHAR(255),
    redirect_uris JSONB,  -- array of allowed redirect URIs
    grant_types JSONB,  -- ["authorization_code", "refresh_token"]
    scopes JSONB,  -- ["openid", "profile", "email"]
    public BOOLEAN,  -- is public client (e.g., mobile app)
    owner_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Authorization Codes (short-lived, ~10 minutes)
CREATE TABLE authorization_codes (
    code VARCHAR(255) PRIMARY KEY,
    client_id VARCHAR(255) REFERENCES oauth2_clients(id),
    user_id UUID REFERENCES users(id),
    scopes JSONB,
    redirect_uri VARCHAR(255),
    nonce VARCHAR(255),  -- OIDC
    code_challenge VARCHAR(255),  -- PKCE
    code_challenge_method VARCHAR(10),  -- S256, plain
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Access Tokens (stored for revocation)
CREATE TABLE access_tokens (
    jti VARCHAR(255) PRIMARY KEY,  -- JWT ID
    token_hash VARCHAR(255) UNIQUE,
    user_id UUID REFERENCES users(id),
    client_id VARCHAR(255) REFERENCES oauth2_clients(id),
    scopes JSONB,
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Refresh Tokens
CREATE TABLE refresh_tokens (
    id VARCHAR(255) PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    client_id VARCHAR(255) REFERENCES oauth2_clients(id),
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    rotation_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- API Keys (for service-to-service without OAuth2)
CREATE TABLE api_keys (
    id VARCHAR(255) PRIMARY KEY,
    key_hash VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    owner_id UUID REFERENCES users(id),
    scopes JSONB,
    rate_limit INT,  -- requests per hour
    expires_at TIMESTAMP,
    revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_used TIMESTAMP
);

-- Authorization Policies (OPA policies)
CREATE TABLE policies (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    policy_rego TEXT,  -- Rego policy code
    version INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Audit Log (all auth events)
CREATE TABLE audit_log (
    id UUID PRIMARY KEY,
    event_type VARCHAR(50),  -- "LOGIN_SUCCESS", "TOKEN_ISSUED", "AUTHZ_DENIED"
    user_id UUID REFERENCES users(id),
    resource VARCHAR(255),
    action VARCHAR(50),  -- "READ", "WRITE", "DELETE"
    authorized BOOLEAN,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- SPIFFE Service Accounts
CREATE TABLE spiffe_service_accounts (
    id VARCHAR(255) PRIMARY KEY,  -- SPIFFE ID
    name VARCHAR(255),
    namespace VARCHAR(255),  -- k8s namespace
    service_account VARCHAR(255),  -- k8s service account
    trust_domain VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Redis Data Structures

```
# Token Cache (speed up validation)
CACHE:TOKEN:{jti} = {
  "user_id": "uuid",
  "scopes": ["read", "write"],
  "expires": 1234567890
}
TTL: 300 seconds (5 minutes)

# Refresh Token Storage
RT:{refresh_token_id} = {
  "user_id": "uuid",
  "created": 1234567800,
  "rotations": 5
}
TTL: 30 days

# Session Management
SESSION:{session_id} = {
  "user_id": "uuid",
  "authenticated": true,
  "created": 1234567800
}
TTL: 3600 seconds (1 hour)

# Token Revocation Blacklist
BLACKLIST:{jti} = true
TTL: token expiration time

# Rate Limit Tracking
RATELIMIT:{user_id}:HOUR = 342  # requests in current hour
TTL: 3600 seconds

# Anomaly Detection Features
METRICS:{user_id} = {
  "requests_1h": 150,
  "requests_24h": 3200,
  "errors_1h": 5,
  "unique_ips_24h": 3
}
TTL: 86400 seconds (24 hours)
```

---

## API ENDPOINTS SPECIFICATION

### OAuth2 Endpoints

```
POST /oauth/authorize
  Query params: client_id, redirect_uri, response_type=code, scope, state
  Returns: Redirect to login or consent screen
  
POST /oauth/token
  Body: {client_id, client_secret, grant_type, code/username/password}
  Returns: {access_token, refresh_token, expires_in, token_type}

POST /oauth/revoke
  Body: {token, token_type_hint}
  Returns: 200 OK

POST /oauth/introspect
  Body: {token}
  Returns: {active, scope, client_id, username, exp}

GET /oauth/userinfo
  Headers: Authorization: Bearer {access_token}
  Returns: {sub, email, name, groups}
```

### API Key Management Endpoints

```
POST /api/keys
  Body: {name, scopes, rate_limit}
  Returns: {key_id, key_secret}  # Secret shown only once!

GET /api/keys
  Returns: [{id, name, scopes, created_at}]

DELETE /api/keys/{key_id}
  Returns: 204 No Content

GET /api/keys/{key_id}/usage
  Returns: {requests_month, last_used, rate_limit_remaining}
```

### Authorization & Policy Endpoints

```
POST /authz/evaluate
  Body: {user, resource, action, attributes}
  Returns: {allowed: true/false, reason}

GET /authz/policies
  Returns: [policies]

POST /authz/policies
  Body: policy Rego code
  Returns: {id, version}
```

---

## PERFORMANCE CHARACTERISTICS

### Throughput & Latency

```
Operation              99th Percentile Latency    Throughput
─────────────────────────────────────────────────────────────
Token validation       <50ms                      10K req/sec
Authorization check    <30ms                      15K req/sec
Rate limit check       <10ms                      50K req/sec
API key lookup         <5ms                       100K req/sec

Bottleneck (single instance):
├─ Database queries: 100-200ms (without cache)
├─ Signature verification: 50-100ms
├─ Policy evaluation: 20-50ms
└─ Total: 170-350ms (mitigated with caching)

With Caching (recommended):
├─ Token cache hit: <1ms
├─ Policy cache hit: <1ms
├─ Rate limit (in-memory): <5ms
└─ Total: 5-10ms (10-50x improvement!)

Cache Hit Rates (targets):
├─ Token cache: 90%+ (most tokens valid)
├─ Policy cache: 85%+ (policies stable)
├─ Rate limit cache: 99%+ (same user requests)
```

---

**Document Version:** 1.0  
**Database Schema:** PostgreSQL + Redis  
**API Endpoints:** 20+ (OAuth2, OIDC, API keys, policies)  
**Performance:** <50ms latency, 10K+ req/sec  
**Status:** Complete Specification
