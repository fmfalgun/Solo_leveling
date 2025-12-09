# SMBMAP: A Comprehensive Guide to SMB Share Enumeration and Exploitation

## Table of Contents
1. [Introduction](#introduction)
2. [SMB Enumeration Fundamentals](#smb-enumeration-fundamentals)
3. [How SMBMAP Works](#how-smbmap-works)
4. [Installation and Setup](#installation-and-setup)
5. [Basic Syntax and Usage](#basic-syntax-and-usage)
6. [Command-Line Options Reference](#command-line-options-reference)
7. [Share Enumeration](#share-enumeration)
8. [Directory and File Listing](#directory-and-file-listing)
9. [File Operations](#file-operations)
10. [Authentication Methods](#authentication-methods)
11. [Advanced Features](#advanced-features)
12. [Practical Examples and Workflows](#practical-examples-and-workflows)
13. [Security and Ethical Considerations](#security-and-ethical-considerations)

---

## Introduction

**smbmap** is a powerful Python tool designed to enumerate SMB shares across an entire network or specific hosts. It provides a more efficient and feature-rich alternative to traditional SMB enumeration tools like smbclient and enum4linux. smbmap allows security professionals and penetration testers to quickly identify accessible shares, list directory contents, check permissions, upload/download files, execute commands, and search for sensitive data patterns.

### Key Characteristics

- **Fast Enumeration**: Quickly list shares and permissions
- **Recursive Directory Listing**: Traverse directory trees with depth control
- **Pattern Matching**: Auto-download files matching regex patterns
- **File Operations**: Upload, download, and delete files
- **Remote Command Execution**: Execute commands on remote systems (if allowed)
- **File Content Search**: Search file contents for specific patterns
- **Permission Detection**: Show READ, WRITE, and NO ACCESS permissions
- **Pass-the-Hash Support**: Authentication using NTLM hashes
- **Kerberos Support**: Authenticate using Kerberos tickets
- **Batch Processing**: Scan multiple hosts from file
- **Output Formats**: Generate reports in grep, CSV, and standard formats
- **Impacket-Based**: Built on Impacket library for reliability

### Primary Use Cases

- **Penetration Testing**: Assess SMB security across networks
- **Vulnerability Assessment**: Identify misconfigured shares
- **Data Exposure Testing**: Find exposed sensitive files
- **Access Control Testing**: Verify share permissions
- **Network Discovery**: Identify accessible resources
- **Compliance Auditing**: Check for exposed shares
- **Incident Response**: Investigate SMB-based breaches
- **Red Teaming**: Simulate realistic attacks

### Limitations

- **Requires Python**: No standalone binary version
- **Speed vs. Accuracy**: Balance needed between speed and thoroughness
- **Detection Risk**: Generates obvious enumeration patterns
- **Complexity**: More complex than simple share listing tools
- **Requires Network Access**: Must be able to reach SMB ports

---

## SMB Enumeration Fundamentals

### Enumeration Stages

**Standard SMB Enumeration Process**:

```
1. HOSTNAME ENUMERATION
   └─ Identify computer name/NetBIOS name

2. LIST SHARES
   └─ Discover all available shares
   └─ Get share types (Disk, IPC, Printer)

3. CHECK NULL SESSION
   └─ Test unauthenticated access
   └─ See what's available without credentials

4. LIST USERS
   └─ Enumerate user accounts
   └─ Identify service accounts

5. CHECK PERMISSIONS
   └─ Verify READ/WRITE access
   └─ Identify admin shares

6. VULNERABILITY SCANNING
   └─ Look for known misconfigurations
   └─ Detect SMB weaknesses

7. OVERALL SCANNING
   └─ Combine all above steps
   └─ Generate comprehensive report
```

### Share Types

```
Disk Shares ($)
├─ C$ - Administrative share (full C: drive)
├─ D$ - Drive shares (D:, E:, etc.)
├─ IPC$ - Inter-Process Communication (pipes)
└─ User Shares - Custom shares for files

Administrative Shares
├─ ADMIN$ - Administrative resources
├─ User folders (user$)
└─ Print$ - Printer driver storage

Printer Shares
├─ Printers - Network printers
└─ Print Server resources
```

### Permission States

```
READ ONLY:
  ├─ Can list directory contents
  ├─ Can download files
  └─ Cannot write or modify

WRITE:
  ├─ Full read access
  ├─ Can upload files
  ├─ Can delete files
  └─ Can create directories

READ, WRITE:
  ├─ Full read and write permissions
  └─ Can perform all file operations

NO ACCESS:
  ├─ Cannot access share
  └─ Share exists but is restricted
```

---

## How SMBMAP Works

### Operational Model

```
┌────────────────────────────────┐
│ User Command                   │
│ smbmap -H 192.168.1.1 -r       │
└────────────┬────────────────────┘
             │
             ▼
┌────────────────────────────────┐
│ Parse Arguments                │
│ ├─ Host/IP address            │
│ ├─ Username/password          │
│ ├─ Domain/workgroup           │
│ └─ Command options            │
└────────────┬────────────────────┘
             │
             ▼
┌────────────────────────────────┐
│ Establish SMB Connection       │
│ ├─ Connect to port 445         │
│ ├─ Negotiate SMB version       │
│ └─ Authenticate (or null sess) │
└────────────┬────────────────────┘
             │
             ▼
┌────────────────────────────────┐
│ Enumerate Shares               │
│ ├─ List all shares             │
│ ├─ Get share type              │
│ ├─ Determine permissions       │
│ └─ Identify admin shares       │
└────────────┬────────────────────┘
             │
             ▼
┌────────────────────────────────┐
│ Traverse/Search as Requested   │
│ ├─ Recursive listing (-r/-R)   │
│ ├─ Pattern matching (-A/-F)    │
│ ├─ Depth limiting (--depth)    │
│ └─ File operations             │
└────────────┬────────────────────┘
             │
             ▼
┌────────────────────────────────┐
│ Process and Format Output      │
│ ├─ Standard output             │
│ ├─ Grep format (-g)            │
│ ├─ CSV format (--csv)          │
│ └─ Display permissions         │
└────────────┬────────────────────┘
             │
             ▼
┌────────────────────────────────┐
│ Output Results to User         │
│ ├─ Display shares              │
│ ├─ Show files/directories      │
│ ├─ Indicate permissions        │
│ └─ Report any actions taken    │
└────────────────────────────────┘
```

### Permission Detection Algorithm

```
For each Share:

1. TEST READ ACCESS
   ├─ Try to list directory
   ├─ If success → Has READ
   └─ If denied → No read access

2. TEST WRITE ACCESS (if not skipped)
   ├─ Try to create temporary file
   ├─ If success → Has WRITE
   ├─ Delete temporary file
   └─ If denied → No write access

3. COMBINE RESULTS
   ├─ READ only
   ├─ WRITE only
   ├─ READ, WRITE
   └─ NO ACCESS

4. DISPLAY TO USER
   └─ Show permission matrix
```

---

## Installation and Setup

### Linux Installation

**Using apt (Ubuntu/Debian)**:

```bash
sudo apt update
sudo apt install smbmap
```

**Using dnf (Fedora/RHEL)**:

```bash
sudo dnf install smbmap
```

**Using pip** (Universal):

```bash
pip install smbmap
```

**Kali Linux** (Pre-installed):

```bash
smbmap --help
```

### macOS Installation

```bash
# Using Homebrew
brew install smbmap

# Or using pip
pip install smbmap
```

### From Source

```bash
git clone https://github.com/ShawnDEvans/smbmap.git
cd smbmap
python -m pip install -r requirements.txt
python smbmap.py --help
```

### Dependencies

```bash
# Required packages
python3
python3-impacket
python3-pyasn1
python3-termcolor

# Install all dependencies
pip install impacket pyasn1 termcolor
```

### Verification

```bash
# Check installation
which smbmap

# Check version
smbmap --version

# Verify help
smbmap --help
```

---

## Basic Syntax and Usage

### General Command Structure

```bash
smbmap [OPTIONS] -H target_host
```

### Most Common Commands

| Command | Purpose |
|---------|---------|
| `smbmap -H 192.168.1.1` | Enumerate shares (anonymous) |
| `smbmap -H 192.168.1.1 -u user -p pass` | Enumerate with credentials |
| `smbmap -H 192.168.1.1 -u user -p hash -r` | Enumerate with hash, list files |
| `smbmap -H 192.168.1.1 -r` | Recursively list all shares |
| `smbmap -H 192.168.1.1 -R --depth 3` | Recursive with depth limit |
| `smbmap -H 192.168.1.1 -A 'pattern'` | Auto-download matching files |
| `--host-file hosts.txt -u user -p pass -r` | Scan multiple hosts |
| `smbmap -H 192.168.1.1 -x "whoami"` | Execute remote command |

---

## Command-Line Options Reference

### Host Specification

| Option | Purpose | Example |
|--------|---------|---------|
| `-H HOST` | Single host IP or FQDN | `-H 192.168.1.1` |
| `--host-file FILE` | File with list of hosts | `--host-file hosts.txt` |
| `-P PORT` | SMB port (default 445) | `-P 445` |

### Authentication Options

| Option | Purpose | Example |
|--------|---------|---------|
| `-u USERNAME` | Username | `-u administrator` |
| `-p PASSWORD` | Password | `-p MyPassword123` |
| `--prompt` | Prompt for password | `--prompt` |
| `-d DOMAIN` | Domain or workgroup | `-d DOMAIN` |
| `-k` | Use Kerberos auth | `-k` |
| `--no-pass` | Use CCache for Kerberos | `--no-pass` |
| `--dc-ip IP` | Domain controller IP | `--dc-ip 192.168.1.254` |

### Enumeration Options

| Option | Purpose | Example |
|--------|---------|---------|
| `-L` | List all drives (admin only) | `-L` |
| `-r [PATH]` | Recursive list (single level default) | `-r` |
| `-R` | Full recursive listing | `-R` |
| `--depth DEPTH` | Limit recursion depth | `--depth 3` |
| `-s SHARE` | Specify share | `-s C$` |
| `--dir-only` | Show only directories | `--dir-only` |
| `--exclude SHARE` | Exclude shares | `--exclude IPC$ ADMIN$` |

### File Operations

| Option | Purpose | Example |
|--------|---------|---------|
| `-A PATTERN` | Auto-download matching files (regex) | `-A '(config\|password)'` |
| `-F PATTERN` | Search file contents | `-F 'password'` |
| `--download PATH` | Download specific file | `--download C$\file.txt` |
| `--upload SRC DST` | Upload file | `--upload local.txt C$\remote.txt` |
| `--delete PATH` | Delete file | `--delete C$\file.txt` |

### Output Options

| Option | Purpose | Example |
|--------|---------|---------|
| `-v` | Show OS version | `-v` |
| `-q` | Quiet output (access only) | `-q` |
| `-g FILE` | Grep format output | `-g results.txt` |
| `--csv FILE` | CSV format output | `--csv shares.csv` |
| `--no-banner` | Remove banner | `--no-banner` |
| `--no-color` | Remove color from output | `--no-color` |

### Advanced Options

| Option | Purpose | Example |
|--------|---------|---------|
| `--signing` | Check SMB signing status | `--signing` |
| `--admin` | Check if user is admin | `--admin` |
| `-x COMMAND` | Execute remote command | `-x 'ipconfig /all'` |
| `--mode CMDMODE` | Execution method (wmi/psexec) | `--mode wmi` |
| `--no-write-check` | Skip write permission check | `--no-write-check` |
| `--timeout SECONDS` | Socket timeout | `--timeout 5` |

---

## Share Enumeration

### Basic Share Listing

**Anonymous enumeration** (no credentials):

```bash
# List available shares
smbmap -H 192.168.1.1

# Expected output:
# [+] IP: 192.168.1.1:445 Name: WIN-SERVER
# Disk Permissions
# ---- -----------
# C$ NO ACCESS
# IPC$ NO ACCESS
# Users READ ONLY
# Public READ, WRITE
```

**With credentials**:

```bash
# Enumerate as specific user
smbmap -H 192.168.1.1 -u john -p password

# Enumerate with domain
smbmap -H 192.168.1.1 -u john -p password -d DOMAIN

# Prompt for password
smbmap -H 192.168.1.1 -u john --prompt
```

### Detailed Share Information

```bash
# Show OS version
smbmap -H 192.168.1.1 -v

# Check SMB signing
smbmap -H 192.168.1.1 --signing

# Check if admin
smbmap -H 192.168.1.1 -u john -p password --admin

# Check specific share permissions
smbmap -H 192.168.1.1 -s Documents -u john -p password
```

### Multiple Host Enumeration

```bash
# Create file with hosts
cat > hosts.txt << 'EOF'
192.168.1.1
192.168.1.2
192.168.1.3
EOF

# Scan all hosts
smbmap --host-file hosts.txt -u admin -p password

# Verbose output with version
smbmap --host-file hosts.txt -v
```

---

## Directory and File Listing

### Non-Recursive Listing

```bash
# List top-level contents
smbmap -H 192.168.1.1 -u user -p pass -r

# List specific share root
smbmap -H 192.168.1.1 -u user -p pass -s Users -r

# List specific directory (no trailing slash for root)
smbmap -H 192.168.1.1 -u user -p pass -r "Documents"
```

### Recursive Listing

```bash
# Full recursive listing
smbmap -H 192.168.1.1 -u user -p pass -R

# Recursive with depth limit
smbmap -H 192.168.1.1 -u user -p pass -R --depth 3

# Very limited depth (2 levels only)
smbmap -H 192.168.1.1 -u user -p pass -R --depth 2

# Recursively list specific share
smbmap -H 192.168.1.1 -u user -p pass -R -s Documents
```

### Filtered Listing

```bash
# Only show directories
smbmap -H 192.168.1.1 -u user -p pass -R --dir-only

# Exclude certain shares
smbmap -H 192.168.1.1 -u user -p pass -R --exclude IPC$ ADMIN$

# Quiet mode (only show accessible shares)
smbmap -H 192.168.1.1 -u user -p pass -R -q

# Combine filters
smbmap -H 192.168.1.1 -u user -p pass -R --dir-only -q
```

### Export Results

```bash
# Grep-friendly format
smbmap -H 192.168.1.1 -u user -p pass -R -g results.txt

# CSV format
smbmap -H 192.168.1.1 -u user -p pass -R --csv shares.csv

# Standard output to file
smbmap -H 192.168.1.1 -u user -p pass -R > listing.txt
```

---

## File Operations

### Downloading Files

**Single file**:

```bash
# Download specific file
smbmap -H 192.168.1.1 -u user -p pass --download "Users\john\Documents\file.txt"

# Download from C$ drive
smbmap -H 192.168.1.1 -u admin -p pass --download "C$\Windows\System32\config\SAM"
```

**Auto-download with pattern**:

```bash
# Download all config files
smbmap -H 192.168.1.1 -u user -p pass -R -A ".*\.config"

# Download password-related files
smbmap -H 192.168.1.1 -u user -p pass -R -A "(password|passwd|pwd)"

# Download web config files
smbmap -H 192.168.1.1 -u user -p pass -R -A "(web\.config|app\.config|\.asp)"

# Download source code
smbmap -H 192.168.1.1 -u user -p pass -R -A "\.(cs|java|py|cpp)$"
```

### Uploading Files

```bash
# Upload payload to share
smbmap -H 192.168.1.1 -u user -p pass --upload "/tmp/payload.exe" "C$\temp\payload.exe"

# Upload to accessible share
smbmap -H 192.168.1.1 -u user -p pass --upload "/tmp/file.txt" "Users\john\Documents\file.txt"

# Upload to relative path
smbmap -H 192.168.1.1 -u user -p pass -s Public --upload "/tmp/data.zip" "data.zip"
```

### Deleting Files

```bash
# Delete specific file
smbmap -H 192.168.1.1 -u admin -p pass --delete "C$\temp\file.txt"

# Delete without prompt
smbmap -H 192.168.1.1 -u admin -p pass --delete "C$\temp\file.txt" --skip
```

---

## Authentication Methods

### Method 1: Anonymous Access

```bash
# No credentials (null session)
smbmap -H 192.168.1.1

# Explicit null session
smbmap -H 192.168.1.1 -u "" -p ""
```

### Method 2: Username Only

```bash
# Prompt for password
smbmap -H 192.168.1.1 -u username --prompt

# Empty password
smbmap -H 192.168.1.1 -u username -p ""
```

### Method 3: Username and Password

```bash
# Standard authentication
smbmap -H 192.168.1.1 -u username -p password

# With domain
smbmap -H 192.168.1.1 -u username -p password -d DOMAIN
```

### Method 4: Pass-the-Hash (NTLM)

```bash
# Using NTLM hash
smbmap -H 192.168.1.1 -u username -p "LM_HASH:NT_HASH"

# Example with actual hash
smbmap -H 192.168.1.1 -u Administrator \
  -p "aad3b435b51404eeaad3b435b51404ee:da76f2c4c96028b7a6111aef4a50a94d"
```

### Method 5: Kerberos Authentication

```bash
# Use Kerberos ticket
smbmap -H 192.168.1.1 -k

# Use cached Kerberos ticket
export KRB5CCNAME='~/current.ccache'
smbmap -H 192.168.1.1 --no-pass

# With domain controller
smbmap -H 192.168.1.1 -k --dc-ip 192.168.1.254
```

---

## Advanced Features

### File Content Search

```bash
# Search for password strings
smbmap -H 192.168.1.1 -u admin -p pass -F "password"

# Search multiple patterns
smbmap -H 192.168.1.1 -u admin -p pass -F "(password|credential|secret)"

# Search in specific path
smbmap -H 192.168.1.1 -u admin -p pass -F "password" --search-path "C:\Users"

# With timeout (default 300 seconds)
smbmap -H 192.168.1.1 -u admin -p pass -F "password" --search-timeout 600
```

### Remote Command Execution

```bash
# Execute command (requires admin access)
smbmap -H 192.168.1.1 -u admin -p pass -x "whoami"

# Execute with WMI (default)
smbmap -H 192.168.1.1 -u admin -p pass -x "ipconfig /all" --mode wmi

# Execute with PSExec
smbmap -H 192.168.1.1 -u admin -p pass -x "cmd /c net user" --mode psexec

# Output will show command results
```

### Administrative Tasks

```bash
# Check if user is administrator
smbmap -H 192.168.1.1 -u user -p pass --admin

# Check SMB signing status
smbmap -H 192.168.1.1 --signing

# Get OS version
smbmap -H 192.168.1.1 -v
```

---

## Practical Examples and Workflows

### Example 1: Quick Network Assessment

```bash
# Scan network quickly
smbmap --host-file targets.txt -u guest -p "" -q
```

### Example 2: Targeted User Assessment

```bash
# Check specific user across network
smbmap --host-file network.txt -u john -p "J0hn_P@ss" -d DOMAIN -q
```

### Example 3: Search for Sensitive Files

```bash
# Recursively search for config files
smbmap -H 192.168.1.100 -u admin -p password \
  -R -A "(web\.config|app\.config|connection\.string)"
```

### Example 4: Full Network Enumeration

```bash
#!/bin/bash
# Enumerate entire network

USERS=("admin" "administrator")
HOSTS=$(cat targets.txt)

for host in $HOSTS; do
    for user in "${USERS[@]}"; do
        echo "[*] Scanning $host as $user"
        smbmap -H "$host" -u "$user" --prompt -R --depth 2
    done
done
```

### Example 5: Automated Backup of Accessible Data

```bash
#!/bin/bash
# Backup all readable shares

HOST="192.168.1.1"
USER="admin"
BACKUP_DIR="/backup/$(date +%Y%m%d)"

mkdir -p "$BACKUP_DIR"

# Get list of accessible shares
SHARES=$(smbmap -H "$HOST" -u "$USER" -p password -q | grep READ)

for share in $SHARES; do
    echo "Backing up $share..."
    smbmap -H "$HOST" -u "$USER" -p password -s "$share" -R \
      --download "*" --output "$BACKUP_DIR/$share"
done
```

### Example 6: Vulnerability Assessment Report

```bash
#!/bin/bash
# Generate security assessment

echo "=== SMB Enumeration Report ===" > report.txt
echo "Date: $(date)" >> report.txt
echo "" >> report.txt

# Enumerate all hosts
smbmap --host-file targets.txt -u guest -p "" --csv report.csv

# Check signing
echo "=== SMB Signing Status ===" >> report.txt
for host in $(cat targets.txt); do
    smbmap -H "$host" --signing >> report.txt
done
```

---

## Security and Ethical Considerations

### Legal Implications

**smbmap Usage**:

- ✓ **Legal for authorized testing** (with written permission)
- ✓ **Permitted on own systems** and authorized networks
- ✗ **Illegal without authorization** (unauthorized network access)
- ✗ **May violate service terms** on third-party networks
- ✗ **Privacy concerns** with file searching and downloading

### Responsible Use

1. **Get Written Authorization**: Signed approval required
2. **Define Scope**: Clear list of authorized targets
3. **Minimize Impact**: Use appropriate timeouts and depth limits
4. **Document Activity**: Keep detailed logs
5. **Protect Data**: Secure downloaded files
6. **Report Findings**: Professional incident reporting
7. **Follow Policy**: Stay within authorized scope

### Detection

Systems can detect smbmap activity:

```bash
# Monitor SMB connections
auditctl -w /var/log/smb/

# Check SMB logs
grep "smbmap\|enumeration\|suspicious" /var/log/syslog

# Monitor port 445 connections
tcpdump -i eth0 'port 445'
```

---

## Summary and Best Practices

### Key Capabilities

1. **Share Enumeration**: Identify all shares and permissions
2. **Recursive Listing**: Traverse directory trees
3. **Pattern Matching**: Auto-download interesting files
4. **File Operations**: Upload/download/delete files
5. **Content Search**: Find sensitive data in files
6. **Command Execution**: Execute remote commands
7. **Batch Processing**: Scan multiple hosts
8. **Flexible Output**: Generate various report formats

### When smbmap is Useful

✓ **Appropriate Uses**:
- Authorized penetration testing
- Security assessments
- Compliance auditing
- Vulnerability assessments
- Data exposure testing
- Red team exercises

✗ **Inappropriate Uses**:
- Unauthorized access
- Data theft
- Privacy invasion
- Network espionage
- Criminal activity

### Best Practices

1. **Get Authorization**: Written approval required
2. **Plan Carefully**: Define targets and scope
3. **Test Safely**: Start with low-risk targets
4. **Limit Depth**: Use `--depth` to prevent timeouts
5. **Exclude IPC$**: Skip Inter-Process Communication shares
6. **Use Quiet Mode**: `-q` to reduce noise
7. **Export Results**: Save findings for analysis
8. **Report Professionally**: Document all findings

### Typical Workflow

```
1. Reconnaissance
   └─ Gather target information

2. Share Discovery
   └─ smbmap with null session

3. Permission Assessment
   └─ Test read/write access

4. Targeted Search
   └─ Look for sensitive files

5. Analysis
   └─ Identify risks

6. Reporting
   └─ Document findings

7. Remediation
   └─ Recommend fixes
```

### Next Steps

- Master SMB enumeration fundamentals
- Practice on authorized test networks
- Learn complementary tools (smbclient, enum4linux)
- Get certified (OSCP, CEH)
- Conduct authorized assessments
- Document all activities
- Follow responsible disclosure practices
