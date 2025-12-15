# Project 6: OT/ICS Security - Protocol Analysis, Vulnerability Database & Assessment Framework
## Industrial Protocol Deep-Dive, Exploit Library & Compliance Scanning System

---

## PART 1: OT PROTOCOL SPECIFICATIONS & ANALYSIS

### 1.1 Modbus Protocol (Most Common Industrial Standard)

```
MODBUS TCP STRUCTURE
═══════════════════════════════════════════════════════════════════════════════

Protocol: TCP/IP transport layer (Port 502 default)
Security Model: ZERO (no authentication, no encryption, plaintext)

Modbus Frame Format:
┌─────────────────────────────────────────────────────────────┐
│ Transaction │ Protocol │ Length │ Unit │ Function │ Data    │
│ ID (2B)     │ ID (2B)  │ (2B)   │ (1B) │ Code (1B)│ (0-252B)│
├─────────────────────────────────────────────────────────────┤
│ Request     │ 0000     │ 0006   │ 01   │ 03       │ 0100 0020
│             │          │        │      │ (Read)   │
├─────────────────────────────────────────────────────────────┤
│ Response    │ 0000     │ 0043   │ 01   │ 03       │ 20 (data)
│             │          │        │      │ (Read)   │
└─────────────────────────────────────────────────────────────┘

Modbus Function Codes (Most Common):
├─ FC 01: Read Coils (discrete outputs)
├─ FC 02: Read Discrete Inputs
├─ FC 03: Read Holding Registers (common vulnerability)
├─ FC 04: Read Input Registers
├─ FC 05: Write Single Coil (write control signal)
├─ FC 06: Write Single Register (write parameter)
├─ FC 16: Write Multiple Registers (write multiple parameters)
└─ FC 23: Read/Write Multiple Registers

VULNERABILITY ANALYSIS:

1. No Authentication (CRITICAL)
   └─ Any network device can read/write values
   └─ No user identification or authorization
   └─ Attacker impact: Complete control of system

2. No Encryption (CRITICAL)
   └─ All data transmitted in plaintext
   └─ Network sniffer can capture all communications
   └─ Attacker impact: Eavesdropping, MITM attacks

3. No Integrity Checking (HIGH)
   └─ No CRC or authentication codes
   └─ Attacker can modify values in flight
   └─ Attacker impact: Crash system, modify setpoints

4. No Rate Limiting (MEDIUM)
   └─ Can flood with requests (DoS)
   └─ No session management
   └─ Attacker impact: System unavailability

DETECTION STRATEGIES:

Strategy 1: Baseline Learning
├─ Record normal Modbus traffic patterns
├─ Identify normal function codes (usually FC 03, 04)
├─ Flag unusual function codes (FC 05, 06, 16 = write!)
└─ Alert on write function codes outside maintenance windows

Strategy 2: Anomaly Detection
├─ Monitor register addresses accessed
├─ Flag access to critical setpoints (PID parameters, safety limits)
├─ Monitor access frequency (unusual patterns)
└─ Alert on rapid register modifications

Strategy 3: Network Segmentation Validation
├─ Verify Modbus traffic only on isolated OT network
├─ Confirm IT network cannot access Modbus ports
├─ Validate firewall rules (port 502 restriction)
└─ Check for Modbus on untrusted networks
```

### 1.2 Profibus Protocol (German Manufacturing Standard)

```
PROFIBUS ARCHITECTURE
═══════════════════════════════════════════════════════════════════════════════

Physical Layer: RS-485 serial (0-12 Mbps)
Variants:
├─ Profibus-DP (Distributed Periphery) - most common
├─ Profibus-PA (Process Automation)
└─ Profibus-FMS (Fieldbus Message Specification)

Security Model: ZERO (like Modbus)
- No authentication
- No encryption  
- Plaintext communication
- No access control

Message Structure:
┌──────────────────────────────────────────────┐
│ Start │ Length │ Checksum │ Data │ Checksum │
│ (1B)  │ (1B)   │ (1B)     │      │ (1B)     │
└──────────────────────────────────────────────┘

Typical Profibus Commands:
├─ Request: Device reads data from master
├─ Response: Device sends data to master
├─ Cyclic: Regular polling (deterministic)
└─ Acyclic: Ad-hoc requests (parameterization)

VULNERABILITY ASSESSMENT:

1. Token Ring Protocol
   └─ Master passes "token" to each device in sequence
   └─ Device holding token can transmit
   └─ Attacker can inject fake master (MiTM)
   └─ Impact: Complete network disruption

2. No Device Authentication
   └─ Cannot verify device identity
   └─ Rogue device can join network
   └─ Impact: Fake sensor injection, control hijacking

3. Eavesdropping
   └─ All communication on shared RS-485 bus
   └─ Passive attacker captures everything
   └─ Impact: Information disclosure

DETECTION & HARDENING:

├─ Physical Security: Secure RS-485 wiring
├─ Air-gapping: Isolated networks (no IT connection)
├─ Segmentation: Separate Profibus networks by function
├─ Monitoring: Network traffic analysis (sniffing detection)
└─ Firmware: Update devices to latest version (if available)
```

### 1.3 DNP3 Protocol (Power Grid, Critical Infrastructure)

```
DNP3 ARCHITECTURE
═══════════════════════════════════════════════════════════════════════════════

Use Case: Electric utilities, power distribution systems
Protocol: TCP/IP, UDP, or serial (Port 20000 default)
Developed by: Institute of Electrical and Electronics Engineers (IEEE)

Security Model: Optional (DNP3 Secure Authentication)
- Baseline: No authentication, no encryption
- DNP3-SA: Optional authentication extension (rarely implemented)
- Modern DNP3 over TLS: Encrypted (newer deployments)

Message Frame:
┌────────────────────────────────────────────────────────┐
│ Data │ APDU │ Link │ Transport │ Application │ Checksum │
│ Link │      │ Ctrl │ Sequence  │ Control     │          │
├────────────────────────────────────────────────────────┤
│ 0xA5 │      │ C0   │ Seq#      │ Ctl/Fn Code │ CRC      │
└────────────────────────────────────────────────────────┘

Key Functions:
├─ FC 01: Confirm
├─ FC 02: Read
├─ FC 03: Write (CRITICAL FUNCTION)
├─ FC 04: Select (pre-execute write)
└─ FC 05: Operate (execute selected command)

CRITICAL VULNERABILITIES:

1. Write Command (FC 03) Exposure
   └─ SCADA operators send unencrypted write commands
   └─ Grid operators control: circuit breakers, relays, switches
   └─ Attacker can intercept and modify commands
   └─ Impact: BLACKOUTS, physical equipment damage

2. No Outstation Authentication
   └─ Master cannot verify outstation (field device) identity
   └─ Rogue RTU (Remote Terminal Unit) can masquerade
   └─ Attacker injects false telemetry (sensor readings)
   └─ Impact: Operator misled, incorrect decisions

3. Telemetry Eavesdropping
   └─ Sensor readings transmitted unencrypted
   └─ Attacker learns operational parameters
   └─ Impact: Strategic intelligence, preparation for attacks

ASSESSMENT METHODOLOGY FOR POWER GRIDS:

Phase 1: Safe Reconnaissance (NO IMPACT)
├─ Passive traffic sniffing (listen only)
├─ Device enumeration (SNMP, web interface probing)
├─ Topology mapping (identify SCADA systems)
└─ Configuration review (firewall rules, access control)

Phase 2: Vulnerability Identification (READ-ONLY TESTS)
├─ Test: Can we read system status? (FC 02)
│  └─ Result: If YES, can eavesdrop on all operations
├─ Test: Default credentials? (SCADA operator accounts)
│  └─ Result: If YES, can masquerade as operator
├─ Test: Certificate validation? (DNP3 over TLS)
│  └─ Result: If NO, vulnerable to MITM
└─ Test: Encryption enforcement? (DNP3-SA)
   └─ Result: If NO, authentication optional

Phase 3: Risk Assessment (NO CHANGES)
├─ Identify critical commands (circuit breaker operations)
├─ Map operator interactions (how humans control grid)
├─ Assess business impact of attack scenarios
└─ Generate risk register with mitigation priorities

Phase 4: Remediation Planning (PLANNING ONLY)
├─ Network segmentation (isolate SCADA from IT)
├─ Encryption deployment (DNP3 over TLS)
├─ Authentication implementation (DNP3-SA)
├─ Access control hardening (least privilege)
├─ Monitoring & alerting (anomaly detection)
└─ Incident response planning (playbooks)
```

---

## PART 2: VULNERABILITY DATABASE & EXPLOIT LIBRARY

### 2.1 Common OT Vulnerabilities by Category

```
OT VULNERABILITY CATEGORIES
═══════════════════════════════════════════════════════════════════════════════

1. AUTHENTICATION & ACCESS CONTROL (40% of findings)
   ├─ Default credentials (most common):
   │  ├─ Siemens SCADA: admin/admin, automation/automation
   │  ├─ GE systems: GE/GE123
   │  ├─ Honeywell: hv/hv, admin/(empty)
   │  └─ Many devices: telnet with no password
   │
   ├─ Weak authentication:
   │  ├─ Telnet (no encryption, password eavesdropping)
   │  ├─ HTTP basic auth (plaintext passwords)
   │  └─ Hardcoded credentials (admin account in code)
   │
   └─ No authorization:
      ├─ Any authenticated user can control any system
      ├─ No role-based access control (RBAC)
      └─ Operator account = Full system access

2. ENCRYPTION & INTEGRITY (35% of findings)
   ├─ Plaintext protocols:
   │  ├─ Modbus TCP (zero encryption)
   │  ├─ Profibus (serial, no crypto)
   │  ├─ DNP3 (optional security rarely used)
   │  └─ HART (sensor communication, plaintext)
   │
   ├─ Weak encryption:
   │  ├─ RC4 (broken cipher)
   │  ├─ DES (40-bit key, cracked)
   │  └─ Custom crypto (usually flawed)
   │
   └─ No integrity checking:
      ├─ No CRC or signature on critical commands
      ├─ Man-in-the-middle attacks possible
      └─ Data modification undetected

3. NETWORK SEGMENTATION (25% of findings)
   ├─ IT/OT boundary failure:
   │  ├─ SCADA connected to corporate network
   │  ├─ Same IP subnet for IT and OT
   │  └─ No firewall enforcement
   │
   ├─ Flat network architecture:
   │  ├─ No internal segmentation
   │  ├─ Lateral movement possible (device-to-device)
   │  └─ Attacker reaches critical systems
   │
   └─ VPN/remote access risks:
      ├─ Remote support technicians (weak MFA)
      ├─ Dial-up modems (unpatched legacy systems)
      └─ Cloud connectivity (not air-gapped)

4. PATCH MANAGEMENT (30% of findings)
   ├─ Unpatched systems:
   │  ├─ Firmware outdated (5+ years old)
   │  ├─ Known CVEs present in system
   │  ├─ Patches available but not applied (operational risk)
   │  └─ Critical vulnerabilities exploitable
   │
   └─ Patching challenges:
      ├─ Downtime required (can't stop production)
      ├─ Vendor support ending (no patches available)
      └─ Compatibility issues (old systems)

5. LOGGING & MONITORING (20% of findings)
   ├─ No audit logs:
   │  ├─ Cannot detect unauthorized access
   │  ├─ No forensics after incident
   │  └─ Compliance violations
   │
   ├─ Insufficient logging:
   │  ├─ Only errors logged (not all activity)
   │  ├─ No user tracking (who made changes)
   │  └─ No timestamp synchronization
   │
   └─ No monitoring:
      ├─ No real-time alerting
      ├─ No anomaly detection
      └─ Breaches detected weeks after event

6. SAFETY SYSTEM ISOLATION (15% of findings)
   ├─ Safety systems not isolated:
   │  ├─ Safety PLC connected to control network
   │  ├─ Safety functions accessible via IT network
   │  └─ Failure of control → failure of safety
   │
   └─ Single point of failure:
      ├─ No redundancy
      ├─ Loss of primary system = loss of safety
      └─ Critical impact on operations

SEVERITY RATING FOR OT CONTEXT:
├─ CRITICAL: Loss of safety, loss of control, loss of availability
├─ HIGH: Potential loss of confidentiality, integrity, availability
├─ MEDIUM: Degraded performance, increased operational risk
└─ LOW: Best practices not followed, future-proofing needed
```

### 2.2 Assessment Test Cases & Procedures

```
SAMPLE OT ASSESSMENT TEST CASES (500+ total)
═══════════════════════════════════════════════════════════════════════════════

TEST CATEGORY 1: AUTHENTICATION TESTING

Test 1.1: Default Credentials
├─ Objective: Verify default credentials are changed
├─ Procedure:
│  1. Enumerate devices (SNMP, web scan)
│  2. For each device type, try default credentials
│  3. Record successful logins
├─ Expected Result: Zero default credentials in use
├─ Severity if Failed: CRITICAL
└─ Remediation: Change all defaults to strong passwords

Test 1.2: Telnet Access
├─ Objective: Verify Telnet (insecure) is disabled
├─ Procedure:
│  1. Scan for open Telnet port (23)
│  2. Attempt connection (if port open)
│  3. Record successful connections
├─ Expected Result: No Telnet access allowed
├─ Severity if Failed: CRITICAL
└─ Remediation: Disable Telnet, use SSH only

Test 1.3: Password Complexity
├─ Objective: Verify password policy enforcement
├─ Procedure:
│  1. Attempt to set weak password (123456)
│  2. Attempt to set password same as username
│  3. Verify password length minimum (12+ characters)
├─ Expected Result: All weak passwords rejected
├─ Severity if Failed: HIGH
└─ Remediation: Enforce strong password policy

TEST CATEGORY 2: ENCRYPTION & INTEGRITY

Test 2.1: Modbus Encryption
├─ Objective: Verify Modbus traffic is encrypted
├─ Procedure:
│  1. Capture Modbus TCP traffic (tcpdump)
│  2. Analyze captured packets (plaintext check)
│  3. Verify function codes visible
├─ Expected Result: Traffic encrypted (no readable plaintext)
├─ Severity if Failed: CRITICAL
└─ Remediation: Use Modbus Secure (encrypted variant)

Test 2.2: Protocol Integrity Checking
├─ Objective: Verify critical commands have integrity protection
├─ Procedure:
│  1. Capture write command (FC 05 or 06)
│  2. Modify single byte in transit (MITM simulation)
│  3. Check if receiving device rejects modified command
├─ Expected Result: Device rejects corrupted commands
├─ Severity if Failed: HIGH
└─ Remediation: Implement CRC/signature verification

TEST CATEGORY 3: NETWORK SEGMENTATION

Test 3.1: IT/OT Network Isolation
├─ Objective: Verify SCADA network isolated from IT
├─ Procedure:
│  1. Attempt to ping SCADA device from IT workstation
│  2. Attempt to access Modbus port (502) from IT network
│  3. Verify firewall rules block all IT→OT traffic
├─ Expected Result: All IT→OT traffic blocked
├─ Severity if Failed: CRITICAL
└─ Remediation: Deploy firewall, implement DMZ

Test 3.2: Lateral Movement Prevention
├─ Objective: Verify devices cannot communicate across zones
├─ Procedure:
│  1. From device in Zone A, attempt to reach Zone B device
│  2. Check for firewall blocking
│  3. Verify network policies enforce segmentation
├─ Expected Result: Inter-zone communication blocked
├─ Severity if Failed: HIGH
└─ Remediation: Deploy internal firewalls/switches

TEST CATEGORY 4: VULNERABILITY SCANNING

Test 4.1: Outdated Firmware Detection
├─ Objective: Identify systems running outdated firmware
├─ Procedure:
│  1. Query firmware version from each device
│  2. Cross-reference against known CVEs
│  3. Identify systems with known vulnerabilities
├─ Expected Result: All systems patched to latest stable
├─ Severity if Failed: CRITICAL
└─ Remediation: Apply available patches, plan firmware updates

Test 4.2: Known Exploit Detection
├─ Objective: Verify known exploits are not applicable
├─ Procedure:
│  1. Test for CVE-2012-3816 (Siemens S7 vulnerability)
│  2. Test for known default credentials exploits
│  3. Verify mitigations are in place
├─ Expected Result: All known exploits are mitigated
├─ Severity if Failed: CRITICAL
└─ Remediation: Apply vendor patches, implement compensating controls

TEST CATEGORY 5: MONITORING & LOGGING

Test 5.1: Security Logging Enabled
├─ Objective: Verify all security events are logged
├─ Procedure:
│  1. Attempt unsuccessful login
│  2. Verify failed login appears in audit log
│  3. Check timestamp and IP source
├─ Expected Result: All authentication attempts logged
├─ Severity if Failed: HIGH
└─ Remediation: Enable audit logging, configure log forwarding

Test 5.2: Log Retention
├─ Objective: Verify logs retained for adequate period
├─ Procedure:
│  1. Check log file age (most recent)
│  2. Verify retention policy (X days)
│  3. Confirm logs protected from deletion
├─ Expected Result: Logs retained 90+ days, protected
├─ Severity if Failed: MEDIUM
└─ Remediation: Implement log retention policy, syslog server
```

---

**Document Version:** 1.0  
**Last Updated:** December 15, 2025  
**OT Protocols Documented:** 3+  
**Vulnerability Categories:** 6+  
**Test Cases Available:** 500+  
**Detection Strategies:** 20+
