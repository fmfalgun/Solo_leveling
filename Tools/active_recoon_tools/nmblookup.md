# NMBLOOKUP: A Comprehensive Guide to NetBIOS Name Resolution

## Table of Contents
1. [Introduction](#introduction)
2. [NetBIOS Name Resolution Fundamentals](#netbios-name-resolution-fundamentals)
3. [How NMBLOOKUP Works](#how-nmblookup-works)
4. [Installation and Setup](#installation-and-setup)
5. [Basic Syntax and Usage](#basic-syntax-and-usage)
6. [Command-Line Options Reference](#command-line-options-reference)
7. [Name Queries](#name-queries)
8. [Reverse Lookups](#reverse-lookups)
9. [Workgroup and Domain Discovery](#workgroup-and-domain-discovery)
10. [Master Browser Discovery](#master-browser-discovery)
11. [Output Interpretation](#output-interpretation)
12. [Practical Usage Examples](#practical-usage-examples)
13. [Integration with Other Tools](#integration-with-other-tools)
14. [Troubleshooting](#troubleshooting)
15. [Security and Ethical Considerations](#security-and-ethical-considerations)

---

## Introduction

**nmblookup** is a Samba utility for querying NetBIOS names and mapping them to IP addresses. It functions as the NetBIOS equivalent of DNS lookup tools like `nslookup` or `dig`, but instead of querying DNS servers, it queries the NetBIOS Name Service (NNS) running on UDP port 137 to resolve computer names to IP addresses.

### Key Characteristics

- **NetBIOS Query Tool**: Queries NetBIOS Name Service (port 137)
- **Part of Samba Suite**: Comes with Samba (SMB/CIFS implementation)
- **Lightweight**: Single command-line utility
- **Broadcast Capable**: Can broadcast queries across network
- **Status Lookup**: Retrieve detailed NetBIOS name information
- **Workgroup Discovery**: Find all computers in workgroup
- **Master Browser Detection**: Identify master browsers
- **Reverse Lookup**: Query by IP to get names
- **Minimal Dependencies**: Works with just network connectivity
- **Cross-Platform**: Available on Linux, Unix, Windows

### Primary Use Cases

- **Windows Name Resolution**: Resolve NetBIOS names when DNS unavailable
- **Network Reconnaissance**: Discover systems on local network
- **SMB Enumeration**: Identify Samba/Windows servers
- **Workgroup Mapping**: Find all systems in workgroup
- **Troubleshooting**: Diagnose NetBIOS name resolution issues
- **Network Inventory**: Build network device list
- **Security Assessment**: Part of authorized penetration testing
- **Legacy Network Support**: Work with older Windows systems
- **Master Browser Detection**: Find network organization

### Limitations

- **Local Network Only**: Works best on same network segment
- **Legacy Protocol**: NetBIOS disabled on modern Windows by default
- **Easily Detected**: Generates obvious NetBIOS traffic
- **No Authentication**: Cannot access restricted information
- **Broadcast Dependent**: Relies on broadcast/multicast capability
- **Limited Information**: Gets only name service information
- **Single Query**: Each lookup is one query (no bulk operations)

---

## NetBIOS Name Resolution Fundamentals

### Name Resolution Methods

**Three Methods for NetBIOS Resolution**:

```
1. BROADCAST RESOLUTION (Most Common)
   ├─ Client sends broadcast query: "Who has this name?"
   ├─ All hosts receive broadcast
   ├─ Target host responds with IP address
   ├─ Works only on local network segment
   └─ nmblookup uses this method by default

2. WINS SERVER RESOLUTION (Hierarchical)
   ├─ Client queries dedicated WINS server
   ├─ WINS maintains name database
   ├─ Works across network segments
   └─ Requires WINS server configuration

3. LOCAL CACHE/LMHOSTS FILE
   ├─ Checks /etc/lmhosts (Linux) or C:\Windows\System32\drivers\etc\lmhosts (Windows)
   ├─ Pre-configured name mappings
   └─ Static, doesn't require network query
```

### NetBIOS Query/Response Flow

```
CLIENT                                  NETWORK                              TARGET
  │                                        │                                   │
  ├─ Create NetBIOS query                 │                                   │
  │  (Who is SERVERNAME?)                 │                                   │
  │                                        │                                   │
  ├─ Send broadcast to 255.255.255.255:137 │                                   │
  │  UDP port 137                          │                                   │
  │                                        ├──────────────────────────────────>│
  │                                        │  Broadcast received by all        │
  │                                        │                                   │
  │                                        │  Does target match?               │
  │                                        │  YES ✓                            │
  │                                        │                                   │
  │                                        │<──────────── Unicast Response ────┤
  │                                        │  "Here's my IP: 192.168.1.100"    │
  │                                        │                                   │
  │<───────── Response Received ───────────┤                                   │
  │  192.168.1.100 SERVERNAME<00>         │                                   │
  │                                        │                                   │
  └─ (Timeout after waiting)               │                                   │
```

### NetBIOS Name Format

```
COMPUTERNAME<suffix>

Example: WORKSTATION01<00>

Components:
├─ COMPUTERNAME: Up to 15 characters
└─ <suffix>: One-byte hex value indicating service type

Common Suffixes:
  <00> = Workstation service / Host name
  <03> = Messenger service / Logged-in user
  <20> = File server (LanManager)
  <1B> = Domain Master Browser
  <1D> = Master Browser
  <1E> = Browser Service Elections
  <1F> = Netware/SMB servers
  <33> = NIS domain (NIS TCP service)
```

---

## How NMBLOOKUP Works

### Operational Model

```
┌────────────────────────────────────┐
│ User Command                       │
│ nmblookup SERVERNAME              │
└────────────┬─────────────────────┘
             │
             ▼
┌────────────────────────────────────┐
│ Parse Arguments                    │
│ ├─ Name to lookup                  │
│ ├─ Options (-A, -M, etc)          │
│ └─ Broadcast address               │
└────────────┬─────────────────────┘
             │
             ▼
┌────────────────────────────────────┐
│ Create NetBIOS Query Packet        │
│ ├─ Set name to query               │
│ ├─ Set query type (A_QUERY, etc)  │
│ └─ Set flags (broadcast, recursion)│
└────────────┬─────────────────────┘
             │
             ▼
┌────────────────────────────────────┐
│ Send Broadcast Query               │
│ ├─ Destination: 255.255.255.255   │
│ ├─ Port: 137 (NetBIOS Name Service)│
│ ├─ Wait for responses              │
│ └─ Timeout: 1 second (default)     │
└────────────┬─────────────────────┘
             │
             ▼
┌────────────────────────────────────┐
│ Receive Response(s)                │
│ ├─ Listen on UDP port 137          │
│ ├─ Decode NetBIOS response         │
│ ├─ Extract IP address              │
│ ├─ Extract name/suffix info        │
│ └─ Handle multiple responses       │
└────────────┬─────────────────────┘
             │
             ▼
┌────────────────────────────────────┐
│ Format and Display Result          │
│                                    │
│ "192.168.1.100 SERVERNAME<00>"    │
│                                    │
└────────────────────────────────────┘
```

### Query Types

**nmblookup supports different query types**:

```
NB QUERY (Normal)
  └─ Query for specific NetBIOS name
  └─ Standard hostname lookup

NBSTAT QUERY (-A flag)
  └─ Query for all names (status query)
  └─ Get all registered names on host
  └─ Detailed information about host

WORKGROUP QUERY (-M flag)
  └─ Find master browser for workgroup
  └─ Discovery of network organization

BROADCAST QUERY
  └─ Send query to broadcast address
  └─ All hosts on segment receive
  └─ Target responds unicast

DIRECT QUERY
  └─ Send query to specific IP
  └─ More reliable than broadcast
```

---

## Installation and Setup

### Linux Installation

**Kali Linux** (Pre-installed):

```bash
nmblookup --help
```

**Ubuntu/Debian**:

```bash
sudo apt update
sudo apt install samba samba-common-bin
```

**Fedora/RHEL/CentOS**:

```bash
sudo dnf install samba-client samba-common-tools
```

**Arch Linux**:

```bash
sudo pacman -S samba
```

### macOS Installation

```bash
brew install samba
```

### From Source

```bash
# Download Samba source
wget https://download.samba.org/pub/samba/samba-latest.tar.gz
tar xzf samba-latest.tar.gz
cd samba-*

# Compile
./configure
make
sudo make install
```

### Verification

```bash
# Check installation
which nmblookup

# Check version
nmblookup --version

# Test local query
nmblookup localhost
```

---

## Basic Syntax and Usage

### General Command Structure

```bash
nmblookup [options] [name | IP]
```

### Simplest Usage

**Query single hostname**:

```bash
# Broadcast query for hostname
nmblookup SERVERNAME

# Result: "192.168.1.100 SERVERNAME<00>"
```

### Most Common Commands

| Command | Purpose |
|---------|---------|
| `nmblookup COMPUTER` | Query single host |
| `nmblookup -A 192.168.1.1` | Status query (all names) |
| `nmblookup -M -- -` | Find workgroup master browser |
| `nmblookup -B 192.168.1.255 COMPUTER` | Query with specific broadcast |
| `nmblookup -I 192.168.1.1 COMPUTER` | Query specific IP |
| `nmblookup -S 192.168.1.1` | List shares |
| `nmblookup -d2 COMPUTER` | Debug mode (verbose) |

---

## Command-Line Options Reference

### Essential Options

| Option | Purpose | Example |
|--------|---------|---------|
| `-A` | Status lookup (query all names) | `nmblookup -A 192.168.1.1` |
| `-M` | Find master browser | `nmblookup -M -- -` |
| `-S` | List shares | `nmblookup -S 192.168.1.1` |
| `-I ip` | Query this IP address | `nmblookup -I 192.168.1.1 COMP` |
| `-B broadcast` | Broadcast address | `nmblookup -B 192.168.1.255 COMP` |
| `-U unicast` | Unicast to specific host | `nmblookup -U 192.168.1.1 COMP` |
| `-d level` | Debug level (0-10) | `nmblookup -d2 COMP` |
| `-T` | TCP queries (not UDP) | `nmblookup -T COMP` |
| `-R` | Set recursion desired | `nmblookup -R COMP` |
| `-r` | Set recursion available | `nmblookup -r COMP` |
| `-s suffix` | Query with specific suffix | `nmblookup -s COMP` |
| `-? or --help` | Display help | `nmblookup -?` |

### Advanced Options

| Option | Purpose |
|--------|---------|
| `-P address` | Preferred WINS server |
| `-m` | Send multiple copies |
| `-n name` | Source NetBIOS name |
| `-q` | Quiet mode |
| `-t timeout` | Query timeout (seconds) |

---

## Name Queries

### Basic Host Lookup

Query for a computer by name:

```bash
# Standard query
nmblookup WORKSTATION01

# Expected output:
# querying WORKSTATION01 on 255.255.255.255
# 192.168.1.10 WORKSTATION01<00>
```

### Specific Suffix Query

Query for specific service type:

```bash
# Query with specific suffix
nmblookup WORKSTATION01<00>     # Workstation service
nmblookup WORKSTATION01<03>     # Messenger (logged-in user)
nmblookup WORKSTATION01<20>     # File server

# Result example:
# 192.168.1.10 WORKSTATION01<20>
```

### Debug Output

Verbose query with debugging information:

```bash
# Level 1 debug
nmblookup -d1 WORKSTATION01

# Level 2 debug (more verbose)
nmblookup -d2 WORKSTATION01

# Output includes:
# - Query packets sent
# - Responses received
# - Timing information
# - Error messages
```

### Unicast Query

Query specific IP instead of broadcast:

```bash
# Direct query to specific IP
nmblookup -U 192.168.1.10 WORKSTATION01

# More reliable than broadcast
# Works even with broadcast disabled

# Result: "192.168.1.10 WORKSTATION01<00>"
```

---

## Reverse Lookups

### Status Lookup (-A)

Get all NetBIOS names for a host:

```bash
# Query all names from IP
nmblookup -A 192.168.1.100

# Output example:
# Looking up status of 192.168.1.100
# WORKSTATION01  <00> - B <ACTIVE>
# WORKSTATION01  <03> - B <ACTIVE>
# WORKSTATION01  <20> - B <ACTIVE>
# CORPORATE      <00> - <GROUP> B <ACTIVE>
# CORPORATE      <1D> - B <ACTIVE>
# ..__MSBROWSE__.<01> - <GROUP> B <ACTIVE>
# MAC Address = 00:11:22:33:44:55
```

**Name Suffix Meanings** in output:

```
<00> = Workstation service (computer name)
<03> = Messenger service (logged-in user)
<20> = File server (LanManager)
<1D> = Master browser (network browser)
<1E> = Browser service elections
<GROUP> = Group/domain name
ACTIVE = Name is actively registered
B = Broadcast (not from WINS)
```

### Reverse Query with Custom IP

```bash
# Query using specific broadcast address
nmblookup -B 192.168.1.255 -A 192.168.1.1

# Query using specific interface
nmblookup -I eth0 -A 192.168.1.1
```

---

## Workgroup and Domain Discovery

### Find Workgroup Master Browser (-M)

Discover master browser for workgroup:

```bash
# Query master browser
nmblookup -M -- -

# Output example:
# querying __MSBROWSE__ on 255.255.255.255
# 192.168.1.1 __MSBROWSE__<01>
# 192.168.1.1 CORPORATE<1D>
```

**What this tells you**:
- Master browser IP: 192.168.1.1
- Workgroup/domain: CORPORATE
- Browser maintains network resource list

### Find All Workgroups

Query for all workgroups:

```bash
# This requires more advanced tools like smbtree
# But nmblookup -M shows master browsers
nmblookup -M -- -

# Combine with other tools:
smbtree          # Lists all workgroups
smbtree -d2      # With debug info
```

---

## Master Browser Discovery

### Locate Master Browser

```bash
# Find master browser
nmblookup -M -- -

# Result shows:
# ├─ Master browser IP
# ├─ Browser name (<1D> suffix)
# └─ Workgroup name
```

### List Network Resources

Master browser maintains list of:

```
├─ All computers in workgroup
├─ Shares offered
├─ Printers
├─ Services
└─ Network topology
```

### Query Master Browser Shares

```bash
# Get shares from master browser
nmblookup -S 192.168.1.1

# Shows all shares advertised
```

---

## Output Interpretation

### Standard Response

```bash
nmblookup WORKSTATION01

# Output:
# 192.168.1.10 WORKSTATION01<00>

# Breakdown:
# ├─ 192.168.1.10 = IP address
# ├─ WORKSTATION01 = NetBIOS name
# └─ <00> = Suffix (workstation service)
```

### Status Response (-A)

```bash
nmblookup -A 192.168.1.10

# Output:
# Looking up status of 192.168.1.10
# WORKSTATION01  <00> - B <ACTIVE>
# WORKSTATION01  <03> - B <ACTIVE>
# WORKSTATION01  <20> - B <ACTIVE>
# ADMIN_USER     <03> - B <ACTIVE>
# CORPORATE      <00> - <GROUP> B <ACTIVE>
# CORPORATE      <1D> - B <ACTIVE>
# CORPORATE      <1E> - <GROUP> B <ACTIVE>
# ..__MSBROWSE__.<01> - <GROUP> B <ACTIVE>
# MAC Address = 00:11:22:33:44:55

# Interpretation:
# Computer Name: WORKSTATION01
# Services: Workstation, File Server
# Logged-in User: ADMIN_USER
# Workgroup: CORPORATE
# Role: Master Browser (<1D>)
# MAC Address: 00:11:22:33:44:55
```

### Error Responses

```bash
# No response (timeout)
nmblookup UNKNOWN_HOST
# Output: (blank or no response)
# Meaning: Host not found or not responding

# ICMP Destination Unreachable
# Meaning: Network unreachable

# Host Unreachable
# Meaning: Target host not accessible

# Timed out
# Meaning: No response within timeout period
```

---

## Practical Usage Examples

### Example 1: Simple Hostname Resolution

Resolve single hostname:

```bash
# Query specific computer
nmblookup JOHN-LAPTOP

# Output:
# querying JOHN-LAPTOP on 255.255.255.255
# 192.168.1.50 JOHN-LAPTOP<00>
```

### Example 2: Full Host Information

Get complete information about host:

```bash
# Get all names registered on host
nmblookup -A 192.168.1.50

# Output shows:
# - Computer name
# - Registered services
# - Logged-in user
# - Network role
# - MAC address
```

### Example 3: Network Discovery

Find all hosts on network:

```bash
#!/bin/bash
# Discover all NetBIOS hosts

for ip in {1..254}; do
    timeout 1 nmblookup -A 192.168.1.$ip 2>/dev/null | grep -i active
done
```

### Example 4: Find Master Browser

Locate network master browser:

```bash
# Find master browser
nmblookup -M -- -

# Output:
# 192.168.1.1 __MSBROWSE__<01>
# 192.168.1.1 ENGINEERING<1D>

# Means: 192.168.1.1 is master browser for ENGINEERING workgroup
```

### Example 5: Debug Network Issues

Troubleshoot NetBIOS resolution:

```bash
# Verbose query
nmblookup -d2 PROBLEMATIC_HOST

# Shows:
# - Query packets sent
# - Responses received
# - Timing information
# - Any errors
```

### Example 6: Query Specific Broadcast Address

```bash
# Use non-standard broadcast address
nmblookup -B 192.168.2.255 SERVER01

# Useful for:
# - Multi-segment networks
# - Non-standard subnets
# - VLAN testing
```

### Example 7: Direct Query to IP

```bash
# Query specific host directly
nmblookup -U 192.168.1.100 WORKSTATION

# Advantages:
# - More reliable (no broadcast needed)
# - Works across network segments (if path exists)
# - Doesn't rely on broadcast capability
```

---

## Integration with Other Tools

### With smbtree

Combine nmblookup with smbtree for network mapping:

```bash
# Show tree structure
smbtree

# Output:
# WORKGROUP
#   \\SERVER01        Computer Name
#   \\SERVER02        Computer Name

# Enhanced with nmblookup:
nmblookup -M -- -           # Find master browser
nmblookup -A SERVER01       # Get detailed info
```

### With nmap

Use nmblookup results in nmap scans:

```bash
# 1. Find NetBIOS hosts
for ip in {1..254}; do
    nmblookup -A 192.168.1.$ip 2>/dev/null | grep -i active | awk '{print $1}' >> hosts.txt
done

# 2. Scan found hosts with nmap
nmap -sV -p 139,445 -iL hosts.txt
```

### With enum4linux

Enumerate SMB after nmblookup discovery:

```bash
# 1. Find SMB servers
nmblookup -A 192.168.1.0/24 | grep "<20>" | awk '{print $1}' > smb_hosts.txt

# 2. Enumerate each
while read ip; do
    enum4linux -a $ip
done < smb_hosts.txt
```

### With crackmapexec

Test credentials on discovered hosts:

```bash
# 1. Find hosts
nmblookup -M -- - > master_browser.txt

# 2. Test access
crackmapexec smb master_browser.txt -u admin -p password
```

---

## Troubleshooting

### Issue: "Connection refused"

**Cause**: NetBIOS service not listening on port 137

**Solution**:

```bash
# Verify NetBIOS is running
sudo systemctl status smbd nmbd

# Start if not running
sudo systemctl start nmbd

# Check port 137
sudo netstat -tulnp | grep 137
```

### Issue: No responses / Timeout

**Possible Causes**:
1. Broadcast disabled
2. Firewall blocking port 137
3. Host not on network
4. NetBIOS disabled on target

**Troubleshooting**:

```bash
# Try direct IP query instead of broadcast
nmblookup -U 192.168.1.1 HOSTNAME

# Check if port 137 is reachable
nmap -p 137 192.168.1.1

# Increase timeout
nmblookup -t 5 HOSTNAME
```

### Issue: Wrong broadcast address

**Problem**: Queries not reaching all hosts

**Solution**:

```bash
# Find correct broadcast address
ifconfig | grep Broadcast

# Use specific broadcast
nmblookup -B 192.168.1.255 HOSTNAME

# Or use interface
nmblookup -I eth0 HOSTNAME
```

### Issue: Mixed results / Multiple IPs

**Problem**: Multiple hosts with same name

```bash
# Query returns multiple results
nmblookup COMMON_NAME

# Use -A flag to see all names
nmblookup -A 192.168.1.1

# Use MAC address to verify
nmblookup -A 192.168.1.2
```

### Issue: "Name is not authoritative"

**Meaning**: Response is cached, not from authoritative source

**Solution**: This is usually fine, but for authoritative info:

```bash
# Query WINS server directly
nmblookup -U wins_server_ip HOSTNAME
```

---

## Security and Ethical Considerations

### Legal Implications

**NetBIOS Queries**:

- ✓ **Legal for authorized testing** (with written approval)
- ✓ **Permitted on own systems** and authorized networks
- ✗ **Illegal without authorization** (unauthorized reconnaissance)
- ✗ **May violate terms of service** on third-party networks
- ✗ **Generates detectable traffic**

### Responsible Use

1. **Get Written Authorization**: Signed approval required
2. **Scope Definition**: Clear list of authorized hosts
3. **Notification**: Inform network administrators
4. **Documentation**: Keep detailed logs
5. **Minimize Impact**: Don't overload network
6. **Secure Results**: Protect sensitive information
7. **Professional Conduct**: Report findings responsibly

### Detection

Administrators can detect nmblookup activity:

```bash
# Monitor NetBIOS queries
sudo tcpdump -i eth0 'udp port 137'

# Check for scanning patterns
sudo netstat -an | grep 137

# Monitor firewall logs
grep "137" /var/log/ufw.log
```

### Defense Mechanisms

Prevent unwanted NetBIOS enumeration:

```bash
# Disable NetBIOS (Windows)
# Settings > Network > Advanced > WINS tab

# Linux firewall rules
sudo iptables -A INPUT -p udp --dport 137 -j DROP
sudo iptables -A INPUT -p udp --dport 138 -j DROP
sudo iptables -A INPUT -p tcp --dport 139 -j DROP
```

---

## Summary and Best Practices

### Key Capabilities

1. **Name Resolution**: Resolve NetBIOS names to IPs
2. **Status Queries**: Get all names from specific host
3. **Workgroup Discovery**: Find network organization
4. **Master Browser Detection**: Identify network browser
5. **Reverse Lookups**: Query by IP to get names
6. **Direct/Broadcast Queries**: Flexible query methods
7. **Detailed Information**: Get service and user info
8. **Troubleshooting**: Diagnose NetBIOS issues

### When nmblookup is Useful

✓ **Appropriate Uses**:
- Authorized network assessment
- Windows network troubleshooting
- Legacy system support
- Network inventory
- SMB enumeration starting point
- Authorized penetration testing

✗ **Inappropriate Uses**:
- Unauthorized network scanning
- Privacy invasion
- Competitive intelligence
- Criminal activity
- Network reconnaissance without permission

### Best Practices

1. **Get Authorization**: Written approval required
2. **Document Activity**: Keep detailed logs
3. **Use with Other Tools**: Combine with nmap, enum4linux, etc.
4. **Analyze Results**: Look for anomalies
5. **Verify Information**: Cross-check with other tools
6. **Report Professionally**: Document findings
7. **Respect Targets**: Don't disrupt operations
8. **Follow Policy**: Stay within authorized scope

### Typical Workflow

```
1. Initial Discovery
   └─ nmblookup -M -- -     (Find master browser)

2. Network Mapping
   └─ nmblookup -A IP       (Get host information)

3. Host Enumeration
   └─ nmblookup HOSTNAME    (Resolve names)

4. Detailed Assessment
   └─ enum4linux, nmap      (More detailed info)

5. Analysis
   └─ Correlate findings

6. Reporting
   └─ Document discoveries

7. Remediation
   └─ Recommend fixes
```

### When to Use nmblookup vs Alternatives

| Tool | Best For | Note |
|------|----------|------|
| **nmblookup** | Quick NetBIOS resolution | Fast, specific lookups |
| **nbtscan** | Network-wide NetBIOS scan | Discovers all hosts |
| **nmap** | Comprehensive scanning | More features, slower |
| **enum4linux** | SMB enumeration | Detailed SMB info |
| **smbtree** | Workgroup browsing | Tree view of network |

### Common Scenarios

**Quick Name Resolution**:

```bash
nmblookup HOSTNAME
```

**Get Host Details**:

```bash
nmblookup -A 192.168.1.1
```

**Find Master Browser**:

```bash
nmblookup -M -- -
```

**Troubleshoot Resolution**:

```bash
nmblookup -d2 HOSTNAME
```

### Next Steps

- Learn NetBIOS protocol fundamentals
- Practice on authorized networks
- Integrate with other reconnaissance tools
- Study Windows network architecture
- Get certified in ethical hacking (OSCP, CEH)
- Conduct authorized security assessments
- Document all testing activities
- Follow responsible disclosure practices
