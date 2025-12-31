# Linux Processes: Comprehensive Technical Guide
## Part 2: Systemd Service Configuration & Management

---

## Table of Contents
1. Systemd Architecture & Concepts
2. Unit Files: Structure & Syntax
3. Service Configuration in Detail
4. Advanced Systemd Features
5. Practical Examples for Security Tools
6. Debugging & Troubleshooting
7. Security Considerations

---

## 1. Systemd Architecture & Concepts

### What is Systemd?

Systemd is a **system and service manager** that replaced traditional SysV init scripts in modern Linux distributions. It provides:

- **Dependency management**: Parallel service startup
- **Socket activation**: Services start on-demand when connections arrive
- **Service supervision**: Automatic restart, resource limiting
- **Logging integration**: Structured journaling via journald
- **Templating**: Dynamic service instantiation
- **Resource cgroups**: CPU, memory, and I/O limits

### Systemd Architecture

```
┌─────────────────────────────────────────────────────┐
│             User/Admin Interface                    │
│  systemctl, systemd-run, timedatectl, etc.         │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│        systemd (PID 1 - Init System)                │
│  ┌────────────────────────────────────────────────┐ │
│  │ Service Manager                                 │ │
│  │ ├─ Unit loader (reads .service files)          │ │
│  │ ├─ Dependency resolver                         │ │
│  │ ├─ Process supervisor                          │ │
│  │ └─ Resource cgroup manager                     │ │
│  └────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────┐ │
│  │ systemd-journald (Logging)                     │ │
│  │ systemd-logind (Session management)            │ │
│  │ systemd-resolved (DNS resolution)              │ │
│  │ systemd-udevd (Hardware hotplug)               │ │
│  └────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
                     │
    ┌────────────────┼────────────────┐
    ▼                ▼                ▼
Services         Timers          Sockets
(background)     (scheduled)      (network)
```

### Unit Types

Systemd manages different types of "units":

| Unit Type | File Extension | Purpose |
|-----------|---|---------|
| **.service** | `.service` | Background service/daemon |
| **.socket** | `.socket` | Network or IPC socket (activation) |
| **.timer** | `.timer` | Scheduled task (replaces cron) |
| **.path** | `.path` | File/directory monitoring |
| **.target** | `.target` | Logical grouping (runlevels) |
| **.device** | `.device` | Hardware device |
| **.automount** | `.automount` | Filesystem automounting |
| **.mount** | `.mount` | Filesystem mounting |
| **.swap** | `.swap` | Swap activation |
| **.slice** | `.slice` | Cgroup resource division |

---

## 2. Unit File Structure & Syntax

### File Locations

Systemd searches units in this order (first match wins):

```
Priority 1 (Highest - System admin overrides)
/etc/systemd/system/                    User modifications, drop-in overrides

Priority 2 (Highest - Distribution specific)
/run/systemd/system/                    Runtime-generated units

Priority 3 (Default - Distribution/vendor supplied)
/usr/lib/systemd/system/                Default service definitions
/lib/systemd/system/ (symlink to above)
```

### Unit File Format

Systemd uses INI-style configuration:

```ini
# Syntax: [Section]
# Key=Value
# Comments start with # or ;

[Unit]
Description=Human-readable description
Documentation=man:page(1) https://example.com
Requires=other.service
Wants=optional.service
After=network.target
Before=shutdown.target
Conflicts=conflicting.service
ConditionFileExists=/etc/config/file

[Service]
Type=simple
ExecStartPre=/bin/mkdir -p /var/run/myservice
ExecStart=/usr/local/bin/myservice --config /etc/myservice.conf
ExecStartPost=/bin/echo "Started"
ExecReload=/bin/kill -HUP $MAINPID
ExecStop=/bin/kill -TERM $MAINPID
ExecStopPost=/bin/rm -f /var/run/myservice.pid
Restart=on-failure
RestartSec=5

StandardInput=socket
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Essential Sections

#### [Unit] Section

Controls unit metadata and dependencies:

```ini
[Unit]
# Description shown in logs and `systemctl status`
Description=My Custom Security Service

# Additional documentation
Documentation=man:myservice(1)
Documentation=https://docs.example.com/myservice

# Hard dependencies (service fails if these don't start)
Requires=network.target

# Soft dependencies (service continues even if these fail)
Wants=network-online.target

# Ordering: When should this start?
After=network.target
Before=network-online.target

# Conflicting units (can't run together)
Conflicts=incompatible.service

# Conditional startup
ConditionFileExists=/etc/myservice/config
ConditionPathExists=/opt/myservice
ConditionVirtualization=!container
ConditionEnvironment=ENABLE_SERVICE=yes
```

**Useful Target Dependencies:**

```
multi-user.target       Start after basic system setup, networking
graphical.target        Start after full desktop environment
network.target          Start after basic networking
network-online.target   Start after network fully online
sound.target            Start after audio system
```

#### [Service] Section

Controls process execution and behavior:

```ini
[Service]
# Process startup type
Type=simple              # Default: blocking ExecStart
Type=forking             # ExecStart returns, service continues
Type=oneshot             # Runs once, doesn't stay running
Type=dbus                # Registers D-Bus name on start
Type=notify              # Waits for sd_notify() call
Type=idle                # Waits until all jobs complete

# User/group to run as
User=myservice
Group=myservice
SupplementaryGroups=docker

# Process execution with variable expansion
ExecStart=/usr/bin/myservice \
    --config ${CONFIG_PATH} \
    --debug

# Pre-start hooks (run sequentially)
ExecStartPre=/bin/mkdir -p /var/run/myservice
ExecStartPre=/bin/chown myservice:myservice /var/run/myservice

# Post-start hooks
ExecStartPost=/bin/echo "Service started successfully"

# Reload signal handling
ExecReload=/bin/kill -HUP $MAINPID

# Pre-stop hooks
ExecStop=/bin/kill -TERM $MAINPID
ExecStopPost=/bin/rm -f /var/run/myservice.pid

# Restart policy
Restart=always           # Always restart on exit
Restart=on-success       # Only if exit code 0
Restart=on-failure       # If non-zero exit or signal
Restart=on-abnormal      # If signal/timeout (not 0/1)
Restart=no               # Don't restart (default)

# Delay between restarts
RestartSec=5s

# Max restarts before giving up
StartLimitInterval=60s
StartLimitBurst=3

# SIGTERM grace period before SIGKILL
TimeoutStopSec=30s

# Max time for startup
TimeoutStartSec=300s

# I/O handling
StandardInput=null       # /dev/null
StandardInput=socket     # Connected socket
StandardInput=tty        # Terminal input

StandardOutput=inherit   # Inherit from parent
StandardOutput=null      # Discard
StandardOutput=journal   # Send to journald
StandardOutput=journal+console  # Both

StandardError=inherit
StandardError=journal

# Security hardening
PrivateTmp=yes           # Isolated /tmp
PrivateDevices=yes       # No /dev access
PrivateNetwork=yes       # Isolated network namespace
ProtectSystem=strict     # Read-only filesystem
ProtectHome=yes          # Hide /home
NoNewPrivileges=yes      # Can't gain privileges
ReadWritePaths=/var/myservice  # RW exceptions to strict FS

# Resource limits
MemoryLimit=512M
CPUQuota=50%
TasksMax=100

# Environment variables
Environment=FOO=bar
Environment="COMPLEX=value with spaces"
EnvironmentFile=/etc/myservice/config
EnvironmentFile=-/etc/myservice/optional.conf

# Working directory and umask
WorkingDirectory=/var/myservice
UMask=0077

# Restart service on file change (watchdog)
Watchdog=300s
WatchdogSignal=SIGABRT
```

#### [Install] Section

Controls how systemctl enable/disable works:

```ini
[Install]
# Unit links to create when enabled
WantedBy=multi-user.target
WantedBy=graphical.target

# Create symbolic requirement link
RequiredBy=critical-service.service

# Alias names for this unit
Alias=myservice.alias.service

# Configuration file to edit after install
Also=myservice.conf
```

---

## 3. Service Configuration in Detail

### Complete Minimal Service Example

```ini
[Unit]
Description=Minimal Security Scanner Service
After=network.target

[Service]
Type=simple
User=scanner
Group=scanner
ExecStart=/usr/local/bin/security-scanner
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

**File Location:** `/etc/systemd/system/security-scanner.service`

### Complex Service with Multiple Stages

```ini
[Unit]
Description=Advanced Network Penetration Testing Service
Documentation=https://docs.example.com/pentest-service
Requires=network.target
After=syslog.target network.target
Conflicts=incompatible-service.service

[Service]
Type=notify
User=pentest
Group=pentest
SupplementaryGroups=docker,plugdev

# Pre-start validation
ExecStartPre=/usr/bin/test -f /etc/pentest/config.yaml
ExecStartPre=/usr/bin/pentest-validator --config /etc/pentest/config.yaml
ExecStartPre=/bin/mkdir -p /var/run/pentest /var/log/pentest
ExecStartPre=/bin/chown pentest:pentest /var/run/pentest /var/log/pentest

# Main service startup
ExecStart=/usr/local/bin/pentest-daemon \
    --config /etc/pentest/config.yaml \
    --log-level ${LOG_LEVEL:-info} \
    --pid /var/run/pentest/daemon.pid

# Post-start verification
ExecStartPost=/bin/sleep 2
ExecStartPost=/usr/bin/pentest-healthcheck

# Handle HUP signal for config reload
ExecReload=/bin/kill -HUP $MAINPID

# Graceful shutdown
ExecStop=/bin/kill -TERM $MAINPID
TimeoutStopSec=30s
ExecStopPost=/bin/rm -f /var/run/pentest/daemon.pid

# Resource limits
MemoryLimit=2G
CPUQuota=75%
TasksMax=200

# Security hardening
PrivateTmp=yes
PrivateDevices=no       # Needs /dev for wireless
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/etc/pentest /var/run/pentest /var/log/pentest
NoNewPrivileges=yes

# I/O configuration
StandardInput=null
StandardOutput=journal
StandardError=journal
SyslogIdentifier=pentest-daemon

# Restart policy
Restart=on-failure
RestartSec=5s
StartLimitInterval=60s
StartLimitBurst=5

# Environment
Environment=LOG_LEVEL=info
Environment=RUST_BACKTRACE=1
EnvironmentFile=-/etc/sysconfig/pentest-daemon

[Install]
WantedBy=multi-user.target
```

### Service with Socket Activation

**Service file:** `/etc/systemd/system/scanner.service`
```ini
[Unit]
Description=Network Scanner Service
Requires=scanner.socket
After=scanner.socket

[Service]
ExecStart=/usr/local/bin/scanner-daemon
StandardInput=socket
StandardOutput=journal
Restart=on-failure
```

**Socket file:** `/etc/systemd/system/scanner.socket`
```ini
[Unit]
Description=Network Scanner Socket
Before=scanner.service

[Socket]
ListenStream=127.0.0.1:9000
ListenDatagram=127.0.0.1:9001
Accept=yes
SocketMode=0600
SocketUser=scanner
SocketGroup=scanner

[Install]
WantedBy=sockets.target
```

---

## 4. Advanced Systemd Features

### Timer Units (Cron Replacement)

**Service:** `/etc/systemd/system/security-audit.service`
```ini
[Unit]
Description=Security Audit Task
Wants=security-audit.timer

[Service]
Type=oneshot
ExecStart=/usr/local/bin/run-security-audit.sh
User=root
StandardOutput=journal
StandardError=journal
```

**Timer:** `/etc/systemd/system/security-audit.timer`
```ini
[Unit]
Description=Daily Security Audit
Requires=security-audit.service

[Timer]
# Run at 2:00 AM every day
OnCalendar=*-*-* 02:00:00

# Or: Run every hour
# OnUnitActiveSec=1h

# Or: Run on boot + every 6 hours
# OnBootSec=10min
# OnUnitActiveSec=6h

# Randomize start within 15 minutes (avoid thundering herd)
RandomizedDelaySec=15min

# If missed, run immediately when systemd starts
Persistent=yes

[Install]
WantedBy=timers.target
```

**Calendar Specification Syntax:**
```
*-*-* 02:30:00         # Daily at 2:30 AM
Mon *-*-* 09:00:00     # Every Monday at 9 AM
*-01,07-01 00:00:00    # 1st of Jan and July at midnight
*/4:*:00              # Every 4 hours on the hour
Sat 15:00:00          # Every Saturday at 3 PM
```

### Path Units (File Watching)

Trigger service when file changes:

**Path:** `/etc/systemd/system/config-monitor.path`
```ini
[Unit]
Description=Monitor Configuration File Changes
Wants=config-monitor.service

[Path]
# Trigger when file is modified
PathChanged=/etc/myservice/config.yaml

# Or: when file exists/doesn't exist
# PathExists=/run/myservice/enable
# PathExistsGlob=/etc/myservice/*.conf

# Only trigger if path already existed
MakeDirectory=yes

[Install]
WantedBy=paths.target
```

**Service:** `/etc/systemd/system/config-monitor.service`
```ini
[Unit]
Description=Configuration Reload Handler
After=config-monitor.path

[Service]
Type=oneshot
ExecStart=/usr/local/bin/reload-config.sh
```

### Template Units

Create multiple instances from single unit file:

**Template Service:** `/etc/systemd/system/wireless-interface@.service`
```ini
[Unit]
Description=Wireless Interface Monitor for %i
After=network-online.target

[Service]
Type=simple
ExecStart=/usr/local/bin/monitor-interface %i
Restart=on-failure

# Variables available:
# %i  - Instance name (wlan0)
# %I  - Full unescaped instance name
# %j  - First component of instance name
# %p  - Prefix (service name before @)
# %n  - Full unit name (wireless-interface@wlan0.service)

[Install]
WantedBy=multi-user.target
```

**Enable instances:**
```bash
systemctl enable wireless-interface@wlan0.service
systemctl enable wireless-interface@wlan1.service
```

---

## 5. Practical Examples for Security Tools

### Example 1: Nmap Service Wrapper

```ini
[Unit]
Description=Nmap Network Discovery Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=nmap
Group=nmap

# Pre-start checks
ExecStartPre=/usr/bin/test -d /var/lib/nmap
ExecStartPre=/usr/bin/test -r /etc/nmap/targets.txt

# Run nmap with logging
ExecStart=/usr/bin/nmap \
    -iL /etc/nmap/targets.txt \
    -oN /var/log/nmap/scan-%t.log \
    --data-length=random \
    -T4

StandardOutput=journal
StandardError=journal
SyslogIdentifier=nmap-service

# Resource limits
MemoryLimit=1G
CPUQuota=80%
TasksMax=50

[Install]
WantedBy=multi-user.target
```

### Example 2: Custom Penetration Testing Agent

```ini
[Unit]
Description=Penetration Testing Agent
Documentation=https://github.com/example/pentest-agent
After=network-online.target
Requires=network-online.target

[Service]
Type=notify
ExecStart=/opt/pentest-agent/bin/agent

User=pentest
Group=pentest

WorkingDirectory=/opt/pentest-agent
StandardOutput=journal
StandardError=journal
SyslogIdentifier=pentest-agent

# Security hardening
PrivateTmp=yes
PrivateDevices=no
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/opt/pentest-agent /var/log/pentest-agent

NoNewPrivileges=yes

# Capabilities instead of running as root
AmbientCapabilities=CAP_NET_RAW CAP_NET_ADMIN

# Resource constraints
MemoryLimit=2G
CPUQuota=50%

# Restart policy
Restart=on-failure
RestartSec=10s
StartLimitInterval=300s
StartLimitBurst=5

# Watchdog
Watchdog=60s

[Install]
WantedBy=multi-user.target
```

### Example 3: Bluetooth Exploitation Service

```ini
[Unit]
Description=Bluetooth Device Security Scanner
After=bluetooth.target
Wants=bluetooth.target
PartOf=bluetooth.target

[Service]
Type=simple
ExecStart=/usr/local/bin/ble-scanner \
    --output /var/log/ble-scanner.log \
    --interval 30

User=ble-scanner
Group=ble-scanner

StandardOutput=journal
StandardError=journal

# Need access to /dev/hci* and /proc/bus/usb
PrivateDevices=no
ProtectSystem=strict
ReadWritePaths=/var/log /var/lib/ble-scanner

# Bluetooth-specific capabilities
AmbientCapabilities=CAP_NET_RAW CAP_NET_ADMIN CAP_SYS_ADMIN

MemoryLimit=512M
CPUQuota=25%

Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

---

## 6. Debugging & Troubleshooting

### Check Unit Status

```bash
# Detailed status
systemctl status myservice.service

# Show process info
systemctl status -l myservice.service

# Show active state + PID
systemctl is-active myservice.service
systemctl show -p MainPID myservice.service
```

### View Service Logs

```bash
# Last 100 lines
journalctl -u myservice.service -n 100

# Real-time follow
journalctl -u myservice.service -f

# Specific time range
journalctl -u myservice.service --since "2024-01-15 10:00" --until "2024-01-15 11:00"

# Show with full details
journalctl -u myservice.service -o verbose

# Previous boots
journalctl -u myservice.service -b -1
```

### Validate Unit File

```bash
# Check syntax
systemd-analyze verify myservice.service

# Show unit file content
systemctl cat myservice.service

# Show unit dependencies
systemctl list-dependencies myservice.service
```

### Test Before Enabling

```bash
# Load unit without starting
systemctl daemon-reload
systemctl show myservice.service

# Start in foreground for debugging
systemd-run --scope -p StandardOutput=journal /usr/bin/myservice

# Run with strace
systemctl stop myservice.service
systemd-run --scope strace -f -e trace=file /usr/bin/myservice
```

### Common Issues

**Issue: Service starts but crashes immediately**
```bash
# View exit status
journalctl -u myservice.service | grep "code=exited"

# Check with ExecStartPre validation
# Add: ExecStartPre=/usr/bin/sh -c "command validation here"
```

**Issue: Service doesn't restart automatically**
```bash
# Check restart policy
systemctl show -p Restart myservice.service

# Check restart limit
systemctl show -p StartLimitBurst myservice.service
systemctl show -p StartLimitIntervalSec myservice.service
```

**Issue: Permissions denied**
```bash
# Check user/group
systemctl show -p User myservice.service
systemctl show -p Group myservice.service

# Check file ownership
ls -la /etc/systemd/system/myservice.service
```

### Debug Mode

```bash
# Run systemd with debug logging
systemctl set-environment SYSTEMD_LOG_LEVEL=debug
journalctl -u systemd -f

# Reset
systemctl unset-environment SYSTEMD_LOG_LEVEL
```

---

## 7. Security Considerations

### Principle of Least Privilege

```ini
[Service]
# Run as unprivileged user
User=service-user
Group=service-group

# Use minimal capabilities instead of root
AmbientCapabilities=CAP_NET_RAW CAP_CHOWN
CapabilityBoundingSet=CAP_NET_RAW CAP_CHOWN CAP_SETFCAP

# Prevent privilege escalation
NoNewPrivileges=yes

# Restrict filesystem access
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/var/lib/myservice /var/log/myservice
```

### Sandboxing

```ini
[Service]
# Filesystem isolation
PrivateTmp=yes                  # Separate /tmp
ProtectSystem=strict            # Read-only /usr, /etc, /boot
ProtectHome=yes                 # Hide /home, /root, /run/user

# Process isolation
PrivateDevices=yes              # No /dev access
ProtectClock=yes                # Can't set system clock
ProtectHostname=yes             # Can't change hostname
ProtectKernelLogs=yes           # No kernel log access
RestrictNamespaces=yes          # Can't create namespaces

# Network isolation
PrivateNetwork=yes              # Separate network ns (if not needed)
RestrictAddressFamilies=AF_INET AF_INET6

# System call filtering
SystemCallFilter=@system-service
SystemCallFilter=~@privileged @resources
SystemCallErrorNumber=EPERM     # Return EPERM on blocked calls
```

### Audit & Monitoring

```ini
[Service]
# Log all execution
StandardOutput=journal
StandardError=journal
SyslogIdentifier=myservice

# Enable systemd audit
AuditMode=yes

# Resource monitoring
MemoryAccounting=yes
TasksAccounting=yes
CPUAccounting=yes

# Restart on abnormal termination
Restart=on-failure
RestartSec=5s
StartLimitBurst=3
StartLimitIntervalSec=60s
```

---

## Quick Reference

### Essential systemctl Commands

```bash
# Enable/disable (auto-start on boot)
systemctl enable myservice.service
systemctl disable myservice.service

# Start/stop/restart
systemctl start myservice.service
systemctl stop myservice.service
systemctl restart myservice.service
systemctl reload myservice.service

# Check status
systemctl status myservice.service
systemctl is-active myservice.service
systemctl is-enabled myservice.service

# Reread configuration
systemctl daemon-reload

# Show unit details
systemctl cat myservice.service
systemctl show myservice.service

# List all units
systemctl list-units --type=service
systemctl list-unit-files

# Create drop-in override
systemctl edit myservice.service

# View logs
journalctl -u myservice.service -f
```

This completes systemd configuration. Part 3 will cover SysV init scripts and alternative init systems.
