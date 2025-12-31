# Process Lifecycle & /proc Reflection: Complete Reference

## Part 1: How Linux Processes Are Initiated

### Method A: User Shell Command Execution
```bash
$ /usr/bin/Xorg :0 -seat seat0 -auth /run/lightdm/seat0/Xauthority
```

**What happens:**
1. Shell calls `fork()` → creates child process (COW parent memory)
2. Child calls `execve()` → loads Xorg binary
3. Kernel creates `/proc/$pid/` directory
4. Process inherits:
   - File descriptors (0=stdin, 1=stdout, 2=stderr)
   - Environment variables
   - Working directory
   - User/group credentials

---

### Method B: Systemd Service Startup
```bash
# /etc/systemd/system/postgres.service
[Service]
ExecStart=/usr/lib/postgresql/18/bin/postgres -D /var/lib/postgresql/18/main
User=postgres
```

**What happens:**
1. systemd reads `.service` file
2. systemd forks → creates child process
3. Child drops privileges to `postgres` user
4. Child `execve()` postgres binary
5. `/proc/$pid/` created with postgres attributes

---

### Method C: Direct Process Spawning (Multi-process)
```bash
/opt/brave.com/brave/brave --type=renderer
```

**What happens:**
1. Parent Brave process calls `fork()` multiple times
2. Each child may call `execve()` or stay within binary
3. Multiple `/proc/$pid/` entries created
4. Threads share memory but have separate `/proc/$pid/task/$tid/` entries

---

## Part 2: Real Examples from /proc Dump

### Example 1: Xorg Display Server

**Initiation:**
- Command: `/usr/lib/xorg/Xorg :0 -seat seat0 ...`
- PID: 1432
- User: root
- Initiated by: lightdm

**Files in `/proc/1432/`:**

**Identity:**
- `cmdline` → Full command with all arguments
- `comm` → "Xorg" (short name)
- `exe` → symlink to `/usr/lib/xorg/Xorg`
- `environ` → DISPLAY=:0, XAUTHORITY=/run/lightdm/seat0/Xauthority

**State (Updated Continuously):**
- `stat` → PID 1432, state S (sleeping), CPU times, threads
- `statm` → Memory: total_vm, resident, shared (in pages)
- `status` → Human-readable version

**File Descriptors (Open Files & Logs):**
- `fd/0` → /dev/null (stdin)
- `fd/1` → /var/log/lightdm/x-0.log (stdout → log)
- `fd/2` → /var/log/Xorg.0.log (stderr → log)
- `fd/6` → /var/log/Xorg.0.log (additional handle)
- `fd/7-50` → Various sockets, GPU devices, input devices

**Memory:**
- `maps` → 100+ lines showing all virtual memory regions
- `smaps` → Detailed per-region stats (RSS, dirty, shared)

---

### Example 2: PostgreSQL Database Server

**Initiation:**
- Command: `/usr/lib/postgresql/18/bin/postgres -D /var/lib/postgresql/18/main`
- PID: 179820 (main), 179821-179830 (child processes/threads)
- User: postgres
- Initiated by: systemd

**Key Files:**
- `stat` → State S, parent systemd (PID 1)
- `statm` → 2GB virtual, 512MB resident
- `fd/1` → /var/log/postgresql/postgresql-18-main.log (output)
- `fd/5` → socket:16765 (UNIX socket for connections)
- `fd/6-100` → More sockets (one per client connection)
- `cgroup` → /system.slice/postgresql-18.service (systemd managed)
- `task/` → Multiple threads (bgwriter, autovacuum, checkpointer)

**Network:**
- `net/tcp` → LISTEN on port 5432
- `net/unix` → LISTEN on /var/run/postgresql/.s.PGSQL.5432

---

### Example 3: Brave Browser (Multi-process)

**Initiation:**
- Command: `/opt/brave.com/brave/brave --type=renderer`
- PIDs: 140647, 140648, 140649, 144237, 145583, 179605+ (50+ processes)
- User: regular user
- Parent: systemd or shell

**Example PID 145583 (Renderer):**
- `cmdline` → `/opt/brave.com/brave/brave --type=renderer --enable-features=...`
- `statm` → 256MB virtual, 128MB resident (per process)
- `fd/` → 100+ entries:
  - `fd/0-2` → /dev/null, pipes
  - `fd/3-10` → PAK files (resources)
  - `fd/11-40` → Socket connections (X11, D-Bus)
  - `fd/25` → Dictionary files
  - `fd/43-48` → Font files (.ttf)
  - `fd/31-32` → /proc/../statm, status (monitoring siblings!)
  - `fd/24,28,32` → /dev/shm (shared memory, deleted)
  - `fd/181+` → More sockets, eventfd, memfd

**Memory:**
- `maps` → 500+ lines showing:
  - Binary code: /opt/brave.com/brave/brave
  - Shared resources: .pak files, fonts, locale archive
  - Anonymous: heap memory
- `smaps` → Per-region detailed stats

**Threading:**
- `task/145583` → Main thread
- `task/145584-145590` → Worker threads (I/O, rendering, GC)

---

## Part 3: /proc File Creation Timeline

### When Kernel Creates `/proc/$pid/` Entries

#### Fork Event
```
kernel/fork.c: copy_process() 
  → PID allocation
  → /proc/$pid/ directory created
  → stat, statm, status: initialized with fork-time data
```

#### Exec Event
```
fs/exec.c: load_elf_binary()
  → exe updated to new binary
  → cmdline updated to new command
  → maps cleared and rebuilt (new memory layout)
  → statm reset (new page counts)
```

#### During Execution
```
Every scheduler tick (~1-10ms):
  → stat updated (CPU time, state, vruntime)
  → sched, schedstat updated (scheduling stats)

Every mmap/munmap:
  → maps updated (new/removed regions)
  → smaps recalculated (per-region stats)

Every open/close/read/write:
  → fd/ updated (new symlinks, deleted entries)
  → fdinfo/ updated (position, flags)
  → io updated (counters increment)
```

---

## Part 4: State Transition Matrix

| Event | Files Updated | What Changes |
|-------|------|-----------|
| **fork()** | stat, statm, status, task/ | All initialized, state=R/S |
| **exec()** | exe, cmdline, environ, maps, statm | New paths, new memory layout |
| **Running** | stat, sched, schedstat | vruntime increases, state=R |
| **Blocked** | stat (state=D/S), wchan, stack | Shows kernel function |
| **File open** | fd/NNN, fdinfo/NNN, io | New symlink, pos=0 |
| **Memory alloc** | maps, smaps, statm | New VMA, RSS increases |
| **Memory free** | smaps, statm | VMA removed, RSS decreases |
| **Signal received** | status (SigPnd) | Signal bitmap updated |
| **Process exits** | stat (state=Z), cgroup | Becomes zombie |

---

## Part 5: How to Interpret Execution from /proc

### Real-time Process Monitoring
```bash
#!/bin/bash
PID=145583

watch -n 0.1 'cat /proc/'$PID'/stat | awk "{print \$2, \$3, \$14+\$15, \$22}"'
# Outputs: comm state cpu_time starttime
# Watch values change live!
```

### Determine Process Blocked State
```bash
# Read wchan to see what kernel function it's waiting on
cat /proc/$PID/wchan
# Examples: 143 (sleep), 956 (poll), ep_poll, futex_wait

# If state=Z (zombie)
state=$(awk '{print $3}' /proc/$PID/stat)
if [[ $state == 'Z' ]]; then
  echo "Zombie - parent needs to wait!"
fi
```

### Track Memory Growth
```bash
# Sample every second
for i in {1..60}; do
  rss=$(awk '{print $6*4}' /proc/$PID/stat)  # RSS in KB
  echo "$(date): RSS=$rss KB"
  sleep 1
done
```

### Find What Files a Process Uses
```bash
# List all files
ls -l /proc/$PID/fd/ | awk '{print $NF}'

# This shows what files, sockets, pipes it's using
# Can detect log files, temp files, etc.
```

---

## Part 6: Complete File Reference (50+ Files)

### Core Identity Files
| File | Purpose | Example Content |
|------|---------|-----------------|
| `stat` | CPU scheduling state (CRITICAL) | PID, state, ppid, cpu, nice, starttime, rss, threads, etc. |
| `statm` | Memory layout | total_vm resident shared text data |
| `status` | Human-readable state | Name, State, Threads, VmRSS, Capabilities |
| `cmdline` | Command line | /opt/brave.com/brave/brave --type=renderer |
| `comm` | Executable short name | Chromium_ChildIOT |
| `exe` | Path to executable | → /opt/brave.com/brave/brave |
| `cwd` | Current directory | → /home/user |
| `root` | Process root | → / |

### Memory Files
| File | Purpose | Content |
|------|---------|---------|
| `maps` | Virtual memory layout | 100-500+ lines of memory regions |
| `mapfiles` | File-backed memory | Memory regions backed by files |
| `smaps` | Detailed per-VMA stats | Size, RSS, PSS, Dirty, Shared, Anonymous |
| `smaps_rollup` | Aggregated stats | Total of all VMAs |
| `pagemap` | Per-page info | 8 bytes per page (binary) |
| `mem` | Raw memory access | Process virtual address space |

### File Descriptor Files
| File | Purpose | Entries |
|------|---------|---------|
| `fd/` | Open file descriptors | 0, 1, 2, 3, ... 181+ |
| `fdinfo/` | FD metadata | pos, flags, mnt_id for each |

### Scheduling Files
| File | Purpose | Update Rate |
|------|---------|-------------|
| `sched` | Scheduler stats | Continuous |
| `schedstat` | CPU/wait time | Continuous |
| `wchan` | Sleep address | On state change |
| `stack` | Kernel stack | On read |
| `autogroup` | CFS autogrouping | On creation |

### I/O & Resources
| File | Purpose | Scope |
|------|---------|-------|
| `io` | I/O counters | Cumulative since start |
| `limits` | RLIMIT values | Per-process settings |
| `oom_score` | OOM priority | 0-1000 |
| `oom_score_adj` | OOM adjustment | -1000 to +1000 |

### Security & Isolation
| File/Dir | Purpose | Content |
|----------|---------|---------|
| `attr/` | LSM attributes | current, exec, prev, fscreate, keycreate |
| `apparmor/` | AppArmor state | current, exec, prev |
| `ns/` | Namespace refs | cgroup, ipc, mnt, net, pid, user, uts |
| `uid_map` | User namespace | UID mappings |
| `gid_map` | Group namespace | GID mappings |
| `cgroup` | Cgroup membership | Hierarchy paths |

### Threading & Children
| File/Dir | Purpose | Entries |
|----------|---------|---------|
| `task/` | Per-thread subdir | $tid/stat, $tid/statm, ... |
| `children` | Child PIDs | Space-separated list |

### Network (Per-Process View)
| File | Purpose | Content |
|------|---------|---------|
| `net/tcp` | TCP sockets | Connection table |
| `net/tcp6` | IPv6 TCP | IPv6 connections |
| `net/udp` | UDP sockets | Datagram info |
| `net/unix` | UNIX sockets | IPC sockets |
| `net/route` | Routing table | IP routes |
| + 40+ more | Network info | Various protocols |

---

**This is your complete reference for understanding process lifecycle and /proc reflection!**

