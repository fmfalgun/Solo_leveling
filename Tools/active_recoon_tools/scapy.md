# SCAPY: A Comprehensive Guide to Advanced Packet Crafting and Network Manipulation

## Table of Contents
1. [Introduction](#introduction)
2. [Packet Fundamentals](#packet-fundamentals)
3. [How SCAPY Works](#how-scapy-works)
4. [Installation and Setup](#installation-and-setup)
5. [Interactive Mode and Python Scripts](#interactive-mode-and-python-scripts)
6. [Packet Creation and Layering](#packet-creation-and-layering)
7. [Working with Protocols](#working-with-protocols)
8. [Sending and Receiving Packets](#sending-and-receiving-packets)
9. [Packet Sniffing and Capture](#packet-sniffing-and-capture)
10. [Advanced Packet Manipulation](#advanced-packet-manipulation)
11. [Network Scanning and Discovery](#network-scanning-and-discovery)
12. [Custom Scripts and Automation](#custom-scripts-and-automation)
13. [PCAP File Handling](#pcap-file-handling)
14. [Practical Examples and Workflows](#practical-examples-and-workflows)
15. [Security and Ethical Considerations](#security-and-ethical-considerations)

---

## Introduction

**Scapy** is a powerful, interactive Python library for packet manipulation, creation, dissection, and analysis. It allows security researchers, network administrators, and penetration testers to forge or decode packets of virtually any protocol, send them over the network, capture responses, and perform advanced network operations that would normally require complex C code.

### Key Characteristics

- **Interactive Python Library**: Can be used in Python scripts or interactive shell
- **Packet Forging**: Create custom packets from scratch with full control
- **Protocol Support**: Supports hundreds of protocols (IP, TCP, UDP, ICMP, DNS, HTTP, etc.)
- **Packet Dissection**: Decode and analyze received packets
- **Packet Sniffing**: Capture live traffic from network interfaces
- **Flexible Stacking**: Layer packets in any combination (using `/` operator)
- **Implicit Packets**: Create multiple packets in single definition
- **PCAP Integration**: Read/write Wireshark and tcpdump PCAP files
- **Raw Socket Access**: Send packets at Layer 2 and Layer 3
- **Response Handling**: Send packets and wait for responses
- **Automatable**: Write complex network operations in Python

### Primary Use Cases

- **Penetration Testing**: Craft custom exploit packets
- **Network Testing**: Test firewall rules and network behavior
- **Protocol Analysis**: Study protocol implementations
- **Network Troubleshooting**: Send specific packets to diagnose issues
- **Security Research**: Test vulnerability detection
- **DoS Simulation**: Generate attack traffic
- **Packet Generation**: Create test traffic for training
- **Network Discovery**: Custom host and service discovery
- **Reverse Engineering**: Analyze network protocols
- **Automated Testing**: Create repeatable network tests

### Limitations

- **Requires Root/Admin**: Raw socket operations need elevated privileges
- **Steep Learning Curve**: More complex than GUI tools
- **Python Dependencies**: Requires Python environment
- **Performance**: Slower than C-based tools for high-speed operations
- **Easily Detected**: Generates obvious network patterns
- **Platform Specific**: Some operations require Linux/Unix

---

## Packet Fundamentals

### OSI Model and Packet Layers

```
Layer 7: Application (DNS, HTTP, HTTPS, SSH, FTP, etc.)
Layer 6: Presentation (Encryption, Compression)
Layer 5: Session (Session Management)
Layer 4: Transport (TCP, UDP, SCTP)
Layer 3: Network (IP, ICMP, GRE)
Layer 2: Data Link (Ethernet, 802.11)
Layer 1: Physical (Bits on wire)

Scapy operates on all layers
```

### Packet Structure

```
┌─────────────────────────────────────┐
│ Ethernet Frame (Layer 2)            │
│ ├─ Destination MAC: 48 bits         │
│ ├─ Source MAC: 48 bits              │
│ ├─ Type: 16 bits (0x0800 = IPv4)   │
│ └─ CRC: 32 bits                     │
├─────────────────────────────────────┤
│ IP Header (Layer 3)                 │
│ ├─ Version/IHL: 8 bits              │
│ ├─ Type of Service: 8 bits          │
│ ├─ Total Length: 16 bits            │
│ ├─ Identification: 16 bits          │
│ ├─ Flags/Fragment Offset: 16 bits   │
│ ├─ TTL: 8 bits                      │
│ ├─ Protocol: 8 bits (6=TCP, 17=UDP) │
│ ├─ Checksum: 16 bits                │
│ ├─ Source IP: 32 bits               │
│ └─ Destination IP: 32 bits          │
├─────────────────────────────────────┤
│ TCP/UDP Header (Layer 4)            │
│ TCP: Source Port, Dest Port, Flags, │
│ Sequence, Acknowledgment, Window    │
│ UDP: Source Port, Dest Port, Length │
├─────────────────────────────────────┤
│ Payload/Data (Layer 7)              │
│ (Optional: HTTP, DNS, etc.)         │
└─────────────────────────────────────┘
```

---

## How SCAPY Works

### Architecture

```
┌─────────────────────────────────┐
│ User Code                       │
│ (Python script or interactive)  │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Scapy API Layer                 │
│ ├─ Packet creation              │
│ ├─ Packet manipulation          │
│ ├─ Protocol stack handling      │
│ └─ Response matching            │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Protocol Modules                │
│ ├─ IP, TCP, UDP, ICMP           │
│ ├─ DNS, HTTP, SSH, FTP          │
│ ├─ 802.11 (WiFi), ARP           │
│ └─ Custom protocols             │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Socket Layer                    │
│ ├─ Raw sockets (Layer 3)        │
│ ├─ Packet sockets (Layer 2)     │
│ └─ BPF/PCAP capture             │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Operating System Kernel         │
│ ├─ Network stack                │
│ ├─ Interface management         │
│ └─ Packet transmission/receipt  │
└─────────────────────────────────┘
```

### Operational Flow

```
1. Create Packet
   └─ Define layers with Scapy objects

2. Customize Fields
   └─ Set source/destination IPs, ports, flags, etc.

3. Stack Layers
   └─ Combine layers using "/" operator

4. Send Packet
   └─ send() = Layer 3
   └─ sendp() = Layer 2

5. Receive Response
   └─ sr() = Send and receive
   └─ sr1() = Send and receive one
   └─ sniff() = Capture packets

6. Process Response
   └─ Analyze received packet
   └─ Extract information
   └─ Take action
```

---

## Installation and Setup

### Linux Installation

**Using pip** (Recommended):

```bash
pip install scapy
```

**Using package manager**:

```bash
# Debian/Ubuntu
sudo apt install python3-scapy

# Fedora/RHEL
sudo dnf install python3-scapy

# Arch Linux
sudo pacman -S scapy
```

### macOS Installation

```bash
pip install scapy
```

### Windows Installation

```bash
pip install scapy
pip install pyreadline    # Optional: for better interactive shell
```

### From Source

```bash
git clone https://github.com/secdev/scapy.git
cd scapy
python setup.py install
```

### Verification

```bash
# Test installation
python3 -c "from scapy.all import *; print(IP())"

# Expected output shows default IP packet

# Check available protocols
python3 -c "from scapy.all import *; print(IP().fields)"
```

### Optional Dependencies

For advanced features:

```bash
# For 802.11 (WiFi) support
pip install python-libpcap

# For visual display
pip install pyx

# For advanced features
pip install graphviz
```

---

## Interactive Mode and Python Scripts

### Interactive Mode

Start Scapy interactive shell:

```bash
sudo scapy
```

**Example interactive session**:

```python
>>> from scapy.all import IP, TCP, send

>>> # Create IP packet
>>> p = IP(dst="192.168.1.1")

>>> # Display packet
>>> p.show()
###[ IP ]###
  version   = 4
  ihl       = None
  tos       = 0x0
  len       = None
  id        = 1
  flags     = 
  frag      = 0
  ttl       = 64
  proto     = ip
  chksum    = None
  src       = 192.168.1.100
  dst       = 192.168.1.1

>>> # Add TCP layer
>>> packet = IP(dst="192.168.1.1") / TCP(dport=80, flags="S")

>>> # Send packet
>>> send(packet)
```

### Python Script Mode

Create script file `script.py`:

```python
#!/usr/bin/env python3
from scapy.all import IP, TCP, send, sr1

# Create packet
packet = IP(dst="192.168.1.1") / TCP(dport=80, flags="S")

# Send and receive one response
response = sr1(packet, timeout=2)

# Display response
if response:
    response.show()
else:
    print("No response received")
```

Run script:

```bash
sudo python3 script.py
```

---

## Packet Creation and Layering

### Creating Single Layer Packets

**IP Packet**:

```python
from scapy.all import IP

# Basic IP packet
p = IP()
print(p)

# With destination
p = IP(dst="192.168.1.1")

# With multiple options
p = IP(dst="192.168.1.1", ttl=64, flags="DF")
```

**TCP Packet**:

```python
from scapy.all import TCP

# Basic TCP
t = TCP()

# With ports and flags
t = TCP(sport=12345, dport=80, flags="S")
```

**UDP Packet**:

```python
from scapy.all import UDP

# Basic UDP
u = UDP()

# With ports
u = UDP(sport=12345, dport=53)
```

**ICMP Packet**:

```python
from scapy.all import ICMP

# Echo request
ic = ICMP(type="echo-request")
```

### Layering Packets (Stacking)

Use `/` operator to stack layers:

```python
from scapy.all import Ether, IP, TCP

# Layer 2, 3, 4 stack
packet = Ether() / IP(dst="192.168.1.1") / TCP(dport=80, flags="S")

# Layer 3 and 4 stack (most common)
packet = IP(dst="192.168.1.1") / TCP(dport=80)

# Multiple layers
packet = IP(dst="192.168.1.1") / TCP(dport=80) / Raw(load="GET / HTTP/1.1\r\n")

# IP over IP (tunneling)
packet = IP(dst="10.0.0.1") / IP(dst="192.168.1.1") / TCP(dport=80)
```

### Modifying Packet Fields

```python
from scapy.all import IP, TCP

# Create packet
p = IP(dst="192.168.1.1") / TCP(dport=80)

# Modify fields
p[IP].ttl = 128
p[TCP].flags = "SA"
p[TCP].sport = 54321

# Access nested fields
print(p[IP].dst)        # "192.168.1.1"
print(p[TCP].dport)     # 80

# Display modified packet
p.show()
```

### Viewing Packet Details

```python
# Simple summary
packet.summary()
# Output: "IP / TCP 192.168.1.100:12345 > 192.168.1.1:80 S"

# Detailed view
packet.show()
# Output: Full packet breakdown

# ASCII art view
packet.draw()

# List layers
packet.layers()
# Output: [Ether, IP, TCP]

# Get field values
packet[IP].fields
# Output: All IP header fields
```

---

## Working with Protocols

### Common Protocol Layers

| Protocol | Import | Example |
|----------|--------|---------|
| Ethernet | `from scapy.all import Ether` | `Ether(dst="ff:ff:ff:ff:ff:ff")` |
| IP | `from scapy.all import IP` | `IP(dst="192.168.1.1")` |
| ICMP | `from scapy.all import ICMP` | `ICMP(type="echo-request")` |
| TCP | `from scapy.all import TCP` | `TCP(dport=80, flags="S")` |
| UDP | `from scapy.all import UDP` | `UDP(dport=53)` |
| DNS | `from scapy.all import DNS` | `DNS(rd=1)` |
| ARP | `from scapy.all import ARP` | `ARP(op="who-has")` |
| 802.11 | `from scapy.all import RadioTap` | For WiFi packets |

### DNS Queries

```python
from scapy.all import IP, UDP, DNS, DNSQR, send, sr1

# Create DNS query packet
dns_query = IP(dst="8.8.8.8") / UDP(dport=53) / DNS(rd=1, qd=DNSQR(qname="example.com"))

# Send and receive response
response = sr1(dns_query, timeout=2)

# Display response
if response:
    response.show()
```

### ARP Queries

```python
from scapy.all import ARP, Ether, srp

# Create ARP request
arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(op="who-has", pdst="192.168.1.1")

# Send and receive
responses = srp(arp_request, timeout=2)

# Display responses
responses.show()
```

### Raw Payloads

```python
from scapy.all import IP, TCP, Raw

# Add raw data to packet
packet = IP(dst="192.168.1.1") / TCP(dport=80) / Raw(load="GET / HTTP/1.1\r\nHost: target\r\n\r\n")

# View raw data
print(packet[Raw].load)
```

---

## Sending and Receiving Packets

### Sending Packets

**Layer 3 (IP) Sending**:

```python
from scapy.all import IP, TCP, send

# Create packet
packet = IP(dst="192.168.1.1") / TCP(dport=80, flags="S")

# Send once
send(packet)

# Send 5 times
send(packet, count=5)

# Send with interval (0.1 seconds)
send(packet, inter=0.1)

# Send continuously (until Ctrl+C)
send(packet, loop=1, inter=0.1)

# Send list of packets
send([packet, packet, packet])

# Verbose output
send(packet, verbose=True)
```

**Layer 2 (Ethernet) Sending**:

```python
from scapy.all import Ether, IP, TCP, sendp

# Create Ethernet frame with IP/TCP
packet = Ether(dst="00:11:22:33:44:55") / IP(dst="192.168.1.1") / TCP(dport=80)

# Send at Layer 2
sendp(packet, iface="eth0")

# Send with specific interface
sendp(packet, iface="wlan0")
```

### Sending and Receiving (Request/Response)

**Single Response (sr1)**:

```python
from scapy.all import IP, TCP, sr1

# Create packet
packet = IP(dst="192.168.1.1") / TCP(dport=80, flags="S")

# Send and receive one response
response = sr1(packet, timeout=2)

# Check if received response
if response:
    print("Received response!")
    response.show()
else:
    print("No response (timeout)")
```

**Multiple Responses (sr)**:

```python
from scapy.all import IP, TCP, sr

# Create packet
packet = IP(dst="192.168.1.0/24", ttl=(1,10)) / TCP(dport=80)

# Send and receive all responses
answered, unanswered = sr(packet, timeout=2)

# Process answered packets
for sent, received in answered:
    print(f"Sent: {sent.summary()}")
    print(f"Received: {received.summary()}")

# Process unanswered
print(f"Unanswered: {len(unanswered)} packets")
```

**Ethernet Layer (srp)**:

```python
from scapy.all import Ether, ARP, srp

# Create ARP request
packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(op="who-has", pdst="192.168.1.0/24")

# Send and receive
answered, unanswered = srp(packet, timeout=1)

# Process results
for sent, received in answered:
    print(f"{received[ARP].psrc} is at {received[ARP].hwsrc}")
```

---

## Packet Sniffing and Capture

### Basic Sniffing

```python
from scapy.all import sniff

# Sniff 10 packets
packets = sniff(count=10)

# Sniff TCP traffic only
packets = sniff(filter="tcp", count=5)

# Sniff DNS traffic
packets = sniff(filter="udp port 53", count=10)

# Sniff HTTP
packets = sniff(filter="tcp port 80", count=5)
```

### Sniffing with Callback

```python
from scapy.all import sniff, IP

def packet_callback(packet):
    if packet[IP]:
        print(f"From {packet[IP].src} to {packet[IP].dst}")

# Sniff with callback
packets = sniff(prn=packet_callback, count=10)
```

### Sniffing on Specific Interface

```python
from scapy.all import sniff

# List available interfaces
from scapy.arch import get_if_list
print(get_if_list())

# Sniff on specific interface
packets = sniff(iface="eth0", count=10)

# Sniff all interfaces
packets = sniff(iface="any", count=10)
```

### Advanced Sniffing

```python
from scapy.all import sniff, IP, TCP

# Custom filter function
def filter_packets(packet):
    return packet.haslayer(IP) and packet[IP].proto == 6  # TCP

# Sniff with filter function
packets = sniff(lfilter=filter_packets, count=10)

# Stop on condition
def stop_filter(packet):
    return packet[IP].dst == "192.168.1.1" if packet.haslayer(IP) else False

packets = sniff(stop_filter=stop_filter, timeout=10)
```

---

## Advanced Packet Manipulation

### Implicit Packets (Multiple Packets in One)

```python
from scapy.all import IP, TCP

# Define packet with multiple values
packet = IP(dst=["192.168.1.1", "192.168.1.2"], ttl=(1,3)) / TCP(dport=[80, 443])

# This creates 2 * 3 * 2 = 12 packets implicitly

# Iterate through implicit packets
for p in packet:
    print(p.summary())
```

### Packet Manipulation Functions

```python
from scapy.all import IP, TCP

# Create packet
p = IP(dst="192.168.1.1") / TCP(dport=80)

# Build packet (converts to bytes)
data = bytes(p)
print(f"Packet size: {len(data)} bytes")

# Get raw representation
print(repr(p))

# Extract field value
ttl = p[IP].ttl

# Set field to range
p[IP].ttl = (10, 20)

# Clear field
p[IP].ttl = None    # Use default

# Copy packet
p2 = p.copy()
```

### Custom Checksums

```python
from scapy.all import IP, TCP

# Create packet
p = IP(dst="192.168.1.1") / TCP(dport=80)

# Checksum automatically calculated when sending
# To manually calculate:
p = IP(dst="192.168.1.1") / TCP(dport=80)
p[IP].chksum = 0
p = IP(str(p))  # Re-parse to calculate

# Disable checksum verification
from scapy import conf
conf.checkIPaddr = False
```

### Packet Matching

```python
from scapy.all import IP, TCP, sr1

# Send packet and get response
response = sr1(IP(dst="192.168.1.1") / TCP(dport=80), timeout=2)

# Check if response answers request
if response.answers(IP(dst="192.168.1.1")):
    print("Valid response")

# Get response field
print(response[TCP].flags)
```

---

## Network Scanning and Discovery

### ARP Scanning (Network Discovery)

```python
from scapy.all import Ether, ARP, srp

def arp_scan(network):
    """Discover hosts on network using ARP"""
    # Create ARP request for network
    arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(op="who-has", pdst=network)
    
    # Send and receive
    answered, unanswered = srp(arp_request, timeout=1, verbose=False)
    
    # Display results
    print("IP Address\t\tMAC Address")
    print("-" * 40)
    for sent, received in answered:
        print(f"{received[ARP].psrc}\t\t{received[ARP].hwsrc}")

# Scan network
arp_scan("192.168.1.0/24")
```

### Port Scanning

```python
from scapy.all import IP, TCP, sr

def tcp_syn_scan(host, ports):
    """Perform TCP SYN scan"""
    # Create packets
    packets = IP(dst=host) / TCP(dport=ports, flags="S")
    
    # Send and receive
    answered, unanswered = sr(packets, timeout=1, verbose=False)
    
    # Analyze responses
    open_ports = []
    for sent, received in answered:
        if received[TCP].flags == 0x12:  # SYN-ACK
            open_ports.append(received[TCP].sport)
    
    return open_ports

# Scan ports
open_ports = tcp_syn_scan("192.168.1.1", [22, 80, 443, 3306])
print(f"Open ports: {open_ports}")
```

### ICMP Ping Sweep

```python
from scapy.all import IP, ICMP, sr

def ping_sweep(network):
    """Ping sweep of network"""
    # Create ICMP echo requests
    packets = IP(dst=network) / ICMP()
    
    # Send and receive
    answered, unanswered = sr(packets, timeout=1, verbose=False)
    
    # Display live hosts
    print("Live hosts:")
    for sent, received in answered:
        print(f"  {received[IP].src}")

# Ping sweep
ping_sweep("192.168.1.0/24")
```

---

## Custom Scripts and Automation

### Firewall Testing

```python
#!/usr/bin/env python3
from scapy.all import IP, TCP, UDP, sr1

def test_firewall_rules(target, ports):
    """Test firewall rules on target"""
    
    print(f"[*] Testing firewall on {target}")
    
    for port in ports:
        # TCP SYN
        tcp_packet = IP(dst=target) / TCP(dport=port, flags="S")
        response = sr1(tcp_packet, timeout=1, verbose=False)
        
        if response:
            if response[TCP].flags == 0x12:  # SYN-ACK
                print(f"[+] TCP {port}: OPEN")
            elif response[TCP].flags == 0x14:  # RST
                print(f"[-] TCP {port}: CLOSED")
        else:
            print(f"[?] TCP {port}: FILTERED")
        
        # UDP
        udp_packet = IP(dst=target) / UDP(dport=port)
        response = sr1(udp_packet, timeout=1, verbose=False)
        
        if response:
            if ICMP in response and response[ICMP].type == 3:  # Unreachable
                print(f"[-] UDP {port}: CLOSED")
            else:
                print(f"[+] UDP {port}: OPEN")
        else:
            print(f"[?] UDP {port}: FILTERED")

# Test firewall
test_firewall_rules("192.168.1.1", [22, 80, 443, 3306])
```

### DNS Enumeration

```python
#!/usr/bin/env python3
from scapy.all import IP, UDP, DNS, DNSQR, sr1

def dns_query(nameserver, domain):
    """Query DNS for domain"""
    
    dns_request = IP(dst=nameserver) / UDP(dport=53) / DNS(rd=1, qd=DNSQR(qname=domain))
    
    response = sr1(dns_request, timeout=2, verbose=False)
    
    if response and DNS in response:
        dns_response = response[DNS]
        print(f"[*] DNS Response for {domain}:")
        
        if dns_response.an:  # Answer section
            for answer in dns_response.an:
                print(f"  {answer.rrname.decode()}: {answer.rdata}")
    else:
        print(f"[-] No DNS response")

# Query DNS
dns_query("8.8.8.8", "example.com")
```

### Packet Sniffer with Export

```python
#!/usr/bin/env python3
from scapy.all import sniff, IP, TCP, UDP

captured_packets = []

def packet_callback(packet):
    captured_packets.append(packet)
    
    if packet.haslayer(IP):
        src = packet[IP].src
        dst = packet[IP].dst
        proto = packet[IP].proto
        
        proto_name = "TCP" if proto == 6 else "UDP" if proto == 17 else "OTHER"
        print(f"[+] {proto_name}: {src} -> {dst}")

# Sniff packets
print("[*] Starting packet capture...")
sniff(prn=packet_callback, count=100, filter="ip")

# Save to PCAP
print(f"[*] Saving {len(captured_packets)} packets to capture.pcap")
wrpcap("capture.pcap", captured_packets)
```

---

## PCAP File Handling

### Reading PCAP Files

```python
from scapy.all import rdpcap

# Read PCAP file
packets = rdpcap("capture.pcap")

# Display packet count
print(f"Captured {len(packets)} packets")

# Iterate through packets
for packet in packets:
    print(packet.summary())

# Filter packets
tcp_packets = [p for p in packets if p.haslayer(TCP)]
print(f"TCP packets: {len(tcp_packets)}")
```

### Writing PCAP Files

```python
from scapy.all import IP, TCP, wrpcap, Raw

# Create packets
packets = []
for i in range(5):
    p = IP(dst="192.168.1.1") / TCP(dport=80) / Raw(load=f"Packet {i}")
    packets.append(p)

# Write to PCAP
wrpcap("test.pcap", packets)

# Append to existing PCAP
wrpcap("test.pcap", packets, append=True)
```

### Analyzing PCAP Files

```python
from scapy.all import rdpcap, IP, TCP, UDP

def analyze_pcap(filename):
    """Analyze PCAP file"""
    
    packets = rdpcap(filename)
    
    # Statistics
    tcp_count = len([p for p in packets if p.haslayer(TCP)])
    udp_count = len([p for p in packets if p.haslayer(UDP)])
    
    print(f"Total packets: {len(packets)}")
    print(f"TCP packets: {tcp_count}")
    print(f"UDP packets: {udp_count}")
    
    # Traffic analysis
    ips = {}
    for packet in packets:
        if packet.haslayer(IP):
            src = packet[IP].src
            if src not in ips:
                ips[src] = 0
            ips[src] += 1
    
    print("\nTop talkers:")
    for ip, count in sorted(ips.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {ip}: {count} packets")

# Analyze
analyze_pcap("capture.pcap")
```

---

## Practical Examples and Workflows

### Example 1: Simple Port Scanner

```python
#!/usr/bin/env python3
from scapy.all import IP, TCP, sr, conf
conf.verb = 0

def simple_port_scan(host, ports):
    """Simple port scanner"""
    
    print(f"[*] Scanning {host}")
    open_ports = []
    
    for port in ports:
        packet = IP(dst=host) / TCP(dport=port, flags="S")
        response = sr1(packet, timeout=1, verbose=False)
        
        if response and response[TCP].flags == 0x12:  # SYN-ACK
            open_ports.append(port)
            print(f"[+] Port {port}: OPEN")
    
    return open_ports

# Scan
simple_port_scan("192.168.1.1", [22, 80, 443, 3306, 8080])
```

### Example 2: ARP Spoofing Detection

```python
#!/usr/bin/env python3
from scapy.all import ARP, Ether, sniff

def detect_arp_spoofing(packet):
    """Detect ARP spoofing attempts"""
    
    if packet.haslayer(ARP) and packet[ARP].op == 2:  # ARP Reply
        print(f"[*] ARP Reply: {packet[ARP].psrc} is at {packet[ARP].hwsrc}")
        
        # Store and check for duplicates
        # (simplified detection)

# Sniff and monitor
print("[*] Monitoring for ARP spoofing...")
sniff(prn=detect_arp_spoofing, filter="arp", count=100)
```

### Example 3: Network Reconnaissance

```python
#!/usr/bin/env python3
from scapy.all import Ether, ARP, IP, ICMP, sr, srp

def network_recon(network):
    """Perform basic network reconnaissance"""
    
    print(f"[*] Performing reconnaissance on {network}")
    
    # ARP scan
    print("\n[*] ARP Scanning...")
    arp = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network)
    answered, _ = srp(arp, timeout=1, verbose=False)
    
    hosts = []
    for _, response in answered:
        ip = response[ARP].psrc
        mac = response[ARP].hwsrc
        hosts.append(ip)
        print(f"  {ip} ({mac})")
    
    # Port scan
    print("\n[*] Port Scanning...")
    for host in hosts[:5]:  # First 5 hosts
        packet = IP(dst=host) / TCP(dport=[22, 80, 443], flags="S")
        answered, _ = sr(packet, timeout=1, verbose=False)
        
        for _, response in answered:
            if response[TCP].flags == 0x12:
                print(f"  {host}: Port {response[TCP].sport} OPEN")

# Scan network
network_recon("192.168.1.0/24")
```

---

## Security and Ethical Considerations

### Legal Implications

**Scapy Usage**:

- ✓ **Legal for authorized testing** (with written permission)
- ✓ **Permitted on own systems** and authorized networks
- ✗ **Illegal without authorization** (unauthorized network access)
- ✗ **May violate service terms** on third-party networks
- ✗ **Easily generates detectable patterns**

### Responsible Use

1. **Get Written Authorization**: Signed approval for testing
2. **Define Scope**: Clear list of authorized targets
3. **Limit Impact**: Avoid network disruption
4. **Document Activity**: Keep detailed logs
5. **Report Findings**: Professional incident reporting
6. **Secure Results**: Protect sensitive information
7. **Follow Policy**: Stay within authorized scope

### Detection

Systems can detect Scapy-generated traffic:

```
- Unusual packet characteristics
- Non-standard TCP flags
- Rapid connection attempts
- Fragmented packets with suspicious content
- Anomalous sequence numbers
- IDS/IPS signatures
```

---

## Summary and Best Practices

### Key Capabilities

1. **Packet Creation**: Full control over all packet fields
2. **Protocol Support**: Hundreds of protocols supported
3. **Layering**: Combine protocols in any way
4. **Sending**: Layer 2 and Layer 3 transmission
5. **Receiving**: Capture and analyze responses
6. **Sniffing**: Monitor live network traffic
7. **PCAP Integration**: Read/write capture files
8. **Automation**: Write complex network scripts

### When Scapy is Useful

✓ **Appropriate Uses**:
- Authorized penetration testing
- Network protocol learning
- Custom packet generation
- Firewall testing
- Network troubleshooting
- Security research
- Protocol analysis

✗ **Inappropriate Uses**:
- Unauthorized network scanning
- DoS attacks
- Credential theft
- Network disruption
- Criminal activity

### Best Practices

1. **Get Authorization**: Written approval required
2. **Learn Protocols**: Understand TCP/IP fundamentals
3. **Test Locally**: Practice on isolated networks
4. **Document Code**: Comment and explain scripts
5. **Error Handling**: Handle timeouts and exceptions
6. **Minimal Impact**: Test carefully to avoid disruption
7. **Professional Ethics**: Report findings responsibly

### Common Patterns

**Port Scanning**:

```python
packets = IP(dst=host) / TCP(dport=ports, flags="S")
answered, unanswered = sr(packets)
```

**Host Discovery**:

```python
arp = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network)
answered, unanswered = srp(arp)
```

**Send and Receive**:

```python
response = sr1(packet, timeout=2)
```

**Sniffing**:

```python
sniff(prn=callback, filter="tcp port 80", count=10)
```

### Next Steps

- Learn TCP/IP protocol fundamentals
- Practice on authorized test networks
- Study protocol implementations
- Develop custom network tools
- Get certified (OSCP, CEH)
- Conduct authorized security assessments
- Document all activities
- Follow responsible disclosure practices
