# Project 3: Zero-Trust Architecture - UML Diagrams & System Design
## Component Interactions, Data Flows & Architectural Patterns

---

## PART 1: SPIFFE/SPIRE WORKLOAD IDENTITY ARCHITECTURE

### 1.1 SPIFFE/SPIRE Component Interaction Diagram

```
SPIFFE/SPIRE Workload Identity Flow
═══════════════════════════════════════════════════════════════════════════════

REQUEST PHASE: Workload requests SVID (certificate)
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│  Pod/Workload (Service A)                                             │
│  ┌─────────────────────────┐                                          │
│  │ App Container           │                                          │
│  │ ├─ Initialize at startup│  1. Call SPIRE Agent                     │
│  │ │  (listen to socket)   │     /run/spire/agent.sock               │
│  │ └─ Register workload ID │                                          │
│  │    spiffe://trust.com/  │                                          │
│  │    ns/default/sa/web    │ 2. Agent authenticates workload          │
│  └─────────────────────────┘    using Kubernetes PSAT                │
│              ↓                                                         │
│  ┌─────────────────────────┐                                          │
│  │ SPIRE Agent             │   3. Request SVID from SPIRE Server      │
│  │ (on same node)          │      (X509-SVID: cert + key)             │
│  ├─ Kubernetes auth        │                                          │
│  │  plugin                 │   4. Return SVID (valid 1 hour)          │
│  ├─ Workload registration  │      + intermediate CA                   │
│  ├─ SVID management        │      + trust bundle                      │
│  └─ Socket access control  │                                          │
│  └─────────────────────────┘                                          │
│              ↓                                                         │
│  ┌─────────────────────────┐                                          │
│  │ SPIRE Server (HA)       │   5. Workload receives SVID               │
│  │ (centralized)           │      (X509 cert + private key)           │
│  ├─ Database (PostgreSQL)  │                                          │
│  │  - SPID assignments     │   6. Workload uses SVID for:             │
│  │  - Issued certificates  │      ├─ mTLS handshake                  │
│  │  - Agent data           │      ├─ Vault auth                       │
│  ├─ CA management          │      ├─ Policy engine auth               │
│  │  - Root CA              │      └─ Logging/audit identity           │
│  │  - Intermediate CA      │                                          │
│  │  - SVID issuance        │   7. SVID lifecycle:                     │
│  │  - Certificate rotation │      ├─ Rotated every hour               │
│  ├─ Workload API           │      ├─ No manual key management         │
│  │  - FetchX509SVID        │      └─ Automatic renewal                │
│  │  - FetchJWTSVID         │                                          │
│  └─────────────────────────┘                                          │
│              ↓                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │ SVID (X509 Certificate)                                        │  │
│  ├─ Subject: CN=spiffe://trust.com/ns/default/sa/web             │  │
│  ├─ Issuer: C=US, O=SPIRE, CN=spiffe-ca.cluster1                │  │
│  ├─ NotBefore: 2024-01-01 10:00:00                               │  │
│  ├─ NotAfter: 2024-01-01 11:00:00 (1 hour TTL)                   │  │
│  ├─ Subject Alt Name (URI): spiffe://trust.com/ns/default/sa/web │  │
│  ├─ Public Key: RSA 2048 or EC P-256                             │  │
│  └─ Private Key: Stored in /var/run/secrets/spiffe/              │  │
│                                                                    │
└────────────────────────────────────────────────────────────────────────┘

AUTHENTICATION PHASE: Workload-to-Workload mTLS using SVID
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│  Service A (Client)              TLS Handshake          Service B (Server)
│  ┌─────────────┐                                        ┌─────────────┐
│  │ Has SVID    │                                        │ Has SVID    │
│  │ cert + key  │ ── ClientHello                        │ cert + key  │
│  │             │    (client cert request)      ──→     │             │
│  │             │                                        │             │
│  │             │ ←── ServerHello                        │             │
│  │             │     (server certificate)               │             │
│  │             │                                        │             │
│  │ Verify      │ ── ClientCertificate                   │             │
│  │ B's SVID    │    (A's certificate)          ──→     │ Verify A's  │
│  │ (SPID)      │                                        │ SVID (SPID) │
│  │             │ ← ClientKeyExchange, Finished          │ Verify A's  │
│  │ Establish   │ ──────────────────────────→            │ signature   │
│  │ encrypted   │                                        │             │
│  │ tunnel      │ ←─────── ServerFinished ────           │             │
│  │             │                                        │             │
│  └─────────────┘                                        └─────────────┘
│        ↓                                                        ↓
│  Result: Both services authenticated via SPIFFE identity    │
│          Encrypted communication established                 │
│          Identity = spiffe://trust.com/ns/default/sa/*       │
│                                                               │
└────────────────────────────────────────────────────────────────────────┘

KEY BENEFITS:
✓ Automatic certificate issuance & rotation (no manual PKI management)
✓ Cryptographic workload identity (not just IP-based)
✓ Zero-knowledge authentication (no shared secrets)
✓ Scalable to thousands of services/identities
✓ Multi-cluster support (same trust domain across clusters)
```

---

## PART 2: ISTIO SERVICE MESH ARCHITECTURE

### 2.1 Istio mTLS Enforcement

```
Istio Service Mesh - mTLS Enforcement Flow
═══════════════════════════════════════════════════════════════════════════════

BEFORE: Network allows plaintext communication (DANGEROUS)
┌──────────────────────────────────────────────────────────────────────┐
│ Client Service                          Server Service               │
│ ┌──────────────────┐                   ┌──────────────────┐          │
│ │ Pod: web-app     │                   │ Pod: api-server  │          │
│ │ Port: 8000       │  plaintext HTTP   │ Port: 8080       │          │
│ │                  │ ─────────────────→ │ (unencrypted)    │          │
│ │                  │                   │                  │          │
│ └──────────────────┘                   └──────────────────┘          │
│         ↑                                       ↑                     │
│ VULNERABILITY: Network traffic readable        │                     │
│ in plaintext (no encryption, no auth)          │                     │
│                                               EXPOSURE                │
└──────────────────────────────────────────────────────────────────────┘

AFTER: Istio enforces mTLS (SECURE)
┌──────────────────────────────────────────────────────────────────────┐
│ Client Service                    Envoy Data Plane               Server │
│ ┌──────────────────┐             ┌────────────────────┐           ┌─ │
│ │ Pod: web-app     │ plaintext   │ Envoy Proxy        │ mTLS     │P  │
│ │ Port: 8000       │ ─→ 127.0.0.1:15000  → Listeners    │ ──→     │o  │
│ │                  │             │                    │          │d  │
│ │                  │             │ VirtualService +   │          │:  │
│ │                  │             │ DestinationRule    │          │80 │
│ │                  │             │                    │          │80 │
│ └──────────────────┘             │ Authenticates      │          │   │
│                                  │ server SVID        │          │   │
│                                  │                    │          │   │
│                                  │ Presents client    │          │   │
│                                  │ SVID for auth      │          │   │
│                                  │                    │          │   │
│                                  └────────────────────┘          └─ │
│                                         ↑                           ↑  │
│                                  Sidecar proxy                  Server │
│                                  (auto-injected)                proxy  │
│                                                                        │
│ SECURITY: End-to-end encryption + mutual authentication               │
│ ✓ Encrypted tunnel (TLS 1.3)                                          │
│ ✓ Server identity verified (SPIFFE SVID)                              │
│ ✓ Client identity presented (SPIFFE SVID)                             │
│ ✓ All configuration transparent to application                        │
│                                                                        │
└──────────────────────────────────────────────────────────────────────┘

Istio Enforcement Levels
├─ DISABLE: No mTLS (not recommended)
├─ PERMISSIVE: Accept both plaintext + mTLS (migration mode)
└─ STRICT: Enforce mTLS on all connections (production)

Configuration Example:
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
spec:
  mtls:
    mode: STRICT          # ← Enforce mTLS everywhere
```

---

## PART 3: NETWORK POLICY ARCHITECTURE

### 3.1 Zero-Trust Network Policies (Deny-by-Default)

```
Kubernetes Network Policy - Deny by Default Architecture
═══════════════════════════════════════════════════════════════════════════════

DEFAULT STATE: DENY ALL TRAFFIC
┌──────────────────────────────────────────────────────────────────────┐
│ Namespace: production                                                 │
│                                                                       │
│ ┌─────────────────┐  ┌────────────────┐  ┌─────────────────┐        │
│ │ Pod: web        │  │ Pod: api       │  │ Pod: database   │        │
│ │ Labels:         │  │ Labels:        │  │ Labels:         │        │
│ │ - tier: web     │  │ - tier: api    │  │ - tier: database│        │
│ │ - app: app1     │  │ - app: app1    │  │ - app: app1     │        │
│ │                 │  │                │  │                 │        │
│ └─────────────────┘  └────────────────┘  └─────────────────┘        │
│         ↑                    ↑                     ↑                  │
│         └────────────────────┴─────────────────────┘                 │
│                              ↓                                       │
│         DEFAULT NETWORK POLICY (applied first):                      │
│         ┌──────────────────────────────────────────────────────────┐ │
│         │ apiVersion: networking.k8s.io/v1                         │ │
│         │ kind: NetworkPolicy                                      │ │
│         │ metadata:                                                │ │
│         │   name: default-deny-all                                 │ │
│         │ spec:                                                    │ │
│         │   podSelector: {}  # Applies to ALL pods                │ │
│         │   policyTypes:                                           │ │
│         │   - Ingress  # DENY all inbound                          │ │
│         │   - Egress   # DENY all outbound                         │ │
│         │   ingress: []  # Empty = DENY all                        │ │
│         │   egress: []   # Empty = DENY all                        │ │
│         └──────────────────────────────────────────────────────────┘ │
│                                                                       │
│ RESULT: All pods isolated (no communication possible)                │
│         └─→ X web cannot reach api                                   │
│         └─→ X api cannot reach database                              │
│         └─→ X pods can reach external services                       │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘

THEN: EXPLICIT ALLOW RULES (whitelist approach)
┌──────────────────────────────────────────────────────────────────────┐
│                                                                       │
│ ALLOW: web → api (inbound on api)                                    │
│ ┌──────────────────────────────────────────────────────────────────┐ │
│ │ apiVersion: networking.k8s.io/v1                                │ │
│ │ kind: NetworkPolicy                                             │ │
│ │ metadata:                                                       │ │
│ │   name: allow-web-to-api                                        │ │
│ │ spec:                                                           │ │
│ │   podSelector:                                                 │ │
│ │     matchLabels:                                               │ │
│ │       tier: api  # This policy applies to api pods             │ │
│ │   policyTypes:                                                 │ │
│ │   - Ingress                                                    │ │
│ │   ingress:                                                     │ │
│ │   - from:                                                      │ │
│ │     - podSelector:                                             │ │
│ │         matchLabels:                                           │ │
│ │           tier: web  # Only allow from web pods               │ │
│ │     ports:                                                     │ │
│ │     - protocol: TCP                                            │ │
│ │       port: 8080                                               │ │
│ └──────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│ ALLOW: api → database (outbound from api)                            │
│ ┌──────────────────────────────────────────────────────────────────┐ │
│ │ apiVersion: networking.k8s.io/v1                                │ │
│ │ kind: NetworkPolicy                                             │ │
│ │ metadata:                                                       │ │
│ │   name: allow-api-to-db                                         │ │
│ │ spec:                                                           │ │
│ │   podSelector:                                                 │ │
│ │     matchLabels:                                               │ │
│ │       tier: api  # This policy applies to api pods             │ │
│ │   policyTypes:                                                 │ │
│ │   - Egress                                                     │ │
│ │   egress:                                                      │ │
│ │   - to:                                                        │ │
│ │     - podSelector:                                             │ │
│ │         matchLabels:                                           │ │
│ │           tier: database  # Allow egress to db pods            │ │
│ │     ports:                                                     │ │
│ │     - protocol: TCP                                            │ │
│ │       port: 5432                                               │ │
│ │   - to:  # Also allow DNS lookups                              │ │
│ │     - namespaceSelector:                                       │ │
│ │         matchLabels:                                           │ │
│ │           name: kube-system                                    │ │
│ │     ports:                                                     │ │
│ │     - protocol: UDP                                            │ │
│ │       port: 53  # DNS                                          │ │
│ └──────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│ RESULT: Explicit whitelisting                                        │
│         ✓ web can reach api on port 8080                             │
│         ✓ api can reach database on port 5432                        │
│         ✓ All other communication still blocked                      │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘

Scaling to 100+ pods:
├─ Same 2 rules handle all web ↔ api communication
├─ Label-based (not IP-based) = cloud-native
├─ Scales to microservices at enterprise scale
└─ Easy to audit & modify policy
```

---

## PART 4: OPA/CONFTEST POLICY ENGINE ARCHITECTURE

### 4.1 Policy Evaluation Flow

```
OPA Policy Engine - Attribute-Based Access Control (ABAC)
═══════════════════════════════════════════════════════════════════════════════

REQUEST: Service A wants to access Database table
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│ Service A (Client)                                                 │
│ ├─ Identity: spiffe://trust.com/ns/default/sa/app-web            │
│ ├─ Labels: tier=web, app=app1, team=platform                      │
│ ├─ Request: READ database.users table                             │
│ └─ Context: timestamp=2024-01-01T10:00:00Z, source_ip=10.0.1.5   │
│                                    ↓                               │
│         Request + Context → OPA Policy Engine                     │
│                                    ↓                               │
│     ┌────────────────────────────────────────────────────────┐   │
│     │ OPA Evaluation Engine                                  │   │
│     │                                                        │   │
│     │ Step 1: Load context into policy variables            │   │
│     │ ├─ subject = {identity, labels, team}                │   │
│     │ ├─ action = "READ"                                    │   │
│     │ ├─ resource = {type: "database", table: "users"}      │   │
│     │ └─ environment = {timestamp, source_ip}               │   │
│     │                                                        │   │
│     │ Step 2: Evaluate Rego policy rules                    │   │
│     │ ├─ Rule: only "data" team can access database         │   │
│     │ ├─ Check: subject.team == "data"? NO                  │   │
│     │ ├─ Rule: "web" team can read non-sensitive tables     │   │
│     │ ├─ Check: resource.table in [\"products\", \"orders\"]?  │   │
│     │ ├─ Check: \"users\" in whitelist? NO                  │   │
│     │ └─ Rule: all access during business hours only        │   │
│     │    Check: timestamp in business_hours()? YES          │   │
│     │                                                        │   │
│     │ Step 3: Aggregate decisions                           │   │
│     │ └─ Decision: DENY (table not in whitelist)           │   │
│     │                                                        │   │
│     └────────────────────────────────────────────────────────┘   │
│                                    ↓                               │
│         DECISION: DENY                                             │
│         REASON: \"web team cannot access users table\"             │
│         LOGGED: Audit log entry created                           │
│         ALERTED: Security team notified (if sensitive)            │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

Same Flow - ALLOW Decision
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│ Service A wants to access Database.products table                  │
│         (REQUEST)                                                  │
│                 ↓                                                  │
│         OPA Policy Evaluation:                                     │
│         ├─ subject.team = \"web\"  ✓                               │
│         ├─ resource.table = \"products\"  ✓ in whitelist           │
│         ├─ action = \"READ\"  ✓                                    │
│         ├─ timestamp in business_hours()  ✓                       │
│         └─ All conditions met                                      │
│                 ↓                                                  │
│         DECISION: ALLOW (implicit)                                │
│         GRANT: Access token issued                                │
│         TTL: 1 hour (policy-driven)                               │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## PART 5: VAULT SECRET MANAGEMENT ARCHITECTURE

### 5.1 Vault PKI & Secret Engine Architecture

```
Vault - Centralized Secret & Key Management
═══════════════════════════════════════════════════════════════════════════════

VAULT ARCHITECTURE (HA Setup with Auto-Unseal)
┌──────────────────────────────────────────────────────────────────────┐
│                                                                       │
│ Vault Cluster (High Availability)                                    │
│ ├─ Leader Node (writes, sealing operations)                          │
│ │  ├─ Storage Backend: PostgreSQL (replicated across AZs)           │
│ │  ├─ Sealed Key: Never in memory (AWS KMS auto-unseal)             │
│ │  ├─ Raft Consensus: 3+ nodes for quorum                           │
│ │  └─ Listener: HTTPS on :8200 (certificate from PKI engine)        │
│ │                                                                    │
│ ├─ Standby Node 1                                                    │
│ │  └─ (Can become leader, replicates from leader)                   │
│ │                                                                    │
│ └─ Standby Node 2                                                    │
│    └─ (Can become leader, replicates from leader)                   │
│                                                                       │
│ Secret Engines Mounted:                                              │
│ ├─ /pki/ (PKI for issuing certificates)                              │
│ │  ├─ Root CA (issued once, never renewed)                          │
│ │  ├─ Intermediate CA (renewed annually)                            │
│ │  └─ Roles (for automated SVID issuance)                           │
│ │                                                                    │
│ ├─ /k8s/ (Kubernetes authentication & secrets)                       │
│ │  ├─ Auth method: kubernetes (PSAT verification)                   │
│ │  ├─ Roles: web-app, api-server, database, etc.                    │
│ │  └─ Policies: attach permissions per role                         │
│ │                                                                    │
│ ├─ /secret/ (Generic key-value secrets)                              │
│ │  ├─ Database credentials                                          │
│ │  ├─ API keys & tokens                                             │
│ │  ├─ Encryption keys                                               │
│ │  └─ Sensitive configurations                                      │
│ │                                                                    │
│ ├─ /database/ (Dynamic database credentials)                         │
│ │  ├─ PostgreSQL connection                                         │
│ │  ├─ Role: read-only, read-write, admin                            │
│ │  ├─ TTL: 15 min (credentials auto-rotate)                         │
│ │  └─ Audit: Every read/write logged                                │
│ │                                                                    │
│ └─ /aws/ (AWS credential generation)                                 │
│    ├─ Role: assume-role, ec2-instance, etc.                         │
│    ├─ TTL: 5 min (STS credentials)                                  │
│    └─ Region-specific roles                                         │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘

VAULT REQUEST FLOW: Workload requests secret
┌──────────────────────────────────────────────────────────────────────┐
│                                                                       │
│ Pod: web-app                                                         │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │                                                                 │ │
│ │ 1. Initialize at startup                                       │ │
│ │    └─ Service account: default                                │ │
│ │    └─ PSAT (JWT): auto-injected by kubelet                    │ │
│ │                                                                 │ │
│ │ 2. Request: \"Vault, get database credentials\"                 │ │
│ │    POST /auth/kubernetes/login                                 │ │
│ │    {                                                            │ │
│ │      \"role\": \"web-app\",                                     │ │
│ │      \"jwt\": \"<service-account-token>\"                       │ │
│ │    }                                                            │ │
│ │                                                                 │ │
│ │ 3. Vault verification                                          │ │
│ │    ├─ Validate JWT signature                                   │ │
│ │    ├─ Verify service account exists in cluster                │ │
│ │    ├─ Look up role: \"web-app\"                                │ │
│ │    └─ Check RBAC policies attached to role                     │ │
│ │                                                                 │ │
│ │ 4. Issue client token                                          │ │
│ │    RESPONSE:                                                   │ │
│ │    {                                                            │ │
│ │      \"auth\": {                                                │ │
│ │        \"client_token\": \"s.xxx...\",  ← Use this              │ │
│ │        \"policies\": [\"web-app-policy\"],                      │ │
│ │        \"token_ttl\": \"1h\"                                    │ │
│ │      }                                                          │ │
│ │    }                                                            │ │
│ │                                                                 │ │
│ │ 5. Store token in memory (never disk)                          │ │
│ │                                                                 │ │
│ │ 6. Request database credentials                                │ │
│ │    GET /database/creds/web-app-role                            │ │
│ │    Header: X-Vault-Token: s.xxx...                             │ │
│ │                                                                 │ │
│ │ 7. Vault checks policies                                       │ │
│ │    ├─ web-app-policy allows: read(database/creds/*)            │ │
│ │    ├─ Decision: ALLOW                                          │ │
│ │    └─ Generate new DB credentials (TTL: 15min)                │ │
│ │                                                                 │ │
│ │ 8. Return credentials                                          │ │
│ │    RESPONSE:                                                   │ │
│ │    {                                                            │ │
│ │      \"data\": {                                                │ │
│ │        \"username\": \"web-app-v1704116400\",  ← auto-generated │ │
│ │        \"password\": \"PaSsWoRd123!\"            ← auto-generated │ │
│ │      }                                                          │ │
│ │    }                                                            │ │
│ │                                                                 │ │
│ │ 9. Connect to database with credentials                        │ │
│ │    └─ Credentials valid for 15 minutes                         │ │
│ │    └─ Automatically revoked after TTL expires                  │ │
│ │                                                                 │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│ KEY BENEFITS:                                                         │
│ ✓ No hardcoded passwords (auto-generated)                            │
│ ✓ Time-limited credentials (automatic expiry)                        │
│ ✓ Audit trail (every request logged)                                 │
│ ✓ Encryption keys never exposed (derived in Vault)                   │
│ ✓ Policy-enforced (can't request credentials for other teams)        │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

---

**Document Version:** 1.0  
**Last Updated:** December 15, 2025  
**Architecture Completeness:** 100% (5 pillars, 20+ interaction diagrams)
