# Kali Linux: Boot, Init & Filesystem Analysis Lab
## Complete Setup Guide for Security Researchers

---

## Table of Contents
1. Lab Architecture & Overview
2. Host System Preparation (Kali)
3. VirtualBox Setup for Lab VMs
4. Creating VM Disk Images (Multiple Rootfs)
5. Init System Test Environments
6. Boot Process Analysis Tools
7. Filesystem Analysis & Forensics Setup
8. Live Boot & Recovery Tools
9. Lab Automation & Scripting
10. Experiment Workflows
11. Troubleshooting & Recovery

---

## 1. Lab Architecture & Overview

### What This Lab Does

```
Purpose: Analyze and test boot processes, init systems, 
and filesystem structures across different Linux configurations

Components:
├─ Host: Kali Linux (your main attack/analysis machine)
├─ Hypervisor: VirtualBox or KVM/QEMU
├─ Guest VMs:
│  ├─ VM 1: Systemd Lab (Ubuntu/Debian-based)
│  ├─ VM 2: SysV/OpenRC Lab (Alpine or older Debian)
│  ├─ VM 3: Custom Init Lab (Buildroot or LFS)
│  └─ VM 4: Analysis Target (any distro to forensically analyze)
│
├─ Disk Images (stored on Kali):
│  ├─ rootfs-systemd.img (20GB, systemd-based)
│  ├─ rootfs-sysv.img (10GB, SysV init)
│  ├─ rootfs-custom.img (15GB, custom init)
│  └─ rootfs-forensic.img (snapshot for analysis)
│
└─ Tools (on Kali host):
   ├─ Bootloader analysis (GRUB tools, EFI tools)
   ├─ Filesystem tools (e2fsprogs, btrfs, xfsprogs)
   ├─ Init analysis (systemd tools, s6, OpenRC)
   ├─ Forensics (sleuthkit, Autopsy, ext4magic)
   ├─ Boot analysis (kernel params, systemd-analyze)
   └─ Scripting (Python, Bash for automation)
```

### Security Researcher Perspective

```
This lab helps you:

1. Understand boot attack surface
   ├─ Bootloader exploitation
   ├─ Initramfs modification
   ├─ Kernel parameter injection
   └─ Early boot rootkits

2. Analyze init system vulnerabilities
   ├─ Service escalation paths
   ├─ Socket/IPC abuse
   ├─ Privilege boundary weaknesses
   └─ Custom init exploits

3. Forensic filesystem analysis
   ├─ Recover deleted files
   ├─ Analyze journaling data
   ├─ Detect tampering
   ├─ Timeline reconstruction
   └─ Carving unallocated space

4. Develop custom tools
   ├─ Filesystem parsers
   ├─ Boot integrity checkers
   ├─ Init system monitors
   └─ Recovery automation

5. Test attack scenarios
   ├─ Boot-time persistence
   ├─ Init system hijacking
   ├─ Filesystem-level attacks
   └─ Recovery evasion
```

---

## 2. Host System Preparation (Kali Linux)

### 2.1 Verify Kali Setup

```bash
# Check Kali installation
cat /etc/os-release
# Should show: Kali Linux

# Verify you have sudo/root access
sudo whoami
# Output: root

# Check available disk space (need 150GB+ for lab)
df -h /
# Look for large partition

# Check CPU virtualization support
grep -E "vmx|svm" /proc/cpuinfo
# If output is empty: virtualization disabled in BIOS
# If showing vmx (Intel) or svm (AMD): you're good

# Check RAM available
free -h
# Recommendation: 16GB+ host RAM for comfortable lab
```

### 2.2 Install Hypervisor (Choose One)

#### **Option A: VirtualBox (Recommended for GUIs)**

```bash
# Install VirtualBox on Kali
sudo apt update
sudo apt install -y virtualbox virtualbox-ext-pack dkms

# Add your user to vboxusers group (for non-sudo access)
sudo usermod -aG vboxusers $USER
newgrp vboxusers

# Verify installation
virtualbox --version

# Start VirtualBox GUI
virtualbox &
# Or use command-line tools:
vboxmanage --version
```

#### **Option B: KVM/QEMU (Recommended for performance)**

```bash
# Install KVM/QEMU
sudo apt update
sudo apt install -y qemu-kvm libvirt-daemon-system libvirt-daemon virt-manager

# Add your user to libvirt group
sudo usermod -aG libvirt $USER
sudo usermod -aG kvm $USER
newgrp libvirt
newgrp kvm

# Verify installation
virsh version
qemu-system-x86_64 --version

# Start virt-manager GUI (Xfce/KDE desktop needed)
virt-manager &
```

**My Recommendation for Kali:** Use **KVM + virt-manager** if you have GUI, **QEMU CLI** if headless. VirtualBox also works well.

### 2.3 Create Lab Directory Structure

```bash
# Create dedicated lab workspace on Kali
mkdir -p ~/lab-boot-init-fs/
cd ~/lab-boot-init-fs/

# Subdirectories for organization
mkdir -p {vm-images,configs,scripts,tools,analysis,backups}

# Explanation:
├─ vm-images/          # Virtual disk images (large, 100+ GB)
├─ configs/            # VM configs, snapshots metadata
├─ scripts/            # Automation scripts (Python, Bash)
├─ tools/              # Custom analysis tools
├─ analysis/           # Forensic results, notes
└─ backups/            # Critical backups

# Set permissions
chmod 700 ~/lab-boot-init-fs/

# Verify
ls -la ~/lab-boot-init-fs/
```

### 2.4 Install Essential Tools on Kali Host

```bash
# Update Kali
sudo apt update
sudo apt upgrade -y

# Filesystem tools
sudo apt install -y \
    e2fsprogs \
    btrfs-progs \
    xfsprogs \
    lvm2 \
    cryptsetup \
    parted \
    gparted \
    gdisk

# Boot & kernel tools
sudo apt install -y \
    grub-common \
    grub-pc-bin \
    grub-efi-amd64-bin \
    efibootmgr \
    dracut \
    initramfs-tools \
    linux-headers-amd64

# Init system tools
sudo apt install -y \
    systemd-container \
    systemd-devel \
    openrc \
    elogind

# Analysis & forensics
sudo apt install -y \
    sleuthkit \
    autopsy \
    testdisk \
    photorec \
    extundelete \
    ext4magic \
    chntpw \
    dd_rescue

# Boot analysis
sudo apt install -y \
    bootloader-utils \
    kexec-tools \
    memtest86+ \
    cpu-checker

# Kernel & module tools
sudo apt install -y \
    kernel-source \
    kernel-devel \
    module-init-tools

# Scripting & automation
sudo apt install -y \
    python3-dev \
    python3-pip \
    git

# Additional utilities
sudo apt install -y \
    tree \
    htop \
    ncdu \
    hexdump \
    hexedit \
    strace \
    ltrace \
    systemtap

# Verify installations
which parted grub-mkimage systemd-analyze sleuthkit
```

### 2.5 Create Kali Working Environment

```bash
# Create analysis notebook
cat > ~/lab-boot-init-fs/README.md << 'EOF'
# Boot, Init & Filesystem Analysis Lab

## Lab Configuration
- Host OS: Kali Linux
- Hypervisor: KVM/QEMU or VirtualBox
- Lab Date: $(date)

## VMs Created
- [ ] VM1: Systemd Lab
- [ ] VM2: SysV/OpenRC Lab
- [ ] VM3: Custom Init Lab
- [ ] VM4: Analysis Target

## Experiments Completed
- [ ] Boot process analysis
- [ ] Init system comparison
- [ ] Filesystem forensics
- [ ] Recovery procedures

## Notes
[Your research notes here]
EOF

# Create tool development directory
mkdir -p ~/lab-boot-init-fs/tools/custom-tools
cat > ~/lab-boot-init-fs/tools/custom-tools/README.md << 'EOF'
# Custom Analysis Tools

## Tools to develop:
1. Boot order analyzer
2. Init system parser
3. Filesystem anomaly detector
4. Permission auditor
5. Journal analyzer
EOF

# Create scripts directory
mkdir -p ~/lab-boot-init-fs/scripts
cat > ~/lab-boot-init-fs/scripts/setup-vm.sh << 'EOF'
#!/bin/bash
# Lab VM setup automation
# Usage: ./setup-vm.sh <vm-name> <distro>

VM_NAME=$1
DISTRO=$2
VM_IMAGE="$HOME/lab-boot-init-fs/vm-images/${VM_NAME}.qcow2"

echo "Creating VM: $VM_NAME"
# Script content will be added below
EOF

chmod +x ~/lab-boot-init-fs/scripts/*.sh
```

---

## 3. VirtualBox Setup for Lab VMs

### 3.1 Creating Base VM (Systemd Lab)

```bash
# Use VirtualBox GUI method:
# Or command-line for headless:

# Method 1: VirtualBox GUI (recommended for first time)
virtualbox &
# Click "New" and follow wizard:
# - Name: "Kali-Boot-Lab-Systemd"
# - Type: Linux
# - Version: Ubuntu 22.04 (64-bit)
# - RAM: 8GB
# - Disk: 50GB, VDI, dynamic

# Method 2: Command-line (vboxmanage)
vboxmanage createvm \
    --name "Kali-Boot-Lab-Systemd" \
    --ostype Ubuntu_64 \
    --register

vboxmanage modifyvm "Kali-Boot-Lab-Systemd" \
    --memory 8192 \
    --cpus 4 \
    --vram 256 \
    --nic1 bridged \
    --bridgeadapter1 eth0

vboxmanage createhd \
    --filename ~/lab-boot-init-fs/vm-images/systemd-lab.vdi \
    --size 50000

vboxmanage storagectl "Kali-Boot-Lab-Systemd" \
    --name "SATA" \
    --add sata

vboxmanage storageattach "Kali-Boot-Lab-Systemd" \
    --storagectl "SATA" \
    --port 0 \
    --device 0 \
    --type hdd \
    --medium ~/lab-boot-init-fs/vm-images/systemd-lab.vdi

vboxmanage storagectl "Kali-Boot-Lab-Systemd" \
    --name "IDE" \
    --add ide

# Download Ubuntu Server ISO to ~/lab-boot-init-fs/isos/
# Then attach:
vboxmanage storageattach "Kali-Boot-Lab-Systemd" \
    --storagectl "IDE" \
    --port 0 \
    --device 0 \
    --type dvddrive \
    --medium ~/lab-boot-init-fs/isos/ubuntu-22.04-live-server-amd64.iso

# Start VM
vboxmanage startvm "Kali-Boot-Lab-Systemd" --type gui
```

### 3.2 Installation & Initial Configuration

```bash
# Inside VM (after booting from ISO):

# Complete Ubuntu installation normally
# When prompted for services to install, choose:
# - [ ] SSH Server (yes)
# - [ ] Standard system utilities (yes)
# - [ ] Build essential tools (yes)

# After first boot:
sudo apt update && sudo apt upgrade -y

# Install tools inside guest VM
sudo apt install -y \
    build-essential \
    linux-headers-generic \
    systemd-devel \
    git \
    curl \
    vim \
    net-tools \
    strace \
    ltrace \
    gdb

# Prepare for cloning/snapshotting
sudo useradd -m labuser
sudo usermod -aG sudo labuser
# Password: (set a simple password)
```

### 3.3 Create Snapshots

```bash
# On Kali host, take snapshots after key milestones

# Snapshot 1: Fresh install
vboxmanage snapshot "Kali-Boot-Lab-Systemd" take "Fresh-Install" \
    --description "Clean Ubuntu 22.04 installation"

# Snapshot 2: Tools installed
vboxmanage snapshot "Kali-Boot-Lab-Systemd" take "Tools-Installed" \
    --description "Development tools and analysis utilities installed"

# List snapshots
vboxmanage snapshot "Kali-Boot-Lab-Systemd" list

# To revert:
vboxmanage snapshot "Kali-Boot-Lab-Systemd" restore "Fresh-Install"
```

---

## 4. Creating VM Disk Images (Multiple Rootfs)

### 4.1 Understanding Multiple Rootfs Need

```
Why different root filesystems?
├─ Test init systems: systemd, SysV, OpenRC, custom s6
├─ Test filesystems: ext4, btrfs, xfs, zfs
├─ Test boot configs: GRUB, UEFI, custom bootloader
└─ Forensic analysis: read-only, unmodified, preserved

Strategy:
├─ Create raw images (img format)
├─ Mount as loop devices
├─ Chroot into them
├─ Modify init, services, configs
├─ Boot from them
└─ Analyze without touching original
```

### 4.2 Creating ext4 Rootfs Image

```bash
# On Kali host

cd ~/lab-boot-init-fs/vm-images/

# Create 20GB sparse ext4 image
dd if=/dev/zero of=rootfs-systemd-clean.img bs=1M count=1
dd if=/dev/zero of=rootfs-systemd-clean.img bs=1M seek=20479 count=1

# Format with ext4
mkfs.ext4 -F rootfs-systemd-clean.img

# Mount it
mkdir -p /tmp/mnt-systemd
sudo mount -o loop rootfs-systemd-clean.img /tmp/mnt-systemd

# Populate with minimal system (using debootstrap)
sudo apt install -y debootstrap

# Create Ubuntu 22.04 rootfs (will take 5-10 minutes)
sudo debootstrap \
    --include=systemd,grub-pc,linux-image-amd64 \
    jammy \
    /tmp/mnt-systemd \
    http://archive.ubuntu.com/ubuntu/

# Unmount
sudo umount /tmp/mnt-systemd

# Verify
ls -lh rootfs-systemd-clean.img
```

### 4.3 Creating Btrfs Rootfs Image

```bash
# Create 20GB sparse btrfs image
cd ~/lab-boot-init-fs/vm-images/

dd if=/dev/zero of=rootfs-btrfs.img bs=1M count=1
dd if=/dev/zero of=rootfs-btrfs.img bs=1M seek=20479 count=1

# Format with btrfs
mkfs.btrfs -f rootfs-btrfs.img

# Mount
mkdir -p /tmp/mnt-btrfs
sudo mount -o loop rootfs-btrfs.img /tmp/mnt-btrfs

# Populate with debootstrap
sudo debootstrap \
    --include=systemd,grub-pc,linux-image-amd64,btrfs-progs \
    jammy \
    /tmp/mnt-btrfs \
    http://archive.ubuntu.com/ubuntu/

# Create btrfs snapshot (for forensic comparison)
sudo btrfs subvolume snapshot /tmp/mnt-btrfs /tmp/mnt-btrfs/@snapshot-clean

sudo umount /tmp/mnt-btrfs

# Verify
ls -lh rootfs-btrfs.img
```

### 4.4 Creating Custom Init Rootfs

```bash
# For testing custom init systems (s6, runit, etc.)

cd ~/lab-boot-init-fs/vm-images/

# Create Alpine Linux image (minimal, ~3GB)
dd if=/dev/zero of=rootfs-alpine-custom.img bs=1M count=1
dd if=/dev/zero of=rootfs-alpine-custom.img bs=1M seek=3071 count=1

mkfs.ext4 -F rootfs-alpine-custom.img

mkdir -p /tmp/mnt-alpine
sudo mount -o loop rootfs-alpine-custom.img /tmp/mnt-alpine

# Alpine uses apk, not apt
# Download Alpine rootfs tarball manually or use:
# https://dl-cdn.alpinelinux.org/alpine/latest-stable/releases/x86_64/

# If you have Alpine rootfs:
# sudo tar xzf alpine-rootfs.tar.gz -C /tmp/mnt-alpine/

# Or install via minimal Alpine environment:
# (This is more complex; using pre-built rootfs easier)

sudo umount /tmp/mnt-alpine
```

---

## 5. Init System Test Environments

### 5.1 Systemd Lab VM Setup

```bash
# Inside Systemd VM (or running on mounted rootfs)

# Verify systemd is init
ps aux | grep -E "^\s*1\s" | head -1

# View system targets
systemctl list-units --type=target

# Create custom service for testing
sudo tee /etc/systemd/system/boot-test.service > /dev/null << 'EOF'
[Unit]
Description=Boot Test Service
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/boot-test.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

# Create script
sudo tee /usr/local/bin/boot-test.sh > /dev/null << 'EOF'
#!/bin/bash
echo "Boot test at $(date)" >> /var/log/boot-test.log
echo "Kernel: $(uname -r)" >> /var/log/boot-test.log
EOF

sudo chmod +x /usr/local/bin/boot-test.sh

# Enable and test
sudo systemctl daemon-reload
sudo systemctl enable boot-test.service
sudo systemctl start boot-test.service

# View logs
journalctl -u boot-test.service

# Test boot timing analysis
systemd-analyze blame
systemd-analyze critical-chain

# Test dependency graph
systemd-analyze plot > /tmp/systemd-deps.svg
# (Useful for visualizing boot dependencies)
```

### 5.2 SysV/OpenRC Lab Setup

```bash
# Create or boot Alpine/Debian-based SysV system

# If using mounted rootfs:
sudo mount -o loop ~/lab-boot-init-fs/vm-images/rootfs-alpine.img /tmp/mnt-sysv
sudo chroot /tmp/mnt-sysv

# Or SSH into SysV VM

# Verify SysV init
ps aux | grep -E "^\s*1\s" | head -1

# List runlevels
ls -la /etc/rc*.d/

# Create custom init script
sudo tee /etc/init.d/boot-analysis << 'EOF'
#!/bin/sh

### BEGIN INIT INFO
# Provides:       boot-analysis
# Required-Start: $local_fs
# Required-Stop:
# Default-Start:  2 3 4 5
# Default-Stop:
# Description:    Boot process analysis
### END INIT INFO

case "$1" in
  start)
    echo "Boot analysis started at $(date)" >> /var/log/boot-analysis.log
    echo "Init system: SysV" >> /var/log/boot-analysis.log
    ;;
  stop)
    echo "Boot analysis stopped" >> /var/log/boot-analysis.log
    ;;
  *)
    echo "Usage: $0 {start|stop}"
    exit 1
    ;;
esac
EOF

sudo chmod +x /etc/init.d/boot-analysis

# Enable for runlevel 3
sudo update-rc.d boot-analysis defaults
# Or manually:
sudo ln -s ../init.d/boot-analysis /etc/rc3.d/S30boot-analysis

# Test
sudo /etc/init.d/boot-analysis start
cat /var/log/boot-analysis.log
```

### 5.3 Creating Test Service Hierarchy

```bash
# For analyzing service dependencies and boot order

# In Systemd system:
cat > ~/lab-boot-init-fs/scripts/test-services.sh << 'EOF'
#!/bin/bash
# Create test service hierarchy

# Service 1: Base service (no dependencies)
sudo tee /etc/systemd/system/test-base.service > /dev/null << 'EOFSERVICE'
[Unit]
Description=Test Base Service

[Service]
Type=oneshot
ExecStart=/bin/echo "Base service started"
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOFSERVICE

# Service 2: Depends on Service 1
sudo tee /etc/systemd/system/test-middle.service > /dev/null << 'EOFSERVICE'
[Unit]
Description=Test Middle Service
After=test-base.service
Requires=test-base.service

[Service]
Type=oneshot
ExecStart=/bin/echo "Middle service started"
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOFSERVICE

# Service 3: Depends on Service 2
sudo tee /etc/systemd/system/test-top.service > /dev/null << 'EOFSERVICE'
[Unit]
Description=Test Top Service
After=test-middle.service
Requires=test-middle.service

[Service]
Type=oneshot
ExecStart=/bin/echo "Top service started"
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOFSERVICE

sudo systemctl daemon-reload
systemctl enable test-base.service test-middle.service test-top.service

# Visualize dependency graph
systemd-analyze plot > /tmp/service-deps.svg
echo "Dependency graph saved to /tmp/service-deps.svg"
EOF

chmod +x ~/lab-boot-init-fs/scripts/test-services.sh
```

---

## 6. Boot Process Analysis Tools

### 6.1 Setting Up Bootloader Analysis

```bash
# On Kali host

# View GRUB configuration
sudo cat /boot/grub/grub.cfg | head -50

# Edit GRUB parameters
sudo vim /etc/default/grub

# Key GRUB parameters to understand:
GRUB_CMDLINE_LINUX="..."     # Kernel command line
GRUB_ENABLE_BLSCFG=true      # BootLoaderSpec
GRUB_TIMEOUT=5               # Boot menu timeout

# Update GRUB
sudo update-grub2

# View GRUB in action (at next boot, press Shift)
# Edit entry with 'e' to see parameters
```

### 6.2 Kernel Parameter Analysis

```bash
# View current kernel boot parameters
cat /proc/cmdline

# Common security-relevant parameters:
# - selinux=0/1           (SELinux enforcement)
# - apparmor=0/1          (AppArmor enforcement)
# - init=/path/to/init    (Alternative init)
# - ro/rw                 (Root mount read-only/read-write)
# - root=UUID/...         (Root filesystem identifier)
# - console=...           (Console device)
# - quiet/verbose         (Logging level)
# - splash                (Splash screen)

# Test kernel parameter injection (in VM):
sudo vim /etc/default/grub

# Add parameter:
GRUB_CMDLINE_LINUX="console=ttyS0"

# Update and reboot
sudo update-grub2
sudo reboot

# View effect:
cat /proc/cmdline
```

### 6.3 Initramfs Analysis

```bash
# Extract and analyze initramfs

# Find initramfs
ls -la /boot/initrd*

# Extract initramfs (compressed image)
cd /tmp
cp /boot/initrd.img-5.15.0-56-generic initrd.gz
gunzip initrd.gz

# Extract CPIO archive
mkdir -p initrd-extracted
cd initrd-extracted
cpio -id < ../initrd

# Examine contents
ls -la
cat init   # First script executed
cat proc/modules
cat etc/fstab (if present)

# View typical structure:
tree . | head -50

# Security analysis:
# - Who can modify /init?
# - Are there shell scripts with weak permissions?
# - Are there hardcoded paths?
grep -r "root" . 2>/dev/null | head -10

# Build custom initramfs
# (Advanced topic, covered in next section)
```

### 6.4 Boot Timing Analysis

```bash
# On Kali host or within VM:

# Systemd boot timing
systemd-analyze

# Output shows:
# - Firmware time
# - Loader time
# - Kernel time
# - Userspace time
# - Total time

# Service startup time
systemd-analyze blame

# Critical path
systemd-analyze critical-chain

# Graphical output (export as SVG)
systemd-analyze plot > boot-timeline.svg

# On Kali (if Xfce/KDE available):
eog boot-timeline.svg  # View with Eye of GNOME
```

---

## 7. Filesystem Analysis & Forensics Setup

### 7.1 Forensic Filesystem Mounting

```bash
# Mounting rootfs images for forensic analysis (read-only)

# Use loop device with read-only flag
sudo mount -o loop,ro ~/lab-boot-init-fs/vm-images/rootfs-systemd-clean.img \
    /mnt/forensic-systemd

# Verify mounted read-only
mount | grep forensic-systemd
# Should show: "ro" flag

# Browsing forensic copy
ls -la /mnt/forensic-systemd/
cat /mnt/forensic-systemd/etc/fstab
find /mnt/forensic-systemd -name "*.conf" | head -20

# Unmount when done
sudo umount /mnt/forensic-systemd
```

### 7.2 Deleted File Recovery

```bash
# Using ext4magic or extundelete

# Mount image (can be read-write for recovery)
sudo mount -o loop ~/lab-boot-init-fs/vm-images/rootfs-ext4.img \
    /mnt/forensic-recover

# View deleted files in ext4
sudo ext4magic /dev/loop0 -f

# Recover specific deleted file
sudo ext4magic /dev/loop0 -r -f /path/to/deleted/file

# Recover all deleted files
sudo ext4magic /dev/loop0 -r -d /tmp/recovered/

# For btrfs (with snapshots):
# Btrfs snapshots are COW (copy-on-write)
# So previous versions exist in snapshots

sudo btrfs filesystem show /mnt/forensic-btrfs
sudo btrfs subvolume list /mnt/forensic-btrfs
```

### 7.3 Filesystem Timeline Creation

```bash
# Create timeline of filesystem changes (forensic analysis)

cat > ~/lab-boot-init-fs/scripts/fs-timeline.py << 'EOF'
#!/usr/bin/env python3

import os
import time
from pathlib import Path

def get_file_times(path):
    """Get filesystem times for a file"""
    stat = os.stat(path)
    return {
        'path': path,
        'atime': time.ctime(stat.st_atime),  # Access time
        'mtime': time.ctime(stat.st_mtime),  # Modify time
        'ctime': time.ctime(stat.st_ctime),  # Change time (metadata)
    }

def create_timeline(root_dir):
    """Create timeline for all files under root_dir"""
    timeline = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                timeline.append(get_file_times(filepath))
            except OSError:
                pass  # Permission denied or similar
    
    # Sort by modification time
    timeline.sort(key=lambda x: x['mtime'], reverse=True)
    return timeline

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: ./fs-timeline.py <directory>")
        sys.exit(1)
    
    root = sys.argv[1]
    timeline = create_timeline(root)
    
    # Output as CSV for analysis
    print("path,atime,mtime,ctime")
    for entry in timeline:
        print(f"{entry['path']},{entry['atime']},{entry['mtime']},{entry['ctime']}")

if __name__ == "__main__":
    main()
EOF

chmod +x ~/lab-boot-init-fs/scripts/fs-timeline.py

# Usage:
python3 ~/lab-boot-init-fs/scripts/fs-timeline.py /mnt/forensic-systemd > \
    ~/lab-boot-init-fs/analysis/fs-timeline.csv
```

### 7.4 Permission & Ownership Analysis

```bash
# Audit filesystem permissions and ownership

cat > ~/lab-boot-init-fs/scripts/fs-audit.sh << 'EOF'
#!/bin/bash
# Filesystem security audit

TARGET_DIR=${1:-.}
REPORT="fs-audit-report.txt"

echo "=== Filesystem Security Audit ===" > "$REPORT"
echo "Target: $TARGET_DIR" >> "$REPORT"
echo "Date: $(date)" >> "$REPORT"
echo "" >> "$REPORT"

# Find world-writable files (security risk)
echo "=== WORLD-WRITABLE FILES (RISK!) ===" >> "$REPORT"
find "$TARGET_DIR" -perm -002 -type f 2>/dev/null >> "$REPORT"

# Find files with setuid bit (privilege escalation potential)
echo "" >> "$REPORT"
echo "=== SETUID FILES ===" >> "$REPORT"
find "$TARGET_DIR" -perm -4000 -type f 2>/dev/null >> "$REPORT"

# Find files with setgid bit
echo "" >> "$REPORT"
echo "=== SETGID FILES ===" >> "$REPORT"
find "$TARGET_DIR" -perm -2000 -type f 2>/dev/null >> "$REPORT"

# Find sticky bit directories
echo "" >> "$REPORT"
echo "=== STICKY BIT DIRECTORIES ===" >> "$REPORT"
find "$TARGET_DIR" -perm -1000 -type d 2>/dev/null >> "$REPORT"

# Root-owned executables in user directories
echo "" >> "$REPORT"
echo "=== ROOT-OWNED FILES IN /HOME ===" >> "$REPORT"
find "$TARGET_DIR/home" -owner root -type f 2>/dev/null >> "$REPORT"

cat "$REPORT"
EOF

chmod +x ~/lab-boot-init-fs/scripts/fs-audit.sh

# Usage:
./scripts/fs-audit.sh /mnt/forensic-systemd
```

---

## 8. Live Boot & Recovery Tools

### 8.1 Setting Up Boot Recovery Tools on Kali

```bash
# Download recovery ISOs

cd ~/lab-boot-init-fs/isos/

# SystemRescue - excellent for recovery
wget https://sourceforge.net/projects/systemrescuecd/files/x86_64/systemrescue-11.00-amd64.iso

# Kali Linux Live (if needed for advanced analysis)
wget https://cdimage.kali.org/kali-latest/kali-linux-live-amd64.iso

# GParted Live - partition management
wget https://sourceforge.net/projects/gparted/files/gparted-live/1.5.0-1/gparted-live-1.5.0-1-amd64.iso

# Clonezilla - disk cloning/imaging
wget https://sourceforge.net/projects/clonezilla/files/clonezilla-live/3.1.1-27/clonezilla-live-3.1.1-27-amd64.iso

# PartedMagic - comprehensive partition/disk tool
# (Commercial, but worth it; or use Clonezilla)

# Verify downloads
sha256sum -c << 'EOF'
[paste SHA256 hashes from download page]
EOF
```

### 8.2 Creating Bootable USB Recovery Key

```bash
# Create persistent rescue USB (with Kali Linux)

# List USB devices
sudo lsblk
# Identify USB device (e.g., /dev/sdc)

# WARNING: Verify you have correct device!
USB_DEVICE=/dev/sdc

# Unmount if mounted
sudo umount ${USB_DEVICE}*

# Write SystemRescue to USB
sudo dd if=~/lab-boot-init-fs/isos/systemrescue-11.00-amd64.iso \
    of=$USB_DEVICE \
    bs=4M \
    status=progress

# Alternative: using Balena Etcher (GUI)
sudo apt install -y balena-etcher-electron
etcher &

# Then drag ISO and USB device to Balena Etcher
```

### 8.3 Automated Backup Strategy

```bash
# Automatic snapshots and backups

cat > ~/lab-boot-init-fs/scripts/backup-lab.sh << 'EOF'
#!/bin/bash
# Backup lab images daily

BACKUP_DIR="$HOME/lab-boot-init-fs/backups"
VM_IMAGES_DIR="$HOME/lab-boot-init-fs/vm-images"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

echo "Starting lab backup at $TIMESTAMP"

# Create daily backup directory
mkdir -p "$BACKUP_DIR/daily-$TIMESTAMP"

# Backup all .img files
for img in "$VM_IMAGES_DIR"/*.img; do
    if [ -f "$img" ]; then
        filename=$(basename "$img")
        echo "Backing up $filename..."
        
        # Use rsync for efficient incremental backup
        rsync -avh "$img" "$BACKUP_DIR/daily-$TIMESTAMP/"
    fi
done

# Keep only last 7 daily backups
find "$BACKUP_DIR" -maxdepth 1 -type d -name "daily-*" | \
    sort -r | tail -n +8 | xargs rm -rf

echo "Backup complete: $BACKUP_DIR/daily-$TIMESTAMP"
EOF

chmod +x ~/lab-boot-init-fs/scripts/backup-lab.sh

# Schedule daily backup (cron)
(crontab -l 2>/dev/null; echo "0 2 * * * $HOME/lab-boot-init-fs/scripts/backup-lab.sh") | \
    crontab -
```

---

## 9. Lab Automation & Scripting

### 9.1 VM Creation Automation Script

```bash
# Automate VM creation from Kali host

cat > ~/lab-boot-init-fs/scripts/create-lab-vm.sh << 'EOF'
#!/bin/bash
# Create lab VM automatically

set -e

VM_NAME=$1
DISK_SIZE=${2:-50}  # GB
ISO_FILE=$3

if [ -z "$VM_NAME" ] || [ -z "$ISO_FILE" ]; then
    echo "Usage: $0 <vm-name> [disk-size-gb] <iso-file>"
    exit 1
fi

DISK_PATH="$HOME/lab-boot-init-fs/vm-images/${VM_NAME}.qcow2"

echo "Creating VM: $VM_NAME"
echo "  Disk size: ${DISK_SIZE}GB"
echo "  Disk path: $DISK_PATH"
echo "  ISO: $ISO_FILE"

# Create QCOW2 disk (if using KVM)
if command -v qemu-img &>/dev/null; then
    qemu-img create -f qcow2 "$DISK_PATH" "${DISK_SIZE}G"
fi

# Create VirtualBox VM (if using VirtualBox)
if command -v vboxmanage &>/dev/null; then
    vboxmanage createvm \
        --name "$VM_NAME" \
        --ostype Linux_64 \
        --register
    
    vboxmanage modifyvm "$VM_NAME" \
        --memory 8192 \
        --cpus 4 \
        --vram 256
    
    vboxmanage createhd \
        --filename "$DISK_PATH" \
        --size $((DISK_SIZE * 1024))
    
    vboxmanage storagectl "$VM_NAME" --name "SATA" --add sata
    vboxmanage storageattach "$VM_NAME" \
        --storagectl "SATA" \
        --port 0 \
        --device 0 \
        --type hdd \
        --medium "$DISK_PATH"
    
    vboxmanage storagectl "$VM_NAME" --name "IDE" --add ide
    vboxmanage storageattach "$VM_NAME" \
        --storagectl "IDE" \
        --port 0 \
        --device 0 \
        --type dvddrive \
        --medium "$ISO_FILE"
    
    echo "VM created. Start with:"
    echo "  vboxmanage startvm '$VM_NAME' --type gui"
fi

echo "VM setup complete!"
EOF

chmod +x ~/lab-boot-init-fs/scripts/create-lab-vm.sh

# Usage:
# ./scripts/create-lab-vm.sh "Systemd-Lab" 50 ~/lab-boot-init-fs/isos/ubuntu-22.04.iso
```

### 9.2 Quick Analysis Script Suite

```bash
# Bundle of quick analysis commands

cat > ~/lab-boot-init-fs/scripts/analyze-boot.sh << 'EOF'
#!/bin/bash
# Quick boot analysis

echo "=== BOOT ANALYSIS REPORT ==="
echo "Generated: $(date)"
echo ""

echo "=== Kernel Command Line ==="
cat /proc/cmdline
echo ""

echo "=== Init System ==="
stat /sbin/init /usr/lib/systemd/systemd-init 2>/dev/null | head -5
ps aux | head -2

echo ""
echo "=== Systemd Boot Timing ==="
systemd-analyze 2>/dev/null || echo "Systemd not available"

echo ""
echo "=== Mounted Filesystems ==="
mount | grep -v "tmpfs\|sysfs\|devpts"

echo ""
echo "=== Filesystem Usage ==="
df -h

echo ""
echo "=== Disk Partitions ==="
lsblk

echo ""
echo "=== Loaded Kernel Modules ==="
lsmod | head -10

echo ""
echo "=== Kernel Log (last 20 lines) ==="
dmesg | tail -20
EOF

chmod +x ~/lab-boot-init-fs/scripts/analyze-boot.sh
```

---

## 10. Experiment Workflows

### 10.1 Experiment: Analyzing Boot Process

```bash
# Complete workflow for analyzing boot process

# Step 1: Take VM snapshot (safe point)
vboxmanage snapshot "Kali-Boot-Lab-Systemd" take "Before-Boot-Analysis" \
    --description "Pre-analysis snapshot"

# Step 2: Boot VM and run analysis
# (SSH into VM or use VirtualBox console)

# Step 3: Capture boot timing
systemd-analyze > analysis/boot-timing-default.txt
systemd-analyze blame > analysis/boot-blame.txt
systemd-analyze plot > analysis/boot-graph.svg

# Step 4: Capture kernel parameters
cat /proc/cmdline > analysis/kernel-cmdline.txt

# Step 5: Examine initramfs
lsinitrd /boot/initrd* > analysis/initrd-contents.txt

# Step 6: Export logs
journalctl --boot > analysis/journal-boot.log
journalctl --boot --no-pager | grep -i "error\|fail\|warning" > \
    analysis/boot-errors.log

# Step 7: Copy analysis to Kali host
scp -r labuser@vm-ip:/tmp/analysis/* ~/lab-boot-init-fs/analysis/

# Step 8: Analyze on Kali
cd ~/lab-boot-init-fs/analysis/
cat boot-timing-default.txt
grep -i "failed" boot-errors.log

# Step 9: Document findings
cat >> README.md << 'EOF'

## Boot Analysis Results

- Default boot time: [from timing report]
- Critical path: [from critical-chain]
- Slowest services: [from blame report]
- Boot errors: [list any errors found]

EOF
```

### 10.2 Experiment: Init System Comparison

```bash
# Compare systemd vs SysV boot and behavior

# Part 1: Systemd system
vboxmanage snapshot "Kali-Boot-Lab-Systemd" take "Systemd-Analysis" \
    --description "Systemd analysis checkpoint"

# Collect systemd metrics
systemd-analyze > analysis/systemd-metrics.txt
systemd-analyze blame | head -20 > analysis/systemd-slowest-services.txt

# Part 2: SysV system
vboxmanage snapshot "Kali-Boot-Lab-SysV" take "SysV-Analysis" \
    --description "SysV analysis checkpoint"

# Collect SysV metrics
/etc/init.d/* --version 2>/dev/null | head -5 > analysis/sysv-version.txt
ls -la /etc/rc*.d/ | wc -l > analysis/sysv-service-count.txt

# Part 3: Compare
cat > analysis/init-comparison.md << 'EOF'
# Init System Comparison

## Systemd
- Boot time: [from metrics]
- Service dependencies: [auto-analyzed]
- Parallel startup: [yes/no]

## SysV
- Boot time: [measured]
- Service dependencies: [manual via runlevels]
- Parallel startup: [minimal]

## Differences
- Feature set:
- Boot speed:
- Configuration complexity:

EOF
```

### 10.3 Experiment: Filesystem Forensics

```bash
# Forensic analysis of filesystem image

# Step 1: Mount forensic copy (read-only)
sudo mount -o loop,ro ~/lab-boot-init-fs/vm-images/rootfs-systemd-clean.img \
    /mnt/forensic-analysis

# Step 2: Run forensic analysis
~/lab-boot-init-fs/scripts/fs-audit.sh /mnt/forensic-analysis > \
    analysis/fs-forensics.txt

# Step 3: Create timeline
python3 ~/lab-boot-init-fs/scripts/fs-timeline.py /mnt/forensic-analysis > \
    analysis/fs-timeline.csv

# Step 4: Check for anomalies
cat > analysis/fs-anomalies.txt << 'EOF'
# Filesystem Anomalies

World-writable files: [should be minimal]
Unexpected SETUID binaries: [audit closely]
Root files in /home: [security issue]
Modified system files: [potential tampering]

EOF

# Step 5: Analyze with sleuthkit (if available)
fls -r /mnt/forensic-analysis > analysis/file-listing.txt 2>/dev/null || true

# Step 6: Unmount
sudo umount /mnt/forensic-analysis
```

---

## 11. Troubleshooting & Recovery

### 11.1 Common Issues & Solutions

```bash
# Issue 1: VM won't boot

Symptoms: Black screen, kernel panic, or bootloader error
Solution:
  1. Boot from recovery ISO attached to VM
  2. Check /etc/fstab for errors
  3. Run fsck on root partition
  4. Check kernel parameters
  
Commands:
  fsck.ext4 /dev/sda1  # Check filesystem
  mount / -o remount,rw  # Remount as writable if needed
  cat /etc/fstab  # Check mount configuration

# Issue 2: Service won't start

Symptoms: systemctl start service returns error
Solution:
  1. Check service file syntax
  2. Check dependencies
  3. View service logs
  
Commands:
  systemctl status service-name  # Detailed status
  journalctl -u service-name     # View service logs
  systemd-analyze verify service-name.service  # Verify syntax

# Issue 3: Filesystem corruption

Symptoms: I/O errors, filesystem read-only
Solution:
  1. Don't force unmount; graceful shutdown better
  2. Use fsck (preferably from recovery ISO)
  3. Check SMART status if physical disk
  
Commands:
  sudo umount /mnt/point  # Graceful unmount
  sudo fsck -y /dev/sdXX  # Auto-repair (use with caution)
  smartctl -a /dev/sda    # Check disk health

# Issue 4: Permission denied errors

Symptoms: "Permission denied" on files/directories
Solution:
  1. Check file permissions
  2. Check UIDs/GIDs
  3. Check SELinux/AppArmor context
  
Commands:
  ls -la /path/to/file        # Check permissions
  stat /path/to/file          # Detailed inode info
  getenforce                  # Check SELinux status
  getfattr -d /path/to/file   # Check extended attrs
```

### 11.2 Revert to Snapshot

```bash
# If something breaks, revert to known-good snapshot

# List available snapshots
vboxmanage snapshot "Kali-Boot-Lab-Systemd" list

# Restore specific snapshot
vboxmanage snapshot "Kali-Boot-Lab-Systemd" restore "Fresh-Install"

# VM will revert to exact state at snapshot time
# All changes since snapshot are lost

# Delete snapshot (to save disk space)
vboxmanage snapshot "Kali-Boot-Lab-Systemd" delete "Old-Snapshot"
```

### 11.3 Recovery Procedures

```bash
# Boot from recovery ISO

1. In VirtualBox, select VM → Settings → Storage
2. Select IDE CD/DVD under Controller: IDE
3. Mount recovery ISO (systemrescue, GParted, etc.)
4. Boot VM (Shift key to see boot menu if needed)

# From recovery environment:
# Check filesystem
fsck.ext4 /dev/sda1

# Mount damaged filesystem
mount -o ro /dev/sda1 /mnt/

# Backup critical files
tar czf /tmp/backup.tar.gz /mnt/etc/ /mnt/var/

# Repair issues
mount -o remount,rw /dev/sda1 /mnt/
# Fix issues...
mount -o remount,ro /dev/sda1

# Reboot to original system
reboot
```

---

## Quick Reference

### VirtualBox Commands

```bash
# List VMs
vboxmanage list vms

# Start VM
vboxmanage startvm "VM-Name" --type headless

# Stop VM
vboxmanage controlvm "VM-Name" poweroff

# Take snapshot
vboxmanage snapshot "VM-Name" take "Snapshot-Name"

# Restore snapshot
vboxmanage snapshot "VM-Name" restore "Snapshot-Name"

# List snapshots
vboxmanage snapshot "VM-Name" list

# Delete VM
vboxmanage unregistervm "VM-Name" --delete
```

### Disk Image Commands

```bash
# Create sparse image
dd if=/dev/zero of=disk.img bs=1M count=1
dd if=/dev/zero of=disk.img bs=1M seek=19999 count=1

# Format with ext4
mkfs.ext4 disk.img

# Mount as loop device
sudo mount -o loop disk.img /mnt/

# Unmount
sudo umount /mnt/

# Copy entire disk
dd if=source.img of=backup.img bs=4M status=progress

# Compress image (for storage)
gzip -9 disk.img  # Creates disk.img.gz
gunzip disk.img.gz  # Restore

# Convert QCOW2 to IMG
qemu-img convert -f qcow2 -O raw disk.qcow2 disk.img
```

### Filesystem Analysis

```bash
# View filesystem
lsblk                          # Show all block devices
mount | column -t              # Show mounts nicely
df -h                          # Disk usage
du -sh *                       # Directory sizes

# Analyze filesystem
fsck -n /dev/sdXX             # Check (no repair)
e2fsck -n /dev/sdXX           # Extended check
tune2fs -l /dev/sdXX          # Show ext4 info

# Mount for analysis
sudo mount -o loop,ro disk.img /mnt/
find /mnt -type f -name "*.log" | head -20
strings /mnt/bin/ls | grep -i "error" | head -5
```

---

**Your Kali Boot, Init & Filesystem Lab is now ready for research and experimentation!** 🚀

Start with the VM setup, take snapshots regularly, and begin analyzing boot processes safely.
