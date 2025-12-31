# Linux Processes: Quick Reference & Decision Guide
## Part 5: Implementation Checklist & Deployment Guide

---

## 1. Quick Decision Tree: Choose Your Approach

```
Do you need a background service running continuously?
│
├─ YES, on modern Linux (Ubuntu 18+, Debian 10+, CentOS 7+)
│  │
│  └─ → USE SYSTEMD (.service files)
│       Advantages: Standardized, logging integrated, dependency management
│       See: Part 2 (systemd guide)
│
├─ YES, but on older Linux or embedded system
│  │
│  └─ → CHOOSE:
│       ├─ SysV init scripts (backward compatible)
│       │  See: Part 3 (SysV guide)
│       │
│       └─ OpenRC (lightweight alternative)
│          See: Part 3 (OpenRC section)
│
├─ YES, and you need maximum control/low footprint
│  │
│  └─ → CUSTOM C DAEMON
│       Advantages: Minimal dependencies, precise control
│       See: Part 4 (C daemon guide)
│
└─ YES, and you want rapid prototyping/flexibility
   │
   └─ → PYTHON DAEMON
        Advantages: Easy development, good debugging
        See: Part 4 (Python daemon guide)
```

---

## 2. Service Checklist: From Concept to Production

### Phase 1: Development (Local Testing)

- [ ] Write and compile/test service code
  ```bash
  # For C:
  gcc -Wall -o myservice myservice.c
  ./myservice --help
  
  # For Python:
  python3 myservice.py --help
  ```

- [ ] Test with systemd-run (simulate systemd environment):
  ```bash
  systemd-run --scope ./myservice
  ```

- [ ] Verify signal handling:
  ```bash
  # In another terminal
  kill -TERM $(pgrep myservice)
  # Check if service shuts down gracefully
  ```

- [ ] Check resource usage:
  ```bash
  # Monitor while running
  top -p $(pgrep myservice)
  ```

### Phase 2: Create Service Unit/Script

**For Systemd:**
```bash
sudo nano /etc/systemd/system/myservice.service
# [Copy template from Part 2]
sudo systemctl daemon-reload
sudo systemctl start myservice.service
sudo systemctl status myservice.service
```

**For SysV:**
```bash
sudo nano /etc/init.d/myservice
# [Copy template from Part 3]
sudo chmod +x /etc/init.d/myservice
sudo service myservice start
sudo service myservice status
```

- [ ] Verify service starts correctly
- [ ] Verify service is running as expected user
- [ ] Check logs for errors:
  ```bash
  # Systemd:
  journalctl -u myservice.service -f
  
  # SysV:
  tail -f /var/log/myservice.log
  ```

### Phase 3: Security Hardening

- [ ] **Run as unprivileged user:**
  ```ini
  [Service]
  User=myservice
  Group=myservice
  ```

- [ ] **Minimize capabilities (C daemons):**
  ```c
  /* Drop unnecessary capabilities */
  cap_t caps = cap_from_text("cap_net_raw=ep");
  cap_set_proc(caps);
  ```

- [ ] **Enable sandbox features (Systemd):**
  ```ini
  [Service]
  PrivateTmp=yes
  ProtectSystem=strict
  ProtectHome=yes
  NoNewPrivileges=yes
  ```

- [ ] **Restrict file access:**
  ```ini
  [Service]
  ReadWritePaths=/var/lib/myservice
  ProtectKernelLogs=yes
  ProtectKernelTunables=yes
  ```

- [ ] **Set resource limits:**
  ```ini
  [Service]
  MemoryLimit=512M
  CPUQuota=50%
  TasksMax=100
  ```

### Phase 4: Logging & Monitoring

- [ ] Configure logging output:
  ```ini
  [Service]
  StandardOutput=journal
  StandardError=journal
  SyslogIdentifier=myservice
  ```

- [ ] Test log output:
  ```bash
  journalctl -u myservice.service | head -20
  ```

- [ ] Set up log rotation (if file-based):
  ```bash
  sudo nano /etc/logrotate.d/myservice
  # Add rotation policy
  ```

- [ ] Monitor health:
  ```bash
  systemctl show myservice -p State
  systemctl show myservice -p ActiveState
  ```

### Phase 5: Restart & Recovery

- [ ] Configure restart policy:
  ```ini
  [Service]
  Restart=on-failure
  RestartSec=5s
  StartLimitBurst=3
  StartLimitIntervalSec=60s
  ```

- [ ] Test restart behavior:
  ```bash
  # Kill the service
  sudo kill -9 $(pgrep myservice)
  
  # Verify it restarts
  sleep 2
  systemctl status myservice
  ```

### Phase 6: Startup & Shutdown

- [ ] Enable auto-start on boot:
  ```bash
  sudo systemctl enable myservice.service
  # or for SysV:
  # sudo update-rc.d myservice defaults
  ```

- [ ] Verify boot behavior:
  ```bash
  # Test in isolated environment or VM
  systemctl reboot
  systemctl status myservice.service
  ```

- [ ] Test graceful shutdown:
  ```bash
  sudo systemctl stop myservice.service --no-block
  journalctl -u myservice.service -f  # Watch logs
  ```

### Phase 7: Testing Checklist

- [ ] [ ] Service starts successfully
- [ ] [ ] Service runs with correct user/group
- [ ] [ ] Service restarts on failure
- [ ] [ ] Service handles SIGTERM gracefully
- [ ] [ ] Service logs to correct location
- [ ] [ ] Service enables on boot
- [ ] [ ] Service stops cleanly on shutdown
- [ ] [ ] No zombie processes left behind
- [ ] [ ] Resource usage is acceptable
- [ ] [ ] Configuration reload works (if applicable)

---

## 3. Common Service Configurations by Use Case

### Simple Network Service

```ini
[Unit]
Description=My Network Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/local/bin/myservice
Restart=on-failure
RestartSec=5s

StandardOutput=journal
StandardError=journal

User=myservice
Group=myservice

[Install]
WantedBy=multi-user.target
```

### Long-Running Batch Job

```ini
[Unit]
Description=Batch Processing Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/batch-processor --config /etc/batch.conf

# Resource limits
MemoryLimit=2G
CPUQuota=100%
TasksMax=500

# Restart policy (conservative for batch jobs)
Restart=on-failure
RestartSec=30s
StartLimitBurst=2

StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Security Tool (Penetration Testing)

```ini
[Unit]
Description=Security Scanning Service
After=network-online.target

[Service]
Type=simple
ExecStart=/opt/security-tool/bin/scanner

User=security
Group=security
SupplementaryGroups=docker,wireshark

# Capabilities for network access
AmbientCapabilities=CAP_NET_RAW CAP_NET_ADMIN CAP_SYS_ADMIN

# Sandboxing
PrivateDevices=no
ProtectSystem=strict
ReadWritePaths=/opt/security-tool /var/log/security-tool

StandardOutput=journal
StandardError=journal

Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

### Periodic Task (Like Cron)

```ini
[Unit]
Description=Periodic Security Audit
Wants=security-audit.timer

[Service]
Type=oneshot
ExecStart=/usr/local/bin/security-audit.sh
StandardOutput=journal
StandardError=journal
```

And the timer:
```ini
[Unit]
Description=Daily Security Audit Timer

[Timer]
OnCalendar=daily
OnCalendar=*-*-* 02:00:00
Persistent=yes
RandomizedDelaySec=15min

[Install]
WantedBy=timers.target
```

---

## 4. Language-Specific Implementation Patterns

### C Daemon Pattern

```
myservice.c (100-500 lines)
    ├─ daemonize() function
    ├─ signal handlers (SIGTERM, SIGHUP, SIGCHLD)
    ├─ main event loop
    └─ graceful shutdown

Compilation:
    gcc -Wall -O2 -o myservice myservice.c -lm

Integration:
    /usr/local/bin/myservice (executable)
    /etc/systemd/system/myservice.service (unit file)
```

**Advantages:**
- Minimal dependencies
- Fine-grained control
- Excellent performance
- Suitable for security-critical code

**Disadvantages:**
- More complex to write
- Requires C knowledge
- Longer development time

### Python Daemon Pattern

```
mydaemon.py (50-200 lines)
    ├─ Daemon class (signal handling)
    ├─ MyService subclass (business logic)
    └─ if __name__ == '__main__': MyService().start()

Dependencies:
    pip install python-daemon pyyaml

Integration:
    /usr/local/bin/mydaemon (Python script)
    /etc/systemd/system/mydaemon.service
    /etc/mydaemon/config.yaml (config file)
```

**Advantages:**
- Rapid development
- Easy debugging
- Good for prototyping
- Large library ecosystem

**Disadvantages:**
- Python runtime dependency
- Slightly higher overhead
- Startup time

### Bash Script Pattern

```
/etc/init.d/myservice (50-150 lines)
    ├─ LSB header
    ├─ start_daemon function
    ├─ stop_daemon function
    └─ case statement for actions

Integration:
    sudo update-rc.d myservice defaults
    sudo service myservice start
```

**Advantages:**
- Simple and portable
- Easy to understand
- No compilation needed

**Disadvantages:**
- Limited error handling
- Poor signal handling
- Slower startup

---

## 5. File Locations Reference

### Systemd Files
```
/etc/systemd/system/          Unit files (admin customization)
/etc/systemd/system/service.service.d/  Drop-in overrides
/run/systemd/system/          Runtime-generated units
/usr/lib/systemd/system/      Vendor-supplied defaults
/var/run/service.pid          Runtime PID file
```

### SysV Files
```
/etc/init.d/                  Init scripts
/etc/rc0.d/ - /etc/rc6.d/     Runlevel symlinks
/etc/default/service          Service configuration
/var/run/service.pid          Runtime PID file
```

### Log Files
```
/var/log/service.log          Application logs
/var/log/syslog               System log (legacy)
journalctl -u service         Systemd journal
```

### Configuration Files
```
/etc/service/config.yaml      Service configuration
/etc/service/                 Configuration directory
/etc/default/service          Environment variables
/etc/sysconfig/service        RedHat-style config
```

---

## 6. Troubleshooting Guide

### Service Won't Start

```bash
# Check syntax
systemd-analyze verify myservice.service

# View full error
journalctl -u myservice.service -n 50

# Test startup command directly
strace /usr/local/bin/myservice

# Check dependencies
systemctl list-dependencies myservice.service
```

**Common Issues:**
- Missing config file → Add `ExecStartPre=/bin/test -f /path/to/config`
- Permission denied → Check User= and file ownership
- Executable not found → Verify ExecStart path
- Port already in use → Check for previous instance, kill zombie

### Service Crashes Immediately

```bash
# Check exit code
journalctl -u myservice.service | grep "code=exited"

# Run in foreground to see output
systemd-run --scope myservice

# Add debugging
ExecStartPre=/bin/sh -c "echo Starting >> /tmp/debug.log"
```

### Service Not Restarting

```bash
# Check restart policy
systemctl show -p Restart myservice.service

# Check restart limits
systemctl show -p StartLimitBurst myservice.service
systemctl show -p StartLimitIntervalSec myservice.service

# Reset limit
systemctl reset-failed myservice.service
```

### High CPU/Memory Usage

```bash
# Monitor process
top -p $(pgrep myservice)

# Check for memory leaks
valgrind /usr/local/bin/myservice  # If compiled with debug

# Add resource limits
MemoryLimit=512M
CPUQuota=50%
```

### Zombie Processes

```bash
# Identify zombies
ps aux | grep Z
ps -o ppid= $(pgrep myservice)

# Cause: Parent not waiting for children
# Solution: Add SIGCHLD handler
signal(SIGCHLD, SIG_IGN);  # or proper handler
```

---

## 7. Performance Tuning

### CPU Affinity
```ini
[Service]
CPUAffinity=0 1 2 3
CPUSchedulingPolicy=batch
```

### Memory Management
```ini
[Service]
MemoryAccounting=yes
MemoryLimit=1G
MemoryMax=2G
MemorySwapMax=0  # No swap
```

### I/O Scheduling
```ini
[Service]
IOSchedulingClass=idle
IOSchedulingPriority=7  # Lowest priority for I/O
```

### CPU Scheduling
```ini
[Service]
CPUQuota=75%          # Use max 75% of one core
CPUSchedulingPolicy=rr
CPUSchedulingPriority=10  # Real-time priority
```

---

## 8. Security Hardening Checklist

- [ ] **Run as unprivileged user**
  ```ini
  User=myservice
  Group=myservice
  ```

- [ ] **Limit filesystem access**
  ```ini
  ProtectSystem=strict
  ProtectHome=yes
  ReadWritePaths=/var/lib/myservice
  ```

- [ ] **Drop unnecessary capabilities**
  ```ini
  AmbientCapabilities=CAP_NET_RAW
  CapabilityBoundingSet=CAP_NET_RAW
  ```

- [ ] **Prevent privilege escalation**
  ```ini
  NoNewPrivileges=yes
  ```

- [ ] **Isolate /tmp**
  ```ini
  PrivateTmp=yes
  ```

- [ ] **Hide /dev**
  ```ini
  PrivateDevices=yes
  ```

- [ ] **Disable system call namespaces**
  ```ini
  RestrictNamespaces=yes
  ```

- [ ] **Syscall filtering**
  ```ini
  SystemCallFilter=~@privileged @resources
  SystemCallErrorNumber=EPERM
  ```

- [ ] **Audit logging**
  ```ini
  AuditMode=yes
  ```

---

## 9. Deployment Commands

### Initial Setup

```bash
# Install executable
sudo cp myservice /usr/local/bin/
sudo chmod 755 /usr/local/bin/myservice

# Create user
sudo useradd -r -s /bin/false myservice

# Create directories
sudo mkdir -p /var/lib/myservice /var/log/myservice
sudo chown -R myservice:myservice /var/lib/myservice /var/log/myservice

# Install config
sudo mkdir -p /etc/myservice
sudo cp myservice.conf /etc/myservice/
sudo chown -R myservice:myservice /etc/myservice
sudo chmod 755 /etc/myservice
sudo chmod 640 /etc/myservice/myservice.conf
```

### Install Service (Systemd)

```bash
# Install unit file
sudo cp myservice.service /etc/systemd/system/

# Reload daemon
sudo systemctl daemon-reload

# Enable auto-start
sudo systemctl enable myservice.service

# Start service
sudo systemctl start myservice.service

# Verify
sudo systemctl status myservice.service
sudo journalctl -u myservice.service -f
```

### Install Service (SysV)

```bash
# Install script
sudo cp myservice /etc/init.d/
sudo chmod 755 /etc/init.d/myservice

# Enable auto-start
sudo update-rc.d myservice defaults

# Start service
sudo service myservice start

# Verify
sudo service myservice status
tail -f /var/log/myservice.log
```

### Update Service

```bash
# Stop service
sudo systemctl stop myservice.service

# Update files
sudo cp myservice /usr/local/bin/
sudo cp myservice.conf /etc/myservice/

# Start service
sudo systemctl start myservice.service

# Check status
sudo systemctl status myservice.service
```

### Remove Service

```bash
# Stop service
sudo systemctl stop myservice.service

# Disable auto-start
sudo systemctl disable myservice.service

# Remove files
sudo rm /etc/systemd/system/myservice.service
sudo rm /usr/local/bin/myservice
sudo rm -rf /etc/myservice /var/lib/myservice /var/log/myservice

# Clean up user
sudo userdel myservice

# Reload daemon
sudo systemctl daemon-reload
```

---

## 10. Monitoring Template

### Health Check Script

```bash
#!/bin/bash

SERVICE="myservice"
PIDFILE="/var/run/$SERVICE.pid"
LOGFILE="/var/log/$SERVICE/$SERVICE.log"

# Check if running
if ! systemctl is-active --quiet $SERVICE; then
    echo "CRITICAL: $SERVICE is not running"
    exit 2
fi

# Check recent errors
if grep -q "ERROR" $LOGFILE; then
    echo "WARNING: Recent errors found in log"
    exit 1
fi

# Check disk space
DISK_USAGE=$(du -s /var/lib/$SERVICE | awk '{print $1}')
if [ $DISK_USAGE -gt 1000000 ]; then  # 1GB
    echo "WARNING: $SERVICE using excessive disk space"
    exit 1
fi

echo "OK: $SERVICE is healthy"
exit 0
```

### Monitoring with Nagios/Icinga

```ini
# /etc/nagios/objects/myservice.cfg

define service{
    use                     local-service
    host_name               localhost
    service_description     MyService Status
    check_command           check_systemd!myservice.service
}

define service{
    use                     local-service
    host_name               localhost
    service_description     MyService Disk Usage
    check_command           check_local_disk!20%!10%!/var/lib/myservice
}
```

---

## Summary & Next Steps

You now have:
- **Part 1**: Understanding of Linux process fundamentals and kernel-level concepts
- **Part 2**: Complete systemd service configuration guide with examples
- **Part 3**: Traditional SysV and OpenRC init systems
- **Part 4**: Custom daemon development in C and Python
- **Part 5**: Implementation checklist and deployment guide

### For Your First Service:

1. **Choose platform**: Systemd (most modern distributions)
2. **Pick language**: Python for rapid development, C for security-critical code
3. **Follow the checklist** in Phase 1-7
4. **Test thoroughly** before production
5. **Monitor and log** for operational visibility
6. **Harden security** based on the checklist

### Recommended Reading Order:

- Security professionals: Focus on Part 4 (daemon development) + Part 2 (systemd hardening)
- DevOps/SysAdmin: Focus on Part 2 (systemd) + Phase 1-7 checklist
- Embedded/IoT: Focus on Part 3 (OpenRC) + Part 4 (C daemons)

Good luck with your process management implementation!
