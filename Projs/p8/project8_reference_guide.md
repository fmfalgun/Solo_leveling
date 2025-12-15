# Project 8: Endpoint Security - Complete Reference Guide & Best Practices
## EDR/EPP Standards, Tools, Compliance Frameworks & Learning Resources

---

## SECTION 1: EDR/EPP STANDARDS & FRAMEWORKS

### EDR (Endpoint Detection & Response)

**Key Capabilities:**
- Real-time endpoint monitoring (process, network, file activity)
- Threat detection using behavioral analysis
- Incident investigation & forensics
- Threat hunting capabilities
- Auto-remediation of threats

**Leading Platforms:**
- Crowdstrike Falcon ($50-$300/endpoint/year)
- Microsoft Defender for Endpoint (part of Microsoft 365)
- Sophos Intercept X ($3-$15/endpoint/month)
- SentinelOne ($15-$50/endpoint/month)
- CrowdStrike, Carbon Black, McAfee, F-Secure

---

### EPP (Endpoint Protection Platform)

**Key Capabilities:**
- Antivirus & antimalware
- Exploit prevention
- Application whitelisting
- Firewall management
- USB/device control

**Leading Platforms:**
- Microsoft Defender Antivirus (built-in Windows)
- Kaspersky
- Norton
- McAfee
- Bitdefender

---

### NIST Cybersecurity Framework (CSF) - Endpoint Focus

```
IDENTIFY:
├─ Endpoint inventory (hardware, software, OS versions)
├─ Data classification (what data on endpoints?)
└─ Access control inventory

PROTECT:
├─ EDR/EPP deployment
├─ Patch management (automated)
├─ Disk encryption
├─ MFA/authentication
└─ Access controls

DETECT:
├─ EDR monitoring (24/7)
├─ Log aggregation & analysis
├─ Threat hunting
└─ Anomaly detection

RESPOND:
├─ Incident response plan
├─ Containment procedures
├─ Investigation tools
└─ Communication protocols

RECOVER:
├─ Backup & restore procedures
├─ System hardening after incident
├─ Root cause analysis
└─ Lessons learned
```

---

## SECTION 2: COMPLIANCE FRAMEWORKS FOR ENDPOINTS

### CIS Controls v8

**Critical Controls for Endpoints:**
1. Asset Management
2. Software Asset Management
3. Data Protection
4. Secure Configuration Management
5. Access Control Management
6. Logging and Monitoring
7. Email and Web Browser Protections
8. Malware Defenses

**CIS Benchmarks:**
- Windows: 200+ checks per version
- macOS: 100+ checks per version
- Linux: 80+ checks per flavor

---

### PCI-DSS (Payment Card Industry)

**Endpoint Requirements:**
- Antivirus software (requirement 5)
- Secure configuration (requirement 2)
- Log monitoring (requirement 10)
- Access control (requirement 7)
- Security patches (requirement 6.2)

---

### HIPAA (Healthcare)

**Endpoint Security Controls:**
- Access control (passwords, MFA, RBAC)
- Encryption (disk + transmission)
- Audit controls (logging all access)
- Integrity controls (prevent data modification)
- Transmission security (TLS 1.2+)

---

### GDPR (EU Data Protection)

**Endpoint Implications:**
- Data minimization (don't store unnecessary data)
- Encryption (protect PII on endpoints)
- Access logging (audit trail)
- Right to be forgotten (delete data)
- Breach notification (72 hours)

---

## SECTION 3: TOOLS & TECHNOLOGIES

### Endpoint Discovery Tools

```
LDAP/AD Scanning:
├─ PowerShell (native Windows)
├─ ldapsearch (Linux/Unix)
└─ ldapcmd (cross-platform)

Network Discovery:
├─ nmap (port scanning)
├─ arp-scan (ARP enumeration)
└─ Shodan (public-facing systems)

Cloud Enumeration:
├─ AWS Systems Manager (EC2 discovery)
├─ Azure Resource Graph (VM inventory)
└─ GCP Cloud Asset Inventory
```

### Vulnerability Scanning Tools

```
OS Vulnerability:
├─ Nessus Professional ($2,590/year)
├─ OpenVAS (free/open-source)
├─ Qualys VMDR ($10K+/year)
└─ Rapid7 InsightVM

Application Scanning:
├─ Dependabot (GitHub)
├─ Snyk (SCA)
└─ Black Duck (code scanning)
```

### Patch Management Tools

```
Built-in Solutions:
├─ Windows Update for Business
├─ Apple Software Update
├─ Unattended-upgrades (Linux)

Third-party Solutions:
├─ WSUS (Windows Server Update Services)
├─ Jamf Pro (Apple)
├─ Puppet/Ansible (Linux)
├─ Ivanti (commercial)
```

### EDR/EPP Integrations

```
Webhooks & APIs:
├─ Crowdstrike Falcon API
├─ Microsoft Defender API
├─ Sophos Central API
└─ SentinelOne API

SIEM Integration:
├─ Splunk (log ingestion)
├─ ELK Stack (open-source)
├─ Datadog (cloud-native)
└─ LogicMonitor
```

---

## SECTION 4: BEST PRACTICES

### Patch Management

```
Best Practices:
├─ Automatic patch deployment (with staging first)
├─ Schedule patches during maintenance windows
├─ Prioritize by severity (critical first)
├─ Verify compliance post-patch
├─ Maintain rollback procedures
└─ Document patch history

Patch Cycle Target:
├─ Critical patches: 7-14 days to deploy
├─ High patches: 30 days
├─ Medium patches: 60-90 days
└─ Low patches: As convenient
```

### EDR Configuration

```
Best Practices:
├─ Enable all behavioral sensors (process, network, file)
├─ Configure threat hunting rules (YARA, sigma rules)
├─ Set up real-time alerts (critical severity)
├─ Enable auto-remediation (common threats)
├─ Establish baseline behavior (first 2-4 weeks)
└─ Regular threat hunting campaigns
```

### Compliance Verification

```
Best Practices:
├─ Continuous compliance monitoring (daily)
├─ Automated remediation for common issues
├─ Exception management with approval workflow
├─ Regular audits (quarterly minimum)
├─ Evidence collection for audits
└─ Trend reporting (improvement tracking)
```

---

## SECTION 5: INCIDENT RESPONSE PLAYBOOKS

### Ransomware Response

```
1. ISOLATION (0-5 minutes)
   └─ Network isolate compromised endpoint
   
2. CONTAINMENT (5-30 minutes)
   ├─ Identify lateral movement direction
   ├─ Block suspicious IPs/domains
   └─ Disable suspect accounts
   
3. INVESTIGATION (30 min - 2 hours)
   ├─ Preserve forensic evidence
   ├─ Identify patient zero
   ├─ Determine encryption type
   └─ Assess backup status
   
4. RECOVERY (2+ hours)
   ├─ Restore from clean backups
   ├─ Reimage if necessary
   └─ Patch vulnerabilities that enabled attack
```

### Malware Detection Response

```
1. IMMEDIATE ACTION
   ├─ Isolate from network
   ├─ Kill malicious process
   └─ Block command & control (C2) servers
   
2. INVESTIGATION
   ├─ Analyze file hashes (VirusTotal)
   ├─ Determine malware family
   └─ Check for lateral movement
   
3. REMEDIATION
   ├─ Remove malware files
   ├─ Revoke compromised credentials
   └─ Patch vulnerable software
```

---

## SECTION 6: METRICS & KPIs

```
Key Performance Indicators (KPIs)
═══════════════════════════════════════════════════════════════════════════════

Vulnerability Management:
├─ MTTR (Mean Time To Remediation): <30 days target
├─ Patch compliance: 95%+ target
├─ Zero-day detection time: <24 hours
└─ Vulnerability severity distribution: Trending down

Compliance:
├─ CIS benchmark: 85%+ target
├─ PCI-DSS compliance: 100% for payment systems
├─ Audit findings: <5% fail rate
└─ Exception approvals: Trending down

Incident Response:
├─ MTTD (Mean Time To Detect): <5 minutes
├─ MTTR (Mean Time To Respond): <2 hours
├─ False positive rate: <10%
└─ Incidents escalated: Trending down
```

---

## SECTION 7: LEARNING RESOURCES

### Books

```
Essential Reading:
├─ "Endpoint Detection and Response (EDR)" by Chad Tullis
├─ "Incident Response: Attack Simulation" by Ed Skoudis
├─ "The Practical SIEM" by Glenn David
└─ "Applied Incident Response" by Steve Anson
```

### Online Courses

```
Platforms:
├─ SANS SEC504 (Hacker Tools) - $8K+
├─ Coursera (Google Cloud Security)
├─ Linux Academy (Cloud Security)
└─ Cybrary (free security courses)
```

### Certifications

```
Relevant Certs:
├─ CEH (Certified Ethical Hacker)
├─ OSCP (Offensive Security)
├─ GCIH (GIAC Certified Incident Handler)
└─ CompTIA Security+
```

---

**Document Version:** 1.0  
**Frameworks Covered:** 5+ (NIST, CIS, PCI-DSS, HIPAA, GDPR)  
**Best Practices:** 50+  
**Tools Documented:** 30+  
**Compliance Resources:** Comprehensive  
**Status:** Complete Reference Guide
