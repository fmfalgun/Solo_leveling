# Init Systems: Complete Technical Guide
## Understanding Linux Init Systems and Their Types

---

## Table of Contents
1. What are Init Systems?
2. Init System Types & Comparison
3. Init System Boot Process
4. Android vs Linux Process Management
5. Android Process Hierarchy Details
6. Binder IPC & SELinux Integration

---

## 1. What are Init Systems?

### Definition

An **init system** is the first process (PID 1) started by the Linux kernel during boot. It is responsible for:

- **System initialization**: Setting up hardware, mounting filesystems
- **Service management**: Starting/stopping/restarting services
- **Process supervision**: Maintaining and monitoring services
- **Dependency management**: Managing service dependencies
- **Logging**: Centralized logging and debugging
- **System shutdown**: Coordinated graceful shutdown

### Core Responsibilities

```
Kernel Boot
    ↓
Init System (PID 1) Takes Over
    ├─ Mount filesystems
    ├─ Configure network
    ├─ Start essential services
    ├─ Manage running services
    ├─ Handle user logins
    ├─ Monitor service health
    └─ Coordinate shutdown
    
Result: Operating System Ready
```

### Why Init System Matters?

The init system is **the most critical process** because:
1. Everything runs as its child or descendant
2. It controls system startup behavior
3. It manages service dependencies
4. It handles process cleanup (reaping zombies)
5. It coordinates graceful shutdown
6. It determines boot speed and parallelization

---

## 2. Init System Types & Comparison

### Major Init Systems

```
Linux Init Systems:
├─ Systemd (modern, 2015+)
├─ SysV Init (traditional, 1980s-2010s)
├─ OpenRC (lightweight alternative)
├─ Runit (minimal, service supervision)
└─ Busybox Init (embedded systems)

Android Init System:
└─ init.rc + init daemon (Android proprietary)
```

---

## **Comprehensive Comparison Table**

### **Systemd vs SysV vs OpenRC**

| Aspect | Systemd | SysV Init | OpenRC | Busybox | Runit |
|--------|---------|-----------|--------|---------|-------|
| **Era** | 2015+ (modern) | 1980s-2010s (legacy) | 2007+ (alternative) | Embedded | Minimal |
| **Architecture** | Monolithic manager | Shell script based | Shell script based | Minimal scripts | Supervision based |
| **Parallelization** | YES - parallel startup | NO - sequential | YES - parallel | Sequential | Parallel supervision |
| **Startup Speed** | Fast (parallel) | Slow (sequential) | Fast (parallel) | Very fast | Fast |
| **Binary Size** | ~10MB+ | ~50KB | ~300KB | ~50KB | ~200KB |
| **Configuration** | INI-style (.service) | Shell scripts | Shell scripts | Shell scripts | Service directories |
| **Dependencies** | YES - automatic | Manual (symlinks) | Manual (annotations) | None | None |
| **Service Restart** | YES - automatic | Manual | Manual | Manual | Automatic supervision |
| **Logging** | journald (integrated) | rsyslog (separate) | rsyslog (separate) | Standard output | Process output |
| **User Services** | YES | NO | YES | NO | YES |
| **Socket Activation** | YES | NO | NO | NO | NO |
| **Timers** | YES (built-in) | cron (separate) | cron (separate) | cron (separate) | cron (separate) |
| **Boot Process** | Dependency graph | /etc/inittab runlevels | /etc/inittab runlevels | Predefined init | Service supervision |
| **Runlevels** | Targets (graphical.target) | 0-6 (shutdown to reboot) | 0-6 (shutdown to reboot) | Predefined | N/A |
| **System Management** | Full system manager | Init only | Init only | Init only | Process supervisor |
| **D-Bus** | YES - integrated | NO | NO | NO | NO |
| **SELinux Support** | YES | NO | NO | Limited | NO |
| **Container Support** | YES | NO | NO | YES | YES |
| **Use Case** | Modern distributions | Legacy systems | Embedded/minimal | Tiny systems | Minimalist |
| **Examples** | Ubuntu 18+, Fedora | RHEL 6, Debian 7 | Alpine Linux, Artix | Busybox systems | Runit systems |
| **Learning Curve** | Moderate-High | Easy | Easy | Very easy | Easy |

---

## 3. Init System Boot Process

### Systemd Boot Flow

```
Kernel Boot
    ↓
Init Systemd (PID 1)
    ├─ Read default target (multi-user.target or graphical.target)
    ├─ Load all unit files
    ├─ Resolve dependencies
    ├─ Start services in parallel
    │   ├─ Service 1 (if dependencies met)
    │   ├─ Service 2 (parallel with Service 1)
    │   └─ Service 3 (wait for dependency)
    ├─ Start getty (login prompt)
    └─ Boot complete
```

### SysV Init Boot Flow

```
Kernel Boot
    ↓
Init Process (SysV) starts
    ├─ Read /etc/inittab
    ├─ Run /etc/rc.d/rc.sysinit (system initialization)
    ├─ Determine runlevel (usually 3 or 5)
    ├─ Execute /etc/rc.d/rcN.d scripts sequentially
    │   ├─ K* scripts stop services (in order)
    │   └─ S* scripts start services (in order)
    ├─ Start getty (login prompt)
    └─ Boot complete (slower than systemd)
```

### OpenRC Boot Flow

```
Kernel Boot
    ↓
Init Process (OpenRC) starts
    ├─ Read /etc/inittab
    ├─ Source openrc scripts
    ├─ Run dependency-based startup
    ├─ Execute rc-service commands for each service
    ├─ Start getty (login prompt)
    └─ Boot complete (faster than SysV, not as parallel as systemd)
```

---

## 4. Android vs Linux Process Management

### Key Differences Overview

```
LINUX                           ANDROID
├─ Init System: Systemd/SysV    ├─ Init System: init.rc + init daemon
├─ Process Model: Traditional   ├─ Process Model: Android-specific
├─ IPC: Signals, pipes, sockets ├─ IPC: Binder (RPC framework)
├─ Privileges: User/root        ├─ Privileges: App UID + SELinux
├─ File Access: Linux DAC       ├─ File Access: SELinux MAC + Binder
├─ Background: Services         ├─ Background: Services + Apps
├─ Memory: Unlimited (or cgroup)├─ Memory: LMK (Low Memory Killer)
└─ Shutdown: Clean termination  └─ Shutdown: App death or system command
```

### Process Hierarchy

**Linux:**
```
Systemd (PID 1)
├─ Service A (PID 100)
├─ Service B (PID 200)
│  └─ Child Process (PID 201)
└─ Service C (PID 300)
    ├─ Child 1 (PID 301)
    └─ Child 2 (PID 302)

Standard parent-child relationships
Process isolation via Linux DAC
```

**Android:**
```
init daemon (PID 1)
├─ zygote (PID 500) - App spawner
│  ├─ App A (PID 5000, UID 10001)
│  ├─ App B (PID 5001, UID 10002)
│  └─ App C (PID 5002, UID 10003)
├─ system_server (PID 501)
│  ├─ ActivityManager
│  ├─ PackageManager
│  └─ PowerManager
└─ ServiceManager (PID 502) - Binder service registry
   ├─ serviceA
   ├─ serviceB
   └─ serviceC

Zygote creates app processes
Each app has unique UID
Binder for inter-process communication
```

---

## 5. Android Process Hierarchy - Detailed

### Android Init System (init.rc)

Android uses **init.rc** script that defines:

```rc
# /system/etc/init.rc (Android)

# Service definition
service zygote /system/bin/app_process64 \
    -Xzygote /system/bin --zygote --start-system-server
    class main
    socket zygote stream 660 root system
    onrestart write /sys/android_power/request_state wake
    priority -20

# Trigger events
on boot
    # Mount filesystems
    mount debugfs /sys/kernel/debug /sys/kernel/debug mode=755
    mkdir /dev/memcg_event_control
    
# Service class
on property:sys.boot_completed=1
    class_start default
```

### Zygote Process Model

```
init daemon (Linux kernel process)
    ↓ (forks)
Zygote Process
    ├─ Pre-loads common Java classes
    ├─ Pre-loads system resources
    ├─ Sets up JVM
    │
    └─ On app launch request (via Binder):
        ├─ fork() creates child process
        ├─ Child inherits JVM, classes, resources
        ├─ Child loads app code
        ├─ Main() called
        └─ App runs (very fast startup)

Result: Apps share common JVM setup, fast launch
```

### Process UID Assignment

```
System Services:
├─ init (UID 0 - root)
├─ zygote (UID 0 - root)
├─ system_server (UID 1000 - system)
└─ ServiceManager (UID 0 - root)

Third-party Apps:
├─ App A (UID 10001 - isolated)
├─ App B (UID 10002 - isolated)
├─ App C (UID 10003 - isolated)
└─ Shared UID apps (UID 10010 - shared, must sign together)

Each app runs in isolated UID
File access restricted by UID + SELinux MAC
```

### Process Memory Management

**Android's Low Memory Killer (LMK):**
```
Available Memory: 2GB
├─ Used by: system_server, apps, caches

When memory < threshold:
    ├─ Kill apps by importance
    ├─ Levels:
    │   ├─ Cached apps (lowest priority)
    │   ├─ Service apps
    │   ├─ Visible apps
    │   ├─ Foreground apps
    │   └─ System apps (never killed)
    └─ Freed memory returned to system
```

### Process States in Android

```
FOREGROUND (Highest priority)
    ├─ App currently visible to user
    ├─ Receives input
    └─ Will keep running even if memory tight

VISIBLE (High priority)
    ├─ Not focused but partially visible
    ├─ Example: Activity behind dialog
    └─ Will keep running if possible

SERVICE (Medium priority)
    ├─ Running a service via startService()
    ├─ Not visible to user
    └─ Killed if memory is very tight

BACKGROUND (Low priority)
    ├─ Not visible, no service
    ├─ Example: onPause called
    └─ Killed first when memory needed

EMPTY (Lowest priority)
    ├─ No code running
    ├─ Kept for quick restart
    └─ Killed if needed
```

---

## 6. Binder IPC & SELinux Integration

### Binder: Android's RPC Framework

Traditional Linux uses:
- Pipes for sequential communication
- Sockets for network-like communication
- Signals for notifications

Android uses **Binder** (a lightweight RPC framework):

```
App A (UID 10001)
    ↓ (Request via Binder)
ServiceManager (Binder Registry, UID 0)
    ├─ Looks up requested service
    └─ Returns service reference
    ↓
Service Provider (UID 1000)
    ├─ Receives request
    ├─ Executes operation
    └─ Returns result
    ↓
App A (UID 10001)
    └─ Receives response

All mediated through Binder kernel driver
```

### SELinux in Android

Android uses **SELinux MAC** (Mandatory Access Control):

```
Traditional Linux DAC:
├─ User ID (UID) - who owns it
├─ Group ID (GID) - what group owns it
└─ Permissions: rwxrwxrwx

Android SELinux:
├─ UID system
├─ Plus SELinux context (domain, type, role)
├─ Example: system_server -> system:system_server_tmpfs_type:rw
└─ Kernel enforces both DAC AND MAC

Result: Fine-grained control even if app gets compromised
```

### App Sandbox via SELinux

```
Normal App (com.example.app, UID 10001)
    ├─ /data/user/0/com.example.app/ (RW)
    ├─ /data/user/0/com.example.app/cache (RW)
    ├─ /system/app (R only)
    ├─ /system/framework (R only)
    ├─ Cannot access /data/user/0/com.other.app/ (SELinux blocks)
    ├─ Cannot access /system/app/other.apk (SELinux blocks)
    └─ Binder calls mediated by ServiceManager

Result: App sandboxed even with root
```

---

## **Quick Comparison: Linux Init Systems**

| Feature | Systemd | SysV | OpenRC | Runit |
|---------|---------|------|--------|-------|
| **Complexity** | High | Low | Low | Minimal |
| **Startup Speed** | Very Fast | Slow | Fast | Fast |
| **Service Restart** | Yes | No | No | Yes |
| **Logging** | Integrated | External | External | External |
| **Good For** | Modern servers/desktop | Legacy | Embedded/minimal | Minimalist |

| Feature | Android init | Linux systemd |
|---------|--------------|---------------|
| **Parent Process** | Kernel (PID 1) | Same |
| **Service Model** | init.rc scripts | Unit files |
| **IPC** | Binder RPC | Signals/sockets |
| **Privilege Model** | UID + SELinux | UID + DAC |
| **Process Spawning** | Direct fork | Direct fork |
| **App Model** | App UID + Zygote | Traditional |

---

## Summary

**Init Systems are critical because they:**
1. Bring the system from kernel to operational
2. Manage service lifecycle
3. Handle dependencies
4. Coordinate shutdown
5. Monitor service health

**Main Types:**
- **Systemd**: Modern, feature-rich, parallelized
- **SysV**: Traditional, simple, sequential
- **OpenRC**: Lightweight alternative
- **Android**: Specialized for mobile with Binder + SELinux

**Android Differences:**
- Uses Binder for inter-process communication instead of traditional IPC
- SELinux MAC for fine-grained privilege control
- Zygote for fast app spawning
- Low Memory Killer for aggressive memory management
- Process states tied to app visibility, not traditional foreground/background

This completes the init systems overview. Next artifacts will cover Android and Linux filesystems in detail!
