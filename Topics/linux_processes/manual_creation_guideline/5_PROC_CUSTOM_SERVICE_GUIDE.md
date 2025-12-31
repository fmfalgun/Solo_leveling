# Creating a Custom Service & Monitoring Its /proc Presence

## Part 1: Understanding How Services Work

### Traditional Method: Direct Execution
```bash
# User runs program manually
$ /usr/local/bin/myapp --config=/etc/myapp.conf

# Kernel's view:
fork() → PID 54321 created
execve("/usr/local/bin/myapp") → Binary loaded
    ↓
/proc/54321/ created with:
  - cmdline: "/usr/local/bin/myapp --config=/etc/myapp.conf"
  - exe: → /usr/local/bin/myapp
  - stat: S (sleeping), consuming resources
```

### Modern Method: Systemd Service

**Systemd:**
- Daemon manager that starts services at boot
- Monitors process state
- Restarts if crashed
- Manages dependencies
- Allocates cgroups for resource control

---

## Part 2: Step-by-Step Creating a Custom Service

### Step 1: Create the Executable

**File:** `/usr/local/bin/mystatus.py`

```python
#!/usr/bin/env python3
"""
A simple monitoring service that logs system status every 5 seconds.
"""

import time
import os
import sys
import logging

# Setup logging
logging.basicConfig(
    filename='/var/log/mystatus.log',
    level=logging.INFO,
    format='%(asctime)s [%(process)d] %(levelname)s: %(message)s'
)

def log_system_info():
    """Log current process and system state."""
    pid = os.getpid()
    
    logging.info(f"Service running (PID {pid})")
    
    # These will appear in /proc/$pid/...
    try:
        with open(f'/proc/{pid}/stat') as f:
            stat_line = f.read().split()
            logging.info(f"State: {stat_line[2]}, CPU: {stat_line[13]+stat_line[14]} jiffies")
    except:
        pass
    
    try:
        with open(f'/proc/{pid}/statm') as f:
            mem_line = f.read().split()
            logging.info(f"Memory: {int(mem_line[1])*4} KB resident")
    except:
        pass

def main():
    logging.info("=== MyStatus Service Started ===")
    logging.info(f"PID: {os.getpid()}")
    
    try:
        while True:
            log_system_info()
            time.sleep(5)
    except KeyboardInterrupt:
        logging.info("=== MyStatus Service Shutting Down ===")
        sys.exit(0)

if __name__ == '__main__':
    main()
```

**Make executable:**
```bash
chmod +x /usr/local/bin/mystatus.py
```

---

### Step 2: Create Systemd Service File

**File:** `/etc/systemd/system/mystatus.service`

```ini
[Unit]
Description=My Custom Status Monitoring Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/mystatus.py
User=mystatus
Group=mystatus

Restart=on-failure
RestartSec=5

StandardOutput=journal
StandardError=journal

MemoryLimit=512M
CPUQuota=50%

[Install]
WantedBy=multi-user.target
```

---

### Step 3: Create System User

```bash
sudo useradd -r -s /bin/false -d /var/lib/mystatus -m mystatus
id mystatus
```

---

### Step 4: Set Permissions & Start

```bash
# Create log directory
sudo mkdir -p /var/log
sudo touch /var/log/mystatus.log
sudo chown mystatus:mystatus /var/log/mystatus.log

# Reload systemd
sudo systemctl daemon-reload

# Start service
sudo systemctl start mystatus.service

# Check status
sudo systemctl status mystatus.service
```

---

## Part 3: How the Service Appears in /proc

### Find the PID
```bash
PID=$(systemctl show mystatus.service -p MainPID | cut -d= -f2)
echo "Service PID: $PID"
```

### Explore /proc/$pid/
```bash
# List all files
ls -la /proc/$PID/

# Check command line
cat /proc/$PID/cmdline | tr '\0' ' '

# Check state
awk '{print "State: " $3 ", CPU: " $14+$15 " jiffies"}' /proc/$PID/stat

# Check memory
awk '{printf "Virtual: %d KB, Resident: %d KB\n", $1*4, $2*4}' /proc/$PID/statm

# Find open files
ls -la /proc/$PID/fd/

# Check log file
readlink /proc/$PID/fd/1
```

---

## Part 4: Real-Time Monitoring Scripts

### Monitor 1: Watch State in Real-Time

```bash
#!/bin/bash
PID=$(systemctl show mystatus.service -p MainPID | cut -d= -f2)

echo "Monitoring mystatus (PID $PID)..."
echo "Update every 1 second. Press Ctrl+C to stop."

while true; do
  state=$(awk '{print $3}' /proc/$PID/stat 2>/dev/null || echo "Z")
  mem=$(awk '{printf "%.1f", $2*4/1024}' /proc/$PID/statm 2>/dev/null || echo "0")
  cpu=$(awk '{print $14+$15}' /proc/$PID/stat 2>/dev/null || echo "0")
  
  printf "$(date +%H:%M:%S) | State: %s | Memory: %s MB | CPU: %s\n" "$state" "$mem" "$cpu"
  sleep 1
done
```

### Monitor 2: Alert on Resource Violations

```bash
#!/bin/bash
PID=$(systemctl show mystatus.service -p MainPID | cut -d= -f2)

MAX_MEMORY_MB=512
MAX_CPU_PERCENT=50

while true; do
  rss=$(awk '{print int($2*4/1024)}' /proc/$PID/statm 2>/dev/null || echo 0)
  if [[ $rss -gt $MAX_MEMORY_MB ]]; then
    echo "ALERT: Memory exceeded! $rss MB > $MAX_MEMORY_MB MB"
  fi
  
  sleep 5
done
```

---

## Part 5: Service Lifecycle in /proc

```
fork()  ──→  /proc/$pid/ CREATED
              stat initialized

exec()  ──→  exe, cmdline, maps UPDATED
              Binary loaded

RUNNING ──→  stat fields 14,15 INCREASE
              wchan = "-" (running)

I/O     ──→  fd/, io UPDATED
              Files opened/closed

BLOCKED ──→  wchan = kernel function
              stat.state = S

EXIT    ──→  stat.state = Z (zombie)
              Persists until parent wait()

CLEANUP ──→  /proc/$pid/ DELETED
              Kernel cleanup complete
```

---

## Part 6: Debugging Service Issues

### Issue: Service Crashes Immediately

```bash
# Check exit status
systemctl show mystatus.service -p ExecMainStatus

# See what happened
journalctl -u mystatus.service -n 20
```

### Issue: Service Using Too Much Memory

```bash
# Track memory over time
PID=$(systemctl show mystatus.service -p MainPID | cut -d= -f2)
while true; do
  awk '{printf "%s: %.1f MB\n", "'$(date)'", $2*4/1024}' /proc/$PID/statm
  sleep 1
done
```

### Issue: Service Won't Start Due to Permissions

```bash
# Check user exists
id mystatus

# Check file permissions
ls -la /usr/local/bin/mystatus.py
ls -la /var/log/mystatus.log

# Check systemd errors
journalctl -u mystatus.service -n 20
```

---

**This completes the service creation guide. Follow these steps to deploy a custom service and monitor it via /proc!**

