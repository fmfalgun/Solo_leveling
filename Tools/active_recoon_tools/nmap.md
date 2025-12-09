# NMAP: A Comprehensive Guide to Network Mapping and Port Scanning

## Table of Contents
1. [Introduction](#introduction)
2. [Network Scanning Fundamentals](#network-scanning-fundamentals)
3. [How NMAP Works](#how-nmap-works)
4. [Installation and Setup](#installation-and-setup)
5. [Basic Syntax and Usage](#basic-syntax-and-usage)
6. [Host Discovery Techniques](#host-discovery-techniques)
7. [Port Scanning Methods](#port-scanning-methods)
8. [Service Detection](#service-detection)
9. [Operating System Fingerprinting](#operating-system-fingerprinting)
10. [Nmap Scripting Engine (NSE)](#nmap-scripting-engine-nse)
11. [Output Formats and Reporting](#output-formats-and-reporting)
12. [Firewall Evasion Techniques](#firewall-evasion-techniques)
13. [Performance Optimization](#performance-optimization)
14. [Practical Examples and Workflows](#practical-examples-and-workflows)
15. [Detection and Defense](#detection-and-defense)
16. [Security and Ethical Considerations](#security-and-ethical-considerations)

---

## Introduction

**Nmap** (Network Mapper) is the world's leading open-source network scanning and reconnaissance tool. It enables network administrators, security professionals, and penetration testers to discover hosts, services, and vulnerabilities across networks. Nmap can identify which hosts are available, what services they're running, what operating systems they use, and much more.

### Key Characteristics

- **Host Discovery**: Identify live hosts across networks
- **Port Scanning**: Determine which ports are open, closed, or filtered
- **Service Detection**: Identify running services and their versions
- **OS Fingerprinting**: Detect operating systems and versions
- **Vulnerability Detection**: Use NSE scripts for advanced scanning
- **Multiple Scan Types**: TCP SYN, UDP, ACK, FIN, Xmas, Null, and more
- **Firewall Evasion**: Techniques to bypass firewall rules
- **Script Automation**: Lua-based scripting engine for custom tasks
- **Multiple Output Formats**: Normal, XML, grepable, and custom outputs
- **Performance Tuning**: Parallel scanning for speed optimization

### Primary Use Cases

- **Network Inventory**: Discover all devices on a network
- **Security Assessment**: Identify vulnerabilities and misconfigurations
- **Compliance Auditing**: Verify services and configurations
- **Troubleshooting**: Diagnose network connectivity issues
- **Vulnerability Management**: Find exploitable services
- **Penetration Testing**: Authorized security testing
- **Incident Response**: Investigate security breaches
- **Network Mapping**: Create network topology diagrams
- **Asset Tracking**: Monitor network devices
- **Firewall Testing**: Verify firewall rules

### Limitations

- **Requires Network Access**: Must be able to reach target network
- **Easily Detected**: IDS/IPS systems recognize nmap patterns
- **Single Machine**: Doesn't scale to Internet-wide scanning (for that use Shodan/Censys)
- **Noisy**: Obvious reconnaissance patterns
- **Accuracy**: Fingerprinting may be incorrect for patched systems

---

## Network Scanning Fundamentals

### TCP/IP Protocol Basics

**Three-Way TCP Handshake**:

```
CLIENT                          SERVER
  │                              │
  ├─ SYN (seq=x) ────────────>│
  │ (Client initiates)          │
  │                              │
  │<─ SYN-ACK (seq=y, ack=x+1) ──┤
  │ (Server responds)            │
  │                              │
  ├─ ACK (seq=x+1, ack=y+1) ──>│
  │ (Client confirms)            │
  │                              │
  └────── Connection Established─┘

Port States:
  OPEN: Service listening (SYN-ACK received)
  CLOSED: No service listening (RST received)
  FILTERED: Firewall blocking (no response)
```

### ICMP Ping Types

```
ICMP Echo Request (Ping)
  │
  ├─ Type 8 (Echo Request)
  │  └─ Used to test host availability
  │
  └─ Type 0 (Echo Reply)
     └─ Sent by target when alive
```

### UDP Port States

```
UDP Port Scan:
  │
  ├─ No Response
  │  └─ Port is open|filtered
  │
  ├─ ICMP Port Unreachable
  │  └─ Port is closed
  │
  └─ UDP Response
     └─ Port is open
```

---

## How NMAP Works

### Operational Model

```
┌────────────────────────────────────┐
│ User Input                         │
│ nmap -sS -p 1-1000 192.168.1.1    │
└────────┬─────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ Parse Arguments                    │
│ ├─ Scan type: -sS (SYN scan)      │
│ ├─ Ports: 1-1000                  │
│ ├─ Target: 192.168.1.1            │
│ └─ Other options                   │
└────────┬─────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ Host Discovery                     │
│ ├─ Ping target                     │
│ ├─ Verify host is alive            │
│ └─ Get MAC address (ARP)           │
└────────┬─────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ Port Scanning                      │
│ ├─ For each port in range:         │
│ │  └─ Send probe packet            │
│ ├─ Listen for responses            │
│ ├─ Classify port state             │
│ └─ Continue parallel scanning      │
└────────┬─────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ Service Detection                  │
│ ├─ For open ports:                 │
│ │  └─ Send service-specific probes │
│ ├─ Match against fingerprint DB    │
│ └─ Identify service/version        │
└────────┬─────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ OS Fingerprinting                  │
│ ├─ Send specially crafted probes   │
│ ├─ Analyze responses               │
│ ├─ Match against known signatures  │
│ └─ Determine OS and version        │
└────────┬─────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ Script Scanning (NSE)              │
│ ├─ Run requested scripts           │
│ ├─ Perform vulnerability checks    │
│ └─ Report findings                 │
└────────┬─────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ Output Generation                  │
│ ├─ Format results                  │
│ ├─ Write to specified format       │
│ └─ Display to user                 │
└────────────────────────────────────┘
```

### Port State Classification

```
OPEN:
  ├─ Service listening and responding
  ├─ Receives: SYN-ACK in response to SYN
  └─ Most concerning (exploitable service)

CLOSED:
  ├─ No service listening
  ├─ Receives: RST (reset packet)
  └─ Port accessible but nothing listening

FILTERED:
  ├─ Firewall blocking or filtering
  ├─ Receives: No response or ICMP unreachable
  └─ Cannot determine if open or closed

UNFILTERED:
  ├─ Port accessible but cannot determine state
  ├─ Used in ACK scan
  └─ Port responds but state unknown

OPEN|FILTERED:
  ├─ Could be open or filtered
  ├─ Occurs with UDP/IP protocol scans
  └─ No definitive response received

CLOSED|FILTERED:
  ├─ Cannot determine if closed or filtered
  ├─ Rare port state
  └─ Indicative of unusual responses
```

---

## Installation and Setup

### Linux Installation

**Kali Linux** (Pre-installed):

```bash
nmap --version
```

**Ubuntu/Debian**:

```bash
sudo apt update
sudo apt install nmap
```

**Fedora/RHEL/CentOS**:

```bash
sudo dnf install nmap
```

**Arch Linux**:

```bash
sudo pacman -S nmap
```

### macOS Installation

```bash
brew install nmap
```

### From Source

```bash
git clone https://github.com/nmap/nmap.git
cd nmap
./configure
make
sudo make install
```

### Zenmap (GUI)

```bash
# Kali Linux
sudo apt install zenmap

# macOS
brew install zenmap

# Windows
# Download from nmap.org
```

### Verification

```bash
# Check version
nmap --version

# Check NSE scripts
ls /usr/share/nmap/scripts/

# Display help
nmap -h
```

---

## Basic Syntax and Usage

### General Command Structure

```bash
nmap [SCAN TYPE] [OPTIONS] [TARGET]
```

### Target Specification

nmap accepts multiple target formats:

```bash
# Single host
nmap 192.168.1.1
nmap example.com

# Multiple hosts
nmap 192.168.1.1 192.168.1.2 192.168.1.3

# IP range
nmap 192.168.1.1-254

# CIDR notation (recommended)
nmap 192.168.1.0/24        # /24 = 256 addresses
nmap 192.168.0.0/16         # /16 = 65,536 addresses

# From file
nmap -iL targets.txt

# Random targets
nmap -iR 1000

# Exclude hosts
nmap 192.168.1.0/24 --exclude 192.168.1.1,192.168.1.254
nmap 192.168.1.0/24 --excludefile exclude.txt
```

### Most Common Commands

| Command | Purpose |
|---------|---------|
| `nmap 192.168.1.1` | Basic TCP SYN scan |
| `nmap -sV 192.168.1.1` | Service version detection |
| `nmap -O 192.168.1.1` | OS detection |
| `nmap -A 192.168.1.1` | Aggressive: everything (-sV -O -sC) |
| `nmap -p 1-1000 192.168.1.1` | Scan ports 1-1000 |
| `nmap -p- 192.168.1.1` | Scan all 65535 ports |
| `nmap --top-ports 20 192.168.1.1` | Scan 20 most common ports |
| `nmap -sS -p- 192.168.1.0/24` | SYN scan entire subnet |

---

## Host Discovery Techniques

### 1. Ping Scan (-sn / -Pn)

Determine which hosts are alive:

```bash
# Standard ping scan
nmap -sn 192.168.1.0/24

# Without ping (treat all as alive)
nmap -Pn 192.168.1.1

# Ping specific host types
nmap -sn -PE 192.168.1.0/24   # ICMP Echo
nmap -sn -PS80,443 192.168.1.0/24  # TCP SYN
nmap -sn -PA80,443 192.168.1.0/24  # TCP ACK
nmap -sn -PU53 192.168.1.0/24      # UDP
```

### 2. ARP Scan

Fast host discovery on local network:

```bash
# ARP scan (very fast on local network)
nmap -sn -PR 192.168.1.0/24

# ARP only
nmap --send-eth 192.168.1.0/24
```

### 3. Host Discovery Methods

| Method | Flag | Use Case |
|--------|------|----------|
| ICMP Echo | `-PE` | Check if host responds to ping |
| ICMP Timestamp | `-PP` | Firewall evasion |
| ICMP Netmask | `-PM` | Get netmask information |
| TCP SYN | `-PS` | Firewall evasion |
| TCP ACK | `-PA` | Firewall evasion |
| UDP | `-PU` | UDP-based discovery |
| ARP | `-PR` | Local network (fastest) |
| None | `-Pn` | Treat all as alive |

---

## Port Scanning Methods

### 1. TCP SYN Scan (-sS) [RECOMMENDED]

Half-open scanning - send SYN but don't complete handshake:

```bash
# Basic SYN scan (requires root)
sudo nmap -sS 192.168.1.1

# SYN scan on specific port
sudo nmap -sS -p 80 192.168.1.1

# SYN scan port range
sudo nmap -sS -p 1-1000 192.168.1.1

# SYN scan common ports
sudo nmap -sS --top-ports 100 192.168.1.1
```

**Advantages**: Fast, stealthy, doesn't complete connections
**Disadvantages**: Requires raw sockets (root)

### 2. TCP Connect Scan (-sT)

Full three-way handshake:

```bash
# TCP connect scan (no root required)
nmap -sT 192.168.1.1

# Connect scan with service detection
nmap -sT -sV 192.168.1.1
```

**Advantages**: Works without root, reliable
**Disadvantages**: Slower, more detectable, completes connections

### 3. UDP Scan (-sU)

Detect open UDP ports:

```bash
# Basic UDP scan
sudo nmap -sU 192.168.1.1

# UDP scan on specific ports
sudo nmap -sU -p 53,123,137,161 192.168.1.1

# UDP scan top ports
sudo nmap -sU --top-ports 20 192.168.1.1

# Combine TCP and UDP
sudo nmap -sS -sU -p T:22,80,443,U:53,123 192.168.1.1
```

**Advantages**: Discover UDP services
**Disadvantages**: Very slow (UDP is slow)

### 4. TCP ACK Scan (-sA)

Determine firewall rules:

```bash
# ACK scan (firewall mapping)
sudo nmap -sA 192.168.1.1

# ACK scan specific ports
sudo nmap -sA -p 80,443 192.168.1.1
```

**Results**:
- UNFILTERED: Port accessible
- FILTERED: Port blocked

### 5. TCP FIN Scan (-sF)

Stealth scan - send FIN flag:

```bash
# FIN scan
sudo nmap -sF 192.168.1.1

# FIN scan specific port
sudo nmap -sF -p 80 192.168.1.1
```

### 6. TCP NULL Scan (-sN)

Send packets with no flags:

```bash
# NULL scan
sudo nmap -sN 192.168.1.1
```

### 7. TCP Xmas Scan (-sX)

Send FIN, PSH, and URG flags:

```bash
# Xmas scan
sudo nmap -sX 192.168.1.1
```

### Port Specification

```bash
# Specific port
nmap -p 80 192.168.1.1

# Multiple ports
nmap -p 22,80,443 192.168.1.1

# Port range
nmap -p 1-1000 192.168.1.1

# All ports
nmap -p- 192.168.1.1

# Top ports
nmap --top-ports 100 192.168.1.1
nmap --top-ports 1000 192.168.1.1

# Service-based port selection
nmap -p http,https,ssh 192.168.1.1

# Exclude ports
nmap -p- --exclude-ports 22,23,25 192.168.1.1

# TCP and UDP separated
nmap -p T:22,80,U:53,123 192.168.1.1
```

---

## Service Detection

### Version Detection (-sV)

Identify services and versions:

```bash
# Basic service detection
nmap -sV 192.168.1.1

# Service detection with scripts
nmap -sV --version-all 192.168.1.1

# Intensive service detection
nmap -sV --version-intensity 9 192.168.1.1

# Service detection with OS fingerprinting
nmap -sV -O 192.168.1.1

# Fast service detection
nmap -sV --version-intensity 3 192.168.1.1
```

**Version Intensity Levels** (0-9):

```
0: No service detection
3: Fast (light probes)
6: Medium (default)
9: Intensive (many probes)
```

### Common Service Ports

| Port | Service | Command |
|------|---------|---------|
| 21 | FTP | `nmap -p 21 -sV` |
| 22 | SSH | `nmap -p 22 -sV` |
| 23 | Telnet | `nmap -p 23 -sV` |
| 25 | SMTP | `nmap -p 25 -sV` |
| 53 | DNS | `nmap -p 53 -sV` |
| 80 | HTTP | `nmap -p 80 -sV` |
| 110 | POP3 | `nmap -p 110 -sV` |
| 143 | IMAP | `nmap -p 143 -sV` |
| 443 | HTTPS | `nmap -p 443 -sV` |
| 3306 | MySQL | `nmap -p 3306 -sV` |
| 3389 | RDP | `nmap -p 3389 -sV` |
| 5432 | PostgreSQL | `nmap -p 5432 -sV` |
| 5900 | VNC | `nmap -p 5900 -sV` |

---

## Operating System Fingerprinting

### OS Detection (-O)

Identify operating system:

```bash
# Basic OS detection
sudo nmap -O 192.168.1.1

# OS detection with service version
sudo nmap -O -sV 192.168.1.1

# Aggressive OS detection
sudo nmap -O --osscan-guess 192.168.1.1

# Limit OS detection to likely systems
sudo nmap -O --osscan-limit 192.168.1.1
```

### OS Detection Techniques

nmap analyzes:

```
1. TTL Characteristics
   ├─ Initial TTL (64 = Linux, 128 = Windows, 255 = Network Device)
   └─ TTL changes indicate OS

2. TCP Window Size
   ├─ Different for each OS
   └─ Helps fingerprint

3. TCP Option Ordering
   ├─ Sequence of TCP flags
   └─ OS-specific patterns

4. ICMP Echo Response
   ├─ Response timing
   └─ TTL values

5. IP Fragment Reassembly
   ├─ How OS handles fragments
   └─ Fragmentation tolerance
```

### Common TTL Values

| OS | TTL | Example |
|----|-----|---------|
| Linux | 64 | Ubuntu, CentOS, Arch |
| Windows | 128 | Windows 7, 8, 10, 11 |
| macOS | 64 | Mac OS X |
| Cisco IOS | 255 | Routers |
| Solaris | 255 | Servers |

---

## Nmap Scripting Engine (NSE)

### Overview

NSE allows Lua-based scripting for advanced functionality:

```
├─ Vulnerability Detection
├─ Brute Force Attacks
├─ Service Discovery
├─ Malware Detection
├─ Custom Probes
└─ Backdoor Detection
```

### Running Scripts

```bash
# Run default scripts
nmap -sC 192.168.1.1

# Run specific script
nmap --script http-title 192.168.1.1

# Run multiple scripts
nmap --script http-title,http-methods 192.168.1.1

# Run script category
nmap --script "default" 192.168.1.1

# Run all scripts
nmap --script "all" 192.168.1.1

# Run with script arguments
nmap --script ssh-brute --script-args passdb=/tmp/passwords 192.168.1.1
```

### Common NSE Scripts

| Script | Purpose |
|--------|---------|
| `ssh-brute` | SSH brute force |
| `http-brute` | HTTP brute force |
| `smb-os-discovery` | SMB information gathering |
| `smb-enum-shares` | SMB share enumeration |
| `ssl-cert` | SSL certificate inspection |
| `http-title` | Web page title |
| `dns-brute` | DNS subdomain brute force |
| `ntp-info` | NTP server information |
| `mysql-info` | MySQL server information |
| `vnc-info` | VNC information gathering |

### Script Categories

```
auth               Credentials/authentication
default            Default script set
discovery          Discover information
dos                Denial of service
exploit            Exploit vulnerability
external           External services
fuzzer             Fuzz with random data
intrusive          May disrupt services
malware            Malware detection
safe               Non-intrusive safe scripts
version            Service version detection
vuln               Vulnerability detection
```

### Running Script Categories

```bash
# Safe scripts only
nmap --script safe 192.168.1.1

# Vulnerability detection
nmap --script vuln 192.168.1.1

# Service discovery
nmap --script discovery 192.168.1.1

# All but intrusive
nmap --script "default,discovery,safe" 192.168.1.1
```

---

## Output Formats and Reporting

### Default Output

```bash
nmap 192.168.1.1
```

### Saving Output

```bash
# Normal format
nmap -oN output.txt 192.168.1.1

# XML format
nmap -oX output.xml 192.168.1.1

# Grepable format
nmap -oG output.gnmap 192.168.1.1

# All formats
nmap -oA output 192.168.1.1

# Append to file
nmap -oA output 192.168.1.1 >> results.txt
```

### Output Formats Explained

**Normal Format (-oN)**:

```
Starting Nmap at Tue Dec 09 10:30:00 2025
Nmap scan report for 192.168.1.1
Host is up (0.0045s latency).

PORT      STATE    SERVICE
22/tcp    open     ssh
80/tcp    open     http
443/tcp   open     https
3306/tcp  closed   mysql

Nmap done at Tue Dec 09 10:30:05 2025
```

**XML Format (-oX)**:

```xml
<?xml version="1.0"?>
<nmaprun scanner="nmap" args="..." version="7.96">
  <host starttime="1701091800" endtime="1701091805">
    <ports>
      <port protocol="tcp" portid="22">
        <state state="open" reason="syn-ack"/>
        <service name="ssh" product="OpenSSH" version="7.4"/>
      </port>
    </ports>
  </host>
</nmaprun>
```

**Grepable Format (-oG)**:

```
Host: 192.168.1.1 Ports: 22/open/tcp//ssh///, 80/open/tcp//http///, 443/open/tcp//https///
```

---

## Firewall Evasion Techniques

### Fragmentation (-f)

Break packets into fragments:

```bash
# Fragment packets
sudo nmap -f 192.168.1.1

# Larger fragments
sudo nmap --mtu 24 192.168.1.1
```

### Timing and Delays

```bash
# Slow timing template (sneaky)
sudo nmap -T0 192.168.1.1

# Fast timing template
sudo nmap -T5 192.168.1.1
```

**Timing Templates**:

| Template | Timing | Use Case |
|----------|--------|----------|
| -T0 | Paranoid | Very slow, avoid detection |
| -T1 | Sneaky | Slow, IDS evasion |
| -T2 | Polite | Avoid network overload |
| -T3 | Normal | Default (balanced) |
| -T4 | Aggressive | Fast scan |
| -T5 | Insane | Very fast (risky) |

### Source Spoofing

```bash
# Spoof source IP (requires root)
sudo nmap -S 192.168.100.1 192.168.1.1

# Use decoy
sudo nmap -D 192.168.100.1,ME 192.168.1.1
```

### Idle Scan (Zombie Scan)

```bash
# Scan through idle host
sudo nmap -sI 192.168.1.50 192.168.1.1
```

---

## Performance Optimization

### Parallel Processing

```bash
# Set parallel probes
nmap --min-parallelism 100 192.168.1.0/24

# Aggressive parallelism
nmap --max-parallelism 256 192.168.1.0/24
```

### Timeout Adjustment

```bash
# Set timeout between probes
nmap --host-timeout 10m 192.168.1.0/24

# Initial RTT timeout
nmap --initial-rtt-timeout 100ms 192.168.1.1
```

### Optimization Example

```bash
# Fast scan of large network
nmap -T4 --max-parallelism 256 -p 1-10000 192.168.1.0/24 --top-ports 1000
```

---

## Practical Examples and Workflows

### Example 1: Complete Host Assessment

```bash
# Comprehensive scan of single host
sudo nmap -A -sV -p- --script discovery 192.168.1.1 -oA complete_scan

# Breakdown:
# -A          = Aggressive (OS, version, scripts, traceroute)
# -sV         = Service version detection
# -p-         = All 65535 ports
# --script discovery = Discovery scripts
# -oA         = All output formats
```

### Example 2: Network-Wide Scan

```bash
# Quick network inventory
nmap -sn 192.168.1.0/24 -oN network_inventory.txt

# Detailed assessment of subnet
sudo nmap -sS -p 1-10000 --top-ports 1000 -sV -O 192.168.1.0/24 -oA subnet_scan
```

### Example 3: Service Detection

```bash
# Find web servers
nmap -p 80,443,8080,8443 -sV 192.168.1.0/24 | grep http

# Find SSH servers
nmap -p 22 -sV 192.168.1.0/24 | grep ssh

# Find database servers
nmap -p 3306,5432,1433,27017 -sV 192.168.1.0/24
```

### Example 4: Vulnerability Scanning

```bash
# Scan for common vulnerabilities
nmap --script vuln 192.168.1.1 -oA vuln_scan

# SSL vulnerabilities
nmap --script ssl-cert,ssl-enum-ciphers -p 443 192.168.1.1

# SMB vulnerabilities
nmap --script smb-vuln* 192.168.1.1
```

### Example 5: OS Fingerprinting

```bash
# Identify all operating systems
sudo nmap -O --osscan-guess 192.168.1.0/24

# OS with version
sudo nmap -O -sV 192.168.1.0/24 | grep "OS:"
```

---

## Detection and Defense

### Detecting Nmap Scans

**Network Level**:

```bash
# Monitor for SYN scans
sudo tcpdump -i eth0 'tcp[tcpflags] & tcp-syn != 0'

# Monitor for unusual flag combinations
sudo tcpdump -i eth0 'tcp[tcpflags] & tcp-fin != 0'

# Monitor for fragments
sudo tcpdump -i eth0 'ip[6:2] & 0x1fff != 0'
```

**Wireshark Filters**:

```
# SYN scan
tcp.flags.syn == 1 and tcp.flags.ack == 0

# FIN scan
tcp.flags.fin == 1

# Xmas scan
tcp.flags.fin == 1 and tcp.flags.psh == 1 and tcp.flags.urg == 1

# UDP scan
udp and ip.dst == 192.168.1.1
```

**IDS/IPS Detection**:

- Suricata, Snort detect port scanning
- High-rate connection attempts trigger alerts
- Unusual flag combinations indicate nmap
- Rapid port transitions indicate scanning

### Defense Mechanisms

**Firewall Rules**:

```bash
# Block unusual flag combinations
iptables -A INPUT -p tcp --tcp-flags FPU FPU -j DROP
iptables -A INPUT -p tcp --tcp-flags SYN,RST SYN,RST -j DROP

# Rate limiting
iptables -A INPUT -p tcp --syn -m limit --limit 1/s -j ACCEPT
iptables -A INPUT -p tcp --syn -j DROP

# Block fragments
iptables -A INPUT -f -j DROP
```

**IDS/IPS Configuration**:

```
1. Enable port scan detection
2. Alert on unusual TCP flags
3. Monitor for fragmentation
4. Track connection rates
5. Alert on rapid port attempts
```

---

## Security and Ethical Considerations

### Legal Implications

**Port Scanning Without Authorization**:

- ✗ **Illegal in many jurisdictions** (Computer Fraud and Abuse Act - CFAA)
- ✗ **May violate service terms**
- ✗ **Can be considered intrusion attempt**
- ✗ **Criminal charges possible**

**Legal Use Cases**:

- ✓ **Authorized penetration testing** (written approval)
- ✓ **Internal network assessment** (own systems)
- ✓ **Bug bounty programs** (within scope)
- ✓ **Security research** (academic/approved)

### Responsible Use

1. **Get Written Authorization**: Signed approval for specific targets
2. **Define Scope**: Clear list of what can be scanned
3. **Limit Impact**: Use appropriate timing templates (-T3)
4. **Document Everything**: Keep detailed logs
5. **Report Findings**: Professional incident reporting
6. **Respect Targets**: Don't disrupt operations
7. **Follow Policy**: Honor authorized scope

### Professional Ethics

Penetration testers must:

- ✓ Maintain confidentiality
- ✓ Stay within authorized scope
- ✓ Avoid unnecessary damage
- ✓ Document all activities
- ✓ Report responsibly
- ✓ Get explicit permission
- ✓ Use minimal force
- ✓ Preserve evidence

---

## Summary and Best Practices

### Key Capabilities

1. **Host Discovery**: Identify live hosts
2. **Port Scanning**: Multiple scanning methods
3. **Service Detection**: Identify services and versions
4. **OS Fingerprinting**: Determine operating systems
5. **Script Automation**: NSE for advanced tasks
6. **Vulnerability Detection**: Find misconfigurations
7. **Firewall Testing**: Probe firewall rules
8. **Multiple Output Formats**: Integration with other tools

### When Nmap is Useful

✓ **Appropriate Uses**:
- Authorized penetration testing
- Network inventory
- Security assessment
- Compliance auditing
- Incident response
- Firewall testing

✗ **Inappropriate Uses**:
- Unauthorized scanning
- Competitive intelligence
- Criminal activity
- Port scanning without permission
- Network disruption

### Best Practices

1. **Get Authorization**: Written approval required
2. **Document Targets**: Clear scope definition
3. **Use Appropriate Timing**: Don't overload networks
4. **Combine Tools**: Use with other reconnaissance tools
5. **Analyze Results**: Look for anomalies
6. **Report Findings**: Professional documentation
7. **Follow Up**: Verify vulnerabilities
8. **Educate Stakeholders**: Explain findings

### Typical Penetration Test Workflow

```
1. Reconnaissance
   └─ Passive information gathering

2. Host Discovery
   └─ nmap -sn to identify live hosts

3. Port Scanning
   └─ nmap -sS for open ports

4. Service Detection
   └─ nmap -sV to identify services

5. OS Fingerprinting
   └─ nmap -O for operating systems

6. Vulnerability Assessment
   └─ nmap --script vuln for vulnerabilities

7. Analysis
   └─ Correlate findings

8. Reporting
   └─ Document discoveries

9. Remediation
   └─ Recommend fixes
```

### Common Scan Scenarios

**Quick Network Scan**:

```bash
nmap -sn 192.168.1.0/24
```

**Standard Audit**:

```bash
sudo nmap -sS -sV -O -p 1-10000 192.168.1.0/24
```

**Full Assessment**:

```bash
sudo nmap -A -p- --script vuln 192.168.1.1
```

**Fast Scan**:

```bash
nmap -T4 --top-ports 1000 192.168.1.0/24
```

**Stealthy Scan**:

```bash
sudo nmap -T1 -f --mtu 24 -p 1-1000 192.168.1.1
```

### Next Steps

- Master basic scanning techniques
- Learn service detection and fingerprinting
- Study NSE scripts and customization
- Practice on authorized networks
- Get certified (OSCP, CEH)
- Develop custom scripts
- Study firewall detection/evasion
- Conduct authorized penetration tests
- Document all activities professionally
- Follow responsible disclosure practices
