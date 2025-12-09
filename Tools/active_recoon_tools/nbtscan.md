# NBTSCAN: A Comprehensive Guide to NetBIOS Network Discovery

## Table of Contents
1. [Introduction](#introduction)
2. [NetBIOS Protocol Fundamentals](#netbios-protocol-fundamentals)
3. [How NBTSCAN Works](#how-nbtscan-works)
4. [Installation and Setup](#installation-and-setup)
5. [Basic Syntax and Usage](#basic-syntax-and-usage)
6. [Command-Line Options Reference](#command-line-options-reference)
7. [Core Enumeration Techniques](#core-enumeration-techniques)
8. [Output Formats](#output-formats)
9. [Practical Usage Examples](#practical-usage-examples)
10. [Advanced Scanning Techniques](#advanced-scanning-techniques)
11. [Integration with Other Tools](#integration-with-other-tools)
12. [Troubleshooting](#troubleshooting)
13. [Limitations and Alternatives](#limitations-and-alternatives)
14. [Security and Ethical Considerations](#security-and-ethical-considerations)

---

## Introduction

**nbtscan** is a specialized command-line tool designed for scanning IP networks and enumerating **NetBIOS name information** from Windows and Samba systems. Unlike general network scanners, nbtscan focuses specifically on the NetBIOS Name Service protocol running on UDP port 137.

### Key Characteristics

- **NetBIOS Focused**: Specifically queries the NetBIOS Name Service (port 137)
- **Rapid Scanning**: Fast enumeration of NetBIOS name information
- **Computer Discovery**: Identifies computer names, workgroups, and domains
- **User Enumeration**: Reveals logged-in users on discovered systems
- **MAC Address Identification**: Shows hardware addresses (with -m flag)
- **Multiple Output Formats**: Default, verbose, /etc/hosts, lmhosts, script-friendly
- **Range Scanning**: Can scan IP ranges or individual addresses
- **Batch Processing**: Read targets from files for automation
- **Lightweight**: Single binary, minimal dependencies

### Primary Use Cases

- **Network Inventory**: Discover all Windows machines on a network segment
- **Security Assessment**: Identify Windows systems for vulnerability assessment
- **Network Reconnaissance**: Map network topology and devices
- **User Discovery**: Find logged-in users on target systems
- **Workgroup Identification**: Determine domain/workgroup structure
- **VLAN Mapping**: Identify devices in network segments
- **Network Troubleshooting**: Verify NetBIOS services are functional
- **Compliance Auditing**: Verify networked device inventory

### Limitations

- **Windows/Samba Only**: Only detects systems with NetBIOS enabled
- **Local Network**: Works best on same network segment (broadcast range)
- **Modern Systems**: Disabled on Windows 10/11 by default (can be re-enabled)
- **Easily Detected**: NetBIOS scanning generates obvious traffic patterns
- **No Credential Discovery**: Cannot obtain passwords or hashes
- **Not Stealth**: NetBIOS queries are easily recognized
- **Single Protocol**: Limited to NetBIOS (port 137)

---

## NetBIOS Protocol Fundamentals

### What is NetBIOS?

**NetBIOS** (Network Basic Input/Output System) is a legacy network protocol primarily used by Windows systems for:

- Computer name resolution (name-to-IP mapping)
- Network printer/share discovery
- Workgroup/domain identification
- Broadcast messaging
- Network services advertisement

### Protocol Stack

```
┌──────────────────────────────────────┐
│ Application Layer (NetBIOS Services) │
│ ├─ Name Service (UDP 137)            │
│ ├─ Datagram Service (UDP 138)        │
│ └─ Session Service (TCP 139)         │
├──────────────────────────────────────┤
│ Transport Layer (UDP/TCP)            │
├──────────────────────────────────────┤
│ Internet Layer (IPv4)                │
├──────────────────────────────────────┤
│ Link Layer (Ethernet)                │
└──────────────────────────────────────┘

KEY: nbtscan focuses on Name Service (UDP 137)
```

### NetBIOS Query/Response

**NetBIOS Name Query (from nbtscan)**:

```
┌─────────────────────────────────────────┐
│ Ethernet Frame                          │
│ ├─ Source MAC: scanner MAC              │
│ ├─ Dest MAC: ff:ff:ff:ff:ff:ff (BC)    │
│ └─ Type: IP                             │
├─────────────────────────────────────────┤
│ IP Header                               │
│ ├─ Source IP: scanner IP                │
│ ├─ Dest IP: 255.255.255.255 (broadcast)│
│ └─ Protocol: UDP                        │
├─────────────────────────────────────────┤
│ UDP Header                              │
│ ├─ Source Port: random ephemeral port  │
│ ├─ Dest Port: 137 (NetBIOS Name Service)
│ └─ Checksum                             │
├─────────────────────────────────────────┤
│ NetBIOS Name Query Packet               │
│ ├─ Transaction ID                       │
│ ├─ Query Type                           │
│ ├─ Name to Query: "*" (all names)      │
│ └─ Query Flags                          │
└─────────────────────────────────────────┘
```

**NetBIOS Response (from target)**:

```
Query: "What NetBIOS names do you have?"

Response:
  Computer Name: WORKSTATION01
  Workgroup: CORPORATE
  Domain Master: DC01
  Logged-in User: JSMITH
  Service Types: File Server, Workstation
  MAC Address: 00:11:22:33:44:55
```

### NetBIOS Name Suffixes

Each NetBIOS name includes a one-byte suffix indicating the service type:

| Suffix | Meaning | Example |
|--------|---------|---------|
| `<00>` | Workstation/Computer | COMPUTER<00> |
| `<03>` | Messenger Service | COMPUTER<03> |
| `<20>` | File Server Service | COMPUTER<20> |
| `<1B>` | Domain Master Browser | DOMAIN<1B> |
| `<1D>` | Master Browser | WORKGROUP<1D> |
| `<1E>` | Browser Service Elections | WORKGROUP<1E> |
| `<00>` GROUP | Domain/Workgroup Name | CORPORATE<00> |

### NetBIOS Name Characteristics

```
Format: COMPUTERNAME<suffix>

Examples:
  WORKSTATION01<00>    (Computer name)
  ADMINISTRATOR<03>    (Logged-in user)
  CORPORATE<00>        (Workgroup/Domain)
  DC01<1B>            (Domain Master Browser)

Maximum Length: 15 characters (NetBIOS limit)
```

---

## How NBTSCAN Works

### Operational Model

```
┌──────────────────────────────────┐
│ User Command                     │
│ nbtscan 192.168.1.0/24          │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ Parse Arguments                  │
│ ├─ Network range                 │
│ ├─ Output format                 │
│ ├─ Timeout values                │
│ └─ Other options                 │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ Generate IP List                 │
│ 192.168.1.0 - 192.168.1.255     │
│ (256 addresses for /24)          │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ For Each IP Address              │
│                                  │
│ 1. Create NetBIOS query packet  │
│ 2. Set query type (*=all names) │
│ 3. Construct UDP packet         │
│ 4. Send to target IP:137        │
│ 5. Start listening for response │
│                                  │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ Receive Responses                │
│                                  │
│ For each response:               │
│ 1. Decode NetBIOS data          │
│ 2. Extract names/suffixes       │
│ 3. Parse MAC address            │
│ 4. Identify user/domain         │
│ 5. Store in results             │
│                                  │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ Format Output                    │
│                                  │
│ Based on options (-v, -e, etc)  │
│ Display results to user         │
└──────────────────────────────────┘
```

### Scanning Strategy

**Sequential Approach**:

```
nbtscan 192.168.1.0/24

Queries sent:
  192.168.1.1   → Waiting up to 1000ms
  192.168.1.2   → Waiting up to 1000ms
  192.168.1.3   → Waiting up to 1000ms
  ...
  192.168.1.254 → Waiting up to 1000ms
  192.168.1.255 → Waiting up to 1000ms

Results aggregated and displayed
```

**Timeout Mechanism**:

- Default timeout: 1 second per IP
- If response received before timeout: Move to next IP
- If timeout expires without response: IP marked non-responsive
- Can adjust with `-t` option

### Speed Factors

**Factors Affecting Scan Speed**:

1. **Number of Targets**: 254 addresses in /24 = scan time × 254
2. **Timeout**: 1000ms default (adjust with `-t`)
3. **Retransmits**: Number of retry attempts (adjust with `-m`)
4. **Bandwidth Control**: `-b` option to throttle (for slow links)
5. **Network Response Time**: Actual time for responses to arrive

**Example Timing**:

```
Scan: nbtscan 192.168.1.0/24 (256 addresses)
Default timeout: 1000ms per IP

Calculation:
  256 IPs × 1 second = 256 seconds (~4.3 minutes)

With optimization:
  -t 500 (500ms timeout): 128 seconds (~2 minutes)
  -t 100 (100ms timeout): 25.6 seconds (faster but risky)
```

---

## Installation and Setup

### Linux Installation

**Kali Linux** (Pre-installed):

```bash
nbtscan --help
```

**Ubuntu/Debian**:

```bash
sudo apt update
sudo apt install nbtscan
```

**Fedora/RHEL/CentOS**:

```bash
sudo dnf install nbtscan
```

**Arch Linux**:

```bash
sudo pacman -S nbtscan
```

### Alternative: nbtscan-unixwiz

Enhanced version with additional features:

```bash
sudo apt install nbtscan-unixwiz
```

### From Source

```bash
# Download source code
wget http://www.unixwiz.net/tools/nbtscan-1.7.2.tar.gz
tar xzf nbtscan-1.7.2.tar.gz
cd nbtscan-1.7.2

# Compile
./configure
make
sudo make install
```

### Verification

```bash
# Check version
nbtscan --help

# Test scan on localhost
nbtscan 127.0.0.1

# Test scan on network
sudo nbtscan 192.168.1.0/24
```

---

## Basic Syntax and Usage

### General Command Structure

```bash
nbtscan [options] [IP_RANGE | HOSTNAME]
```

### IP Range Formats

nbtscan accepts multiple range formats:

```bash
# CIDR notation
nbtscan 192.168.1.0/24      # All IPs from .0 to .255

# IP range with dash
nbtscan 192.168.1.1-254     # From .1 to .254

# Single IP
nbtscan 192.168.1.100

# Hostname
nbtscan example.com

# From file
nbtscan -f iplist.txt
```

### Most Common Commands

| Command | Purpose |
|---------|---------|
| `nbtscan 192.168.1.0/24` | Scan entire subnet |
| `nbtscan -r 192.168.1.0/24` | Scan with local port 137 (Win95) |
| `nbtscan -v 192.168.1.0/24` | Verbose output (all names) |
| `nbtscan -e 192.168.1.0/24` | /etc/hosts format output |
| `nbtscan -s : 192.168.1.0/24` | Script-friendly (colon-separated) |
| `nbtscan -f targets.txt` | Scan IPs from file |
| `nbtscan -t 500 192.168.1.0/24` | 500ms timeout |

---

## Command-Line Options Reference

### Essential Options

| Option | Purpose | Example |
|--------|---------|---------|
| `-r` | Use local port 137 (Win95 compatibility) | `nbtscan -r 192.168.1.0/24` |
| `-v` | Verbose output (all names received) | `nbtscan -v 192.168.1.1` |
| `-d` | Dump packets (debug mode) | `nbtscan -d 192.168.1.1` |
| `-e` | /etc/hosts format | `nbtscan -e 192.168.1.0/24` |
| `-l` | lmhosts format | `nbtscan -l 192.168.1.0/24` |
| `-t timeout` | Timeout in milliseconds (default 1000) | `nbtscan -t 500 192.168.1.0/24` |
| `-b bandwidth` | Bandwidth throttling in bps | `nbtscan -b 5000 192.168.1.0/24` |
| `-s separator` | Script-friendly output separator | `nbtscan -s : 192.168.1.0/24` |
| `-h` | Human-readable service names | `nbtscan -v -h 192.168.1.1` |
| `-m retransmits` | Number of retransmit attempts | `nbtscan -m 2 192.168.1.1` |
| `-f filename` | Read IPs from file | `nbtscan -f targets.txt` |
| `-q` | Quiet mode (suppress banners) | `nbtscan -q 192.168.1.0/24` |

### Advanced Options

| Option | Purpose |
|--------|---------|
| `-n` | No inverse name lookups |
| `-p port` | Specify UDP port (default 137) |
| `-o outfile` | Send results to output file |
| `-H` | Generate HTTP headers |

---

## Core Enumeration Techniques

### 1. Basic Network Scan

Discover all NetBIOS-enabled devices:

```bash
sudo nbtscan 192.168.1.0/24
```

**Output Example**:

```
Scanning 255 addresses, timeout is 1000 ms, RTT is approximately 92 ms

192.168.1.1   *SMBSERVER         SHARING          Ethernet 00:11:22:33:44:55
192.168.1.5   WORKSTATION01      Ethernet         00:aa:bb:cc:dd:01
192.168.1.10  LAPTOP-USER        JOHN_SMITH       Ethernet 00:aa:bb:cc:dd:02
192.168.1.20  PRINTER-NETWORK    CORPORATE        Ethernet 00:aa:bb:cc:dd:03
```

**Information Revealed**:
- IP Address
- Computer Name (or share name)
- Workgroup/Domain (if domain controller)
- Logged-in User (sometimes)
- MAC Address (with -m)

### 2. Verbose Enumeration

Get all NetBIOS names for detailed analysis:

```bash
sudo nbtscan -v 192.168.1.1
```

**Output Example**:

```
192.168.1.1:
  WORKSTATION01        <00> UNIQUE
  WORKSTATION01        <03> UNIQUE
  WORKSTATION01        <20> UNIQUE
  ADMINISTRATOR        <03> UNIQUE
  CORPORATE            <00> GROUP
  CORPORATE            <1D> UNIQUE
  CORPORATE            <1E> GROUP
  ..__MSBROWSE__.      <01> GROUP
```

**Name Suffix Meanings**:
- `<00>` = Computer name
- `<03>` = Messenger/logged-in user
- `<20>` = File server service
- `<1D>` = Master browser
- `<1E>` = Browser elections

### 3. User Discovery

Identify logged-in users:

```bash
sudo nbtscan -v 192.168.1.0/24 | grep "<03>"
```

**Output Example**:

```
192.168.1.5   JOHN_SMITH       <03> Messenger Service
192.168.1.10  JANE_DOE         <03> Messenger Service
192.168.1.15  ADMIN_USER       <03> Messenger Service
```

Users are shown with `<03>` suffix (Messenger Service).

### 4. Domain/Workgroup Mapping

Identify organizational structure:

```bash
sudo nbtscan -v 192.168.1.0/24 | grep -E "<00> GROUP|<1D> UNIQUE"
```

**Output Example**:

```
192.168.1.1   CORPORATE        <00> GROUP
192.168.1.1   CORPORATE        <1D> UNIQUE (Domain Master Browser)
192.168.1.10  ENGINEERING      <00> GROUP
192.168.1.10  ENGINEERING      <1D> UNIQUE (Master Browser)
```

---

## Output Formats

### 1. Default Format

```bash
nbtscan 192.168.1.0/24
```

**Output**:

```
IP Address        Computer Name    User Name        MAC Address
192.168.1.1      SERVER01         SHARING          00:11:22:33:44:55
192.168.1.5      LAPTOP01         JOHN_SMITH       00:aa:bb:cc:dd:01
```

### 2. Verbose Format (-v)

```bash
nbtscan -v 192.168.1.1
```

**Output**:

```
192.168.1.1:
  WORKSTATION01        <00> UNIQUE  - Workstation Service
  WORKSTATION01        <03> UNIQUE  - Messenger Service
  WORKSTATION01        <20> UNIQUE  - File Server Service
  ADMINISTRATOR        <03> UNIQUE  - Logged-in User
```

### 3. /etc/hosts Format (-e)

```bash
nbtscan -e 192.168.1.0/24
```

**Output** (compatible with /etc/hosts):

```
192.168.1.1    SERVER01.local
192.168.1.5    LAPTOP01.local
192.168.1.10   WORKSTATION01.local
```

Can be appended to /etc/hosts:

```bash
sudo nbtscan -e 192.168.1.0/24 >> /etc/hosts
```

### 4. lmhosts Format (-l)

```bash
nbtscan -l 192.168.1.0/24
```

**Output** (Windows-compatible lmhosts format):

```
192.168.1.1     SERVER01
192.168.1.5     LAPTOP01
192.168.1.10    WORKSTATION01
```

### 5. Script-Friendly Format (-s)

```bash
nbtscan -s : 192.168.1.0/24
```

**Output** (colon-separated, easy to parse):

```
192.168.1.1:SERVER01:00:UNIQUE
192.168.1.5:LAPTOP01:00:UNIQUE
192.168.1.10:WORKSTATION01:03:UNIQUE
```

Can be parsed with tools like awk, sed, or Python:

```bash
nbtscan -s : 192.168.1.0/24 | cut -d: -f1,2 | sort -u
```

---

## Practical Usage Examples

### Example 1: Basic Network Discovery

Discover all computers on network:

```bash
sudo nbtscan 192.168.1.0/24
```

### Example 2: Identify Servers

Find file servers and domain controllers:

```bash
sudo nbtscan -v 192.168.1.0/24 | grep -E "<20>|<1B>|<1D>"
```

### Example 3: User Enumeration

Find all logged-in users:

```bash
sudo nbtscan -v 192.168.1.0/24 | grep "<03>" | awk '{print $1, $2}' | sort -u
```

**Output**:

```
192.168.1.5 JOHN_SMITH
192.168.1.10 JANE_DOE
192.168.1.15 ADMIN_USER
```

### Example 4: Create Network Inventory

Generate /etc/hosts entries:

```bash
sudo nbtscan -e 192.168.1.0/24 > network_inventory.txt
```

### Example 5: Scan Multiple Subnets

```bash
for subnet in 192.168.1.0 192.168.2.0 192.168.3.0; do
    echo "=== Scanning $subnet/24 ==="
    sudo nbtscan $subnet/24
done
```

### Example 6: Export to CSV Format

```bash
sudo nbtscan -s , 192.168.1.0/24 > scan_results.csv
```

**CSV Output**:

```
IP Address,Computer Name,User,MAC Address
192.168.1.1,SERVER01,SHARING,00:11:22:33:44:55
192.168.1.5,LAPTOP01,JOHN_SMITH,00:aa:bb:cc:dd:01
```

### Example 7: Fast Timeout Scan

Reduce timeout for faster scanning:

```bash
sudo nbtscan -t 500 192.168.1.0/24
```

Scans twice as fast but may miss slow responders.

### Example 8: Scan Specific Hosts

From a target list file:

```bash
# Create target file
cat > targets.txt << 'EOF'
192.168.1.1
192.168.1.5
192.168.1.10
192.168.1.20
EOF

# Scan targets
sudo nbtscan -f targets.txt
```

---

## Advanced Scanning Techniques

### Continuous Monitoring

Monitor network changes over time:

```bash
#!/bin/bash
# Monitor NetBIOS names daily

LOGDIR="/var/log/nbtscan"
mkdir -p $LOGDIR

while true; do
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    sudo nbtscan -q 192.168.1.0/24 > $LOGDIR/scan_$TIMESTAMP.txt
    
    # Compare with previous scan if exists
    if [ -f "$LOGDIR/previous.txt" ]; then
        echo "=== New Hosts ==="
        diff $LOGDIR/previous.txt $LOGDIR/scan_$TIMESTAMP.txt | grep ">"
    fi
    
    cp $LOGDIR/scan_$TIMESTAMP.txt $LOGDIR/previous.txt
    sleep 3600  # Scan every hour
done
```

### Parallel Scanning

Scan multiple subnets simultaneously:

```bash
#!/bin/bash
# Scan multiple subnets in parallel

SUBNETS="192.168.1.0/24 192.168.2.0/24 192.168.3.0/24 192.168.4.0/24"

for subnet in $SUBNETS; do
    sudo nbtscan -q $subnet > scan_$subnet.txt &
done

wait
echo "All scans complete"
```

### Domain/Workgroup Analysis

Map organizational structure:

```bash
#!/bin/bash
# Analyze domain structure

echo "Domains/Workgroups found:"
sudo nbtscan -v 192.168.1.0/24 | grep -E "<00> GROUP" | \
    awk '{print $2}' | sort -u

echo ""
echo "Master Browsers:"
sudo nbtscan -v 192.168.1.0/24 | grep -E "<1D> UNIQUE" | \
    awk '{print $1, $2}'
```

### Service Detection

Identify service types by suffix:

```bash
#!/bin/bash
# Service type analysis

echo "=== Workstations (<00> UNIQUE) ==="
sudo nbtscan -v 192.168.1.0/24 | grep "<00> UNIQUE"

echo ""
echo "=== File Servers (<20> UNIQUE) ==="
sudo nbtscan -v 192.168.1.0/24 | grep "<20> UNIQUE"

echo ""
echo "=== Master Browsers (<1D> UNIQUE) ==="
sudo nbtscan -v 192.168.1.0/24 | grep "<1D> UNIQUE"
```

---

## Integration with Other Tools

### With Nmap

Combine nbtscan for quick discovery, nmap for detailed scanning:

```bash
# 1. Quick NetBIOS discovery
sudo nbtscan -q 192.168.1.0/24 > netbios_hosts.txt

# 2. Extract IPs from results
cat netbios_hosts.txt | awk '{print $1}' > ips.txt

# 3. Detailed nmap scan
nmap -sV -p 139,445 --iL ips.txt
```

### With enum4linux

Enumerate SMB shares after nbtscan discovery:

```bash
# 1. Find SMB servers
sudo nbtscan -v 192.168.1.0/24 | grep "<20>" | awk '{print $1}' > smb_servers.txt

# 2. Enumerate each server
while read ip; do
    echo "=== Enumerating $ip ==="
    enum4linux -a $ip
done < smb_servers.txt
```

### With CrackMapExec

Test credentials on discovered hosts:

```bash
# 1. Discover hosts
sudo nbtscan -q 192.168.1.0/24 | awk '{print $1}' > targets.txt

# 2. Test common credentials
crackmapexec smb targets.txt -u admin -p password
```

### With Metasploit

Use nbtscan results in Metasploit:

```bash
# 1. Generate host list
sudo nbtscan -q 192.168.1.0/24 | awk '{print $1}' > hosts.txt

# 2. Import into msfconsole
msfconsole
> workspace create netbios_scan
> import hosts.txt
> hosts
```

---

## Troubleshooting

### Issue: Permission Denied

**Problem**: "Operation not permitted" or "Permission denied"

**Solution**: Run with sudo

```bash
sudo nbtscan 192.168.1.0/24
```

### Issue: No Responses

**Possible Causes**:
1. NetBIOS disabled on targets
2. Firewall blocking port 137
3. Wrong network range
4. No NetBIOS services on network

**Troubleshooting**:

```bash
# Check if port 137 is reachable
nmap -p 137 192.168.1.0/24

# Try specific host
nbtscan 192.168.1.1

# Increase timeout
nbtscan -t 2000 192.168.1.0/24
```

### Issue: Slow Scanning

**Solution 1: Reduce timeout**

```bash
nbtscan -t 500 192.168.1.0/24  # 500ms instead of 1000ms
```

**Solution 2: Scan specific range**

```bash
nbtscan 192.168.1.1-100  # Only first 100 addresses
```

**Solution 3: Use bandwidth throttling**

```bash
nbtscan -b 50000 192.168.1.0/24  # 50kbps throttle
```

### Issue: Incomplete Results

**Cause**: Some hosts didn't respond within timeout

**Solution**: Increase timeout and retransmits

```bash
nbtscan -t 2000 -m 2 192.168.1.0/24
```

### Issue: False Positives

**Possible Cause**: Samba servers responding differently

**Solution**: Verify with nmap or direct connection

```bash
nmap -p 139,445 -sV 192.168.1.1
```

---

## Limitations and Alternatives

### nbtscan Limitations

1. **Windows/Samba Only**: No detection of other systems
2. **Noisy**: Easy to detect on network
3. **Requires Open Port 137**: Firewalls can block
4. **Modern Systems**: Disabled by default on Windows 10/11
5. **No Authentication**: Cannot access restricted info
6. **Limited Scope**: Only works on local network segment

### Alternatives

**nmblookup** (Samba tool):

```bash
# Lookup single host
nmblookup -A 192.168.1.1

# Find workgroup
nmblookup -M -- -
```

**nmap** (More comprehensive):

```bash
# NetBIOS enumeration script
nmap -p 137 --script nbstat.nse 192.168.1.0/24

# SMB enumeration
nmap -p 445 --script smb-enum-shares.nse 192.168.1.0/24
```

**enum4linux** (SMB-focused):

```bash
# Complete SMB enumeration
enum4linux -a 192.168.1.1
```

**CrackMapExec** (Modern SMB recon):

```bash
# Scan and gather info
crackmapexec smb 192.168.1.0/24
```

**Samba Net** (Samba utilities):

```bash
# Lookup NetBIOS
net lookup 192.168.1.1
```

---

## Security and Ethical Considerations

### Legal Implications

**NetBIOS Scanning**:

- ✓ **Legal for authorized testing** (with written permission)
- ✓ **Permitted on own systems** and authorized networks
- ✗ **Illegal without authorization** (unauthorized access)
- ✗ **May violate terms of service** on third-party networks
- ✗ **Privacy concerns** (user identification)

### Responsible Use

1. **Get Written Authorization**: Signed approval for network assessment
2. **Scope Definition**: Clear definition of what can be scanned
3. **Notification**: Inform stakeholders of testing
4. **Documentation**: Keep detailed logs
5. **Minimize Impact**: Don't disrupt network operations
6. **Secure Results**: Protect sensitive enumeration data
7. **Professional Conduct**: Report findings professionally

### Detection

Administrators can detect nbtscan activity:

```bash
# Monitor port 137 traffic
sudo tcpdump -i eth0 -n 'udp port 137'

# Check for scanning patterns
sudo netstat -an | grep 137
```

### Defense Mechanisms

Disable NetBIOS to prevent enumeration:

```powershell
# Windows: Disable NetBIOS over TCP/IP
# Settings > Network > Advanced > WINS tab > Disable NetBIOS
```

Or use firewall rules:

```bash
# Block port 137
sudo iptables -A INPUT -p udp --dport 137 -j DROP
```

---

## Summary and Best Practices

### Key Capabilities

1. **Quick Network Discovery**: Find Windows/Samba systems
2. **User Enumeration**: Identify logged-in users
3. **Service Detection**: Identify file servers, browsers
4. **Multiple Output Formats**: Integration with other tools
5. **Batch Scanning**: Process multiple targets/ranges
6. **Fast Enumeration**: Quick reconnaissance

### When nbtscan is Useful

✓ **Appropriate Uses**:
- Network inventory (authorized)
- Authorized penetration testing
- Network troubleshooting
- Active Directory assessment
- Internal security audits
- Vulnerability assessment

✗ **Inappropriate Uses**:
- Unauthorized network scanning
- Privacy invasion
- Competitive intelligence
- Criminal activity
- Unauthorized access attempts

### Best Practices

1. **Get Authorization**: Written approval required
2. **Document Findings**: Keep detailed records
3. **Combine Tools**: Use with nmap, enum4linux, etc.
4. **Analyze Results**: Look for anomalies
5. **User Investigation**: Follow up on users found
6. **Service Mapping**: Identify critical systems
7. **Report Professionally**: Comprehensive findings
8. **Respect Privacy**: Handle user information carefully

### Typical Workflow

```
1. Network Scope Definition
   └─ Determine network ranges to scan

2. Initial nbtscan
   └─ Quick discovery of NetBIOS systems

3. Analysis
   ├─ Identify users
   ├─ Map workgroups
   └─ Find file servers

4. Detailed Assessment
   └─ Use enum4linux, nmap, etc.

5. Vulnerability Assessment
   └─ Check for misconfigurations

6. Reporting
   └─ Document findings

7. Remediation
   └─ Recommend fixes
```

### Next Steps

- Practice on authorized test networks
- Learn NetBIOS protocol fundamentals
- Integrate with other reconnaissance tools
- Develop custom scripts for automation
- Get certified in ethical hacking
- Conduct authorized penetration tests
- Document all activities
- Follow responsible disclosure
