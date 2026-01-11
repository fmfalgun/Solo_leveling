# Netboot Files: Comprehensive Analysis & Execution Guide

---

## Table of Contents
1. Understanding File Purpose Hierarchy
2. Detailed File Analysis
3. Execution Flow & Dependencies
4. Runtime Analysis & Debugging
5. Performance Profiling
6. Advanced Troubleshooting
7. Monitoring & Metrics

---

## Part 1: File Purpose Hierarchy

```
Boot Process Timeline:

FIRMWARE (BIOS/UEFI)
  ↓
  ├─→ Network Card ROM (PXE)
  │    └─→ DHCP Discovery
  │
  ├─→ Download bootloader
  │    ├─→ pxelinux.0 (BIOS)
  │    └─→ grubx64.efi (UEFI)
  │
  ├─→ Execute bootloader
  │    ├─→ Load configuration
  │    ├─→ Load dependent modules
  │    │    ├─→ vesamenu.c32
  │    │    ├─→ libcom32.c32
  │    │    └─→ libutil.c32
  │    └─→ Display menu
  │
  ├─→ User selection / timeout
  │
  ├─→ Download kernel + initramfs
  │    ├─→ vmlinuz-6.1.0
  │    └─→ initrd-netboot.img
  │
  ├─→ Hand control to kernel
  │
KERNEL (Linux)
  ├─→ Decompress initramfs
  │
  ├─→ Execute /init script
  │    ├─→ Load drivers
  │    ├─→ Configure network
  │    ├─→ Mount root (NFS/iSCSI)
  │    └─→ pivot_root
  │
  ├─→ Load rootfs
  │    └─→ filesystem.squashfs (optional)
  │
INIT SYSTEM (systemd/init)
  └─→ User environment ready
```

---

## Part 2: Individual File Deep Analysis

### File 1: pxelinux.0

#### **What It Is**
```
Physical File: /srv/tftp/pxelinux.0
Size: ~65-128 KB
Format: 16-bit x86 real-mode executable
Architecture: x86/x86-64 (legacy BIOS)
Compression: gzip (optional)
Location in Boot: Firmware → Downloaded via TFTP → Executed
```

#### **Need/Purpose**
- Initial bootloader for BIOS systems using PXE (Preboot eXecution Environment)
- Runs in real mode (16-bit), with minimal memory constraints
- Acts as intermediary between BIOS/network firmware and Linux kernel
- Handles configuration parsing and menu display
- Manages kernel/initramfs loading

#### **Internal Structure**
```
pxelinux.0 binary breakdown:

Offset 0x00000: Boot code (16-bit x86 assembly)
                - BIOS entry point
                - Real mode initialization
                - Stack/memory setup
                - Hardware detection

Offset 0x00100: Real-mode kernel
                - DHCP client implementation
                - TFTP client implementation
                - File system handlers
                - Menu system integration

Offset 0x02000: Memory manager
                - Extended memory access
                - Memory layout management
                - Protected/real mode switching

Offset 0x04000: Configuration parser
                - pxelinux.cfg reading
                - Menu option parsing
                - Default boot handler

Offset 0x06000: BIOS interrupt handlers
                - Int 0x10 (video)
                - Int 0x13 (disk)
                - Int 0x19 (boot)
                - Int 0x1A (time)
```

#### **Methods to Execute/Analyze**

**1. Examine Binary Structure**
```bash
# Check file type
file /srv/tftp/pxelinux.0
# Output: x86 boot sector, code offset 0x10

# Hexdump first 512 bytes (boot sector)
hexdump -C /srv/tftp/pxelinux.0 | head -30

# Look for SYSLINUX signature
strings /srv/tftp/pxelinux.0 | grep -i syslinux

# Check size
ls -lh /srv/tftp/pxelinux.0
stat /srv/tftp/pxelinux.0
```

**2. Monitor Execution with tcpdump**
```bash
# Start tcpdump to capture network traffic
sudo tcpdump -i eth0 -w pxeboot.pcap 'port 67 or port 68 or port 69'

# Boot client via PXE
# (trigger on client machine)

# Analyze captured packets
sudo tcpdump -r pxeboot.pcap -A | grep -A5 "pxelinux"

# Detailed analysis
wireshark pxeboot.pcap  # GUI analysis
```

**3. Real-Time Boot Logging**
```bash
# Monitor kernel messages during PXE boot
sudo journalctl -f -k

# Monitor DHCP server
sudo journalctl -u dnsmasq -f

# Monitor TFTP transfers
# Use tftpd-hpa verbose mode: -vvv
sudo systemctl stop tftpd-hpa
sudo tftpd-hpa -l -s /srv/tftp -vvv

# Or use strace on tftp process
sudo strace -p $(pgrep -f tftpd) -e write,read 2>&1 | grep -i pxe
```

**4. Simulate/Test Boot**
```bash
# Test with QEMU (no actual DHCP/TFTP)
qemu-system-x86_64 \
  -bios /usr/share/seabios/bios.bin \
  -m 1024 \
  -boot n \
  -net nic,model=e1000 \
  -net user,tftp=/srv/tftp,bootfile=pxelinux.0 \
  -nographic \
  -serial stdio 2>&1 | tee qemu-boot.log

# Extract boot messages
grep -i "pxelinux\|tftp\|dhcp\|error" qemu-boot.log
```

**5. Validate File Integrity**
```bash
# Check CRC/integrity
cksum /srv/tftp/pxelinux.0

# Compare with known good version
sha256sum /srv/tftp/pxelinux.0
# Compare against SYSLINUX release checksums

# Verify permissions (must be readable by tftp daemon)
ls -la /srv/tftp/pxelinux.0
chmod 644 /srv/tftp/pxelinux.0

# Test TFTP readability
tftp 127.0.0.1 69
> get pxelinux.0 /tmp/test.0
> quit
ls -la /tmp/test.0
```

---

### File 2: vesamenu.c32

#### **What It Is**
```
Physical File: /srv/tftp/pxelinux/vesamenu.c32
Size: ~150-300 KB
Format: COM32 module (32-bit x86 binary)
Dependencies: libcom32.c32, libutil.c32
Architecture: x86-64
Compression: Usually gzipped
Loaded By: pxelinux.0 (via configuration)
```

#### **Need/Purpose**
- Provides graphical user interface for boot menu
- Replaces text-based SYSLINUX menu with VESA graphics
- Enables mouse/keyboard interaction
- Renders custom backgrounds and themes
- Improves user experience during netboot

#### **Technical Components**
```
vesamenu.c32 structure:

ELF Header (32-bit executable)
  ↓
COM32 Setup Code
  ├─→ Detect VESA support
  ├─→ Query video modes
  ├─→ Allocate video memory
  └─→ Initialize graphics hardware

VESA Driver
  ├─→ Int 0x10 AH=4F (VESA BIOS extensions)
  ├─→ Video mode enumeration
  ├─→ Mode switching
  └─→ Framebuffer management

Rendering Engine
  ├─→ Text rendering
  ├─→ Image scaling/rendering
  ├─→ Color management
  └─→ Layout engine

Menu System
  ├─→ Menu item parsing
  ├─→ Keyboard handler
  ├─→ Mouse handler
  └─→ Scrolling/pagination

Configuration Parser
  ├─→ MENU directives
  ├─→ Color schemes
  ├─→ Background images
  └─→ Layout parameters
```

#### **Methods to Execute/Analyze**

**1. Examine Module Properties**
```bash
# Check file type (should be ELF 32-bit)
file /srv/tftp/pxelinux/vesamenu.c32

# Analyze ELF structure
readelf -h /srv/tftp/pxelinux/vesamenu.c32

# List sections
readelf -S /srv/tftp/pxelinux/vesamenu.c32

# Check symbols (debugging info)
nm /srv/tftp/pxelinux/vesamenu.c32

# Disassemble entry point
objdump -d /srv/tftp/pxelinux/vesamenu.c32 | head -50
```

**2. Verify Dependencies**
```bash
# Check if dependent libraries exist
ls -la /srv/tftp/pxelinux/{libcom32,libutil}.c32

# Verify in tftp directory
find /srv/tftp -name "*.c32" -exec ls -lh {} \;

# Test loading in pxelinux config
cat > /srv/tftp/pxelinux.cfg/test-menu << 'EOF'
DEFAULT vesamenu.c32
PROMPT 0
TIMEOUT 50

LABEL test
  MENU LABEL Test Entry
  KERNEL /boot/vmlinuz-6.1.0
  APPEND ro console=tty0
  IPAPPEND 2
EOF
```

**3. Monitor Module Loading**
```bash
# Use strace to trace system calls during module load
sudo strace -f -e trace=open,openat,read,write \
  qemu-system-x86_64 \
  -bios /usr/share/seabios/bios.bin \
  -m 1024 \
  -boot n \
  -net nic,model=e1000 \
  -net user,tftp=/srv/tftp,bootfile=pxelinux.0 \
  2>&1 | grep -i "vesamenu\|libcom32\|libutil"

# Capture detailed output
2>&1 | tee vesamenu-trace.log
```

**4. Test Graphics Rendering**
```bash
# Boot with QEMU and redirect graphics to window
qemu-system-x86_64 \
  -bios /usr/share/seabios/bios.bin \
  -m 1024 \
  -boot n \
  -net nic,model=e1000 \
  -net user,tftp=/srv/tftp,bootfile=pxelinux.0 \
  -display gtk  # Shows graphics window (if VESA works)

# Or with SDL
# -display sdl

# Check VESA capability in logs
# Look for: "VESA modes detected" or "VESA not available"
```

**5. Analyze Configuration Parsing**
```bash
# Check what menu items are defined
grep "^LABEL\|^MENU LABEL" /srv/tftp/pxelinux.cfg/default

# Validate configuration syntax
# (No built-in validator, but examine for common errors)
cat /srv/tftp/pxelinux.cfg/default | while read line; do
  case "$line" in
    LABEL*|KERNEL*|APPEND*|MENU*|TIMEOUT*|DEFAULT*)
      echo "Valid: $line";;
    *)
      if [ ! -z "$line" ] && [[ ! "$line" =~ ^# ]]; then
        echo "Unknown: $line"
      fi;;
  esac
done

# Test menu rendering
# Boot and visually inspect for:
# - Menu items displayed
# - Background image shown (if configured)
# - Colors correct
# - Mouse/keyboard working
```

---

### File 3: ldlinux.c32

#### **What It Is**
```
Physical File: /srv/tftp/pxelinux/ldlinux.c32
Size: ~40-80 KB
Format: COM32 module (32-bit x86 binary)
Dependencies: libcom32.c32
Architecture: x86-64
Role: Optional/Legacy core module
```

#### **Need/Purpose**
- Provides core SYSLINUX bootloader functionality as COM32 module
- Handles advanced configuration and boot chain logic
- May be required for certain menu features or legacy configurations
- Provides fallback menu system if vesamenu unavailable
- Supports boot script execution

#### **When It's Used**
```
Typical scenarios:

1. No vesamenu available (text-based boot only)
   - pxelinux.0 → ldlinux.c32 (fallback)

2. Complex boot chains
   - pxelinux.0 → ldlinux.c32 → other modules

3. Boot script execution
   - Interpreted boot sequences

4. Compatibility
   - Some configurations require explicit ldlinux.c32
```

#### **Methods to Execute/Analyze**

**1. Check if Needed**
```bash
# Inspect pxelinux.cfg for ldlinux references
grep -i "ldlinux" /srv/tftp/pxelinux.cfg/*

# Check if vesamenu sufficient (most common case)
# If no ldlinux references and vesamenu works, ldlinux not needed

# Test without ldlinux
cd /srv/tftp/pxelinux
mv ldlinux.c32 ldlinux.c32.bak
# Boot and test if still works
# If yes, ldlinux not necessary for your config
```

**2. Analyze Module Capabilities**
```bash
# Extract strings to see feature list
strings /srv/tftp/pxelinux/ldlinux.c32 | grep -E "feature|support|capability"

# Check sections
readelf -S /srv/tftp/pxelinux/ldlinux.c32

# Compare with vesamenu
# ldlinux typically smaller, fewer features
diff <(nm /srv/tftp/pxelinux/ldlinux.c32 | sort) \
     <(nm /srv/tftp/pxelinux/vesamenu.c32 | sort)
```

**3. Enable Fallback Testing**
```bash
# Create test config using ldlinux
cat > /srv/tftp/pxelinux.cfg/ldlinux-test << 'EOF'
UI ldlinux.c32
PROMPT 1
TIMEOUT 50

LABEL test-ldlinux
  MENU LABEL Test with ldlinux
  KERNEL /boot/vmlinuz-6.1.0
  APPEND ro console=tty0
EOF

# Boot with MAC address
# Create: pxelinux.cfg/01-aa-bb-cc-dd-ee-ff pointing to ldlinux-test
```

---

### File 4 & 5: libcom32.c32 & libutil.c32

#### **What They Are**
```
Physical Files:
  - /srv/tftp/pxelinux/libcom32.c32 (20-50 KB)
  - /srv/tftp/pxelinux/libutil.c32 (30-60 KB)

Format: COM32 libraries (32-bit x86 binaries)
Type: Shared libraries / Runtime support
Dependencies: None (core dependencies)
Loaded By: pxelinux.0 during module initialization
```

#### **Need/Purpose**

**libcom32.c32:**
- Core runtime library for all COM32 modules
- Provides standard C library functions in bootloader context
- Bridges between COM32 code and SYSLINUX/pxelinux.0
- Implements system calls and hardware access

**libutil.c32:**
- Utility library extending libcom32
- Provides UI/menu rendering functions
- Handles graphics operations
- Input/output utilities
- Used by vesamenu and other UI modules

#### **API/Function Categories**

```c
// libcom32.c32 provides:

// Standard C library
void *malloc(size_t);
void free(void *);
int printf(const char *, ...);
int snprintf(char *, size_t, const char *, ...);

// String operations
char *strcpy(char *, const char *);
size_t strlen(const char *);
int strcmp(const char *, const char *);

// Memory operations
void *memcpy(void *, const void *, size_t);
int memcmp(const void *, const void *, size_t);

// File I/O
FILE *fopen(const char *, const char *);
int fread(void *, size_t, size_t, FILE *);
int fclose(FILE *);

// Hardware access
int getc(void);
int putchar(int);
int serial_putchar(int);

// System calls
struct biosregs { ... };
int intcall(uint16_t, struct biosregs *);

// libutil.c32 extends with:

// Menu/UI
void draw_menu(struct menu_item *, int);
int menu_select(struct menu_item *, int);

// Graphics
void cls(void);
void set_color(int, int);
void draw_string(int, int, const char *);
void draw_image(int, int, const char *);

// Input handling
int keyboard_input(void);
int mouse_input(int *, int *);
```

#### **Methods to Execute/Analyze**

**1. Verify Presence and Linkage**
```bash
# Check both files exist
ls -lh /srv/tftp/pxelinux/{libcom32,libutil}.c32

# Verify readability
test -r /srv/tftp/pxelinux/libcom32.c32 && echo "libcom32 readable"
test -r /srv/tftp/pxelinux/libutil.c32 && echo "libutil readable"

# Check permissions
chmod 644 /srv/tftp/pxelinux/libcom32.c32
chmod 644 /srv/tftp/pxelinux/libutil.c32
```

**2. Dependency Chain Analysis**
```bash
# View which modules depend on these libraries
# by checking references in pxelinux.cfg

grep -r "vesamenu\|ldlinux" /srv/tftp/pxelinux.cfg/ | \
  while read line; do
    echo "Module used: $(echo $line | cut -d: -f2)"
    echo "  Requires: libcom32.c32"
    if grep -q vesamenu <<< "$line"; then
      echo "  Requires: libutil.c32"
    fi
  done
```

**3. Test Library Loading Sequence**
```bash
# Create minimal test with each module separately
cat > /srv/tftp/pxelinux.cfg/lib-test-1 << 'EOF'
UI vesamenu.c32
PROMPT 0
TIMEOUT 10
LABEL test
  KERNEL /boot/vmlinuz-6.1.0
EOF

# Boot and check logs
# If vesamenu loads successfully, libcom32 + libutil working

# Test fallback without vesamenu
cat > /srv/tftp/pxelinux.cfg/lib-test-2 << 'EOF'
PROMPT 1
TIMEOUT 10
LABEL test
  KERNEL /boot/vmlinuz-6.1.0
EOF

# This tests core pxelinux.0 without additional modules
```

**4. Monitor Runtime Calls**
```bash
# Use strace to trace system calls
# Look for open() calls loading libraries
sudo strace -e trace=open,openat qemu-system-x86_64 \
  -bios /usr/share/seabios/bios.bin \
  -m 1024 \
  -boot n \
  -net nic,model=e1000 \
  -net user,tftp=/srv/tftp,bootfile=pxelinux.0 \
  2>&1 | grep -E "libcom32|libutil|\.c32"
```

---

### File 6: grubx64.efi

#### **What It Is**
```
Physical File: /srv/tftp/grub/grubx64.efi or /boot/efi/EFI/BOOT/BOOTX64.EFI
Size: ~1-2 MB
Format: PE/COFF executable (UEFI)
Architecture: x86-64 / x64
Self-contained: Yes (all functionality included)
Compression: gzip/LZ4 (optional)
Loaded By: UEFI firmware
```

#### **Need/Purpose**
- Primary bootloader for UEFI-based systems
- Native support for UEFI calling conventions
- Can boot from multiple sources (local disk, network, USB)
- Better suited for modern hardware than pxelinux.0
- Supports larger initramfs and more flexible configurations

#### **UEFI Boot Process**
```
UEFI Firmware Startup
  ↓
Read Boot Variables (NVRAM)
  ├─→ Boot order
  ├─→ Boot devices
  └─→ Boot options
  
Network Boot Protocol Discovery
  ├─→ IPv4 DHCP
  ├─→ IPv6 Router advertisement
  └─→ Boot server location
  
Download Boot Loader
  ├─→ TFTP or HTTP
  └─→ grubx64.efi
  
Execute grubx64.efi
  ├─→ UEFI environment initialization
  ├─→ Console setup
  └─→ Load grub.cfg
  
Parse grub.cfg & Display Menu
  ├─→ Graphics initialization
  ├─→ Menu rendering
  └─→ Wait for selection
  
Load Kernel + Initramfs
  ├─→ Via TFTP/HTTP
  └─→ Memory allocation
  
Transfer to Kernel
```

#### **Methods to Execute/Analyze**

**1. Verify UEFI Binary Structure**
```bash
# Check file type (PE/COFF for UEFI)
file /srv/tftp/grub/grubx64.efi
# Expected: PE32+ executable (X86-64), for EFI/UEFI

# Inspect PE header
strings /srv/tftp/grub/grubx64.efi | head -20

# Check sections
readelf -S /srv/tftp/grub/grubx64.efi

# Disassemble small portion
objdump -d /srv/tftp/grub/grubx64.efi | head -30
```

**2. Test UEFI Boot with QEMU**
```bash
# Prepare UEFI environment
# Copy OVMF firmware to working directory
cp /usr/share/ovmf/OVMF.fd /tmp/
chmod +w /tmp/OVMF.fd

# Boot with UEFI
qemu-system-x86_64 \
  -bios /tmp/OVMF.fd \
  -m 2048 \
  -boot net \
  -net nic,model=e1000 \
  -net user,tftp=/srv/tftp \
  -nographic \
  -serial stdio 2>&1 | tee uefi-boot.log

# Check for UEFI boot messages
grep -i "uefi\|efi\|grub" uefi-boot.log
```

**3. Analyze grub.cfg Loading**
```bash
# Verify grub.cfg exists and is readable
ls -lah /srv/tftp/grub/grub.cfg

# Check configuration syntax
grub-script-check /srv/tftp/grub/grub.cfg

# Extract menu entries
grep "^menuentry" /srv/tftp/grub/grub.cfg

# Validate all paths referenced in grub.cfg exist
grep -oE '\/(boot|grub)\/[^ "]+' /srv/tftp/grub/grub.cfg | \
  while read path; do
    if [ ! -f "/srv/tftp/$path" ]; then
      echo "MISSING: $path"
    else
      ls -lh "/srv/tftp/$path"
    fi
  done
```

**4. Monitor GRUB Execution**
```bash
# Enable GRUB debug output
# Add to grub.cfg:
cat >> /srv/tftp/grub/grub.cfg << 'EOF'
# Debug configuration
set debug=all
set pager=1
EOF

# Boot and capture output
# Messages will show GRUB internal operations

# Or use strace on grubx64.efi if running natively
# (limited utility in netboot context due to EFI environment)
```

**5. Test Boot Menu**
```bash
# Boot via UEFI and manually select each menu entry
# Verify:
#   1. Menu displays correctly
#   2. Each entry boots successfully
#   3. Kernel parameters passed correctly
#   4. Network persistence works

# Collect boot logs
# From QEMU output
# From kernel dmesg
# From NFS mount logs
```

---

### File 7: default (pxelinux.cfg/default)

#### **What It Is**
```
Physical File: /srv/tftp/pxelinux.cfg/default
Format: Text configuration file (SYSLINUX format)
Size: 1-10 KB typical
Encoding: ASCII/UTF-8
No compilation needed: Parsed at boot time
Purpose: Boot menu and kernel options specification
```

#### **Need/Purpose**
- Defines boot menu structure and options for BIOS PXE boot
- Specifies kernel image location and boot parameters
- Sets timeouts and default boot entries
- Allows MAC-specific overrides (pxelinux.cfg/01-MAC-ADDR)
- Enables user selection during netboot process

#### **Methods to Execute/Analyze**

**1. Validate Configuration Syntax**
```bash
# Manual validation (pxelinux has no built-in checker)
cat /srv/tftp/pxelinux.cfg/default | \
  awk '
  /^[A-Z]/ && prev != "APPEND" { print NR ": " $0; prev=$1; next }
  /^APPEND/ { prev=$1; next }
  /^LABEL/ { prev=$1; print NR ": " $0; next }
  /^KERNEL/ { prev=$1; print NR ": " $0; next }
  { if (NF > 0) print "Line " NR ": Unknown: " $0 }
  END { print "Validation complete" }
  '

# Check for common errors
echo "=== Checking for issues ==="
grep -n "^LABEL" /srv/tftp/pxelinux.cfg/default | \
  while read line; do
    label=$(echo "$line" | awk '{print $2}')
    kernel=$(grep -A5 "^LABEL $label" | grep "^KERNEL")
    if [ -z "$kernel" ]; then
      echo "ERROR: LABEL $label has no KERNEL"
    fi
  done
```

**2. Verify Referenced Files Exist**
```bash
#!/bin/bash
# Check all referenced files

CONFIG="/srv/tftp/pxelinux.cfg/default"
TFTP_ROOT="/srv/tftp"

echo "Checking files referenced in $CONFIG..."

# Extract kernel paths
grep "^KERNEL" "$CONFIG" | awk '{print $2}' | while read kernel; do
  fullpath="$TFTP_ROOT$kernel"
  if [ -f "$fullpath" ]; then
    echo "✓ Kernel exists: $kernel ($(du -h "$fullpath" | cut -f1))"
  else
    echo "✗ MISSING: $kernel"
  fi
done

# Extract initrd paths
grep "initrd=" "$CONFIG" | grep -oE 'initrd=[^ "]+' | cut -d= -f2 | \
  while read initrd; do
    fullpath="$TFTP_ROOT$initrd"
    if [ -f "$fullpath" ]; then
      echo "✓ Initrd exists: $initrd ($(du -h "$fullpath" | cut -f1))"
    else
      echo "✗ MISSING: $initrd"
    fi
  done

# Extract any other files
grep -oE '\/(boot|images|pxelinux)\/[^ "]+' "$CONFIG" | sort -u | \
  while read file; do
    fullpath="$TFTP_ROOT$file"
    if [ -f "$fullpath" ] || [ -d "$fullpath" ]; then
      echo "✓ Referenced file: $file"
    else
      echo "✗ MISSING: $file"
    fi
  done
```

**3. Test Configuration Parsing**
```bash
# Boot and observe menu
# Check that:
#   1. All LABEL entries appear in menu
#   2. Menu LABEL text displays correctly
#   3. Default entry highlighted
#   4. Timeout countdown works
#   5. Timeout boot to default entry works

# Monitor with serial console
# Look for: "Booting..." messages
# These indicate config successfully parsed
```

**4. Debug Configuration Issues**
```bash
# If menu not appearing correctly

# 1. Check pxelinux.0 debug
# Use: PXELINUX debug=1 kernel parameter (if supported)

# 2. Monitor DHCP/TFTP
sudo tcpdump -i eth0 -A 'port 69' | grep -i "pxelinux.cfg\|default"

# 3. Test parsing with pxelinux directly
# Create test config:
cat > /srv/tftp/pxelinux.cfg/test-simple << 'EOF'
DEFAULT linux
LABEL linux
  KERNEL /boot/vmlinuz-6.1.0
  APPEND ro console=tty0
EOF

# Boot with MAC override pointing to test-simple
# (via pxelinux.cfg/01-MAC-ADDR)

# 4. Simplify step-by-step
# Start with minimal config, add features gradually
```

---

### File 8: initrd-netboot.img

#### **What It Is**
```
Physical File: /srv/tftp/boot/initrd-netboot.img
Format: gzip-compressed cpio archive
Size: 20-150 MB (depending on drivers/modules)
Architecture: x86-64 / ARM / other (matches kernel)
Components: Kernel modules, utilities, init script, libraries
Loaded By: Kernel (via pxelinux/grub APPEND/initrd)
```

#### **Need/Purpose**
- Provides temporary root filesystem during early boot
- Contains network drivers and DHCP client
- Includes NFS/iSCSI tools for mounting real root
- Runs init script to configure networking and mount filesystem
- Enables pivot_root to switch to real root filesystem

#### **Methods to Execute/Analyze**

**1. Extract and Inspect**
```bash
# Create working directory
mkdir -p /tmp/initrd-analysis
cd /tmp/initrd-analysis

# Method 1: Using gunzip + cpio
gunzip -c /srv/tftp/boot/initrd-netboot.img | \
  cpio -idm 2>/dev/null

# Method 2: Using unmkinitramfs (if available)
unmkinitramfs /srv/tftp/boot/initrd-netboot.img output/

# List extracted contents
ls -la
tree -L 3  # If tree installed

# Verify essential files exist
for file in init sbin/init lib/modules bin/ip bin/mount sbin/modprobe; do
  if [ -f "$file" ]; then
    echo "✓ $file exists"
  else
    echo "✗ MISSING: $file"
  fi
done
```

**2. Analyze Boot Scripts**
```bash
# Extract initramfs
cd /tmp/initrd-analysis
gunzip -c /srv/tftp/boot/initrd-netboot.img | cpio -idm

# Examine init script
cat init | head -50

# Check for network initialization
grep -n "dhcp\|ip\|network\|eth" init

# Check for NFS mounting
grep -n "nfs\|mount\|pivot_root" init

# Look for error handling
grep -n "error\|fail\|exit" init

# Full script analysis
wc -l init
grep "^[a-z_]*)" init  # Functions defined
grep "^\s*[a-z_]*" init | sort -u  # Commands used
```

**3. Check Included Modules**
```bash
# List kernel modules
cd /tmp/initrd-analysis
ls -la lib/modules/*/kernel/

# Count modules by type
find lib/modules -name "*.ko" | xargs file | \
  cut -d: -f2 | sort | uniq -c

# Check for network drivers
ls lib/modules/*/kernel/drivers/net/

# Check for filesystem drivers
ls lib/modules/*/kernel/fs/

# Verify required modules for netboot
for mod in nfs virtio_net e1000 8139too r8169 bnx2; do
  if find lib/modules -name "$mod.ko" | grep -q .; then
    echo "✓ $mod included"
  else
    echo "✗ MISSING: $mod"
  fi
done
```

**4. Analyze Library Dependencies**
```bash
# List libraries
cd /tmp/initrd-analysis
find lib -name "*.so*" | sort

# Check dependencies of key binaries
ldd bin/ip 2>/dev/null || file bin/ip

ldd sbin/modprobe 2>/dev/null || file sbin/modprobe

# Verify libc included
ls lib/libc.so.* lib64/libc.so.*

# Check for missing dependencies
for bin in bin/ip bin/mount bin/sh sbin/modprobe; do
  if [ -f "$bin" ]; then
    echo "=== $bin ==="
    ldd "$bin" 2>&1 | grep -v "not found" || echo "  Static or error"
  fi
done
```

**5. Verify Boot Parameters**
```bash
# Check how initramfs reacts to kernel parameters
grep -r "root=" init | head -5

grep -r "nfsroot=" init | head -5

grep -r "ip=" init | head -5

# Test-run init script (won't work fully, but check syntax)
bash -n init  # Check syntax only

# Simulate boot sequence locally (dangerous, dry-run only)
# source ./init  # DON'T RUN - only for inspection
```

**6. Monitor Runtime Boot**
```bash
# Boot with rd.debug to see initramfs messages
# In bootloader config:
# APPEND ... rd.debug rd.shell ...

# Or boot with verbose parameters
# APPEND ... loglevel=7 ...

# Capture boot messages
journalctl -b -k | grep -i "initramfs\|init\|network\|nfs"

# From serial console (preferred)
# Watch for:
# - Module loading messages
# - Network configuration output
# - Mount commands
# - pivot_root operation
```

**7. Compare Initramfs Versions**
```bash
# Create checksums for each version
sha256sum /srv/tftp/boot/initrd-*.img > /tmp/initrd-checksums.txt

# Compare file sizes
du -h /srv/tftp/boot/initrd-*.img

# Extract multiple versions and compare
mkdir -p /tmp/initrd-v1 /tmp/initrd-v2

gunzip -c /srv/tftp/boot/initrd-netboot-v1.img | \
  cpio -idm -D /tmp/initrd-v1 2>/dev/null

gunzip -c /srv/tftp/boot/initrd-netboot-v2.img | \
  cpio -idm -D /tmp/initrd-v2 2>/dev/null

# Diff directory structure
diff -r /tmp/initrd-v1 /tmp/initrd-v2 | head -50

# Check specific differences
diff /tmp/initrd-v1/init /tmp/initrd-v2/init
```

---

### File 9: filesystem.squashfs

#### **What It Is**
```
Physical File: /srv/tftp/boot/filesystem.squashfs
Format: SquashFS read-only filesystem image
Size: 100-800 MB typical (compressed)
Original Size: 300-2000+ MB uncompressed
Compression Ratio: 30-70% typical
Compression Type: gzip, zstd, xz, etc.
Loaded By: Kernel (mounted as loop device or overlayfs)
```

#### **Need/Purpose**
- Compressed read-only image of entire OS root filesystem
- Significant size reduction for network transfer
- Fast decompression during boot
- Live system capability (no permanent modifications)
- Can be mounted with overlay for write capability
- Alternative to NFS for ultra-portable netboot

#### **Methods to Execute/Analyze**

**1. Extract and Inspect**
```bash
# Create mount point
mkdir -p /tmp/squashfs-mount

# Mount squashfs
sudo mount -o loop /srv/tftp/boot/filesystem.squashfs /tmp/squashfs-mount

# List contents
ls -la /tmp/squashfs-mount/

# Check directory structure
tree -L 2 /tmp/squashfs-mount/ | head -40

# Verify essential directories
for dir in bin sbin lib etc usr var sys proc dev; do
  if [ -d "/tmp/squashfs-mount/$dir" ]; then
    echo "✓ /$dir exists"
  else
    echo "✗ MISSING: /$dir"
  fi
done

# Check disk usage per directory
du -sh /tmp/squashfs-mount/* | sort -hr | head -20

# Unmount when done
sudo umount /tmp/squashfs-mount
```

**2. Analyze Compression**
```bash
# Check compression info
unsquashfs -stat /srv/tftp/boot/filesystem.squashfs

# Output includes:
# - Compression type
# - Block size
# - Original vs compressed size
# - Compression ratio

# Detailed statistics
unsquashfs -stat /srv/tftp/boot/filesystem.squashfs | grep -E "Compression|Original|Compressed"

# List large files (good recompression candidates)
unsquashfs -ll /srv/tftp/boot/filesystem.squashfs | \
  awk '{print $3, $NF}' | sort -rn | head -20

# Count files
unsquashfs -ll /srv/tftp/boot/filesystem.squashfs | wc -l
```

**3. Recreate and Optimize**
```bash
# Extract squashfs
mkdir -p /tmp/squashfs-extracted
cd /tmp/squashfs-extracted

unsquashfs -d root /srv/tftp/boot/filesystem.squashfs

# Remove unnecessary files (logs, caches, etc.)
rm -rf root/var/log/*
rm -rf root/var/cache/*
rm -rf root/tmp/*
rm -rf root/.git*
rm -rf root/usr/share/doc/*

# Recompress with better settings
mksquashfs root /tmp/filesystem-optimized.squashfs \
  -comp zstd \
  -Xcompression-level 22 \
  -b 1048576 \
  -threads $(nproc)

# Compare sizes
du -h /srv/tftp/boot/filesystem.squashfs
du -h /tmp/filesystem-optimized.squashfs

# Calculate improvement
orig=$(du -b /srv/tftp/boot/filesystem.squashfs | cut -f1)
new=$(du -b /tmp/filesystem-optimized.squashfs | cut -f1)
percent=$((100 * new / orig))
echo "New size: $percent% of original"
```

**4. Test SquashFS Boot**
```bash
# Boot with squashfs in kernel parameters
# In pxelinux.cfg/default:
cat >> /srv/tftp/pxelinux.cfg/squashfs-test << 'EOF'
LABEL squashfs-test
  KERNEL /boot/vmlinuz-6.1.0
  APPEND root=/dev/nfs \
    nfsroot=192.168.1.1:/export/custom-os \
    loop=filesystem.squashfs \
    loopback=iso9660 \
    ip=dhcp ro console=tty0 \
    initrd=/boot/initrd-netboot.img,/boot/filesystem.squashfs
EOF

# Boot and verify mounting
df -h  # Check mount points
mount | grep squashfs
mount | grep overlayfs

# Monitor boot time
time system_boot  # Measure total time
```

**5. Create Overlay for Persistence**
```bash
# During boot (in initramfs), the kernel typically:

# Mount squashfs as read-only
mount -o loop,ro filesystem.squashfs /squash

# Create writable layers
mkdir -p /overlay/upper /overlay/work

# Mount overlayfs
mount -t overlay overlay \
  -o lowerdir=/squash,upperdir=/overlay/upper,workdir=/overlay/work \
  /root

# This creates:
# - Read-only base from squashfs
# - Writable layer in tmpfs
# - Changes visible to process, lost on reboot

# To make changes persistent:
# Copy modified files from /overlay/upper
# back to source and rebuild squashfs
```

**6. Performance Analysis**
```bash
# Monitor decompression during boot
iostat -x 1  # While booting

# Check I/O patterns
iotop  # While system boots from squashfs

# Measure read times
time unsquashfs -l /srv/tftp/boot/filesystem.squashfs > /dev/null

# Calculate decompression speed
time gunzip -c filesystem.squashfs | cpio -t > /dev/null

# Network transfer time simulation
# File size
du -h /srv/tftp/boot/filesystem.squashfs

# Estimate transfer time
# size_MB / (network_bandwidth_MBps) = seconds
```

---

## Part 3: Complete Boot Flow Analysis

### Boot Timeline with Checkpoints

```
Time    Component           Action                      Analysis Point
─────────────────────────────────────────────────────────────────────────
0ms     BIOS/UEFI          Power-on POST              tcpdump start
100ms   PXE ROM            Network initialization      journalctl -k
150ms   Network            DHCP request sent           tcpdump -A
200ms   DHCP Server        Response with boot info    Check DHCP logs
220ms   Client             Parse DHCP response        grep DHCP logs
250ms   Network            TFTP request for pxelinux  tcpdump port 69
300ms   TFTP Server        Send pxelinux.0            Monitor tftp transfer
350ms   Network            pxelinux.0 received        Check file size
400ms   Client             Execute pxelinux.0         Monitor CPU
450ms   pxelinux.0         Parse config               strace output
500ms   pxelinux.0         Display menu               Serial console
1000ms  User               Select menu item            Watch selection
1050ms  pxelinux.0         Load kernel + initramfs    Monitor TFTP
1500ms  TFTP               Transfer complete           Check received size
1600ms  pxelinux.0         Hand to kernel              Monitor transition
1700ms  Kernel             Decompress initramfs       dmesg output
1800ms  Kernel             Mount initramfs            dmesg root=
1850ms  Kernel             Execute /init              dmesg init= message
1900ms  initramfs init     Load drivers              dmesg modprobe
2000ms  initramfs init     Configure network         grep "ip link"
2100ms  initramfs init     DHCP for NFS              grep dhclient
2200ms  DHCP Client        Acquire IP                Check network
2300ms  initramfs init     Mount NFS root            dmesg NFS mount
2500ms  initramfs init     pivot_root                dmesg pivot_root
2600ms  Real init          systemd start             systemd output
3000ms  User Space         System ready              systemd show-environment
```

### Log File Locations and Analysis

```bash
# Collection during boot

# 1. Kernel messages
journalctl -b -k > /tmp/kernel-boot.log
dmesg > /tmp/dmesg.log

# 2. System messages
journalctl -b > /tmp/systemd-boot.log
tail -f /var/log/messages  # RHEL-based

# 3. Network/DHCP
journalctl -u dnsmasq > /tmp/dhcp.log
journalctl -u systemd-networkd > /tmp/network.log

# 4. NFS mount logs
tail -f /var/log/nfs* > /tmp/nfs.log
mountstats > /tmp/nfs-stats.log

# 5. TFTP transfer logs
tcpdump -i eth0 'port 69' -w /tmp/tftp.pcap
wireshark /tmp/tftp.pcap

# 6. Serial console (preferred for complete boot)
# Redirect console output to file:
# APPEND console=ttyS0,115200n8 > /tmp/serial-boot.log
```

---

## Part 4: Automated Testing & Validation

### Boot Validation Script

```bash
#!/bin/bash
# netboot-validation.sh - Complete boot validation

set -e

TFTP_ROOT="/srv/tftp"
NFS_EXPORT="/export"
RESULTS="/tmp/netboot-validation-$(date +%s).txt"

{
  echo "=== Netboot Validation Report ==="
  echo "Date: $(date)"
  echo ""
  
  # 1. File existence checks
  echo "=== FILE EXISTENCE CHECKS ==="
  
  files=(
    "$TFTP_ROOT/pxelinux.0"
    "$TFTP_ROOT/pxelinux/vesamenu.c32"
    "$TFTP_ROOT/pxelinux/libcom32.c32"
    "$TFTP_ROOT/pxelinux/libutil.c32"
    "$TFTP_ROOT/grub/grubx64.efi"
    "$TFTP_ROOT/boot/vmlinuz-6.1.0"
    "$TFTP_ROOT/boot/initrd-netboot.img"
    "$TFTP_ROOT/boot/filesystem.squashfs"
    "$TFTP_ROOT/pxelinux.cfg/default"
    "$TFTP_ROOT/grub/grub.cfg"
  )
  
  for file in "${files[@]}"; do
    if [ -f "$file" ]; then
      size=$(du -h "$file" | cut -f1)
      echo "✓ $file ($size)"
    else
      echo "✗ MISSING: $file"
    fi
  done
  
  echo ""
  echo "=== FILE INTEGRITY CHECKS ==="
  
  # 2. File type checks
  file "$TFTP_ROOT/pxelinux.0" | grep -q "boot sector" && \
    echo "✓ pxelinux.0 is boot sector" || \
    echo "✗ pxelinux.0 type incorrect"
  
  file "$TFTP_ROOT/grub/grubx64.efi" | grep -q "PE32+" && \
    echo "✓ grubx64.efi is PE32+ UEFI" || \
    echo "✗ grubx64.efi type incorrect"
  
  file "$TFTP_ROOT/boot/vmlinuz-6.1.0" | grep -q "bzImage\|x86 boot executable" && \
    echo "✓ kernel is bzImage" || \
    echo "✗ kernel type incorrect"
  
  file "$TFTP_ROOT/boot/initrd-netboot.img" | grep -q "gzip\|cpio" && \
    echo "✓ initrd is gzip/cpio" || \
    echo "✗ initrd type incorrect"
  
  unsquashfs -stat "$TFTP_ROOT/boot/filesystem.squashfs" > /dev/null 2>&1 && \
    echo "✓ squashfs is valid" || \
    echo "✗ squashfs corrupted"
  
  echo ""
  echo "=== CONFIGURATION CHECKS ==="
  
  # 3. Config file validation
  grep -q "^LABEL.*custom-os" "$TFTP_ROOT/pxelinux.cfg/default" && \
    echo "✓ pxelinux config has boot entries" || \
    echo "✗ pxelinux config incomplete"
  
  grep -q "^menuentry" "$TFTP_ROOT/grub/grub.cfg" && \
    echo "✓ grub config has menu entries" || \
    echo "✗ grub config incomplete"
  
  # 4. Check referenced files in config
  echo ""
  echo "=== CONFIG REFERENCED FILES ==="
  grep -oE '\/(boot|images)\/[^ "]+' "$TFTP_ROOT/pxelinux.cfg/default" | sort -u | \
    while read file; do
      if [ -f "$TFTP_ROOT$file" ]; then
        echo "✓ $file exists"
      else
        echo "✗ MISSING: $file"
      fi
    done
  
  echo ""
  echo "=== INITRAMFS CONTENT CHECK ==="
  
  # 5. Initramfs analysis
  mkdir -p /tmp/initrd-check
  gunzip -c "$TFTP_ROOT/boot/initrd-netboot.img" | \
    cpio -idm -D /tmp/initrd-check 2>/dev/null
  
  [ -f /tmp/initrd-check/init ] && \
    echo "✓ initramfs has /init" || \
    echo "✗ initramfs missing /init"
  
  [ -d /tmp/initrd-check/lib/modules ] && \
    echo "✓ initramfs has kernel modules" || \
    echo "✗ initramfs missing modules"
  
  [ -f /tmp/initrd-check/bin/ip ] && \
    echo "✓ initramfs has ip utility" || \
    echo "✗ initramfs missing ip"
  
  rm -rf /tmp/initrd-check
  
  echo ""
  echo "=== SERVICE STATUS ==="
  
  # 6. Service checks
  systemctl is-active dnsmasq > /dev/null && \
    echo "✓ DHCP (dnsmasq) running" || \
    echo "✗ DHCP not running"
  
  systemctl is-active nfs-server > /dev/null && \
    echo "✓ NFS server running" || \
    echo "✗ NFS server not running"
  
  systemctl is-active tftpd-hpa > /dev/null && \
    echo "✓ TFTP server running" || \
    echo "✗ TFTP server not running"
  
  echo ""
  echo "=== NFS EXPORTS CHECK ==="
  showmount -e localhost | tail -n +2 | while read export; do
    echo "✓ NFS export: $export"
  done
  
  echo ""
  echo "=== Validation Complete ==="
  echo "Report saved to: $RESULTS"
  
} | tee "$RESULTS"

echo ""
echo "Full report: cat $RESULTS"
```

---

## Part 5: Summary & Quick Reference

### File Dependency Graph

```
pxelinux.0 (BIOS Boot)
    ├── pxelinux.cfg/default (configuration)
    │   ├── vmlinuz-6.1.0 (kernel)
    │   ├── initrd-netboot.img (initramfs)
    │   └── filesystem.squashfs (optional rootfs)
    │
    └── vesamenu.c32 (optional menu)
        ├── libcom32.c32 (core library)
        └── libutil.c32 (UI library)

grubx64.efi (UEFI Boot)
    ├── grub.cfg (configuration)
    │   ├── vmlinuz-6.1.0 (kernel)
    │   ├── initrd-netboot.img (initramfs)
    │   └── filesystem.squashfs (optional rootfs)
    │
    └── (self-contained, no module dependencies)
```

### Quick Validation Commands

```bash
# One-liner validation checks
for f in pxelinux.0 vmlinuz-6.1.0 initrd-netboot.img filesystem.squashfs; do
  [ -f "/srv/tftp/boot/$f" ] && echo "✓ $f" || echo "✗ Missing $f"
done

# Service health
systemctl is-active dnsmasq nfs-server tftpd-hpa | grep -c "active" | \
  grep -q "3" && echo "✓ All services running" || echo "✗ Service down"

# Boot test
qemu-system-x86_64 -bios /usr/share/seabios/bios.bin -m 1024 -boot n \
  -net nic,model=e1000 -net user,tftp=/srv/tftp,bootfile=pxelinux.0 \
  -nographic -serial stdio 2>&1 | tee boot-test.log

# Check boot success
grep -q "custom-os" boot-test.log && echo "✓ Boot successful" || echo "✗ Boot failed"
```

This comprehensive guide enables you to understand, execute, analyze, and troubleshoot every component of your custom OS netboot infrastructure.
