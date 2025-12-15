# Project 8: Endpoint Security - Architecture, Database & API Specifications
## System Design, Data Models & Integration Points

---

## SYSTEM ARCHITECTURE

```
LAYERED ENDPOINT SECURITY ARCHITECTURE
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                           │
│  ├─ Executive Dashboard                                         │
│  ├─ Admin Portal                                                │
│  ├─ API Documentation                                           │
│  └─ Compliance Reports                                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              APPLICATION LAYER (REST API)                       │
│  ├─ Endpoint Discovery API                                      │
│  ├─ Vulnerability Assessment API                               │
│  ├─ Patch Management API                                        │
│  ├─ Compliance Checking API                                     │
│  └─ Incident Response API                                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│            BUSINESS LOGIC LAYER (Engines)                       │
│  ├─ Vulnerability Scanner Engine                               │
│  ├─ Risk Scoring Engine                                        │
│  ├─ Patch Orchestrator                                         │
│  ├─ Compliance Checker                                         │
│  └─ Incident Response Engine                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          INTEGRATION LAYER (EDR/EPP Connectors)                 │
│  ├─ Crowdstrike Falcon Connector                               │
│  ├─ Microsoft Defender Connector                               │
│  ├─ Sophos Connector                                           │
│  ├─ SentinelOne Connector                                      │
│  └─ Generic EDR/EPP Interface                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                    │
│  ├─ PostgreSQL (Relational)                                     │
│  ├─ Elasticsearch (Search & Analytics)                          │
│  ├─ Redis (Caching)                                             │
│  └─ S3/Blob Storage (Patch files, logs)                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## DATABASE SCHEMA

### PostgreSQL Tables

```sql
-- Endpoints table
CREATE TABLE endpoints (
    id UUID PRIMARY KEY,
    hostname VARCHAR(255) UNIQUE NOT NULL,
    device_id VARCHAR(255),  -- EDR device ID
    os_type VARCHAR(50),  -- Windows, macOS, Linux
    os_version VARCHAR(50),
    ip_address INET,
    mac_address MACADDR,
    last_seen TIMESTAMP,
    agent_version VARCHAR(50),  -- EDR agent version
    status ENUM('healthy', 'at_risk', 'critical'),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Vulnerabilities table
CREATE TABLE vulnerabilities (
    id UUID PRIMARY KEY,
    cve_id VARCHAR(20) UNIQUE,  -- CVE-XXXX-XXXXX
    title VARCHAR(500),
    description TEXT,
    cvss_score FLOAT,  -- 0.0-10.0
    severity ENUM('critical', 'high', 'medium', 'low'),
    exploitability VARCHAR(50),  -- functional, proof-of-concept, unproven
    affected_systems JSONB,  -- OSes, software versions
    remediation TEXT,
    source VARCHAR(100),  -- NVD, VulnDB, vendor
    published_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Endpoint vulnerabilities (many-to-many)
CREATE TABLE endpoint_vulnerabilities (
    endpoint_id UUID REFERENCES endpoints(id),
    vulnerability_id UUID REFERENCES vulnerabilities(id),
    risk_score FLOAT,  -- Combined risk (CVSS + context)
    detected_at TIMESTAMP,
    remediated_at TIMESTAMP,
    status ENUM('open', 'in_progress', 'remediated', 'exception'),
    PRIMARY KEY (endpoint_id, vulnerability_id)
);

-- Software inventory
CREATE TABLE software_installed (
    id UUID PRIMARY KEY,
    endpoint_id UUID REFERENCES endpoints(id),
    name VARCHAR(255),
    version VARCHAR(50),
    vendor VARCHAR(255),
    install_date DATE,
    last_execution TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Patches table
CREATE TABLE patches (
    id UUID PRIMARY KEY,
    kb_number VARCHAR(50),  -- Windows: KB###, others: vendor ID
    title VARCHAR(500),
    description TEXT,
    severity ENUM('critical', 'high', 'medium', 'low'),
    released_date DATE,
    reboot_required BOOLEAN,
    estimated_size_mb INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Patch deployments
CREATE TABLE patch_deployments (
    id UUID PRIMARY KEY,
    patch_id UUID REFERENCES patches(id),
    endpoint_id UUID REFERENCES endpoints(id),
    status ENUM('pending', 'staging', 'deployed', 'failed', 'rolled_back'),
    deployment_date TIMESTAMP,
    completion_date TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Compliance audits
CREATE TABLE compliance_audits (
    id UUID PRIMARY KEY,
    endpoint_id UUID REFERENCES endpoints(id),
    framework VARCHAR(50),  -- CIS, NIST, PCI-DSS, HIPAA, SOC2
    check_name VARCHAR(255),
    compliance_status BOOLEAN,
    evidence TEXT,
    remediation TEXT,
    audit_date TIMESTAMP,
    next_audit TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Incidents
CREATE TABLE incidents (
    id UUID PRIMARY KEY,
    endpoint_id UUID REFERENCES endpoints(id),
    threat_type VARCHAR(100),  -- ransomware, malware, exfiltration, etc.
    severity ENUM('critical', 'high', 'medium', 'low'),
    status ENUM('open', 'investigating', 'contained', 'resolved'),
    detected_at TIMESTAMP,
    contained_at TIMESTAMP,
    resolved_at TIMESTAMP,
    root_cause TEXT,
    response_actions JSONB,  -- Array of actions taken
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## API ENDPOINTS

### Endpoint Management

```
GET /api/endpoints
  Returns: [{id, hostname, os_type, status, risk_score}]
  
GET /api/endpoints/{endpoint_id}
  Returns: Detailed endpoint information + vulnerabilities + compliance status
  
POST /api/endpoints/scan
  Body: {endpoint_ids: [list]}
  Returns: {task_id, status: "scanning"}
  
GET /api/endpoints/{endpoint_id}/vulnerabilities
  Returns: [{cve_id, title, risk_score, status}]
```

### Vulnerability Management

```
GET /api/vulnerabilities
  Query: {severity, affected_systems, limit}
  Returns: [{cve_id, title, cvss_score, endpoints_affected}]
  
POST /api/vulnerabilities/scan
  Body: {endpoint_id}
  Returns: {task_id, scan_time_estimate: "2 minutes"}
  
GET /api/vulnerabilities/{cve_id}/endpoints
  Returns: [endpoints affected by vulnerability]
```

### Patch Management

```
GET /api/patches/available
  Returns: [{kb_number, title, severity, released_date}]
  
POST /api/patches/deploy
  Body: {patch_id, endpoint_ids, strategy: "staged"}
  Returns: {deployment_id, status: "pending"}
  
GET /api/patches/{deployment_id}/status
  Returns: {status, success_rate, failed_endpoints}
```

### Compliance

```
GET /api/compliance/status
  Returns: {cis: 85%, nist: 78%, pci_dss: 92%, hipaa: 88%}
  
GET /api/compliance/audit/{framework}
  Returns: [compliance checks + status]
  
POST /api/compliance/remediate
  Body: {endpoint_id, check_id}
  Returns: {remediation_plan, estimated_time}
```

### Incident Response

```
GET /api/incidents
  Returns: [{id, threat_type, severity, status, detected_at}]
  
POST /api/incidents/respond
  Body: {endpoint_id, response_type: "isolate"}
  Returns: {action_id, status: "executing"}
  
GET /api/incidents/{incident_id}/timeline
  Returns: Chronological timeline of detection + response
```

---

## INTEGRATION POINTS

```
EXTERNAL INTEGRATIONS (10+)
═══════════════════════════════════════════════════════════════════════════════

EDR/EPP Platforms:
├─ Crowdstrike Falcon API
├─ Microsoft Defender API
├─ Sophos API
└─ SentinelOne API

Vulnerability Databases:
├─ NVD (National Vulnerability Database)
├─ VulnDB
├─ Exploit-DB
└─ Vendor advisories (Microsoft, Apple, etc.)

Identity & Access:
├─ Active Directory/LDAP
├─ Okta
├─ Azure AD
└─ SSO (SAML, OIDC)

Ticketing & ITSM:
├─ Jira
├─ ServiceNow
├─ Zendesk
└─ Linear

Communication:
├─ Slack/Teams webhooks
├─ PagerDuty
├─ Opsgenie
└─ Email

Cloud Storage:
├─ AWS S3 (patch files)
├─ Azure Blob Storage
└─ GCP Cloud Storage
```

---

## PERFORMANCE CHARACTERISTICS

```
Performance Targets (Benchmarks)
═══════════════════════════════════════════════════════════════════════════════

Operation                          Target Latency    Throughput
─────────────────────────────────────────────────────────────────
Endpoint discovery (1000 hosts)    <2 seconds        1000/sec
Vulnerability scan (per endpoint)  <10 seconds       100/sec
Risk scoring calculation           <100ms            10K/sec
Patch deployment status check      <500ms            1000/sec
Compliance audit (per endpoint)    <5 seconds        200/sec
Dashboard load time                <2 seconds        50 concurrent users

Scalability:
├─ Endpoints: 100K+ supported
├─ Vulnerabilities: 1M+ in database
├─ Patches: 100K+ stored
├─ Concurrent API users: 50+
└─ Data retention: 90+ days
```

---

**Document Version:** 1.0  
**Database:** PostgreSQL + Elasticsearch + Redis  
**API Endpoints:** 20+ (fully documented)  
**Integration Points:** 15+  
**Performance:** Sub-second latency (with caching)  
**Scalability:** 100K+ endpoints supported
