# DNSMASQ: A Comprehensive Guide to DNS/DHCP/TFTP/PXE Services

## Table of Contents
1. [Introduction](#introduction)
2. [Architecture and Components](#architecture-and-components)
3. [Installation and Setup](#installation-and-setup)
4. [DNS Configuration](#dns-configuration)
5. [DHCP Configuration](#dhcp-configuration)
6. [Advanced Features](#advanced-features)
7. [TFTP and PXE Boot](#tftp-and-pxe-boot)
8. [IPv6 Support](#ipv6-support)
9. [Security Features](#security-features)
10. [Performance Tuning](#performance-tuning)
11. [Practical Use Cases](#practical-use-cases)
12. [Troubleshooting](#troubleshooting)
13. [Integration and Automation](#integration-and-automation)

---

## Introduction

**dnsmasq** is a lightweight, single-process DNS, DHCP, TFTP, PXE, router advertisement and BOOTP server designed for small networks and embedded systems. It is intended to provide coupled DNS and DHCP services to a local area network (LAN).

### Key Characteristics

- **All-in-One Solution**: Provides DNS, DHCP, TFTP, PXE, and BOOTP services in one binary
- **Lightweight**: Minimal memory footprint (~5-10 MB), suitable for embedded systems and Raspberry Pi
- **Simple Configuration**: Single configuration file (/etc/dnsmasq.conf) with readable syntax
- **DNS Caching**: Built-in DNS caching with configurable TTLs
- **Dynamic DHCP**: Automatic hostname-to-IP mappings from DHCP leases
- **IPv4 and IPv6**: Full support for both address families
- **DNSSEC**: Optional DNSSEC validation for secure DNS
- **Authoritative DNS**: Can serve as authoritative DNS for local domains
- **No Dependencies**: Minimal external dependencies
- **POSIX Portable**: Runs on Linux, BSD, macOS, Windows (Cygwin), Solaris

### Primary Use Cases

- **Home Networks**: DHCP and DNS for home routers (OpenWrt, pfSense)
- **Lab Environments**: Test network infrastructure without commercial solutions
- **Embedded Systems**: DNS/DHCP on IoT devices, Raspberry Pi
- **Network Boot**: PXE boot servers for diskless workstations
- **DNS Caching**: Local DNS cache for all network clients
- **Network Isolation**: Separate DNS namespace for private networks
- **VLAN Management**: Per-VLAN DNS/DHCP configuration
- **Ad-Blocking**: Redirect advertisement domains locally
- **Development**: Local DNS names for development servers

### Advantages vs. ISC DHCP/BIND

| Feature | dnsmasq | ISC DHCP | BIND |
|---------|---------|----------|------|
| **Single Binary** | Yes | No (separate) | No |
| **Memory Usage** | ~5-10 MB | ~15-20 MB | 50+ MB |
| **Configuration Complexity** | Simple | Medium | Complex |
| **DHCP + DNS Integration** | Native | Requires extra config | Requires plugins |
| **IPv6 Support** | Excellent | Good | Excellent |
| **Ease of Setup** | Very Easy | Medium | Difficult |
| **Suitable for Embedded** | Yes | Yes | No |
| **PXE/TFTP** | Built-in | Via plugin | Via plugin |

---

## Architecture and Components

### System Architecture

```
┌─────────────────────────────────────────────────────┐
│ dnsmasq Single Process                              │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ DNS Forwarder (Port 53 UDP/TCP)             │   │
│  ├─────────────────────────────────────────────┤   │
│  │ - Caches responses from upstream servers    │   │
│  │ - Answers from /etc/hosts                   │   │
│  │ - Answers from DHCP leases                  │   │
│  │ - Authoritative for configured domains      │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ DHCP Server (Port 67 UDP)                   │   │
│  ├─────────────────────────────────────────────┤   │
│  │ - Assigns addresses from configured ranges  │   │
│  │ - Updates DNS with assigned names           │   │
│  │ - Supports static leases                    │   │
│  │ - IPv4 and IPv6 support                     │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ TFTP Server (Port 69 UDP)                   │   │
│  ├─────────────────────────────────────────────┤   │
│  │ - Serves boot files for PXE clients         │   │
│  │ - Supports blocksize negotiation            │   │
│  │ - Read-only mode supported                  │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ PXE Server (Port 4011 UDP)                  │   │
│  ├─────────────────────────────────────────────┤   │
│  │ - Provides PXE boot configuration           │   │
│  │ - Proxy mode support                        │   │
│  │ - Architecture detection (x86, x86-64, ARM) │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ BOOTP Server (Port 67 UDP)                  │   │
│  ├─────────────────────────────────────────────┤   │
│  │ - Legacy BOOTP protocol support             │   │
│  │ - Backward compatibility                    │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ Router Advertisement (ICMPv6)               │   │
│  ├─────────────────────────────────────────────┤   │
│  │ - IPv6 RA for stateless autoconfiguration   │   │
│  │ - Prefix delegation                         │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ Configuration & Lease Management             │   │
│  ├─────────────────────────────────────────────┤   │
│  │ - Reads /etc/dnsmasq.conf                   │   │
│  │ - Reads /etc/hosts                          │   │
│  │ - Stores/manages leases in /var/lib/dnsmasq│   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Core Concepts

**DNS Forwarding**: dnsmasq acts as a DNS forwarding cache. When a client queries for a domain:

1. **Local Check**: Does it exist in /etc/hosts or DHCP leases? → Answer directly
2. **Cache Check**: Is it in the DNS cache? → Answer from cache
3. **Local Domain Check**: Is it in a configured local domain? → Answer locally or fail
4. **Upstream Forward**: Not known locally → Forward to upstream DNS server
5. **Caching**: Store result in cache for future queries

**DHCP Integration**: Unlike separate DHCP and DNS:

1. When DHCP assigns an address to a client, dnsmasq automatically creates a DNS entry
2. Clients can find each other by hostname without manual DNS configuration
3. Hostnames from /etc/hosts are automatically added to DNS
4. DHCP leases file is shared with DNS for integration

**Port Binding**: dnsmasq binds to specific ports:

- **UDP 53**: DNS queries (both forward and reverse)
- **TCP 53**: DNS zone transfers and large responses
- **UDP 67**: DHCP server
- **UDP 68**: BOOTP (included in DHCP)
- **UDP 69**: TFTP server
- **UDP 4011**: PXE server (proxy DHCP)
- **ICMPv6**: Router Advertisements (IPv6)

---

## Installation and Setup

### Linux Installation

**Ubuntu/Debian**:

```bash
sudo apt update
sudo apt install dnsmasq

# Verify installation
dnsmasq --version
which dnsmasq
```

**Fedora/RHEL/CentOS**:

```bash
sudo dnf install dnsmasq

# Or
sudo yum install dnsmasq
```

**Arch Linux**:

```bash
sudo pacman -S dnsmasq
```

**Alpine Linux** (minimal):

```bash
apk add dnsmasq
```

### macOS Installation

```bash
brew install dnsmasq

# Start as daemon
brew services start dnsmasq

# Configuration location
/usr/local/etc/dnsmasq.conf
```

### FreeBSD Installation

```bash
pkg install dnsmasq

# Enable and start
sysrc dnsmasq_enable=YES
service dnsmasq start
```

### Verification

```bash
# Check version
dnsmasq --version

# Test configuration syntax
dnsmasq --test

# Show help
dnsmasq --help
dnsmasq --help dhcp     # DHCP options
dnsmasq --help dhcp6    # DHCPv6 options
```

### Starting the Service

**As Systemd Service** (Linux):

```bash
# Enable at boot
sudo systemctl enable dnsmasq

# Start service
sudo systemctl start dnsmasq

# Check status
sudo systemctl status dnsmasq

# View logs
sudo journalctl -u dnsmasq -f
```

**As OpenRC Service** (Alpine/Gentoo):

```bash
sudo rc-service dnsmasq start
sudo rc-update add dnsmasq default
```

**Manual Foreground** (for debugging):

```bash
# Run in foreground without daemonizing
sudo dnsmasq -d -q
```

---

## DNS Configuration

### Basic DNS Setup

The simplest DNS configuration forwards queries to upstream servers:

```bash
# /etc/dnsmasq.conf

# Listen on specific address
listen-address=::1,127.0.0.1,192.168.1.10

# Set cache size (number of entries)
cache-size=150

# Upstream DNS servers
server=8.8.8.8          # Google
server=1.1.1.1          # Cloudflare

# Enable IPv6
server=2001:4860:4860::8888  # Google IPv6

# Never forward certain queries
domain-needed           # Don't forward plain names
bogus-priv             # Don't forward private IPs
```

### Upstream DNS Configuration

**Single Upstream Server**:

```
server=8.8.8.8
```

**Multiple Upstream Servers**:

```
server=8.8.8.8          # Google
server=1.1.1.1          # Cloudflare
server=9.9.9.9          # Quad9
```

**Domain-Specific Upstream**:

```
# Corporate DNS for internal domain
server=/internal.company.com/192.168.1.1

# ISP DNS for some domains
server=/isp.local/192.168.0.1

# Use specific server for specific domain
server=/google.com/1.2.3.4
server=/gmail.google.com/2.3.4.5    # More specific takes precedence
```

**Non-Standard DNS Port**:

```
server=8.8.8.8#5353    # Port 5353 instead of 53
```

**Server Ordering**:

```
# By default, dnsmasq tries servers in parallel
# Force sequential ordering:
strict-order

# Or query ALL servers for redundancy:
all-servers
```

### Local DNS Names

**Using /etc/hosts**:

```bash
# /etc/hosts

127.0.0.1       localhost
::1             localhost
192.168.1.1     router
192.168.1.10    dnsmasq.local dnsmasq
192.168.1.20    server1.local server1
192.168.1.30    server2.local server2
```

dnsmasq reads /etc/hosts and makes names resolvable via DNS.

**Additional Hosts Files**:

```
# Read additional hosts files
addn-hosts=/etc/hosts.local
addn-hosts=/etc/hosts.d/

# Or watch directory for changes
hostsdir=/etc/dnsmasq.hosts.d
```

### DNS Records

**A Records (IPv4)**:

```
# Redirect doubleclick.net to local IP
address=/doubleclick.net/127.0.0.1

# Redirect entire domain
address=/ads.example.com/0.0.0.0
```

**AAAA Records (IPv6)**:

```
# IPv6 address
address=/example.com/fe80::1
```

**CNAME Records**:

```
# Create alias
cname=www.example.local,example.local
cname=mail.example.local,example.local
```

**MX Records**:

```
# Mail exchange record
mx-host=example.com,mail.example.com,10
mx-host=example.com,mail2.example.com,20

# Default MX target
mx-target=mail.example.com
localmx                # All local hosts have MX record
```

**SRV Records**:

```
# LDAP server location
srv-host=_ldap._tcp.example.com,ldapserver.example.com,389

# Multiple SRV with priorities
srv-host=_ldap._tcp.example.com,ldap1.example.com,389,1
srv-host=_ldap._tcp.example.com,ldap2.example.com,389,2
```

**TXT Records**:

```
# SPF record
txt-record=example.com,v=spf1 a -all

# DMARC record
txt-record=_dmarc.example.com,v=DMARC1;p=none;
```

**PTR Records**:

```
# Reverse DNS
ptr-record=1.0.0.127.in-addr.arpa,localhost
```

### Authoritative DNS

**Local Authority for Domain**:

```
# Be authoritative for example.com
local=/example.com/

# Clients will resolve example.com from this dnsmasq only
# Never forwarded upstream
```

**Authoritative Zone with Auth-Server**:

```
# Enable authoritative DNS
auth-server=dnsmasq.example.com,192.168.1.10

# Configure authoritative zone
auth-zone=example.com,192.168.1.0/24
```

### DNS Caching Control

**Cache Size**:

```
# Default 150 entries, 4000 bytes each
cache-size=150

# Increase for larger networks
cache-size=1000

# Disable caching
cache-size=0
```

**TTL Control**:

```
# TTL for local records from /etc/hosts
local-ttl=3600          # 1 hour

# TTL for DHCP-assigned names
dhcp-ttl=600            # 10 minutes

# TTL for negative responses (NXDOMAIN)
neg-ttl=600

# Maximum TTL returned to clients
max-ttl=3600

# Maximum TTL stored in cache
max-cache-ttl=7200
```

**Log Queries**:

```
# Log all DNS queries
log-queries

# Extra verbose logging
log-queries=extra       # Includes query ID and requester IP

# Protocol-level logging
log-queries=proto       # Also shows UDP/TCP
```

---

## DHCP Configuration

### Basic DHCP Setup

**Simple DHCP Range**:

```
# Enable DHCP on eth0
interface=eth0

# DHCP address range with 24-hour lease
dhcp-range=192.168.1.100,192.168.1.200,24h

# Set router (gateway)
dhcp-option=option:router,192.168.1.1

# Set DNS servers
dhcp-option=option:dns-server,192.168.1.10
```

**Multiple Subnets**:

```
# LAN
interface=eth0
dhcp-range=192.168.1.100,192.168.1.200,24h
dhcp-option=option:router,192.168.1.1

# DMZ
interface=eth1
dhcp-range=192.168.100.50,192.168.100.150,24h
dhcp-option=option:router,192.168.100.1
```

### Static DHCP Leases

**By MAC Address**:

```
# Always assign 192.168.1.50 to this MAC
dhcp-host=11:22:33:44:55:66,192.168.1.50

# With hostname
dhcp-host=11:22:33:44:55:66,workstation,192.168.1.50

# With infinite lease
dhcp-host=11:22:33:44:55:66,workstation,192.168.1.50,infinite
```

**By Hostname**:

```
# Define in /etc/hosts then reference
# /etc/hosts:
# 192.168.1.50  workstation

# /etc/dnsmasq.conf:
dhcp-host=workstation

# Will serve configured IP to host named "workstation"
```

**Multiple MACs for Same IP** (laptop docking):

```
# Laptop may have wired and wireless MACs
dhcp-host=11:22:33:44:55:66,aa:bb:cc:dd:ee:ff,laptop,192.168.1.50
```

### DHCP Options

**Common Options**:

```
# Router/Gateway
dhcp-option=option:router,192.168.1.1

# DNS Servers
dhcp-option=option:dns-server,192.168.1.10,8.8.8.8

# Domain Name
dhcp-option=option:domain-name,example.local

# Domain Search List
dhcp-option=option:domain-search,example.local,internal.example.com

# NTP Servers
dhcp-option=option:ntp-server,192.168.1.11,time.nist.gov

# Broadcast Address
dhcp-option=option:broadcast,192.168.1.255

# Subnet Mask
dhcp-option=option:netmask,255.255.255.0
```

**Windows-Specific Options**:

```
# WINS/NetBIOS nameserver
dhcp-option=option:netbios-ns,192.168.1.11

# WINS datagram distribution server
dhcp-option=option:netbios-dgm-server,192.168.1.11

# NetBIOS scope
dhcp-option=option:netbios-scope,workgroup

# Windows Internet Name Service (WINS)
dhcp-option=44,192.168.1.11
```

### DHCP Tagging System

**Vendor-Based Options**:

```
# Send specific options to Linux clients
dhcp-vendorclass=set:linux,Linux

# Send options only to devices with "Linux" in vendor string
dhcp-option=tag:linux,option:classless-static-route,10.0.0.0/24,192.168.1.1

# iPhone/iPad specific
dhcp-vendorclass=set:apple,Apple*
dhcp-option=tag:apple,option:wpad,http://proxy.example.com/wpad.dat
```

**MAC-Based Tagging**:

```
# Tag devices by MAC prefix
dhcp-mac=set:printers,00:11:22:*:*:*

# Send specific options to tagged devices
dhcp-option=tag:printers,option:ntp-server,192.168.1.11
```

**Client Class Tagging**:

```
# Tag based on user-class
dhcp-userclass=set:accounts,accounts

# Send options only to accounts department
dhcp-option=tag:accounts,option:routers,192.168.1.10
```

**Conditional Tags**:

```
# Tag wired vs wireless
dhcp-mac=set:wired,*
# (all devices get 'wired' tag by default)

# Interface-based tagging
tag-if=set:vlan100,tag:eth0
tag-if=set:vlan200,tag:eth1

# Send different options per interface
dhcp-option=tag:vlan100,option:router,192.168.100.1
dhcp-option=tag:vlan200,option:router,192.168.200.1
```

### Lease Management

**Lease File**:

```
# Where dnsmasq stores DHCP leases
dhcp-leasefile=/var/lib/dnsmasq/dnsmasq.leases

# Script to run when lease created/destroyed
dhcp-script=/usr/local/bin/dhcp-update.sh
```

**Lease File Format**:

```
# Example /var/lib/dnsmasq/dnsmasq.leases:
# expires_epoch client-id MAC-address IP-address hostname
1735000000 01:aa:bb:cc:dd:ee:ff aa:bb:cc:dd:ee:ff 192.168.1.101 laptop
1735086400 01:11:22:33:44:55:66 11:22:33:44:55:66 192.168.1.102 workstation
```

**Authoritative Mode**:

```
# dnsmasq takes over all leases on network
# Useful for DHCP failover scenarios
dhcp-authoritative
```

### Advanced DHCP Features

**Rapid Commit (RFC 4039)**:

```
# Server responds immediately to client discovery
# Must be only DHCP server on segment
dhcp-rapid-commit
```

**Ignore Certain Clients**:

```
# Don't serve DHCP to unknown clients
dhcp-ignore=tag:!known

# Only serve DHCP to listed clients
dhcp-host=11:22:33:44:55:66,workstation,192.168.1.50
dhcp-host=aa:bb:cc:dd:ee:ff,laptop,192.168.1.51
```

**Lease Time Calculation**:

```
# Default lease time
dhcp-range=192.168.1.100,192.168.1.200,12h

# T1 (renewal time, usually 50% of lease)
dhcp-option=option:T1,6h

# T2 (rebinding time, usually 87.5% of lease)
dhcp-option=option:T2,10h
```

---

## Advanced Features

### IPv6 Support

**DHCPv6**:

```
# Enable DHCPv6 with prefix length
dhcp-range=2001:db8::100,2001:db8::200,64,12h

# Router Advertisements
enable-ra

# Stateless DHCP only (clients use SLAAC)
dhcp-range=2001:db8::,ra-stateless

# Stateless DHCP with names for SLAAC addresses
dhcp-range=2001:db8::,ra-names
```

**IPv6 Options**:

```
# DNS servers for IPv6
dhcp-option=option6:dns-server,[2001:4860:4860::8888],[2001:4860:4860::8844]

# Domain search for IPv6
dhcp-option=option6:domain-search,example.com
```

### DNSSEC Validation

**Enable DNSSEC**:

```
# Validate DNSSEC signatures
dnssec

# Trust anchors configuration
conf-file=/etc/dnsmasq/trust-anchors.conf

# Check unsigned zones properly
dnssec-check-unsigned
```

### Connection Tracking & Filtering

**Netfilter Integration**:

```
# Add DNS results to iptables ipsets
ipset=/youtube.com/google.com/streaming

# For nftables (newer firewall)
nftset=/youtube.com/ip#filter#streaming
nftset=/youtube.com/6#ip#filter#streaming6
```

**Connection Mark Filtering**:

```
# Allow DNS queries based on connmark
connmark-allowlist-enable=0xf0

# Specific DNS patterns per connmark
connmark-allowlist=0x10,google.com,youtube.com
connmark-allowlist=0x20,facebook.com,instagram.com
```

---

## TFTP and PXE Boot

### Basic TFTP Server

```
# Enable TFTP server
enable-tftp

# Set root directory for TFTP files
tftp-root=/var/tftp

# Fail gracefully if directory missing
tftp-no-fail

# Only serve files owned by dnsmasq user
tftp-secure

# Disable blocksize negotiation (for broken clients)
tftp-no-blocksize
```

### PXE Boot Configuration

**Simple PXE Boot**:

```
# Serve pxelinux bootloader
dhcp-boot=pxelinux.0

# With TFTP server location
dhcp-boot=pxelinux.0,tftp.example.com,192.168.1.10

# With custom root path
dhcp-boot=/pxelinux/pxelinux.0,server.local,192.168.1.10
```

**Architecture-Specific PXE**:

```
# Detect client architecture
dhcp-match=peecees,option:client-arch,0        # x86
dhcp-match=itanics,option:client-arch,2        # IA64
dhcp-match=hammers,option:client-arch,6        # x86-64
dhcp-match=mactels,option:client-arch,7        # EFI x86-64
dhcp-match=arm,option:client-arch,8            # ARM

# Boot different files per architecture
dhcp-boot=tag:peecees,pxelinux.0
dhcp-boot=tag:hammers,pxelinux64.0
dhcp-boot=tag:arm,bootarm.efi
```

**PXE Menu**:

```
# Interactive PXE boot menu
pxe-prompt="Press F8 for menu"
pxe-prompt="Press F8 for menu.",30      # 30-second timeout

# Boot options
pxe-service=x86PC,"Boot from local disk"
pxe-service=x86PC,"Linux Install",pxelinux
pxe-service=x86PC,"Windows Install via RIS",1,192.168.1.20
```

**iPXE Boot**:

```
# First load iPXE
dhcp-boot=undionly.kpxe

# Detect iPXE capability
dhcp-match=set:ipxe,175                # iPXE sends option 175

# Boot real OS via iPXE
dhcp-boot=tag:ipxe,http://boot.ipxe.org/boot.php
```

---

## Performance Tuning

### Cache Optimization

```
# Increase cache for fewer upstream queries
cache-size=10000

# Set minimum TTL for short-lived records
min-cache-ttl=300      # Don't cache below 5 minutes

# Set maximum TTL to reduce cache bloat
max-cache-ttl=86400    # Cap at 24 hours
```

### Connection and Query Handling

```
# Maximum concurrent connections
dhcp-lease-max=1000

# Maximum queries per second
query-port=0           # Single port (faster but less secure)

# Multiple ports for redundancy
port-limit=5           # Use up to 5 different ports

# Source port range for outbound queries
min-port=10000
max-port=60000
```

### Logging Performance

```
# Asynchronous logging to avoid blocking
log-async=25           # Queue up to 25 log lines

# Use syslog instead of direct file
log-facility=LOCAL0

# Reduce log verbosity in production
# (remove or comment out log-queries)
```

### Memory Optimization

```
# Reduce cache if memory-constrained
cache-size=100         # Minimal cache

# Limit number of DHCP leases
dhcp-lease-max=100     # Small network only

# Disable TFTP if not needed
# (just don't include enable-tftp)
```

---

## Practical Use Cases

### Home Network Setup

```
# /etc/dnsmasq.conf

# Interface configuration
interface=eth0
listen-address=192.168.1.10

# DNS Configuration
cache-size=500
server=8.8.8.8
server=1.1.1.1
domain-needed
bogus-priv
local=/home.local/

# DHCP Configuration
dhcp-range=192.168.1.100,192.168.1.200,24h
dhcp-option=option:router,192.168.1.1
dhcp-option=option:dns-server,192.168.1.10
dhcp-option=option:domain-name,home.local

# Static leases for common devices
dhcp-host=aa:bb:cc:dd:ee:01,laptop,192.168.1.101
dhcp-host=aa:bb:cc:dd:ee:02,desktop,192.168.1.102
dhcp-host=aa:bb:cc:dd:ee:03,printer,192.168.1.50,infinite

# Logging
log-queries
log-facility=/var/log/dnsmasq.log
```

### Ad-Blocking Setup

```
# /etc/dnsmasq.conf

# Block common ad servers
address=/doubleclick.net/0.0.0.0
address=/google-analytics.com/0.0.0.0
address=/ads.google.com/0.0.0.0
address=/pagead2.googlesyndication.com/0.0.0.0
address=/adserver.com/0.0.0.0

# Or use external blocklist (requires update script)
# addn-hosts=/etc/dnsmasq/blocklist.txt

# Or use domain-based blocking
server=/ads.example.com/127.0.0.1
server=/tracker.example.com/127.0.0.1

# Redirect to local page instead
address=/ads.example.com/192.168.1.10  # Local web server shows "blocked"
```

### Lab Environment Setup

```
# /etc/dnsmasq.conf

# Lab domain
domain=lab.local
local=/lab.local/

# DNS for lab servers
address=/dns.lab.local/192.168.100.10
address=/dhcp.lab.local/192.168.100.10
address=/web.lab.local/192.168.100.20
address=/db.lab.local/192.168.100.21
address=/app.lab.local/192.168.100.22

# Explicit DHCP leases for lab equipment
dhcp-range=192.168.100.100,192.168.100.200,24h
dhcp-host=00:11:22:33:44:55,server1,192.168.100.30
dhcp-host=00:11:22:33:44:66,server2,192.168.100.31
dhcp-host=00:11:22:33:44:77,client1,192.168.100.101

# TFTP for PXE boot testing
enable-tftp
tftp-root=/var/tftp

# Logging for troubleshooting
log-queries=extra
log-dhcp
```

### Enterprise Network Setup

```
# /etc/dnsmasq.conf

# Multiple VLANs
# VLAN 10 - Corporate
interface=eth0.10
listen-address=192.168.10.10
dhcp-range=tag:corp,192.168.10.100,192.168.10.200,24h
dhcp-option=tag:corp,option:router,192.168.10.1
dhcp-option=tag:corp,option:domain-name,corp.example.com

# VLAN 20 - Guest
interface=eth0.20
listen-address=192.168.20.10
dhcp-range=tag:guest,192.168.20.100,192.168.20.200,12h
dhcp-option=tag:guest,option:router,192.168.20.1
dhcp-option=tag:guest,option:domain-name,guest.example.com

# DNS for internal domains
server=/corp.example.com/192.168.10.1
server=/example.com/8.8.8.8

# DHCP scripting for updates
dhcp-script=/opt/dnsmasq/update-dns.sh

# Logging for auditing
log-queries=extra
log-facility=/var/log/dnsmasq-audit.log
```

---

## Troubleshooting

### Configuration Issues

**Syntax Check**:

```bash
# Validate configuration without starting
sudo dnsmasq --test

# Output on error:
# dnsmasq: syntax check OK.
```

**Common Errors**:

```bash
# Port already in use
# Error: Failed to bind port 53

# Solution: Find what's using port
sudo lsof -i :53
sudo netstat -tlnp | grep 53

# Kill competing service
sudo systemctl stop systemd-resolved  # Ubuntu
sudo systemctl stop named              # BIND
```

### DNS Issues

**DNS Not Resolving**:

```bash
# Test DNS locally
dig @127.0.0.1 example.com

# Check if upstream servers reachable
nslookup 8.8.8.8
nslookup example.com 8.8.8.8

# Check dnsmasq logs
sudo journalctl -u dnsmasq -n 50
```

**DHCP Clients Can't Resolve**:

```bash
# Verify DHCP option 6 (DNS servers) is set
dhcpdump -i eth0 | grep "DNS"

# Check client received correct DNS
cat /etc/resolv.conf    # On DHCP client

# Ensure dnsmasq listens on DHCP interface
sudo netstat -tlnup | grep dnsmasq
```

### DHCP Issues

**Clients Not Getting Leases**:

```bash
# Check DHCP logs
sudo journalctl -u dnsmasq -n 100 | grep DHCP

# Verify DHCP range is configured
grep dhcp-range /etc/dnsmasq.conf

# Check if address pool exhausted
sudo tail -20 /var/lib/dnsmasq/dnsmasq.leases

# Verify interface configuration
ip addr show
```

**Lease Renewal Issues**:

```bash
# Clear old leases
sudo systemctl stop dnsmasq
sudo rm /var/lib/dnsmasq/dnsmasq.leases
sudo systemctl start dnsmasq

# Force client to renew
sudo dhclient -r              # Release
sudo dhclient eth0            # Renew
```

### Performance Issues

**High CPU Usage**:

```bash
# Check what's being logged
grep "log-" /etc/dnsmasq.conf

# Disable query logging if excessive
# Comment out: log-queries

# Check cache hit rate
# (requires recompile with stats support)
```

**Slow DNS Resolution**:

```bash
# Check upstream server response times
time dig @8.8.8.8 example.com

# Try different upstream
server=1.1.1.1      # Try Cloudflare

# Monitor cache effectiveness
# (check if same queries repeat)
```

---

## Integration and Automation

### NetworkManager Integration

dnsmasq can be used as NetworkManager plugin:

```bash
# /etc/NetworkManager/conf.d/dns.conf
[main]
dns=dnsmasq

# Create per-connection dnsmasq config
mkdir -p /etc/NetworkManager/dnsmasq.d/

# Add connection-specific config
echo "address=/corp.example.com/192.168.1.1" > \
  /etc/NetworkManager/dnsmasq.d/corporate.conf

# Reload NetworkManager
sudo nmcli general reload
```

### Systemd Integration

**Service Unit**:

```ini
# /etc/systemd/system/dnsmasq.service
[Unit]
Description=dnsmasq DNS/DHCP Server
After=network-online.target

[Service]
Type=forking
PIDFile=/run/dnsmasq.pid
ExecStartPre=/usr/sbin/dnsmasq --test
ExecStart=/usr/sbin/dnsmasq
ExecReload=/bin/kill -HUP $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Monitoring Integration

**Prometheus Metrics**:

```bash
# Simple script to export cache stats
cat > /usr/local/bin/dnsmasq-exporter.sh << 'EOF'
#!/bin/bash
# Query dnsmasq cache via ubus
echo "# HELP dnsmasq_cache_size Cache entries"
echo "# TYPE dnsmasq_cache_size gauge"

# Requires dnsmasq compiled with ubus support
ubus call dnsmasq stats | jq '.cache_size'
EOF
```

**Logging to Syslog**:

```
# Send logs to syslog for centralization
log-facility=LOG_LOCAL0

# Forward to syslog aggregation:
# rsyslog, syslog-ng, or journald
```

### Backup and Recovery

**Configuration Backup**:

```bash
# Backup main config
sudo cp /etc/dnsmasq.conf /etc/dnsmasq.conf.backup

# Backup DHCP leases
sudo cp /var/lib/dnsmasq/dnsmasq.leases \
  /var/lib/dnsmasq/dnsmasq.leases.backup

# Version control (recommended)
cd /etc
sudo git init
sudo git add dnsmasq.conf
sudo git commit -m "Initial dnsmasq config"
```

**Recovery Procedure**:

```bash
# Stop service
sudo systemctl stop dnsmasq

# Restore config
sudo cp /etc/dnsmasq.conf.backup /etc/dnsmasq.conf

# Test syntax
sudo dnsmasq --test

# Restore leases (optional)
sudo cp /var/lib/dnsmasq/dnsmasq.leases.backup \
  /var/lib/dnsmasq/dnsmasq.leases

# Restart
sudo systemctl start dnsmasq
```

---

## Summary and Best Practices

### Key Strengths of dnsmasq

1. **All-in-One Solution**: DNS + DHCP + TFTP + PXE in single binary
2. **Lightweight**: Perfect for embedded systems and routers
3. **Simple Configuration**: Human-readable config file
4. **DNS/DHCP Integration**: Automatic hostname registration
5. **Zero-Configuration Networking**: Works without complex setup
6. **IPv6 Support**: Full DHCPv6 and IPv6 capabilities
7. **Flexible Tagging System**: Advanced DHCP behavior customization
8. **DNSSEC Support**: Optional DNS security
9. **Wide Compatibility**: Runs on everything from IoT to servers

### Configuration Best Practices

1. **Use Configuration File**: Keep settings in /etc/dnsmasq.conf
2. **Test Before Deployment**: Always run `dnsmasq --test`
3. **Document Custom Settings**: Comment your configuration
4. **Monitor Logs**: Regularly check logs for issues
5. **Backup Configuration**: Version control your config
6. **Gradual Rollout**: Test on small networks first
7. **Use Tags**: Leverage tagging for complex networks
8. **Set Appropriate TTLs**: Balance between freshness and load
9. **Secure TFTP**: Enable tftp-secure if needed
10. **Plan for Redundancy**: Run multiple dnsmasq instances

### Common Pitfalls to Avoid

1. **Conflicting Servers**: Don't run multiple DNS/DHCP on same network
2. **Wrong Interface**: Verify dnsmasq listens on correct interface
3. **Lease Pool Too Small**: Ensure DHCP range has enough addresses
4. **Cache Size Too Large**: Wastes memory for small networks
5. **Missing Upstream Servers**: Always configure upstream DNS
6. **No Local Domain**: Use local= for private domains
7. **Insecure TFTP**: Enable tftp-secure if serving boot files
8. **Excessive Logging**: log-queries can slow down busy servers
9. **Old Config Files**: Test after OS upgrades
10. **No Monitoring**: Set up monitoring/alerting for production

### Next Steps

- Deploy dnsmasq in your lab environment
- Integrate with existing infrastructure
- Set up monitoring and alerting
- Document your configuration
- Train team on dnsmasq management
- Plan for high availability if needed
- Regularly review logs and performance
- Keep dnsmasq updated with security patches
