# Project 6: OT/ICS Security - Implementation Plan, Compliance Mapping & Checklists
## 14-Week Execution Plan with IEC 62443, NIST CSF & NERC CIP Alignment

---

## PHASE-LEVEL BREAKDOWN (14 weeks, 360-480 hours)

### PHASE 1: OT PROTOCOL ANALYSIS (Weeks 1-4, 160 hours)

**Week 1: Protocol Research & Wireshark Integration (40 hours)**
```
MONDAY-TUESDAY: Modbus Deep-Dive
├─ Read RFC 1006 (TCP/IP binding for Modbus)
├─ Analyze Modbus TCP frame structure
├─ Develop Wireshark dissector for Modbus
├─ Test with sample PCAP files
├─ Implement function code parsing (FC 01-16)

WEDNESDAY: Profibus Protocol Analysis
├─ Study Profibus-DP architecture (RS-485 physical layer)
├─ Research token ring mechanism
├─ Analyze device discovery & configuration
├─ Plan detection strategies

THURSDAY: DNP3 & OPC-UA
├─ Study DNP3 frame structure (critical for power grids)
├─ Research DNP3 function codes (read/write)
├─ Analyze OPC-UA (modern industrial protocol)
├─ Compare security models (none vs optional)

FRIDAY: Tool Development
├─ Create protocol parser library (Python)
├─ Implement packet dissector
├─ Test with 50+ sample packets
└─ Document implementation
```

**Week 2: Vulnerability Scanner Development (40 hours)**
- [ ] Default credential scanner (telnet, SSH, HTTP)
- [ ] Weak encryption detector
- [ ] Protocol-level fuzzing engine
- [ ] CVE database integration (NVD + OT-specific)
- [ ] Test against 50+ CVE samples

**Week 3: Network Discovery & Topology Mapping (40 hours)**
- [ ] SNMP device enumeration
- [ ] Shodan API integration (find public-facing systems)
- [ ] Web UI scanning (HMI interfaces)
- [ ] Port scanning (OT-specific ports: 502 Modbus, 20000 DNP3)
- [ ] Topology visualization

**Week 4: Risk Assessment Engine (40 hours)**
- [ ] CVSS v3.1 scoring implementation
- [ ] IEC 62443 risk model
- [ ] FAIR (Factor Analysis of Information Risk)
- [ ] Business impact assessment
- [ ] Critical asset identification

---

## COMPLIANCE MAPPING FRAMEWORK

### IEC 62443 COMPLIANCE MATRIX

```
IEC 62443 INDUSTRIAL AUTOMATION & CONTROL SYSTEMS SECURITY
═══════════════════════════════════════════════════════════════════════════════

IEC 62443-1-1: VOCABULARY & CONCEPTS
├─ Asset: Equipment, software, systems in OT environment
├─ Vulnerability: Weakness exploitable by attacker
├─ Security Level (SL): 0-4 (0=no protection, 4=maximum protection)
└─ Zone: Group of systems with similar security requirements

IEC 62443-3-3: SYSTEM SECURITY REQUIREMENTS
├─ 22 General Requirements (SR-1 to SR-22)
├─ 3 Asset Protection Requirements
├─ 6 System Development Requirements
├─ 7 System Monitoring & Response Requirements
└─ 6 Additional Planning & Response Requirements

SECURITY REQUIREMENTS MAPPING:

SR-1: IDENTIFICATION & AUTHENTICATION
├─ Requirement: All users must be uniquely identified
├─ Assessment:
│  ├─ Can you identify individual user actions? (yes/no)
│  ├─ Do default accounts exist? (yes/no → critical)
│  └─ Is MFA implemented? (yes/no → important)
├─ Current State: [ ] COMPLIANT [ ] NON-COMPLIANT [ ] PARTIAL
└─ Remediation Plan: __________________

SR-2: USE CONTROL
├─ Requirement: Limit user actions based on role
├─ Assessment:
│  ├─ Is RBAC implemented? (yes/no)
│  ├─ Can operators modify system parameters? (should be NO)
│  └─ Are maintenance accounts isolated? (yes/no)
├─ Current State: [ ] COMPLIANT [ ] NON-COMPLIANT [ ] PARTIAL
└─ Remediation Plan: __________________

SR-3: SYSTEM INTEGRITY
├─ Requirement: Detect unauthorized changes to systems
├─ Assessment:
│  ├─ Is firmware signature verification enabled? (yes/no)
│  ├─ Are configuration files protected? (yes/no)
│  └─ Is file integrity monitoring in place? (yes/no)
├─ Current State: [ ] COMPLIANT [ ] NON-COMPLIANT [ ] PARTIAL
└─ Remediation Plan: __________________

SR-4: INFORMATION CONFIDENTIALITY
├─ Requirement: Protect sensitive information from disclosure
├─ Assessment:
│  ├─ Is Modbus traffic encrypted? (currently NO - critical)
│  ├─ Are passwords transmitted securely? (SSH vs Telnet)
│  └─ Is sensitive data logged securely? (yes/no)
├─ Current State: [ ] COMPLIANT [ ] NON-COMPLIANT [ ] PARTIAL
└─ Remediation Plan: __________________

SR-5: RESTRICT DATA FLOW
├─ Requirement: Limit data flow to intended destinations
├─ Assessment:
│  ├─ Are firewalls enforcing data flow policies? (yes/no)
│  ├─ Is network segmentation present? (yes/no)
│  └─ Are egress filters in place? (yes/no)
├─ Current State: [ ] COMPLIANT [ ] NON-COMPLIANT [ ] PARTIAL
└─ Remediation Plan: __________________

SR-6: TIMELY RESPONSE TO EVENTS
├─ Requirement: Detect and respond to security events
├─ Assessment:
│  ├─ Is logging enabled? (yes/no)
│  ├─ Are security events detected in real-time? (yes/no)
│  └─ Is incident response plan documented? (yes/no)
├─ Current State: [ ] COMPLIANT [ ] NON-COMPLIANT [ ] PARTIAL
└─ Remediation Plan: __________________

(Additional 16+ Security Requirements follow similar structure)
```

### NIST CSF MAPPING FOR OT SYSTEMS

```
NIST CYBERSECURITY FRAMEWORK (Adapted for OT)
═══════════════════════════════════════════════════════════════════════════════

FUNCTION 1: IDENTIFY (Asset Discovery & Management)
├─ Asset Inventory:
│  ├─ [ ] All SCADA systems documented
│  ├─ [ ] All PLC/RTU systems inventoried
│  ├─ [ ] Hardware specifications recorded
│  └─ [ ] Firmware versions tracked
│
├─ Risk Assessment:
│  ├─ [ ] Critical assets identified (safety-related)
│  ├─ [ ] Data flow diagrams created
│  ├─ [ ] Threat scenarios documented
│  └─ [ ] Business impact assessed (downtime cost)
│
└─ Governance:
   ├─ [ ] Security policy for OT documented
   ├─ [ ] Roles & responsibilities assigned
   └─ [ ] Change management process in place

FUNCTION 2: PROTECT (Access Control & Hardening)
├─ Access Control:
│  ├─ [ ] Authentication mechanisms (strong passwords)
│  ├─ [ ] MFA for remote access
│  ├─ [ ] Default credentials removed
│  └─ [ ] Least privilege principle enforced
│
├─ Network Security:
│  ├─ [ ] Firewall rules configured
│  ├─ [ ] Network segmentation (IT/OT boundary)
│  ├─ [ ] VPN for remote access
│  └─ [ ] Network monitoring (IDS/IPS)
│
└─ Data Security:
   ├─ [ ] Encryption in transit (TLS 1.2+)
   ├─ [ ] Encryption at rest (for databases)
   ├─ [ ] Key management (rotation, storage)
   └─ [ ] Data classification (what's critical?)

FUNCTION 3: DETECT (Monitoring & Alerting)
├─ Anomaly Detection:
│  ├─ [ ] Baseline behavior established
│  ├─ [ ] Monitoring tools deployed
│  ├─ [ ] Alerting rules configured
│  └─ [ ] False positive tuning completed
│
├─ Logging:
│  ├─ [ ] Security events logged
│  ├─ [ ] Logs centralized (syslog server)
│  ├─ [ ] Log retention policy (90+ days)
│  └─ [ ] Log integrity protected
│
└─ Event Analysis:
   ├─ [ ] Security Information & Event Management (SIEM)
   ├─ [ ] Threat intelligence integrated
   └─ [ ] Alerts reviewed 24/7

FUNCTION 4: RESPOND (Incident Handling)
├─ Response Planning:
│  ├─ [ ] Incident response plan documented
│  ├─ [ ] Contact list maintained
│  ├─ [ ] Escalation procedures defined
│  └─ [ ] Legal considerations addressed
│
├─ Response Execution:
│  ├─ [ ] Incidents detected and reported
│  ├─ [ ] Containment procedures executed
│  ├─ [ ] Evidence preservation
│  └─ [ ] Communication with stakeholders
│
└─ Post-Incident:
   ├─ [ ] Root cause analysis
   ├─ [ ] Lessons learned documented
   └─ [ ] Preventive improvements implemented

FUNCTION 5: RECOVER (Restoration & Business Continuity)
├─ Recovery Planning:
│  ├─ [ ] Disaster recovery plan documented
│  ├─ [ ] Backup systems verified
│  ├─ [ ] Recovery time objectives (RTO) defined
│  └─ [ ] Recovery point objectives (RPO) defined
│
├─ Recovery Execution:
│  ├─ [ ] Backup systems operational
│  ├─ [ ] Data restoration tested
│  ├─ [ ] System restoration procedures
│  └─ [ ] Communications restored
│
└─ Recovery Testing:
   ├─ [ ] Disaster recovery drills conducted
   ├─ [ ] Restoration times validated
   └─ [ ] Lessons learned incorporated
```

### NERC CIP COMPLIANCE (For Power Grid Systems)

```
NERC CIP (NORTH AMERICAN ELECTRIC RELIABILITY CORPORATION)
═══════════════════════════════════════════════════════════════════════════════

Applicability: Bulk Electric System (BES) protecting power grid
Standards: CIP-002 through CIP-014

CIP-002: ASSET IDENTIFICATION & CATEGORIZATION
├─ [ ] All BES Cyber Systems identified
├─ [ ] Categorized as Critical (if affecting BES)
└─ [ ] Documentation maintained

CIP-003: SECURITY PLAN
├─ [ ] Security program documented
├─ [ ] Personnel training requirements defined
├─ [ ] Vendor management procedures
└─ [ ] Enforcement mechanisms in place

CIP-004: PERSONNEL & TRAINING
├─ [ ] Background checks completed
├─ [ ] Security training provided
├─ [ ] Access control roles defined
└─ [ ] Authorization documented

CIP-005: SYSTEM SECURITY PERIMETER
├─ [ ] Secure perimeter defined
├─ [ ] Physical security controls
├─ [ ] Electronic security controls
└─ [ ] Boundary protection devices

CIP-007: SYSTEM SECURITY MANAGEMENT
├─ [ ] Ports & services identified & documented
├─ [ ] Security patches applied timely
├─ [ ] Malware protection implemented
├─ [ ] Antivirus software current
└─ [ ] System hardening baseline

CIP-009: RECOVERY & RESTORATION
├─ [ ] Backup systems documented
├─ [ ] Recovery plan prepared
├─ [ ] Offsite backups maintained
└─ [ ] Recovery testing documented

(CIP-010 through CIP-014 follow similar pattern)
```

---

## ASSESSMENT CHECKLIST (200+ Items)

### PHASE A: RECONNAISSANCE & DISCOVERY

**Asset Identification**
- [ ] SCADA servers documented (count: ___)
- [ ] DCS controllers listed (count: ___)
- [ ] PLC devices enumerated (count: ___)
- [ ] RTU remote terminal units (count: ___)
- [ ] HMI/SCADA workstations (count: ___)
- [ ] Historian/database servers (count: ___)
- [ ] Engineering workstations (count: ___)
- [ ] Network infrastructure (switches, firewalls, routers)

**Network Topology**
- [ ] Network diagram created
- [ ] Network segments identified
- [ ] IP address ranges documented
- [ ] VLAN configuration mapped
- [ ] Firewall rules extracted
- [ ] Physical connections documented

**Operational Parameters**
- [ ] Process flow documented
- [ ] Critical setpoints identified
- [ ] Safety interlocks documented
- [ ] Backup systems identified
- [ ] Operational windows defined (when assessment allowed)

### PHASE B: VULNERABILITY ASSESSMENT

**Authentication Testing**
- [ ] Default credentials attempted (Telnet, SSH, HTTP)
  - [ ] Siemens SCADA: admin/admin → FAILED/PASSED
  - [ ] GE systems: GE/GE123 → FAILED/PASSED
  - [ ] Honeywell HAS: hv/hv → FAILED/PASSED
  - [ ] Generic: common/common → FAILED/PASSED
- [ ] Weak password policy tested
- [ ] MFA implementation verified
- [ ] Service account audit completed
- [ ] Privilege escalation tested

**Network Segmentation**
- [ ] IT network isolated from OT
- [ ] DMZ present between IT/OT
- [ ] Firewall rules enforced (IT→OT blocked)
- [ ] VLAN routing disabled (if not needed)
- [ ] Intra-OT segmentation checked
- [ ] Remote access controls tested

**Encryption & Integrity**
- [ ] Modbus traffic encrypted (encryption: ___ or NONE)
- [ ] SSH vs Telnet usage (SSH: _% / Telnet: _%)
- [ ] VPN for remote access (configured: yes/no)
- [ ] Certificate validation (TLS, SSL) tested
- [ ] Data integrity mechanisms verified
- [ ] Cryptographic algorithms reviewed (AES? DES? RC4?)

**Patch Management**
- [ ] Firmware versions documented (see table below)
  | System Type | System Name | Firmware Version | Latest Version | Patch Status |
  |---|---|---|---|---|
  | SCADA | System-1 | v5.2.1 | v8.0.1 | OUTDATED |
  | DCS | Honeywell-ABC | v2.1.0 | v3.5.2 | CRITICAL |
  | PLC | Siemens-300 | v4.5.0 | v4.9.1 | PATCH AVAILABLE |
  
- [ ] Known CVEs identified per system
- [ ] Patch availability checked (vendor status)
- [ ] Patch testing scheduled (production impact)

**Logging & Monitoring**
- [ ] Audit logging enabled
- [ ] Security events logged (failed logins, configuration changes)
- [ ] Log retention period (days: ___)
- [ ] Log storage location (local/remote/both)
- [ ] Log protection from deletion
- [ ] Real-time monitoring tool (SIEM: _____)
- [ ] Alerting configured (thresholds set)

### PHASE C: COMPLIANCE VERIFICATION

**IEC 62443 Requirements (22 SRs)**
- [ ] SR-1: Identification & Authentication - Status: ☐ FULL ☐ PARTIAL ☐ NONE
- [ ] SR-2: Use Control - Status: ☐ FULL ☐ PARTIAL ☐ NONE
- [ ] SR-3: System Integrity - Status: ☐ FULL ☐ PARTIAL ☐ NONE
- [ ] SR-4: Information Confidentiality - Status: ☐ FULL ☐ PARTIAL ☐ NONE
- [ ] SR-5: Restrict Data Flow - Status: ☐ FULL ☐ PARTIAL ☐ NONE
- [ ] SR-6: Timely Response to Events - Status: ☐ FULL ☐ PARTIAL ☐ NONE
- [ ] (SR-7 through SR-22 follow similar pattern)

**NIST CSF Functions**
- [ ] IDENTIFY: ___% complete
- [ ] PROTECT: ___% complete
- [ ] DETECT: ___% complete
- [ ] RESPOND: ___% complete
- [ ] RECOVER: ___% complete

**NERC CIP (if applicable)**
- [ ] CIP-002: Asset Identification - ☐ COMPLIANT ☐ NON-COMPLIANT
- [ ] CIP-003: Security Plan - ☐ COMPLIANT ☐ NON-COMPLIANT
- [ ] CIP-004: Personnel Training - ☐ COMPLIANT ☐ NON-COMPLIANT
- [ ] (CIP-005 through CIP-014 follow similar pattern)

---

## RISK REGISTER TEMPLATE

```
RISK REGISTER - OT/ICS ASSESSMENT
═══════════════════════════════════════════════════════════════════════════════

| ID | Finding | Severity | Likelihood | Risk Score | Remediation | Timeline |
|---|---|---|---|---|---|---|
| 1 | Default Modbus credentials | CRITICAL | HIGH | 45 | Change to strong password | Immediate |
| 2 | No network segmentation (IT/OT) | CRITICAL | MEDIUM | 40 | Deploy firewall DMZ | 30 days |
| 3 | Firmware v5.2 (CVE-2020-XXXX exists) | HIGH | HIGH | 30 | Update to v8.0 | 60 days |
| 4 | No audit logging | HIGH | MEDIUM | 25 | Enable Windows audit | 14 days |
| 5 | Telnet enabled on SCADA server | HIGH | MEDIUM | 25 | Disable Telnet, use SSH | 7 days |
| 6 | Weak password policy | MEDIUM | HIGH | 20 | Enforce 12+ char, special chars | 30 days |
```

---

**Document Version:** 1.0  
**Total Checklist Items:** 200+  
**Compliance Frameworks Covered:** 3 (IEC 62443, NIST CSF, NERC CIP)  
**Assessment Duration:** 2-3 weeks per facility
