# ENUM4LINUX: A Comprehensive Guide to SMB/RPC/LDAP Enumeration

## Table of Contents
1. [Introduction](#introduction)
2. [SMB Protocol Fundamentals](#smb-protocol-fundamentals)
3. [How ENUM4LINUX Works](#how-enum4linux-works)
4. [Installation and Setup](#installation-and-setup)
5. [Basic Syntax and Usage](#basic-syntax-and-usage)
6. [Core Enumeration Techniques](#core-enumeration-techniques)
7. [Command-Line Options Reference](#command-line-options-reference)
8. [Practical Usage Examples](#practical-usage-examples)
9. [Advanced Enumeration Techniques](#advanced-enumeration-techniques)
10. [ENUM4LINUX-NG (Python Version)](#enum4linux-ng-python-version)
11. [Troubleshooting and Optimization](#troubleshooting-and-optimization)
12. [Integration with Other Tools](#integration-with-other-tools)
13. [Security Considerations](#security-considerations)

---

## Introduction

**enum4linux** is a powerful SMB enumeration tool that extracts detailed information from Windows and Samba systems on a network. Originally written in Perl as enum4linux.pl, it has evolved to include enum4linux-ng, a modernized Python rewrite with enhanced features.

### Key Characteristics

- **Comprehensive Enumeration**: Extracts users, groups, shares, policies, and OS information
- **Multiple Protocols**: Works via SMB, RPC (MS-RPC), LDAP, and NetBIOS
- **Wrapper Tool**: Combines Samba tools (nmblookup, net, rpcclient, smbclient) into one interface
- **RID Cycling**: Enumerate users through relative identifier enumeration
- **Null Session Support**: Exploit null sessions when available
- **Authentication Options**: Supports passwords, NTLM hashes, Kerberos tickets
- **Structured Output**: JSON/YAML export (enum4linux-ng only)
- **Active Directory Ready**: Designed for Windows domain enumeration
- **No Root Required**: Works as non-privileged user (unlike some SMB tools)

### Primary Use Cases

- **Reconnaissance Phase**: Gather domain information during penetration testing
- **User Enumeration**: Discover user accounts for password spraying
- **Share Enumeration**: Identify accessible file shares
- **Password Policy Analysis**: Understand security baselines
- **OS Fingerprinting**: Determine operating system and version
- **Group Membership**: Map organizational structure
- **Active Directory Mapping**: Collect domain information
- **Vulnerability Assessment**: Identify misconfigurations

### Limitations

- **Slow RID Cycling**: Can be time-intensive on large domains (improved in ng version)
- **Noisy**: Generates significant SMB traffic (easily detected)
- **Credential Dependent**: More information available with valid credentials
- **Not Stealth**: Obvious reconnaissance patterns
- **Samba Dependency**: Requires Samba tools on system
- **Network Only**: Cannot test local system (is network reconnaissance tool)

---

## SMB Protocol Fundamentals

### SMB Overview

**SMB (Server Message Block)** is a network protocol used for sharing files, printers, and other resources on Windows networks. It operates at the application layer and uses:

- **Port 139** (NetBIOS over TCP): Legacy SMB (SMBv1)
- **Port 445** (Direct TCP): Modern SMB (SMBv2/SMBv3)

### SMB Protocol Stack

```
┌─────────────────────────────────────────┐
│ Application (File Sharing, Print Queue) │
├─────────────────────────────────────────┤
│ CIFS (Common Internet File System)      │
├─────────────────────────────────────────┤
│ SMB (Server Message Block)              │
│ ├─ SMBv1 (deprecated)                   │
│ ├─ SMBv2 (Windows Vista+)               │
│ └─ SMBv3 (Windows 8+)                   │
├─────────────────────────────────────────┤
│ NetBIOS / Direct TCP                    │
├─────────────────────────────────────────┤
│ TCP Port 139 or 445                     │
└─────────────────────────────────────────┘
```

### Related Protocols Enumerated by ENUM4LINUX

**RPC (Remote Procedure Call)**
- Used for domain controller communication
- MS-RPC: Microsoft's RPC implementation
- Allows remote function invocation across network
- Key for querying domain information

**LDAP (Lightweight Directory Access Protocol)**
- Directory service protocol
- Used by Active Directory
- Can be used for user and group enumeration
- More reliable than RPC for domain info

**NetBIOS**
- Name resolution protocol
- Provides computer names and workgroup info
- Legacy but still used by Windows

### SMB Shares and Sessions

**Administrative Shares** (Always present):
- `IPC$` - Interprocess communication (hidden, commonly used)
- `C$` - Drive access (hidden, admin only)
- `D$`, `E$`, etc. - Other drives (hidden, admin only)
- `ADMIN$` - Remote administration (hidden, admin only)

**User Shares**:
- Named shares created by administrators
- May contain files and folders
- Permissions control access

**Null Sessions**:
- Authentication without username/password
- Allows some enumeration even without credentials
- Increasingly restricted in modern Windows

---

## How ENUM4LINUX Works

### Underlying Mechanisms

ENUM4LINUX is essentially a sophisticated wrapper around four Samba command-line tools:

```
┌─────────────────────────────────────────┐
│ ENUM4LINUX (Perl or Python)             │
├─────────────────────────────────────────┤
│ Orchestrates and parses output from:    │
│                                         │
│ 1. nmblookup                            │
│    └─ NetBIOS name queries              │
│                                         │
│ 2. net                                  │
│    └─ Samba net command (RPC wrapper)   │
│                                         │
│ 3. rpcclient                            │
│    └─ Direct RPC queries                │
│                                         │
│ 4. smbclient                            │
│    └─ SMB file share access             │
│                                         │
└─────────────────────────────────────────┘
```

### Enumeration Flow

```
1. Target Specification
   └─ enum4linux [options] target_ip

2. Connection Testing
   ├─ Attempt null session (no credentials)
   ├─ Attempt authentication (if credentials provided)
   └─ Verify SMB/RPC accessibility

3. Protocol Selection
   ├─ Check if SMB available (port 445/139)
   ├─ Check if LDAP available (port 389/636)
   └─ Check if RPC available (port 135)

4. NetBIOS Enumeration (if -N specified)
   ├─ Use nmblookup for name resolution
   ├─ Extract workgroup/domain
   └─ Retrieve NetBIOS name cache

5. User Enumeration (if -U specified)
   ├─ Via RPC: enumdomusers command
   ├─ Via RID cycling: query SID repeatedly
   └─ Build user list with SIDs

6. Group Enumeration (if -G specified)
   ├─ Via RPC: enumdomgroups command
   ├─ Enumerate group members (if -Gm)
   └─ Map group structure

7. Share Enumeration (if -S specified)
   ├─ Use smbclient to list shares
   ├─ Attempt to map each share
   ├─ Test read/write permissions
   └─ Report accessible shares

8. Policy Enumeration (if -P specified)
   ├─ Query password policy via RPC
   ├─ Query lockout policy
   └─ Retrieve account policies

9. OS Enumeration (if -O specified)
   ├─ Query server info via RPC
   ├─ Retrieve OS version
   └─ Get system uptime

10. LDAP Enumeration (if -L specified)
    ├─ Query DC information
    ├─ Enumerate users via LDAP
    └─ Retrieve domain trusts

11. RID Cycling (if -R specified)
    ├─ Query SID from domain
    ├─ Append RID values (500+)
    └─ Resolve SID to username

12. Output Generation
    ├─ Parse all responses
    ├─ Consolidate results
    └─ Format and display
```

### RID Cycling Technique

RID (Relative Identifier) cycling is the most powerful enumeration technique:

**How It Works:**

1. **Obtain Domain SID**:
   ```
   Domain SID: S-1-5-21-3623811015-3361044348-30300510
   ```

2. **Append RIDs** (starting from 500 - first user):
   ```
   User 1: S-1-5-21-3623811015-3361044348-30300510-500  → Administrator
   User 2: S-1-5-21-3623811015-3361044348-30300510-501  → Guest
   User 3: S-1-5-21-3623811015-3361044348-30300510-502  → KRBTGT
   User 4: S-1-5-21-3623811015-3361044348-30300510-1000 → First domain user
   ```

3. **Query Each SID**:
   ```
   rpcclient> lookupsids S-1-5-21-3623811015-3361044348-30300510-500
   Resolves to: DOMAIN\Administrator
   ```

4. **Enumerate Systematically**:
   - Tries RIDs 500-550 (built-in accounts)
   - Then 1000-1050 (domain users)
   - Can be extended with custom ranges

**Why This Works:**
- Windows assigns RIDs sequentially
- Even if null sessions disabled, unauthenticated RID queries sometimes work
- Can enumerate all users without credentials
- Extremely effective on older Windows systems

### Null Session Exploitation

**What is a Null Session?**

A null session is an unauthenticated SMB connection:
```bash
smbclient //192.168.1.10/IPC$ -U "" -N
```

**What Can Be Enumerated via Null Session?**

✓ User names (via RPC enumeration)
✓ Domain information (via LSA queries)
✓ Share names
✓ Password policies
✓ Group information

**Modern Defenses:**

- Windows Server 2000+: Restricted anonymous access
- Registry: RestrictAnonymous = 1 (blocks most null session)
- However, many systems still allow limited null session queries

---

## Installation and Setup

### Linux Installation

**Kali Linux** (Pre-installed):

```bash
# Already included in Kali
enum4linux -h
```

**Ubuntu/Debian**:

```bash
# Original enum4linux.pl
sudo apt install enum4linux

# Or modern enum4linux-ng
sudo apt install enum4linux-ng
```

**Fedora/RHEL/CentOS**:

```bash
sudo dnf install enum4linux      # Original
sudo dnf install enum4linux-ng   # Modern Python version
```

**Arch Linux**:

```bash
sudo pacman -S enum4linux
sudo pacman -S enum4linux-ng
```

### Dependencies Installation

**For enum4linux.pl (Perl version)**:

```bash
# Requires Perl and Samba tools
sudo apt install perl samba samba-common-bin

# Individual Samba tools
sudo apt install smbclient      # SMB client
sudo apt install rpcclient      # RPC client
sudo apt install nmblookup      # NetBIOS lookup
```

**For enum4linux-ng (Python version)**:

```bash
# Python 3 and dependencies
sudo apt install python3 python3-pip

# Required Python packages
pip3 install impacket ldap3 pyyaml

# Still needs Samba tools
sudo apt install samba-common-bin
```

### Compilation from Source

**From GitHub (Latest Development):**

```bash
# Clone original enum4linux
git clone https://github.com/portcullistech/enum4linux.git
cd enum4linux
sudo chmod +x enum4linux.pl
sudo cp enum4linux.pl /usr/local/bin/enum4linux

# Or clone modern enum4linux-ng
git clone https://github.com/cddmp/enum4linux-ng.git
cd enum4linux-ng
sudo chmod +x enum4linux-ng.py
sudo cp enum4linux-ng.py /usr/local/bin/enum4linux-ng
```

### Verification

```bash
# Check original version
enum4linux -h

# Check ng version
enum4linux-ng -h

# Verify Samba tools available
nmblookup --version
rpcclient --version
smbclient --version
```

---

## Basic Syntax and Usage

### Minimal Usage

```bash
# Most basic scan (uses -A by default)
enum4linux 192.168.1.10

# Equivalent to specifying -A
enum4linux -a 192.168.1.10
```

### General Syntax

```bash
# Original enum4linux.pl
enum4linux [options] target_host

# Modern enum4linux-ng
enum4linux-ng [options] target_host
```

### Quick Reference - Most Common Commands

| Command | Purpose |
|---------|---------|
| `enum4linux -a 192.168.1.10` | Complete enumeration (all options) |
| `enum4linux -U 192.168.1.10` | List users only |
| `enum4linux -S 192.168.1.10` | List shares only |
| `enum4linux -P 192.168.1.10` | Password policy only |
| `enum4linux -O 192.168.1.10` | OS information only |
| `enum4linux -u admin -p pass 192.168.1.10` | Authenticated enumeration |
| `enum4linux -R 192.168.1.10` | RID cycling |

---

## Core Enumeration Techniques

### 1. User Enumeration (-U)

**What It Does:**
Retrieves list of user accounts on the target system.

**Command:**
```bash
enum4linux -U 192.168.1.10
```

**Output Example:**
```
user:[administrator] rid:[0x1f4]
user:[guest] rid:[0x1f5]
user:[krbtgt] rid:[0x1f6]
user:[john_smith] rid:[0x3e8]
user:[jane_doe] rid:[0x3e9]
```

**Interpretation:**
- Administrator account (RID 500/0x1f4)
- Guest account (RID 501/0x1f5)
- KRBTGT (Kerberos key distribution center ticket)
- Domain users starting at RID 1000 (0x3e8+)

**Uses:**
- Identify user accounts for password spraying
- Determine naming conventions
- Find service accounts
- Map organizational structure

### 2. Group Enumeration (-G)

**What It Does:**
Enumerates groups and optionally group members.

**Commands:**
```bash
enum4linux -G 192.168.1.10          # Groups only
enum4linux -Gm 192.168.1.10         # Groups with members
```

**Output Example:**
```
group:[domain admins] rid:[0x200]
group:[domain users] rid:[0x201]
group:[domain guests] rid:[0x202]
group:[builtin_administrators] rid:[0x220]

Group 'domain admins' (RID: 512) has member:
    administrator [Administrator]
    john_smith [John Smith]
```

**Uses:**
- Identify privileged groups
- Map domain structure
- Find users in sensitive groups
- Discover nested group memberships

### 3. Share Enumeration (-S)

**What It Does:**
Lists available SMB shares and tests access permissions.

**Command:**
```bash
enum4linux -S 192.168.1.10
```

**Output Example:**
```
Sharename       Type      Comment
=========       ====      =======
ADMIN$          Disk      Remote Admin
C$              Disk      Default share
IPC$            IPC       Remote IPC
data_shared     Disk      Shared Documents
backup          Disk      Backup Storage

Mapping: \\192.168.1.10\ADMIN$ [Mapping: FAILED] [Listing: N/A] [Writing: N/A]
Mapping: \\192.168.1.10\C$ [Mapping: OK] [Listing: OK] [Writing: N/A]
Mapping: \\192.168.1.10\data_shared [Mapping: OK] [Listing: OK] [Writing: OK]
```

**Interpretation:**
- Mapping: Can share be mounted?
- Listing: Can share contents be read?
- Writing: Can files be written to share?

**Uses:**
- Find accessible data
- Identify sensitive shared folders
- Detect misconfigured shares
- Plan data exfiltration

### 4. Password Policy (-P)

**What It Does:**
Retrieves domain password policy settings.

**Command:**
```bash
enum4linux -P 192.168.1.10
```

**Output Example:**
```
[+] Retieved partial password policy with domain logon server:

Password Info for Domain: CORP.LOCAL
======================

Minimum password length: 8
Password must meet complexity requirements: Yes
Password expires in: 90 days
Minimum password age: 1 day
Reset count minimum: None
Locked Account Duration: 30 minutes
Account Lockout Threshold: 5 attempts
Password History: 24 passwords remembered
Force user logoff: Never
Refuse machine password change: No
```

**Uses:**
- Plan password spraying (understand lockout)
- Identify weak policies
- Guide credential generation
- Understand account recovery process

### 5. OS Information (-O)

**What It Does:**
Retrieves operating system and system information.

**Command:**
```bash
enum4linux -O 192.168.1.10
```

**Output Example:**
```
[+] Retrieving OS information from 192.168.1.10

OS Information:
    OS Version: Windows Server 2016
    OS Build: 14393
    OS Service Pack: None
    Hostname: DC01
    Domain: CORP.LOCAL
    Forest: CORP.LOCAL
    Domain Controller: Yes
```

**Uses:**
- Identify OS for targeted exploits
- Determine system end-of-life status
- Plan upgrade requirements
- Map domain controller locations

### 6. NetBIOS Information (-N)

**What It Does:**
Performs NetBIOS lookup and retrieves name information.

**Command:**
```bash
enum4linux -N 192.168.1.10
```

**Output Example:**
```
[+] Looking up status of 192.168.1.10

Looking up status of 192.168.1.10
    DC01            <00> -         B <ACTIVE>  Workstation Service
    DC01            <20> -         B <ACTIVE>  File Server Service
    CORP            <00> -         B <ACTIVE>  Domain/Workgroup Name
    CORP            <1b> -         B <ACTIVE>  Domain Master Browser
    CORP            <1c> -         B <ACTIVE>  Domain Controllers
    CORP            <1d> -         B <ACTIVE>  Master Browser
    __MSBROWSE__    <01> -         B <ACTIVE>  Master Browser
```

**Uses:**
- Determine workgroup/domain name
- Identify domain controllers
- Discover system roles
- Map network topology

### 7. Printer Information (-I)

**What It Does:**
Enumerates networked printers.

**Command:**
```bash
enum4linux -I 192.168.1.10
```

**Uses:**
- Identify print servers
- Discover printer vulnerabilities
- Map network devices

### 8. RID Cycling (-R)

**What It Does:**
Enumerates users by cycling through RID values without relying on RPC enumeration.

**Command:**
```bash
enum4linux -R 192.168.1.10          # Default range (500-550, 1000-1050)
enum4linux -R 500-2000 192.168.1.10 # Custom range
enum4linux -R -d 192.168.1.10       # With details
```

**Output Example:**
```
Trying to enumerate users rid by rid from 500 to 550

rid:[1000] rid_name:[user1] rid_type:[1]
rid:[1001] rid_name:[user2] rid_type:[1]
rid:[1002] rid_name:[user3] rid_type:[1]
rid:[1003] rid_name:[svc_account] rid_type:[1]
rid:[1004] rid_name:[test_user] rid_type:[1]

Result: 5 users found
```

**Uses:**
- Enumerate users when RPC enumeration fails
- Find users missed by standard enumeration
- Bypass some null session restrictions
- Comprehensive user discovery

---

## Command-Line Options Reference

### Original enum4linux.pl Options

| Option | Long Form | Purpose |
|--------|-----------|---------|
| `-U` | | Get users via RPC |
| `-M` | | Get machine list |
| `-N` | | NetBIOS names lookup |
| `-S` | | Get shares |
| `-P` | | Get password policy |
| `-G` | | Get groups |
| `-G -m` | | Get groups with members |
| `-a` | | All simple enumerations |
| `-u username` | | Username for authentication |
| `-p password` | | Password for authentication |
| `-d domain` | | Domain/Workgroup name |
| `-c` | | Specify list of shares (for brute force) |
| `-r range` | | RID range (e.g., 500-5000) |
| `-R` | | RID cycling |
| `-i` | | Get printer info |
| `-o` | | Get OS information |
| `-l` | | Get additional info via LDAP |

### Modern enum4linux-ng Options

| Option | Purpose |
|--------|---------|
| `-A` | All simple enumerations (no RID cycling by default) |
| `-As` | All simple without NetBIOS |
| `-U` | Get users via RPC |
| `-G` | Get groups |
| `-Gm` | Get groups with members |
| `-S` | Get shares |
| `-C` | Get services |
| `-P` | Password policy |
| `-O` | OS information |
| `-L` | LDAP info (DCs only) |
| `-I` | Printer info |
| `-R` | RID cycling (requires explicit option) |
| `-N` | NetBIOS names lookup |
| `-u user` | Username for auth |
| `-p pass` | Password for auth |
| `-K ticketfile` | Kerberos ticket |
| `-H nthash` | NTLM hash for auth |
| `-w domain` | Workgroup/domain |
| `-d` | Detailed output |
| `-k knownusers` | Users to use for SID lookup |
| `-r ranges` | RID ranges |
| `-s shares` | Shares file for brute force |
| `-oJ file.json` | JSON output |
| `-oY file.yaml` | YAML output |
| `-oA file` | Both JSON and YAML |
| `-t timeout` | Connection timeout |
| `-v` | Verbose |

---

## Practical Usage Examples

### Example 1: Basic Reconnaissance

Gather all available information from target without credentials:

```bash
enum4linux -a 192.168.1.10
```

**Output Includes:**
- OS information
- User accounts
- Groups
- Shares
- Password policies
- Printers
- NetBIOS information

### Example 2: Targeted User Enumeration

Focus only on discovering users for password spraying:

```bash
enum4linux -U 192.168.1.10
```

**Then save usernames to file:**

```bash
enum4linux -U 192.168.1.10 | grep "user:" | cut -d'[' -f2 | cut -d']' -f1 > users.txt
```

### Example 3: Authenticated Enumeration

Use known credentials for deeper access:

```bash
enum4linux -u admin -p "P@ssw0rd" -a 192.168.1.10
```

### Example 4: RID Cycling with Wide Range

Enumerate all users in domain:

```bash
enum4linux -R 500-5000 192.168.1.10
```

### Example 5: Share Enumeration and Analysis

Find accessible shares:

```bash
enum4linux -S 192.168.1.10 | grep "Mapping: OK"
```

### Example 6: Password Policy for Spraying

Get policy to avoid lockout:

```bash
enum4linux -P 192.168.1.10
```

**Extract key info:**
- Minimum length
- Complexity requirements
- Lockout threshold
- Lockout duration

### Example 7: Multi-Target Enumeration

Scan entire subnet:

```bash
for ip in 192.168.1.{10..30}; do
    echo "=== Scanning $ip ==="
    enum4linux -a $ip 2>/dev/null | grep -E "OS Version|Hostname|user:|group:"
done
```

### Example 8: JSON Output (enum4linux-ng)

Export results for processing:

```bash
enum4linux-ng -A -oJ results.json 192.168.1.10
```

**Parse with jq:**

```bash
# Extract users
jq '.users' results.json

# Extract groups
jq '.groups' results.json

# Extract shares
jq '.shares' results.json
```

### Example 9: Kerberos Authentication (enum4linux-ng)

Use Kerberos ticket for enumeration:

```bash
enum4linux-ng -A -K krb5.ccache 192.168.1.10
```

### Example 10: NTLM Hash Authentication

Use NTLM hash instead of password:

```bash
enum4linux-ng -A -H aad3b435b51404eeaad3b435b51404ee:5f4dcc3b5aa765d61d8327deb882cf99 192.168.1.10
```

---

## Advanced Enumeration Techniques

### RID Cycling Deep Dive

**Process:**

1. **Obtain Domain SID via LSA Query:**

```bash
rpcclient -U "" -N 192.168.1.10 -c "lsaquery"

# Returns something like:
# Domain Name: CORP
# Domain Sid: S-1-5-21-3623811015-3361044348-30300510
```

2. **Attempt to Enumerate SID:**

```bash
rpcclient -U "" -N 192.168.1.10 -c "lookupsids S-1-5-21-3623811015-3361044348-30300510-500"

# Returns: CORP\Administrator
```

3. **Cycle Through RID Values:**

For each RID from 500 onwards:
```
500  → Administrator
501  → Guest
502  → KRBTGT
1000 → First domain user
1001 → Second domain user
...
```

**Speed Optimization (enum4linux-ng):**

Instead of one RPC call per RID, batch multiple RIDs:

```bash
lookupsids S-1-5-21-3623811015-3361044348-30300510-500 S-1-5-21-3623811015-3361044348-30300510-501 S-1-5-21-3623811015-3361044348-30300510-502
```

### LDAP Enumeration

More reliable than RPC for large domains:

```bash
enum4linux-ng -L 192.168.1.10
```

**Extracts via LDAP:**
- Users (via LDAP search)
- Groups
- Domain information
- Organizational units
- Trust relationships
- FSMO roles

### Null Session Detection and Exploitation

**Test for Null Session:**

```bash
smbclient -L //192.168.1.10 -U "" -N
```

If this works, null sessions are enabled:

```bash
# Further enumeration possible
rpcclient -U "" -N 192.168.1.10 -c "enumdomusers"
```

### Authenticated vs Anonymous Trade-offs

**Anonymous Access (Null Session):**
- ✓ Stealthy (appears as computer, not user)
- ✗ Limited information
- ✓ No credential exposure
- ✗ Likely blocked on modern systems

**Authenticated Access:**
- ✗ Obvious user account activity
- ✓ Comprehensive information
- ✗ Risk of account lockout
- ✓ Access to sensitive resources

### SMB Dialect Detection

**Check SMB versions supported:**

```bash
enum4linux-ng -A 192.168.1.10
```

Modern versions show:
```
SMB Dialects Supported:
    2.0.2
    2.1
    3.0
    3.0.2
    3.1.1
```

---

## ENUM4LINUX-NG (Python Version)

### Why Use Modern Version?

**Advantages over Original:**

1. **Speed**: RID cycling batching (10-100x faster)
2. **Output Formats**: JSON/YAML export for automation
3. **Smarter Enumeration**: Automatically skips failed tests
4. **Better Parsing**: Structured data extraction
5. **Modern Python**: Python 3 compatible
6. **IPv6 Support**: Experimental IPv6 support
7. **Timeout Support**: Graceful handling of slow targets
8. **Colored Output**: Better readability

### Installation

```bash
# Ubuntu/Debian
sudo apt install enum4linux-ng

# Or from GitHub
git clone https://github.com/cddmp/enum4linux-ng.git
chmod +x enum4linux-ng/enum4linux-ng.py
sudo ln -s $(pwd)/enum4linux-ng/enum4linux-ng.py /usr/local/bin/enum4linux-ng
```

### JSON Output Example

```bash
enum4linux-ng -A -oJ results 192.168.1.10
```

**Output File: results.json**

```json
{
  "users": [
    {
      "rid": 500,
      "name": "Administrator",
      "type": "SidTypeUser"
    },
    {
      "rid": 1000,
      "name": "john_smith",
      "type": "SidTypeUser"
    }
  ],
  "groups": [
    {
      "rid": 512,
      "name": "Domain Admins",
      "members": ["Administrator", "john_smith"]
    }
  ],
  "shares": [
    {
      "name": "C$",
      "mapping": "OK",
      "listing": "OK",
      "writing": "N/A"
    }
  ],
  "os": {
    "os_version": "Windows Server 2016",
    "hostname": "DC01",
    "domain": "CORP.LOCAL"
  }
}
```

**Process with Tools:**

```bash
# Extract all users
jq -r '.users[].name' results.json > users.txt

# Extract domain admins
jq -r '.groups[] | select(.name == "Domain Admins") | .members[]' results.json

# Check accessible shares
jq -r '.shares[] | select(.mapping == "OK") | .name' results.json
```

### YAML Output

```bash
enum4linux-ng -A -oY results 192.168.1.10
```

**More human-readable format for manual review.**

---

## Troubleshooting and Optimization

### Issue: Connection Refused

**Symptoms:**
```
[!] Connection error occurred: Connection refused
```

**Causes:**
- Target not running SMB
- Wrong port
- Firewall blocking

**Solutions:**

```bash
# Verify SMB is running
nmap -p 445,139 192.168.1.10

# Check if SMB service is enabled
crackmapexec smb 192.168.1.10

# Try with timeout extension
enum4linux-ng -t 10 192.168.1.10
```

### Issue: No RPC Access

**Symptoms:**
```
[!] Error executing enumdomusers
[+] Could not connect to rpc services
```

**Causes:**
- RPC is disabled
- Firewall blocking RPC
- Incorrect credentials

**Solutions:**

```bash
# Try RID cycling instead
enum4linux -R 192.168.1.10

# Try LDAP if available
enum4linux-ng -L 192.168.1.10

# Force specific authentication
enum4linux -u administrator -p password 192.168.1.10
```

### Issue: Slow Enumeration

**Symptoms:**
- RID cycling takes very long
- Connection timeouts

**Solutions:**

```bash
# Use batched RID cycling (ng version)
enum4linux-ng -R 192.168.1.10

# Reduce RID range
enum4linux-ng -r 500-600 192.168.1.10

# Increase timeout
enum4linux-ng -t 30 192.168.1.10

# Skip slow tests
enum4linux-ng -As 192.168.1.10  # Skip NetBIOS
```

### Issue: Access Denied (Restricted Anonymous)

**Symptoms:**
```
NT_STATUS_ACCESS_DENIED
```

**Causes:**
- RestrictAnonymous = 2 (full restriction)
- Null sessions disabled

**Solutions:**

```bash
# Must use valid credentials
enum4linux -u admin -p password 192.168.1.10

# Or use Kerberos
enum4linux-ng -K ticket.ccache 192.168.1.10

# Try different protocols
crackmapexec smb 192.168.1.10 -u '' -p ''
```

### Performance Optimization

**For Large Domains:**

```bash
# Use enum4linux-ng with batched RID cycling
enum4linux-ng -R 192.168.1.10

# Set appropriate timeout
enum4linux-ng -t 10 192.168.1.10

# Use JSON output for faster processing
enum4linux-ng -oJ results 192.168.1.10 && jq '.users' results.json
```

**For Multiple Targets:**

```bash
# Parallel enumeration of multiple hosts
for target in 192.168.1.{10..50}; do
    enum4linux-ng -A -oJ "results_$target" $target &
done
wait
```

---

## Integration with Other Tools

### With Nmap

**Discover SMB ports first:**

```bash
nmap -p 445,139 -sV 192.168.1.0/24

# Then enumerate each target
nmap -p 445,139 192.168.1.0/24 | grep "open" | cut -d' ' -f1 | while read target; do
    enum4linux -a $target
done
```

### With CrackMapExec

```bash
# Faster SMB enumeration
crackmapexec smb 192.168.1.10 -u "" -p "" --shares

# Then use enum4linux for detailed info
enum4linux -a 192.168.1.10
```

### Workflow: Recon to Exploit

```bash
#!/bin/bash
# Complete reconnaissance workflow

TARGET=$1

echo "[*] Starting enumeration on $TARGET"

# 1. Enumerate with enum4linux
enum4linux -oJ enum_results.json $TARGET

# 2. Extract users
jq -r '.users[].name' enum_results.json > users.txt

# 3. Get password policy
LOCKOUT=$(jq -r '.password_policy.account_lockout_threshold' enum_results.json)
echo "[+] Lockout threshold: $LOCKOUT attempts"

# 4. Extract accessible shares
jq -r '.shares[] | select(.mapping == "OK") | .name' enum_results.json > shares.txt

# 5. Attempt password spray (example)
hydra -L users.txt -p "Welcome1" smb://$TARGET

# 6. Access found shares
while read share; do
    smbclient //$TARGET/$share -U admin%password -c "ls"
done < shares.txt
```

---

## Security Considerations

### Detection and Evasion

**Enumeration is Noisy:**

```
- Generates dozens of SMB connections
- RPC queries are easily logged
- Port scanners detect activity
- IDS/IPS may trigger on patterns
```

**Detection Methods:**

```
- SMB event log analysis (Event ID 4688)
- IDS signatures for RPC queries
- Connection rate analysis
- NetFlow/sFlow traffic analysis
```

**Cannot Truly Evade:**

Unlike port scanning, enumeration requires actual SMB connections.

### Responsible Use

1. **Get Authorization**: Ensure you have permission
2. **Document Activities**: Keep logs of enumeration
3. **Avoid DoS**: Don't hammer servers with queries
4. **Respect Credentials**: Don't share/expose user accounts found
5. **Manage Results**: Securely store enumeration data
6. **Remediate**: Help fix misconfigurations found

### Ethical Penetration Testing

Use enum4linux as part of authorized assessments:

- ✓ Internal security assessments
- ✓ Red team exercises
- ✓ Vulnerability assessments
- ✓ Security hardening
- ✗ Unauthorized access
- ✗ Competitive intelligence
- ✗ Criminal purposes

---

## Summary and Best Practices

### Key Capabilities

1. **User Discovery**: Enumerate domain and local users
2. **Group Mapping**: Understand organizational structure
3. **Share Discovery**: Identify accessible resources
4. **Policy Extraction**: Understand security posture
5. **OS Fingerprinting**: Identify systems and versions
6. **RID Cycling**: Comprehensive user enumeration
7. **Multiple Auth Methods**: Passwords, hashes, Kerberos

### Best Practices

1. **Start Simple**: Use `-A` for first reconnaissance
2. **Focus Enumeration**: Use specific options for efficiency
3. **Document Findings**: Export JSON/YAML for reports
4. **Combine Tools**: Use with Nmap, CrackMapExec
5. **Check Credentials**: Use found users for password spraying
6. **Analyze Results**: Look for suspicious accounts
7. **Test Systematically**: Enumerate each domain separately

### Typical Workflow

```
1. Port Scan (Nmap)
   └─ Identify SMB ports (445/139)

2. Quick Enumeration (enum4linux -A)
   └─ Gather basic information

3. Focused Enumeration (enum4linux -U, -S, -P)
   └─ Extract specific data

4. RID Cycling (enum4linux -R)
   └─ Comprehensive user list

5. Credential Spraying
   └─ Use found users + common passwords

6. Authenticated Enumeration
   └─ Deeper access with valid credentials

7. Report Generation
   └─ Document findings
```

### When to Use enum4linux

- ✓ Active Directory reconnaissance
- ✓ Windows network enumeration
- ✓ Samba server assessment
- ✓ User discovery
- ✓ Share enumeration
- ✓ Penetration testing
- ✗ Not for stealth (very noisy)
- ✗ Not for remote networks (local only)

### Next Steps

1. Practice enumeration in lab environments
2. Learn underlying SMB/RPC protocols
3. Master RID cycling technique
4. Integrate with other tools
5. Develop custom scripts
6. Set up home lab with Samba
7. Practice password spraying
8. Develop comprehensive reports
