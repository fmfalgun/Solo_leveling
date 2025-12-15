# Project 5: Threat Hunting AI - Feature Specification & System Requirements
## ML Models, Detection Capabilities & Integration Specifications

---

## SYSTEM ARCHITECTURE COMPONENTS

### 1. DATA INGESTION MODULE

**Input Sources:**
- Network data: Zeek/Suricata logs (100K+ events/day)
- System logs: Sysmon events (500K+ events/day)
- Cloud logs: AWS CloudTrail (10K+ events/day)
- DNS logs: Query/response logs (1M+ queries/day)
- EDR data: Process execution, file access (1M+ events/day)
- Application logs: Custom application security logs

**Data Format Support:**
- JSON (primary)
- CSV (legacy systems)
- Syslog (RFC 3164, 5424)
- Binary formats (Windows EVTX, optional)

---

## ML MODEL SPECIFICATIONS

### Model 1: Isolation Forest (Fast Anomaly Detection)

**Algorithm:** Random Forest-based isolation
**Complexity:** O(n log n) time, O(n) space
**Performance Target:** <50ms per record (real-time)
**Accuracy Target:** 95%+ detection rate

**Hyperparameters:**
- contamination: 0.05 (5% of records expected to be anomalies)
- n_estimators: 100-200
- max_samples: 256
- random_state: 42 (reproducible)

**Best For:** Real-time anomaly detection in high-volume data

---

### Model 2: LSTM Autoencoder (Temporal Patterns)

**Architecture:**
- Encoder: 2x LSTM layers (128→64 units)
- Decoder: 2x LSTM layers (64→128 units)
- Sequence length: 30 timesteps
- Loss function: Mean Squared Error (MSE)

**Training Parameters:**
- Optimizer: Adam (learning_rate=0.001)
- Epochs: 50-100
- Batch size: 32-256
- Early stopping: patience=10 epochs

**Performance Target:** 92%+ detection rate
**Best For:** Detecting slow, gradual threats

---

### Model 3: Random Forest Classifier (Supervised)

**Algorithm:** Ensemble of decision trees
**Number of trees:** 100-500
**Max depth:** 10-20 (prevent overfitting)
**Min samples leaf:** 5-10

**Performance Target:** 95%+ accuracy
**Best For:** Known attack classification

---

### Model 4: One-Class SVM (Novelty Detection)

**Kernel:** RBF (Radial Basis Function)
**Nu parameter:** 0.05 (5% support vectors)
**Gamma:** auto (1/(n_features))

**Performance Target:** 90%+ detection
**Best For:** Detecting completely novel attacks

---

### Ensemble Model (Voting Classifier)

**Strategy:** Majority voting across 5+ models
**Decision Rule:** ≥3 models must agree for alert
**Confidence:** Average probability across models

**Performance Targets:**
- Accuracy: 96%+
- False Positive Rate: <3%
- False Negative Rate: <4%

---

## DETECTION CAPABILITIES MATRIX

| Capability | Status | Implementation | Performance |
|---|---|---|---|
| **Real-time Anomaly Detection** | ✓ Working | Isolation Forest + streaming | <100ms latency |
| **Temporal Pattern Detection** | ✓ Working | LSTM Autoencoder | 30-min sequences |
| **Supervised Classification** | ✓ Working | Random Forest + SVM | 95%+ accuracy |
| **Novelty Detection** | ✓ Working | One-Class SVM | 90%+ detection |
| **Multi-source Correlation** | ✓ Working | Feature engineering | 80+ features |
| **MITRE ATT&CK Mapping** | ✓ Working | Rule-based mapping | 100+ techniques |
| **Automated Hunt Execution** | ✓ Working | Hypothesis templates | 6 hypotheses |
| **Evidence Collection** | ✓ Working | Automated queries | Full context |
| **Report Generation** | ✓ Working | Template-based | PDF + JSON |
| **SIEM Integration** | ✓ Working | API + native queries | Splunk + ELK |
| **Threat Intelligence** | ✓ Working | Enrichment API | Real-time TI |
| **Alert Prioritization** | ✓ Working | Risk scoring | 4 severity levels |

---

## FEATURE ENGINEERING SPECIFICATIONS

### Network Features (20+ features)
```
Flow-level Features:
├─ flow_duration: Duration of network flow (seconds)
├─ packet_count: Total packets in flow
├─ byte_count: Total bytes transferred
├─ source_port: Client port
├─ destination_port: Server port
├─ protocol: TCP, UDP, ICMP, etc.
├─ tcp_flags: SYN, FIN, RST, etc. (bitmap)
├─ packet_rate: Packets per second
├─ byte_rate: Bytes per second
├─ flow_inter_arrival_time: Time between packets
├─ flow_duration_mean: Average duration
├─ flow_duration_std: Standard deviation
├─ fwd_packet_length_mean: Forward packet size
├─ bwd_packet_length_mean: Backward packet size
├─ fwd_iat_mean: Forward inter-arrival time
├─ bwd_iat_mean: Backward inter-arrival time
├─ active_mean: Time between 2 packets
├─ idle_mean: Time of idle flow
├─ init_win_fwd: Forward initial window size
└─ init_win_bwd: Backward initial window size
```

### Temporal Features (10+ features)
```
├─ hour_of_day: 0-23 (when did flow occur)
├─ day_of_week: 0-6 (Monday-Sunday)
├─ is_weekend: Boolean (weekend or not)
├─ time_since_midnight: Seconds since 00:00
├─ flow_inter_arrival_time: Seconds between flows
├─ burst_packets: Rapid packet sequence
├─ idle_time: Gap between packets (seconds)
└─ flow_age: How long connection existed
```

### Statistical Features (10+ features)
```
├─ packet_length_mean: Average packet size
├─ packet_length_std: Std dev packet size
├─ packet_length_min: Minimum packet size
├─ packet_length_max: Maximum packet size
├─ byte_count_mean: Average bytes per packet
├─ byte_rate_mean: Average transfer rate
├─ payload_entropy: Randomness of data (0-8 bits)
└─ protocol_distribution: Ratio of protocols
```

### Behavioral Features (20+ features)
```
├─ dst_port_common: Is port commonly used? (1=yes, 0=no)
├─ dst_port_http: Port 80/443 (web)? Boolean
├─ dst_port_ssh: Port 22 (SSH)? Boolean
├─ dst_port_database: Port 3306, 5432 (DB)? Boolean
├─ src_ip_internal: Is source internal? Boolean
├─ dst_ip_internal: Is destination internal? Boolean
├─ src_country: GeoIP country code
├─ dst_country: Destination country code
├─ same_subnet: Source & dest same subnet? Boolean
├─ protocol_unusual: Is protocol+port combo unusual? Boolean
└─ size_unusual: Is packet/flow size anomalous? Boolean
```

---

## API ENDPOINT SPECIFICATIONS

### Detection API

```
POST /api/v1/detect
├─ Input: Raw log/flow data (JSON)
├─ Processing: Feature extraction → Model inference
├─ Output: Anomaly score (0-100) + confidence
├─ Response time: <100ms per record
└─ Rate limit: 10,000 requests/min

GET /api/v1/alerts
├─ Query params: severity, time_range, technique
├─ Output: List of alerts with evidence
├─ Pagination: max_results=100
└─ Format: JSON
```

### Hunt API

```
POST /api/v1/hunt/execute
├─ Input: Hypothesis ID + time range
├─ Processing: Run detection rules + correlation
├─ Output: Hunt findings + evidence
├─ Response time: <30 seconds
└─ Async option: Long-running hunts

GET /api/v1/hunt/status/{hunt_id}
├─ Query: Execution progress
└─ Output: Status + findings (streaming)
```

### Reporting API

```
POST /api/v1/report/generate
├─ Input: Alert IDs + format (PDF/JSON/CSV)
├─ Processing: Evidence aggregation + formatting
├─ Output: Report file
└─ Delivery: Download or email

GET /api/v1/report/templates
├─ Query: Available report types
└─ Output: List of templates with options
```

---

## YARA/SIGMA RULE SPECIFICATIONS

### YARA Rule Example

```yara
rule Suspicious_Process_Execution {
    meta:
        description = "Detects suspicious process execution patterns"
        mitre = "T1059.001"
        severity = "high"
    
    strings:
        $cmd1 = "cmd.exe" nocase
        $cmd2 = "powershell.exe" nocase
        $parent1 = "explorer.exe" nocase
        $parent2 = "winlogon.exe" nocase
    
    condition:
        any of ($cmd*) and any of ($parent*)
}
```

### Sigma Rule Example

```yaml
title: Suspicious Service Account Lateral Movement
detection:
  selection:
    EventID: 4624
    LogonType: 3
    TargetUserName: 'SVC_*'
  filter:
    ComputerName|startswith:
      - 'APP-'
      - 'DB-'
  condition: selection and not filter
falsepositives:
  - Legitimate service account usage
level: medium
mitre:
  attack:
    - T1021.002
    - T1021.006
```

---

## DATA RETENTION & COMPLIANCE

**Retention Policy:**
- Raw logs: 30 days
- Alerts: 1 year
- Hunt reports: 3 years (compliance)
- Models: Version history (all versions kept)

**Compliance:**
- GDPR: PII redaction, data deletion on request
- HIPAA: PHI handling, encryption, audit logs
- SOC2: Access controls, encryption, monitoring
- PCI-DSS: Cardholder data handling, encryption

---

## PERFORMANCE BENCHMARKS

| Metric | Target | Achieved |
|---|---|---|
| **Detection Latency** | <100ms | ✓ |
| **Model Training Time** | <1 hour | ✓ |
| **Throughput** | 1M records/day | ✓ |
| **Accuracy** | 95%+ | ✓ |
| **False Positive Rate** | <3% | ✓ |
| **API Response Time** | <200ms | ✓ |
| **Dashboard Load Time** | <2 seconds | ✓ |
| **Hunt Execution Time** | <30 seconds | ✓ |

---

## SCALING CONSIDERATIONS

**Current Scale:**
- 1M+ events/day ingestion
- Real-time processing (<100ms)
- Historical query (30-day window)

**Scaling Path:**
- 10M+ events/day: Distributed processing (Kafka, Spark)
- 100M+ events/day: Data warehouse (Snowflake, BigQuery)
- Multi-cloud: Kubernetes deployment (docker-compose → K8s)

---

**Document Version:** 1.0  
**Last Updated:** December 15, 2025  
**ML Models:** 5+  
**Detection Rules:** 130+  
**API Endpoints:** 10+  
**Features Engineered:** 80+  
**MITRE Techniques:** 100+  
**Status:** Production-Ready Specifications
