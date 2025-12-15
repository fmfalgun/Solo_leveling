# Project 6: OT/ICS Security - Complete Reference Guide & Resource Compilation
## Standards, Tools, Frameworks & Implementation Resources

---

## SECTION 1: OT/ICS STANDARDS & FRAMEWORKS

### IEC 62443 (Industrial Automation and Control Systems Security)

**Standard Overview:**
- Develops internationally by International Electrotechnical Commission
- Covers: SCADA, DCS, PLC, IACS security
- Four parts:
  - IEC 62443-1-1: Vocabulary and concepts
  - IEC 62443-2-x: Policy and procedures
  - IEC 62443-3-x: System security requirements
  - IEC 62443-4-x: Component security requirements

**22 System Security Requirements (SRs):**

```
SR-1: Identification and Authentication
SR-2: Use Control
SR-3: System Integrity
SR-4: Information Confidentiality
SR-5: Restrict Data Flow
SR-6: Timely Response to Events
SR-7: System Monitoring and Alerting
SR-8: Software/Firmware Integrity
SR-9: Configuration Management
SR-10: Information Deletion
SR-11: Cybersecurity Event Accountability
SR-12: Information Handling
SR-13: Information Exposure
SR-14: Secure Defaults
SR-15: Registry or Database Integrity
SR-16: Trusted Channel
SR-17: Secure Coding
SR-18: Software Documentation
SR-19: Software Quality Assurance
SR-20: Secured Device Installation
SR-21: Integrity of Control Devices
SR-22: Information System Partitioning
```

**Resources:**
- IEC 62443-1-1:2010 (Vocabulary) - free preview
- IEC 62443-3-3:2013 (System Security) - €198 (purchase required)
- NIST Cybersecurity Framework CSF (free alternative)

---

### NIST Cybersecurity Framework (CSF)

**Five Functions (applicable to OT):**

1. **IDENTIFY (Asset Management)**
   - Maintain inventory of assets
   - Identify critical systems
   - Categorize systems by function
   - Document data flows

2. **PROTECT (Access Control & Hardening)**
   - Authentication & authorization
   - Network segmentation
   - Data protection (encryption)
   - System hardening

3. **DETECT (Monitoring & Alerting)**
   - Anomaly detection systems
   - Security event logging
   - Threat intelligence integration
   - Alert mechanisms

4. **RESPOND (Incident Handling)**
   - Incident response plan
   - Containment procedures
   - Evidence collection
   - Communication protocols

5. **RECOVER (Business Continuity)**
   - Disaster recovery plan
   - Backup systems & testing
   - System restoration procedures
   - Post-incident improvements

**Resource:** Download free from NIST (https://www.nist.gov/cyberframework)

---

### NERC CIP (North American Electric Reliability Corporation)

**Applicability:** Bulk Electric System (BES) in North America

**Standards (CIP-002 through CIP-014):**

```
CIP-002: Systems Security Management
├─ Asset identification
├─ Security program
└─ Cyber security plan

CIP-003: Security Management Controls
├─ Personnel security
├─ Physical security perimeter
└─ Systems security management

CIP-004: Personnel and Training
├─ Personnel risk assessment
├─ Security awareness training
└─ Authorized access

CIP-005: Systems Security Perimeter
├─ Electronic security perimeter
├─ Electronic access control or monitoring
└─ Physical security of electronic devices

CIP-007: System Security Management
├─ Security patch management
├─ Malware prevention
├─ System security configuration
└─ Physical security controls

CIP-009: Recovery Plans for BES Cyber Systems
├─ Backup systems
├─ Restoration procedures
└─ Testing of recovery capability
```

**Penalties:** $25K-$500K per violation

---

## SECTION 2: OT PROTOCOLS & TECHNOLOGIES

### Industrial Protocols (Quick Reference)

| Protocol | Layer | Usage | Security | Popularity |
|---|---|---|---|---|
| **Modbus TCP** | Application | General automation | ZERO | 60%+ |
| **Profibus-DP** | Data Link | Manufacturing | ZERO | 40%+ |
| **DNP3** | Application | Power grids, utilities | Optional | 70% (energy) |
| **OPC-UA** | Application | Modern industrial | Strong | Growing |
| **HART** | Application | Sensor data | Weak | High (legacy) |
| **Ethernet/IP** | Application | Allen-Bradley systems | Weak | 30% |
| **Siemens S7** | Application | Siemens SCADA | Weak | 50%+ |

---

## SECTION 3: TOOLS & SOFTWARE

### Free/Open-Source OT Security Tools

```
Network Analysis:
├─ Wireshark - packet capture & analysis (install custom dissectors)
├─ Zeek IDS - network monitoring
├─ Suricata IDS - open IDS with OT plugins
└─ tcpdump - command-line packet capture

Vulnerability Scanning:
├─ OpenVAS - vulnerability scanner
├─ Metasploit - exploitation framework (industrial modules)
├─ Shodan API - search public-facing industrial devices
└─ Custom scripts (Python, Ruby, Bash)

Protocol Analysis:
├─ IDA Pro (free community edition) - firmware analysis
├─ Ghidra - reverse engineering
└─ Binwalk - firmware extraction

Monitoring & Detection:
├─ Osquery - system monitoring
├─ Wazuh - log aggregation + alerts
├─ ELK Stack - Elasticsearch, Logstash, Kibana
└─ OSSEC - host-based intrusion detection

Configuration & Hardening:
├─ Ansible - configuration management
├─ Chef - infrastructure automation
├─ Kubernetes - container orchestration (modern OT)
└─ Terraform - infrastructure as code

Compliance & Reporting:
├─ OpenSCAP - compliance scanning
├─ Lynis - security audit tool
└─ Custom reporting scripts (Python + templating)
```

### Commercial OT Security Tools (For Comparison)

```
Vulnerability Management:
├─ Nessus OT - $50K-$100K/year
├─ Qualys OT - $75K-$150K/year
└─ Rapid7 InsightVM - $60K-$120K/year

Network Monitoring:
├─ Fortive Nexus - $200K-$500K/year
├─ CyberX (Tenable) - $100K-$250K/year
└─ Claroty - $150K-$300K/year

SCADA-Specific:
├─ GE Predix - enterprise OT platform
├─ Siemens Sitewise - AWS industrial IoT
└─ Honeywell Forge - cloud industrial platform
```

---

## SECTION 4: LEARNING RESOURCES

### Books

```
Essential OT Security Reading:

1. "SCADA Systems Security" by Gopal Chandra
   └─ Overview of SCADA architecture and threats

2. "Industrial Network Security" by Eric D. Knapp
   └─ Detailed network segmentation and monitoring

3. "Practical SCADA Security" by Paul Schweitzer
   └─ Real-world hardening techniques

4. "Applied Cyber Physical Systems Security" by Quanyan Zhu
   └─ Safety-critical systems (healthcare, power)

5. "The NIST Cybersecurity Framework" (Official)
   └─ Free download from NIST website
```

### Online Courses

```
Free Resources:
├─ SANS OnDemand OT Security (expensive but reputable)
├─ NIST Cybersecurity Framework (online training)
├─ ICS-CERT (Department of Homeland Security) advisories
└─ YouTube: "SCADA hacking" playlists (security researchers)

Certifications:
├─ GICSP (GIAC Industrial Control Systems Professional)
├─ GSEC (GIAC Security Essentials) - IT base
├─ OSCP (Offensive Security Certified Professional) - good foundation
└─ ICS-CERT Training (government, free for critical infrastructure)
```

### Research Papers & Publications

```
Academic Databases:
├─ IEEE Xplore (industrial control systems papers)
├─ ACM Digital Library (security research)
├─ ResearchGate (preprints from researchers)
└─ ArXiv (latest security papers)

Key Research Topics:
├─ Modbus vulnerability analysis
├─ DNP3 protocol security
├─ SCADA anomaly detection (ML approaches)
├─ Network segmentation for ICS
├─ Safety-critical system security
└─ Critical infrastructure protection
```

---

## SECTION 5: COMPLIANCE CHECKLISTS

### Quick IEC 62443 Assessment Checklist

- [ ] SR-1: Can you uniquely identify each user?
- [ ] SR-2: Can you restrict unauthorized actions?
- [ ] SR-3: Can you detect system modifications?
- [ ] SR-4: Is sensitive data encrypted?
- [ ] SR-5: Do firewalls restrict data flow?
- [ ] SR-6: Do you detect security events in real-time?
- [ ] SR-7: Is there continuous monitoring?
- [ ] SR-8: Is firmware integrity verified?
- [ ] SR-9: Is configuration managed centrally?
- [ ] SR-10: Can you delete sensitive data?
- [ ] SR-11: Are all cyber events logged & tracked?
- [ ] SR-12: Is information classified?
- [ ] SR-13: Is sensitive information protected?
- [ ] SR-14: Are secure defaults enforced?
- [ ] SR-15: Is database/registry integrity validated?
- [ ] SR-16: Are trusted channels used for critical communication?
- [ ] SR-17: Is code developed securely?
- [ ] SR-18: Is software documentation available?
- [ ] SR-19: Are quality assurance practices implemented?
- [ ] SR-20: Is device installation secure?
- [ ] SR-21: Are control devices protected from tampering?
- [ ] SR-22: Are different security zones isolated?

**Scoring:** ✓ = 1 point, Partial ✓ = 0.5 point
- 20-22 points: LEVEL 3-4 (Proactive)
- 15-19 points: LEVEL 2 (Managed)
- 10-14 points: LEVEL 1 (Basic)
- 0-9 points: LEVEL 0 (Absent)

---

## SECTION 6: INDUSTRY CONTACTS & COMMUNITIES

### Professional Organizations

```
ISACA (Information Systems Audit and Control Association)
├─ Offers GIAC certifications
├─ Professional community
└─ Networking events (local chapters)

IEEE Industrial Electronics Society
├─ Research publications
├─ Conference proceedings
└─ Professional networking

ICS-CERT (US Homeland Security)
├─ Free advisories on vulnerabilities
├─ Training resources
└─ Incident reporting hotline
```

### Online Communities

```
Reddit:
├─ r/ICS_Security
├─ r/Scada
└─ r/IndustrialControl

LinkedIn:
├─ OT Security professionals group
├─ Industrial IoT group
└─ SCADA Systems group

GitHub:
├─ Industrial protocol dissectors
├─ OT security tools
└─ Security research repositories

Conferences:
├─ S4 (Security of Industrial Control Systems & SCADA)
├─ SecurityWeek: ICS Summit
├─ SANS ICS Cyber Security Summit
└─ Black Hat USA (ICS track)
```

---

## SECTION 7: QUICK START IMPLEMENTATION GUIDE

### Week 1 Kickoff (First Steps)

```
Day 1: Learning & Assessment Scoping
├─ Read IEC 62443-1-1 (vocabulary)
├─ Review NIST CSF overview
├─ Identify organization's OT systems
└─ Define scope of assessment

Day 2-3: Protocol Deep-Dive
├─ Study Modbus TCP/RTU
├─ Download Wireshark
├─ Install custom Modbus dissector
└─ Analyze sample PCAP files

Day 4-5: Tool Setup
├─ Install Zeek or Suricata
├─ Set up test SCADA lab (VM-based simulation)
├─ Create default credential database
└─ Build protocol parser (Python)

Tools to Install:
├─ Wireshark (packet analysis)
├─ Python 3.10+ (automation scripts)
├─ Docker (lab environment)
├─ Git (version control)
└─ VS Code or PyCharm (IDE)

Budgeted Time: 40 hours
Cost: Free (open-source tools)
```

---

## SECTION 8: PROJECT SUCCESS METRICS

### Portfolio Impact Goals

```
At Project Completion (14 weeks):

Deliverables:
├─ 8-10 working software tools
├─ 200+ pages documentation
├─ 5+ case studies (real assessments)
├─ 4-5 blog posts
└─ 1 research paper draft

Market Position:
├─ GitHub: 500-1,000 stars (if public)
├─ Industry recognition: 3-5 speaking invitations
├─ Consulting pipeline: 2-3 leads
└─ Job offers: 5-10 interviews (OT security roles)

Financial Impact (Year 1):
├─ Consulting revenue: $150K-$300K
├─ SaaS revenue (if scaled): $200K-$400K
├─ Total Year 1: $350K-$700K
└─ Year 2 projection: $500K-$2M

Career Advancement:
├─ Senior engineer roles: $220K-$350K salary
├─ Consulting founder: $200K-$500K+ income
├─ Speaking engagements: $5K-$25K per event
└─ Book opportunity: $50K-$200K advances
```

---

## SECTION 9: CRITICAL SUCCESS FACTORS

```
1. SAFETY FIRST
   └─ Non-disruptive testing (zero downtime) is essential
   └─ No production system disruption = trust & repeat business

2. COMPLIANCE EXPERTISE
   └─ Deep knowledge of IEC 62443, NIST, NERC CIP
   └─ Firms pay premium for compliance mapping

3. PRACTICAL METHODOLOGY
   └─ Real-world assessment experience (via case studies)
   └─ Playbooks for common vulnerabilities

4. AUTOMATION & SPEED
   └─ Manual assessments take 2-4 weeks
   └─ Your tools should reduce to 2-3 days

5. PROFESSIONAL PRESENTATION
   └─ Executive-grade reports (for C-suite)
   └─ Technical findings (for engineers)
   └─ Compliance mapping (for compliance team)

6. INDUSTRY NETWORKING
   └─ Build relationships with energy, manufacturing, healthcare
   └─ Sponsorships & speaking at OT security conferences
   └─ Early mover advantage (2-3 year window)
```

---

**Document Version:** 1.0  
**Last Updated:** December 15, 2025  
**Total Resources:** 50+ references  
**Standards Covered:** 3 (IEC 62443, NIST CSF, NERC CIP)  
**Tools Documented:** 30+  
**Success Metrics:** Comprehensive  
**Implementation Guide:** Complete  
**Status:** Ready for Execution
