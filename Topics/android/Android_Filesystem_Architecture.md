# Android Filesystem Architecture
## Directory Structure, Security Model, and App Sandbox Implementation

---

## Table of Contents
1. Android Filesystem Overview
2. Root Directory Structure & Usage
3. Security Layers: UID, GID, SELinux
4. Android App Sandbox Model
5. Data Partition Details
6. System Security Enforcement
7. Bootloader & Verified Boot
8. How Android Denies Root & Terminal Access

---

## 1. Android Filesystem Overview

### Filesystem Partitions

Android devices have multiple partitions, each serving a specific purpose:

```
┌─────────────────────────────────────────────────────────┐
│                 NAND Flash Storage                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Bootloader  │  Recovery  │  Boot  │  System │  Data  │
│  (read-only) │ (r/w)      │ (r/o)  │ (r/o)  │ (r/w) │
│              │            │        │        │       │
│  Kernel      │ Recovery   │ Kernel │ /sys   │ /data │
│  loader      │ OS         │ +ramdisk   files  │ Apps  │
│              │            │        │        │ Cache │
└─────────────────────────────────────────────────────────┘

Typical Layout:
├─ Bootloader: ~1-4 MB (immutable)
├─ Recovery: ~30-50 MB (system updates)
├─ Boot: ~8-16 MB (kernel + ramdisk)
├─ System: ~500MB-2GB (Android OS + apps)
└─ Data: Rest of storage (user data, app data)
```

### Mount Points at Runtime

```
/                    (root - usually tmpfs/ramdisk)
├─ /system           (System partition - read-only after boot)
├─ /data             (Data partition - read/write)
├─ /vendor           (Vendor-specific files - read-only)
├─ /cache            (Cache partition - read/write)
├─ /dev              (Device nodes - runtime)
├─ /proc             (Process info - runtime)
├─ /sys              (Sysfs - runtime)
├─ /product          (Product-specific - read-only)
├─ /odm              (ODM files - read-only)
└─ /metadata         (Metadata - system use)
```

---

## 2. Root Directory Structure & Usage

### /system - System Partition (Read-Only)

```
/system
├─ /system/app/
│  ├─ SystemUI.apk
│  ├─ Contacts.apk
│  ├─ Dialer.apk
│  └─ ... (pre-installed system apps)
│
├─ /system/priv-app/
│  ├─ Settings.apk (system privilege level)
│  ├─ PermissionController.apk
│  └─ ... (privileged system apps)
│
├─ /system/framework/
│  ├─ android.jar (Android framework classes)
│  ├─ core.jar
│  └─ ... (system libraries)
│
├─ /system/lib64/ and /system/lib/
│  ├─ libc.so (C standard library)
│  ├─ libcrypto.so
│  ├─ libopenssl.so
│  └─ ... (native libraries)
│
├─ /system/bin/
│  ├─ app_process64 (Zygote - app spawner)
│  ├─ system_server
│  ├─ installd
│  └─ ... (system executables)
│
├─ /system/etc/
│  ├─ init.rc (initialization script)
│  ├─ permissions/ (permission definitions)
│  └─ security/ (security policies)
│
├─ /system/xbin/
│  └─ Various diagnostic tools (busybox, etc.)
│
└─ /system/fonts/
   └─ System fonts
```

**Purpose**: Contains Android OS, pre-installed apps, system services, libraries

**Permissions**: Read-only after boot (remounted ro), mounted from read-only partition

**Who Can Access**: System UID (1000+) and apps with system privileges

---

### /data - Data Partition (Read-Write)

```
/data
├─ /data/user/
│  ├─ /data/user/0/        (Primary user)
│  │  ├─ com.example.app/
│  │  │  ├─ files/         (App private files - chmod 700)
│  │  │  ├─ cache/         (App cache - chmod 771)
│  │  │  ├─ lib/           (App native libs)
│  │  │  ├─ databases/     (SQLite databases)
│  │  │  ├─ shared_prefs/  (Preference files)
│  │  │  └─ files-metadata/ (File metadata)
│  │  └─ com.other.app/
│  │     └─ ... (same structure)
│  │
│  ├─ /data/user/10/       (Secondary user - if multi-user enabled)
│  │  └─ ... (isolated user data)
│  │
│  └─ /data/user_de/0/     (Device encrypted data)
│     └─ ... (same structure as user/)
│
├─ /data/app/
│  ├─ com.example.app-<version>.apk  (Downloaded app APK)
│  ├─ com.example.app-<version>/     (App extraction dir)
│  │  ├─ base.apk
│  │  ├─ lib/ (native libraries)
│  │  └─ oat/ (compiled code)
│  └─ ... (other apps)
│
├─ /data/local/
│  ├─ /data/local/tmp/     (World-writable temp - security risk)
│  └─ /data/local/bootchart/
│
├─ /data/misc/
│  ├─ /data/misc/user/     (User-specific misc files)
│  ├─ /data/misc/wifi/     (WiFi data)
│  ├─ /data/misc/bluetooth/ (Bluetooth data)
│  └─ /data/misc/settings/ (System settings)
│
├─ /data/system/
│  ├─ packages.xml        (Installed packages info - critical)
│  ├─ users/              (User account data)
│  ├─ wallpaper/          (Wallpaper)
│  ├─ notification_sounds/ (Notification audio)
│  ├─ appops/             (App permissions)
│  └─ dropbox/            (System logs)
│
├─ /data/cache/
│  ├─ recovery/           (Recovery partition cache)
│  └─ backup/             (Backup data)
│
├─ /data/anr/             (ANR crash logs)
├─ /data/tombstones/      (Crash tombstones)
├─ /data/backup/          (Backup files)
└─ /data/log/             (Various logs)
```

**Purpose**: User data, app data, settings, databases, caches

**Permissions**: Read-write, but protected by UID/GID/SELinux

**Who Can Access**: Each app accesses only its own UID directory + system services

---

### /vendor - Vendor Partition (Read-Only)

```
/vendor
├─ /vendor/bin/           (Vendor-specific executables)
├─ /vendor/lib64/         (Vendor-specific libraries)
├─ /vendor/lib/
├─ /vendor/etc/           (Vendor configuration)
├─ /vendor/app/           (Vendor-specific apps)
└─ /vendor/overlay/       (Vendor resource overlays)
```

**Purpose**: Device-specific (manufacturer) binaries and libraries

**Why Separate**: Allows system updates without rebuilding device-specific code

---

### /cache - Cache Partition (Read-Write, Optional)

```
/cache
├─ /cache/recovery/
├─ /cache/apt/
└─ /cache/... (application cache)
```

**Purpose**: Temporary cache, optional in modern Android

**Note**: Mostly deprecated in favor of /data/cache

---

### /metadata - Metadata Partition

```
/metadata
├─ first_stage_mount (mount configuration)
└─ ... (system-critical metadata)
```

**Purpose**: Critical system metadata, not user-accessible

---

### Special Runtime Directories

```
/dev         (Device nodes - kernel created)
/proc        (Process info - kernel created)
/sys         (Sysfs - kernel created)
/root        (Root user home - not used on Android)
/sdcard      (External storage symlink to /data/media)
/storage     (Storage mount points)
/mnt         (External storage mounting)
```

---

## 3. Security Layers: UID, GID, SELinux, and Binder

### Layer 1: UID/GID Permission Model

```
System UIDs (0-1000):
├─ UID 0 (root) - Reserved, not used after init
├─ UID 1 (init) - Init process
├─ UID 1000 (system) - System UID
├─ UID 1001 (phone) - Phone UID
├─ UID 2000 (shell) - adb shell
└─ UID 2000-9999 (reserved)

Application UIDs (10000+):
├─ UID 10001 (com.example.app) - First installed app
├─ UID 10002 (com.other.app) - Second app
├─ UID 10003 (com.another.app) - Third app
└─ ... (each app gets unique UID from 10000 onwards)

File Access Example:
────────────────────
-rw------- 1 app_10001 app_10001  /data/user/0/com.example.app/cache/file.txt
├─ Owner: UID 10001 (only this app can read/write)
├─ Group: GID 10001 (same app)
└─ Permissions: 600 (rw for owner, nothing for others)

Result: Each app isolated by UID, cannot access other app files
```

### Layer 2: SELinux MAC (Mandatory Access Control)

```
Traditional Linux DAC (Discretionary):
└─ Only checks UID/GID/permissions

Android SELinux MAC:
└─ ADDITIONAL enforcement even if DAC allows

Example: Normal App Context
────────────────────────────
app_10001 process
├─ Domain: untrusted_app
├─ Type: untrusted_app_type
├─ Can read: /system/framework (permitted)
├─ Cannot read: /data/user/0/com.other.app (DENIED by SELinux)
├─ Can use: app_socket (permitted)
└─ Cannot use: system_socket (DENIED by SELinux)

Example: System App Context
────────────────────────────
system_server process
├─ Domain: system_server
├─ Type: system_server_type
├─ Can read: /system (permitted)
├─ Can read: /data/system (permitted)
├─ Can access: all_services (permitted)
└─ Cannot modify: /system files (read-only)

Example: Shell Context (adb shell)
────────────────────────────────
shell process (UID 2000)
├─ Domain: shell
├─ Type: shell_type
├─ Can read: /system (permitted)
├─ Can read: /data (limited, not all)
└─ Restrictions on:
   ├─ Cannot kill system_server
   ├─ Cannot access /data/user/0/* directly
   └─ Cannot use system sockets
```

### Layer 3: Binder Mediation

```
App A (UID 10001) → Wants to call system service
    ├─ Creates Binder transaction
    ├─ ServiceManager validates:
    │  ├─ Is app allowed to call this service? (checked via SELinux)
    │  ├─ What permissions does service require? (checked via manifest)
    │  └─ Is app granted those permissions?
    └─ If denied: Binder returns error
    
    If allowed:
    └─ Service handles request with context of requesting app
       ├─ Knows which app called (callingUid, callingPid)
       ├─ Enforces app's permissions
       └─ Returns result only if allowed

Result: Cannot call system services without proper permissions
```

### Combined Security Example

```
App com.example.app (UID 10001, Domain: untrusted_app)
    ├─ Wants to access /data/user/0/com.other.app/

Layer 1 - DAC Check:
    ├─ File: com.other.app/ (UID 10002)
    ├─ App UID: 10001
    ├─ Permissions: 700 (owner only)
    └─ Result: DENIED by DAC ✗

Layer 2 - SELinux Check:
    ├─ App domain: untrusted_app
    ├─ File context: app_data_file
    ├─ Rule: untrusted_app cannot read app_data_file (unless own)
    └─ Result: DENIED by SELinux ✗

Layer 3 - Binder Check (if using service):
    ├─ Call: SystemService.readOtherAppData()
    ├─ Service checks callingUid (10001)
    ├─ Requires: READ_OTHER_APP_DATA permission
    ├─ Permission granted? NO
    └─ Result: DENIED by Binder ✗

Final Result: ALL THREE LAYERS DENY ACCESS ✓✓✓
```

---

## 4. Android App Sandbox Model

### Process Creation & Isolation

```
User opens app: com.example.app

1. Launcher calls ActivityManager (via Binder)
   └─ "Start com.example.app"

2. ActivityManager checks:
   ├─ Is app installed? ✓
   ├─ Is app signature valid? ✓
   ├─ Is app enabled? ✓
   └─ Can launcher start it? ✓

3. ActivityManager requests Zygote:
   └─ "Fork process for com.example.app"

4. Zygote forks:
   ├─ New process created
   ├─ Inherits JVM, framework classes, common libraries
   ├─ Child: app_process + app code
   └─ Parent: Zygote (ready for next fork)

5. Child process (new app):
   ├─ setuid(10001) - change UID to app's UID
   ├─ setgid(10001)
   ├─ Initialize SELinux domain: untrusted_app
   ├─ Load app code and resources
   └─ Call onCreate()

6. App running:
   ├─ UID 10001 (isolated)
   ├─ Domain: untrusted_app (SELinux)
   ├─ Only /data/user/0/com.example.app/ accessible
   ├─ Cannot access other app data
   └─ Cannot access /system/app
```

### File Access Restrictions

```
App com.example.app (UID 10001)
├─ Can access:
│  ├─ /data/user/0/com.example.app/ (own directory) ✓
│  ├─ /data/user/0/com.example.app/cache/ ✓
│  ├─ /data/user/0/com.example.app/shared_prefs/ ✓
│  ├─ /system/app/ (read-only) ✓
│  ├─ /system/framework/ (read-only) ✓
│  ├─ /sdcard/Android/data/com.example.app/ ✓
│  └─ SharedPreferences with other apps (if signed with same key)
│
└─ Cannot access:
   ├─ /data/user/0/com.other.app/ ✗ (DAC + SELinux)
   ├─ /data/system/ ✗ (SELinux blocks)
   ├─ /system/build.prop ✗ (even if readable, SELinux blocks)
   ├─ /data/ root ✗ (no permission)
   ├─ /proc/<pid> of other apps ✗
   └─ /dev/kmem or /dev/mem ✗ (dangerous devices)
```

### Permission System (Manifest)

```
AndroidManifest.xml:
───────────────────
<manifest>
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.READ_CONTACTS" />
    <uses-permission android:name="android.permission.CAMERA" />
    
    <application>
        <activity android:name=".MainActivity" />
        <service android:name=".MyService" />
    </application>
</manifest>

At Install Time:
    ├─ Permissions checked
    ├─ Assigned to app's uid (10001)
    └─ Stored in /data/system/packages.xml

At Runtime (Android 6.0+):
    ├─ User grants/denies each permission
    ├─ Stored per app
    └─ Kernel enforces via SELinux

Result: Even with UID isolation, permissions further restrict access
```

---

## 5. Why Android Apps Can't Get Root

### Architecture Design

```
Android Security Architecture:
════════════════════════════════

App Process (UID 10001)
    ├─ Cannot call setuid(0) because:
    │  ├─ Process already started with UID 10001
    │  ├─ setuid() requires being root (UID 0)
    │  ├─ Process doesn't have CAP_SETUID capability
    │  └─ Cannot escalate to UID 0 ✗
    │
    ├─ Cannot fork process with UID 0 because:
    │  ├─ fork() preserves parent UID
    │  ├─ Only root can setuid() to 0
    │  └─ Zygote (UID 0 but restricted) won't fork with UID 0 ✗
    │
    ├─ Cannot directly access /dev/kmem because:
    │  ├─ /dev/kmem owned by root (UID 0)
    │  ├─ Permissions: 600 (root only)
    │  ├─ SELinux denies even if permission changed
    │  └─ Cannot escalate privilege ✗
    │
    └─ Cannot use exploits because:
       ├─ SELinux MAC prevents privilege escalation
       ├─ Many kernel interfaces blocked to unprivileged
       ├─ Exploit may crash kernel but won't gain root
       └─ Verified Boot detects modified kernel ✗
```

### No Root Access for Apps

```
Even if app is "rooted":
├─ From user's perspective: Superuser app can grant permissions
├─ But at kernel level:
│  ├─ App still runs as UID 10001
│  ├─ Cannot actually call setuid(0)
│  ├─ Superuser app just grants permissions via SELinux policy
│  └─ Root-level operations still restricted by SELinux ✗

"Root" on Android typically means:
├─ Superuser app installed
├─ SELinux policy modified to allow privileged operations
├─ But process still runs as non-zero UID (usually system:10001)
├─ And system_server still mediates sensitive operations
└─ So truly limited compared to traditional Unix root
```

---

## 6. No Terminal Access for Regular Users

### Why Android Has No Terminal by Default

```
Traditional Linux:
    ├─ Terminal emulator runs (bash, sh)
    ├─ Shell runs as user
    ├─ User can execute commands
    ├─ Commands run with user's UID
    └─ User can explore filesystem

Android Design:
    ├─ App (UID 10001) cannot fork bash/shell
    ├─ Shell would still run as UID 10001 (inherits parent UID)
    ├─ Even if shell is available (/system/bin/sh exists):
    │  ├─ fork() creates UID 10001 shell
    │  ├─ Shell cannot access /data/user/0/<other-app>/
    │  ├─ Shell cannot access /system/app/
    │  ├─ Shell cannot modify /system/
    │  └─ Shell is just another app process
    │
    ├─ ADB Shell (developer mode, UID 2000) has more access:
    │  ├─ But still restricted by SELinux
    │  ├─ Cannot directly modify /system
    │  └─ Cannot access other app data (SELinux blocks)
    │
    └─ Result: No unrestricted terminal ✓ (feature, not bug)
```

### SELinux Prevents Direct File Access

```
Even if you had shell access:
──────────────────────────────

Try: cat /data/system/packages.xml (as shell, UID 2000)
    ├─ DAC Check:
    │  ├─ File owner: UID 1000 (system)
    │  ├─ File perms: 640
    │  ├─ Shell UID: 2000
    │  └─ DAC: DENIED ✗
    │
    └─ Result: No access even if shell available

Try: adb shell su (with no Superuser app)
    ├─ Kernel setuid(0) call
    ├─ Capability check: CAP_SETUID? NO
    ├─ Result: DENIED ✗
    │
Try: adb shell su (with Superuser app installed)
    ├─ Superuser app: "Grant root to shell?"
    ├─ If user grants:
    │  ├─ Superuser modifies SELinux policy
    │  ├─ shell domain gets more permissions
    │  └─ But underlying process still UID 2000
    │
    └─ Result: More operations allowed, but not true UID 0

Final: Cannot escalate UID 2000 → 0 without compromise
```

---

## 7. How Filesystem Protects System

### Read-Only System Partition

```
Boot sequence:
    ├─ Kernel mounts /system as read-write initially
    ├─ init.rc runs (system configuration)
    ├─ System services start
    └─ /system remounted as read-only
        ├─ mount -o ro,remount /system

Verification:
    ├─ After boot, verify /system is read-only:
    │  └─ stat /system → (ro,noatime,nodiratime)
    │
    └─ Try to modify:
       ├─ touch /system/app/NewFile.apk → Permission denied
       ├─ Even as shell (UID 2000) → Denied
       ├─ Even with Superuser → Denied (ro filesystem)
       └─ Only recovery or bootloader can modify

Result: System cannot be modified without recovery mode
```

### Encrypted Data Partition

```
Modern Android uses encryption:

/data partition encryption:
    ├─ Full disk encryption (FDE) or File-based encryption (FBE)
    │
    ├─ FBE:
    │  ├─ Each app's data encrypted separately
    │  ├─ Key derived from user PIN/pattern
    │  ├─ Without PIN: /data/user/0/com.* cannot be accessed
    │  ├─ Only system_server can decrypt (knows PIN)
    │  └─ Result: Other phones cannot access your app data
    │
    └─ Even if phone is stolen:
       ├─ Thief boots into recovery
       ├─ Finds /data partition encrypted
       ├─ Without PIN: Cannot access user data
       └─ Data protected ✓
```

---

## 8. System Enforcement Mechanisms

### Verified Boot (Bootloader)

```
Boot sequence with Verified Boot:
────────────────────────────────

1. Bootloader starts
2. Bootloader verifies boot.img signature
   ├─ Uses public key stored in bootloader
   ├─ If signature invalid: HALT (refuse to boot)
   └─ Signature valid: Continue

3. Kernel verifies system.img
   ├─ Checks root hash at boot
   ├─ If modified: HALT or boot in RED state
   └─ Unmodified: Boot normally

Result:
    ├─ Cannot boot modified kernel
    ├─ Cannot load modified system
    └─ Device boot integrity guaranteed ✓

Exception: Unlocked bootloader
    ├─ Developer mode enables unlocked bootloader
    ├─ Can boot custom kernel/recovery
    └─ But: Bootloader warns, data wiped, device marked as unlocked
```

### SELinux Policy Enforcement

```
System startup with SELinux:
────────────────────────────

init (UID 0, Domain: kernel) loads /system/etc/selinux/

Policy defines:
    ├─ allow system_server system_data_file { read write open };
    │  └─ system_server CAN read/write system_data_file
    │
    ├─ deny untrusted_app app_data_file { write };
    │  (except own app_data_file)
    │  └─ apps CANNOT write other app data
    │
    └─ deny untrusted_app system_socket { connect };
       └─ apps CANNOT connect to system sockets (except allowed)

Enforcement:
    ├─ Every syscall checked against policy
    ├─ If denied: EACCES error
    ├─ Example: open("/data/system/packages.xml", O_WRONLY)
    │  ├─ Caller: untrusted_app domain
    │  ├─ File: system_data_file type
    │  ├─ Operation: write
    │  └─ Policy: DENY → EACCES returned ✓
    │
    └─ No way around: Kernel enforces, not userspace
```

---

## Summary: Android Security Through Filesystem

| Layer | Mechanism | Example | Prevents |
|-------|-----------|---------|----------|
| **UID/GID** | Process UID 10001 | App isolated by UID | Cross-app file access |
| **Filesystem Perms** | File mode 700, owner UID | App dir readable only by UID 10001 | Permission-based access |
| **SELinux DAC** | Domain + type rules | App domain restricted | Privilege escalation |
| **Binder** | Service permission checks | Only granted apps call services | Unauthorized service calls |
| **Encryption** | FBE encrypted /data | Data encrypted with PIN key | Offline data theft |
| **Verified Boot** | Hash verification | System.img signed | Booting modified kernel |
| **Read-only /system** | Mount remounted ro | System partition immutable | System modification |

**Result**: Comprehensive security through **filesystem, permissions, SELinux, and encryption working together**
