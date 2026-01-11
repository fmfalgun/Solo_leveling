# Network Boot Files: Analysis, Execution & Debugging Guide

## Table of Contents
1. [pxelinux.0 - BIOS Bootloader](#pxelinux)
2. [ldlinux.c32 - Core Library](#ldlinux)
3. [libcom32.c32 - C Library](#libcom32)
4. [libutil.c32 - Utility Library](#libutil)
5. [vesamenu.c32 - Menu System](#vesamenu)
6. [grubx64.efi - UEFI Bootloader](#grub)
7. [default - Configuration File](#default-config)
8. [initrd - Initial RAM Disk](#initrd)
9. [filesystem.squashfs - Root Filesystem](#squashfs)
10. [Complete Analysis Workflow](#workflow)

---

## 1. pxelinux.0 - BIOS Bootloader {#pxelinux}

### What It Is
```
Type:     x86 bootloader executable
Size:     ~26KB
Format:   16-bit real mode binary
Purpose:  First stage PXE bootloader for BIOS systems
When:     Executed by PXE firmware after DHCP/TFTP
```

### Why It's Needed

**The Problem:**
- BIOS PXE firmware is extremely limited (no filesystem, minimal network stack)
- Can only download ONE file via TFTP
- No user interface, no menu, no configuration

**The Solution:**
- pxelinux.0 is that ONE file
- Provides a full bootloader environment
- Can load additional modules
- Can read configuration
- Can present menus
- Can load kernels with parameters

### Binary Structure Analysis

```bash
# 1. Get the file
cp /usr/lib/PXELINUX/pxelinux.0 ./

# 2. Check file type
file pxelinux.0
# Output: pxelinux.0: DOS/MBR boot sector

# 3. View hexdump (first 512 bytes - boot sector)
xxd -l 512 pxelinux.0
# You'll see:
# 00000000: eb63 9000 0000 0000 0000 0000 0000 0000  .c..............
# First 2 bytes: EB 63 = JMP instruction (entry point)

# 4. Check for strings (embedded messages)
strings pxelinux.0
# Output shows:
# PXELINUX
# Loading
# Boot failed
# !PXE
# PXENV+

# 5. Detailed analysis with objdump (disassemble)
objdump -D -b binary -m i8086 pxelinux.0 | less
# Shows 16-bit x86 assembly code

# 6. Check size and permissions
ls -lh pxelinux.0
# -rw-r--r-- 1 user user 26K pxelinux.0
# Must be readable by TFTP server
```

### Execution Flow Analysis

```
Stage 1: PXE Firmware Loads pxelinux.0
    ↓
    [Memory Layout]
    0x07C00: Boot sector (512 bytes)
    0x10000: Rest of pxelinux.0
    
Stage 2: pxelinux.0 Initialization
    ↓
    1. Detect PXE stack (!PXE or PXENV+ structure)
    2. Initialize network card (already done by PXE)
    3. Get DHCP info (IP, server, boot file path)
    4. Set up TFTP client
    
Stage 3: Load Core Module
    ↓
    Search for and load: ldlinux.c32
    (Required - everything else depends on this)
    
Stage 4: Configuration Loading
    ↓
    Search path (in order):
    /pxelinux.cfg/<UUID>
    /pxelinux.cfg/01-<MAC>
    /pxelinux.cfg/<IP-hex>
    /pxelinux.cfg/default
    
Stage 5: Execute Configuration
    ↓
    Load modules specified (vesamenu.c32, etc.)
    Display menu or boot kernel
```

### How to Test/Debug

```bash
#!/bin/bash
# test-pxelinux.sh

# Method 1: Test with QEMU
echo "Testing pxelinux.0 with QEMU..."
qemu-system-x86_64 \
    -m 512M \
    -boot n \
    -netdev user,id=net0,tftp=/var/lib/tftpboot,bootfile=pxelinux.0 \
    -device e1000,netdev=net0,mac=52:54:00:12:34:56 \
    -nographic \
    -serial mon:stdio

# Method 2: Monitor what it requests via TFTP
echo "Monitoring TFTP requests..."
sudo tcpdump -i any -n -vv port 69 &
TCPDUMP_PID=$!

# Wait and analyze
sleep 30
kill $TCPDUMP_PID

# Method 3: Check TFTP logs
echo "Checking TFTP server logs..."
sudo journalctl -u tftpd-hpa -f

# Method 4: Test TFTP download manually
echo "Testing manual TFTP download..."
tftp 192.168.1.50 << EOF
binary
get pxelinux.0
quit
EOF

if [ -f pxelinux.0 ]; then
    echo "✓ pxelinux.0 downloaded successfully"
    ls -lh pxelinux.0
else
    echo "✗ Failed to download pxelinux.0"
fi
```

### Common Issues & Solutions

```bash
# Issue 1: "TFTP open timeout"
# Analysis:
tcpdump -i eth0 port 69
# Look for RRQ (Read Request) packets
# Solution: Check firewall, TFTP service

# Issue 2: "Failed to load ldlinux.c32"
# Analysis:
ls -la /var/lib/tftpboot/ldlinux.c32
# Solution: Copy from same SYSLINUX version
cp /usr/lib/syslinux/modules/bios/ldlinux.c32 /var/lib/tftpboot/

# Issue 3: "No DEFAULT or UI configuration"
# Analysis:
cat /var/lib/tftpboot/pxelinux.cfg/default
# Solution: Must have DEFAULT or UI directive

# Issue 4: Hangs after loading
# Analysis: Enable debug output
# Add to kernel command line: debug loglevel=7
```

### Creating Debug Version

```bash
# Build pxelinux with debug output
git clone https://github.com/geneC/syslinux.git
cd syslinux

# Edit core/pxelinux.asm to add debug messages
# Then build
make installer
make
cp bios/core/pxelinux.0 /var/lib/tftpboot/pxelinux-debug.0
```

---

## 2. ldlinux.c32 - Core Library {#ldlinux}

### What It Is
```
Type:     COM32 module (SYSLINUX module format)
Size:     ~115KB
Format:   32-bit protected mode code
Purpose:  Core runtime library for SYSLINUX
When:     Loaded automatically by pxelinux.0
```

### Why It's Needed

**The Architecture:**
```
pxelinux.0 (16-bit real mode, limited)
    ↓ loads
ldlinux.c32 (32-bit protected mode, full environment)
    ↓ provides services to
All other .c32 modules (vesamenu.c32, etc.)
```

**Services Provided:**
- Memory management (malloc, free)
- File I/O through TFTP
- Configuration parsing
- Module loading system
- Hardware detection
- Basic I/O (console, keyboard)

### Binary Analysis

```bash
# 1. Get the file
cp /usr/lib/syslinux/modules/bios/ldlinux.c32 ./

# 2. File type
file ldlinux.c32
# ldlinux.c32: data

# 3. Check for COM32 signature
xxd -l 16 ldlinux.c32
# Should start with: COM32 header signature

# 4. Strings analysis
strings ldlinux.c32 | grep -i "error\|load\|init"
# Shows internal error messages and function names

# 5. Check exports (symbols it provides)
objdump -t ldlinux.c32 2>/dev/null | head -50
# Shows exported function symbols

# 6. Size analysis
ls -lh ldlinux.c32
# Compare with other .c32 files

# 7. Verify it's from same SYSLINUX version
rpm -qf /usr/lib/syslinux/modules/bios/ldlinux.c32
# or
dpkg -S /usr/lib/syslinux/modules/bios/ldlinux.c32
```

### Module Format Analysis

```bash
#!/bin/bash
# analyze-com32-module.sh

MODULE="ldlinux.c32"

echo "=== COM32 Module Analysis: $MODULE ==="

# Header analysis
echo -e "\n1. Header (first 64 bytes):"
xxd -l 64 $MODULE

# Size
echo -e "\n2. Size:"
ls -lh $MODULE

# Strings (function names, messages)
echo -e "\n3. Key strings:"
strings $MODULE | grep -E "^[a-z_]+$" | head -20

# Dependencies (looks for other module names)
echo -e "\n4. Possible dependencies:"
strings $MODULE | grep "\.c32"

# Version info
echo -e "\n5. Version info:"
strings $MODULE | grep -i "version\|syslinux\|copyright"

# Entry points
echo -e "\n6. Analyzing structure..."
file $MODULE
```

### How It Loads

```
pxelinux.0 execution:
    1. Switch to 32-bit protected mode
    2. TFTP download ldlinux.c32
    3. Verify COM32 header signature
    4. Allocate memory for module
    5. Load module into memory
    6. Resolve relocations
    7. Jump to entry point
    8. ldlinux.c32 initializes runtime
    9. Returns to pxelinux.0
    10. Now pxelinux.0 can call ldlinux functions
```

### Testing

```bash
# Test 1: Verify it loads
# Watch TFTP logs
tail -f /var/log/syslog | grep tftp &

# Boot a client
# Look for: "RRQ from ... filename ldlinux.c32"

# Test 2: Check for errors
# In pxelinux.cfg/default, add:
SERIAL 0 115200
# Boot client and watch serial output

# Test 3: Version matching
echo "Checking version compatibility..."
PXELINUX_VER=$(strings pxelinux.0 | grep "SYSLINUX" | head -1)
LDLINUX_VER=$(strings ldlinux.c32 | grep "SYSLINUX" | head -1)

echo "pxelinux.0 version: $PXELINUX_VER"
echo "ldlinux.c32 version: $LDLINUX_VER"

if [ "$PXELINUX_VER" != "$LDLINUX_VER" ]; then
    echo "⚠ WARNING: Version mismatch!"
fi
```

### Common Issues

```bash
# Issue: "Failed to load ldlinux.c32"
# Cause 1: File not found
ls -la /var/lib/tftpboot/ldlinux.c32
# Solution: Copy from SYSLINUX package

# Cause 2: Version mismatch
# Solution: Copy ALL files from same version
cp /usr/lib/syslinux/modules/bios/*.c32 /var/lib/tftpboot/

# Cause 3: Corrupted file
# Solution: Verify checksum
md5sum ldlinux.c32
# Compare with known good copy

# Cause 4: Wrong architecture
file ldlinux.c32
# Must match: BIOS vs UEFI
```

---

## 3. libcom32.c32 - C Library {#libcom32}

### What It Is
```
Type:     COM32 module
Size:     ~167KB
Format:   Standard C library implementation
Purpose:  Provides libc functions to other modules
Depends:  ldlinux.c32
```

### Why It's Needed

**Standard C Functions:**
```c
// libcom32.c32 provides these to other modules:
printf()      // Formatted output
malloc()      // Memory allocation
strcpy()      // String operations
fopen()       // File operations
scanf()       // Input parsing
atoi()        // Conversions
// ... and hundreds more
```

**Without it:**
- Each module would need to implement its own C functions
- Huge code duplication
- Larger file sizes

**With it:**
- Modules are smaller
- Standard behavior
- Easier to develop new modules

### Analysis

```bash
#!/bin/bash
# analyze-libcom32.sh

echo "=== Analyzing libcom32.c32 ==="

FILE="libcom32.c32"

# 1. Size comparison
echo "Size comparison:"
ls -lh ldlinux.c32 libcom32.c32 libutil.c32 vesamenu.c32

# 2. Extract and analyze contents
echo -e "\n2. Extracting initrd..."
mkdir -p initrd-analysis
cd initrd-analysis
zcat ../$INITRD | cpio -idm 2>/dev/null || \
xzcat ../$INITRD | cpio -idm 2>/dev/null || \
bzcat ../$INITRD | cpio -idm 2>/dev/null
cd ..

echo "  Extracted to: initrd-analysis/"
echo "  Total size unpacked: $(du -sh initrd-analysis | cut -f1)"
echo "  Total files: $(find initrd-analysis -type f | wc -l)"

# 3. Directory structure
echo -e "\n3. Directory structure:"
tree -L 2 -d initrd-analysis 2>/dev/null || find initrd-analysis -type d -maxdepth 2

# 4. Init script analysis
echo -e "\n4. Init script (/init):"
if [ -f "initrd-analysis/init" ]; then
    echo "  ✓ Found"
    echo "  Size: $(ls -lh initrd-analysis/init | awk '{print $5}')"
    echo "  Executable: $([ -x initrd-analysis/init ] && echo 'Yes' || echo 'No')"
    echo "  Shebang: $(head -1 initrd-analysis/init)"
    echo -e "\n  First 20 lines:"
    head -20 initrd-analysis/init | sed 's/^/    /'
else
    echo "  ✗ NOT FOUND - This will cause kernel panic!"
fi

# 5. Binaries included
echo -e "\n5. Binaries:"
find initrd-analysis -type f -executable -path "*/bin/*" -o -path "*/sbin/*" | \
    sed 's|initrd-analysis/||' | sort

# 6. Kernel modules
echo -e "\n6. Kernel modules:"
if [ -d "initrd-analysis/lib/modules" ]; then
    echo "  Kernel version: $(ls initrd-analysis/lib/modules/)"
    echo "  Module count: $(find initrd-analysis/lib/modules -name "*.ko" | wc -l)"
    echo -e "\n  Network drivers:"
    find initrd-analysis/lib/modules -name "*net*.ko" -o -name "*e1000*.ko" -o -name "*virtio*.ko" | \
        sed 's|.*/||'
    echo -e "\n  Filesystem modules:"
    find initrd-analysis/lib/modules -path "*/fs/*.ko" | sed 's|.*/||'
else
    echo "  ✗ No kernel modules found"
fi

# 7. Libraries
echo -e "\n7. Shared libraries:"
find initrd-analysis -name "*.so*" | wc -l | xargs echo "  Count:"
find initrd-analysis -name "*.so*" | sed 's|.*/||' | sort -u | head -10

# 8. Scripts
echo -e "\n8. Scripts:"
find initrd-analysis -name "*.sh" -o -name "*-functions" | \
    sed 's|initrd-analysis/||'

# 9. Device nodes
echo -e "\n9. Device nodes:"
find initrd-analysis/dev -type c -o -type b 2>/dev/null | \
    xargs ls -l | awk '{print "  " $NF " (" $5 ", " $6 ")"}'

# 10. Configuration files
echo -e "\n10. Configuration files:"
find initrd-analysis/etc -type f 2>/dev/null | sed 's|initrd-analysis/||'

# 11. Network boot specific
echo -e "\n11. Network boot features:"
if grep -q "wget\|curl\|tftp" initrd-analysis/init 2>/dev/null; then
    echo "  ✓ Network download capability"
fi
if grep -q "nfs\|mount.*nfs" initrd-analysis/init 2>/dev/null; then
    echo "  ✓ NFS support"
fi
if grep -q "squashfs" initrd-analysis/init 2>/dev/null; then
    echo "  ✓ SquashFS support"
fi
if grep -q "overlay" initrd-analysis/init 2>/dev/null; then
    echo "  ✓ OverlayFS support"
fi

# 12. Memory usage estimation
echo -e "\n12. Memory usage (when loaded):"
echo "  Compressed: $(ls -lh $INITRD | awk '{print $5}')"
echo "  Uncompressed: $(du -sh initrd-analysis | cut -f1)"
echo "  Ratio: $(echo "scale=1; $(du -sk $INITRD | cut -f1) * 100 / $(du -sk initrd-analysis | cut -f1)" | bc)% of original size"
```

### Testing initrd

```bash
#!/bin/bash
# test-initrd.sh

INITRD="initrd.img"
KERNEL="/boot/vmlinuz-$(uname -r)"

echo "=== Testing initrd ==="

# Test 1: Verify it's valid
echo "Test 1: Validation"
if zcat $INITRD | cpio -t > /dev/null 2>&1; then
    echo "  ✓ Valid gzip'd cpio archive"
elif xzcat $INITRD | cpio -t > /dev/null 2>&1; then
    echo "  ✓ Valid xz'd cpio archive"
else
    echo "  ✗ Invalid format!"
    exit 1
fi

# Test 2: Check for /init
echo -e "\nTest 2: Init script"
if zcat $INITRD | cpio -t 2>/dev/null | grep -q "^init$"; then
    echo "  ✓ /init found"
else
    echo "  ✗ /init missing - WILL CAUSE KERNEL PANIC!"
fi

# Test 3: Boot in QEMU
echo -e "\nTest 3: QEMU boot test"
echo "  Starting QEMU (timeout 30s)..."
timeout 30 qemu-system-x86_64 \
    -kernel $KERNEL \
    -initrd $INITRD \
    -append "debug console=ttyS0" \
    -nographic \
    -m 512M \
    2>&1 | tee qemu-boot.log

if grep -q "Kernel panic" qemu-boot.log; then
    echo "  ✗ Kernel panic occurred!"
    grep -A 5 "Kernel panic" qemu-boot.log
else
    echo "  ✓ Boot successful (or in progress)"
fi

# Test 4: Network capabilities
echo -e "\nTest 4: Network boot features"
TMP_DIR=$(mktemp -d)
cd $TMP_DIR
zcat $INITRD | cpio -idm 2>/dev/null

if [ -f init ]; then
    echo "  Checking init script..."
    grep -q "wget\|curl" init && echo "    ✓ HTTP download support"
    grep -q "mount.*nfs" init && echo "    ✓ NFS mount support"
    grep -q "squashfs" init && echo "    ✓ SquashFS support"
    grep -q "ip.*addr\|ifconfig\|dhcp" init && echo "    ✓ Network configuration"
fi

cd - > /dev/null
rm -rf $TMP_DIR
```

---

## 9. filesystem.squashfs - Root Filesystem {#squashfs}

### What It Is
```
Type:     SquashFS compressed filesystem
Size:     100MB - 2GB (depending on OS)
Format:   Read-only compressed filesystem
Purpose:  Your actual operating system
When:     Mounted by initrd after network download
```

### Complete Analysis

```bash
#!/bin/bash
# analyze-squashfs.sh

SQFS="filesystem.squashfs"

echo "=== Complete SquashFS Analysis ==="

# 1. Basic info
echo "1. File information:"
file $SQFS
ls -lh $SQFS

# 2. SquashFS details
echo -e "\n2. SquashFS structure:"
unsquashfs -s $SQFS

# 3. Compression statistics
echo -e "\n3. Compression analysis:"
unsquashfs -stat $SQFS

# 4. List contents (top level)
echo -e "\n4. Root directory contents:"
unsquashfs -ll $SQFS | head -20

# 5. Size breakdown
echo -e "\n5. Size breakdown by directory:"
unsquashfs -ll $SQFS | awk '{if ($1 ~ /^d/) print $NF}' | while read dir; do
    SIZE=$(unsquashfs -ll $SQFS "$dir" 2>/dev/null | \
           awk '{sum+=$3} END {print sum}')
    printf "  %-20s %10s bytes\n" "$dir" "$SIZE"
done | sort -k2 -n -r | head -10

# 6. Count files
echo -e "\n6. File statistics:"
echo "  Total entries: $(unsquashfs -ll $SQFS | wc -l)"
echo "  Directories: $(unsquashfs -ll $SQFS | grep -c "^d")"
echo "  Regular files: $(unsquashfs -ll $SQFS | grep -c "^-")"
echo "  Symlinks: $(unsquashfs -ll $SQFS | grep -c "^l")"

# 7. Check essential directories
echo -e "\n7. Essential directories check:"
for dir in bin sbin lib etc usr var; do
    if unsquashfs -ll $SQFS | grep -q "^d.*/$dir$"; then
        echo "  ✓ /$dir"
    else
        echo "  ✗ /$dir MISSING"
    fi
done

# 8. Check init system
echo -e "\n8. Init system:"
if unsquashfs -ll $SQFS | grep -q "systemd"; then
    echo "  Type: systemd"
elif unsquashfs -ll $SQFS | grep -q "sbin/init"; then
    echo "  Type: sysvinit or compatible"
else
    echo "  Type: Unknown or missing"
fi

# 9. Kernel modules (if included)
echo -e "\n9. Kernel modules:"
MODULE_COUNT=$(unsquashfs -ll $SQFS "lib/modules" 2>/dev/null | grep ".ko$" | wc -l)
if [ $MODULE_COUNT -gt 0 ]; then
    echo "  Found: $MODULE_COUNT modules"
    unsquashfs -ll $SQFS "lib/modules" 2>/dev/null | head -5
else
    echo "  None (expected if using initrd for drivers)"
fi

# 10. Installed packages (Debian/Ubuntu)
echo -e "\n10. Installed software:"
if unsquashfs -ll $SQFS "var/lib/dpkg/status" > /dev/null 2>&1; then
    PKG_COUNT=$(unsquashfs -cat $SQFS var/lib/dpkg/status 2>/dev/null | grep -c "^Package:")
    echo "  Debian packages: $PKG_COUNT"
elif unsquashfs -ll $SQFS "var/lib/rpm" > /dev/null 2>&1; then
    echo "  RPM-based system detected"
fi

# 11. Mount test
echo -e "\n11. Mount test:"
MOUNT_POINT=$(mktemp -d)
if mount -t squashfs -o loop $SQFS $MOUNT_POINT 2>/dev/null; then
    echo "  ✓ Successfully mounted at $MOUNT_POINT"
    echo "  Contents:"
    ls -la $MOUNT_POINT | head -10
    umount $MOUNT_POINT
    rmdir $MOUNT_POINT
else
    echo "  ✗ Failed to mount"
fi

# 12. Compare with uncompressed size
echo -e "\n12. Compression efficiency:"
COMPRESSED=$(stat -f%z $SQFS 2>/dev/null || stat -c%s $SQFS)
UNCOMPRESSED=$(unsquashfs -stat $SQFS | grep "Uncompressed size" | awk '{print $3}')
if [ -n "$UNCOMPRESSED" ]; then
    RATIO=$(echo "scale=1; $COMPRESSED * 100 / $UNCOMPRESSED" | bc)
    echo "  Compressed: $(numfmt --to=iec $COMPRESSED)"
    echo "  Uncompressed: $(numfmt --to=iec $UNCOMPRESSED)"
    echo "  Compression ratio: $RATIO%"
fi
```

### Extracting and Modifying

```bash
#!/bin/bash
# extract-modify-repack-squashfs.sh

SQFS="filesystem.squashfs"
EXTRACT_DIR="squashfs-root"

echo "=== Extract, Modify, Repack SquashFS ==="

# 1. Extract
echo "1. Extracting..."
unsquashfs $SQFS
cd $EXTRACT_DIR

# 2. Make modifications (example: add a file)
echo "2. Making modifications..."
echo "Hello from modified squashfs" > root/MODIFIED.txt

# 3. Check what changed
echo "3. Modified files:"
find . -name "MODIFIED.txt"

# 4. Repack
echo "4. Repacking with same compression..."
cd ..
mksquashfs $EXTRACT_DIR filesystem-modified.squashfs \
    -comp $(unsquashfs -stat $SQFS | grep "Compression" | awk '{print $2}') \
    -b 1M

# 5. Compare sizes
echo "5. Size comparison:"
ls -lh $SQFS filesystem-modified.squashfs

# 6. Cleanup
echo "6. Cleaning up..."
rm -rf $EXTRACT_DIR
echo "Done! New file: filesystem-modified.squashfs"
```

---

## 10. Complete Analysis Workflow {#workflow}

### Automated Complete Analysis

```bash
#!/bin/bash
# complete-netboot-analysis.sh

TFTP_ROOT="/var/lib/tftpboot"
HTTP_ROOT="/var/www/html/boot"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║       Complete Network Boot System Analysis               ║"
echo "╚════════════════════════════════════════════════════════════╝"

cd $TFTP_ROOT || exit 1

# 1. BIOS Boot Chain
echo -e "\n1. BIOS BOOT CHAIN ANALYSIS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "pxelinux.0" ]; then
    echo "✓ pxelinux.0"
    file pxelinux.0
    ls -lh pxelinux.0
    
    # Check dependencies
    echo -e "\n  Dependencies:"
    for module in ldlinux.c32 libcom32.c32 libutil.c32 vesamenu.c32; do
        if [ -f "$module" ]; then
            echo "    ✓ $module ($(ls -lh $module | awk '{print $5}'))"
        else
            echo "    ✗ $module MISSING"
        fi
    done
    
    # Check config
    if [ -f "pxelinux.cfg/default" ]; then
        echo -e "\n  ✓ Configuration: pxelinux.cfg/default"
        echo "    Entries: $(grep -c "^LABEL" pxelinux.cfg/default)"
    else
        echo -e "\n  ✗ Configuration MISSING"
    fi
else
    echo "✗ pxelinux.0 NOT FOUND"
fi

# 2. UEFI Boot Chain
echo -e "\n\n2. UEFI BOOT CHAIN ANALYSIS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "grubx64.efi" ]; then
    echo "✓ grubx64.efi"
    file grubx64.efi
    ls -lh grubx64.efi
    
    if [ -f "grub/grub.cfg" ]; then
        echo -e "\n  ✓ Configuration: grub/grub.cfg"
        echo "    Entries: $(grep -c "^menuentry" grub/grub.cfg)"
    else
        echo -e "\n  ✗ Configuration MISSING"
    fi
else
    echo "✗ grubx64.efi NOT FOUND"
fi

# 3. Kernel
echo -e "\n\n3. KERNEL ANALYSIS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "vmlinuz" ]; then
    echo "✓ vmlinuz"
    file vmlinuz
    ls -lh vmlinuz
    
    # Try to extract version
    strings vmlinuz | grep "Linux version" | head -1
else
    echo "✗ vmlinuz NOT FOUND"
fi

# 4. Initrd
echo -e "\n\n4. INITRD ANALYSIS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "initrd.img" ]; then
    echo "✓ initrd.img"
    file initrd.img
    ls -lh initrd.img
    
    # Check for /init
    if zcat initrd.img 2>/dev/null | cpio -t 2>/dev/null | grep -q "^init$"; then
        echo "  ✓ Contains /init script"
    else
        echo "  ✗ Missing /init - CRITICAL ERROR"
    fi
    
    # Count files
    FILE_COUNT=$(zcat initrd.img 2>/dev/null | cpio -t 2>/dev/null | wc -l)
    echo "  Files: $FILE_COUNT"
else
    echo "✗ initrd.img NOT FOUND"
fi

# 5. Root Filesystem
echo -e "\n\n5. ROOT FILESYSTEM ANALYSIS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

for location in "$HTTP_ROOT/filesystem.squashfs" "$TFTP_ROOT/filesystem.squashfs"; do
    if [ -f "$location" ]; then
        echo "✓ filesystem.squashfs"
        echo "  Location: $location"
        file "$location"
        ls -lh "$location"
        
        if command -v unsquashfs > /dev/null; then
            unsquashfs -stat "$location" 2>/dev/null | head -5
        fi
        break
    fi
done

if [ ! -f "$HTTP_ROOT/filesystem.squashfs" ] && [ ! -f "$TFTP_ROOT/filesystem.squashfs" ]; then
    echo "✗ filesystem.squashfs NOT FOUND"
fi

# 6. Network Services
echo -e "\n\n6. NETWORK SERVICES CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# DHCP/TFTP
if systemctl is-active --quiet dnsmasq 2>/dev/null; then
    echo "✓ dnsmasq (DHCP+TFTP) - Running"
elif systemctl is-active --quiet tftpd-hpa 2>/dev/null; then
    echo "✓ tftpd-hpa (TFTP) - Running"
else
    echo "✗ TFTP server not running"
fi

# HTTP
if systemctl is-active --quiet nginx 2>/dev/null; then
    echo "✓ nginx (HTTP) - Running"
elif systemctl is-active --quiet apache2 2>/dev/null; then
    echo "✓ apache2 (HTTP) - Running"
else
    echo "⚠ HTTP server not running (optional)"
fi

# 7. File Integrity
echo -e "\n\n7. FILE INTEGRITY CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_file() {
    if [ -f "$1" ]; then
        if [ -r "$1" ]; then
            echo "  ✓ $1 (readable)"
        else
            echo "  ⚠ $1 (not readable)"
        fi
    else
        echo "  ✗ $1 (missing)"
    fi
}

echo "TFTP accessible files:"
check_file "pxelinux.0"
check_file "ldlinux.c32"
check_file "vesamenu.c32"
check_file "pxelinux.cfg/default"
check_file "vmlinuz"
check_file "initrd.img"

# 8. Permissions
echo -e "\n\n8. PERMISSIONS CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "TFTP root permissions:"
ls -ld $TFTP_ROOT
echo -e "\nKey files:"
ls -lh pxelinux.0 ldlinux.c32 vmlinuz initrd.img 2>/dev/null | awk '{print $1, $5, $9}'

# 9. Size Summary
echo -e "\n\n9. SIZE SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

total_size() {
    find $TFTP_ROOT -type f -exec stat -f%z {} \; 2>/dev/null | \
        awk '{sum+=$1} END {print sum}' || \
    find $TFTP_ROOT -type f -exec stat -c%s {} \; 2>/dev/null | \
        awk '{sum+=$1} END {print sum}'
}

TOTAL=$(total_size)
echo "Total TFTP root size: $(echo $TOTAL | numfmt --to=iec 2>/dev/null || echo $TOTAL bytes)"

if [ -f "$HTTP_ROOT/filesystem.squashfs" ]; then
    SQFS_SIZE=$(stat -f%z "$HTTP_ROOT/filesystem.squashfs" 2>/dev/null || \
                stat -c%s "$HTTP_ROOT/filesystem.squashfs")
    echo "SquashFS size: $(echo $SQFS_SIZE | numfmt --to=iec 2>/dev/null || echo $SQFS_SIZE bytes)"
fi

# 10. Boot Flow Simulation
echo -e "\n\n10. BOOT FLOW SIMULATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "BIOS Client Boot Path:"
echo "  1. PXE firmware requests DHCP"
echo "  2. DHCP provides: IP + pxelinux.0"
echo "  3. TFTP download: pxelinux.0"
[ -f "pxelinux.0" ] && echo "     ✓ Available" || echo "     ✗ Missing"
echo "  4. pxelinux.0 loads: ldlinux.c32"
[ -f "ldlinux.c32" ] && echo "     ✓ Available" || echo "     ✗ Missing"
echo "  5. Reads config: pxelinux.cfg/default"
[ -f "pxelinux.cfg/default" ] && echo "     ✓ Available" || echo "     ✗ Missing"
echo "  6. Loads menu: vesamenu.c32"
[ -f "vesamenu.c32" ] && echo "     ✓ Available" || echo "     ✗ Missing"
echo "  7. Downloads: vmlinuz + initrd.img"
[ -f "vmlinuz" ] && [ -f "initrd.img" ] && echo "     ✓ Available" || echo "     ✗ Missing"
echo "  8. Boots kernel with initrd"
echo "  9. Initrd downloads: filesystem.squashfs"
[ -f "$HTTP_ROOT/filesystem.squashfs" ] && echo "     ✓ Available" || echo "     ✗ Missing"
echo "  10. System boots from squashfs"

echo -e "\n╔════════════════════════════════════════════════════════════╗"
echo "║                    Analysis Complete                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
```

Save this script and run it to get a complete analysis of your network boot setup!

---

## Summary

You now have complete tools to:

1. **Analyze** every file in your network boot setup
2. **Debug** issues at each stage of the boot process
3. **Test** components individually and as a complete system
4. **Understand** the purpose and interaction of each file
5. **Modify** and rebuild components as needed

Each file plays a critical role:
- **pxelinux.0** - First stage bootloader (BIOS)
- **ldlinux.c32** - Core runtime library
- **libcom32.c32** - C standard library
- **libutil.c32** - Utility functions
- **vesamenu.c32** - Graphical menu
- **grubx64.efi** - UEFI bootloader
- **default** - Boot configuration
- **initrd** - Early boot environment
- **filesystem.squashfs** - Your OS

Use these analysis scripts to understand, debug, and optimize your network boot infrastructure! function names
echo -e "\n2. Exported functions (sample):"
strings $FILE | grep -E "^(printf|malloc|strcpy|memcpy|fopen)" | head -20

# 3. Check all C standard library functions
echo -e "\n3. C standard library functions found:"
for func in printf scanf malloc free strcpy strcmp strlen fopen fclose; do
    if strings $FILE | grep -q "^$func$"; then
        echo "  ✓ $func"
    else
        echo "  ✗ $func"
    fi
done

# 4. Dependencies
echo -e "\n4. This module provides services to:"
cd /var/lib/tftpboot
for module in *.c32; do
    if [ "$module" != "$FILE" ] && [ "$module" != "ldlinux.c32" ]; then
        if strings $module | grep -q "libcom32"; then
            echo "  - $module"
        fi
    fi
done

# 5. Memory footprint
echo -e "\n5. Memory usage when loaded:"
size $FILE 2>/dev/null || echo "  (Cannot determine - not ELF format)"
```

### Module Chain

```
Dependency Chain:

vesamenu.c32
    ↓ calls printf(), malloc(), etc.
libcom32.c32
    ↓ calls low-level services
ldlinux.c32
    ↓ interfaces with
pxelinux.0 (hardware/BIOS)
```

### Testing

```bash
# Test: Which modules need libcom32?
echo "Modules requiring libcom32.c32:"

cd /var/lib/tftpboot
for module in *.c32; do
    if [ "$module" != "libcom32.c32" ] && [ "$module" != "ldlinux.c32" ]; then
        if strings $module | grep -q "libcom32"; then
            echo "  $module → libcom32.c32"
        fi
    fi
done

# Test: Remove libcom32 and see what breaks
echo -e "\nTest: Temporarily removing libcom32.c32"
mv libcom32.c32 libcom32.c32.backup

# Try to boot - menu will fail to load
# Error: "Failed to load libcom32.c32"

# Restore
mv libcom32.c32.backup libcom32.c32
```

---

## 4. libutil.c32 - Utility Library {#libutil}

### What It Is
```
Type:     COM32 module
Size:     ~24KB
Format:   Utility functions library
Purpose:  Common utility functions
Depends:  ldlinux.c32, libcom32.c32
```

### Why It's Needed

**Utility Functions:**
- Configuration file parsing
- String manipulation helpers
- Menu system utilities
- Color/display helpers

**Used by:**
- Menu systems (menu.c32, vesamenu.c32)
- Configuration parsers
- Other complex modules

### Analysis

```bash
#!/bin/bash
# analyze-libutil.sh

FILE="libutil.c32"

echo "=== Analyzing libutil.c32 ==="

# 1. Size (smallest of the libraries)
echo "1. Size:"
ls -lh $FILE

# 2. Functions it provides
echo -e "\n2. Utility functions (sample):"
strings $FILE | grep -E "_[a-z]+_" | head -20

# 3. Who uses it?
echo -e "\n3. Modules depending on libutil:"
for module in *.c32; do
    if [ "$module" != "$FILE" ]; then
        if strings $module | grep -q "libutil"; then
            echo "  - $module"
        fi
    fi
done

# 4. Compare all library sizes
echo -e "\n4. Library size comparison:"
ls -lh ldlinux.c32 libcom32.c32 libutil.c32 | awk '{print $9, $5}'
```

---

## 5. vesamenu.c32 - Menu System {#vesamenu}

### What It Is
```
Type:     COM32 module (UI component)
Size:     ~27KB
Format:   Menu system with graphics
Purpose:  Display graphical boot menu
Depends:  ldlinux.c32, libcom32.c32, libutil.c32
```

### Why It's Needed

**Text vs Graphics:**
```
Without vesamenu.c32:
  1. Boot Linux
  2. Boot Windows
  [Text only, no colors, no background]

With vesamenu.c32:
  ╔════════════════════════════════════╗
  ║  [Background Image]                ║
  ║  ┌──────────────────────────────┐  ║
  ║  │ ► Boot Linux                 │  ║
  ║  │   Boot Windows               │  ║
  ║  │   Memory Test                │  ║
  ║  └──────────────────────────────┘  ║
  ╚════════════════════════════════════╝
  [Colors, borders, graphics]
```

### Features Analysis

```bash
#!/bin/bash
# analyze-vesamenu.sh

echo "=== Analyzing vesamenu.c32 ==="

FILE="vesamenu.c32"

# 1. Capabilities
echo "1. Features detected:"
strings $FILE | grep -i "menu\|color\|background\|vesa"

# 2. Color support
echo -e "\n2. Color modes supported:"
strings $FILE | grep -i "color\|rgb\|palette"

# 3. Resolution support
echo -e "\n3. Video modes:"
strings $FILE | grep -E "[0-9]{3,4}x[0-9]{3,4}"

# 4. Configuration directives
echo -e "\n4. Configuration options:"
strings $FILE | grep -E "MENU (TITLE|COLOR|BACKGROUND|RESOLUTION)"

# 5. Compare with menu.c32
if [ -f "menu.c32" ]; then
    echo -e "\n5. Size comparison:"
    echo "  vesamenu.c32 (graphical): $(ls -lh vesamenu.c32 | awk '{print $5}')"
    echo "  menu.c32 (text only):     $(ls -lh menu.c32 | awk '{print $5}')"
fi
```

### Configuration Analysis

```bash
# Analyze your menu configuration
cat > analyze-menu-config.sh << 'EOF'
#!/bin/bash

CONFIG="/var/lib/tftpboot/pxelinux.cfg/default"

echo "=== Menu Configuration Analysis ==="

# 1. Menu system used
echo "1. Menu system:"
grep -E "^(DEFAULT|UI)" $CONFIG

# 2. Menu appearance
echo -e "\n2. Menu appearance settings:"
grep "^MENU" $CONFIG | grep -E "(TITLE|COLOR|BACKGROUND)"

# 3. Menu entries
echo -e "\n3. Boot entries:"
grep "^LABEL" $CONFIG

# 4. Timeouts
echo -e "\n4. Timeout settings:"
grep -E "^TIMEOUT" $CONFIG

# 5. Required files
echo -e "\n5. Files referenced:"
grep -E "KERNEL|APPEND|BACKGROUND" $CONFIG | \
    grep -oE "[a-zA-Z0-9._-]+\.(c32|png|jpg|img|0)" | sort -u

# 6. Verify all files exist
echo -e "\n6. File verification:"
grep -oE "[a-zA-Z0-9._-]+\.(c32|png|jpg|img|0)" $CONFIG | sort -u | while read file; do
    if [ -f "/var/lib/tftpboot/$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (MISSING!)"
    fi
done
EOF

chmod +x analyze-menu-config.sh
./analyze-menu-config.sh
```

### Testing Menu Appearance

```bash
# Test different menu configurations
cat > test-menu-appearance.sh << 'EOF'
#!/bin/bash

TFTP_ROOT="/var/lib/tftpboot"
CONFIG="$TFTP_ROOT/pxelinux.cfg/default"

# Backup current config
cp $CONFIG $CONFIG.backup

# Test 1: Simple text menu
cat > $CONFIG << 'MENU1'
DEFAULT menu.c32
TIMEOUT 50

LABEL test
    MENU LABEL Test Entry
    KERNEL vmlinuz
MENU1

echo "Test 1: Simple text menu"
echo "Boot a client and observe"
read -p "Press enter when done..."

# Test 2: Graphical menu with colors
cat > $CONFIG << 'MENU2'
DEFAULT vesamenu.c32
TIMEOUT 50

MENU TITLE Test Menu
MENU COLOR screen 37;40 #80ffffff #00000000
MENU COLOR border 30;44 #ffffffff #00000000

LABEL test
    MENU LABEL Test Entry
    KERNEL vmlinuz
MENU2

echo "Test 2: Graphical menu with colors"
echo "Boot a client and observe"
read -p "Press enter when done..."

# Restore
mv $CONFIG.backup $CONFIG
echo "Configuration restored"
EOF

chmod +x test-menu-appearance.sh
```

---

## 6. grubx64.efi - UEFI Bootloader {#grub}

### What It Is
```
Type:     EFI PE32+ executable
Size:     ~1.2MB (much larger than pxelinux.0)
Format:   UEFI application
Purpose:  Boot loader for UEFI systems
When:     Loaded by UEFI firmware (not BIOS)
```

### Why It's Needed

**UEFI vs BIOS:**
```
BIOS Boot:            UEFI Boot:
PXE → pxelinux.0      UEFI PXE → grubx64.efi
(16-bit, simple)      (64-bit, complex)
~26KB                 ~1.2MB
TFTP only             TFTP + HTTP
```

**UEFI Advantages:**
- Full 64-bit environment
- HTTP/HTTPS support
- Filesystem drivers built-in
- Can read local disks
- Secure Boot support
- More flexible

### Binary Analysis

```bash
#!/bin/bash
# analyze-grubx64-efi.sh

FILE="grubx64.efi"

echo "=== Analyzing grubx64.efi ==="

# 1. File type
echo "1. File type:"
file $FILE

# 2. PE header analysis
echo -e "\n2. PE/COFF header:"
objdump -p $FILE | head -30

# 3. Sections
echo -e "\n3. Binary sections:"
objdump -h $FILE

# 4. Embedded modules
echo -e "\n4. GRUB modules included:"
strings $FILE | grep "\.mod$" | sort | uniq

# 5. Supported filesystems
echo -e "\n5. Filesystem support:"
strings $FILE | grep -E "^(ext[234]|xfs|btrfs|fat|ntfs)"

# 6. Network protocols
echo -e "\n6. Network protocols:"
strings $FILE | grep -iE "(tftp|http|nfs)"

# 7. Size comparison
echo -e "\n7. Size comparison:"
echo "  grubx64.efi:  $(ls -lh $FILE | awk '{print $5}')"
echo "  pxelinux.0:   $(ls -lh pxelinux.0 | awk '{print $5}')"
echo "  Ratio: $(echo "scale=1; $(stat -f%z $FILE) / $(stat -f%z pxelinux.0)" | bc)x larger"
```

### Building Custom GRUB

```bash
#!/bin/bash
# build-custom-grub-efi.sh

echo "Building custom GRUB EFI image..."

# Modules to include
MODULES="
    normal
    tftp
    http
    net
    efinet
    efi_gop
    efi_uga
    all_video
    boot
    linux
    linux16
    linuxefi
    chain
    configfile
    echo
    font
    gfxterm
    gfxmenu
    gzio
    jpeg
    png
    part_gpt
    part_msdos
    ext2
    fat
    iso9660
    search
    test
    loadenv
    reboot
    halt
"

# Build
grub-mkimage \
    -d /usr/lib/grub/x86_64-efi \
    -O x86_64-efi \
    -o grubx64-custom.efi \
    -p "(tftp)/grub" \
    $MODULES

echo "Created grubx64-custom.efi"
ls -lh grubx64-custom.efi

# Analyze what's included
echo -e "\nModules included:"
strings grubx64-custom.efi | grep "\.mod$" | wc -l

# Compare sizes
echo -e "\nSize comparison:"
ls -lh /usr/lib/grub/x86_64-efi/grubx64.efi grubx64-custom.efi 2>/dev/null || echo "Stock GRUB not found"
```

### Configuration Analysis

```bash
#!/bin/bash
# analyze-grub-config.sh

CONFIG="/var/lib/tftpboot/grub/grub.cfg"

echo "=== Analyzing GRUB Configuration ==="

# 1. Check if config exists
if [ ! -f "$CONFIG" ]; then
    echo "ERROR: $CONFIG not found!"
    exit 1
fi

# 2. Parse menu entries
echo "1. Menu entries found:"
grep "menuentry" $CONFIG | sed 's/menuentry "\([^"]*\)".*/  - \1/'

# 3. Default boot
echo -e "\n2. Default settings:"
grep -E "^set (default|timeout)" $CONFIG

# 4. Network boot entries
echo -e "\n3. Network boot configuration:"
grep -A 5 "linux.*http\|linux.*tftp" $CONFIG

# 5. Files referenced
echo -e "\n4. Files referenced:"
grep -oE "(vmlinuz|initrd|kernel|boot)[a-zA-Z0-9._-]*" $CONFIG | sort -u

# 6. Check syntax
echo -e "\n5. Syntax check:"
grub-script-check $CONFIG && echo "  ✓ Syntax OK" || echo "  ✗ Syntax errors found"

# 7. Test configuration (dry run)
echo -e "\n6. Simulating configuration load:"
grub-script-check $CONFIG
```

### Testing GRUB

```bash
#!/bin/bash
# test-grub-uefi.sh

echo "Testing GRUB UEFI boot..."

# Method 1: QEMU with OVMF (UEFI firmware)
if [ ! -f /usr/share/ovmf/OVMF.fd ]; then
    echo "Installing OVMF (UEFI firmware for QEMU)..."
    sudo apt-get install ovmf
fi

# Test boot
qemu-system-x86_64 \
    -bios /usr/share/ovmf/OVMF.fd \
    -m 2G \
    -boot n \
    -netdev user,id=net0,tftp=/var/lib/tftpboot,bootfile=grubx64.efi \
    -device e1000,netdev=net0 \
    -serial mon:stdio \
    -nographic

# Method 2: Check GRUB logs (on client after boot)
# On UEFI client, GRUB can log to EFI variables
# Check with: efibootmgr -v
```

---

## 7. default - Configuration File {#default-config}

### What It Is
```
Type:     Text configuration file
Size:     Usually < 10KB
Format:   SYSLINUX configuration directives
Purpose:  Defines boot menu and options
When:     Read by pxelinux.0 after loading
```

### Complete Analysis

```bash
#!/bin/bash
# analyze-pxelinux-config.sh

CONFIG="/var/lib/tftpboot/pxelinux.cfg/default"

echo "=== Complete PXELINUX Configuration Analysis ==="

# 1. Basic info
echo "1. File info:"
ls -lh $CONFIG
echo "  Lines: $(wc -l < $CONFIG)"
echo "  Size: $(du -h $CONFIG | cut -f1)"

# 2. Directives used
echo -e "\n2. Configuration directives:"
grep -E "^[A-Z]+" $CONFIG | cut -d' ' -f1 | sort | uniq -c

# 3. Menu system
echo -e "\n3. Menu system:"
if grep -q "vesamenu.c32" $CONFIG; then
    echo "  Type: Graphical (vesamenu.c32)"
    echo "  Colors: $(grep -c "MENU COLOR" $CONFIG) defined"
    echo "  Background: $(grep "MENU BACKGROUND" $CONFIG | awk '{print $3}')"
elif grep -q "menu.c32" $CONFIG; then
    echo "  Type: Text (menu.c32)"
else
    echo "  Type: None (prompt mode)"
fi

# 4. Boot entries
echo -e "\n4. Boot entries:"
awk '/^LABEL/ {label=$2; getline; print "  " label ": " $0}' $CONFIG

# 5. Timeout settings
echo -e "\n5. Timeout:"
TIMEOUT=$(grep "^TIMEOUT" $CONFIG | awk '{print $2}')
echo "  Raw value: $TIMEOUT (1/10 seconds)"
echo "  Human readable: $(echo "scale=1; $TIMEOUT/10" | bc) seconds"

# 6. Default boot
echo -e "\n6. Default boot:"
grep "^DEFAULT\|MENU DEFAULT" $CONFIG

# 7. Required files
echo -e "\n7. Required files:"
{
    grep "DEFAULT\|UI" $CONFIG | awk '{print $2}'
    grep "KERNEL\|APPEND" $CONFIG | grep -oE "[a-z0-9._-]+\.(c32|img|0)"
} | sort -u | while read file; do
    if [ -f "/var/lib/tftpboot/$file" ]; then
        printf "  ✓ %-20s %s\n" "$file" "$(ls -lh /var/lib/tftpboot/$file | awk '{print $5}')"
    else
        printf "  ✗ %-20s MISSING!\n" "$file"
    fi
done

# 8. Kernel parameters
echo -e "\n8. Kernel boot parameters:"
grep "APPEND" $CONFIG | sed 's/.*APPEND /  /'

# 9. Validate syntax
echo -e "\n9. Configuration validation:"
if grep -q "^DEFAULT\|^UI" $CONFIG; then
    echo "  ✓ Has DEFAULT or UI directive"
else
    echo "  ✗ Missing DEFAULT or UI directive"
fi

if grep -q "^LABEL" $CONFIG; then
    echo "  ✓ Has boot entries (LABEL)"
else
    echo "  ✗ No boot entries defined"
fi
```

---

## 8. initrd - Initial RAM Disk {#initrd}

### What It Is
```
Type:     Compressed CPIO archive (gzipped)
Size:     10-50MB (varies greatly)
Format:   cpio | gzip
Purpose:  Temporary root filesystem for early boot
When:     Loaded by bootloader, extracted by kernel
```

### Why It's Needed

**Boot Process Problem:**
```
Kernel needs → Storage drivers → To mount root filesystem
But drivers are → In root filesystem → Chicken-and-egg!
```

**Solution:**
initrd provides a complete minimal environment in RAM with all necessary drivers and tools.

### Complete Analysis

```bash
#!/bin/bash
# analyze-initrd.sh

INITRD="initrd.img"

echo "=== Complete initrd Analysis ==="

# 1. Basic information
echo "1. File information:"
file $INITRD
ls -lh $INITRD
echo "  Compression: $(file $INITRD | grep -o "gzip\|xz\|bzip2\|lzma")"

# 2. Extract
