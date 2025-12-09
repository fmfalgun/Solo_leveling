# DHCP-PROBE: A Comprehensive Guide to Rogue DHCP Server Detection

## Table of Contents
1. [Introduction](#introduction)
2. [Security Context: Rogue DHCP Servers](#security-context-rogue-dhcp-servers)
3. [How DHCP-PROBE Works](#how-dhcp-probe-works)
4. [Installation and Compilation](#installation-and-compilation)
5. [Basic Syntax](#basic-syntax)
6. [Configuration Files](#configuration-files)
7. [Command-Line Options](#command-line-options)
8. [Packet Flavors and Detection Mechanisms](#packet-flavors-and-detection-mechanisms)
9. [Practical Usage Examples](#practical-usage-examples)
10. [Advanced Configuration](#advanced-configuration)
11. [Integration with Alert Systems](#integration-with-alert-systems)
12. [Limitations and Workarounds](#limitations-and-workarounds)
13. [Comparison with Other Tools](#comparison-with-other-tools)
14. [Troubleshooting and Best Practices](#troubleshooting-and-best-practices)

---

## Introduction

**dhcp-probe** (also written as **dhcp_probe**) is a specialized network security tool designed to detect and identify **rogue DHCP and BootP servers** on directly-attached Ethernet networks. Unlike tools that test known servers, dhcp-probe actively searches for unauthorized servers that may be compromising network security.

### Key Characteristics

- **Rogue Server Detection**: Identifies unauthorized DHCP/BootP servers
- **Periodic Probing**: Continuously monitors networks for new servers
- **Broadcast-Based**: Sends multiple flavors of DHCP/BootP requests
- **Filtering Capability**: Ignores known/legitimate servers
- **Alert Integration**: Executes external programs when rogues detected
- **Packet Capture**: Records DHCP traffic to pcap format
- **Enterprise Ready**: Designed for network administrator use

### Primary Use Cases

- **Security Auditing**: Detect unauthorized DHCP servers
- **Network Monitoring**: Continuous rogue server detection
- **Incident Response**: Identify compromised or misbehaving servers
- **Compliance Verification**: Ensure network security policies
- **Network Troubleshooting**: Identify unexpected DHCP responses
- **Multi-VLAN Monitoring**: Track DHCP servers across VLANs

### Typical Security Scenario

A malicious actor or misconfigured device on your network might run an unauthorized DHCP server to:
- Redirect clients to malicious gateways (man-in-the-middle attacks)
- Poison DNS settings to intercept traffic
- Serve incorrect gateway addresses to disrupt network connectivity
- Steal credentials through captive portals
- Deploy malware through compromised boot files

---

## Security Context: Rogue DHCP Servers

### Why Rogue DHCP Servers Are Dangerous

DHCP is a critical infrastructure protocol—every client device depends on it for network configuration. A rogue server can:

**1. Redirect Default Gateway**
```
Legitimate Server: 192.168.1.1 (company firewall)
Rogue Server: 192.168.1.10 (attacker's machine)
Result: Client traffic routed through attacker
```

**2. Poison DNS Settings**
```
Legitimate DNS: 8.8.8.8 (Google)
Rogue DNS: 192.168.1.100 (attacker's DNS forwarder)
Result: Users redirected to fake websites
```

**3. Man-in-the-Middle Position**
```
Client → Rogue DHCP Gateway → Attacker Machine → Real Gateway → Internet
         ↑ All traffic captured here
```

**4. Boot File Injection (BootP)**
```
PXE Client requests boot file
Rogue BootP Server responds with malware-laden boot image
Client downloads and executes attacker's code
```

### Detection Challenges

Rogue servers are difficult to identify because:

- **Broadcast Nature**: Normal DHCP broadcast traffic makes rogues hard to distinguish
- **Standard Responses**: Rogues respond like legitimate servers
- **Configuration Variants**: Different server software responds differently
- **Transient**: Rogues may be temporary (rogue WiFi AP, infected laptop)
- **Layer 2 Issues**: Some switching configurations hide unauthorized servers
- **Spoofing Risk**: Sophisticated attackers can forge MAC addresses

### Why Tools Like dhcp-probe Are Essential

Traditional monitoring cannot reliably detect rogues because:
- Standard DHCP client/server traffic is encrypted
- Packet capture shows many legitimate-looking DHCP responses
- Manual identification requires protocol expertise
- Need for continuous monitoring with rapid alerts

dhcp-probe addresses these gaps by:
- Sending specific probe packets to provoke responses
- Filtering known legitimate servers
- Comparing responses across multiple packet types
- Logging and alerting on all unknowns

---

## How DHCP-PROBE Works

### Core Operating Principle

dhcp-probe implements a **probe cycle** that repeats continuously:

```
┌─────────────────────────────────────────────────────┐
│ DHCP-PROBE PROBE CYCLE                              │
├─────────────────────────────────────────────────────┤
│ 1. Install pcap filter for UDP port 68              │
├─────────────────────────────────────────────────────┤
│ 2. Broadcast DHCP/BootP request packet #1           │
│    ├─ BOOTPREQUEST (BootP clients)                  │
│    ├─ DHCPDISCOVER (DHCP new clients)              │
│    ├─ DHCPREQUEST (DHCP renewals)                  │
│    ├─ DHCPREQUEST with Server ID (broken server)   │
│    ├─ DHCPREQUEST with Requested IP (NAK test)     │
│    └─ DHCPREQUEST in REBINDING state (topology)    │
├─────────────────────────────────────────────────────┤
│ 3. Listen for responses (default: 5 seconds)        │
├─────────────────────────────────────────────────────┤
│ 4. For each response:                               │
│    ├─ Filter: Is it valid (correct CHADDR)?        │
│    ├─ Filter: Is sender a known legal server?      │
│    ├─ Filter: Is sender's MAC in legal list?       │
│    └─ If unknown: LOG, ALERT, CAPTURE              │
├─────────────────────────────────────────────────────┤
│ 5. Remove pcap filter                               │
├─────────────────────────────────────────────────────┤
│ 6. Repeat for each packet flavor                    │
├─────────────────────────────────────────────────────┤
│ 7. Sleep (default: 300 seconds / 5 minutes)         │
├─────────────────────────────────────────────────────┤
│ 8. Return to step 1 (until signal to exit)          │
└─────────────────────────────────────────────────────┘
```

### Packet Filtering Mechanism

The tool uses a multi-stage filtering approach:

**Stage 1: Basic Validation**
- Ignores packets with wrong CHADDR (not responses to our probes)
- Checks hardware type (HTYPE) matches Ethernet (1)
- Validates hardware length (HLEN) is 6 bytes

**Stage 2: Legal Server Whitelist**
- Compares response source IP against `legal_server` list in config
- If IP appears in whitelist, response is ignored
- Unknown IP addresses proceed to logging

**Stage 3: MAC Address Validation (Optional)**
- If `legal_server_ethersrc` statements exist, check Ethernet source MAC
- Unknown MAC addresses trigger alerts even if IP appears legitimate
- This catches MAC spoofing attempts

**Stage 4: Lease Network Analysis (Optional)**
- If response contains non-zero `yiaddr` (offered IP)
- Compares against `lease_network_of_concern` list
- Flags if offered IP falls in legitimate address ranges
- Helps distinguish rogue servers from misconfigured ones

### Packet Structure Sent by dhcp-probe

Each probe packet sent by dhcp-probe has the following structure:

```
Ethernet Layer:
├─ Destination MAC: ff:ff:ff:ff:ff:ff (broadcast)
├─ Source MAC: [configured or interface's MAC]
└─ Type: 0x0800 (IPv4)

IPv4 Layer:
├─ Source IP: 0.0.0.0 (looks like DHCP client)
├─ Destination IP: 255.255.255.255 (broadcast)
├─ TTL: 60 (allows crossing some routers)
├─ Protocol: UDP (17)
└─ Flags: 0 (no fragmentation)

UDP Layer:
├─ Source Port: 68 (BootP client)
├─ Destination Port: 67 (BootP server)
└─ Checksum: Computed

BootP/DHCP Payload (300 bytes):
├─ OP: BOOTREQUEST (1)
├─ HTYPE: Ethernet (1)
├─ HLEN: 6 (MAC address length)
├─ HOPS: 0 (no relay)
├─ XID: 1 (transaction ID, static in probes)
├─ SECS: 0 (client age)
├─ FLAGS: 0x0000
├─ CIADDR: 0.0.0.0 (varies by packet type)
├─ YIADDR: 0.0.0.0
├─ SIADDR: 0.0.0.0
├─ GIADDR: 0.0.0.0
├─ CHADDR: [configured or interface's MAC]
├─ SNAME: [zeros]
├─ FILE: [zeros]
└─ OPTIONS: RFC1048 cookie + DHCP options + END
```

### Multiple Packet "Flavors"

dhcp-probe sends six different packet types in each cycle because different servers respond to different requests:

**1. BOOTPREQUEST (BootP Legacy)**
- Mimics a BootP client asking for boot information
- Provokes older BootP servers
- No DHCP options
- Characteristic: `op = BOOTREQUEST, no DHCP Message Type option`

**2. DHCPDISCOVER**
- Mimics a DHCP client starting up
- Requests an IP address assignment
- Characteristic: `DHCP Message Type = 1 (DISCOVER)`
- Provokes DHCPOFFER responses

**3. DHCPREQUEST with Server Identifier**
- Mimics a client accepting an offer
- Includes a fake "Server Identifier" (default: 10.254.254.254)
- Characteristic: `DHCP Message Type = 3 (REQUEST), includes Server Identifier`
- Provokes DHCPACK responses

**4. DHCPREQUEST without Server Identifier**
- Mimics a client renewing/rebinding
- No Server Identifier (client already has IP)
- Includes "Requested IP Address" (default: 172.31.254.254)
- Characteristic: `DHCP Message Type = 3 (REQUEST), no Server Identifier`
- Provokes DHCPNAK from authoritative servers (tests topology awareness)

**5. DHCPREQUEST in REBINDING State**
- Mimics a client with an assigned IP attempting rebind
- CIADDR field contains topologically wrong IP
- Characteristic: `CIADDR = 172.31.254.254`
- Provokes DHCPNAK from servers aware of network topology

**6. Other Variants (Implementation-Dependent)**
- Some implementations test additional states
- Custom configurations can define additional packet types
- Designed to catch broken or misconfigured servers

### Why Multiple Flavors Matter

Different DHCP servers have different response behavior:

```
Server Type              BOOTREQ   DISCOVER   REQUEST   REQUEST(NAK)   REBIND(NAK)
Standard ISC DHCPD       REPLY     OFFER      ACK       NAK            NAK
Microsoft Windows        REPLY?    OFFER      ACK       NAK            NAK
Broken Server (no state) REPLY     OFFER      OFFER     OFFER          OFFER
Wireless AP              —         OFFER      ACK       —              —
Misconfigured Router     —         —          —         —              —
```

By sending all six variants, dhcp-probe can:
- Detect servers that don't respect proper DHCP state
- Identify non-standard or broken implementations
- Catch servers only responding to certain packet types
- Differentiate legitimate from rogue servers by behavior

---

## Installation and Compilation

### Prerequisites

Before installing dhcp-probe, ensure you have:

**Required Libraries:**
- libpcap (packet capture library)
- libnet (network packet construction)

**Development Tools:**
- GCC compiler
- Make utility
- Standard C library development files

### Installing on Solaris 10 (Original Platform)

Princeton University officially supported Solaris 10 SPARC:

```bash
# Install required packages
pkg install system/header-math
pkg install developer/gcc
pkg install library/libpcap

# Download and extract
cd /tmp
wget https://www.net.princeton.edu/software/dhcp_probe/dhcp_probe-1.3.1.tar.gz
tar xzf dhcp_probe-1.3.1.tar.gz
cd dhcp_probe-1.3.1

# Compile
./configure
make

# Install
sudo make install
# Typically installs to /usr/local/sbin/dhcp_probe
# Configuration to /usr/local/etc/dhcp_probe.cf
```

### Linux Installation (Requires Patching)

dhcp-probe was written for Solaris and requires porting for Linux. Several community patches exist:

**For Ubuntu/Debian (Using Weppelman Patch for 1.2.1):**

```bash
# Install dependencies
sudo apt update
sudo apt install -y \
    build-essential \
    libpcap-dev \
    libnet1-dev \
    wget

# Download original version
cd /tmp
wget https://www.net.princeton.edu/software/dhcp_probe/dhcp_probe-1.2.1.tar.gz
tar xzf dhcp_probe-1.2.1.tar.gz
cd dhcp_probe-1.2.1

# Download and apply Weppelman Linux patch
wget https://www.net.princeton.edu/software/dhcp_probe/dhcp_probe-1.2.1-weppelman-1.diff.txt
patch -p1 < dhcp_probe-1.2.1-weppelman-1.diff.txt

# Configure and compile
./configure
make
sudo make install
```

**For Fedora/RHEL (Using Available Patches):**

```bash
# Install dependencies
sudo dnf install -y \
    gcc \
    make \
    libpcap-devel \
    libnet-devel \
    wget

# Download and patch as above
# Similar process to Ubuntu/Debian
```

### FreeBSD Installation (Using Cristi Klein Patch)

```bash
# Install dependencies
sudo pkg install -y \
    gcc \
    libpcap \
    libnet

# Download and apply patch for FreeBSD 1.2.0
cd /tmp
wget https://www.net.princeton.edu/software/dhcp_probe/dhcp_probe-1.2.0.tar.gz
tar xzf dhcp_probe-1.2.0.tar.gz
cd dhcp_probe-1.2.0

wget https://www.net.princeton.edu/software/dhcp_probe/dhcp_probe-1.2.0-cristi-1.diff.txt
patch -p1 < dhcp_probe-1.2.0-cristi-1.diff.txt

./configure
make
sudo make install
```

### macOS Installation

macOS may require additional libraries:

```bash
# Install dependencies with Homebrew
brew install libpcap libnet

# Compile as above
./configure
make
sudo make install
```

### Verify Installation

```bash
# Check if installed
which dhcp_probe
dhcp_probe -v        # Version (if implemented)
man dhcp_probe       # Manual page (if installed)

# Test basic functionality
sudo dhcp_probe -h   # Display help
```

### Building from Git (Advanced)

If using community-maintained forks:

```bash
git clone https://github.com/[user]/dhcp_probe.git
cd dhcp_probe
autoconf
automake --add-missing
./configure
make
sudo make install
```

---

## Basic Syntax

### Minimal Command

```bash
sudo dhcp_probe [-c config_file] interface_name
```

### Example: Monitor eth0

```bash
sudo dhcp_probe eth0
```

This starts monitoring on interface `eth0` using default configuration.

### Full Syntax

```bash
sudo dhcp_probe [options] interface_name
```

### Command-Line Options

| Option | Argument | Purpose |
|--------|----------|---------|
| `-c` | config_file | Path to configuration file (default: /usr/local/etc/dhcp_probe.cf) |
| `-d` | debuglevel | Debug verbosity level (0-7, higher = more verbose) |
| `-f` | — | Run in foreground (don't daemonize) |
| `-h` | — | Display help message |
| `-l` | log_file | Path to log file output |
| `-o` | capture_file | Write packet captures to pcap file |
| `-p` | pid_file | Write process ID to file (for daemon management) |
| `-Q` | vlan_id | Add 802.1Q VLAN tag to packets |
| `-s` | capture_bufsize | Packet capture buffer size (bytes) |
| `-T` | — | Test mode: parse config and exit |
| `-v` | — | Verbose mode |
| `-w` | cwd | Change working directory (for daemon) |

### Privilege Requirements

**dhcp_probe requires root access** because it needs to:
- Bind to UDP port 68 (privileged port)
- Send raw Ethernet frames with broadcast MAC
- Access network interface drivers
- Read/write system files

```bash
sudo dhcp_probe eth0      # Correct
dhcp_probe eth0           # Fails: permission denied
```

---

## Configuration Files

### Default Configuration Location

```
/usr/local/etc/dhcp_probe.cf      (default, Solaris convention)
/etc/dhcp_probe.cf                (alternative)
~root/dhcp_probe.cf              (if specified with -c)
```

### Basic Configuration Template

```
# dhcp_probe.cf - configuration file for dhcp_probe

# Indicate this is the config file version
config_version: 1

# Legal DHCP/BootP servers (whitelist)
# Any response from an IP NOT listed here is considered rogue
legal_server: 192.168.1.1         # Primary DHCP server
legal_server: 192.168.1.2         # Secondary DHCP server

# Optional: MAC address verification
# If any legal_server_ethersrc is specified, MAC checking is enabled
legal_server_ethersrc: 00:11:22:33:44:55    # Primary MAC
legal_server_ethersrc: 00:11:22:33:44:66    # Secondary MAC

# Networks of concern for offered IP addresses
# Alerts if rogue offers IPs in these ranges
lease_network_of_concern: 192.168.1.0/24   # Production VLAN
lease_network_of_concern: 10.0.0.0/8       # All corporate IPs

# Probe parameters
response_wait_time: 5000          # milliseconds to wait for responses
cycle_time: 300                   # seconds between probe cycles

# Packet generation parameters
chaddr: 00:aa:bb:cc:dd:ee         # Client MAC to use in probes
server_id: 10.254.254.254         # Fake server ID for REQUEST
client_ip_address: 172.31.254.254 # Fake client IP for testing

# Ethernet parameters
ether_src: 00:aa:bb:cc:dd:ee      # Source MAC (if different from chaddr)

# Alert programs (called when rogue detected)
# Arguments: program_name interface source_ip source_ethaddr
alert_program_name: /usr/local/bin/alert_rogue.sh

# Alert program 2 (more flexible interface)
# Uses command-line options: -p program -I interface -i ip -m mac -y yiaddr
alert_program_name2: /usr/local/bin/alert_rogue_v2.sh
```

### Configuration Statement Details

**legal_server Statement**

Specifies IP addresses of known legitimate DHCP/BootP servers:

```
legal_server: 192.168.1.1
legal_server: 192.168.1.2
legal_server: 10.0.1.1
```

Any response from an IP address NOT listed is considered unknown (potential rogue).

**legal_server_ethersrc Statement**

If ANY `legal_server_ethersrc` statements are specified, MAC address checking is enabled:

```
legal_server_ethersrc: 00:11:22:33:44:55
legal_server_ethersrc: 00:11:22:33:44:66
```

Responses with MACs not in this list are treated as unknown.

**lease_network_of_concern Statement**

Marks IP address ranges that should trigger elevated alerts:

```
lease_network_of_concern: 192.168.1.0/24
lease_network_of_concern: 10.0.0.0/8
```

If rogue offers an IP in one of these ranges, the log message notes this. Useful for:
- Identifying if rogue could affect critical networks
- Triggering different alert levels based on severity
- Compliance reporting on credential networks

**response_wait_time**

Milliseconds to wait for responses after sending each probe:

```
response_wait_time: 5000    # 5 seconds (default)
response_wait_time: 3000    # 3 seconds (faster)
response_wait_time: 10000   # 10 seconds (thorough)
```

**cycle_time**

Seconds to wait between complete probe cycles:

```
cycle_time: 300         # 5 minutes (default)
cycle_time: 60          # 1 minute (frequent checking)
cycle_time: 3600        # 1 hour (light monitoring)
```

**chaddr**

Client hardware (MAC) address to use in probe packets:

```
chaddr: 00:aa:bb:cc:dd:ee      # Use this MAC

# If not specified, dhcp_probe uses the interface's actual MAC
```

Useful for:
- Testing with specific MAC vendors (e.g., simulate Apple devices)
- Monitoring server behavior for different MAC types
- Avoiding potential MAC filtering by servers

**server_id and client_ip_address**

Fake values to use in DHCP packets:

```
server_id: 10.254.254.254           # Used in REQUEST with Server ID
client_ip_address: 172.31.254.254   # Used in REQUEST/REBIND CIADDR
```

These should be:
- Non-routable or topologically wrong for your network
- Unlikely to match any actual IP on your network
- Different from legitimate DHCP servers/clients

**ether_src**

Ethernet source MAC (if different from CHADDR):

```
ether_src: 00:11:22:33:44:55
```

Most installations use the interface's actual MAC.

**alert_program_name**

External program to execute when rogue detected:

```
alert_program_name: /usr/local/bin/alert_rogue.sh
```

Invoked as:
```bash
/usr/local/bin/alert_rogue.sh dhcp_probe eth0 192.168.1.100 00:aa:bb:cc:dd:ee
```

Arguments (positional):
1. Program name (dhcp_probe)
2. Interface name (eth0)
3. Rogue IP address (192.168.1.100)
4. Rogue MAC address (00:aa:bb:cc:dd:ee)

**alert_program_name2**

Enhanced alert program with command-line options:

```
alert_program_name2: /usr/local/bin/alert_rogue_v2.sh
```

Invoked with options:
```bash
/usr/local/bin/alert_rogue_v2.sh \
    -p dhcp_probe \
    -I eth0 \
    -i 192.168.1.100 \
    -m 00:aa:bb:cc:dd:ee \
    -y 192.168.1.50         # If offered IP in lease_network_of_concern
```

The `-y` option is only included if rogue offered an IP in a concern network.

---

## Command-Line Options

### Option: -c config_file

Specify alternate configuration file:

```bash
sudo dhcp_probe -c /etc/dhcp_probe.conf eth0
sudo dhcp_probe -c /tmp/test.conf eth0
```

If not specified, default locations are searched:
1. `/usr/local/etc/dhcp_probe.cf`
2. `/etc/dhcp_probe.cf`

### Option: -d debuglevel

Set debug verbosity (0-7):

```bash
sudo dhcp_probe -d 0 eth0         # Silent
sudo dhcp_probe -d 3 eth0         # Normal
sudo dhcp_probe -d 7 eth0         # Maximum verbosity
```

Higher numbers produce more diagnostic output to stderr.

### Option: -f foreground

Run in foreground instead of daemonizing:

```bash
sudo dhcp_probe -f eth0
```

Useful for:
- Testing configuration
- Debugging output
- Running in containers/systemd
- Development and diagnostics

### Option: -h help

Display help message and exit:

```bash
sudo dhcp_probe -h
```

### Option: -l log_file

Specify log file for output:

```bash
sudo dhcp_probe -l /var/log/dhcp_probe.log eth0
sudo dhcp_probe -l /tmp/probe.log -f eth0
```

Log file contains:
- Rogue server detections
- Error messages
- Status changes
- Alert program executions

### Option: -o capture_file

Write packet captures to pcap file:

```bash
sudo dhcp_probe -o /tmp/dhcp_responses.pcap eth0
```

Captured file can be analyzed with:

```bash
tcpdump -r /tmp/dhcp_responses.pcap -n
wireshark /tmp/dhcp_responses.pcap
```

**Important**: Opening capture file truncates previous content. Move old files before restarting:

```bash
sudo mv /tmp/dhcp_responses.pcap /tmp/dhcp_responses.pcap.bak
sudo dhcp_probe -o /tmp/dhcp_responses.pcap eth0
```

### Option: -p pid_file

Write process ID to file:

```bash
sudo dhcp_probe -p /var/run/dhcp_probe.pid eth0
```

Useful for:
- Daemon management (systemd, supervisor)
- Process tracking scripts
- Clean shutdown

### Option: -Q vlan_id

Add 802.1Q VLAN tag to packets:

```bash
sudo dhcp_probe -Q 100 eth0        # Send packets tagged with VLAN 100
```

Use when:
- Operating system doesn't automatically tag packets
- Testing specific VLANs on a trunk interface
- Need explicit VLAN isolation

**Warning**: Don't use if OS automatically tags packets—double-tagging breaks transmission.

### Option: -s capture_bufsize

Packet capture buffer size in bytes:

```bash
sudo dhcp_probe -s 65536 eth0      # 64 KB buffer
sudo dhcp_probe -s 262144 eth0     # 256 KB buffer
```

Larger buffers capture more packets before dropping, but use more memory.

### Option: -T test

Test configuration and exit (don't run):

```bash
sudo dhcp_probe -T -c /etc/dhcp_probe.cf eth0
```

Useful for:
- Validating configuration syntax
- Checking for errors before deployment
- CI/CD pipelines
- Safe configuration changes

### Option: -v verbose

Enable verbose output:

```bash
sudo dhcp_probe -v eth0
sudo dhcp_probe -v -l /var/log/dhcp_probe.log eth0
```

### Option: -w cwd

Change working directory (for daemon):

```bash
sudo dhcp_probe -w /var/lib/dhcp_probe eth0
```

Useful when:
- Running as unprivileged user (still requires root for probe)
- Organizing daemon state files
- Working in chroot environments

---

## Packet Flavors and Detection Mechanisms

### Understanding the Six Packet Types

dhcp-probe sends six different packet types to provoke responses from different server implementations.

### Packet Type 1: BootP Request (BOOTPREQUEST)

**Purpose**: Detect legacy BootP servers

**Characteristics**:
- No DHCP options field
- Pure BootP format (RFC 951)
- Mimics diskless workstation requesting boot file

**Packet Structure**:
```
op: BOOTREQUEST (1)
DHCP Options: None (BootP-only)
```

**Expected Responses**:
- **Legitimate BootP Server**: BOOTPREPLY with SIADDR and FILE fields
- **DHCP Server**: May reply with DHCPOFFER or ignore
- **Rogue Server**: Any response with correct CHADDR

**Detection Use**: Finds old BootP servers that newer DHCP tools miss

---

### Packet Type 2: DHCP Discover (DHCPDISCOVER)

**Purpose**: Detect DHCP servers willing to assign addresses to unknown clients

**Characteristics**:
- DHCP Message Type: 1 (DISCOVER)
- Requests: Client Identifier (MAC)
- Broadcast from 0.0.0.0 (client without IP)

**Packet Structure**:
```
DHCP Message Type: 1 (DISCOVER)
Client Identifier: 01:chaddr
```

**Expected Responses**:
- **Legitimate DHCP Server**: DHCPOFFER with proposed IP
- **Broken Server**: May ignore (too picky about clients)
- **Rogue Server**: DHCPOFFER accepting unknown client

**Detection Use**: Standard detection—finds most configured servers

---

### Packet Type 3: DHCP Request with Server Identifier

**Purpose**: Test server response to explicit server selection

**Characteristics**:
- DHCP Message Type: 3 (REQUEST)
- Server Identifier: 10.254.254.254 (fake, non-routable)
- Client Identifier: 01:chaddr
- Requested IP: 172.31.254.254 (fake, topologically wrong)

**Packet Structure**:
```
DHCP Message Type: 3 (REQUEST)
Server Identifier: 10.254.254.254
Requested IP Address: 172.31.254.254
Client Identifier: 01:chaddr
```

**Expected Responses**:
- **Legitimate Server**: DHCPACK if it's the specified server, ignores otherwise
- **Broken Server**: May ACK despite wrong Server Identifier
- **Rogue Server**: Unknown behavior, likely responds

**Detection Use**: Catches broken servers that don't respect Server Identifier field

---

### Packet Type 4: DHCP Request without Server Identifier

**Purpose**: Test server behavior during renewal phase

**Characteristics**:
- DHCP Message Type: 3 (REQUEST)
- Requested IP: 172.31.254.254 (topologically wrong)
- No Server Identifier (client already has server)
- Client Identifier: 01:chaddr

**Packet Structure**:
```
DHCP Message Type: 3 (REQUEST)
Requested IP Address: 172.31.254.254
Client Identifier: 01:chaddr
(No Server Identifier)
```

**Expected Responses**:
- **Aware Server**: DHCPNAK (IP not on this network)
- **Broken Server**: May ACK anyway
- **Wrong Network Server**: Ignores (not authoritative)

**Detection Use**: Tests topology awareness—can detect misconfigured servers

---

### Packet Type 5: DHCP Request in REBINDING State

**Purpose**: Test server topology awareness during rebinding

**Characteristics**:
- DHCP Message Type: 3 (REQUEST)
- CIADDR: 172.31.254.254 (topologically wrong current IP)
- Client Identifier: 01:chaddr
- No Requested IP field

**Packet Structure**:
```
DHCP Message Type: 3 (REQUEST)
CIADDR: 172.31.254.254
Client Identifier: 01:chaddr
```

**Expected Responses**:
- **Aware Server**: DHCPNAK (not on this network)
- **Careless Server**: DHCPACK (doesn't validate IP)
- **Rogue Server**: Any response indicates potential threat

**Detection Use**: Detects servers that don't validate client IPs during binding

---

### Why Subtle Differences Matter

Consider this detection scenario:

```
Network: 192.168.1.0/24

Packet Type 1 (BOOTREQUEST):
├─ Legitimate BootP Server: Responds (expected)
├─ Misconfigured Router: Might respond (unexpected)
└─ Real DHCP Server: Ignores (expected)

Packet Type 2 (DHCPDISCOVER):
├─ All DHCP Servers: Respond (expected)
└─ BootP-Only Server: Ignores (expected)

Packet Type 3 (REQUEST with fake Server ID):
├─ Server 10.254.254.254: Ignores (expected)
├─ Broken Server: Might ACK (rogue behavior)
└─ Legitimate Server: Ignores (expected)

Packet Type 5 (REBINDING with wrong IP):
├─ Topology-Aware Server: DHCPNAK (expected)
├─ Topology-Unaware Server: DHCPACK (rogue behavior)
└─ Correct Network Server: DHCPNAK (expected)
```

By analyzing response patterns across all six packet types, dhcp-probe can:
- Identify broken/misconfigured servers
- Detect spoofed servers
- Find topology-unaware DHCP implementations
- Locate wildly inappropriate server configurations

---

## Practical Usage Examples

### Example 1: Basic Monitoring

Monitor a single interface for rogue servers:

```bash
# Create minimal config
cat > /etc/dhcp_probe.cf << 'EOF'
config_version: 1
legal_server: 192.168.1.1
response_wait_time: 5000
cycle_time: 300
EOF

# Start monitoring
sudo dhcp_probe -l /var/log/dhcp_probe.log eth0

# View logs
sudo tail -f /var/log/dhcp_probe.log
```

**Output when rogue detected**:
```
2025-01-15 14:32:10 dhcp_probe[12345]: Response from unknown server 192.168.1.42 (00:aa:bb:cc:dd:ee)
```

### Example 2: Rapid Detection with Short Cycle

For security audit or incident response:

```bash
# Aggressive detection: 10-second cycles
cat > /tmp/dhcp_probe_fast.cf << 'EOF'
config_version: 1
legal_server: 192.168.1.1
legal_server: 192.168.1.2
response_wait_time: 3000      # 3 seconds wait
cycle_time: 10                # Check every 10 seconds
EOF

# Run in foreground with high verbosity
sudo dhcp_probe -v -d 5 -c /tmp/dhcp_probe_fast.cf \
    -l /tmp/dhcp_probe_rapid.log eth0
```

### Example 3: Multi-VLAN Monitoring

Monitor multiple VLANs from a single host:

```bash
# Create logical interfaces for each VLAN
sudo ip link add link eth0 name eth0.100 type vlan id 100
sudo ip link add link eth0 name eth0.200 type vlan id 200
sudo ip link add link eth0 name eth0.300 type vlan id 300

# Bring them up
sudo ip link set eth0.100 up
sudo ip link set eth0.200 up
sudo ip link set eth0.300 up

# Run dhcp_probe on each VLAN
sudo dhcp_probe -c /etc/dhcp_probe_vlan100.cf -l /var/log/dhcp_probe_vlan100.log eth0.100 &
sudo dhcp_probe -c /etc/dhcp_probe_vlan200.cf -l /var/log/dhcp_probe_vlan200.log eth0.200 &
sudo dhcp_probe -c /etc/dhcp_probe_vlan300.cf -l /var/log/dhcp_probe_vlan300.log eth0.300 &
```

### Example 4: Integration with Alert System

Send alerts when rogues detected:

```bash
# Alert script
cat > /usr/local/bin/alert_rogue_handler.sh << 'EOF'
#!/bin/bash
# Arguments: program_name interface source_ip source_ethaddr

PROGRAM=$1
INTERFACE=$2
SOURCE_IP=$3
SOURCE_MAC=$4

# Send alert email
echo "Rogue DHCP Server Detected!" | \
  mail -s "SECURITY: Rogue DHCP on $INTERFACE" \
       -c "security@example.com" \
       admin@example.com \
       <<< "
Program: $PROGRAM
Interface: $INTERFACE
Rogue IP: $SOURCE_IP
Rogue MAC: $SOURCE_MAC
Time: $(date)
Hostname: $(hostname)
"

# Log to syslog
logger -t dhcp_probe -p security.alert \
    "Rogue DHCP detected: IP=$SOURCE_IP MAC=$SOURCE_MAC on $INTERFACE"

# Create incident ticket (example)
curl -X POST https://tickets.example.com/api/incidents \
    -H "Authorization: Bearer $API_TOKEN" \
    -d "{\"type\": \"security\", \"rogue_ip\": \"$SOURCE_IP\"}"
EOF

chmod +x /usr/local/bin/alert_rogue_handler.sh

# Configuration with alert program
cat > /etc/dhcp_probe.cf << 'EOF'
config_version: 1
legal_server: 192.168.1.1
alert_program_name: /usr/local/bin/alert_rogue_handler.sh
response_wait_time: 5000
cycle_time: 300
EOF

# Run dhcp_probe
sudo dhcp_probe eth0
```

### Example 5: Packet Capture for Forensics

Capture all responses to analyze server behavior:

```bash
# Capture to pcap file
sudo dhcp_probe -c /etc/dhcp_probe.cf \
                -o /tmp/dhcp_responses.pcap \
                -l /var/log/dhcp_probe.log \
                eth0

# Later, analyze with tcpdump
tcpdump -r /tmp/dhcp_responses.pcap -v

# Or with Wireshark
wireshark /tmp/dhcp_responses.pcap
```

### Example 6: Systemd Service Unit

Run dhcp_probe as a system service:

```bash
# Create service file
cat > /etc/systemd/system/dhcp-probe.service << 'EOF'
[Unit]
Description=DHCP Rogue Server Detection
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/local/sbin/dhcp_probe -c /etc/dhcp_probe.cf eth0
Restart=always
RestartSec=10
User=root
StandardOutput=journal
StandardError=journal
SyslogIdentifier=dhcp-probe

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable dhcp-probe.service
sudo systemctl start dhcp-probe.service

# Monitor
sudo journalctl -u dhcp-probe -f
```

### Example 7: Configuration Validation

Test config before deployment:

```bash
# Validate syntax
sudo dhcp_probe -T -c /etc/dhcp_probe.cf eth0

# Output if valid:
# (no output, returns 0)

# Output if invalid:
# dhcp_probe: error in config file line 5: unknown statement
```

---

## Advanced Configuration

### Lease Networks of Concern

Mark critical IP ranges that require immediate alerting:

```
config_version: 1

legal_server: 192.168.1.1
legal_server: 192.168.1.2

# If rogue offers IPs in these ranges, extra alert
lease_network_of_concern: 192.168.1.0/24    # Production network
lease_network_of_concern: 10.0.0.0/8        # All corporate IPs
lease_network_of_concern: 172.16.0.0/12     # Private networks
```

When rogue offers an IP matching these ranges, the log includes the offered IP:

```
Response from unknown server 192.168.1.100 (00:aa:bb:cc:dd:ee)
  Offered IP 192.168.1.50 in configured Lease Network of Concern 192.168.1.0/24
```

### Enhanced Alert Program (alert_program_name2)

More flexible alert script using command-line options:

```bash
cat > /usr/local/bin/alert_v2.sh << 'EOF'
#!/bin/bash

while [[ $# -gt 0 ]]; do
    case $1 in
        -p) PROGRAM="$2"; shift 2 ;;
        -I) INTERFACE="$2"; shift 2 ;;
        -i) ROGUE_IP="$2"; shift 2 ;;
        -m) ROGUE_MAC="$2"; shift 2 ;;
        -y) OFFERED_IP="$2"; shift 2 ;;
        *) shift ;;
    esac
done

# Determine alert level based on offered IP
if [ -n "$OFFERED_IP" ]; then
    SEVERITY="CRITICAL"
    REASON="Offered IP in concern range: $OFFERED_IP"
else
    SEVERITY="HIGH"
    REASON="Rogue detected but offering non-critical IP"
fi

# Custom handling
logger -p security.alert \
    "[$SEVERITY] Rogue DHCP: IP=$ROGUE_IP MAC=$ROGUE_MAC Interface=$INTERFACE - $REASON"

# Send alert
mail -s "[$SEVERITY] Rogue DHCP Detected" security@example.com <<< \
    "Interface: $INTERFACE
Rogue IP: $ROGUE_IP
Rogue MAC: $ROGUE_MAC
Offered IP: ${OFFERED_IP:-None in concern range}
Time: $(date)
Severity: $SEVERITY
Reason: $REASON"
EOF

chmod +x /usr/local/bin/alert_v2.sh

# Configure to use it
cat >> /etc/dhcp_probe.cf << 'EOF'
alert_program_name2: /usr/local/bin/alert_v2.sh
lease_network_of_concern: 192.168.1.0/24
lease_network_of_concern: 10.0.0.0/8
EOF
```

### MAC Address Whitelisting

Enable MAC address checking for even stricter validation:

```
config_version: 1

legal_server: 192.168.1.1
legal_server_ethersrc: 00:11:22:33:44:55

legal_server: 192.168.1.2
legal_server_ethersrc: 00:11:22:33:44:66

# Now ANY response from an unknown MAC is treated as rogue
# Even if IP matches legal_server list
```

This catches:
- MAC spoofing attacks
- IP address takeover
- Server replacement attacks

### Custom Packet Parameters

Adjust probe packets for testing specific scenarios:

```
config_version: 1

# Use specific MAC addresses for probes
chaddr: 08:00:27:f3:27:23          # Mimic VirtualBox VM

# Ethernet source (if different)
ether_src: 00:11:22:33:44:55       # Use specific source MAC

# Fake server/client IPs (must be topologically wrong)
server_id: 10.254.254.254           # Fake server
client_ip_address: 172.31.254.254   # Fake client IP
```

---

## Integration with Alert Systems

### Nagios/Icinga Integration

Create a Nagios plugin that runs dhcp_probe and checks for rogues:

```bash
cat > /usr/lib/nagios/plugins/check_rogue_dhcp.sh << 'EOF'
#!/bin/bash
# Nagios plugin for dhcp_probe

INTERFACE=${1:-eth0}
CONFIG_FILE=${2:-/etc/dhcp_probe.cf}
TEMP_LOG=$(mktemp)

# Run dhcp_probe briefly
timeout 30 dhcp_probe -f -c "$CONFIG_FILE" \
    -l "$TEMP_LOG" \
    "$INTERFACE" 2>/dev/null &

sleep 10  # Let it run a bit

# Check for rogue detection
if grep -q "Response from unknown server" "$TEMP_LOG"; then
    ROGUE=$(grep "Response from unknown server" "$TEMP_LOG" | head -1)
    echo "CRITICAL: Rogue DHCP detected - $ROGUE"
    rm -f "$TEMP_LOG"
    exit 2
else
    echo "OK: No rogue DHCP servers detected"
    rm -f "$TEMP_LOG"
    exit 0
fi
EOF

chmod +x /usr/lib/nagios/plugins/check_rogue_dhcp.sh

# Add to Nagios configuration
cat > /etc/nagios/objects/dhcp_probe.cfg << 'EOF'
define service {
    service_description    Rogue DHCP Detection
    host_name            network-monitor
    check_command        check_rogue_dhcp!eth0!/etc/dhcp_probe.cf
    check_interval       5
    retry_interval       1
    max_check_attempts   3
    notification_options w,c
}
EOF
```

### Prometheus Integration

Export dhcp_probe metrics:

```bash
cat > /usr/local/bin/dhcp_probe_exporter.py << 'EOF'
#!/usr/bin/env python3
import subprocess
import time
import sys
from prometheus_client import start_http_server, Gauge, Counter

rogue_servers_detected = Gauge('dhcp_probe_rogues_detected', 
                               'Number of rogue DHCP servers detected',
                               ['interface'])
probe_errors = Counter('dhcp_probe_errors_total',
                       'Total dhcp_probe execution errors',
                       ['interface'])

def run_dhcp_probe(interface, config_file):
    try:
        result = subprocess.run(
            ['dhcp_probe', '-f', '-c', config_file, interface],
            timeout=30,
            capture_output=True,
            text=True
        )
        
        rogue_count = result.stdout.count('Response from unknown server')
        rogue_servers_detected.labels(interface=interface).set(rogue_count)
        
    except subprocess.TimeoutExpired:
        probe_errors.labels(interface=interface).inc()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        probe_errors.labels(interface=interface).inc()

if __name__ == '__main__':
    start_http_server(8000)
    
    while True:
        run_dhcp_probe('eth0', '/etc/dhcp_probe.cf')
        time.sleep(300)  # Check every 5 minutes
EOF

chmod +x /usr/local/bin/dhcp_probe_exporter.py
```

---

## Limitations and Workarounds

### Limitation 1: Broadcast-Based Detection

**Issue**: Only detects servers on the same physical network segment.

**Why**: DHCP broadcasts don't cross routers. Relay agents convert them to unicasts only to known legitimate servers (defeating detection).

**Workaround**: Run dhcp_probe on each network segment:

```bash
# Monitor multiple network segments
for interface in eth0 eth1 eth2; do
    sudo dhcp_probe -c /etc/dhcp_probe.cf \
        -l /var/log/dhcp_probe_${interface}.log \
        "$interface" &
done
```

### Limitation 2: Single Interface

**Issue**: dhcp_probe monitors only one interface at a time.

**Why**: Requires dedicated pcap filter per interface.

**Workaround**: Run multiple instances:

```bash
# One instance per interface
sudo dhcp_probe -p /var/run/dhcp_probe_eth0.pid eth0 &
sudo dhcp_probe -p /var/run/dhcp_probe_eth1.pid eth1 &
sudo dhcp_probe -p /var/run/dhcp_probe_eth2.pid eth2 &
```

Or use logical VLAN interfaces:

```bash
# Create VLAN interfaces
sudo ip link add link eth0 name eth0.100 type vlan id 100
sudo ip link set eth0.100 up

# Monitor VLAN
sudo dhcp_probe eth0.100
```

### Limitation 3: Switch Filtering

**Issue**: Some Ethernet switches filter Layer 2 broadcasts, preventing probe packets from reaching far sides of switch.

**Example**: Cisco Nexus switches may not flood DHCP broadcasts.

**Workaround**: 
- Move dhcp_probe closer to rogue (connect to access port, not trunk)
- Use port mirroring (SPAN) to capture traffic
- Check switch DHCP Snooping configuration
- Verify broadcast flooding is enabled

### Limitation 4: Non-Ethernet Interfaces

**Issue**: dhcp_probe only supports Ethernet (requires LLC layer 2 headers).

**Why**: Uses libnet/pcap for Ethernet frame construction.

**Workaround**: 
- Use VPN/tunnel interfaces with Ethernet emulation
- Create virtual Ethernet interfaces
- For wireless: capture on base station in monitor mode

### Limitation 5: MAC Spoofing by Sophisticated Attackers

**Issue**: Attacker can forge MAC addresses to match legitimate servers.

**Workaround**:
- Use DHCP Snooping at switch level (hardware security)
- Monitor at Layer 2 with spanning tree/port security
- Combine with other security controls (802.1X, DAI)
- Use tools that can't be spoofed (switch port security)

### Limitation 6: Encrypted Control Plane Issues

**Issue**: On some platforms, pcap might not capture loopback or tunneled DHCP.

**Workaround**: Run on physical interface, not logical interface.

---

## Comparison with Other Tools

| Feature | dhcp-probe | nmap | tcpdump | Wireshark | DHCP Snooping |
|---------|-----------|------|---------|-----------|---------------|
| **Purpose** | Rogue detection | Network scanning | Packet capture | Traffic analysis | Hardware security |
| **Method** | Active probing | DHCP DISCOVER | Passive sniffing | Passive analysis | Layer 2 filtering |
| **Finds Rogues** | Yes | Partial | If capturing | If capturing | Yes (automatic) |
| **Continuous** | Yes | Manual | Ongoing | Manual | Always on |
| **Alerts** | Yes | No | No | No | Yes |
| **Configuration** | Required | None | Filters | Filters | Switch config |
| **Accuracy** | High | Medium | Medium | Medium | Very high |
| **Response Time** | Seconds | Minutes | Real-time | Varies | Real-time |
| **Cost** | Free | Free | Free | Free | Hardware cost |
| **Ease of Use** | Medium | Easy | Medium | Easy | Hard |

### When to Use Each Tool

**Use dhcp-probe when:**
- Need automated rogue detection
- Want periodic probing without impact
- Need alerting/integration
- Testing without acquiring leases
- Monitoring over long periods

**Use nmap when:**
- One-time discovery needed
- Want to scan beyond local segment (with relay)
- Need to combine with other port scanning
- More portable (works on Windows)

**Use tcpdump when:**
- Capturing real traffic
- Analyzing legitimate DHCP conversations
- Investigating specific incidents
- Troubleshooting DHCP issues

**Use Wireshark when:**
- GUI-based analysis preferred
- Need detailed packet dissection
- Training/learning DHCP
- Reconstructing DHCP exchanges

**Use DHCP Snooping when:**
- Need hardware-level protection
- Cannot afford to run probes
- Require absolute security
- Have capable switches

---

## Troubleshooting and Best Practices

### Issue: Configuration File Errors

**Problem**: dhcp_probe fails to start due to config file problems.

**Debug**:

```bash
# Test configuration syntax
sudo dhcp_probe -T -c /etc/dhcp_probe.cf eth0

# If invalid, check for common errors
cat /etc/dhcp_probe.cf | grep -n "^"  # Show line numbers

# Common mistakes:
# - Incorrect CIDR notation: 192.168.1/24 (missing .0)
# - Missing colons: legal_server 192.168.1.1
# - Tab vs. space indentation
# - Duplicate statements not allowed in same section
```

### Issue: No Rogue Servers Detected (But Know One Exists)

**Possible Causes**:

1. **Rogue on different network segment** → Run dhcp_probe on that segment
2. **Rogue not responding to probe packets** → Try different packet types
3. **Firewall blocking responses** → Check network ACLs
4. **Switch filtering broadcasts** → Move probe location
5. **Response wait time too short** → Increase `response_wait_time`

**Diagnostic**:

```bash
# Capture all DHCP traffic while running probe
sudo tcpdump -i eth0 'port 67 or port 68' -n

# In another terminal, run probe
sudo dhcp_probe -v eth0

# Compare captured responses with what dhcp_probe reports
```

### Issue: False Positives (Legitimate Server Reported as Rogue)

**Problem**: Known legitimate server reported as unknown.

**Solution**:

```bash
# Find the server's actual IP
sudo tcpdump -i eth0 'port 67' -n | grep OFFER

# Add to legal_server list
echo "legal_server: 192.168.1.42" >> /etc/dhcp_probe.cf

# Verify configuration
sudo dhcp_probe -T -c /etc/dhcp_probe.cf eth0

# Restart dhcp_probe
sudo systemctl restart dhcp-probe
```

### Issue: Alert Program Not Executing

**Debug**:

```bash
# Verify alert script is executable
ls -l /usr/local/bin/alert_rogue.sh
# Should show: -rwxr-xr-x

# Check script syntax
bash -n /usr/local/bin/alert_rogue.sh

# Add logging to script to verify execution
cat >> /usr/local/bin/alert_rogue.sh << 'EOF'
echo "Alert triggered at $(date)" >> /tmp/alert_debug.log
EOF

# Test alert manually
/usr/local/bin/alert_rogue.sh dhcp_probe eth0 192.168.1.100 00:aa:bb:cc:dd:ee
```

### Issue: High CPU Usage

**Problem**: dhcp_probe consuming significant CPU.

**Causes**:
1. Too-short `cycle_time` (too frequent probing)
2. Too-long `response_wait_time` (waiting too long for responses)
3. Multiple instances running

**Solution**:

```bash
# Check running instances
ps aux | grep dhcp_probe

# Kill duplicates if any
sudo killall dhcp_probe

# Adjust timing in config
cat > /etc/dhcp_probe.cf << 'EOF'
response_wait_time: 3000      # Reduce from 5000
cycle_time: 600               # Increase from 300 (10 min cycles)
EOF

# Restart
sudo systemctl restart dhcp-probe
```

### Best Practice: Configuration Management

Maintain configuration in version control:

```bash
# Store configuration securely
git init /etc/dhcp_probe_configs
cd /etc/dhcp_probe_configs

# Create organization structure
mkdir -p {vlan100,vlan200,vlan300,production,testing}

# Track changes
git add *.cf
git commit -m "DHCP probe configurations for all VLANs"

# Deployment script
cat > deploy_probe_configs.sh << 'EOF'
#!/bin/bash
for config in *.cf; do
    interface=$(basename $config .cf)
    sudo cp $config /etc/dhcp_probe_${interface}.cf
    sudo chown root:root /etc/dhcp_probe_${interface}.cf
    sudo chmod 0600 /etc/dhcp_probe_${interface}.cf
done
EOF
```

### Best Practice: Monitoring Alert Logs

Create a log aggregation system:

```bash
# Centralized syslog forwarding
cat > /etc/rsyslog.d/99-dhcp-probe.conf << 'EOF'
:programname, isequal, "dhcp_probe" @@syslog.central.example.com:514
EOF

# Or use journalctl for systemd
sudo journalctl -u dhcp-probe -f | tee -a /var/log/dhcp_probe_stream.log
```

### Best Practice: Incident Response Playbook

Document response procedures:

```bash
cat > /runbooks/rogue_dhcp_response.md << 'EOF'
# Rogue DHCP Detection Response

## Alert Received
- dhcp_probe detected unknown DHCP server: {IP} ({MAC})
- Time: {timestamp}
- Interface: {interface}

## Immediate Actions (< 5 minutes)
1. Acknowledge alert to team
2. Log incident in ticketing system
3. Attempt to identify source:
   - Ping rogue IP: ping {IP}
   - Run nmap: nmap -sV -A {IP}
   - Check for open DHCP port: sudo nmap -sU -p67 {IP}

## Investigation (5-15 minutes)
1. Isolate interface: sudo ip link set {interface} down
2. Capture traffic: sudo tcpdump -i {interface} -w rogue_dhcp.pcap
3. Verify legitimate servers responding
4. Check switch port for physical access

## Resolution (15+ minutes)
1. Identify source device
2. Disconnect from network
3. Preserve for forensics
4. Notify security team
5. Update legal_server list if false positive

## Post-Incident
1. Review how rogue accessed network
2. Update access controls
3. Conduct vulnerability assessment
4. Document lessons learned
EOF
```

---

## Summary and Key Takeaways

### Critical Capabilities

1. **Automated Rogue Detection**: Continuously searches for unauthorized DHCP servers
2. **Multiple Packet Types**: Tests with six different request types to catch various server misconfigurations
3. **Flexible Filtering**: Whitelist known servers, check MAC addresses, analyze offered IPs
4. **Alert Integration**: Execute custom programs when rogues detected
5. **Evidence Preservation**: Capture packets to pcap for forensic analysis

### Key Limitations

1. **Broadcast-Based**: Only works on local network segments
2. **Single Interface**: Each instance monitors one interface (can run multiple)
3. **No Hardware Security**: Software-based (combine with DHCP Snooping)
4. **Requires Root**: Needs raw socket access

### When to Deploy dhcp-probe

- **Enterprise Networks**: Continuous rogue server detection
- **Sensitive VLANs**: Critical production networks
- **Security Operations**: Part of comprehensive monitoring
- **Compliance**: Meet security audit requirements
- **Incident Response**: Active investigation of DHCP issues

### Recommended Configuration

```
config_version: 1

# List all legitimate DHCP servers
legal_server: 192.168.1.1
legal_server: 192.168.1.2

# Optional MAC verification for added security
legal_server_ethersrc: 00:11:22:33:44:55
legal_server_ethersrc: 00:11:22:33:44:66

# Flag critical network ranges
lease_network_of_concern: 192.168.1.0/24
lease_network_of_concern: 10.0.0.0/8

# Moderate probing (balance between detection and impact)
response_wait_time: 5000
cycle_time: 300

# Alert program for integration
alert_program_name: /usr/local/bin/alert_rogue.sh
```

### Integration Strategy

1. **Identify all legitimate DHCP servers**
2. **Create whitelisted configuration**
3. **Run dhcp_probe on each network segment**
4. **Integrate with existing monitoring/alerting**
5. **Establish incident response procedures**
6. **Regular review of detected servers**
7. **Combine with network-level DHCP Snooping**

### Next Steps

- Evaluate your current DHCP security posture
- Deploy dhcp-probe in test environments first
- Create comprehensive alert procedures
- Document and train security team
- Integrate with SIEM/monitoring systems
- Establish baseline of legitimate servers
- Begin continuous rogue server detection
