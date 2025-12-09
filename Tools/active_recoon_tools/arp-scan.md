# ARP-Scan: A Comprehensive Guide to Network Discovery and Host Enumeration

## Table of Contents
1. [Introduction](#introduction)
2. [How ARP-Scan Works](#how-arp-scan-works)
3. [Installation](#installation)
4. [Basic Syntax](#basic-syntax)
5. [Core Concepts](#core-concepts)
6. [Essential Commands](#essential-commands)
7. [Advanced Options](#advanced-options)
8. [Output Formatting](#output-formatting)
9. [Practical Use Cases](#practical-use-cases)
10. [Performance Optimization](#performance-optimization)
11. [Scripting and Automation](#scripting-and-automation)
12. [Security Considerations](#security-considerations)
13. [Troubleshooting](#troubleshooting)

---

## Introduction

**arp-scan** is a command-line tool designed for network reconnaissance and host discovery on local area networks (LANs). Unlike higher-layer scanning tools (such as Nmap), arp-scan operates at **OSI Layer 2** (Data Link Layer) using the Address Resolution Protocol (ARP), making it exceptionally effective at discovering hosts that might not respond to traditional Layer 3 or Layer 4 scans.

### Key Advantages

- **Firewall Bypass**: Devices cannot block ARP packets without losing network connectivity
- **Non-Routable Protocol**: Works exclusively on local network segments, reducing noise on remote networks
- **Speed**: Extremely fast because ARP is a fundamental layer 2 protocol with minimal overhead
- **MAC Address Identification**: Automatically identifies device vendors using OUI (Organizationally Unique Identifier) databases
- **High Accuracy**: Discovers hosts that might be hidden from ICMP/TCP/UDP scanning

### Limitations

- **Local Network Only**: ARP cannot be routed, so it only works on the local subnet
- **Not Stealth**: ARP traffic is obvious and will be detected by intrusion detection systems (IDS)
- **IPv4 Only**: Does not support IPv6 discovery (which uses NDP instead)

---

## How ARP-Scan Works

### The Address Resolution Protocol (ARP)

ARP is a layer 2 protocol that maps IPv4 addresses (layer 3) to MAC addresses (layer 2). This mapping is essential for network communication on Ethernet networks.

### ARP Request-Response Mechanism

1. **Request Phase**: arp-scan sends an ARP request packet asking "Who has IP address X.X.X.X?"
2. **Broadcast**: The request is broadcast to the Ethernet broadcast address (ff:ff:ff:ff:ff:ff)
3. **Host Response**: Any device with the requested IP address must respond with its MAC address
4. **Recording**: arp-scan captures the response and records the IP-to-MAC mapping
5. **Vendor Lookup**: The MAC address is cross-referenced against OUI databases to identify the device vendor

### Why All Hosts Respond

ARP is a fundamental protocol that IPv4 hosts cannot block:
- Firewalls cannot filter ARP packets without breaking local network communication
- Even if IP-based traffic is blocked, the host must respond to ARP to maintain network connectivity
- This makes arp-scan reliable for complete host discovery on a local segment

### ARP Packet Structure

```
Ethernet Frame Header:
├── Destination MAC: ff:ff:ff:ff:ff:ff (broadcast)
├── Source MAC: [scanner's MAC]
└── Protocol Type: 0x0806 (ARP)

ARP Packet:
├── Hardware Type (ar$hrd): 1 (Ethernet)
├── Protocol Type (ar$pro): 0x0800 (IPv4)
├── Hardware Length (ar$hln): 6 bytes
├── Protocol Length (ar$pln): 4 bytes
├── Operation (ar$op): 1 (Request)
├── Sender MAC (ar$sha): [scanner's MAC]
├── Sender IP (ar$spa): [scanner's IP]
├── Target MAC (ar$tha): 00:00:00:00:00:00 (unknown)
└── Target IP (ar$tpa): [target IP address]
```

---

## Installation

### Linux (Debian/Ubuntu)

```bash
sudo apt install arp-scan
```

### Linux (Fedora/RHEL/CentOS)

```bash
sudo yum install arp-scan
```

### Linux (Arch)

```bash
sudo pacman -S arp-scan
```

### macOS (Homebrew)

```bash
brew install arp-scan
```

### From Source

```bash
git clone https://github.com/royhills/arp-scan.git
cd arp-scan
./configure
make
sudo make install
```

### Verify Installation

```bash
arp-scan --version
arp-scan -h
```

---

## Basic Syntax

### General Command Structure

```bash
arp-scan [options] [targets]
```

### Where `[targets]` Can Be Specified As

- **Single IP**: `192.168.1.5`
- **CIDR Notation**: `192.168.1.0/24` (includes network and broadcast)
- **IP Range**: `192.168.1.1-192.168.1.254`
- **Network with Mask**: `192.168.1.0:255.255.255.0`
- **Local Network**: `--localnet` (auto-generate from current interface)
- **From File**: `--file=targets.txt` (one target per line)

### Privilege Requirements

**arp-scan requires elevated privileges** because it uses raw sockets to send and receive packets:

```bash
sudo arp-scan --localnet
```

Or use capabilities (safer than SUID root):

```bash
sudo setcap cap_net_raw+p /usr/bin/arp-scan
arp-scan --localnet  # Now works without sudo
```

---

## Core Concepts

### Network Interface Selection

arp-scan operates on a specific network interface. By default, it uses the lowest numbered, configured, up interface (excluding loopback).

To view available interfaces:

```bash
ip link show
ifconfig
```

To specify an interface explicitly:

```bash
arp-scan -I eth0 192.168.1.0/24
arp-scan --interface=wlan0 --localnet
```

### Local Network Scanning

The `--localnet` (or `-l`) option automatically generates targets based on the interface's configured IP address and netmask:

```bash
sudo arp-scan --localnet
```

This is equivalent to manually specifying the network. For example, if your interface has IP 10.0.0.106 with netmask 255.255.255.0, this command scans 10.0.0.0-10.0.0.255.

### MAC Address and Vendor Identification

Every Ethernet device has a globally unique MAC address (in theory). The first 24 bits of the MAC address identify the device manufacturer (OUI - Organizationally Unique Identifier). arp-scan includes databases to decode these:

- **ieee-oui.txt**: IEEE OUI registry (vendor database)
- **mac-vendor.txt**: Custom vendor mappings

Example output:

```
192.168.1.1    00:50:56:c0:00:08    VMware, Inc.
192.168.1.2    a4:1f:72:7f:25:bb    Dell Inc.
192.168.1.3    10:60:4b:73:43:de    Hewlett Packard
```

---

## Essential Commands

### 1. Scan Your Local Network

```bash
sudo arp-scan --localnet
```

**Output:**
```
Interface: eth0, datalink type: EN10MB (Ethernet)
Starting arp-scan 1.9.9 with 256 hosts
192.168.1.1    00:50:56:c0:00:08    VMware, Inc.
192.168.1.5    a4:1f:72:7f:25:bb    Dell Inc.
192.168.1.10   10:60:4b:73:43:de    Hewlett Packard
3 packets received by filter, 0 packets dropped by kernel
Ending arp-scan 1.9.9: 256 hosts scanned in 2.327 seconds (110.01 hosts/sec)
3 responded
```

### 2. Scan a Specific Subnet

```bash
sudo arp-scan -I eth0 192.168.1.0/24
sudo arp-scan -I eth0 10.0.0.1-10.0.0.254
sudo arp-scan -I eth0 10.0.0.0:255.255.255.0
```

### 3. Quiet Mode (Minimal Output)

```bash
sudo arp-scan --localnet -q
```

**Output (vendor information omitted):**
```
192.168.1.1    00:50:56:c0:00:08
192.168.1.5    a4:1f:72:7f:25:bb
192.168.1.10   10:60:4b:73:43:de
```

### 4. Plain Mode (Script-Friendly Output)

```bash
sudo arp-scan --localnet -x
```

**Output (header and footer omitted):**
```
192.168.1.1    00:50:56:c0:00:08    VMware, Inc.
192.168.1.5    a4:1f:72:7f:25:bb    Dell Inc.
192.168.1.10   10:60:4b:73:43:de    Hewlett Packard
```

### 5. Verbose Output

```bash
sudo arp-scan --localnet -v
```

Displays scan progress, packet details, and debugging information. Use multiple `-v` flags for more verbosity:

```bash
sudo arp-scan --localnet -vv    # More verbose
sudo arp-scan --localnet -vvv   # Maximum verbosity
```

### 6. Save Results to File

```bash
sudo arp-scan --localnet > results.txt
sudo arp-scan --localnet --plain --format='${ip},${mac},${vendor}' > results.csv
```

### 7. Read Targets from File

```bash
echo "192.168.1.1" > targets.txt
echo "192.168.1.5" >> targets.txt
sudo arp-scan --file=targets.txt
```

### 8. Save Responses in PCAP Format

```bash
sudo arp-scan --localnet -W responses.pcap
tcpdump -nr responses.pcap
wireshark responses.pcap
```

---

## Advanced Options

### Retry and Timeout Control

**Adjust retry attempts:**

```bash
sudo arp-scan --localnet -r 3      # 3 attempts per host (default: 2)
sudo arp-scan --localnet --retry=1  # Single attempt (faster, risky)
sudo arp-scan --localnet --retry=5  # 5 attempts (slower, thorough)
```

**Adjust timeout per host:**

```bash
sudo arp-scan --localnet -t 1000    # 1000ms timeout (default: 500ms)
sudo arp-scan --localnet --timeout=200  # 200ms timeout (faster)
```

**Adjust backoff factor:**

```bash
sudo arp-scan --localnet -b 2.0     # Multiply timeout by 2.0 per retry
```

### Bandwidth and Packet Rate Control

**Limit outgoing bandwidth:**

```bash
sudo arp-scan --localnet -B 64000   # 64 kbps (default: 256000)
sudo arp-scan --localnet --bandwidth=1M  # 1 Mbps
```

**Set packet interval:**

```bash
sudo arp-scan --localnet -i 5       # 5ms between packets (in milliseconds)
sudo arp-scan --localnet -i 5000u   # 5000 microseconds between packets
```

### Modify ARP Packet Contents

**Spoof source IP address (useful for testing):**

```bash
sudo arp-scan --localnet --arpspa=10.0.0.50
sudo arp-scan --localnet -s 10.0.0.50
```

**Set source MAC address:**

```bash
sudo arp-scan --localnet --arpsha=aa:bb:cc:dd:ee:ff
sudo arp-scan --localnet -u aa:bb:cc:dd:ee:ff
```

**Set destination Ethernet address (instead of broadcast):**

```bash
sudo arp-scan --localnet --destaddr=aa:bb:cc:dd:ee:ff
sudo arp-scan --localnet -T aa:bb:cc:dd:ee:ff
```

**Unicast to a specific MAC address:**

```bash
sudo arp-scan --localnet --destaddr=00:11:22:33:44:55
```

### Randomization

**Randomize scan order:**

```bash
sudo arp-scan --localnet -R
sudo arp-scan --localnet --random
```

**Randomize with reproducible seed:**

```bash
sudo arp-scan --localnet --random --randomseed=12345
```

### Ignoring Duplicates

**Don't display duplicate responses:**

```bash
sudo arp-scan --localnet -g
sudo arp-scan --localnet --ignoredups
```

### Round-Trip Time (RTT) Calculation

**Display packet response time:**

```bash
sudo arp-scan --localnet -D
sudo arp-scan --localnet --rtt
```

**Output example:**
```
192.168.1.1    00:50:56:c0:00:08    VMware, Inc.           0.245ms
192.168.1.5    a4:1f:72:7f:25:bb    Dell Inc.              0.312ms
192.168.1.10   10:60:4b:73:43:de    Hewlett Packard        0.198ms
```

### DNS Resolution

**Resolve IPs to hostnames:**

```bash
sudo arp-scan --localnet -d
sudo arp-scan --localnet --resolve
```

**Numeric mode (no DNS lookups, faster):**

```bash
sudo arp-scan --localnet -N
```

---

## Output Formatting

### Default Format

```bash
sudo arp-scan --localnet
```

**Output:**
```
IP Address         MAC Address             Vendor
192.168.1.1        00:50:56:c0:00:08       VMware, Inc.
```

### Custom Format Strings

The `--format` option allows custom output formats using field references:

**Available Fields:**
- `${ip}` - Target IPv4 address
- `${mac}` - MAC address (xx:xx:xx:xx:xx:xx format)
- `${vendor}` - Vendor string
- `${name}` - Hostname (if `--resolve` is used)
- `${rtt}` - Round-trip time (if `--rtt` is used)
- `${padding}` - Padding after ARP packet (if nonzero)
- `${framing}` - Framing type (if not Ethernet_II)
- `${vlan}` - 802.1Q VLAN ID (if present)
- `${proto}` - ARP protocol (if not 0x0800)
- `${dup}` - Duplicate packet number (>1)

**Format String Examples:**

**CSV Output:**

```bash
sudo arp-scan --localnet --plain --format='${ip},${mac},${vendor}'
```

**Output:**
```
192.168.1.1,00:50:56:c0:00:08,VMware, Inc.
192.168.1.5,a4:1f:72:7f:25:bb,Dell Inc.
192.168.1.10,10:60:4b:73:43:de,Hewlett Packard
```

**Tab-Separated Values:**

```bash
sudo arp-scan --localnet --format='${ip}\t${mac}\t${vendor}'
```

**IP and MAC Only:**

```bash
sudo arp-scan --localnet --format='${ip} ${mac}'
```

**Aligned Columns with RTT:**

```bash
sudo arp-scan --localnet --rtt --format='|${ip;-15}|${mac}|${rtt;8}|'
```

**Output:**
```
|192.168.1.1        |00:50:56:c0:00:08|    0.245|
|192.168.1.5        |a4:1f:72:7f:25:bb|    0.312|
|192.168.1.10       |10:60:4b:73:43:de|    0.198|
```

**JSON-like Output (manual):**

```bash
sudo arp-scan --localnet --format='{"ip":"${ip}","mac":"${mac}","vendor":"${vendor}"}'
```

### Field Width Formatting

In format strings, you can specify field width:
- `${ip;15}` - Right-align in 15 characters
- `${ip;-15}` - Left-align in 15 characters

---

## Practical Use Cases

### 1. Network Inventory and Asset Management

Discover all devices on your network and create an inventory:

```bash
sudo arp-scan --localnet --plain \
  --format='${ip},${mac},${vendor}' > network_inventory.csv
```

Then analyze with standard tools:

```bash
head -20 network_inventory.csv
sort network_inventory.csv
cut -d',' -f3 network_inventory.csv | sort | uniq -c
```

### 2. Detecting Unauthorized Devices

Compare current scan results with a baseline:

```bash
# Create baseline
sudo arp-scan --localnet --plain --format='${ip},${mac}' > baseline.txt

# Later, check for new devices
sudo arp-scan --localnet --plain --format='${ip},${mac}' > current.txt

# Find new devices
diff baseline.txt current.txt
```

### 3. Identify Device Types by MAC Prefix

Find all devices from a specific manufacturer:

```bash
# Find all Dell devices
sudo arp-scan --localnet --plain | grep -i dell

# Find all Cisco devices
sudo arp-scan --localnet | grep -i cisco
```

### 4. Quick Network Troubleshooting

Check if specific devices are online:

```bash
# Test if gateway is online
sudo arp-scan -I eth0 192.168.1.1

# Test a range of IPs
sudo arp-scan -I eth0 192.168.1.1-10
```

### 5. Detect Duplicate IP Addresses

Multiple devices with the same IP will show multiple MAC addresses:

```bash
sudo arp-scan --localnet --plain --format='${ip}' | sort | uniq -c | grep -v " 1 "
```

This helps identify IP conflicts (which typically cause "ARP Announcement Conflict" messages).

### 6. Monitor Network Changes Over Time

```bash
#!/bin/bash
SCAN_DIR="/var/log/network_scans"
mkdir -p "$SCAN_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT="$SCAN_DIR/scan_$TIMESTAMP.txt"

sudo arp-scan --localnet > "$OUTPUT"

# Alert if fewer than expected devices
DEVICE_COUNT=$(grep -c "packets received" "$OUTPUT")
if [ "$DEVICE_COUNT" -lt 5 ]; then
    echo "Warning: Fewer devices detected!" | mail -s "Network Alert" admin@example.com
fi
```

### 7. Identify Rogue WiFi Access Points

Scan your wireless interface to find unauthorized access points:

```bash
# For wireless interface
sudo arp-scan -I wlan0 --localnet | grep -i "wireless\|802.11"
```

### 8. Integration with Nmap

Use arp-scan for fast local discovery, then use Nmap for deeper scanning:

```bash
# Get active hosts on LAN
HOSTS=$(sudo arp-scan --localnet --plain --format='${ip}' | grep -E "^[0-9]+\.")

# Run Nmap on those hosts
nmap -sV $(echo $HOSTS | tr '\n' ' ')
```

---

## Performance Optimization

### Scan Speed Factors

The time for a single-pass scan is calculated as:

```
Time = (n × i) + t + o
```

Where:
- `n` = number of hosts
- `i` = packet interval (milliseconds)
- `t` = timeout (milliseconds)
- `o` = overhead (typically ~100ms)

### Optimization Strategies

**1. Increase Bandwidth (For Large Networks):**

```bash
# Default: 256 kbps
sudo arp-scan --localnet --bandwidth=1M  # 1 Mbps

# Warning: Too high can cause network disruption
# Recommended: Keep under 10 Mbps for most networks
```

**2. Reduce Timeouts (Trade thoroughness for speed):**

```bash
# Faster scan, but may miss slow devices
sudo arp-scan --localnet --timeout=200 --retry=1
```

**3. Skip Vendor Lookup:**

```bash
# Quiet mode doesn't load OUI files
sudo arp-scan --localnet -q
```

**4. Expected Scan Times**

Example estimates for different network sizes (default settings):

- Small office (10 hosts): ~1-2 seconds
- Medium office (50 hosts): ~2-3 seconds
- Subnet /24 (254 hosts): ~3-5 seconds
- Subnet /16 (65,536 hosts): ~120+ seconds

### Bandwidth Calculation

To achieve a specific scan time:

```
Required Interval = (Total Scan Time - Timeout - Overhead) / Number of Hosts
Required Bandwidth = (28 bytes × 8 bits) / Interval in seconds
```

Example: For 256 hosts in 10 seconds with 1-second timeout:
```
(10 - 1 - 0.1) / 256 = 34ms interval
(28 × 8) / 0.034 = 6,588 bps ≈ 6.6 kbps
```

---

## Scripting and Automation

### Bash Script: Continuous Network Monitoring

```bash
#!/bin/bash
# Monitor network for changes every 5 minutes

INTERFACE="eth0"
NETWORK="192.168.1.0/24"
LOG_DIR="/var/log/arp-monitor"
mkdir -p "$LOG_DIR"

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    OUTPUT_FILE="$LOG_DIR/scan_$(date +%s).txt"
    
    sudo arp-scan -I "$INTERFACE" "$NETWORK" --plain \
        --format='${ip},${mac},${vendor}' > "$OUTPUT_FILE"
    
    echo "[$TIMESTAMP] Scan complete. Found $(wc -l < $OUTPUT_FILE) hosts"
    
    sleep 300  # 5 minutes
done
```

### Bash Script: Device Type Classification

```bash
#!/bin/bash
# Classify devices by vendor

sudo arp-scan --localnet --plain --format='${vendor}' | sort | uniq -c | \
    while read count vendor; do
        case "$vendor" in
            *VMware*)   echo "Virtual Machines: $count" ;;
            *Cisco*)    echo "Network Equipment: $count" ;;
            *Apple*)    echo "Apple Devices: $count" ;;
            *Intel*)    echo "Intel Devices: $count" ;;
            *)          echo "Other: $count ($vendor)" ;;
        esac
    done | sort -rn
```

### Python Script: Network Scan with Database Storage

```python
#!/usr/bin/env python3
import subprocess
import sqlite3
import json
from datetime import datetime

def scan_network(interface, network):
    cmd = [
        'sudo', 'arp-scan', '-I', interface, network,
        '--plain', '--format=${ip},${mac},${vendor}'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    devices = []
    for line in result.stdout.strip().split('\n'):
        if line and ',' in line:
            ip, mac, vendor = line.split(',')
            devices.append({
                'ip': ip.strip(),
                'mac': mac.strip(),
                'vendor': vendor.strip(),
                'timestamp': datetime.now().isoformat()
            })
    
    return devices

def store_in_database(devices, db_path='network.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY,
            ip TEXT,
            mac TEXT,
            vendor TEXT,
            timestamp TEXT
        )
    ''')
    
    for device in devices:
        cursor.execute(
            'INSERT INTO devices (ip, mac, vendor, timestamp) VALUES (?, ?, ?, ?)',
            (device['ip'], device['mac'], device['vendor'], device['timestamp'])
        )
    
    conn.commit()
    conn.close()

# Run scan
devices = scan_network('eth0', '192.168.1.0/24')
store_in_database(devices)

print(f"Discovered {len(devices)} devices")
for device in devices:
    print(f"  {device['ip']:15} {device['mac']:17} {device['vendor']}")
```

### Periodic Automated Scans with Cron

```bash
# Add to crontab (crontab -e)
# Run network scan every 30 minutes
*/30 * * * * sudo arp-scan --localnet --plain --format='${ip},${mac},${vendor}' >> /var/log/network-scans.log

# Daily summary at 8 AM
0 8 * * * echo "Daily Network Scan:" >> /var/log/network-summary.log && \
           sudo arp-scan --localnet >> /var/log/network-summary.log
```

---

## Security Considerations

### Why ARP-Scan Is Noisy

- **Broadcast traffic**: All devices on the network receive the scan
- **Obvious pattern**: IDS/IPS systems easily recognize the scan pattern
- **ARP logs**: Network administrators can see ARP scans in syslog

### Not for Stealth Testing

If your penetration test requires stealth:

```bash
# Bad (too obvious)
sudo arp-scan --localnet

# Better (at least some hosts use other tools)
nmap -sn 192.168.1.0/24

# Best (alternative tools)
sudo netdiscover -r 192.168.1.0/24 -p
```

### Legitimate Use Cases

- **Network inventory and management**
- **Authorized penetration testing**
- **Network troubleshooting and diagnosis**
- **Security audits (with authorization)**
- **Lab/internal network testing**

### Responsible Scanning

1. **Get Authorization**: Ensure you have written permission to scan the network
2. **Notify Admins**: Inform network administrators before scanning
3. **Schedule Appropriately**: Avoid high-traffic periods
4. **Use Appropriate Bandwidth**: Don't saturate the network
5. **Document Results**: Keep records of what you found and when

---

## Troubleshooting

### Common Issues and Solutions

**Issue: "Operation not permitted" or "raw socket error"**

```bash
# Solution 1: Use sudo
sudo arp-scan --localnet

# Solution 2: Set CAP_NET_RAW capability
sudo setcap cap_net_raw+p /usr/bin/arp-scan
arp-scan --localnet  # Now works without sudo
```

**Issue: "No interface specified and no default interface found"**

```bash
# Solution: Specify interface explicitly
sudo arp-scan -I eth0 192.168.1.0/24

# Find available interfaces
ip link show
```

**Issue: "No hosts found" or very few responses**

```bash
# Check network configuration
ifconfig
ip addr show

# Verify interface has IP address
ip addr show eth0

# Check network connectivity
ping 192.168.1.1

# Try with verbose mode to see what's happening
sudo arp-scan --localnet -vv
```

**Issue: "Cannot open pcap file" when using `-W`**

```bash
# Solution: Ensure write permissions to output directory
sudo arp-scan --localnet -W /tmp/results.pcap
sudo chown $USER:$USER /tmp/results.pcap
```

**Issue: Slow scan performance**

```bash
# Solution 1: Increase bandwidth
sudo arp-scan --localnet --bandwidth=1M

# Solution 2: Reduce timeout
sudo arp-scan --localnet --timeout=200

# Solution 3: Single retry
sudo arp-scan --localnet --retry=1

# Combination (fastest)
sudo arp-scan --localnet -r 1 -t 100 -B 1M
```

**Issue: Different results between runs**

```bash
# This is normal - devices may not respond in same time
# Use --ignoredups to see consistent results
sudo arp-scan --localnet --ignoredups

# Or increase timeout to allow all devices to respond
sudo arp-scan --localnet --timeout=1000
```

**Issue: MAC address not recognized (vendor shows "Unknown")**

```bash
# Update OUI database
sudo get-oui -f /usr/share/arp-scan/ieee-oui.txt

# Or check custom MAC file
cat /etc/arp-scan/mac-vendor.txt

# Add custom entry if needed
echo "aa:bb:cc:dd:ee:ff  Custom Vendor Name" >> ~/.arp-scan/mac-vendor.txt
sudo arp-scan --localnet --macfile=~/.arp-scan/mac-vendor.txt
```

---

## Advanced Features

### ARP Fingerprinting

The `arp-fingerprint` tool can identify operating systems based on ARP responses:

```bash
# Fingerprint a specific host
arp-fingerprint -v 192.168.1.1

# Fingerprint all hosts on network
arp-fingerprint -l
```

### 802.1Q VLAN Support

Scan through VLAN tagging:

```bash
# Scan with VLAN ID 100
sudo arp-scan --localnet --vlan=100
```

### 802.2 LLC/SNAP Framing

For legacy networks using LLC encapsulation:

```bash
sudo arp-scan --localnet --llc
```

### Custom Padding

Add data after ARP packet (for testing):

```bash
sudo arp-scan --localnet --padding=deadbeef
```

---

## Summary

**arp-scan** is an indispensable tool for network reconnaissance on local area networks. Its operation at Layer 2 makes it reliable for complete host discovery, even against firewalls and filtering devices. When combined with scripting and automation, it becomes a powerful platform for network monitoring, inventory management, and security auditing.

### Key Takeaways

1. **Layer 2 Advantage**: Works where higher-layer tools fail
2. **Complete Discovery**: Cannot be blocked without breaking network
3. **Fast and Efficient**: Minimal protocol overhead
4. **Vendor Identification**: Automatic device type recognition
5. **Flexible Output**: Customize formats for integration with other tools
6. **Not Stealth**: Use responsibly and with authorization
7. **Highly Scriptable**: Integrates easily with automation workflows

### Next Steps

- Experiment with different scan parameters in your lab environment
- Integrate arp-scan results into your network monitoring workflow
- Create custom reporting scripts for your infrastructure
- Combine with other tools (Nmap, Wireshark) for comprehensive analysis
