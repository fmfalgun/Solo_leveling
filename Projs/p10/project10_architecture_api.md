# Project 10: Microservices Security - Architecture Diagrams, Database & API Design

---

## SYSTEM ARCHITECTURE LAYERS

```
MULTI-CLUSTER KUBERNETES SECURITY ORCHESTRATION
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────┐
│  MANAGEMENT & CONTROL PLANE (Centralized)       │
│  ├─ Policy server (central)                     │
│  ├─ Compliance controller                       │
│  ├─ Audit aggregator                            │
│  └─ Central dashboards & APIs                   │
└────────────────┬────────────────────────────────┘
                 │
     ┌───────────┼───────────┐
     ↓           ↓           ↓
┌──────────┐ ┌──────────┐ ┌──────────┐
│ EKS      │ │ GKE      │ │ AKS      │
│ Cluster  │ │ Cluster  │ │ Cluster  │
│ (AWS)    │ │ (Google) │ │ (Azure)  │
└────┬─────┘ └────┬─────┘ └────┬─────┘
     │            │            │
     ├────────────┼────────────┤
     │            │            │
┌────▼────────────▼────────────▼────┐
│   SECURITY ORCHESTRATION LAYER     │
│  ├─ CIS Benchmark enforcement      │
│  ├─ Pod security policies          │
│  ├─ Network policies               │
│  ├─ RBAC synchronization           │
│  └─ Secrets management             │
└────┬─────────────────────────────┬─┘
     │                             │
┌────▼──────────────┐     ┌────────▼──┐
│ SERVICE MESH      │     │ WORKLOAD   │
│ (Istio)           │     │ IDENTITY   │
│ ├─ mTLS           │     │ (SPIFE/SPIRE)
│ ├─ Auth policies  │     │ ├─ SVID    │
│ ├─ Traffic mgmt   │     │ ├─ Attestation
│ └─ Observability  │     │ └─ Federation
└────┬──────────────┘     └────────┬──┘
     │                            │
     │         ┌──────────────┐   │
     └────────▶│ RUNTIME SEC  │◀──┘
              │ (Falco)      │
              │ ├─ Monitoring│
              │ ├─ Policies  │
              │ └─ Incidents │
              └──────────────┘
                     │
                     ▼
              ┌──────────────┐
              │ DASHBOARDS   │
              │ & REPORTING  │
              └──────────────┘
```

---

## DATABASE SCHEMA

### PostgreSQL Tables (Core)

```sql
-- Clusters (multi-cloud management)
CREATE TABLE clusters (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    cloud_provider VARCHAR(50),  -- aws, gcp, azure
    region VARCHAR(100),
    k8s_version VARCHAR(20),
    cis_score FLOAT,
    last_audit TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Workloads (pods, deployments, etc.)
CREATE TABLE workloads (
    id UUID PRIMARY KEY,
    cluster_id UUID REFERENCES clusters(id),
    namespace VARCHAR(255),
    name VARCHAR(255),
    kind VARCHAR(50),  -- Deployment, DaemonSet, etc.
    image VARCHAR(500),
    service_account VARCHAR(255),
    trust_domain VARCHAR(255),  -- SPIFFE trust domain
    created_at TIMESTAMP DEFAULT NOW()
);

-- SPIFFE Identities
CREATE TABLE spiffe_identities (
    id UUID PRIMARY KEY,
    workload_id UUID REFERENCES workloads(id),
    spiffe_id VARCHAR(500),  -- spiffe://trust-domain/service/name
    svid_not_before TIMESTAMP,
    svid_not_after TIMESTAMP,
    public_key BYTEA,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Network Policies
CREATE TABLE network_policies (
    id UUID PRIMARY KEY,
    cluster_id UUID REFERENCES clusters(id),
    namespace VARCHAR(255),
    name VARCHAR(255),
    policy_json JSONB,  -- K8s NetworkPolicy spec
    created_at TIMESTAMP DEFAULT NOW()
);

-- Compliance Audits
CREATE TABLE compliance_audits (
    id UUID PRIMARY KEY,
    cluster_id UUID REFERENCES clusters(id),
    framework VARCHAR(50),  -- CIS, PCI-DSS, HIPAA
    check_name VARCHAR(255),
    status BOOLEAN,
    evidence TEXT,
    remediation TEXT,
    audit_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Security Events (Falco)
CREATE TABLE security_events (
    id UUID PRIMARY KEY,
    cluster_id UUID REFERENCES clusters(id),
    event_type VARCHAR(100),  -- container_escape, privilege_escalation
    severity ENUM('critical', 'high', 'medium', 'low'),
    workload_id UUID REFERENCES workloads(id),
    description TEXT,
    detected_at TIMESTAMP,
    response_action VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## REST API ENDPOINTS (30+)

### Cluster Management
```
GET /api/clusters
  Returns: [{id, name, cloud_provider, cis_score, status}]

GET /api/clusters/{cluster_id}
  Returns: Detailed cluster information + compliance status

POST /api/clusters/scan
  Body: {cluster_id}
  Returns: {scan_id, status: "scanning"}
```

### Workload Security
```
GET /api/clusters/{cluster_id}/workloads
  Returns: [{namespace, name, image, spiffe_id, mTLS_status}]

GET /api/workloads/{workload_id}/security-posture
  Returns: {cis_violations, network_exposure, rbac_issues}

POST /api/workloads/{workload_id}/remediate
  Body: {remediation_type: "apply_network_policy"}
  Returns: {action_id, status: "pending"}
```

### Compliance
```
GET /api/clusters/{cluster_id}/compliance
  Returns: {cis: 85%, pci_dss: 92%, hipaa: 88%, hipaa: 88%}

GET /api/compliance/audit-report
  Query: {framework: "cis", format: "pdf"}
  Returns: Binary PDF report

POST /api/compliance/remediate
  Body: {cluster_id, check_id}
  Returns: {remediation_plan, eta: "2 hours"}
```

### Service Mesh
```
GET /api/clusters/{cluster_id}/service-mesh/policies
  Returns: [{policy_name, source, destination, action}]

POST /api/service-mesh/policies
  Body: {cluster_id, source_ns, dest_ns, allow/deny}
  Returns: {policy_id, status: "created"}
```

### Workload Identity
```
GET /api/workloads/{workload_id}/identity
  Returns: {spiffe_id, svid_status, trust_domain}

POST /api/identity/federate
  Body: {source_cluster, dest_cluster}
  Returns: {federation_status: "established"}
```

---

## MONITORING & OBSERVABILITY

### Prometheus Metrics
```
# K8s Security Metrics
kubernetes_cis_benchmark_compliance (gauge, 0-100)
kubernetes_network_policies_count (gauge)
kubernetes_rbac_violations (counter)
kubernetes_secret_age_days (gauge)
kubernetes_audit_events_total (counter)

# Istio/mTLS Metrics
istio_mtls_connections (gauge)
istio_authorization_denied_total (counter)
istio_certificate_expiry_days (gauge)

# SPIFFE Metrics
spiffe_svid_issued_total (counter)
spiffe_workload_attestations_total (counter)
spiffe_trust_domain_connections (gauge)

# Falco Runtime Metrics
falco_alerts_total (counter, by severity)
falco_detection_latency_ms (histogram)
falco_policy_violations (counter)
```

### Dashboard Visualizations
```
Cluster Health Dashboard:
├─ CIS Benchmark compliance score (per cluster)
├─ mTLS coverage (% of traffic encrypted)
├─ Network policy coverage (% of pods)
├─ RBAC violations (trend over time)
└─ Audit events (real-time feed)

Security Posture Dashboard:
├─ Workload vulnerability distribution
├─ Privilege escalation attempts (last 24h)
├─ Container escapes detected
├─ Unauthorized access attempts
└─ Incident response timeline

Compliance Dashboard:
├─ CIS benchmark (all clusters)
├─ PCI-DSS (payment workloads)
├─ HIPAA (healthcare data)
└─ Evidence collection automation
```

---

## INTEGRATION POINTS

### Cloud Platforms
```
AWS EKS:
├─ VPC networking integration
├─ IAM role binding
├─ CloudWatch logging
└─ AWS Secrets Manager

Google GKE:
├─ VPC networking
├─ GCP IAM
├─ Cloud Logging
└─ Secret Manager

Microsoft AKS:
├─ Azure virtual networks
├─ Azure AD/RBAC
├─ Azure Monitor
└─ Key Vault
```

### External Services
```
Identity:
├─ SPIFFE/SPIRE (workload identity)
├─ HashiCorp Vault (secrets)

Observability:
├─ Prometheus (metrics)
├─ Elasticsearch (logs)
├─ Grafana (dashboards)
├─ Datadog (optional)

Security:
├─ Falco (runtime)
├─ Trivy (image scanning)
├─ OPA/Gatekeeper (policy)

Compliance:
├─ Audit logging
├─ Evidence collection
├─ Report generation
```

---

## PERFORMANCE CHARACTERISTICS

```
Latency Targets:
├─ Policy enforcement: <100ms
├─ Audit event logging: <500ms
├─ Compliance check: <5 seconds/cluster
├─ Dashboard load: <2 seconds
└─ API response: <200ms (p95)

Throughput:
├─ Workloads managed: 10K+
├─ Clusters: 20+
├─ Policies: 1M+
└─ Events/second: 10K+

Scalability:
├─ Concurrent users: 100+
├─ Data retention: 90+ days
└─ Multi-region: Supported
```

---

**Document Version:** 1.0  
**API Endpoints:** 30+  
**Database Tables:** 10+  
**Integration Points:** 15+  
**Cloud Providers:** 3+ (AWS, GCP, Azure)  
**Status:** Complete Architecture & Design
