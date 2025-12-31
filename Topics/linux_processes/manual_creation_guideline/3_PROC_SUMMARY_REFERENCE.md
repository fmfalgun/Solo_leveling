# /proc Process Files: Summary Reference & Quick Lookup

## At a Glance: Process Lifecycle

```
fork() syscall
    ↓ (Kernel creates /proc/$pid/)
Executable loaded (exec)
    ↓ (exe, maps, statm updated)
Running / Sleeping / I/O Blocked
    ↓ (stat, sched, fd, io updated continuously)
Signal received / File opened / Memory allocated
    ↓ (appropriate /proc files updated)
Process exits / Killed
    ↓ (state=Z in /proc/$pid/stat)
Parent waits (wait4)
    ↓ (Kernel deletes /proc/$pid/)
Gone from system
```

---

## Quick Process Identification

| Need to know... | Check file... | Example |
|---|---|---|
| **What command started this?** | `cmdline` | `/usr/lib/postgresql/18/bin/postgres -D /var/lib/postgresql/18/main` |
| **What executable?** | `exe` | → `/usr/lib/postgresql/18/bin/postgres` |
| **Short name?** | `comm` | `postgres` |
| **Current state (sleeping/running)?** | `stat` (3rd field) | `S` = sleeping, `R` = running, `Z` = zombie |
| **How much memory in use?** | `statm` (2nd field) or `status` VmRSS | `524288` pages = 2GB, or `VmRSS: 512000 kB` |
| **What files is it using?** | `fd/` symlinks | `fd/1 → /var/log/postgresql/postgresql-18-main.log` |
| **Where is it waiting?** | `wchan` | `143` = kernel sleep, or `-` if running |
| **Is it a zombie?** | `stat` field 3 | If `state=Z`, parent must do wait() |
| **How many threads?** | `status` Threads field | `Threads: 4` |
| **Parent process ID?** | `stat` field 4 | `140647` |
| **CPU time accumulated?** | `stat` fields 14+15 | jiffies (divide by 100 for seconds) |

---

## File Category Cheat Sheet

### Identity & Execution (Read Once)
```
cmdline    → Full command line
comm       → Short name
exe        → Executable path
environ    → Environment variables
cwd        → Current directory
root       → Process root (chroot)
auxv       → ELF auxiliary data
```

### State & Scheduling (Read Frequently)
```
stat       → KEY: All in one line (PID, state, ppid, cpu, nice, etc.)
statm      → Memory: virt, resident, shared, text, data (pages)
status     → Human-readable version of stat + extras
sched      → Detailed scheduler stats
schedstat  → CPU time on core, wait time, context switches
wchan      → Kernel function if sleeping, else "-"
autogroup  → CFS autogrouping info
```

### Memory (Read for Performance Analysis)
```
maps       → Full virtual address map (100s of lines)
smaps      → Detailed per-VMA stats (RSS, PSS, shared, etc.)
smaps_rollup → Aggregated smaps
pagemap    → Per-page information (present, swapped, soft-dirty)
numamaps   → NUMA distribution
mem        → Direct memory access (pseudo-file)
```

### File Descriptors (Real-time Log/Socket Tracking)
```
fd/        → Directory: symlinks to actual files/sockets/pipes
            Examples:
            fd/0 → /dev/null
            fd/1 → /var/log/postgresql.log (stdout)
            fd/5 → socket:16765 (network socket)
fdinfo/    → Directory: metadata for each fd
            fd/1: pos=123456, flags=02000001, mnt_id=32
```

### I/O & Resources
```
io         → Read/write syscall counts and byte totals
limits     → RLIMIT values (open files, stack, memory, etc.)
oom_score  → How likely to be killed by OOM killer
oom_score_adj → User adjustment (-1000 to +1000)
```

### Security & Isolation
```
attr/      → LSM attributes (AppArmor, SELinux)
apparmor/  → AppArmor profile state
loginuid   → Audit login UID
```

### Namespaces & Containers
```
ns/        → Symlinks to namespace references
uid_map    → User namespace UID mapping
gid_map    → Group namespace GID mapping
setgroups  → Allow setgroups()?
cgroup     → Cgroup membership
```

### Threading
```
task/      → Directory of per-thread subdirs
            task/145583/ → Main thread
            task/145584/ → Thread 2
children   → List of child process PIDs
```

### Mounts & Filesystem
```
mountinfo  → Detailed per-mount info
mounts     → Simple mount table
mountstats → Extended mount stats
```

---

## Real-Time Monitoring by Use Case

### Monitor CPU Usage
```bash
while true; do
  stats=$(awk '{print $14":"$15}' /proc/$PID/stat)
  echo "$(date): utime:stime = $stats"
  sleep 1
done
```

### Monitor Memory Growth
```bash
watch -n 1 'cat /proc/$PID/statm | awk "{print \$1,\$2,\$3}"'
# Shows: total_vm(pages) resident(pages) shared(pages)
```

### Track All Open Files/Sockets
```bash
# One-time snapshot
ls -l /proc/$PID/fd/ | awk '{print $NF}'

# Or follow changes
inotifywait -m /proc/$PID/fd/ -e create,delete
```

### Find Process Blocked State
```bash
cat /proc/$PID/wchan
# Returns: function name if sleeping, "-" if running
# Examples: ep_poll, futex_wait, do_sys_open, etc.
```

### Check If Process Is a Zombie
```bash
state=$(awk '{print $3}' /proc/$PID/stat)
if [[ $state == 'Z' ]]; then echo "ZOMBIE"; fi
```

### Trace Memory Mappings
```bash
# What shared libraries loaded?
grep '.so' /proc/$PID/maps | awk '{print $NF}'

# Show all details
cat /proc/$PID/smaps | head -50
```

### Check Network Connections
```bash
# What ports listening?
cat /proc/$PID/net/tcp | awk '$4=="0A"'

# What UNIX sockets connected?
cat /proc/$PID/net/unix
```

### Monitor Threads
```bash
# How many threads running?
ls /proc/$PID/task/ | wc -l

# Get stat for each thread
for tid in $(ls /proc/$PID/task/); do
  echo "Thread $tid: $(awk '{print $3}' /proc/$PID/task/$tid/stat)"
done
```

---

## File Descriptions by Category

### Process State (Continuously Updated)

| File | How Often | What It Shows |
|------|-----------|---------------|
| `stat` | Every jiffy (~1-10ms) | PID, state, CPU, memory, threads, etc. (50+ fields) |
| `statm` | Every jiffy | Memory: virt, resident, shared, text, data (pages) |
| `status` | Every jiffy | Human-readable version of stat + extras |
| `sched` | Periodically | vruntime, sleep_time, migrations, wakeups |
| `schedstat` | Periodically | CPU time on CPU, wait time, context switches |
| `wchan` | On state change | Kernel function if sleeping; "-" if runnable |

### Memory Layout (Updated on mmap/munmap)

| File | Size | When Updated |
|------|------|--------------|
| `maps` | 10-100 KB | On malloc/free, dlopen, mmap syscalls |
| `smaps` | 50-200 KB | On demand (expensive to compute) |
| `pagemap` | MB-range | Tracks page state (present, swapped) |

### File Descriptors (Real-Time I/O Visibility)

| File/Dir | # Entries | Updated When |
|----------|-----------|--------------|
| `fd/` | 0-300+ | File opened/closed or socket created |
| `fdinfo/` | Same as fd/ | FD position or flags change |

---

## Practical Debugging Examples

### Scenario 1: Process Using Too Much Memory
```bash
# Check resident set size
rss=$(awk '{print $6*4}' /proc/$PID/stat)
echo "RSS: $rss KB"

# Check what's mapped
cat /proc/$PID/smaps | grep "Rss:" | awk '{sum+=$2} END {print "Total:", sum}'

# Find largest mapping
cat /proc/$PID/smaps | awk '/^[0-9a-f]/ {size=$1; next} /^Rss:/ {print size, $2}' | sort -k2 -rn | head
```

### Scenario 2: Process Hung/Blocked
```bash
# Check state
state=$(awk '{print $3}' /proc/$PID/stat)
echo "State: $state (R=running, S=sleep, D=disk, Z=zombie)"

# If sleeping, see where
wchan=$(cat /proc/$PID/wchan)
echo "Blocked in: $wchan"

# See stack
cat /proc/$PID/stack
```

### Scenario 3: High CPU Usage
```bash
# Get CPU times
awk '{print "utime=" $14 " stime=" $15}' /proc/$PID/stat

# Calculate percentage over time
old_time=$(awk '{print $14+$15}' /proc/$PID/stat)
sleep 1
new_time=$(awk '{print $14+$15}' /proc/$PID/stat)
cpu_percent=$(( (new_time - old_time) * 100 / 100 ))
echo "CPU: $cpu_percent%"
```

### Scenario 4: Track Process File Access
```bash
# What files currently open?
ls -l /proc/$PID/fd/ | grep -E '\.(log|tmp|txt)'

# What sockets connected?
ls /proc/$PID/fd/ | xargs -I {} readlink /proc/$PID/fd/{} | grep socket

# Monitor in real-time
watch -n 0.5 'ls /proc/'$PID'/fd/ | wc -l'
```

### Scenario 5: Check Process Namespace Isolation
```bash
# Is process in custom namespaces?
ls -i /proc/$PID/ns/
ls -i /proc/1/ns/        # Compare with init
# Same inode = same namespace

# In container?
cat /proc/$PID/cgroup | grep docker
```

---

## Essential Commands

```bash
# Get all files in /proc/$pid
ls -la /proc/$PID/ 2>/dev/null | awk '{print $NF}'

# Quick process snapshot
cat /proc/$PID/stat /proc/$PID/status | head -20

# Find process' main log file
readlink /proc/$PID/fd/1 /proc/$PID/fd/2

# Count threads
ls /proc/$PID/task | wc -l

# Check if zombie
ps aux | grep $PID | grep -q '<defunct>' && echo "ZOMBIE" || echo "ALIVE"

# Memory in human-readable
awk '{printf "RSS: %.1f MB\n", $6*4/1024}' /proc/$PID/statm

# CPU time accumulated (in seconds)
awk '{printf "CPU: %.1f sec\n", ($14+$15)/100}' /proc/$PID/stat

# I/O counters
tail -5 /proc/$PID/io
```

---

This is your **daily reference guide**. Keep it handy for debugging!

