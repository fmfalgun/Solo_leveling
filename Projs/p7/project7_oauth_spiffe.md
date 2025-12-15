# Project 7: API Gateway - OAuth2, SPIFFE, Token Management & Authorization
## Authentication Architecture, Security Implementation & Policy Engine

---

## PART 1: OAUTH2/OIDC IMPLEMENTATION DETAILS

### OAuth2 Grant Types Supported

```
1. AUTHORIZATION CODE GRANT (Most common for web apps)
   Flow: User Login → Redirect to OAuth server → User consent → 
         Code issued → Backend exchanges code for token
   
   Implementation:
   - GET /authorize?client_id=xxx&redirect_uri=xxx&scope=read+write
   - POST /token (code exchange)
   - Tokens: Access token (short-lived), Refresh token (long-lived)

2. CLIENT CREDENTIALS GRANT (Service-to-service, no user context)
   Flow: Service sends credentials → Receives access token
   
   Implementation:
   - POST /token (client_id, client_secret)
   - Token: Access token (long-lived for machine-to-machine)

3. IMPLICIT GRANT (Legacy, browser-based SPA)
   Flow: Direct token issuance (no code exchange needed)
   
   Implementation:
   - GET /authorize → Token issued directly
   - Security: More vulnerable, PKCE recommended

4. RESOURCE OWNER PASSWORD CREDENTIALS (Legacy, use with caution)
   Flow: User provides credentials directly (not recommended)
   
   Implementation:
   - POST /token (username, password)
```

### Token Management

```python
class TokenManager:
    """Manages OAuth2 token lifecycle"""
    
    def issue_access_token(user_id, scope, client_id):
        """Issue JWT access token (15-60 min expiration)"""
        payload = {
            'sub': user_id,
            'scope': scope,
            'aud': client_id,
            'exp': time.time() + 3600,  # 1 hour
            'iat': time.time(),
            'jti': uuid.uuid4()  # unique token ID
        }
        return jwt.encode(payload, private_key, algorithm='RS256')
    
    def issue_refresh_token(user_id, client_id):
        """Issue refresh token (7-365 days expiration)"""
        payload = {
            'sub': user_id,
            'aud': client_id,
            'exp': time.time() + (30 * 86400),  # 30 days
            'type': 'refresh'
        }
        # Store in Redis with revocation support
        return jwt.encode(payload, private_key, algorithm='RS256')
    
    def validate_token(token):
        """Validate token signature & expiration"""
        try:
            decoded = jwt.decode(token, public_key, algorithms=['RS256'])
            # Check if revoked
            if is_revoked(decoded['jti']):
                return False
            return decoded
        except jwt.ExpiredSignatureError:
            return False
    
    def refresh_access_token(refresh_token):
        """Exchange refresh token for new access token"""
        decoded = validate_token(refresh_token)
        if decoded['type'] != 'refresh':
            raise InvalidTokenError()
        return issue_access_token(decoded['sub'], decoded['aud'])
    
    def revoke_token(token_jti):
        """Add token to revocation list (blacklist)"""
        redis.setex(f'revoked:{token_jti}', 86400, True)
```

### ID Token (OIDC Extension)

```
ID Token = JWT containing user identity information

Payload Example:
{
  "iss": "https://oauth.example.com",
  "sub": "user123",
  "aud": "client_id",
  "exp": 1234567890,
  "iat": 1234567800,
  "name": "John Doe",
  "email": "john@example.com",
  "email_verified": true,
  "picture": "https://...",
  "groups": ["admin", "developers"]
}

Used by: Client-side applications (verify user identity)
Different from: Access token (which is used for API authorization)
```

---

## PART 2: SPIFFE INTEGRATION

### SPIFFE SVID (SPIFFE Verifiable Identity Document)

```
SVID = X.509 certificate binding workload to SPIFFE ID

SPIFFE ID Format:
spiffe://trust-domain/path/to/service

Example IDs:
- spiffe://example.com/ns/production/sa/my-app
- spiffe://example.com/ns/staging/sa/database
- spiffe://example.com/host/web-server-01

SVID Components:
1. Certificate (X.509, valid ~1 hour)
   - Issued by SPIRE
   - Contains SPIFFE ID in URI SAN extension
   - Short-lived, auto-rotated

2. Private Key
   - Kept on workload machine
   - Used for mTLS connections

3. CA Bundle
   - Public certs for verification
   - Auto-updated
```

### Service-to-Service Authentication (mTLS)

```go
// Service A (Client) - using SPIFFE SVID
source, _ := workloadapi.NewX509Source(ctx)
client := &http.Client{
    Transport: &http.Transport{
        TLSClientConfig: &tls.Config{
            GetClientCertificate: source.GetX509SVID,
            RootCAs: spiffe_cas,
        },
    },
}

// Call Service B with mTLS
resp, _ := client.Get("https://service-b.example.com/api")

// Service B (Server) - verify client identity
tlsConfig := &tls.Config{
    Certificates: []tls.Certificate{serverCert},
    ClientAuth: tls.RequireAndVerifyClientCert,
    ClientCAs: spiffe_cas,
}

// Extract client identity from certificate
func handleRequest(w http.ResponseWriter, r *http.Request) {
    clientCert := r.TLS.PeerCertificates[0]
    clientID, _ := extractSPIFFEID(clientCert)
    // clientID = "spiffe://example.com/ns/prod/sa/app-a"
}
```

---

## PART 3: AUTHORIZATION ENGINE (OPA)

### Role-Based Access Control (RBAC)

```rego
# OPA policy for RBAC

# Define roles and their permissions
role_permissions[role] = permissions {
    role == "admin"
    permissions := ["read", "write", "delete", "admin"]
} {
    role == "developer"
    permissions := ["read", "write"]
} {
    role == "readonly"
    permissions := ["read"]
}

# User-to-role mapping
user_roles["john@example.com"] = ["admin"]
user_roles["jane@example.com"] = ["developer"]
user_roles["public@example.com"] = ["readonly"]

# Main authorization rule
allow {
    user := input.user
    action := input.action
    resource := input.resource
    
    # Get user's role
    role := user_roles[user][_]
    
    # Get role's permissions
    permission := role_permissions[role][_]
    
    # Check if permission allows action
    action == permission
}

# Example: Deny data deletion for non-admins
deny {
    input.action == "delete"
    user_roles[input.user][_] != "admin"
}
```

### Attribute-Based Access Control (ABAC)

```rego
# ABAC: More fine-grained than RBAC
# Based on attributes of: user, resource, environment

allow {
    # User attribute: department is "engineering"
    input.user_dept == "engineering"
    
    # Resource attribute: tier is "internal"
    input.resource_tier == "internal"
    
    # Environment: business hours (9-17:00)
    time.now_ns()[0:5] > "09000" and time.now_ns()[0:5] < "17000"
    
    # Action: read/write allowed
    input.action in ["read", "write"]
}

# Example: ABAC rule for sensitive data
allow {
    input.user_level >= 3  # User level 3+
    input.resource_sensitivity == "high"
    input.user_mfa_enabled == true  # MFA required for sensitive data
    input.location == "office"  # Office access only
}
```

### SPIFFE Identity-Based Policies

```rego
# Policies based on SPIFFE workload identity

allow {
    # Client is a trusted service (identified by SPIFFE ID)
    client_id := input.client_spiffe_id
    
    # Only allow if client is in same trust domain
    startswith(client_id, "spiffe://example.com")
    
    # Allow all actions for in-domain services
    true
}

# Example: Restrict database access to specific services
allow {
    # Only database reader service can access database
    input.client_spiffe_id == "spiffe://example.com/ns/prod/sa/db-reader"
    input.resource == "database"
    input.action in ["read"]
}

deny {
    # Prevent data exfiltration
    input.action == "bulk_export"
    not startswith(input.client_spiffe_id, "spiffe://example.com")
}
```

---

## PART 4: RATE LIMITING & ABUSE DETECTION

### Token Bucket Rate Limiter

```python
class RateLimiter:
    """Token bucket algorithm for rate limiting"""
    
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity        # tokens
        self.refill_rate = refill_rate  # tokens per second
        self.tokens = capacity
        self.last_refill = time.time()
    
    def allow_request(self):
        """Check if request is allowed"""
        # Refill tokens based on time elapsed
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        
        self.tokens = min(self.capacity, 
                         self.tokens + tokens_to_add)
        self.last_refill = now
        
        # Allow if tokens available
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

# Per-user rate limiting (Redis-backed)
RATE_LIMITS = {
    "free_tier": {"requests": 100, "window": 3600},    # 100 req/hour
    "pro_tier": {"requests": 10000, "window": 3600},   # 10K req/hour
}

def check_rate_limit(user_id, tier):
    key = f"rate_limit:{user_id}"
    current = redis.incr(key)
    
    if current == 1:
        # First request in window, set expiration
        redis.expire(key, RATE_LIMITS[tier]["window"])
    
    if current > RATE_LIMITS[tier]["requests"]:
        raise RateLimitExceeded()
```

### Anomaly Detection (ML-based)

```python
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    """Detect abnormal API usage patterns"""
    
    def __init__(self):
        self.model = IsolationForest(contamination=0.05)
        self.features = ['request_count', 'error_rate', 'avg_latency']
    
    def train_baseline(self, historical_data):
        """Train on normal usage patterns"""
        X = historical_data[self.features].values
        self.model.fit(X)
        self.threshold = np.percentile(
            self.model.score_samples(X), 5
        )
    
    def is_anomalous(self, user_id, metrics):
        """Check if current behavior is anomalous"""
        X = [[metrics['request_count'], 
              metrics['error_rate'],
              metrics['avg_latency']]]
        
        score = self.model.score_samples(X)[0]
        return score < self.threshold
    
    def detect_threats(self):
        """Detect known attack patterns"""
        # Brute-force detection
        if failed_logins > 5 in 1_minute:
            return "BRUTE_FORCE"
        
        # Credential stuffing
        if unique_ips > 10 and same_password in 5_minutes:
            return "CREDENTIAL_STUFFING"
        
        # Token theft (unusual location/device)
        if ip_location_changed and new_device:
            return "POSSIBLE_TOKEN_THEFT"
        
        return None
```

---

## PART 5: KUBERNETES DEPLOYMENT

### Helm Chart for API Gateway

```yaml
# values.yaml
replicaCount: 3

image:
  repository: api-gateway
  tag: "1.0.0"

service:
  type: LoadBalancer
  port: 443
  targetPort: 8443

oauth2:
  enabled: true
  issuer: "https://oauth.example.com"
  clientSecretRef: oauth-secret

spiffe:
  enabled: true
  trustDomain: "example.com"
  agentAddr: "unix:///run/spire/sockets/agent.sock"

rateLimit:
  enabled: true
  redis: "redis://redis:6379"
  defaultLimit: "1000/hour"

monitoring:
  prometheus:
    enabled: true
    scrapeInterval: 30s
  grafana:
    dashboards: true

# helm install api-gateway ./chart -f values.yaml
```

---

**Document Version:** 1.0  
**OAuth2 Grant Types:** 4+  
**SPIFFE Integration:** Full (mTLS + SVID)  
**Authorization Models:** RBAC + ABAC + Identity-based  
**Rate Limiting:** Token bucket + per-user + anomaly detection  
**Deployment:** Kubernetes native (Helm charts)
