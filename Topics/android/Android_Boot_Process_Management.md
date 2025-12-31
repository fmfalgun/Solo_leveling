# Android: Complete Boot Process & Process Management
## From Bootloader to App Execution with Detailed Technical Analysis

---

## Table of Contents
1. Android Boot Sequence (Detailed)
2. Init System (init.rc and init daemon)
3. Zygote Process Creation Model
4. Process Management in Android
5. Memory Management & Low Memory Killer
6. Binder & Inter-Process Communication
7. SELinux Enforcement in Process Context
8. App Lifecycle Management
9. System Server & Core Services
10. Debugging Process Issues

---

## 1. Android Boot Sequence (Detailed)

### Phase 1: Bootloader

```
Power-on
    ↓
CPU starts executing from ROM
    ├─ ROM contains bootloader code
    └─ First code to execute
    
Bootloader Responsibilities:
    ├─ Initialize CPU, memory controller
    ├─ Load first-stage bootloader from ROM
    ├─ Load second-stage bootloader from flash
    ├─ Display splash screen
    ├─ Initialize display
    └─ Load kernel into RAM
    
Verify Boot:
    ├─ Second-stage bootloader verifies boot.img signature
    ├─ Uses public key stored in bootloader
    ├─ If signature invalid: HALT (refuse to boot)
    ├─ Display warning if bootloader unlocked
    └─ Continue to kernel if valid

Kernel Loading:
    ├─ Load /boot/boot.img:
    │  ├─ Kernel image (vmlinuz-*)
    │  ├─ Ramdisk (initramfs.img)
    │  └─ Kernel command-line parameters
    ├─ Decompress kernel
    ├─ Set CPU to kernel entry point
    └─ Jump to kernel

Total Time: ~500ms - 2 seconds
```

### Phase 2: Kernel Initialization

```
Kernel Starts (0xC0000000 or higher memory address)
    ↓
Early Kernel Initialization:
    ├─ Initialize CPU MMU (memory management unit)
    ├─ Initialize GIC (interrupt controller)
    ├─ Set up paging
    ├─ Initialize UART (serial console)
    └─ Early printk messages visible
    
Memory Setup:
    ├─ Parse kernel command-line parameters
    ├─ Initialize memory zones (DMA, Normal, HighMem)
    ├─ Set up page allocator
    ├─ Initialize slab allocator
    └─ Device tree parsing (describes hardware)
    
Subsystem Initialization:
    ├─ Initialize scheduling system
    ├─ Initialize timer subsystem
    ├─ Initialize interrupt handling
    ├─ Initialize process management
    ├─ Initialize virtual memory system
    └─ Initialize filesystem cache
    
Device Initialization:
    ├─ Initialize platform-specific code
    ├─ Initialize clock framework
    ├─ Initialize power management
    ├─ Initialize regulators (voltage supplies)
    └─ Device drivers initialization starts
    
Filesystem Mounting:
    ├─ Mount rootfs (ramdisk)
    ├─ Ramdisk contains /system, /data filesystems (initially)
    ├─ Later these will be mounted from flash partitions
    └─ Create basic device nodes (/dev/null, /dev/zero, etc.)

Init Process Creation:
    ├─ Kernel reaches end of initialization
    ├─ Kernel looks for init process to exec
    ├─ Tries: /sbin/init, /etc/init, /bin/init
    ├─ On Android: finds /init (in ramdisk)
    ├─ Kernel calls: execve("/init", null, null)
    └─ Control passes to init process
    
Total Time: ~1-3 seconds
```

### Phase 3: Init Process (First Stage)

```
Init Process Starts (First Stage - executes from ramdisk)
    ├─ PID 1 (always PID 1)
    ├─ Runs as root (UID 0)
    └─ No parent (parent is kernel)

First-Stage Init Responsibilities:
    ├─ Load kernel modules from /lib/modules/*
    ├─ Set up dynamic partition (super partition)
    ├─ Mount /system, /vendor, /product partitions
    ├─ Perform filesystem checks (fsck)
    ├─ Mount /data partition
    ├─ Load SELinux policy from /system
    ├─ Transition to SELinux enforcing mode
    │  ├─ Before: Permissive (logs denials, allows)
    │  └─ After: Enforcing (denies, returns -EACCES)
    │
    ├─ Execute second-stage init (/system/bin/init)
    └─ Exit (becomes zombie, reaped by kernel)

First-Stage Init Code Location:
    └─ /init (binary, linked into ramdisk)
    
Handoff:
    ├─ First-stage init becomes zombie
    ├─ Second-stage init is the new PID 1
    └─ Control now in /system/bin/init
    
Total Time: ~500ms - 2 seconds
```

### Phase 4: Init Process (Second Stage)

```
Second-Stage Init (Becomes PID 1)
    ├─ Adopted by kernel
    ├─ Runs from /system/bin/init
    ├─ Has full /system, /vendor, /data mounted
    ├─ SELinux enforcing mode active
    └─ Now performs main initialization

Second-Stage Init Responsibilities:
    
    1. Parse Init Scripts:
       ├─ Read /system/etc/init.rc
       ├─ Read /system/etc/init/*.rc
       ├─ Read /vendor/etc/init/*.rc
       ├─ Read /odm/etc/init/*.rc
       └─ Read /product/etc/init/*.rc
    
    2. Parse Device Tree Overlays:
       └─ System-on-Chip specific configuration
    
    3. Initialize System Properties:
       ├─ ro.secure (security level)
       ├─ ro.debuggable (debugging enabled?)
       ├─ ro.boot.* (bootloader parameters)
       └─ ro.hardware (device hardware)
    
    4. Set Up SELinux Contexts:
       ├─ Set process context for init (init domain)
       ├─ Set file contexts (/system/lib -> system_lib_file)
       ├─ Load compiled SELinux policy
       └─ Now enforcing MAC
    
    5. Create Essential Directories:
       ├─ /dev/socket/ (for Binder)
       ├─ /dev/memcg_event_control (memory cgroup)
       ├─ /sys/kernel/debug (debugfs)
       └─ /dev/pts (pseudo-terminals)
    
    6. Start Essential Services:
       ├─ ServiceManager (Binder service registry)
       │  ├─ Listens on /dev/binder
       │  ├─ Maintains service registry
       │  ├─ Mediates service requests
       │  └─ PID varies per Android version
       │
       ├─ Zygote (Java VM spawner)
       │  ├─ Loads Dalvik/ART VM
       │  ├─ Pre-loads Android framework classes
       │  ├─ Pre-loads system resources
       │  ├─ Listens for fork requests
       │  ├─ PID determined by Zygote start
       │  └─ Details below
       │
       ├─ system_server (Core system services)
       │  ├─ Forked by Zygote
       │  ├─ Contains ActivityManager, PackageManager, etc.
       │  └─ Manages all Android services
       │
       └─ adbd (ADB daemon - if debuggable)
          ├─ Listens on port 5037
          ├─ Allows remote shell access
       └─ Only if ro.debuggable=1
    
    7. Trigger Boot Events:
       ├─ on early-init (early setup)
       ├─ on init (main initialization)
       ├─ on boot (when devices initialized)
       ├─ on property:sys.boot_completed=1 (boot complete)
       └─ Signal to launcher to start
    
    8. Main Loop:
       ├─ Read property changes
       ├─ Check for crashed processes
       ├─ Restart crashed services
       ├─ Handle signals
       └─ Sleep waiting for events

Total Time: ~5-15 seconds
```

---

## 2. Init System: init.rc Script Format

### Basic Structure

```rc
# /system/etc/init.rc

# Import other init files
import /init.${ro.zygote}.rc
import /system/etc/init/hw/init.${ro.hardware}.rc

# Global variables
on early-init
    # Very early initialization
    setprop path.audio_socket /dev/socket/audio_socket
    start ueventd

on init
    # Initialization after early-init
    mkdir /dev/socket 0755 root root
    mkdir /dev/memcg_event_control 0755 root system
    
on boot
    # After all devices initialized
    class_start core
    class_start main

# Service definition
service servicemanager /system/bin/servicemanager
    class core
    user system
    group system
    critical
    setenv CLASSPATH ${BOOTCLASSPATH}
    socket binder stream 0666 root system

service zygote /system/bin/app_process64 \
    -Xzygote /system/bin --zygote --start-system-server
    class main
    priority -20
    user system
    group system readproc reserved_disk

# Trigger on condition
on property:sys.boot_completed=1
    class_start late_start

# Action on event
on property:ro.secure=0
    setprop ro.adb.secure 0
```

### Service Definitions

```rc
service <name> <executable> [<argument>]*
    class <name>              # Service class (core, main, late_start)
    user <username>           # UID to run as
    group <groupname> *       # GID and supplementary groups
    priority <priority>       # Nice value (-20 to 19)
    disabled                  # Don't auto-start
    oneshot                   # Don't restart if exits
    critical                  # Restart if crashes
    socket <name> <type> <perm> <user> <group>  # Create socket
    on property:<name>=<value> # Start on property change
    setenv <key> <value>      # Environment variables
```

### Events and Triggers

```rc
on <trigger>
    <command>
    <command>

Triggers:
├─ early-init           (very early)
├─ init                 (normal init)
├─ boot                 (devices ready)
├─ property:name=value  (property changed)
└─ service:<name>       (service event)
```

---

## 3. Zygote Process Creation Model

### Zygote Overview

```
Zygote = Java process spawner

Design:
    ├─ Single JVM instance
    ├─ Pre-loads common Java classes
    ├─ Pre-loads system resources (strings, colors, themes)
    ├─ Child processes inherit pre-loaded state
    ├─ App launch = fork() + minimal setup
    └─ Results in very fast app startup (~100-200ms)

Alternative (if no Zygote):
    ├─ Each app starts fresh
    ├─ Load JVM (slow, ~1-2 seconds)
    ├─ Parse DEX files (slow)
    ├─ Optimize JIT compilation
    └─ Total startup: ~5-10 seconds per app
```

### Zygote Startup

```
init reads /system/etc/init/hw/init.zygote.rc:

service zygote /system/bin/app_process64 \
    -Xzygote /system/bin --zygote --start-system-server
    class main
    socket zygote stream 660 root system
    onrestart write /sys/android_power/request_state wake
    priority -20
    user system
    group system readproc reserved_disk

Zygote Process Initialization:
    ├─ Executed by init as root (UID 0)
    ├─ /system/bin/app_process64 loaded
    ├─ Zygote runtime initialization:
    │  ├─ Load Dalvik/ART VM
    │  ├─ Initialize VM with startup flags
    │  ├─ Call ZygoteInit.main()
    │  └─ Enter pre-load phase
    │
    ├─ Pre-load Phase (in init_process_for_app):
    │  ├─ Load framework classes:
    │  │  ├─ android.app.Activity
    │  │  ├─ android.app.Service
    │  │  ├─ android.content.Context
    │  │  ├─ android.graphics.drawable.*
    │  │  └─ ... (~10,000 more classes)
    │  │
    │  ├─ Load system resources:
    │  │  ├─ Strings, colors, layouts
    │  │  ├─ Themes, drawables
    │  │  ├─ Animations
    │  │  └─ Dimensions, styles
    │  │
    │  ├─ JIT compilation for loaded classes
    │  └─ Result: ~100-200MB heap filled with pre-loaded state
    │
    ├─ Socket Binding:
    │  ├─ Create /dev/socket/zygote socket
    │  ├─ Listen for fork requests
    │  ├─ Permissions: 660 (user system, group system)
    │  └─ Only system_server can connect
    │
    ├─ Start System Server:
    │  ├─ Fork child process
    │  ├─ Child executes: SystemServer.main()
    │  ├─ System server has PID > 1 (not 1)
    │  └─ Loads core system services
    │
    └─ Enter Main Loop:
       ├─ Loop forever
       ├─ Accept fork requests
       ├─ For each request:
       │  ├─ fork() creates child
       │  ├─ Child inherits JVM state
       │  ├─ Child loads app code
       │  └─ Child runs app
       └─ Parent ready for next request

Pre-loaded classes benefit:
    ├─ Shared between all apps
    ├─ Already parsed (faster)
    ├─ Already JIT-compiled
    ├─ Already in memory
    └─ Result: App startup 10x faster

Drawback:
    └─ Shared classes can't be updated without full reboot
```

### Process Creation Request

```
App Launch Sequence:
───────────────────

1. User taps app icon
2. Launcher Activity calls startActivity()
3. Launcher calls ActivityManagerService via Binder

ActivityManager.startActivity():
    ├─ Checks if app process exists
    ├─ If exists: createBaseProcessLocked() not called
    ├─ If not exists:
    │  ├─ calculateProcessRecordName() - get app's UID
    │  ├─ startProcessLocked()
    │  └─ requestZygoteFork()
    │
    └─ Zygote Fork Request:
       ├─ CONNECT to /dev/socket/zygote
       ├─ WRITE fork request with:
       │  ├─ uid (10001 for first installed app)
       │  ├─ gid (10001)
       │  ├─ gids (supplementary groups)
       │  ├─ rlimits (resource limits)
       │  ├─ capabilities (Linux capabilities)
       │  ├─ selinux_name (SELinux domain: untrusted_app)
       │  ├─ nice (priority)
       │  ├─ is_system_app (false for third-party)
       │  ├─ is_child_zygote (false for normal apps)
       │  └─ app_data_dir (/data/user/0/com.example.app)
       │
       └─ WAIT for PID response

Zygote Fork:
    ├─ Zygote process receives fork request
    ├─ Calls fork()
    ├─ Parent (Zygote):
    │  ├─ Receives child PID from kernel
    │  └─ Sends PID back to ActivityManager
    │
    └─ Child Process:
       ├─ Has exact copy of Zygote's memory
       ├─ Includes pre-loaded classes, resources
       ├─ setuid(10001) - change to app UID
       ├─ setgid(10001) - change to app GID
       ├─ setgroups() - add supplementary groups
       ├─ setrlimit() - set resource limits
       ├─ Set SELinux context: untrusted_app domain
       ├─ Initialize app-specific data
       ├─ Load app's classes and code
       ├─ Call ActivityThread.main()
       └─ App is now running

Result:
    ├─ App process created with correct UID
    ├─ App running in isolated sandbox
    ├─ Shared memory optimized (fork inherits)
    └─ App startup time: ~100-200ms
```

---

## 4. Process Management in Android

### Process Hierarchy

```
Kernel Init
    ↓
init process (PID 1, UID 0, Domain: init)
    ├─ ServiceManager (PID ~150, UID 1000, Domain: servicemanager)
    │  └─ Service registry mediator
    │
    ├─ Zygote (PID ~500, UID 0 initially, Domain: zygote)
    │  ├─ system_server (PID ~501, UID 1000, Domain: system_server)
    │  │  ├─ ActivityManager
    │  │  ├─ PackageManager
    │  │  ├─ WindowManager
    │  │  ├─ PowerManager
    │  │  └─ ... (more services)
    │  │
    │  ├─ App Process 1 (PID ~2000, UID 10001, Domain: untrusted_app)
    │  │  └─ App: com.example.app
    │  │
    │  ├─ App Process 2 (PID ~2001, UID 10002, Domain: untrusted_app)
    │  │  └─ App: com.other.app
    │  │
    │  └─ App Process N (PID ~2000+N, UID 10000+N)
    │     └─ App: com.another.app
    │
    └─ Other Essential Services
       ├─ adbd (UID 1000, shell)
       ├─ vold (Volume daemon)
       ├─ logd (Logging daemon)
       └─ surfaceflinger (Display compositor)
```

### Process States

Android assigns processes one of five importance levels:

```
Foreground (Highest Priority)
    ├─ The app user is directly interacting with
    ├─ App is focused (has input focus)
    ├─ Services called from foreground app
    ├─ Broadcast receivers called from foreground app
    │
    └─ LMK won't kill unless critical memory shortage

Visible (High Priority)
    ├─ App partially visible but not focused
    ├─ Example: Activity behind a dialog/translucent Activity
    ├─ Services called from visible app
    │
    └─ LMK kills if very low memory

Service (Medium Priority)
    ├─ App has a service running (started via startService())
    ├─ Not visible to user
    ├─ Examples: music player, GPS tracking
    │
    └─ LMK kills if low memory

Background (Low Priority)
    ├─ App is not visible
    ├─ onPause() called, activity stopped
    ├─ Service no longer running
    │
    └─ LMK kills first to free memory

Empty (Lowest Priority)
    ├─ No code running
    ├─ Process kept for quick restart
    ├─ Can be killed immediately
    │
    └─ LMK kills immediately if needed
```

### Memory Management: Low Memory Killer (LMK)

```
Memory Pressure Detection:
    ├─ Monitor /proc/meminfo
    ├─ Check available memory
    ├─ If below threshold: trigger LMK

LMK Thresholds:
    ├─ Device with 2GB RAM:
    │  ├─ Empty: 46 MB
    │  ├─ Background: 67 MB
    │  ├─ Service: 88 MB
    │  ├─ Visible: 120 MB
    │  └─ Foreground: 155 MB
    │
    ├─ Device with 4GB RAM:
    │  ├─ Empty: 64 MB
    │  ├─ Background: 102 MB
    │  ├─ Service: 127 MB
    │  ├─ Visible: 191 MB
    │  └─ Foreground: 216 MB
    │
    └─ Configurable in /system/etc/init.rc or kernel params

Kill Process Selection:
    ├─ Sort processes by importance level
    ├─ Within same level: kill oldest first
    ├─ Send SIGKILL to lowest-importance process
    ├─ Repeat until memory freed
    │
    └─ Never kill:
       ├─ Foreground process (user will notice)
       ├─ System processes (system crash)
       └─ Kernel processes

Example Memory Crisis:
    ├─ Available memory drops below 64 MB
    ├─ User is playing game (foreground - safe)
    ├─ Chrome browser open in background (safe)
    ├─ Music player (service - safe)
    ├─ Email app (background - kill)
    ├─ Messenger app (background - kill)
    ├─ Email synced (empty - kill first)
    └─ Repeat until 100+ MB free
```

---

## 5. Binder & Inter-Process Communication

### Binder Architecture

```
Traditional Unix IPC:
├─ Pipes (one-way, same host)
├─ Sockets (bidirectional)
├─ Shared memory
└─ Signals (notifications)

Android Binder:
├─ Custom RPC framework
├─ Kernel driver (/dev/binder)
├─ Lightweight, efficient
├─ Built for mobile
└─ Handles privilege elevation
```

### Binder Communication Flow

```
Client Process (App A)                  Binder Kernel Driver              Service (system_server)
├─ Wants to call service               ├─ Validates permission             ├─ Implements IService
├─ Obtains service reference           ├─ Transfers data                   ├─ Executes request
├─   via ServiceManager                └─ Marshals result back              └─ Returns response
│
│ 1. Get Service Reference:
│    ├─ ServiceManager.getService("com.android.settings")
│    └─ Binder RPC to ServiceManager
│
│ 2. ServiceManager Returns:
│    ├─ IBinder interface to service
│    └─ Communications handle in app
│
│ 3. Call Service Method:
│    ├─ Prepare Parcel (serialized data)
│    ├─ Call transact(code, data, reply)
│    └─ Binder driver intercepts
│
├─ Binder Driver:
│   ├─ Receives call from client
│   ├─ Check capabilities/permissions
│   ├─ Query service by handle
│   ├─ Check destination process permission
│   └─ If denied: return EPERM
│
│ 4. Service Receives:
│    ├─ Binder onTransact() called
│    ├─ Parse request code
│    ├─ Unmarshal parameters
│    ├─ Execute method
│    ├─ Marshal result
│    └─ Return to kernel
│
└─ 5. Client Receives:
    ├─ Kernel moves result to client memory
    ├─ reply Parcel populated
    └─ Client reads result
```

### Permission Checking

```
When App A calls Service:

1. Binder checks:
   ├─ Does app have permission in manifest?
   ├─ Is permission granted (runtime on Android 6+)?
   ├─ Is SELinux policy allows communication?
   ├─ Does service want to allow caller?
   └─ If all pass: allow call

2. Service checks:
   ├─ Gets callingUid from Binder
   ├─ Gets callingPid from Binder
   ├─ Knows exact identity of caller
   ├─ Can enforce app-specific rules
   └─ Can deny based on caller

Example: INTERNET Permission
    ├─ App A calls: ConnectivityManager.startUsingNetworkFeature()
    ├─ Manifest declares: <uses-permission android:name="android.permission.INTERNET" />
    ├─ User not granted permission
    │
    ├─ Service checks callingUid
    ├─ Looks up permission: uid 10001, permission INTERNET
    ├─ Permission not found/granted
    ├─ Service denies: throws SecurityException
    └─ App receives exception
```

---

## 6. SELinux Enforcement

### SELinux Domains for Common Processes

```
Process                 Domain                 Can Access
─────────────────────────────────────────────────────────────
init                    kernel                 Everything
zygote                  zygote                 Zygote-specific
system_server           system_server          System files, all services
Normal App (com.*)      untrusted_app          Own files, common system
System App              system_app             Extended system access
Priv App                priv_app               Full system access (with caution)
ServiceManager          servicemanager         Service registry
ADB Shell               shell                  Limited access
adbd                    adbd                   ADB-specific
```

### App Sandbox via SELinux

```
Scenario: App tries to read /data/system/packages.xml

1. File Permissions (DAC):
   ├─ File: packages.xml (UID 1000, perms 640)
   ├─ App: UID 10001
   ├─ DAC: DENIED (not owner, no group membership)
   └─ Result: Permission denied ✗

2. SELinux (MAC):
   ├─ File context: system_data_file
   ├─ App domain: untrusted_app
   ├─ Policy rule: deny untrusted_app system_data_file { read };
   ├─ SELinux: DENIED
   └─ Result: Permission denied ✗

3. Binder (if via service):
   ├─ App calls: PackageManager.getInstalledPackages()
   ├─ PackageManager checks: callingUid 10001
   ├─ Requires: READ_INSTALLED_PACKAGES permission
   ├─ Permission granted? Only if declared + user approved
   ├─ Binder: DENIED if not granted
   └─ Result: Permission denied ✗

Conclusion: Cannot access even if one layer permits (all must permit)
```

---

## 7. System Server & Core Services

### System Server Startup

```
Zygote forks system_server:
    ├─ UID: 1000 (system)
    ├─ Domain: system_server (SELinux)
    ├─ Loads: SystemServer.java
    ├─ Calls: SystemServer.run()
    │
    └─ Core Services Started:
       │
       ├─ Phase 1 - Critical Services:
       │  ├─ ActivityManagerService (controls app lifecycle)
       │  ├─ PackageManagerService (manages packages)
       │  ├─ PowerManagerService (power management)
       │  ├─ LightsService (LED control)
       │  ├─ DisplayManagerService (display management)
       │  ├─ InputManagerService (touch input)
       │  └─ WindowManagerService (window management)
       │
       ├─ Phase 2 - Core Services:
       │  ├─ NotificationManagerService
       │  ├─ AudioService
       │  ├─ CameraService
       │  ├─ LocationManagerService
       │  ├─ SensorService
       │  ├─ TelephogyService
       │  └─ BluetoothManagerService
       │
       ├─ Phase 3 - Other Services:
       │  ├─ DockObserverService
       │  ├─ WiredAccessoryManager
       │  ├─ USBService
       │  ├─ ContentServiceService
       │  ├─ AppOpsService
       │  └─ PermissionControllerService
       │
       └─ Phase 4 - Post-Bootup:
          ├─ All services started
          ├─ Boot complete signal sent
          ├─ Launcher app started
          └─ System ready for user
```

---

## 8. App Lifecycle Management

### ActivityManager Tracking

```
ActivityManager tracks:
├─ Which apps are running
├─ In which process
├─ With which UID
├─ In which state (foreground, background, etc.)
├─ Memory usage of each app
└─ Importance for LMK

When App Launched:
    ├─ ActivityManager.startActivity()
    ├─ Checks if process exists
    ├─ If not: requestZygoteFork()
    ├─ Waits for process created
    ├─ Creates ActivityRecord
    ├─ Moves to RUNNING state
    └─ Calls Activity.onCreate()

When App Goes Background:
    ├─ Activity.onPause() called
    ├─ Activity.onStop() called
    ├─ ActivityManager updates importance
    ├─ Changes from FOREGROUND to BACKGROUND
    ├─ Process still running (ready for quick resume)
    └─ Eligible for LMK kill if memory needed

When App Exits:
    ├─ User swipes app away
    ├─ Or app calls finish()
    ├─ Activity.onDestroy() called
    ├─ If no more activities: process can exit
    ├─ Process death handled by init
    ├─ Child process (forked from Zygote) becomes zombie
    ├─ init reaps (wait()s for) zombie
    └─ Resources freed
```

---

## Summary: Android vs Linux Process Management

| Aspect | Linux | Android |
|--------|-------|---------|
| **Init System** | systemd, SysV | init.rc + init daemon |
| **Service Management** | Unit files | init.rc services |
| **Process Spawning** | Direct fork/exec | Zygote fork |
| **IPC** | Signals, pipes, sockets | Binder RPC |
| **Process Isolation** | UID/GID/DAC | UID/GID/SELinux/Binder |
| **Privilege Elevation** | sudo, setuid, capabilities | Only within Binder framework |
| **Memory Management** | Swapping, OOM Killer | Low Memory Killer |
| **Boot Time** | 10-30 seconds | 5-20 seconds (optimized) |
| **Process States** | Running/sleeping/stopped | Foreground/visible/service/background/empty |
| **Terminal Access** | Shell access universal | No terminal (security) |
| **File Access** | User/group based | UID/SELinux/Binder |

This completes the comprehensive Android boot and process management guide!
