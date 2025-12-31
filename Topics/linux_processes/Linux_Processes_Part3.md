# Linux Processes: Comprehensive Technical Guide
## Part 3: SysV Init Scripts & Traditional Process Management

---

## Table of Contents
1. SysV Init System Overview
2. Init Script Structure & Syntax
3. SysV Runlevels
4. Creating & Managing Init Scripts
5. Start-Stop-Daemon Utility
6. Service Management Commands
7. OpenRC Alternative
8. Comparison: SysV vs. Systemd

---

## 1. SysV Init System Overview

### Historical Context

Before systemd (2015+), Linux systems used **SysV init** (System V init), derived from AT&T System V Unix. Key characteristics:

- **Sequential startup**: Services start one at a time (slower)
- **Runlevel-based**: Different target states (runlevel 3 = multi-user)
- **Script-based**: Shell scripts in `/etc/init.d/`
- **No dependency resolution**: Admin specifies start order via symlinks

### SysV Directory Structure

```
/etc/init.d/                    # Init scripts (executable)
├── service1
├── service2
└── service3

/etc/rc0.d/ - /etc/rc6.d/       # Runlevel directories
├── /etc/rc0.d/ (runlevel 0 - shutdown)
├── /etc/rc1.d/ (runlevel 1 - single-user)
├── /etc/rc2.d/ (runlevel 2 - multi-user)
├── /etc/rc3.d/ (runlevel 3 - multi-user with networking)
├── /etc/rc4.d/ (runlevel 4 - user-defined)
├── /etc/rc5.d/ (runlevel 5 - graphical multi-user)
└── /etc/rc6.d/ (runlevel 6 - reboot)

Each rcX.d/ contains symlinks to /etc/init.d/ scripts:
S20service  (S = start, 20 = priority)
K30service  (K = stop, 30 = priority)
```

### Startup Sequence

```
Kernel Boot
    ↓
/sbin/init (PID 1)
    ↓
Read /etc/inittab (runlevel specification)
    ↓
Execute /etc/rc.d/rc.sysinit (common initialization)
    ↓
Execute scripts in /etc/rcX.d/ (for current runlevel)
    ↓
Start getty (login prompts)
    ↓
System Ready
```

---

## 2. Init Script Structure & Syntax

### Basic Init Script Template

```bash
#!/bin/bash

### BEGIN INIT INFO
# Provides:          myservice
# Required-Start:    $network $remote_fs
# Required-Stop:     $network $remote_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: My Custom Service
# Description:       Detailed description of what this service does
### END INIT INFO

# Sourcing standard functions
. /lib/lsb/init-functions
# or (older systems)
. /etc/rc.d/init.d/functions

# Variables
NAME="myservice"
DAEMON="/usr/local/bin/myservice"
PIDFILE="/var/run/$NAME.pid"
SCRIPTNAME="/etc/init.d/$NAME"
USER="myservice"
GROUP="myservice"

# Check if daemon exists
[ -x "$DAEMON" ] || exit 0

# Source defaults if they exist
[ -f "/etc/default/$NAME" ] && . "/etc/default/$NAME"

start() {
    echo "Starting $NAME"
    start_daemon -p "$PIDFILE" "$DAEMON"
    log_end_msg $?
}

stop() {
    echo "Stopping $NAME"
    killproc -p "$PIDFILE" "$DAEMON"
    log_end_msg $?
}

restart() {
    stop
    sleep 1
    start
}

status() {
    status_of_proc -p "$PIDFILE" "$DAEMON" "$NAME"
    exit $?
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $SCRIPTNAME {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0
```

### Detailed Script Components

#### LSB Header (LSB = Linux Standard Base)

The header comment is parsed by tools to understand dependencies:

```bash
### BEGIN INIT INFO
# Provides:          myservice
#   The service name this script provides

# Required-Start:    $network $syslog
#   Services/runlevels that must start before this
#   $network = networking up
#   $syslog = system logging
#   $local_fs = local filesystems mounted
#   $remote_fs = remote filesystems mounted
#   $time = system clock set correctly

# Required-Stop:     $network $syslog
#   Services/runlevels needed for stopping

# Should-Start:      $named
#   Soft dependencies (optional)

# Should-Stop:       $named

# Default-Start:     2 3 4 5
#   Runlevels where this service auto-starts

# Default-Stop:      0 1 6
#   Runlevels where this service auto-stops

# Short-Description: Brief one-line description
# Description:       Longer description (can be multi-line)
#                    with more details about the service
### END INIT INFO
```

#### Function Library Sourcing

```bash
# LSB functions (more portable, Debian-based)
. /lib/lsb/init-functions

# Red Hat/CentOS functions
. /etc/rc.d/init.d/functions

# Available functions after sourcing:
# - log_success_msg "Message"
# - log_failure_msg "Message"
# - log_warning_msg "Message"
# - log_end_msg 0  (0=success, 1=failure)
```

#### Configuration Files

```bash
# Source optional configuration
[ -f "/etc/default/$NAME" ] && . "/etc/default/$NAME"
[ -f "/etc/sysconfig/$NAME" ] && . "/etc/sysconfig/$NAME"
```

This allows customization without editing the script:

**Example `/etc/default/myservice`:**
```bash
# Options passed to daemon
DAEMON_OPTS="--config /etc/myservice/config.yaml --debug"

# User to run as
SERVICE_USER="myservice"
SERVICE_GROUP="myservice"

# Nice value (priority)
NICE=-5

# Resource limits
ULIMIT_OPEN_FILES=65536
```

---

## 3. SysV Runlevels

### Runlevel Definitions

```
Runlevel 0:  Shutdown/Halt
  - All services stopped
  - System powered down

Runlevel 1:  Single-User Mode
  - Minimal services
  - No networking
  - Root access for maintenance
  - No user logins

Runlevel 2:  Multi-User Mode (without NFS)
  - All networking except NFS
  - Debian default for server

Runlevel 3:  Multi-User Mode (with NFS)
  - Full networking
  - Text interface
  - RedHat/CentOS server default

Runlevel 4:  User-Defined
  - Not used by default
  - Can customize per system

Runlevel 5:  Graphical Multi-User
  - X11/GUI enabled
  - Full multi-user networking
  - Desktop default

Runlevel 6:  Reboot
  - Shutdown and reboot sequence
```

### Checking Current Runlevel

```bash
# Check current runlevel
runlevel           # Output: "N 5" (previous N, current 5)

# Or with systemd
systemctl get-default
# Output: graphical.target (equivalent to runlevel 5)
```

### Mapping Systemd Targets to Runlevels

| Runlevel | Systemd Target | Use Case |
|----------|---|---------|
| 0 | poweroff.target | System halt |
| 1 | rescue.target | Single-user maintenance |
| 2 | multi-user.target | Multi-user (Debian) |
| 3 | multi-user.target | Multi-user text mode |
| 4 | (user-defined) | Custom |
| 5 | graphical.target | Graphical desktop |
| 6 | reboot.target | System reboot |

---

## 4. Creating & Managing Init Scripts

### Complete Example: Security Scanner Service

```bash
#!/bin/bash

### BEGIN INIT INFO
# Provides:          security-scanner
# Required-Start:    $network $syslog $remote_fs
# Required-Stop:     $network $syslog $remote_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Network Security Scanner Service
# Description:       Performs continuous network security scanning
#                    and reports vulnerabilities
### END INIT INFO

. /lib/lsb/init-functions

# Script configuration
NAME="security-scanner"
DAEMON="/usr/local/bin/security-scanner"
DAEMON_ARGS="--config /etc/security-scanner/config.yaml"
PIDFILE="/var/run/$NAME.pid"
SCRIPTNAME="/etc/init.d/$NAME"
USER="scanner"
GROUP="scanner"
LOGDIR="/var/log/security-scanner"
LOGFILE="$LOGDIR/$NAME.log"

# Sanity checks
[ -x "$DAEMON" ] || { echo "Daemon not executable: $DAEMON"; exit 1; }
[ -d "$LOGDIR" ] || mkdir -p "$LOGDIR"
[ -f "/etc/default/$NAME" ] && . "/etc/default/$NAME"

# LSB log functions
log_start() {
    log_daemon_msg "Starting $NAME" "$NAME"
}

log_stop() {
    log_daemon_msg "Stopping $NAME" "$NAME"
}

start_service() {
    log_start
    
    # Pre-start validation
    if [ ! -f /etc/security-scanner/config.yaml ]; then
        log_warning_msg "Config file not found"
        return 2
    fi
    
    # Start daemon
    start-stop-daemon --start \
        --quiet \
        --pidfile "$PIDFILE" \
        --chuid "$USER:$GROUP" \
        --exec "$DAEMON" \
        -- $DAEMON_ARGS >> "$LOGFILE" 2>&1
    
    RETVAL=$?
    
    if [ $RETVAL -eq 0 ]; then
        # Get actual PID
        PID=$(pgrep -f "$DAEMON")
        [ -n "$PID" ] && echo $PID > "$PIDFILE"
        log_end_msg 0
    else
        log_end_msg 1
    fi
    
    return $RETVAL
}

stop_service() {
    log_stop
    
    start-stop-daemon --stop \
        --quiet \
        --pidfile "$PIDFILE" \
        --retry=TERM/30/KILL/5 \
        --exec "$DAEMON"
    
    RETVAL=$?
    
    if [ $RETVAL -eq 0 ]; then
        rm -f "$PIDFILE"
        log_end_msg 0
    else
        log_end_msg 1
    fi
    
    return $RETVAL
}

restart_service() {
    stop_service
    sleep 2
    start_service
}

status_service() {
    status_of_proc -p "$PIDFILE" "$DAEMON" "$NAME"
}

case "$1" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart|force-reload)
        restart_service
        ;;
    status)
        status_service
        ;;
    *)
        echo "Usage: $SCRIPTNAME {start|stop|restart|force-reload|status}"
        exit 1
        ;;
esac

exit $?
```

### Installation

```bash
# 1. Create script
sudo nano /etc/init.d/security-scanner
sudo chmod +x /etc/init.d/security-scanner

# 2. Verify LSB header
sudo lsb_release -a
sudo /lib/lsb/init-functions  # Load functions to test

# 3. Enable for runlevels 2-5
sudo update-rc.d security-scanner defaults
# Equivalent to:
# sudo ln -s /etc/init.d/security-scanner /etc/rc2.d/S20security-scanner
# sudo ln -s /etc/init.d/security-scanner /etc/rc3.d/S20security-scanner
# ... and stop links in rc0.d and rc6.d

# 4. Start service
sudo service security-scanner start

# 5. Verify
sudo service security-scanner status
```

---

## 5. Start-Stop-Daemon Utility

`start-stop-daemon` is the standard tool for managing daemon processes in init scripts.

### Syntax

```bash
start-stop-daemon --start [OPTIONS]
start-stop-daemon --stop [OPTIONS]
start-stop-daemon --status [OPTIONS]
```

### Starting a Daemon

```bash
start-stop-daemon --start \
    --quiet \
    --pidfile /var/run/myservice.pid \
    --user myservice \
    --group myservice \
    --chdir /var/lib/myservice \
    --exec /usr/bin/myservice \
    -- --arg1 value1 --arg2 value2
```

**Options:**
- `--start`: Start the process
- `--quiet`: Suppress output
- `--pidfile /path/to/file`: Track PID (required for --stop)
- `--user username`: Run as user
- `--group groupname`: Run as group
- `--chdir /path`: Change working directory
- `--exec /path/to/binary`: Executable to run
- `--background`: Fork to background
- `--make-pidfile`: Create pidfile (for daemons that don't)
- `--umask 0077`: Set file creation mask
- `--env VAR=value`: Pass environment variables
- `--`: End of options, start of program args

### Stopping a Daemon

```bash
start-stop-daemon --stop \
    --quiet \
    --pidfile /var/run/myservice.pid \
    --retry=TERM/30/KILL/5 \
    --exec /usr/bin/myservice
```

**Retry Logic:**
- `--retry=TERM/30/KILL/5`: Send SIGTERM, wait 30s, send SIGKILL, wait 5s
- `--retry=5`: Just wait 5 seconds for process to exit
- `--oknodo`: Don't fail if already stopped

### Checking Status

```bash
start-stop-daemon --status \
    --pidfile /var/run/myservice.pid \
    --exec /usr/bin/myservice

# Exit codes:
# 0 = running
# 1 = not running but pidfile exists
# 3 = not running
# 4 = cannot determine status
```

---

## 6. Service Management Commands

### Legacy service Command

```bash
# (wrapper around init scripts)
sudo service myservice start
sudo service myservice stop
sudo service myservice restart
sudo service myservice status
sudo service myservice reload
```

### Update-rc.d (Debian/Ubuntu)

Install/remove init script from runlevels:

```bash
# Enable for default runlevels (2-5)
sudo update-rc.d myservice defaults

# Enable for specific runlevels
sudo update-rc.d myservice defaults 20 80
# S20 in rc2-rc5, K80 in rc0,rc1,rc6

# Disable (remove symlinks)
sudo update-rc.d -f myservice remove

# Disable but keep symlink
sudo update-rc.d myservice disable

# Re-enable
sudo update-rc.d myservice enable
```

### Chkconfig (RedHat/CentOS)

```bash
# Enable for default levels
sudo chkconfig myservice on

# Enable for specific levels
sudo chkconfig --level 345 myservice on

# Disable
sudo chkconfig myservice off

# Check status
sudo chkconfig --list myservice
```

---

## 7. OpenRC Alternative

OpenRC is a lighter-weight alternative to systemd, used in Alpine Linux, Artix Linux, and others.

### OpenRC Service Script Structure

**Location:** `/etc/init.d/myservice`

```bash
#!/sbin/openrc-run

# OpenRC service description
description="My Custom Service"
command="/usr/local/bin/myservice"
command_args="--config /etc/myservice.conf"
pidfile="/run/$RC_SVCNAME.pid"
command_user="myservice:myservice"

# Pre-start function
depend() {
    need localmount
    need bootmisc
    after net
    keyword -vserver -lxc -openvz -prefix -uml
}

# Called when service starts
start_pre() {
    [ -d "/var/log/myservice" ] || mkdir -p "/var/log/myservice"
    [ -d "/var/lib/myservice" ] || mkdir -p "/var/lib/myservice"
    chown -R myservice:myservice "/var/log/myservice" "/var/lib/myservice"
}

# Custom stop behavior
stop() {
    ebegin "Stopping ${RC_SVCNAME}"
    start-stop-daemon --stop --pidfile "${pidfile}" --exec "${command}"
    eend $?
}

# Status check
status() {
    if service_started; then
        einfo "Status of ${RC_SVCNAME}: started"
    else
        einfo "Status of ${RC_SVCNAME}: stopped"
    fi
}
```

### OpenRC Service Management

```bash
# Start/stop/restart
sudo rc-service myservice start
sudo rc-service myservice stop
sudo rc-service myservice restart

# Enable/disable (auto-start)
sudo rc-update add myservice default
sudo rc-update del myservice default

# Check status
sudo rc-status

# Manual service loading
sudo source /etc/init.d/myservice
sudo start
sudo stop
```

### OpenRC Runlevels

```bash
# List available runlevels
ls /etc/runlevels/

# Check current
rc-status

# Switch runlevel
sudo rc default
sudo rc single
sudo rc shutdown
```

---

## 8. Comparison: SysV vs. Systemd vs. OpenRC

| Feature | SysV Init | Systemd | OpenRC |
|---------|-----------|---------|--------|
| **Startup Type** | Sequential | Parallel | Sequential/Parallel (configurable) |
| **Configuration** | Shell scripts | INI-style files | Shell scripts |
| **Dependency Resolution** | Manual (symlinks) | Automatic | Manual annotations |
| **Restart Handling** | Manual | Automatic | Manual/Plugin-based |
| **Resource Limits** | cgroups v1 | cgroups v2 | cgroups |
| **Logging** | Separate (rsyslog) | journald | Separate (rsyslog) |
| **Socket Activation** | No | Yes | No |
| **User Services** | No | Yes | Yes (runit) |
| **Init System Size** | ~50KB | ~10MB+ | ~300KB |
| **Init Complexity** | Medium | High | Low |
| **Debuggability** | High (bash) | Medium | High (bash) |
| **Portability** | POSIX shell | Linux-only | Portable |
| **Learning Curve** | Easy | Moderate | Easy |

### Migration Decision Tree

```
Using modern Linux (Ubuntu 18+, Debian 10+, CentOS 7+)?
    ├─ YES → Use systemd
    │         (Most packages support it)
    │
    ├─ Need very low footprint (IoT, embedded)?
    │    ├─ YES → Use OpenRC or runit
    │    └─ NO → Continue below
    │
    └─ Need POSIX portability (BSD, minimal Linux)?
         └─ YES → Use OpenRC or custom SysV
```

---

## Quick Reference

### Creating a Service

**Systemd:** 
```bash
sudo systemctl edit --force myservice.service
sudo systemctl daemon-reload
sudo systemctl start myservice.service
```

**SysV:**
```bash
sudo nano /etc/init.d/myservice
sudo chmod +x /etc/init.d/myservice
sudo update-rc.d myservice defaults
sudo service myservice start
```

**OpenRC:**
```bash
sudo nano /etc/init.d/myservice
sudo chmod +x /etc/init.d/myservice
sudo rc-update add myservice default
sudo rc-service myservice start
```

### Process Management Commands

```bash
# Check running processes
ps aux | grep myservice
pgrep -a myservice
systemctl status myservice

# View logs
# Systemd:
journalctl -u myservice.service -f

# SysV/OpenRC:
tail -f /var/log/myservice.log

# Kill process
kill -9 $(pgrep myservice)

# Resource usage
top -p $(pgrep myservice)
```

This completes SysV and init system alternatives. Part 4 will cover custom daemon development in C and Python.
