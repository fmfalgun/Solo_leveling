# Linux Filesystem Architecture  
## Directory Structure, Hierarchy, Permissions, and System Organization

---

## Table of Contents
1. Linux Filesystem Overview
2. Root Directory Structure (FHS - Filesystem Hierarchy Standard)
3. Directory Purposes and Permissions
4. Permission Model: UID/GID/Modes
5. Special Filesystems (/proc, /sys, /dev)
6. Mount Points and Partition Structure
7. Linking: Hard Links vs Symbolic Links
8. Common File Locations Reference

---

## 1. Linux Filesystem Overview

### Filesystem Principles

```
Linux filesystem follows key principles:
├─ Everything is a file (files, directories, devices, sockets)
├─ Single rooted tree (one /, everything below)
├─ Case-sensitive (File.txt ≠ file.txt)
├─ Forward slashes for paths (/home/user/file.txt)
├─ No drive letters (unlike Windows C:, D:)
└─ Hierarchical and extensible
```

### Basic Filesystem Structure

```
/                                (Root directory - top of hierarchy)
├─ Essential system directories
├─ User directories
├─ Variable data
├─ Device files
├─ Virtual filesystems
└─ Mount points for other partitions
```

---

## 2. Linux Root Directory Structure (FHS)

### / - Root Directory

The absolute top of the filesystem hierarchy.

```bash
ls -la /
```

Output:
```
drwxr-xr-x.  root root  /
lrwxrwxrwx   root root  /bin → usr/bin
lrwxrwxrwx   root root  /lib → usr/lib
drwxr-xr-x   root root  /boot
drwxr-xr-x   root root  /dev
drwxr-xr-x   root root  /etc
drwxr-xr-x   root root  /home
lrwxrwxrwx   root root  /lib → usr/lib
lrwxrwxrwx   root root  /lib64 → usr/lib64
drwx------   root root  /root
drwxr-xr-x   root root  /run
lrwxrwxrwx   root root  /sbin → usr/sbin
drwxr-xr-x   root root  /sys
drwxrwxrwt   root root  /tmp
drwxr-xr-x   root root  /usr
drwxr-xr-x   root root  /var
drwxr-xr-x   root root  /opt
drwxr-xr-x   root root  /mnt
drwxr-xr-x   root root  /media
```

---

## 3. Complete Directory Reference

### /bin - Essential User Binaries

```
/bin/
├─ Essential command-line tools
├─ Available to all users
├─ Examples:
│  ├─ ls      (list files)
│  ├─ cat     (view file contents)
│  ├─ bash    (shell)
│  ├─ grep    (search text)
│  ├─ find    (search files)
│  ├─ cp      (copy)
│  ├─ mv      (move)
│  ├─ rm      (remove)
│  ├─ chmod   (change permissions)
│  ├─ chown   (change owner)
│  └─ touch   (create file)
│
└─ Typically symlink to /usr/bin (modern systems)

Permissions: drwxr-xr-x (755)
Owner: root
```

### /sbin - System Binaries

```
/sbin/
├─ System administration commands
├─ Usually requires root privilege
├─ Examples:
│  ├─ ifconfig    (network configuration)
│  ├─ route       (routing table)
│  ├─ iptables    (firewall)
│  ├─ fdisk       (disk partition)
│  ├─ mount       (mount filesystems)
│  ├─ reboot      (reboot system)
│  ├─ shutdown    (shutdown system)
│  ├─ parted      (partition tool)
│  ├─ lvchange    (LVM management)
│  └─ systemctl   (systemd control)
│
└─ Typically symlink to /usr/sbin (modern systems)

Permissions: drwxr-xr-x (755)
Owner: root
```

### /lib and /lib64 - System Libraries

```
/lib/
├─ Essential shared libraries
├─ Required by binaries in /bin and /sbin
├─ Examples:
│  ├─ libc.so.6        (C standard library)
│  ├─ libm.so.6        (math library)
│  ├─ libdl.so.2       (dynamic loader)
│  ├─ libcrypt.so.1    (encryption)
│  ├─ libssl.so.1.1    (SSL/TLS)
│  ├─ libcrypto.so.1.1 (crypto)
│  └─ libnss_*.so      (name service)

/lib64/
├─ 64-bit libraries (on 64-bit systems)
├─ /lib32 for 32-bit (on some systems)
└─ Same libraries as /lib but different architecture

Permissions: drwxr-xr-x (755)
Owner: root
```

### /boot - Boot Files

```
/boot/
├─ Bootloader files (GRUB, LILO)
├─ Kernel images
├─ Initial ramdisk (initramfs, initrd)
├─ Files:
│  ├─ vmlinuz-5.10.0-13  (Linux kernel image)
│  ├─ initrd-5.10.0-13   (Initial ramdisk for modules)
│  ├─ config-5.10.0-13   (Kernel configuration)
│  ├─ System.map         (Kernel symbol map)
│  ├─ grub/
│  │  ├─ grub.cfg       (GRUB configuration)
│  │  └─ /i386-pc/      (GRUB modules)
│  └─ lost+found/        (fsck recovery)
│
├─ Only readable by root
├─ Separate partition for security
│
└─ Permissions: drwxr-xr-x (755)

Boot process:
    ├─ BIOS/UEFI loads bootloader from /boot
    ├─ Bootloader loads kernel from /boot/vmlinuz-*
    ├─ Bootloader loads initramfs from /boot/initrd-*
    ├─ Kernel takes over
    └─ initramfs mounts root filesystem
```

### /dev - Device Files

```
/dev/
├─ Virtual device files representing hardware
├─ Kernel-managed (udev creates dynamically)
├─ Block devices (disks, partitions):
│  ├─ /dev/sda       (First hard disk)
│  ├─ /dev/sda1      (First partition of sda)
│  ├─ /dev/nvme0n1   (NVMe disk)
│  └─ /dev/vda       (Virtual disk - QEMU/KVM)
│
├─ Character devices:
│  ├─ /dev/tty       (Terminal)
│  ├─ /dev/ttyS0     (Serial port)
│  ├─ /dev/null      (Discard output)
│  ├─ /dev/zero      (Generate zeros)
│  ├─ /dev/random    (Random data)
│  ├─ /dev/urandom   (Non-blocking random)
│  └─ /dev/pts/*     (Pseudo-terminals)
│
├─ Special devices:
│  ├─ /dev/mapper/   (Device mapper - LVM, encryption)
│  ├─ /dev/loop0     (Loop device - mount file as disk)
│  └─ /dev/dm-*      (Device mapper devices)
│
└─ Permissions: Dynamic (udev rules)

Example: Access hard disk partition
    ├─ cat /dev/sda1 → reads sector-by-sector
    ├─ Only root can do this
    └─ Low-level disk access
```

### /etc - Configuration Files

```
/etc/
├─ System-wide configuration files
├─ Plain text (mostly)
├─ Edit to configure system behavior
├─ Key files:
│  ├─ passwd              (user accounts)
│  ├─ shadow              (password hashes - root only)
│  ├─ group               (group definitions)
│  ├─ gshadow             (group passwords)
│  ├─ sudoers             (sudo permissions)
│  ├─ hostname            (system hostname)
│  ├─ fstab               (filesystem mount table)
│  ├─ resolv.conf         (DNS configuration)
│  ├─ hosts               (hostname to IP mapping)
│  ├─ SSH config          (ssh server configuration)
│  ├─ network/            (network configuration)
│  ├─ sysctl.conf         (kernel parameters)
│  └─ security/           (security settings, AppArmor, SELinux)
│
├─ Subdirectories:
│  ├─ /etc/systemd/       (systemd unit files)
│  ├─ /etc/init.d/        (SysV init scripts)
│  ├─ /etc/cron.d/        (scheduled tasks)
│  ├─ /etc/default/       (default settings for services)
│  ├─ /etc/ssl/           (SSL certificates)
│  ├─ /etc/ssh/           (SSH keys and config)
│  ├─ /etc/apt/           (APT package manager)
│  ├─ /etc/yum.repos.d/   (Yum repository config)
│  └─ /etc/profile.d/     (shell profile scripts)
│
├─ Permissions: Mostly 644 or 755, some 600 (shadow, sudoers)
└─ Owner: root

Important: Never edit /etc/passwd manually (use passwd command)
           Use vipw to edit /etc/passwd safely
```

### /home - User Home Directories

```
/home/
├─ User home directories
├─ Each user gets /home/username/
├─ Example structure:
│  /home/alice/
│  ├─ .bashrc          (bash configuration)
│  ├─ .bash_history    (shell history)
│  ├─ .ssh/            (SSH keys)
│  │  ├─ id_rsa        (private key)
│  │  ├─ id_rsa.pub    (public key)
│  │  └─ authorized_keys (allowed remote users)
│  ├─ .config/         (application configs)
│  ├─ .local/          (user local data)
│  │  ├─ bin/          (user scripts)
│  │  ├─ share/        (user data)
│  │  └─ lib/          (user libraries)
│  ├─ Documents/       (documents)
│  ├─ Downloads/       (downloads)
│  ├─ Music/           (music files)
│  ├─ Pictures/        (images)
│  └─ Videos/          (videos)
│
├─ Permissions: 700 (user only - drwx------)
├─ Owner: user (alice)
│
└─ /root/ (root user home)
   ├─ Only accessible by root
   ├─ Permissions: 700
   └─ Not in /home (special case)
```

### /root - Root User Home

```
/root/
├─ Home directory of root user
├─ NOT in /home (special location)
├─ Only root can access
├─ Same structure as regular user home
├─ Permissions: 700 (drwx------)
│
└─ Usage:
    ├─ Root's configuration files
    ├─ Root's private files
    ├─ Root's SSH keys
    └─ Root's shell history
```

### /tmp - Temporary Files

```
/tmp/
├─ Temporary files (cleared on reboot)
├─ World-writable (anyone can create/delete)
├─ Permissions: 1777 (drwxrwxrwt - sticky bit set)
├─ Files cleaned on reboot
│
├─ Example:
│  ├─ /tmp/file1234567.tmp  (temporary data)
│  ├─ /tmp/xvfb-run-12345   (X server socket)
│  └─ /tmp/.X11-unix/       (X display sockets)
│
└─ Never store important data in /tmp
```

### /var - Variable Data

```
/var/
├─ Variable data that changes during runtime
├─ NOT cleared on reboot
├─ Subdirectories:
│  │
│  ├─ /var/log/              (System logs)
│  │  ├─ syslog              (system log)
│  │  ├─ auth.log            (authentication)
│  │  ├─ kernel.log          (kernel messages)
│  │  ├─ apt/                (APT package manager)
│  │  ├─ auth.log            (sudo, SSH attempts)
│  │  └─ /var/log/app-name/  (application logs)
│  │
│  ├─ /var/cache/            (Cache data)
│  │  ├─ apt/                (APT cache)
│  │  ├─ apt-apt-cacher/     (APT cacher)
│  │  └─ yum/                (Yum cache)
│  │
│  ├─ /var/spool/            (Print jobs, mail)
│  │  ├─ mail/               (incoming mail)
│  │  ├─ cron/               (cron jobs)
│  │  └─ cups/               (print jobs)
│  │
│  ├─ /var/run/              (Runtime data)
│  │  ├─ sshd.pid            (SSH daemon PID)
│  │  ├─ mysqld.pid          (MySQL PID)
│  │  └─ docker.sock         (Docker socket)
│  │  (often symlink to /run/)
│  │
│  ├─ /var/lock/             (Lock files)
│  │  └─ .lock files for resources
│  │  (often symlink to /run/lock/)
│  │
│  ├─ /var/tmp/              (Temporary files - survives reboot)
│  │  └─ /tmp is cleared, /var/tmp survives
│  │
│  ├─ /var/lib/              (Application data)
│  │  ├─ mysql/              (MySQL database files)
│  │  ├─ postgresql/         (PostgreSQL data)
│  │  ├─ docker/             (Docker container data)
│  │  ├─ apt/                (APT data)
│  │  └─ dpkg/               (Package management)
│  │
│  ├─ /var/www/              (Web server data)
│  │  ├─ html/               (HTML files)
│  │  └─ cgi-bin/            (CGI scripts)
│  │
│  └─ /var/mail/             (User mail)
│     └─ Deprecated (use /var/spool/mail/)
│
└─ Permissions: Varies by subdirectory
```

### /usr - User Programs and Data

```
/usr/
├─ User programs, libraries, and documentation
├─ Not essential for boot (can be on separate partition)
├─ Mounted after /
├─ Subdirectories:
│  │
│  ├─ /usr/bin/              (User programs)
│  │  ├─ python3
│  │  ├─ perl
│  │  ├─ gcc
│  │  ├─ g++
│  │  ├─ vim
│  │  └─ ... (thousands of utilities)
│  │
│  ├─ /usr/sbin/             (System programs)
│  │  ├─ useradd             (add user)
│  │  ├─ userdel             (delete user)
│  │  ├─ groupadd            (add group)
│  │  ├─ sshd-keygen         (SSH key generation)
│  │  └─ ... (system tools)
│  │
│  ├─ /usr/lib/              (Libraries for /usr/bin)
│  │  ├─ libssl.so.1.1
│  │  ├─ libcrypto.so.1.1
│  │  ├─ libpython3.9.so
│  │  └─ ... (thousands of libraries)
│  │
│  ├─ /usr/lib64/            (64-bit libraries)
│  │
│  ├─ /usr/local/            (Locally installed software)
│  │  ├─ bin/                (user-installed programs)
│  │  ├─ lib/                (user-installed libraries)
│  │  └─ share/              (user-installed data)
│  │
│  ├─ /usr/share/            (Shared data files)
│  │  ├─ doc/                (documentation)
│  │  ├─ man/                (manual pages)
│  │  ├─ icons/              (icons)
│  │  ├─ fonts/              (fonts)
│  │  ├─ locale/             (localization)
│  │  ├─ templates/          (templates)
│  │  └─ applications/       (desktop shortcuts)
│  │
│  ├─ /usr/include/          (C header files)
│  │  ├─ stdio.h
│  │  ├─ stdlib.h
│  │  └─ ... (development headers)
│  │
│  ├─ /usr/src/              (Source code)
│  │  ├─ linux/              (kernel source)
│  │  └─ /linux-headers/     (kernel headers for building)
│  │
│  └─ /usr/games/            (Games)
│
└─ Typically read-only on production servers
```

### /opt - Optional Software

```
/opt/
├─ Third-party or optional software
├─ Not part of standard installation
├─ Example directory structure:
│  /opt/
│  ├─ google-chrome/         (Chrome browser)
│  │  ├─ bin/
│  │  ├─ lib/
│  │  └─ share/
│  │
│  ├─ java/                  (Java installation)
│  │  ├─ jdk-11.0.11/
│  │  └─ jdk-1.8.0_291/
│  │
│  ├─ tomcat/                (Tomcat app server)
│  │  ├─ bin/
│  │  ├─ webapps/
│  │  └─ lib/
│  │
│  ├─ docker/                (Docker installation)
│  │  └─ docker-compose
│  │
│  └─ mycompany/             (Company software)
│     ├─ application/
│     ├─ config/
│     └─ data/
│
└─ Each vendor can manage their own directory
```

### /mnt and /media - Mount Points

```
/mnt/
├─ Temporary mount points
├─ System administrator mounts devices here
├─ Example:
│  ├─ /mnt/usb/              (USB drive mounted here)
│  ├─ /mnt/external/         (External disk)
│  ├─ /mnt/nfs/              (NFS share)
│  └─ /mnt/backup/           (Backup drive)
│
└─ Usage:
    mount /dev/sdb1 /mnt/usb

/media/
├─ Automatic mount points
├─ Desktop environment mounts devices
├─ Example:
│  ├─ /media/alice/USB_DRIVE/   (USB with label)
│  ├─ /media/alice/EXTERNAL/    (External disk)
│  └─ /media/bob/BACKUP/        (Another user's mount)
│
└─ Used by file managers and automount
```

### /proc - Process Information (Virtual Filesystem)

```
/proc/
├─ Virtual filesystem - kernel-created
├─ No actual files on disk
├─ Shows running processes and system info
├─ Re-created on every boot
├─ Examples:
│  ├─ /proc/1/               (process 1 - init)
│  │  ├─ cmdline             (command line)
│  │  ├─ status              (process status)
│  │  ├─ maps                (memory maps)
│  │  ├─ fd/                 (file descriptors)
│  │  ├─ cwd                 (current working directory symlink)
│  │  └─ exe                 (executable symlink)
│  │
│  ├─ /proc/[pid]/           (process-specific info)
│  │  ├─ environ             (environment variables)
│  │  ├─ io                  (I/O statistics)
│  │  ├─ limits              (resource limits)
│  │  ├─ net/                (network info per process)
│  │  └─ numa_maps           (NUMA memory info)
│  │
│  ├─ /proc/cpuinfo          (CPU information)
│  ├─ /proc/meminfo          (Memory information)
│  ├─ /proc/diskstats        (Disk I/O stats)
│  ├─ /proc/net/             (Network information)
│  │  ├─ tcp                 (TCP connections)
│  │  ├─ udp                 (UDP connections)
│  │  ├─ netstat             (network stats)
│  │  └─ route               (routing table)
│  │
│  ├─ /proc/sys/             (Kernel parameters - sysctl)
│  │  ├─ kernel/
│  │  ├─ net/
│  │  ├─ fs/
│  │  └─ ... (tunable kernel settings)
│  │
│  ├─ /proc/cmdline          (kernel boot parameters)
│  ├─ /proc/version          (kernel version)
│  ├─ /proc/uptime           (system uptime)
│  ├─ /proc/load_avg         (load average)
│  └─ /proc/modules          (loaded kernel modules)
│
└─ Read-only for users (some restricted)
```

### /sys - Sysfs (Virtual Filesystem)

```
/sys/
├─ Virtual filesystem - kernel device structures
├─ No actual files on disk
├─ Shows hardware and kernel structures
├─ More organized than /proc
├─ Examples:
│  ├─ /sys/block/            (block devices)
│  │  ├─ sda/                (disk sda)
│  │  ├─ sdb/                (disk sdb)
│  │  └─ nvme0n1/            (NVMe disk)
│  │
│  ├─ /sys/class/            (device classes)
│  │  ├─ net/                (network interfaces)
│  │  │  ├─ eth0/            (ethernet)
│  │  │  ├─ wlan0/           (WiFi)
│  │  │  └─ lo/              (loopback)
│  │  │
│  │  ├─ usb/                (USB devices)
│  │  ├─ pci/                (PCI devices)
│  │  └─ graphics/           (GPU)
│  │
│  ├─ /sys/devices/          (device tree)
│  ├─ /sys/bus/              (buses - PCI, USB, etc.)
│  ├─ /sys/kernel/           (kernel subsystems)
│  ├─ /sys/module/           (loaded modules)
│  └─ /sys/fs/               (filesystems)
│
└─ Some files writable (for tuning)
```

### /run - Runtime Data

```
/run/
├─ Runtime data for daemons
├─ Cleared on reboot
├─ Similar to old /var/run
├─ Examples:
│  ├─ /run/sshd.pid          (SSH daemon PID)
│  ├─ /run/docker.sock       (Docker socket)
│  ├─ /run/mysqld/           (MySQL daemon directory)
│  ├─ /run/systemd/          (systemd runtime)
│  │  ├─ journal/            (journal sockets)
│  │  └─ cgroups/            (cgroup mounts)
│  │
│  ├─ /run/lock/             (lock files)
│  ├─ /run/user/             (user runtime directories)
│  │  ├─ 1000/               (user ID 1000)
│  │  │  ├─ bus              (D-Bus socket)
│  │  │  └─ gvfs/            (GVFS mounts)
│  │  └─ 1001/               (user ID 1001)
│  │
│  └─ /run/initramfs/        (initramfs data)
│
└─ Permissions: Various (mostly 755 or 777 for sockets)
```

### /lost+found - Filesystem Recovery

```
/lost+found/
├─ Created by fsck (filesystem check)
├─ Contains recovered files after crash
├─ One per partition
├─ Example:
│  ├─ /lost+found/           (root partition)
│  ├─ /home/lost+found/      (if /home is separate partition)
│  └─ /var/lost+found/       (if /var is separate partition)
│
└─ Files recovered from inode without parent directory
```

---

## 4. Permission Model: UID/GID/Modes

### User and Group IDs

```
/etc/passwd (user database):
──────────────────────────────
alice:x:1000:1000:Alice:/home/alice:/bin/bash
││    │ │    │    │     │         │
│└────┘ │    │    │     │         └─ Login shell
│       │    │    │     └──────────── Home directory
│       │    │    └────────────────── Gecos (full name)
│       │    └──────────────────────── GID (group 1000 - alice)
│       └────────────────────────────── UID (1000)
└────────────────────────────────────── Username

/etc/group (group database):
───────────────────────────
alice:x:1000:
└─ Group alice (GID 1000)

/etc/shadow (password hashes, root only):
──────────────────────────────────────────
alice:$6$...hash...:18000:0:99999:7:::
└─ Password hash (encrypted)
```

### File Permissions

```
ls -la /home/alice/secret.txt
-rw-r--r-- 1 alice alice 1024 Nov  1 10:00 secret.txt
││││││││││ │ ││││  ││││  ││││     ││    ││
││││││││││ │ ││││  ││││  ││││     ││    └── Filename
││││││││││ │ ││││  ││││  ││││     └──────── Time
││││││││││ │ ││││  ││││  └───────────────── File size (bytes)
││││││││││ │ ││││  └────────────────────── Group (alice, GID 1000)
││││││││││ │ └──────────────────────────── Owner (alice, UID 1000)
││││││││││ └──────────────────────────────── Hard link count (1)
└─────────┴──────────────────────────────── File type and permissions

Permission bits:
────────────────
-       rw-      r--      r--
│       │││      │││      │││
│       │││      │││      └──┴──┴── Other (o): read only
│       │││      └──┴──┴────────── Group (g): read only
│       └──┴──┴────────────────── Owner (u): read-write
└────────────────────────────── Regular file (- = file, d = directory, l = symlink)

Octal notation:
───────────────
4 = read (r)
2 = write (w)
1 = execute (x)

rwx = 4+2+1 = 7
rw- = 4+2+0 = 6
r-x = 4+0+1 = 5
r-- = 4+0+0 = 4
-wx = 0+2+1 = 3
-w- = 0+2+0 = 2
--x = 0+0+1 = 1
--- = 0+0+0 = 0

Example: 755
├─ Owner: 7 (rwx)
├─ Group: 5 (r-x)
└─ Other: 5 (r-x)

Example: 644
├─ Owner: 6 (rw-)
├─ Group: 4 (r--)
└─ Other: 4 (r--)
```

### Special Permissions

```
Sticky Bit (1000 in octal):
───────────────────────────
drwxrwxrwt /tmp
└─ t in permission (execute position has sticky bit)
└─ Only owner can delete files in /tmp (even if world-writable)

Setuid Bit (4000 in octal):
──────────────────────────
-rwsr-xr-x /usr/bin/passwd
└─ s instead of x (setuid bit)
└─ When run, executes as file owner (root), not runner

Setgid Bit (2000 in octal):
──────────────────────────
-rwxr-sr-x /usr/bin/chage
└─ s instead of x (setgid bit)
└─ When run, executes as file group, not runner
```

---

## 5. Linux Filesystem Structure Summary

| Directory | Purpose | User Access | Owner |
|-----------|---------|---|---|
| / | Root | Read-only | root |
| /bin | Essential binaries | All users | root |
| /sbin | System binaries | Root only | root |
| /lib | Essential libraries | All users | root |
| /boot | Kernel & bootloader | Read-only | root |
| /dev | Device files | Varies | root |
| /etc | Configuration | All read, root write | root |
| /home | User homes | User only | each user |
| /root | Root home | Root only | root |
| /tmp | Temporary | All users | root |
| /var | Variable data | All read, varying write | root |
| /usr | User programs | All read, root write | root |
| /opt | Optional software | Varies | root |
| /mnt | Manual mounts | Varies | root |
| /media | Auto mounts | Varies | root |
| /proc | Process info | All read | kernel |
| /sys | System info | All read | kernel |
| /run | Runtime data | Varies | root |

---

## 6. Partition Structure

### Typical Partitions on Linux Server

```
Device: /dev/sda (500GB disk)
────────────────────────────

/dev/sda1: EFI System Partition    (512 MB)  → /boot/efi
/dev/sda2: /boot partition        (1 GB)    → /boot
/dev/sda3: Root partition         (50 GB)   → /
/dev/sda4: Extended               (448 GB)
   /dev/sda5: /home partition    (100 GB)   → /home
   /dev/sda6: /var partition     (100 GB)   → /var
   /dev/sda7: /tmp partition     (50 GB)    → /tmp
   /dev/sda8: Swap partition     (8 GB)     → (swap)

Separate partitions allow:
├─ Independent filesystem types
├─ Independent mount permissions (/ read-only, /var read-write)
├─ Independent quotas
├─ Independent backup strategies
└─ Containment of filesystem corruption
```

---

## Summary: Linux Filesystem

**Key Points:**

1. **Hierarchical**: Single tree rooted at /
2. **Standard**: FHS (Filesystem Hierarchy Standard) compliance
3. **Flexible**: Can mount additional partitions anywhere
4. **Permissioned**: UID/GID/mode based access control
5. **Transparent**: Virtual filesystems (/proc, /sys) provide system info
6. **Portable**: Same structure on all Linux systems

This completes the Linux filesystem reference! Next artifact will cover Android process management in complete detail.
