# Quick-Start Lab Setup Guide
## Get Safe Environment Running in 1 Hour

---

## ⚡ **FASTEST SETUP (30 Minutes)**

### Step 1: Download VirtualBox (5 min)
```bash
# Linux
sudo apt install virtualbox virtualbox-ext-pack

# macOS
# Download from: virtualbox.org
# Or: brew install virtualbox

# Windows
# Download installer from virtualbox.org
```

### Step 2: Download Linux ISO (5-10 min)
```
Download one of these (2-5 GB):
├─ Ubuntu Server 22.04 LTS (Recommended for beginners)
│  └─ https://ubuntu.com/download/server
│
├─ Debian 12 (Stable, minimal)
│  └─ https://www.debian.org/download
│
└─ CentOS Stream (Enterprise-like)
   └─ https://www.centos.org/download/
```

### Step 3: Create VM (15-20 min)

**In VirtualBox GUI:**
```
1. Click "New"
2. Name: "FilesystemLab"
3. Type: "Linux"
4. Version: Select your chosen distro
5. Memory: 4096 MB (4 GB)
6. Create disk: 50 GB, VDI, dynamically allocated
7. Click Create
8. Right-click VM → Settings → Storage
9. Add ISO file to CD drive
10. Click OK
```

### Step 4: Install Linux (30 min, but mostly automatic)
```
1. Right-click VM → Start
2. Follow installation wizard
3. When asked where to install: use default (whole disk)
4. Set password you'll remember
5. Wait for installation to complete
6. It will ask to remove ISO and reboot
```

### Step 5: Boot and Verify
```
1. VM boots to login screen
2. Login with your credentials
3. Run: lsblk
   
Should see:
    NAME    MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
    sda       8:0    0   50G  0 disk
    └─sda1    8:1    0   50G  0 part /
    
✅ Success! You have a 50GB virtual disk
```

### Step 6: Take First Snapshot (2 min)
```
1. In VirtualBox, select VM (must be OFF)
2. Click "Snapshots" tab
3. Click "Take Snapshot"
4. Name: "Fresh_Install"
5. Description: "Clean Linux before any modifications"
6. Click OK
```

**Total Time: ~45 minutes to safe lab ready** ✅

---

## 📦 **INSTALL ESSENTIAL TOOLS (10 Minutes)**

```bash
# Copy-paste this entire block:

# Update system
sudo apt update && sudo apt upgrade -y

# Partition and filesystem tools
sudo apt install -y \
    parted \
    gparted \
    lvm2 \
    e2fsprogs \
    btrfs-progs \
    cryptsetup

# Init system tools
sudo apt install -y \
    systemd-container \
    sysv-rc-conf

# Development tools
sudo apt install -y \
    build-essential \
    git \
    vim \
    nano

# Useful utilities
sudo apt install -y \
    tree \
    htop \
    ncdu \
    openssh-server

# Verification
echo "✅ All tools installed!"
```

**After installation, take another snapshot:**
```
1. Right-click VM → Snapshots → Take Snapshot
2. Name: "Base_System_With_Tools"
3. Click OK
```

---

## 🧪 **YOUR FIRST EXPERIMENT (Testing Partitions)**

### SAFE Experiment: List and Understand Partitions

```bash
# STEP 1: Take snapshot before starting
# (Done in VirtualBox UI - snapshot: "FirstExperiment")

# STEP 2: Examine current partitions
lsblk
# Shows: sda with sda1 (your root partition)

# STEP 3: See more details
sudo parted -l
# Shows: partition table, size, filesystem

# STEP 4: Check mounted filesystems
mount | column -t
# Shows: what's mounted where

# STEP 5: Check disk usage
df -h
# Shows: used space, available space

# STEP 6: View raw partition info
sudo blkid
# Shows: filesystem types, UUIDs

# STEP 7: Check filesystem details
stat /
# Shows: inode number, permissions, etc.
```

**Success Indicators:**
```
✅ Commands run without errors
✅ Output shows your partition (/dev/sda1)
✅ Root filesystem is mounted on /
✅ No error messages
```

**If something goes wrong:**
```
1. In VirtualBox: Right-click VM
2. Snapshots → Click "FirstExperiment"
3. Click "Restore"
4. VM reboots to exact same state
5. Try again!
```

---

## 🎯 **EXPERIMENT 2: Create New Partition**

### Safely Create and Format a New Virtual Disk

```bash
# STEP 1: Take snapshot
# (VirtualBox GUI → Snapshots → Take Snapshot: "CreatePartition")

# STEP 2: In VirtualBox, ADD A VIRTUAL DISK
VirtualBox → Select VM → Settings → Storage
├─ Controller: SATA
├─ Click "Add" (green plus)
├─ Create new disk
├─ Size: 10 GB
├─ Type: VDI
├─ OK
# This creates /dev/sdb (second virtual disk)

# STEP 3: Inside VM, verify new disk appeared
lsblk
# Should show:
#   sdb    8:16    0   10G  0 disk

# STEP 4: Create partition on new disk
sudo parted /dev/sdb
    mklabel gpt          # Create partition table
    mkpart primary ext4 1MB 10GB  # Create partition
    print                # Verify
    quit                 # Exit

# STEP 5: Format the partition
sudo mkfs.ext4 /dev/sdb1
# Output: Creating filesystem with 2621440 4k blocks...

# STEP 6: Mount the partition
sudo mkdir -p /mnt/testdisk
sudo mount /dev/sdb1 /mnt/testdisk

# STEP 7: Verify
ls -la /mnt/testdisk/
# Should be empty but mountable

# STEP 8: Create test file
echo "Hello from partition" | sudo tee /mnt/testdisk/test.txt
cat /mnt/testdisk/test.txt

# STEP 9: Unmount when done
sudo umount /mnt/testdisk
```

**Success Indicators:**
```
✅ lsblk shows /dev/sdb with /dev/sdb1
✅ mkfs.ext4 completes without error
✅ Mount succeeds
✅ Can read/write files
✅ Unmount succeeds
```

**If you make a mistake:**
```
1. It's fine! Nothing is permanent
2. In VirtualBox: Snapshots → Restore "CreatePartition"
3. Try again with corrections
4. Practice makes perfect!
```

---

## 🔄 **EXPERIMENT 3: LVM (More Complex)**

### Create Logical Volumes

```bash
# STEP 1: Take snapshot
# (VirtualBox Snapshots: "LVMExperiment")

# STEP 2: Make sure /dev/sdb exists
# If not, add another virtual disk in VirtualBox

# STEP 3: Create Physical Volume (PV)
sudo pvcreate /dev/sdb1
# Output: Physical volume "/dev/sdb1" successfully created

# STEP 4: Create Volume Group (VG)
sudo vgcreate myvg /dev/sdb1
# Output: Volume group "myvg" successfully created

# STEP 5: Create Logical Volume (LV)
sudo lvcreate -L 5G -n mylv myvg
# Output: Logical volume "mylv" created

# STEP 6: Format logical volume
sudo mkfs.ext4 /dev/myvg/mylv

# STEP 7: Mount
sudo mkdir -p /mnt/lvm_test
sudo mount /dev/myvg/mylv /mnt/lvm_test

# STEP 8: Verify
ls -la /mnt/lvm_test/

# STEP 9: Check LVM status
sudo lvs     # List logical volumes
sudo pvs     # List physical volumes
sudo vgs     # List volume groups

# STEP 10: Cleanup (when done)
sudo umount /mnt/lvm_test
sudo lvremove /dev/myvg/mylv
sudo vgremove myvg
sudo pvremove /dev/sdb1
```

**This teaches:**
- ✅ Physical volumes (hardware)
- ✅ Volume groups (abstraction)
- ✅ Logical volumes (virtual partitions)
- ✅ Flexibility of LVM

---

## 📝 **EXPERIMENT 4: Init Scripts**

### Test Custom Systemd Service

```bash
# STEP 1: Take snapshot
# (Snapshots: "SystemdService")

# STEP 2: Create test script
cat > /tmp/hello.sh << 'EOF'
#!/bin/bash
echo "Hello from custom service!"
date >> /tmp/service-log.txt
EOF

chmod +x /tmp/hello.sh

# STEP 3: Create systemd service file
sudo tee /etc/systemd/system/hello.service > /dev/null << 'EOF'
[Unit]
Description=Hello Service
After=network.target

[Service]
Type=oneshot
ExecStart=/tmp/hello.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

# STEP 4: Reload systemd
sudo systemctl daemon-reload

# STEP 5: Start service
sudo systemctl start hello.service

# STEP 6: Check if it ran
cat /tmp/service-log.txt
# Should show: timestamp of when service ran

# STEP 7: Enable on boot (optional)
sudo systemctl enable hello.service

# STEP 8: Check service status
sudo systemctl status hello.service

# STEP 9: Reboot and verify it runs
sudo reboot
# Wait for boot...
cat /tmp/service-log.txt
# Should have new timestamp

# STEP 10: Disable when done
sudo systemctl disable hello.service
sudo systemctl stop hello.service
```

**This teaches:**
- ✅ Service files syntax
- ✅ Service lifecycle
- ✅ Boot-time execution
- ✅ Logging and debugging

---

## 🛡️ **SAFETY CHECKLIST**

Before EACH experiment:
```
□ Experiment name decided
□ Snapshot taken with that name
□ All commands reviewed before running
□ Partition numbers verified (lsblk before command)
□ Backup taken if modifying critical files
□ Recovery plan known
□ Starting commands are read-only (list, check, verify)
```

After EACH experiment:
```
□ Document what worked
□ Document what failed
□ Note any errors/surprises
□ Test recovery (revert snapshot)
□ Take new snapshot if successful state
```

---

## 📚 **NEXT STEPS**

After mastering these 4 experiments:

1. **Read the full guides:**
   - Linux Filesystem Architecture
   - Init Systems Guide
   - Android Filesystem Architecture
   - Android Boot Process

2. **Advanced experiments:**
   - Encryption (cryptsetup)
   - Btrfs snapshots
   - Custom kernel parameters
   - Bootloader modification

3. **Real hardware:**
   - Raspberry Pi (safe hardware)
   - Old laptop (real boot process)
   - Dual boot setup (with care)

---

## 🚀 **YOUR SAFE LAB IS READY!**

You now have:
```
✅ VirtualBox (hypervisor)
✅ Linux VM (isolated OS)
✅ 50GB virtual disk (plenty of space)
✅ Snapshot capability (instant recovery)
✅ Essential tools installed
✅ 4 safe experiments ready
✅ Zero risk to your real system
```

**Golden Rule: If something breaks in VM, revert snapshot and try again. It's EXPECTED to fail during learning!**

---

## 📞 **Quick Reference**

| Task | Command |
|------|---------|
| List disks | `lsblk` |
| Show partitions | `sudo parted -l` |
| Mount disk | `sudo mount /dev/sdb1 /mnt/test` |
| Unmount | `sudo umount /mnt/test` |
| Format | `sudo mkfs.ext4 /dev/sdb1` |
| Check filesystem | `sudo fsck /dev/sdb1` |
| Create partition | `sudo parted /dev/sdb` |
| Create LVM | `sudo pvcreate /dev/sdb1` |
| List services | `sudo systemctl list-units --type=service` |
| Check service | `sudo systemctl status servicename` |
| View logs | `sudo journalctl -xe` |
| Revert snapshot | VirtualBox → Snapshots → Restore |

**Everything in your control. Learning by doing. Zero risk. 100% recovery.** 🎓
