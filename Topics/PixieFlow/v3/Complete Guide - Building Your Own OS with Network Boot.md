# Complete Guide: Building Your Own OS with Network Boot

## Table of Contents
1. [Overview: The Complete Picture](#overview)
2. [Boot Process Deep Dive](#boot-process)
3. [PXE/Network Boot Fundamentals](#pxe-fundamentals)
4. [Boot Loader Files Explained](#bootloader-files)
5. [Building Your Own OS from Scratch](#building-os)
6. [Creating initrd/initramfs](#creating-initrd)
7. [Filesystem Options: SquashFS](#squashfs)
8. [Complete Network Boot Setup](#complete-setup)
9. [UEFI vs BIOS Boot](#uefi-bios)
10. [Testing and Debugging](#testing)
11. [Advanced Topics](#advanced)

---

## 1. Overview: The Complete Picture {#overview}

### What We're Building

```
[Target Machine] ──PXE──> [TFTP/HTTP Server] ──> Boot Files
                                                   ├─ pxelinux.0 (BIOS)
                                                   ├─ grubx64.efi (UEFI)
                                                   ├─ vmlinuz (kernel)
                                                   ├─ initrd.img
                                                   └─ filesystem.squashfs
```

### Complete Boot Flow

```
1. Machine Powers On
   └─> Firmware (BIOS/UEFI)
       └─> Network Boot ROM (PXE)
           ├─> DHCP Discovery (requests IP + boot info)
           │   Response: IP=192.168.1.100, TFTP=192.168.1.50, Bootfile=pxelinux.0
           │
           └─> TFTP Download bootfile
               │
               ├─ BIOS Mode: pxelinux.0
               │   └─> Loads modules (vesamenu.c32, ldlinux.c32, etc.)
               │       └─> Reads pxelinux.cfg/default
               │           └─> Displays boot menu
               │               └─> Downloads vmlinuz + initrd.img
               │                   └─> Boots kernel
               │
               └─ UEFI Mode: grubx64.efi
                   └─> Reads grub.cfg
                       └─> Downloads vmlinuz + initrd.img
                           └─> Boots kernel

2. Kernel Boots
   └─> Decompresses itself into memory
       └─> Extracts initrd into rootfs (RAM)
           └─> Executes /init from initrd
               └─> Init script:
                   ├─> Mount pseudo-filesystems (proc, sys, dev)
                   ├─> Load kernel modules
                   ├─> Configure network
                   ├─> Download/mount filesystem.squashfs (your OS)
                   └─> switch_root to squashfs, exec /sbin/init

3. Your OS Starts
   └─> Your init system takes over
       └─> Start services, display login, etc.
```

---

## 2. Boot Process Deep Dive {#boot-process}

### Stage 1: Firmware (BIOS/UEFI)

**BIOS Legacy:**
- Executes first bootable device
- Looks for PXE option ROM
- Simple, 16-bit real mode
- Uses TFTP for file transfer

**UEFI Modern:**
- Full pre-boot environment
- HTTP(S) support in addition to TFTP
- Secure Boot support
- 64-bit, more complex

### Stage 2: PXE (Preboot eXecution Environment)

PXE is a standardized way to boot from network:

```
Client                          DHCP Server              TFTP Server
  |                                  |                       |
  |---DHCP DISCOVER (broadcast)----->|                       |
  |                                  |                       |
  |<--DHCP OFFER (IP + boot info)----|                       |
  |   - Your IP: 192.168.1.100       |                       |
  |   - Server IP: 192.168.1.50      |                       |
  |   - Boot filename: pxelinux.0    |                       |
  |                                  |                       |
  |---DHCP REQUEST------------------>|                       |
  |<--DHCP ACK-----------------------|                       |
  |                                  |                       |
  |---TFTP RRQ pxelinux.0---------------------------->|      |
  |<--TFTP DATA (pxelinux.0 binary)-------------------|      |
  |                                  |                       |
  [Execute pxelinux.0]               |                       |
```

### Stage 3: Boot Loader (SYSLINUX/GRUB)

The bootloader:
1. Provides a menu interface (optional)
2. Allows selection of different kernels/options
3. Loads kernel + initrd into memory
4. Passes control to kernel with boot parameters

### Stage 4: Kernel + initrd

The kernel:
1. Initializes hardware
2. Extracts initrd to memory
3. Mounts it as temporary root
4. Executes /init

### Stage 5: Your OS

Your init script transitions to the real OS filesystem.

---

## 3. PXE/Network Boot Fundamentals {#pxe-fundamentals}

### DHCP Server Configuration

**ISC DHCP (dhcpd.conf):**
```conf
# /etc/dhcp/dhcpd.conf
default-lease-time 600;
max-lease-time 7200;
authoritative;

subnet 192.168.1.0 netmask 255.255.255.0 {
    range 192.168.1.100 192.168.1.200;
    option routers 192.168.1.1;
    option domain-name-servers 8.8.8.8;
    
    # PXE Boot options
    next-server 192.168.1.50;  # TFTP server IP
    
    # BIOS clients
    if exists user-class and option user-class = "iPXE" {
        filename "http://192.168.1.50/boot.ipxe";
    } elsif option architecture-type = 00:00 {
        filename "pxelinux.0";  # BIOS
    }
    # UEFI clients
    elsif option architecture-type = 00:07 {
        filename "grubx64.efi";  # UEFI 64-bit
    }
    elsif option architecture-type = 00:09 {
        filename "grubx64.efi";  # UEFI 64-bit alternative
    }
}
```

**dnsmasq (simpler alternative):**
```conf
# /etc/dnsmasq.conf
interface=eth0
dhcp-range=192.168.1.100,192.168.1.200,12h
dhcp-boot=pxelinux.0,,192.168.1.50

# UEFI support
dhcp-match=set:efi-x86_64,option:client-arch,7
dhcp-boot=tag:efi-x86_64,grubx64.efi

# TFTP server
enable-tftp
tftp-root=/var/lib/tftpboot
```

### TFTP Server Setup

```bash
# Install TFTP server
apt-get install tftpd-hpa

# Configure
cat > /etc/default/tftpd-hpa << EOF
TFTP_USERNAME="tftp"
TFTP_DIRECTORY="/var/lib/tftpboot"
TFTP_ADDRESS="0.0.0.0:69"
TFTP_OPTIONS="--secure --verbose"
EOF

# Restart service
systemctl restart tftpd-hpa

# Set permissions
chmod -R 755 /var/lib/tftpboot
chown -R tftp:tftp /var/lib/tftpboot
```

### HTTP Server (Optional but Faster)

TFTP is slow (512 byte blocks). HTTP is much faster for large files.

```bash
# Install nginx
apt-get install nginx

# Create boot directory
mkdir -p /var/www/html/boot

# Configure nginx
cat > /etc/nginx/sites-available/netboot << 'EOF'
server {
    listen 80;
    root /var/www/html;
    
    location /boot {
        autoindex on;
        # Allow range requests for large files
        add_header Accept-Ranges bytes;
    }
}
EOF

ln -s /etc/nginx/sites-available/netboot /etc/nginx/sites-enabled/
systemctl restart nginx
```

---

## 4. Boot Loader Files Explained {#bootloader-files}

### SYSLINUX/PXELINUX (BIOS Boot)

#### pxelinux.0
**What it is:** The core PXE boot loader for BIOS systems.

**Function:**
- First file downloaded by PXE firmware
- Tiny bootloader (~26KB) written in assembly
- Provides basic boot functionality
- Loads configuration and additional modules

**Technical Details:**
```
Size: ~26KB
Format: x86 16-bit real mode executable
Location: /var/lib/tftpboot/pxelinux.0
Source: Part of SYSLINUX package
```

**How it works:**
1. PXE firmware loads it into memory at 0x7C00
2. Relocates itself to high memory
3. Initializes basic drivers (network, TFTP)
4. Searches for configuration file
5. Loads additional modules as needed

**Configuration Search Path:**
```
pxelinux.0 searches for config in this order:
1. pxelinux.cfg/<client-UUID>
2. pxelinux.cfg/01-<MAC-address>  (e.g., 01-88-99-aa-bb-cc-dd)
3. pxelinux.cfg/<IP-in-hex>       (e.g., C0A80164 for 192.168.1.100)
4. pxelinux.cfg/<IP-in-hex-minus-last-digit>
5. ... (continues removing digits)
6. pxelinux.cfg/default           (final fallback)
```

#### ldlinux.c32
**What it is:** Core library module for SYSLINUX.

**Function:**
- Essential runtime library
- Provides core API functions
- Must be present for SYSLINUX to work
- All other .c32 modules depend on it

**Technical Details:**
```
Size: ~115KB
Format: COM32 (SYSLINUX module format)
Dependencies: None (it's the base)
Required: YES - pxelinux.0 needs this
```

**Automatically loaded by:** pxelinux.0 during initialization

#### libcom32.c32
**What it is:** Standard C library for COM32 modules.

**Function:**
- Provides standard C functions (printf, malloc, etc.)
- Used by other complex modules
- Contains file I/O, memory management, string functions

**Technical Details:**
```
Size: ~167KB
Format: COM32 module
Dependencies: ldlinux.c32
Required: Only if other modules need C library functions
```

#### libutil.c32
**What it is:** Utility functions library.

**Function:**
- Provides common utility functions
- String parsing, configuration handling
- Used by menu systems

**Technical Details:**
```
Size: ~24KB
Format: COM32 module
Dependencies: ldlinux.c32, libcom32.c32
Required: Only if menu modules need it
```

#### vesamenu.c32
**What it is:** Graphical boot menu system.

**Function:**
- Provides a colorful, graphical boot menu
- Uses VESA graphics modes
- Supports backgrounds, colors, borders
- Better looking than text-only menu

**Technical Details:**
```
Size: ~27KB
Format: COM32 module
Dependencies: ldlinux.c32, libcom32.c32, libutil.c32
Alternative: menu.c32 (text-only, simpler)
```

**Features:**
- Graphical interface with VGA colors
- Customizable appearance (backgrounds, colors)
- Keyboard navigation
- Timeout support
- Password protection

**Configuration Example:**
```
UI vesamenu.c32
MENU TITLE My Custom OS Boot Menu
MENU BACKGROUND splash.png
MENU COLOR screen 37;40 #80ffffff #00000000 std

LABEL myos
    MENU LABEL My Custom OS
    KERNEL vmlinuz
    APPEND initrd=initrd.img boot=live
```

#### Complete Module Dependencies
```
pxelinux.0 (bootloader core)
    └─> ldlinux.c32 (required, auto-loaded)
        ├─> libcom32.c32 (if using advanced modules)
        │   └─> libutil.c32 (if using menus)
        │       └─> vesamenu.c32 (graphical menu)
        └─> Other modules:
            ├─> menu.c32 (text menu)
            ├─> chain.c32 (chainload other bootloaders)
            ├─> reboot.c32 (reboot system)
            └─> poweroff.c32 (power off system)
```

### GRUB (UEFI Boot)

#### grubx64.efi
**What it is:** GRUB2 bootloader compiled as UEFI application.

**Function:**
- Full-featured bootloader for UEFI systems
- Supports complex configurations
- Can boot Linux, Windows, other OS
- Includes filesystem drivers (ext4, xfs, etc.)

**Technical Details:**
```
Size: ~1.2MB (much larger than pxelinux.0)
Format: EFI PE32+ executable
Location: /var/lib/tftpboot/grubx64.efi
Architecture: x86_64 UEFI
```

**How it works:**
1. UEFI firmware loads grubx64.efi
2. GRUB initializes in UEFI mode
3. Reads grub.cfg configuration
4. Can access local disks with filesystem drivers
5. Loads kernel + initrd
6. Executes via UEFI boot services

**Configuration File (grub.cfg):**
```bash
# /var/lib/tftpboot/grub.cfg
set timeout=5
set default=0

menuentry "My Custom OS" {
    echo "Loading kernel..."
    linux (tftp)/vmlinuz boot=live
    echo "Loading initrd..."
    initrd (tftp)/initrd.img
    boot
}

menuentry "My Custom OS (Debug)" {
    linux (tftp)/vmlinuz boot=live debug
    initrd (tftp)/initrd.img
    boot
}
```

**Building grubx64.efi:**
```bash
# Install GRUB tools
apt-get install grub-efi-amd64

# Create GRUB image with network support
grub-mkimage -d /usr/lib/grub/x86_64-efi \
    -O x86_64-efi \
    -o grubx64.efi \
    -p '(tftp)/grub' \
    normal tftp net efinet efi_gop efi_uga all_video boot linux

# Modules included:
# - tftp: TFTP client
# - net, efinet: Network stack
# - efi_gop, efi_uga: Graphics
# - boot, linux: Linux boot support
```

### Configuration Files

#### default (PXELINUX config)
**What it is:** Main configuration file for PXELINUX.

**Location:** `/var/lib/tftpboot/pxelinux.cfg/default`

**Complete Example:**
```
# Timeout in 1/10 seconds (50 = 5 seconds)
TIMEOUT 50
DEFAULT vesamenu.c32

# Prompt for manual entry
PROMPT 0

# Menu configuration
MENU TITLE === My Custom OS Network Boot ===
MENU BACKGROUND splash.png
MENU COLOR screen 37;40 #80ffffff #00000000 std
MENU COLOR border 30;44 #ffffffff #00000000 std
MENU COLOR title 1;36;44 #ff00ffff #00000000 std
MENU COLOR sel 7;37;40 #e0000000 #20ff8000 all
MENU COLOR unsel 37;44 #50ffffff #00000000 std

# Boot entries
LABEL myos
    MENU LABEL ^1) My Custom OS (Standard)
    MENU DEFAULT
    KERNEL vmlinuz
    APPEND initrd=initrd.img boot=live root=/dev/nfs nfsroot=192.168.1.50:/export/root ip=dhcp quiet splash

LABEL myos-debug
    MENU LABEL ^2) My Custom OS (Debug Mode)
    KERNEL vmlinuz
    APPEND initrd=initrd.img boot=live root=/dev/nfs nfsroot=192.168.1.50:/export/root ip=dhcp debug nosplash console=tty0 console=ttyS0,115200n8

LABEL myos-safe
    MENU LABEL ^3) My Custom OS (Safe Mode)
    KERNEL vmlinuz
    APPEND initrd=initrd.img boot=live root=/dev/nfs nfsroot=192.168.1.50:/export/root ip=dhcp nomodeset

LABEL memtest
    MENU LABEL ^4) Memory Test
    KERNEL memtest86+.bin

LABEL local
    MENU LABEL ^5) Boot from Local Disk
    LOCALBOOT 0

# Advanced options submenu
MENU BEGIN advanced
    MENU TITLE Advanced Options
    
    LABEL mainmenu
        MENU LABEL Return to Main Menu
        MENU EXIT
    
    LABEL shell
        MENU LABEL Drop to PXELINUX Shell
        COM32 shell.c32
    
    LABEL reboot
        MENU LABEL Reboot System
        COM32 reboot.c32
    
    LABEL poweroff
        MENU LABEL Power Off System
        COM32 poweroff.c32
MENU END
```

**Directives Explained:**
```
TIMEOUT <n>        - Wait n/10 seconds before auto-boot
DEFAULT <label>    - Default boot entry or menu system
PROMPT <0|1>       - Show boot: prompt (0=no, 1=yes)
LABEL <name>       - Defines a boot entry
KERNEL <file>      - Kernel or module to load
APPEND <options>   - Kernel command line parameters
MENU LABEL <text>  - Display name in menu
MENU DEFAULT       - This is the default selection
LOCALBOOT <n>      - Boot from local disk (0=first HDD)
COM32 <module>     - Load a COM32 module
MENU BEGIN/END     - Create a submenu
```

---

## 5. Building Your Own OS from Scratch {#building-os}

### Minimal OS Components

```
Your OS needs:
1. Kernel (Linux or custom)
2. Init system (systemd, sysvinit, or custom)
3. Shell (bash, busybox)
4. Core utilities (coreutils or busybox)
5. Libraries (glibc or musl)
6. Device management (udev or static /dev)
7. Optional: Network manager, package manager, etc.
```

### Approach 1: Linux From Scratch (LFS)

**Full manual build:**
```bash
# This is a 200+ step process
# Key phases:

# 1. Bootstrap toolchain
#    - Build cross-compiler
#    - Build binutils, gcc, glibc

# 2. Build base system
#    - Linux kernel
#    - Core utilities
#    - Init system

# 3. Configure system
#    - Boot scripts
#    - Network configuration
#    - User accounts
```

### Approach 2: Buildroot (Automated)

**Much faster, reproducible:**
```bash
# Install Buildroot
git clone https://github.com/buildroot/buildroot.git
cd buildroot

# Configure
make menuconfig
# Select:
# - Target architecture: x86_64
# - Toolchain options
# - System configuration
# - Kernel: Linux
# - Filesystem: squashfs

# Build (takes 1-2 hours)
make

# Output will be in:
# output/images/
#   ├── rootfs.squashfs
#   ├── bzImage (kernel)
#   └── rootfs.tar
```

### Approach 3: Debootstrap (Debian-based)

**Create Debian-based minimal system:**
```bash
#!/bin/bash
# Build a minimal Debian-based OS

TARGET="/tmp/myos"
RELEASE="bookworm"

# Install debootstrap
apt-get install debootstrap squashfs-tools

# Create base system
mkdir -p $TARGET
debootstrap --arch=amd64 --variant=minbase $RELEASE $TARGET

# Chroot and customize
chroot $TARGET /bin/bash << 'CHROOT_EOF'

# Set root password
echo "root:mypassword" | chpasswd

# Install kernel
apt-get update
apt-get install -y linux-image-amd64

# Install essential packages
apt-get install -y \
    systemd \
    systemd-sysv \
    network-manager \
    openssh-server \
    vim \
    less \
    iproute2 \
    iputils-ping

# Configure network
cat > /etc/systemd/network/20-wired.network << EOF
[Match]
Name=en*

[Network]
DHCP=yes
EOF

systemctl enable systemd-networkd

# Configure SSH
systemctl enable ssh

# Cleanup
apt-get clean
rm -rf /var/lib/apt/lists/*

CHROOT_EOF

# Copy kernel out
cp $TARGET/boot/vmlinuz-* /var/lib/tftpboot/vmlinuz

# Create squashfs
mksquashfs $TARGET /var/lib/tftpboot/filesystem.squashfs -comp xz -b 1M
```

### Approach 4: Custom Minimal OS

**Truly minimal (10-50MB):**
```bash
#!/bin/bash
# Build tiny custom OS with busybox

ROOTFS="/tmp/tiny-os"
mkdir -p $ROOTFS/{bin,sbin,etc,proc,sys,dev,lib,lib64,usr,root,tmp,var}

# Get busybox (provides most utilities)
cd /tmp
wget https://busybox.net/downloads/binaries/1.35.0-x86_64-linux-musl/busybox
chmod +x busybox
mv busybox $ROOTFS/bin/

# Create symlinks for all utilities
chroot $ROOTFS /bin/busybox --install -s

# Create init system
cat > $ROOTFS/sbin/init << 'EOF'
#!/bin/sh
# Minimal init script

# Mount pseudo-filesystems
mount -t proc proc /proc
mount -t sysfs sysfs /sys
mount -t devtmpfs devtmpfs /dev

# Set hostname
hostname myos

# Configure network
ip link set lo up
ip link set eth0 up
udhcpc -i eth0

# Start services
# ... add your services here ...

# Drop to shell
exec /bin/sh
EOF

chmod +x $ROOTFS/sbin/init

# Create fstab
cat > $ROOTFS/etc/fstab << EOF
proc  /proc  proc  defaults  0 0
sysfs /sys   sysfs defaults  0 0
EOF

# Copy necessary libraries (if not using static busybox)
# ldd $ROOTFS/bin/busybox will show what's needed

# Create squashfs
mksquashfs $ROOTFS filesystem.squashfs -comp xz
```

---

## 6. Creating initrd/initramfs {#creating-initrd}

### Purpose of initrd in Network Boot

For network boot, initrd must:
1. Initialize network drivers
2. Configure network (DHCP or static)
3. Download the actual OS filesystem (squashfs)
4. Mount it and switch to it

### Complete initrd Build Script

```bash
#!/bin/bash
# build-netboot-initrd.sh

set -e

INITRD_DIR="initrd-work"
KERNEL_VER=$(uname -r)
OUTPUT="netboot-initrd.img"

echo "Building network boot initrd..."

# Clean and create structure
rm -rf $INITRD_DIR
mkdir -p $INITRD_DIR/{bin,sbin,etc,lib,lib64,proc,sys,dev,run,newroot,tmp}

# Install busybox (static binary recommended)
cp /bin/busybox $INITRD_DIR/bin/
cd $INITRD_DIR/bin
for cmd in sh mount umount ip cat ls grep sed awk cut tr \
           mkdir rmdir mknod sleep echo test [ wget; do
    ln -sf busybox $cmd
done
cd ../..

# Copy essential tools
cp /sbin/switch_root $INITRD_DIR/sbin/
cp /sbin/modprobe $INITRD_DIR/sbin/
cp /sbin/depmod $INITRD_DIR/sbin/

# Copy libraries (if not using static busybox)
mkdir -p $INITRD_DIR/lib/x86_64-linux-gnu
cp -P /lib/x86_64-linux-gnu/libc.so* $INITRD_DIR/lib/x86_64-linux-gnu/
cp -P /lib/x86_64-linux-gnu/libm.so* $INITRD_DIR/lib/x86_64-linux-gnu/
cp -P /lib/x86_64-linux-gnu/libpthread.so* $INITRD_DIR/lib/x86_64-linux-gnu/
cp -P /lib64/ld-linux-x86-64.so* $INITRD_DIR/lib64/

# Copy kernel modules (network + filesystem)
mkdir -p $INITRD_DIR/lib/modules/$KERNEL_VER
MODULES_SRC="/lib/modules/$KERNEL_VER"

# Network drivers
cp -r $MODULES_SRC/kernel/drivers/net $INITRD_DIR/lib/modules/$KERNEL_VER/kernel/

# Filesystem support (squashfs, NFS, overlay)
mkdir -p $INITRD_DIR/lib/modules/$KERNEL_VER/kernel/fs
cp -r $MODULES_SRC/kernel/fs/{squashfs,nfs,nfs_common,lockd,overlayfs} \
   $INITRD_DIR/lib/modules/$KERNEL_VER/kernel/fs/ 2>/dev/null || true

# Generate module dependencies
depmod -b $INITRD_DIR $KERNEL_VER

# Create device nodes
mknod -m 600 $INITRD_DIR/dev/console c 5 1
mknod -m 666 $INITRD_DIR/dev/null c 1 3
mknod -m 666 $INITRD_DIR/dev/zero c 1 5
mknod -m 644 $INITRD_DIR/dev/random c 1 8
mknod -m 644 $INITRD_DIR/dev/urandom c 1 9
mknod -m 666 $INITRD_DIR/dev/tty c 5 0

# Create init script
cat > $INITRD_DIR/init << 'INIT_SCRIPT'
#!/bin/sh
# Network boot init script

export PATH=/bin:/sbin:/usr/bin:/usr/sbin

# Mount pseudo-filesystems
mount -t proc proc /proc
mount -t sysfs sysfs /sys
mount -t devtmpfs devtmpfs /dev
mkdir -p /dev/pts /dev/shm
mount -t devpts devpts /dev/pts
mount -t tmpfs tmpfs /dev/shm

echo "=== Network Boot Init ==="
echo "Starting network configuration..."

# Parse kernel command line
ROOT_URL=""
DEBUG=0
OVERLAYFS=0

for param in $(cat /proc/cmdline); do
    case "$param" in
        root=*)
            ROOT_URL="${param#root=}"
            ;;
        debug)
            DEBUG=1
            ;;
        overlay)
            OVERLAYFS=1
            ;;
    esac
done

# Debug shell
if [ "$DEBUG" = "1" ]; then
    echo "Debug mode - dropping to shell"
    echo "Type 'exit' to continue boot"
    /bin/sh
fi

# Load network modules
echo "Loading network drivers..."
modprobe e1000 2>/dev/null || true
modprobe e1000e 2>/dev/null || true
modprobe virtio_net 2>/dev/null || true
modprobe 8139too 2>/dev/null || true

# Wait for network interfaces
sleep 2

# Find first network interface
IFACE=$(ip -o link show | awk -F': ' '{print $2}' | grep -v lo | head -1)
echo "Using network interface: $IFACE"

# Configure network (DHCP)
echo "Configuring network via DHCP..."
ip link set $IFACE up
udhcpc -i $IFACE -n -q

# Wait for network
echo "Waiting for network connectivity..."
for i in $(seq 1 30); do
    if ip route get 8.8.8.8 >/dev/null 2>&1; then
        echo "Network is up!"
        break
    fi
    sleep 1
done

# Download and mount root filesystem
echo "Root URL: $ROOT_URL"

if [ -z "$ROOT_URL" ]; then
    echo "ERROR: No root= parameter specified"
    echo "Example: root=http://192.168.1.50/filesystem.squashfs"
    /bin/sh
fi

case "$ROOT_URL" in
    http://*|https://*)
        # Download squashfs from HTTP
        echo "Downloading filesystem from $ROOT_URL ..."
        wget -O /tmp/filesystem.squashfs "$ROOT_URL"
        
        if [ $? -ne 0 ]; then
            echo "ERROR: Failed to download filesystem"
            /bin/sh
        fi
        
        # Mount squashfs
        modprobe squashfs
        mkdir -p /squashfs
        mount -t squashfs /tmp/filesystem.squashfs /squashfs
        
        if [ "$OVERLAYFS" = "1" ]; then
            # Use overlayfs for read-write
            echo "Setting up overlay filesystem..."
            modprobe overlay
            mkdir -p /overlay/upper /overlay/work
            mount -t tmpfs tmpfs /overlay
            mkdir -p /overlay/upper /overlay/work
            mount -t overlay overlay \
                -o lowerdir=/squashfs,upperdir=/overlay/upper,workdir=/overlay/work \
                /newroot
        else
            # Mount read-only
            mount --bind /squashfs /newroot
        fi
        ;;
        
    nfs:*)
        # Mount NFS directly
        NFS_PATH="${ROOT_URL#nfs:}"
        echo "Mounting NFS root: $NFS_PATH"
        modprobe nfs
        mount -t nfs -o nolock "$NFS_PATH" /newroot
        ;;
        
    *)
        echo "ERROR: Unsupported root URL: $ROOT_URL"
        echo "Supported: http://, https://, nfs:"
        /bin/sh
        ;;
esac

# Verify root filesystem
if [ ! -d "/newroot/bin" ] || [ ! -d "/newroot/sbin" ]; then
    echo "ERROR: Root filesystem doesn't look valid"
    echo "Contents of /newroot:"
    ls -la /newroot
    /bin/sh
fi

echo "Root filesystem mounted successfully"

# Move mounts to new root
echo "Preparing to switch root..."
mount --move /proc /newroot/proc
mount --move /sys /newroot/sys
mount --move /dev /newroot/dev

# Switch to new root
echo "Switching to new root filesystem..."
exec switch_root /newroot /sbin/init

# If we get here, something went wrong
echo "ERROR: switch_root failed!"
/bin/sh
INIT_SCRIPT

chmod +x $INITRD_DIR/init

# Package into cpio archive
echo "Creating initrd image..."
cd $INITRD_DIR
find . -print0 | cpio --null --create --format=newc | gzip -9 > ../$OUTPUT
cd ..

echo "Done! Created $OUTPUT"
ls -lh $OUTPUT
```

### Testing Your initrd

```bash
# Extract and inspect
mkdir test-initrd
cd test-initrd
zcat ../netboot-initrd.img | cpio -idmv

# Check init script
cat init

# Verify modules
ls -R lib/modules/

# Test in QEMU
qemu-system-x86_64 \
    -kernel /boot/vmlinuz-$(uname -r) \
    -initrd ../netboot-initrd.img \
    -append "console=ttyS0 debug root=http://192.168.1.50/filesystem.squashfs" \
    -nographic \
    -m 1G \
    -enable-kvm
```

---

## 7. Filesystem Options: SquashFS {#squashfs}

### What is SquashFS?

**SquashFS** is a compressed read-only filesystem:
- High compression (60-80% reduction)
- Fast random access
- Read-only (perfect for network boot)
- Used by LiveCDs, embedded systems

### Why SquashFS for Network Boot?

```
Advantages:
✓ Smaller download size (compressed)
✓ Reduced network traffic
✓ Read-only ensures consistency
✓ Fast decompression (in-memory)
✓ Can overlay with writable layer

Example sizes:
- Full Debian system: 2GB uncompressed
- SquashFS with xz:  600MB
- Download time:     10s vs 3 minutes
```

### Creating SquashFS

```bash
# Basic creation
mksquashfs /path/to/rootfs filesystem.squashfs

# With compression options
mksquashfs /path/to/rootfs filesystem.squashfs \
    -comp xz \           # Compression: xz (best), gzip (fast), lzo (fastest)
    -b 1M \              # Block size (larger = better compression)
    -Xdict-size 100% \   # XZ dictionary size
    -no-xattrs           # Skip extended attributes

# Exclude files
mksquashfs /path/to/rootfs filesystem.squashfs \
    -e /path/to/rootfs/tmp/* \
    -e /path/to/rootfs/var/cache/* \
    -e /path/to/rootfs/var/log/*

# View contents without mounting
unsquashfs -ll filesystem.squashfs

# Extract
unsquashfs filesystem.squashfs
```

### Mounting SquashFS

```bash
# In your OS or initrd
mount -t squashfs /path/to/filesystem.squashfs /mnt

# With loop device
losetup /dev/loop0 filesystem.squashfs
mount -t squashfs /dev/loop0 /mnt

# In kernel cmdline
root=/dev/squashfs0 squashfs=/path/to/filesystem.squashfs
```

### OverlayFS: Making SquashFS Writable

```bash
# Create overlay
mkdir -p /overlay/{upper,work}
mount -t tmpfs tmpfs /overlay

# Mount squashfs as lower (read-only)
mount -t squashfs filesystem.squashfs /lower

# Create overlay (appears writable)
mount -t overlay overlay \
    -o lowerdir=/lower,upperdir=/overlay/upper,workdir=/overlay/work \
    /merged

# Now /merged is read-write!
# - Reads come from /lower (squashfs)
# - Writes go to /overlay/upper (RAM)
# - Changes lost on reboot (unless you save them)
```

### Persistent Overlay

```bash
# Save changes to network
cat > /etc/rc.local << 'EOF'
#!/bin/sh
# On shutdown, save overlay to server
save_overlay() {
    tar -czf /tmp/overlay.tar.gz -C /overlay/upper .
    curl -X POST --data-binary @/tmp/overlay.tar.gz \
        http://192.168.1.50/save-overlay/$(hostname)
}

trap save_overlay EXIT TERM
EOF

# On next boot, restore
wget http://192.168.1.50/overlay/$(hostname).tar.gz -O /tmp/overlay.tar.gz
tar -xzf /tmp/overlay.tar.gz -C /overlay/upper
```

### Comparison: SquashFS vs Other Options

```
┌─────────────┬──────────────┬─────────────┬────────────┬───────────┐
│ Filesystem  │ Compression  │ Read-Write  │ Use Case   │ Size      │
├─────────────┼──────────────┼─────────────┼────────────┼───────────┤
│ SquashFS    │ Yes (high)   │ No          │ Network    │ Smallest  │
│             │              │             │ boot       │           │
├─────────────┼──────────────┼─────────────┼────────────┼───────────┤
│ ext4        │ No           │ Yes         │ Normal     │ Largest   │
│             │              │             │ install    │           │
├─────────────┼──────────────┼─────────────┼────────────┼───────────┤
│ OverlayFS   │ No           │ Yes         │ Network    │ RAM-based │
│             │              │             │ boot RW    │           │
├─────────────┼──────────────┼─────────────┼────────────┼───────────┤
│ NFS         │ No           │ Yes         │ Network    │ N/A       │
│             │              │             │ boot       │ (server)  │
└─────────────┴──────────────┴─────────────┴────────────┴───────────┘
```

---

## 8. Complete Network Boot Setup {#complete-setup}

### Server Setup - Complete Script

```bash
#!/bin/bash
# setup-netboot-server.sh
# Complete network boot server setup

set -e

SERVER_IP="192.168.1.50"
TFTP_ROOT="/var/lib/tftpboot"
HTTP_ROOT="/var/www/html/boot"
NFS_ROOT="/export/netboot"

echo "=== Setting up Network Boot Server ==="

# Install required packages
echo "Installing packages..."
apt-get update
apt-get install -y \
    dnsmasq \
    nginx \
    nfs-kernel-server \
    syslinux-common \
    pxelinux \
    grub-efi-amd64 \
    squashfs-tools

# Create directories
mkdir -p $TFTP_ROOT/{pxelinux.cfg,grub}
mkdir -p $HTTP_ROOT
mkdir -p $NFS_ROOT

# Configure dnsmasq (DHCP + TFTP)
cat > /etc/dnsmasq.conf << EOF
# Interface to listen on
interface=eth0
bind-interfaces

# DHCP range
dhcp-range=192.168.1.100,192.168.1.200,12h

# Gateway
dhcp-option=3,192.168.1.1

# DNS
dhcp-option=6,8.8.8.8,8.8.4.4

# TFTP server
enable-tftp
tftp-root=$TFTP_ROOT

# PXE boot files
dhcp-match=set:bios,option:client-arch,0
dhcp-boot=tag:bios,pxelinux.0

dhcp-match=set:efi64,option:client-arch,7
dhcp-boot=tag:efi64,grubx64.efi

dhcp-match=set:efi64,option:client-arch,9
dhcp-boot=tag:efi64,grubx64.efi

# Logging
log-dhcp
log-queries
EOF

# Copy PXELINUX files
echo "Copying PXELINUX files..."
cp /usr/lib/PXELINUX/pxelinux.0 $TFTP_ROOT/
cp /usr/lib/syslinux/modules/bios/{ldlinux.c32,libcom32.c32,libutil.c32,vesamenu.c32,menu.c32,reboot.c32,poweroff.c32} $TFTP_ROOT/

# Create PXELINUX config
cat > $TFTP_ROOT/pxelinux.cfg/default << 'EOF'
DEFAULT vesamenu.c32
TIMEOUT 50
PROMPT 0

MENU TITLE Network Boot Server
MENU BACKGROUND
MENU COLOR screen 37;40 #80ffffff #00000000 std
MENU COLOR border 30;44 #ffffffff #00000000 std
MENU COLOR title 1;36;44 #ff00ffff #00000000 std
MENU COLOR sel 7;37;40 #e0ffffff #20ff8000 all
MENU COLOR unsel 37;44 #50ffffff #00000000 std
MENU COLOR hotkey 1;37;44 #ffffffff #00000000 std
MENU COLOR hotsel 1;7;37;40 #e0400000 #20ff8000 all

LABEL myos
    MENU LABEL ^1. Boot My Custom OS
    MENU DEFAULT
    KERNEL vmlinuz
    APPEND initrd=initrd.img root=http://192.168.1.50/boot/filesystem.squashfs overlay quiet splash

LABEL myos-debug
    MENU LABEL ^2. Boot My Custom OS (Debug)
    KERNEL vmlinuz
    APPEND initrd=initrd.img root=http://192.168.1.50/boot/filesystem.squashfs overlay debug

LABEL myos-nfs
    MENU LABEL ^3. Boot My Custom OS (NFS Root)
    KERNEL vmlinuz
    APPEND initrd=initrd.img root=nfs:192.168.1.50:/export/netboot ip=dhcp

LABEL local
    MENU LABEL ^4. Boot from Local Disk
    LOCALBOOT 0

MENU SEPARATOR

LABEL reboot
    MENU LABEL ^R. Reboot
    COM32 reboot.c32

LABEL poweroff
    MENU LABEL ^P. Power Off
    COM32 poweroff.c32
EOF

# Setup GRUB for UEFI
echo "Setting up GRUB for UEFI..."
grub-mkimage \
    -d /usr/lib/grub/x86_64-efi \
    -O x86_64-efi \
    -o $TFTP_ROOT/grubx64.efi \
    -p "(tftp)/grub" \
    normal tftp net efinet efi_gop efi_uga all_video boot linux configfile echo

# Create GRUB config
cat > $TFTP_ROOT/grub/grub.cfg << 'EOF'
set timeout=5
set default=0

menuentry "My Custom OS" {
    echo "Loading kernel..."
    linux (tftp)/vmlinuz root=http://192.168.1.50/boot/filesystem.squashfs overlay quiet splash
    echo "Loading initrd..."
    initrd (tftp)/initrd.img
}

menuentry "My Custom OS (Debug)" {
    linux (tftp)/vmlinuz root=http://192.168.1.50/boot/filesystem.squashfs overlay debug
    initrd (tftp)/initrd.img
}

menuentry "My Custom OS (NFS)" {
    linux (tftp)/vmlinuz root=nfs:192.168.1.50:/export/netboot ip=dhcp
    initrd (tftp)/initrd.img
}
EOF

# Configure nginx for HTTP boot
cat > /etc/nginx/sites-available/netboot << 'EOF'
server {
    listen 80;
    root /var/www/html;
    
    location /boot {
        autoindex on;
        add_header Cache-Control "public, max-age=3600";
        add_header Accept-Ranges bytes;
    }
}
EOF

ln -sf /etc/nginx/sites-available/netboot /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Configure NFS
cat > /etc/exports << EOF
$NFS_ROOT 192.168.1.0/24(ro,sync,no_subtree_check,no_root_squash)
EOF

# Set permissions
chmod -R 755 $TFTP_ROOT
chmod -R 755 $HTTP_ROOT

# Restart services
echo "Starting services..."
systemctl restart dnsmasq
systemctl restart nginx
systemctl restart nfs-kernel-server

echo ""
echo "=== Network Boot Server Setup Complete ==="
echo ""
echo "Server IP: $SERVER_IP"
echo "TFTP Root: $TFTP_ROOT"
echo "HTTP Root: $HTTP_ROOT"
echo "NFS Root:  $NFS_ROOT"
echo ""
echo "Next steps:"
echo "1. Copy your kernel to: $TFTP_ROOT/vmlinuz"
echo "2. Copy your initrd to: $TFTP_ROOT/initrd.img"
echo "3. Copy your squashfs to: $HTTP_ROOT/filesystem.squashfs"
echo "4. Or copy your OS to: $NFS_ROOT/"
echo ""
echo "Services status:"
systemctl status dnsmasq --no-pager -l
systemctl status nginx --no-pager -l
systemctl status nfs-kernel-server --no-pager -l
```

### Building Your OS and Deploying

```bash
#!/bin/bash
# build-and-deploy-os.sh

SERVER_IP="192.168.1.50"
TFTP_ROOT="/var/lib/tftpboot"
HTTP_ROOT="/var/www/html/boot"

echo "=== Building Custom OS ==="

# Build OS using Buildroot
cd /tmp
git clone https://github.com/buildroot/buildroot.git
cd buildroot

# Configure (or use saved config)
make menuconfig
# Select: x86_64, squashfs, your packages

# Build
make -j$(nproc)

# Copy artifacts
echo "Deploying to server..."
cp output/images/bzImage $TFTP_ROOT/vmlinuz
echo "Kernel deployed"

# Build custom initrd
./build-netboot-initrd.sh
cp netboot-initrd.img $TFTP_ROOT/initrd.img
echo "Initrd deployed"

# Copy squashfs
cp output/images/rootfs.squashfs $HTTP_ROOT/filesystem.squashfs
echo "Filesystem deployed"

echo ""
echo "=== Deployment Complete ==="
echo "Clients can now network boot!"
```

### Client Testing

```bash
# Test with QEMU
qemu-system-x86_64 \
    -m 2G \
    -enable-kvm \
    -boot n \
    -netdev user,id=net0,tftp=$TFTP_ROOT,bootfile=pxelinux.0 \
    -device e1000,netdev=net0 \
    -serial stdio

# Or with real hardware:
# 1. Enter BIOS/UEFI
# 2. Enable Network Boot (PXE)
# 3. Set boot order: Network first
# 4. Save and reboot
```

---

## 9. UEFI vs BIOS Boot {#uefi-bios}

### Fundamental Differences

```
┌─────────────────┬──────────────────┬──────────────────┐
│ Feature         │ BIOS             │ UEFI             │
├─────────────────┼──────────────────┼──────────────────┤
│ Age             │ 1981             │ 2005+            │
├─────────────────┼──────────────────┼──────────────────┤
│ Boot Mode       │ 16-bit real mode │ 32/64-bit        │
├─────────────────┼──────────────────┼──────────────────┤
│ Boot Files      │ pxelinux.0       │ grubx64.efi      │
│                 │ (<26KB)          │ (~1.2MB)         │
├─────────────────┼──────────────────┼──────────────────┤
│ Config          │ pxelinux.cfg/    │ grub.cfg         │
│                 │ default          │                  │
├─────────────────┼──────────────────┼──────────────────┤
│ Protocols       │ TFTP only        │ TFTP, HTTP(S)    │
├─────────────────┼──────────────────┼──────────────────┤
│ Secure Boot     │ No               │ Yes              │
├─────────────────┼──────────────────┼──────────────────┤
│ Partition Size  │ 2TB max (MBR)    │ 9ZB (GPT)        │
└─────────────────┴──────────────────┴──────────────────┘
```

### Detecting Boot Mode

```bash
# On running system, check boot mode
[ -d /sys/firmware/efi ] && echo "UEFI" || echo "BIOS"

# In initrd, check
if [ -d /sys/firmware/efi ]; then
    echo "Booted via UEFI"
else
    echo "Booted via BIOS"
fi
```

### Supporting Both Modes

Your server should provide both:

```bash
# DHCP config for both
dhcp-match=set:bios,option:client-arch,0
dhcp-boot=tag:bios,pxelinux.0

dhcp-match=set:efi64,option:client-arch,7
dhcp-boot=tag:efi64,grubx64.efi

dhcp-match=set:efi64-alt,option:client-arch,9
dhcp-boot=tag:efi64-alt,grubx64.efi
```

### UEFI HTTP Boot

UEFI supports HTTP boot (faster than TFTP):

```bash
# GRUB config with HTTP
cat > grub.cfg << 'EOF'
set timeout=5

# HTTP boot
menuentry "My OS (HTTP)" {
    linux (http,192.168.1.50)/boot/vmlinuz root=http://192.168.1.50/boot/filesystem.squashfs
    initrd (http,192.168.1.50)/boot/initrd.img
}

# TFTP fallback
menuentry "My OS (TFTP)" {
    linux (tftp)/vmlinuz root=http://192.168.1.50/boot/filesystem.squashfs
    initrd (tftp)/initrd.img
}
EOF
```

### Secure Boot Considerations

For Secure Boot (UEFI only):
```bash
# Sign your kernel
sbsign --key DB.key --cert DB.crt --output vmlinuz.signed vmlinuz

# Sign GRUB
sbsign --key DB.key --cert DB.crt --output grubx64.efi.signed grubx64.efi

# Use shim (pre-signed bootloader)
# Most distros provide shim.efi signed by Microsoft
cp /usr/lib/shim/shimx64.efi.signed $TFTP_ROOT/bootx64.efi
```

---

## 10. Testing and Debugging {#testing}

### Testing Locally with QEMU

```bash
#!/bin/bash
# test-netboot-qemu.sh

# BIOS boot test
qemu-system-x86_64 \
    -m 2G \
    -enable-kvm \
    -boot n \
    -netdev user,id=net0,tftp=/var/lib/tftpboot,bootfile=pxelinux.0,net=192.168.76.0/24,dhcpstart=192.168.76.100 \
    -device e1000,netdev=net0 \
    -serial mon:stdio \
    -display none

# UEFI boot test
qemu-system-x86_64 \
    -m 2G \
    -enable-kvm \
    -bios /usr/share/ovmf/OVMF.fd \
    -boot n \
    -netdev user,id=net0,tftp=/var/lib/tftpboot,bootfile=grubx64.efi \
    -device e1000,netdev=net0 \
    -serial mon:stdio \
    -display none
```

### Network Debugging

```bash
# Monitor DHCP requests
tcpdump -i eth0 -n port 67 and port 68

# Monitor TFTP transfers
tcpdump -i eth0 -n port 69

# Monitor HTTP requests
tail -f /var/log/nginx/access.log

# Check what clients request
tail -f /var/log/syslog | grep dnsmasq
```

### Common Issues

#### Issue 1: "PXE-E32: TFTP open timeout"
```
Problem: TFTP server not responding
Solutions:
- Check firewall: ufw allow 69/udp
- Verify TFTP service: systemctl status tftpd-hpa
- Check permissions: chmod 755 /var/lib/tftpboot/*
- Test manually: tftp 192.168.1.50 -c get pxelinux.0
```

#### Issue 2: "No DEFAULT or UI configuration directive found"
```
Problem: PXELINUX can't find config
Solutions:
- Check config exists: ls -la /var/lib/tftpboot/pxelinux.cfg/default
- Check permissions: chmod 644 /var/lib/tftpboot/pxelinux.cfg/default
- Verify DEFAULT line in config
```

#### Issue 3: "Failed to load ldlinux.c32"
```
Problem: Missing SYSLINUX modules
Solutions:
- Copy all required .c32 files to TFTP root
- Ensure they're from same SYSLINUX version
- Check: ls -la /var/lib/tftpboot/*.c32
```

#### Issue 4: Kernel panic - no init found
```
Problem: initrd issues
Solutions:
- Verify /init exists in initrd: zcat initrd.img | cpio -t | grep '^init
- Check /init is executable: extract and ls -la init
- Test initrd in QEMU with debug parameter
```

#### Issue 5: Can't download filesystem.squashfs
```
Problem: Network/HTTP issues in initrd
Solutions:
- Add debug to init script
- Check network: add "ip addr" and "ip route" commands
- Test wget manually: wget http://192.168.1.50/boot/filesystem.squashfs
- Check nginx logs
```

### Debug Init Script

```bash
# Add to your initrd /init for debugging
cat >> init << 'EOF'

# Debug function
debug() {
    echo "=== DEBUG: $1 ==="
    case "$1" in
        network)
            ip addr show
            ip route show
            cat /etc/resolv.conf
            ping -c 3 8.8.8.8
            ;;
        modules)
            lsmod
            ;;
        mounts)
            mount
            df -h
            ;;
        *)
            echo "Available: network, modules, mounts"
            ;;
    esac
}

# Check for debug parameter
if grep -q "debug" /proc/cmdline; then
    debug network
    debug modules
    debug mounts
    /bin/sh
fi
EOF
```

---

## 11. Advanced Topics {#advanced}

### A. iPXE - Advanced Network Boot

iPXE is more powerful than standard PXE:
- HTTP/HTTPS support (faster than TFTP)
- iSCSI boot
- FCoE boot
- Scriptable
- Can chainload to PXELINUX/GRUB

```bash
# Compile iPXE
git clone https://github.com/ipxe/ipxe.git
cd ipxe/src

# Build with HTTP support
make bin/undionly.kpxe  # BIOS
make bin-x86_64-efi/ipxe.efi  # UEFI

# Deploy
cp bin/undionly.kpxe /var/lib/tftpboot/
cp bin-x86_64-efi/ipxe.efi /var/lib/tftpboot/

# Create iPXE script
cat > /var/www/html/boot.ipxe << 'EOF'
#!ipxe

dhcp
echo Network configured: ${net0/ip}

menu Select boot option
item myos Boot My OS
item shell Drop to iPXE shell
choose target && goto ${target}

:myos
kernel http://192.168.1.50/boot/vmlinuz root=http://192.168.1.50/boot/filesystem.squashfs
initrd http://192.168.1.50/boot/initrd.img
boot

:shell
shell
EOF

# DHCP hands out iPXE, iPXE loads script
# dhcpd.conf:
# if exists user-class and option user-class = "iPXE" {
#     filename "http://192.168.1.50/boot.ipxe";
# } else {
#     filename "undionly.kpxe";
# }
```

### B. Diskless Workstations

Full stateless desktop system:

```bash
# Server exports full desktop environment
# /etc/exports
/export/ubuntu-desktop 192.168.1.0/24(ro,sync,no_root_squash,no_subtree_check)

# initrd mounts root via NFS
# Each client gets unique /home from separate export
# /etc/exports
/export/home/client1 192.168.1.101(rw,sync,no_root_squash)
/export/home/client2 192.168.1.102(rw,sync,no_root_squash)

# initrd determines hostname/IP and mounts correct home
CLIENT_IP=$(ip addr show dev eth0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)
mount -t nfs 192.168.1.50:/export/home/$(hostname) /home
```

### C. iSCSI Boot

Boot from SAN storage:

```bash
# In initrd, add iSCSI support
modprobe iscsi_tcp
modprobe libiscsi

# Discover targets
iscsiadm -m discovery -t st -p 192.168.1.60

# Login to target
iscsiadm -m node -T iqn.2024.com.example:target1 -p 192.168.1.60 --login

# Root device appears as /dev/sda
mount /dev/sda1 /newroot
```

### D. Custom Splash Screen

```bash
# Create splash for PXELINUX
# Create 640x480 PNG image
convert splash.png -resize 640x480! splash.ppm

# Convert to LSS16 format
ppmtolss16 < splash.ppm > splash.lss

# Copy to TFTP root
cp splash.lss /var/lib/tftpboot/

# Update pxelinux.cfg/default
MENU BACKGROUND splash.lss
```

### E. Automated Deployment System

```bash
# Complete workflow
cat > deploy-system.sh << 'EOF'
#!/bin/bash

# 1. Build OS
cd buildroot && make

# 2. Create versioned squashfs
VERSION=$(date +%Y%m%d-%H%M)
mksquashfs output/images/rootfs rootfs-$VERSION.squashfs -comp xz

# 3. Deploy to server
scp rootfs-$VERSION.squashfs server:/var/www/html/boot/
ssh server "ln -sf rootfs-$VERSION.squashfs /var/www/html/boot/filesystem.squashfs"

# 4. Update boot config with new version
ssh server "sed -i 's/version=[0-9-]*/version=$VERSION/' /var/lib/tftpboot/pxelinux.cfg/default"

# 5. Notify clients to reboot
for client in $(cat clients.txt); do
    ssh root@$client "reboot"
done
EOF
```

### F. Security Considerations

```bash
# 1. Secure TFTP (read-only)
# In /etc/default/tftpd-hpa
TFTP_OPTIONS="--secure --readonly"

# 2. HTTPS for filesystem download
# In initrd init script
wget --no-check-certificate https://192.168.1.50/boot/filesystem.squashfs

# 3. Verify integrity
# On server, create checksums
sha256sum filesystem.squashfs > filesystem.squashfs.sha256

# In initrd
wget https://server/filesystem.squashfs
wget https://server/filesystem.squashfs.sha256
sha256sum -c filesystem.squashfs.sha256 || exit 1

# 4. Encrypted overlay
cryptsetup luksFormat /dev/ram0
cryptsetup luksOpen /dev/ram0 encrypted
mkfs.ext4 /dev/mapper/encrypted
mount /dev/mapper/encrypted /overlay/upper
```

---

## Summary and Next Steps

You now have complete knowledge of:
1. ✓ Boot process from power-on to OS
2. ✓ PXE/TFTP/HTTP protocols
3. ✓ BIOS (PXELINUX) and UEFI (GRUB) boot
4. ✓ All boot files and their purposes
5. ✓ Building custom OS with initrd
6. ✓ SquashFS and overlay filesystems
7. ✓ Complete server setup
8. ✓ Testing and debugging
9. ✓ Advanced topics

### Recommended Path

```
Week 1: Setup server, test with existing distro
Week 2: Build minimal Buildroot OS, deploy
Week 3: Create custom initrd, understand every line
Week 4: Optimize (compression, speed, features)
Week 5: Add advanced features (iPXE, iSCSI, etc.)
```

### Resources

- **Linux From Scratch**: https://www.linuxfromscratch.org/
- **Buildroot Manual**: https://buildroot.org/downloads/manual/manual.html
- **SYSLINUX Wiki**: https://wiki.syslinux.org/
- **GRUB Manual**: https://www.gnu.org/software/grub/manual/
- **Kernel Documentation**: /usr/src/linux/Documentation/

Good luck building your OS!
