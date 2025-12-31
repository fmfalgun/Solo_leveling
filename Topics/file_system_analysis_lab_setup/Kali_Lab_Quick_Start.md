# Kali Boot-Init-FS Lab: Quick Start (1 Day Setup)
## From Zero to Working Lab in Single Day

---

## ⚡ **FASTEST PATH (6-8 hours)**

### Hour 1: Preparation

```bash
# On Kali Linux host, create lab directory
mkdir -p ~/kali-boot-lab/{vm-images,configs,scripts,analysis,isos,backups}
cd ~/kali-boot-lab/

# Install hypervisor (choose one)

# Option A: VirtualBox (GUI-friendly)
sudo apt update
sudo apt install -y virtualbox virtualbox-ext-pack
sudo usermod -aG vboxusers $USER
newgrp vboxusers

# Option B: KVM/QEMU (more performant)
sudo apt install -y qemu-kvm libvirt-daemon-system virt-manager
sudo usermod -aG libvirt $USER
sudo usermod -aG kvm $USER
newgrp libvirt

# Install analysis tools (will use throughout)
sudo apt install -y \
    e2fsprogs btrfs-progs xfsprogs lvm2 \
    parted gparted \
    sleuthkit extundelete ext4magic \
    systemd-container openrc \
    python3 python3-pip git

# Verify
virtualbox --version  # or: virsh version
```

### Hour 2-3: Download ISOs

```bash
cd ~/kali-boot-lab/isos/

# Ubuntu Server (for Systemd lab)
wget https://releases.ubuntu.com/22.04/ubuntu-22.04.3-live-server-amd64.iso

# Alpine Linux (for SysV/OpenRC lab)
wget https://alpinelinux.org/downloads/
# Direct: https://dl-cdn.alpinelinux.org/alpine/v3.18/releases/x86_64/alpine-3.18.4-x86_64.iso

# SystemRescue (recovery/forensics)
wget https://sourceforge.net/projects/systemrescuecd/files/x86_64/systemrescue-11.00-amd64.iso

# Verify sizes (should match download page)
ls -lh *.iso

# Expected:
# ubuntu-22.04.3-live-server-amd64.iso  ~1.3GB
# alpine-3.18.4-x86_64.iso              ~200MB
# systemrescue-11.00-amd64.iso          ~700MB
```

### Hour 4-5: Create First VM (Systemd Lab)

```bash
# Using VirtualBox GUI (easiest):

# 1. Open VirtualBox
virtualbox &

# 2. Click "New"
# 3. Fill in:
#    - Name: "Kali-Boot-Lab-Systemd"
#    - Type: Linux
#    - Version: Ubuntu (64-bit)
#    - Memory: 8GB (8192 MB)
#    - Disk: 50GB, VDI, Dynamic

# 4. Click "Create"

# 5. Before starting, attach ISO:
#    - Right-click VM → Settings → Storage
#    - Click "Empty" under IDE
#    - Click folder icon → Select ubuntu-22.04.3.iso
#    - Click OK

# 6. Start VM (double-click VM name)

# 7. Follow Ubuntu installation
#    - Choose "Ubuntu Server"
#    - Default network/disk options OK
#    - Create user: labuser / password: (anything)
#    - Select: SSH Server + Standard utilities
#    - Complete installation (takes 5-10 min)

# 8. After first boot, inside VM:
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential linux-headers-generic

# 9. Back on Kali host, take snapshot:
vboxmanage snapshot "Kali-Boot-Lab-Systemd" take "Fresh-Install"
```

### Hour 6: Second VM (Alpine/SysV Lab)

```bash
# Repeat similar process for Alpine VM

# Create new VM in VirtualBox:
# - Name: "Kali-Boot-Lab-Alpine"
# - Type: Linux
# - Version: Other Linux (64-bit)
# - Memory: 4GB
# - Disk: 20GB
# - Attach: alpine-3.18.4-x86_64.iso

# Alpine installation is simpler:
# 1. Boot from ISO
# 2. Type: setup-alpine
# 3. Accept defaults for most prompts
# 4. Disk: sda, sys (standard)
# 5. Reboot, remove ISO

# After boot:
apk update
apk add openrc openssh build-base linux-headers

# Enable SSH
rc-service sshd start
rc-update add sshd

# On Kali host, take snapshot:
vboxmanage snapshot "Kali-Boot-Lab-Alpine" take "Fresh-Install"
```

### Hour 7-8: Setup Lab Structure

```bash
# Create analysis workspace on Kali

cat > ~/kali-boot-lab/README.md << 'EOF'
# Kali Boot, Init & Filesystem Analysis Lab

## Setup Date: $(date)
## Host: Kali Linux
## VMs Created:
- [ ] Systemd Lab (Ubuntu 22.04)
- [ ] SysV/Alpine Lab
- [ ] Recovery Tools (SystemRescue)

## Quick Links
- Systemd VM IP: $(ssh labuser@[IP] "hostname -I")
- Alpine VM IP: $(ssh root@[IP] "hostname -I")

## Lab Workflow:
1. SSH into VM
2. Modify configs/services
3. Analyze with scripts
4. Revert via snapshot if needed
EOF

# Create quick analysis script
cat > ~/kali-boot-lab/scripts/analyze.sh << 'EOF'
#!/bin/bash
# Quick boot analysis (run in VM via SSH)

VM_IP=$1
VM_USER=${2:-labuser}

ssh $VM_USER@$VM_IP << 'EOFSCRIPT'
echo "=== Boot Analysis ==="
echo "Kernel: $(uname -r)"
echo "Init: $(ps -p1 -o comm=)"
echo "Boot time: $(systemd-analyze 2>/dev/null | grep "Startup")"
echo ""
echo "=== Services ==="
systemctl list-units --type=service 2>/dev/null || \
  rc-service --list
echo ""
echo "=== Mounts ==="
mount | grep -v "tmpfs\|sysfs"
EOFSCRIPT
EOF

chmod +x ~/kali-boot-lab/scripts/analyze.sh

echo "Lab setup complete!"
```

---

## 🎯 **TODAY: YOUR FIRST EXPERIMENTS**

### Experiment 1: Compare Boot Times (30 min)

```bash
# In Systemd VM (via SSH)
ssh labuser@[systemd-vm-ip]

# Capture boot timing
systemd-analyze > /tmp/boot-timing.txt
systemd-analyze blame | head -20 > /tmp/slowest-services.txt

# View
cat /tmp/boot-timing.txt
cat /tmp/slowest-services.txt

# Copy to Kali for analysis
exit
scp labuser@[systemd-vm-ip]:/tmp/boot-timing.txt ~/kali-boot-lab/analysis/

# In Alpine VM
ssh root@[alpine-vm-ip]

# Check boot time (rough estimate)
uptime
dmesg | grep -E "CPU|memory|startup" | tail -5

# Compare with Systemd (huge difference!)
exit
```

### Experiment 2: Analyze Init System (30 min)

```bash
# Systemd analysis (in Systemd VM)
ssh labuser@[systemd-vm-ip]

# View service dependencies
systemctl list-dependencies multi-user.target | head -20

# Graph dependencies
systemd-analyze plot > /tmp/deps.svg

# Check specific service
systemctl show ssh

# Modify a service (test)
sudo cp /lib/systemd/system/ssh.service /etc/systemd/system/
sudo vim /etc/systemd/system/ssh.service
# Add line under [Unit]: StandardOutput=journal
sudo systemctl daemon-reload
sudo systemctl restart ssh
journalctl -u ssh -n 10

# SysV analysis (in Alpine VM)
ssh root@[alpine-vm-ip]

# View services
ls /etc/init.d/

# View runlevels
ls /etc/rc*.d/

# Check service config
cat /etc/init.d/sshd

# Revert Systemd changes (on Kali host)
vboxmanage snapshot "Kali-Boot-Lab-Systemd" restore "Fresh-Install"
# Click OK to confirm revert
```

### Experiment 3: Filesystem Analysis (30 min)

```bash
# On Kali host: Create raw image from running VM

# First, shutdown VM gracefully
ssh labuser@[systemd-vm-ip] "sudo shutdown -h now"

# Copy disk image
cd ~/kali-boot-lab/vm-images/
cp systemd-lab.vdi systemd-lab-snapshot.vdi

# Convert to raw format (if needed for analysis)
# qemu-img convert -f vdi -O raw systemd-lab.vdi systemd-lab.img

# Mount for forensic analysis
mkdir -p /mnt/forensic-analysis
# Note: VDI is VirtualBox format; convert or mount carefully

# Alternative: Create raw ext4 image from scratch
dd if=/dev/zero of=forensic-sample.img bs=1M count=1
dd if=/dev/zero of=forensic-sample.img bs=1M seek=9999 count=1
mkfs.ext4 -F forensic-sample.img

# Mount it
sudo mount -o loop,ro forensic-sample.img /tmp/forensic-test

# Audit filesystem
python3 ~/kali-boot-lab/scripts/fs-audit.py /tmp/forensic-test

# Unmount
sudo umount /tmp/forensic-test
```

### Experiment 4: Boot Modification Testing (30 min)

```bash
# In Systemd VM: Modify kernel parameters

ssh labuser@[systemd-vm-ip]

# View current parameters
cat /proc/cmdline

# Edit GRUB
sudo vim /etc/default/grub

# Add to GRUB_CMDLINE_LINUX:
#   console=ttyS0 debug verbose

# Update GRUB
sudo update-grub2

# Reboot and observe
sudo shutdown -r now

# After reboot, check
cat /proc/cmdline
dmesg | tail -30

# Revert snapshot if needed
# (On Kali host)
vboxmanage snapshot "Kali-Boot-Lab-Systemd" restore "Fresh-Install"
```

---

## 📋 **CHECKLIST: First Day Complete?**

```
✓ Kali host tools installed
✓ Hypervisor (VirtualBox or KVM) installed
✓ ISOs downloaded (Ubuntu, Alpine, SystemRescue)
✓ 2 VMs created (Systemd + Alpine)
✓ Both VMs snapshots taken
✓ 4 experiments completed
✓ Analysis results saved
✓ Lab automation scripts created

Ready for: Advanced experiments, custom tools, forensics
```

---

## 🚀 **NEXT WEEK: BUILD ON THIS**

```
Week 2 Topics:
├─ Boot order modification
├─ Initramfs analysis/modification
├─ Custom init system creation
├─ Kernel parameter injection
├─ SELinux/AppArmor interactions
├─ Filesystem attack vectors
└─ Recovery tool mastery

Tools to develop:
├─ Boot analyzer (Python)
├─ Service dependency visualizer
├─ Filesystem auditor
├─ Timeline generator
└─ Anomaly detector
```

---

## 💾 **BACKUP STRATEGY**

```bash
# After successful setup, backup VMs

cd ~/kali-boot-lab/backups/

# Compress VM disks (one-time)
tar czf systemd-lab-20250101.tar.gz ~/kali-boot-lab/vm-images/systemd-lab.vdi

# Weekly incremental
rsync -av ~/kali-boot-lab/vm-images/ ./weekly-backup/

# Keep 4 week backups
ls -d weekly-backup-* | sort -r | tail -n +5 | xargs rm -rf
```

---

## 🔧 **DURING LAB SESSIONS**

```bash
# Template workflow for experiments:

# 1. SSH into VM
ssh labuser@[VM-IP]

# 2. Perform modifications
sudo vim /etc/systemd/system/something.service
sudo systemctl daemon-reload
sudo systemctl restart something

# 3. Analyze results
journalctl -u something -n 20
systemctl status something

# 4. Copy results back
exit
scp labuser@[VM-IP]:/tmp/results.txt ~/kali-boot-lab/analysis/

# 5. If broken, revert snapshot (on Kali host)
vboxmanage snapshot "VM-Name" restore "Fresh-Install"

# 6. Document findings
vim ~/kali-boot-lab/analysis/experiment-log.md
```

---

## 🎓 **SUCCESS INDICATORS**

You'll know the lab is working when:

```
✓ Can SSH into both VMs
✓ Can run systemd-analyze in Systemd VM
✓ Can view services in Alpine VM
✓ Can mount and analyze disk images
✓ Can revert VMs via snapshots (5-10 seconds)
✓ Boot times consistent (same VM reboots)
✓ Analysis scripts collect data without errors
```

---

**You're now ready for boot + init + filesystem research!** 🚀

Start with the experiments above, then move to the full guide for deeper topics.

Use snapshots liberally. Experiment fearlessly. Learn systematically.
