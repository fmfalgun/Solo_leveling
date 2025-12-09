# DHCPING: A Comprehensive Guide to DHCP Server Testing and Diagnostics

## Table of Contents
1. [Introduction](#introduction)
2. [DHCP Protocol Fundamentals](#dhcp-protocol-fundamentals)
3. [How DHCPING Works](#how-dhcping-works)
4. [Installation](#installation)
5. [Basic Syntax](#basic-syntax)
6. [Core Concepts](#core-concepts)
7. [Essential Commands](#essential-commands)
8. [Advanced Options](#advanced-options)
9. [DHCPING vs Other DHCP Testing Tools](#dhcping-vs-other-dhcp-testing-tools)
10. [Practical Use Cases](#practical-use-cases)
11. [Integration and Automation](#integration-and-automation)
12. [Troubleshooting](#troubleshooting)
13. [Security Considerations](#security-considerations)

---

## Introduction

**dhcping** is a specialized command-line utility designed for testing and diagnostics of DHCP servers on local area networks (LANs). Unlike general-purpose DHCP clients that attempt to lease an IP address, dhcping simulates a DHCP relay agent or alternate client model to send targeted DHCP messages and analyze server responses.

### Key Characteristics

- **Targeted Testing**: Tests specific DHCP servers without disrupting normal network operations
- **Relay Agent Simulation**: Operates as a DHCP relay or testing client, not as a standard DHCP client
- **Response Analysis**: Validates DHCP server functionality through response verification
- **Non-Lease Oriented**: Tests server availability without consuming IP addresses from the pool
- **Lightweight**: Minimal network impact and resource requirements
- **Monitoring Integration**: Designed for integration with monitoring systems like relayd or Nagios

### Primary Use Cases

- Verifying DHCP server availability and functionality
- Network monitoring and health checks
- Troubleshooting DHCP configuration issues
- Testing failover and redundancy scenarios
- Automated DHCP service monitoring
- Validating DHCP server responses

### Limitations

- **Local Network Only**: Cannot test DHCP servers across routed network boundaries
- **No DHCP Discovery**: Does not discover DHCP servers; you must specify the server IP
- **Single Server Testing**: Tests one DHCP server at a time (requires multiple invocations for multiple servers)
- **Limited to DHCPREQUEST/DHCPINFORM**: Cannot perform full DORA (Discover, Offer, Request, Acknowledge) sequence

---

## DHCP Protocol Fundamentals

### Overview of DHCP

DHCP (Dynamic Host Configuration Protocol) is a network administration protocol that automatically assigns IP addresses and other network configuration parameters to devices on a network. It operates at the application layer (Layer 7) using UDP ports:

- **UDP Port 67**: DHCP Server (also called BOOTP server port)
- **UDP Port 68**: DHCP Client (also called BOOTP client port)

### DORA Process (Standard DHCP Client Lease)

The standard DHCP initialization follows a four-step exchange:

**1. DISCOVER (Client → Network)**
- Client broadcasts "Is there a DHCP server?"
- Source IP: 0.0.0.0 (client has no IP yet)
- Destination IP: 255.255.255.255 (broadcast)
- Destination MAC: ff:ff:ff:ff:ff:ff (broadcast)

**2. OFFER (Server → Client)**
- Server responds with available IP address and lease terms
- Source IP: Server IP address
- Destination IP: 255.255.255.255 (broadcast, since client still has 0.0.0.0)
- Contains: Offered IP, subnet mask, gateway, DNS servers, lease time

**3. REQUEST (Client → Network)**
- Client accepts the offer and requests the IP
- Source IP: Still 0.0.0.0 (awaiting confirmation)
- Destination IP: 255.255.255.255 (broadcast)
- Contains: Server Identifier (which server to use if multiple responded)

**4. ACKNOWLEDGE (Server → Client)**
- Server confirms the lease and finalizes configuration
- Source IP: Server IP address
- Destination IP: Client's new IP (or broadcast if client hasn't configured interface)
- Contains: Final IP configuration, lease time, renewal times (T1/T2)

### DHCP Message Format

```
┌─────────────────────────────────────────────────────────┐
│ Ethernet Header                                         │
│  - Source MAC: client's MAC address                     │
│  - Destination MAC: ff:ff:ff:ff:ff:ff (broadcast)      │
│  - Type: 0x0800 (IP)                                    │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ IP Header                                               │
│  - Source IP: 0.0.0.0 or client IP (for renewals)     │
│  - Destination IP: 255.255.255.255 or server IP        │
│  - Protocol: UDP (17)                                   │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ UDP Header                                              │
│  - Source Port: 68 (client port)                        │
│  - Destination Port: 67 (server port)                   │
│  - Length: total UDP packet size                        │
│  - Checksum: optional but recommended                   │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ DHCP Payload (BOOTP Format)                             │
├─────────────────────────────────────────────────────────┤
│ OP (1 byte)                                             │
│  - 1 = BOOTREQUEST, 2 = BOOTREPLY                       │
├─────────────────────────────────────────────────────────┤
│ HTYPE (1 byte)                                          │
│  - 1 = Ethernet                                         │
├─────────────────────────────────────────────────────────┤
│ HLEN (1 byte)                                           │
│  - 6 = MAC address length (for Ethernet)               │
├─────────────────────────────────────────────────────────┤
│ HOPS (1 byte)                                           │
│  - Relay agent hop count (0 for direct client)         │
├─────────────────────────────────────────────────────────┤
│ XID (4 bytes)                                           │
│  - Transaction ID (client-generated, random)            │
├─────────────────────────────────────────────────────────┤
│ SECS (2 bytes)                                          │
│  - Seconds elapsed since client boot                    │
├─────────────────────────────────────────────────────────┤
│ FLAGS (2 bytes)                                         │
│  - Broadcast flag (0x8000) and reserved bits           │
├─────────────────────────────────────────────────────────┤
│ CIADDR (4 bytes)                                        │
│  - Client IP address (0.0.0.0 for DISCOVER)            │
├─────────────────────────────────────────────────────────┤
│ YIADDR (4 bytes)                                        │
│  - Your IP address (offered by server, 0.0.0.0 for req)│
├─────────────────────────────────────────────────────────┤
│ SIADDR (4 bytes)                                        │
│  - Server IP address (if server wants to tell client)  │
├─────────────────────────────────────────────────────────┤
│ GIADDR (4 bytes)                                        │
│  - Gateway IP address (relay agent address)             │
├─────────────────────────────────────────────────────────┤
│ CHADDR (16 bytes)                                       │
│  - Client hardware address (MAC address + padding)      │
├─────────────────────────────────────────────────────────┤
│ SNAME (64 bytes)                                        │
│  - Server host name (optional, null-terminated string) │
├─────────────────────────────────────────────────────────┤
│ FILE (128 bytes)                                        │
│  - Boot file name (for diskless clients)               │
├─────────────────────────────────────────────────────────┤
│ OPTIONS (variable length)                               │
│  - DHCP options (starts with magic cookie 0x63825363)  │
│  - Format: Type(1) | Length(1) | Value(Length)         │
└─────────────────────────────────────────────────────────┘
```

### Common DHCP Options

| Option | Name | Purpose |
|--------|------|---------|
| 1 | Subnet Mask | Network subnet mask (e.g., 255.255.255.0) |
| 3 | Router | Default gateway IP address |
| 6 | Domain Name Servers | DNS server IP addresses |
| 15 | Domain Name | Client's domain name |
| 28 | Broadcast Address | Network broadcast address |
| 50 | Requested IP Address | IP address client wants |
| 51 | Lease Time | Lease duration in seconds |
| 53 | DHCP Message Type | 1=DISCOVER, 2=OFFER, 3=REQUEST, 4=DECLINE, 5=ACK, 6=NAK, 7=RELEASE, 8=INFORM |
| 54 | Server Identifier | DHCP server IP address |
| 58 | Renewal Time (T1) | When to start renewing lease |
| 59 | Rebinding Time (T2) | When to rebind if renewal fails |

---

## How DHCPING Works

### Relay Agent Simulation Model

dhcping operates differently from standard DHCP clients. Instead of performing the full DORA sequence, it simulates a **DHCP relay agent** sending DHCPREQUEST or DHCPINFORM messages directly to a specific server.

### DHCPREQUEST Model (Default)

When you run dhcping with basic options, it sends a DHCPREQUEST message:

**Step-by-Step Process:**

1. **User Invocation**
   ```bash
   sudo dhcping -c 192.168.50.10 -s 192.168.50.21 -h "08:00:27:f3:27:23"
   ```

2. **Packet Construction**
   - Creates a DHCPREQUEST message (DHCP Message Type = 3)
   - Sets CIADDR (Client IP Address) to `-c` value (192.168.50.10)
   - Sets destination to server IP (192.168.50.21)
   - Uses client MAC address from `-h` option
   - Generates random XID (transaction ID)

3. **Network Transmission**
   - Sends UDP packet to server IP:port 67
   - Source port: random ephemeral port
   - Destination port: 67
   - Expects unicast response (not broadcast)

4. **Response Reception**
   - Listens for DHCPACK (successful) or DHCPNAK (failure)
   - Analyzes server response
   - Reports success or failure

5. **Exit Status**
   - Returns 0 if valid response received
   - Returns non-zero if no response or error

### DHCPINFORM Model (Optional)

When invoked with specific options, dhcping can send DHCPINFORM instead:

- Sends DHCPINFORM message (DHCP Message Type = 8)
- Used by clients that already have an IP address
- Requests additional configuration parameters (DNS, gateway, etc.)
- Does not request a lease renewal
- Server responds with DHCPACK containing requested options only

### Key Differences from Standard DHCP Clients

| Aspect | Standard DHCP Client | dhcping |
|--------|----------------------|---------|
| Flow | Full DORA sequence | Single REQUEST/INFORM message |
| IP Requirement | None (starts at 0.0.0.0) | Requires IP (from -c option) |
| Server Discovery | Broadcast DISCOVER | Direct unicast to specified IP |
| Multiple Servers | Tests first responder | Tests specific server only |
| Lease Acquisition | Leases IP address | No lease acquisition |
| Network Impact | Configures network interface | No interface changes |
| Use Case | Normal client operation | Monitoring/testing |

---

## Installation

### Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install dhcping
```

### Linux (Fedora/RHEL/CentOS)

```bash
sudo yum install dhcping
```

### Linux (Arch)

```bash
sudo pacman -S dhcping
```

### FreeBSD

```bash
sudo pkg install dhcping
```

### macOS (Homebrew)

```bash
brew install dhcping
```

### From Source (GitHub)

```bash
git clone https://github.com/eait-itig/dhcping.git
cd dhcping
./configure
make
sudo make install
```

If configure script doesn't exist:

```bash
cd dhcping
autoconf
automake --add-missing
./configure
make
sudo make install
```

### Verify Installation

```bash
dhcping -v        # Display version
which dhcping      # Show location
dhcping --help     # Display help message
```

---

## Basic Syntax

### General Command Structure

```bash
dhcping [options] -s <DHCP_SERVER_IP>
```

### Minimum Required Options

The absolute minimum to run dhcping:

```bash
sudo dhcping -s 192.168.50.21
```

However, for meaningful testing, you typically need:

```bash
sudo dhcping -c <CLIENT_IP> -s <SERVER_IP> -h <CLIENT_MAC>
```

### Privilege Requirements

**dhcping requires root or elevated privileges** because it needs to:
- Bind to UDP port 68 (DHCP client port)
- Send raw UDP packets
- Access network interfaces

```bash
sudo dhcping -s 192.168.50.21
```

Or with sudo without password (if configured):

```bash
sudo dhcping -s 192.168.50.21 -c 192.168.50.10 -h "08:00:27:f3:27:23"
```

---

## Core Concepts

### Client IP Address (-c)

Specifies the IP address to use as the DHCP client in the REQUEST message:

```bash
sudo dhcping -c 192.168.50.10 -s 192.168.50.21
```

This sets the CIADDR (Client IP Address) field in the DHCP packet. The server will recognize this as a renewal request from a client with this IP.

**Important**: The IP address doesn't need to actually be configured on your system; dhcping simply puts this value in the DHCP packet.

### Server IP Address (-s)

Specifies the DHCP server to test:

```bash
sudo dhcping -s 192.168.50.21
```

This is the destination IP address for the DHCPREQUEST packet. The server must be reachable on the network.

### Client MAC Address (-h)

Specifies the client hardware (MAC) address:

```bash
sudo dhcping -h "08:00:27:f3:27:23" -s 192.168.50.21
```

This sets the CHADDR (Client Hardware Address) field in the DHCP packet. The server uses this to match the request to a specific client entry.

**Format**: Hex bytes separated by colons (standard MAC address notation)

**Note**: If not specified, dhcping attempts to use your actual MAC address (implementation-dependent).

### Request ID (XID)

Each DHCP message includes a transaction ID (XID) to match requests with responses:

- **Generated**: dhcping generates a random 32-bit value
- **Purpose**: Matches DHCP requests with responses
- **Not user-configurable**: Most implementations generate this automatically

---

## Essential Commands

### 1. Test a Specific DHCP Server

```bash
sudo dhcping -c 192.168.50.10 -s 192.168.50.21 -h "08:00:27:f3:27:23"
```

**Output (Success):**
```
Got answer from: 192.168.50.21
```

**Output (Failure):**
```
no answer
```

**Breakdown:**
- `-c 192.168.50.10`: Client IP (simulated client address)
- `-s 192.168.50.21`: Server IP (DHCP server to test)
- `-h "08:00:27:f3:27:23"`: Client MAC address

### 2. Minimal Test (Let System Detect MAC)

```bash
sudo dhcping -c 192.168.50.10 -s 192.168.50.21
```

In this case, dhcping attempts to determine your actual MAC address from the system.

### 3. Test with Timeout

```bash
sudo dhcping -c 192.168.50.10 -s 192.168.50.21 -h "08:00:27:f3:27:23" -w 5000
```

Wait up to 5000 milliseconds (5 seconds) for a response (default is typically 3000ms).

### 4. Verbose Output

```bash
sudo dhcping -c 192.168.50.10 -s 192.168.50.21 -h "08:00:27:f3:27:23" -v
```

Displays detailed information about the request and response packets.

### 5. Test Multiple DHCP Servers

```bash
for server in 192.168.50.21 192.168.50.22 192.168.50.23; do
    echo "Testing $server..."
    sudo dhcping -c 192.168.50.10 -s "$server" -h "08:00:27:f3:27:23"
done
```

### 6. Test with Different Client IPs

```bash
# Test if DHCP server recognizes various IP addresses
for ip in 192.168.50.1 192.168.50.100 192.168.50.200; do
    echo "Testing with client IP: $ip"
    sudo dhcping -c "$ip" -s 192.168.50.21 -h "08:00:27:f3:27:23"
done
```

### 7. Test with Different Client MACs

```bash
# Test with multiple simulated clients
for mac in "08:00:27:f3:27:23" "08:00:27:aa:bb:cc" "08:00:27:dd:ee:ff"; do
    echo "Testing with MAC: $mac"
    sudo dhcping -c 192.168.50.10 -s 192.168.50.21 -h "$mac"
done
```

### 8. Quick Availability Check (Scripting)

```bash
if sudo dhcping -c 192.168.50.10 -s 192.168.50.21 -h "08:00:27:f3:27:23" > /dev/null 2>&1; then
    echo "DHCP server is operational"
else
    echo "DHCP server is not responding"
fi
```

---

## Advanced Options

### Request Interface (-r)

Specifies the network interface from which to send the request:

```bash
sudo dhcping -r eth0 -c 192.168.50.10 -s 192.168.50.21
```

### Wait Timeout (-w)

Specifies timeout in milliseconds for waiting on server response:

```bash
# Wait 2 seconds (2000 ms) - faster
sudo dhcping -w 2000 -c 192.168.50.10 -s 192.168.50.21

# Wait 10 seconds (10000 ms) - more lenient
sudo dhcping -w 10000 -c 192.168.50.10 -s 192.168.50.21
```

**Default**: Usually 3000ms (3 seconds)

**Use Cases:**
- Short timeout (1000-2000ms): For LAN testing where response is expected quickly
- Long timeout (5000-10000ms): For testing across slower links or heavily loaded servers

### DHCPINFORM Message

Some implementations support sending DHCPINFORM instead of DHCPREQUEST:

```bash
# Request additional configuration parameters
sudo dhcping -i -c 192.168.50.10 -s 192.168.50.21
```

DHCPINFORM is useful when:
- Client already has an IP address
- Testing parameter request handling
- Requesting specific options without lease renewal

### Retries

Some versions of dhcping support retry attempts:

```bash
sudo dhcping -c 192.168.50.10 -s 192.168.50.21 --retry=3
```

Tests multiple times before declaring failure.

---

## DHCPING vs Other DHCP Testing Tools

### Comparison Table

| Feature | dhcping | nmap (script) | dhcpcd | dhclient |
|---------|---------|---------------|--------|----------|
| **Purpose** | DHCP server testing | Network scanning | Full DHCP client | Full DHCP client |
| **Server Target** | Specific server IP | Discovery broadcast | Discovery broadcast | Discovery broadcast |
| **Message Type** | REQUEST/INFORM | DISCOVER/INFORM | DISCOVER→REQUEST | DISCOVER→REQUEST |
| **Multiple Servers** | One at a time | Shows first response | Shows first response | Configures interface |
| **Lease Acquisition** | No | No | Yes | Yes |
| **Interface Config** | No | No | Yes | Yes |
| **Monitoring Ready** | Yes | No | No | No |
| **Learning Curve** | Easy | Medium | Medium | Medium |
| **Root Required** | Yes | Yes | Yes | Yes |

### When to Use Each Tool

**Use dhcping when:**
- Testing specific DHCP servers
- Monitoring DHCP service health
- Integrating with automated systems
- Testing without acquiring leases
- Need fast, lightweight testing

**Use nmap when:**
- Discovering DHCP servers on network
- Comprehensive network scanning needed
- Identifying rogue DHCP servers
- Both DISCOVER and INFORM testing desired

**Use dhcpcd when:**
- Need to obtain an actual lease
- Testing full DHCP client functionality
- Want to verify lease renewal
- Testing client-side DHCP behavior

**Use dhclient when:**
- Testing on Linux with ISC DHCP
- Need to renew/release leases
- Testing DHCP failover scenarios
- Analyzing full DHCP exchange

---

## Practical Use Cases

### 1. Monitoring DHCP Service Health

Create a simple health check script:

```bash
#!/bin/bash
# dhcp-health-check.sh

DHCP_SERVER="192.168.50.21"
CLIENT_IP="192.168.50.10"
CLIENT_MAC="08:00:27:f3:27:23"

if sudo dhcping -c "$CLIENT_IP" -s "$DHCP_SERVER" -h "$CLIENT_MAC" > /dev/null 2>&1; then
    echo "SUCCESS: DHCP server $DHCP_SERVER is responding"
    exit 0
else
    echo "FAILURE: DHCP server $DHCP_SERVER is not responding"
    exit 1
fi
```

Run from cron:

```bash
# Crontab entry to check every 5 minutes
*/5 * * * * /usr/local/bin/dhcp-health-check.sh >> /var/log/dhcp-health.log 2>&1
```

### 2. Testing DHCP Failover

Test both primary and secondary DHCP servers:

```bash
#!/bin/bash
# dhcp-failover-test.sh

PRIMARY="192.168.50.21"
SECONDARY="192.168.50.22"
CLIENT_IP="192.168.50.50"
CLIENT_MAC="08:00:27:f3:27:23"

echo "Testing Primary DHCP Server: $PRIMARY"
if sudo dhcping -c "$CLIENT_IP" -s "$PRIMARY" -h "$CLIENT_MAC" > /dev/null 2>&1; then
    echo "✓ Primary server is operational"
else
    echo "✗ Primary server is DOWN"
fi

echo "Testing Secondary DHCP Server: $SECONDARY"
if sudo dhcping -c "$CLIENT_IP" -s "$SECONDARY" -h "$CLIENT_MAC" > /dev/null 2>&1; then
    echo "✓ Secondary server is operational"
else
    echo "✗ Secondary server is DOWN"
fi
```

### 3. Monitoring Multiple Networks

Test DHCP servers across multiple network segments:

```bash
#!/bin/bash
# dhcp-multi-segment-test.sh

# Define networks
declare -A NETWORKS=(
    [LAN1_Server]="192.168.1.1"
    [LAN1_Client]="192.168.1.100"
    [LAN1_MAC]="08:00:27:00:00:01"
    
    [LAN2_Server]="192.168.2.1"
    [LAN2_Client]="192.168.2.100"
    [LAN2_MAC]="08:00:27:00:00:02"
    
    [LAN3_Server]="192.168.3.1"
    [LAN3_Client]="192.168.3.100"
    [LAN3_MAC]="08:00:27:00:00:03"
)

for segment in LAN1 LAN2 LAN3; do
    server="${NETWORKS[${segment}_Server]}"
    client="${NETWORKS[${segment}_Client]}"
    mac="${NETWORKS[${segment}_MAC]}"
    
    echo "Testing $segment (Server: $server)"
    if sudo dhcping -c "$client" -s "$server" -h "$mac" > /dev/null 2>&1; then
        echo "  ✓ DHCP operational"
    else
        echo "  ✗ DHCP FAILURE - Alert!"
    fi
done
```

### 4. Integration with Nagios Monitoring

```bash
#!/bin/bash
# check_dhcp_server.sh - Nagios plugin wrapper for dhcping

SERVER="$1"
CLIENT_IP="$2"
CLIENT_MAC="$3"
TIMEOUT="$4"

if [ -z "$SERVER" ] || [ -z "$CLIENT_IP" ] || [ -z "$CLIENT_MAC" ]; then
    echo "UNKNOWN: Usage: $0 <server_ip> <client_ip> <client_mac> [timeout_ms]"
    exit 3
fi

TIMEOUT=${TIMEOUT:-3000}

START=$(date +%s%N)

if sudo dhcping -c "$CLIENT_IP" -s "$SERVER" -h "$CLIENT_MAC" -w "$TIMEOUT" > /dev/null 2>&1; then
    END=$(date +%s%N)
    RESPONSE_TIME=$(( (END - START) / 1000000 ))
    
    echo "OK: DHCP server $SERVER responding (${RESPONSE_TIME}ms) | response_time=${RESPONSE_TIME}ms"
    exit 0
else
    END=$(date +%s%N)
    RESPONSE_TIME=$(( (END - START) / 1000000 ))
    
    echo "CRITICAL: DHCP server $SERVER not responding (timeout=${TIMEOUT}ms) | response_time=${RESPONSE_TIME}ms"
    exit 2
fi
```

Usage in Nagios:

```bash
define service {
    service_description  DHCP Server Check
    host_name           infrastructure-server
    check_command       check_dhcp_server!192.168.50.21!192.168.50.10!08:00:27:f3:27:23!3000
    check_interval      5
    retry_interval      1
    max_check_attempts  3
}
```

### 5. Testing DHCP Response Times

Measure server response performance:

```bash
#!/bin/bash
# dhcp-response-time-test.sh

SERVER="192.168.50.21"
CLIENT_IP="192.168.50.10"
CLIENT_MAC="08:00:27:f3:27:23"
ITERATIONS=10

echo "Testing DHCP response times ($ITERATIONS iterations)"
echo "Server: $SERVER"
echo "---"

for i in $(seq 1 $ITERATIONS); do
    START=$(date +%s%N)
    
    if sudo dhcping -c "$CLIENT_IP" -s "$SERVER" -h "$CLIENT_MAC" > /dev/null 2>&1; then
        END=$(date +%s%N)
        RESPONSE_MS=$(( (END - START) / 1000000 ))
        echo "Request $i: ${RESPONSE_MS}ms"
    else
        echo "Request $i: TIMEOUT"
    fi
    
    sleep 0.5  # Brief pause between requests
done
```

### 6. Testing Specific DHCP Scopes

Test if DHCP server responds for specific IP ranges:

```bash
#!/bin/bash
# dhcp-scope-test.sh

SERVER="192.168.50.21"
CLIENT_MAC="08:00:27:f3:27:23"

# Test different scopes
declare -a SCOPES=("192.168.50.10" "192.168.50.100" "192.168.50.200" "192.168.50.250")

echo "Testing DHCP scopes on server: $SERVER"
echo "---"

for ip in "${SCOPES[@]}"; do
    echo -n "Scope $ip: "
    if sudo dhcping -c "$ip" -s "$SERVER" -h "$CLIENT_MAC" > /dev/null 2>&1; then
        echo "✓ Responds"
    else
        echo "✗ No response"
    fi
done
```

---

## Integration and Automation

### Bash Integration with logging

```bash
#!/bin/bash
# dhcp-monitor.sh - Continuous DHCP monitoring

LOG_FILE="/var/log/dhcp-monitor.log"
ALERT_EMAIL="admin@example.com"
CHECK_INTERVAL=60

SERVERS=(
    "primary:192.168.50.21:192.168.50.10:08:00:27:f3:27:23"
    "secondary:192.168.50.22:192.168.50.10:08:00:27:f3:27:23"
)

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    for entry in "${SERVERS[@]}"; do
        IFS=':' read -r name server client mac <<< "$entry"
        
        if sudo dhcping -c "$client" -s "$server" -h "$mac" > /dev/null 2>&1; then
            echo "[$TIMESTAMP] $name ($server): UP" >> "$LOG_FILE"
        else
            echo "[$TIMESTAMP] $name ($server): DOWN - ALERT!" >> "$LOG_FILE"
            echo "DHCP Server Alert: $name is down" | \
                mail -s "DHCP Alert: $name DOWN" "$ALERT_EMAIL"
        fi
    done
    
    sleep "$CHECK_INTERVAL"
done
```

### Python Integration

```python
#!/usr/bin/env python3
import subprocess
import sys
from datetime import datetime

def test_dhcp_server(client_ip, server_ip, client_mac, timeout=3000):
    """Test DHCP server and return result."""
    cmd = [
        'sudo', 'dhcping',
        '-c', client_ip,
        '-s', server_ip,
        '-h', client_mac,
        '-w', str(timeout)
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=10,
            text=True
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False

def monitor_dhcp_servers(servers_config, log_file=None):
    """Monitor multiple DHCP servers."""
    results = {}
    
    for name, config in servers_config.items():
        client_ip = config['client_ip']
        server_ip = config['server_ip']
        client_mac = config['client_mac']
        
        success = test_dhcp_server(client_ip, server_ip, client_mac)
        results[name] = success
        
        status = "UP" if success else "DOWN"
        timestamp = datetime.now().isoformat()
        
        message = f"[{timestamp}] {name} ({server_ip}): {status}"
        print(message)
        
        if log_file:
            with open(log_file, 'a') as f:
                f.write(message + '\n')
    
    return results

if __name__ == "__main__":
    servers = {
        'Primary': {
            'server_ip': '192.168.50.21',
            'client_ip': '192.168.50.10',
            'client_mac': '08:00:27:f3:27:23'
        },
        'Secondary': {
            'server_ip': '192.168.50.22',
            'client_ip': '192.168.50.10',
            'client_mac': '08:00:27:f3:27:23'
        }
    }
    
    results = monitor_dhcp_servers(servers, '/var/log/dhcp-monitor.log')
    
    # Exit with error if any server is down
    if not all(results.values()):
        sys.exit(1)
```

---

## Troubleshooting

### Issue: "permission denied" or "cannot bind to port"

**Problem**: dhcping requires root privileges or the ability to bind to UDP port 68.

**Solution 1: Use sudo**
```bash
sudo dhcping -c 192.168.50.10 -s 192.168.50.21 -h "08:00:27:f3:27:23"
```

**Solution 2: Configure sudo without password (not recommended)**
```bash
# In /etc/sudoers (use visudo)
your_user ALL=(ALL) NOPASSWD: /usr/bin/dhcping
```

**Solution 3: Use setcap (if available)**
```bash
sudo setcap cap_net_raw+p /usr/bin/dhcping
dhcping -c 192.168.50.10 -s 192.168.50.21 -h "08:00:27:f3:27:23"
```

### Issue: "no answer" - Server not responding

**Causes**:
1. DHCP server is down or unreachable
2. Network connectivity issue
3. Firewall blocking DHCP traffic
4. Server doesn't recognize client IP/MAC
5. Wrong server IP address

**Troubleshooting**:

```bash
# Verify connectivity to server
ping 192.168.50.21

# Check if port 67 is open
sudo nmap -sU -p 67 192.168.50.21

# Use verbose mode to see more details
sudo dhcping -v -c 192.168.50.10 -s 192.168.50.21 -h "08:00:27:f3:27:23"

# Try with longer timeout
sudo dhcping -w 5000 -c 192.168.50.10 -s 192.168.50.21 -h "08:00:27:f3:27:23"

# Check firewall rules
sudo iptables -L -n | grep 67
```

### Issue: Inconsistent Results / Timeouts

**Causes**:
1. Server slow to respond
2. Network congestion
3. Server under heavy load
4. Unreliable network link

**Solutions**:

```bash
# Increase timeout to allow slower responses
sudo dhcping -w 5000 -c 192.168.50.10 -s 192.168.50.21 -h "08:00:27:f3:27:23"

# Add retry logic in script
for attempt in 1 2 3; do
    if sudo dhcping -c 192.168.50.10 -s 192.168.50.21 -h "08:00:27:f3:27:23"; then
        echo "Success on attempt $attempt"
        break
    fi
    sleep 1
done
```

### Issue: "unable to determine interface"

**Cause**: Cannot find network interface to send from.

**Solution**: Specify interface explicitly with `-r` option:

```bash
sudo dhcping -r eth0 -c 192.168.50.10 -s 192.168.50.21 -h "08:00:27:f3:27:23"

# List available interfaces
ip link show
```

### Issue: Wrong source MAC address

**Problem**: The MAC address in the DHCP packet doesn't match what you specified.

**Verify with tcpdump**:

```bash
# In one terminal, monitor DHCP traffic
sudo tcpdump -i eth0 -n 'udp port 67 or udp port 68'

# In another terminal, run dhcping
sudo dhcping -c 192.168.50.10 -s 192.168.50.21 -h "08:00:27:f3:27:23"

# Check the CHADDR field in tcpdump output
```

---

## Security Considerations

### Non-Disruptive Testing

dhcping is safe for production networks:
- Does **not** acquire IP addresses
- Does **not** configure network interfaces
- Does **not** interfere with normal DHCP operations
- Is **read-only** in terms of network state changes

### Firewall and Access Control

```bash
# Ensure outbound UDP 67 traffic is allowed
sudo iptables -I OUTPUT -p udp --dport 67 -j ACCEPT

# Ensure inbound UDP 68 responses are allowed
sudo iptables -I INPUT -p udp --sport 67 --dport 68 -j ACCEPT
```

### Audit Logging

Many DHCP servers log all requests. dhcping requests appear in these logs:
- May trigger IDS/IPS alerts if policy disallows unknown MAC addresses
- Can be identified by the request pattern
- Should be documented in change control if used in production

### Authorized Use

Always obtain permission before testing DHCP servers:
1. Production environment testing requires change control
2. Inform network administrators of planned tests
3. Document test results for compliance/audit purposes
4. Use appropriate testing windows (off-hours if possible)
5. Monitor for any side effects during testing

---

## Advanced Configuration

### Testing Across VLAN Boundaries

If DHCP servers are on different VLANs:

```bash
# Ensure routing is configured properly
ip route show

# Test through routing interface
sudo dhcping -r eth0.100 -c 192.168.100.50 -s 192.168.1.21 -h "08:00:27:f3:27:23"
```

### Testing with DHCP Relays

If DHCP requests must pass through relay agents:

```bash
# Specify relay agent IP in GIADDR (if supported)
# Most implementations of dhcping do this automatically
sudo dhcping -c 192.168.50.10 -s 192.168.50.21 -h "08:00:27:f3:27:23"
```

### Load Testing DHCP Servers

Simple load test:

```bash
#!/bin/bash
# dhcp-load-test.sh

SERVER="192.168.50.21"
BASE_IP="192.168.50"
BASE_MAC="08:00:27:f3:27"
ITERATIONS=100
CONCURRENT=10

echo "Load Testing DHCP Server: $SERVER"
echo "Sending $ITERATIONS requests with $CONCURRENT concurrent threads"

for i in $(seq 1 $ITERATIONS); do
    # Generate test IP and MAC
    OCTET=$(( (i % 200) + 10 ))
    CLIENT_IP="$BASE_IP.$OCTET"
    MAC_LAST=$(printf "%02x\n" $(( i % 256 )))
    CLIENT_MAC="$BASE_MAC:00:$MAC_LAST"
    
    # Run in background with wait limit
    (
        if sudo dhcping -c "$CLIENT_IP" -s "$SERVER" -h "$CLIENT_MAC" > /dev/null 2>&1; then
            echo "✓ $i"
        else
            echo "✗ $i"
        fi
    ) &
    
    # Limit concurrent processes
    if (( i % CONCURRENT == 0 )); then
        wait
    fi
done

wait
echo "Load test complete"
```

---

## Summary and Best Practices

### Key Takeaways

1. **Lightweight Testing**: dhcping provides minimal-impact DHCP server testing
2. **Monitoring Integration**: Designed specifically for automated monitoring systems
3. **No Side Effects**: Tests without acquiring leases or configuring interfaces
4. **Specific Servers**: Tests one server at a time by design
5. **Quick Response**: Typically completes in milliseconds
6. **Production Safe**: Non-disruptive and appropriate for live networks

### Best Practices

1. **Always Use sudo**: Never skip privilege escalation
2. **Specify All Parameters**: Use `-c`, `-s`, and `-h` for reliable results
3. **Set Appropriate Timeouts**: Balance responsiveness with reliability
4. **Log Results**: Capture output for auditing and troubleshooting
5. **Monitor Trends**: Track response times for early problem detection
6. **Test Failover**: Regularly verify backup DHCP servers
7. **Document Changes**: Record configuration changes affecting DHCP
8. **Secure Access**: Restrict who can run dhcping on production systems

### Common Integration Patterns

- **Cron Jobs**: Periodic monitoring and reporting
- **Nagios/Icinga**: Integration as a service check plugin
- **Prometheus**: Custom exporter for metrics collection
- **Shell Scripts**: Bash wrappers for complex scenarios
- **Monitoring Agents**: SNMP or REST API integrations

### Next Steps

- Test in your lab environment first
- Develop monitoring scripts for your infrastructure
- Integrate with existing monitoring platforms
- Document your DHCP architecture
- Create runbooks for DHCP troubleshooting
- Train staff on DHCP diagnostics
