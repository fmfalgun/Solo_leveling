# Linux Processes: Comprehensive Technical Guide
## Part 1: Process Fundamentals & Kernel Architecture

---

## Table of Contents
1. Process Basics & Kernel Architecture
2. Process Life Cycle & States
3. Process Scheduling & Context Switching
4. Memory Management & Address Spaces
5. Inter-Process Communication (IPC)

---

## 1. Process Basics & Kernel Architecture

### What is a Process?

A **process** is an abstraction that represents an executing program with its own isolated environment. Unlike a program (static code on disk), a process is a dynamic entity with allocated resources, execution context, and state.

**Key Definitions:**
- **Program**: Static executable code and data stored on disk
- **Process**: Instance of a program in execution with memory, file descriptors, and scheduling context
- **Process ID (PID)**: Unique identifier assigned by the kernel
- **Parent Process ID (PPID)**: PID of the process that spawned this process
- **Thread**: Lightweight execution unit within a process sharing memory space

### Process Structure: The `task_struct`

The Linux kernel maintains a `struct task_struct` for each process. This is the core data structure:

```c
struct task_struct {
    volatile long state;           // Process state (TASK_RUNNING, TASK_INTERRUPTIBLE, etc.)
    void *stack;                   // Kernel stack pointer
    int prio;                      // Dynamic priority
    struct mm_struct *mm;          // Memory management struct
    struct files_struct *files;    // Open file descriptors
    struct signal_struct *signal;  // Signal handlers
    struct pid *thread_pid;        // Process identifier
    struct task_struct *parent;    // Parent process pointer
    struct list_head children;     // Child processes list
    // ... 100+ additional fields
};
```

### Process Descriptor Organization

All running processes are organized in a circular linked list called the **run queue**. The kernel's process scheduler iterates this list to decide which process gets CPU time next.

**Process Descriptor Locations:**
- Stored in kernel memory (not user-accessible)
- Indexed by PID in the `PID hash table`
- Per-CPU run queues for scheduling

### User vs. Kernel Space

```
High Address (0xFFFFFFFF for 32-bit)
┌─────────────────────────────┐
│   Kernel Space              │ (Protected by MMU)
│   - Kernel Code             │
│   - Kernel Data             │
│   - Kernel Stack            │
├─────────────────────────────┤
│   User Space                │ (Isolated per process)
│   - Stack (grows down)      │
│   - Memory-mapped regions   │
│   - Heap (grows up)         │
│   - BSS (uninitialized)     │
│   - Data (initialized)      │
│   - Text (code)             │
└─────────────────────────────┘
Low Address (0x00000000)
```

**Access Protection:**
- User processes cannot directly access kernel memory
- Syscalls provide controlled access via context switch
- Memory Management Unit (MMU) enforces isolation

---

## 2. Process Life Cycle & States

### Process States (Linux Kernel)

A process can exist in several states:

```
                         TASK_RUNNING (R)
                              ↑    ↓
                              ↓    ↑
                    (Context Switch)
                              
          ↓                          ↑
    TASK_INTERRUPTIBLE         TASK_WAKEUP
         (S, Ds)              (signal/timer)
          ↓                          
    Waiting for:                    
    - I/O completion                
    - Lock acquisition              
    - Signal delivery               
          
          ↓
    TASK_UNINTERRUPTIBLE (D)
    (Deep sleep, I/O intensive)
          
          ↓
    TASK_STOPPED (T)
    (Debugger/SIGSTOP)
          
          ↓
    TASK_TRACED (t)
    (Being debugged)
          
          ↓
    EXIT_ZOMBIE (Z)
    (Waiting for parent wait())
          
          ↓
    EXIT_DEAD
    (Task struct freed)
```

**State Legend in `ps` output:**
- `R`: Running or runnable (in run queue)
- `S`: Interruptible sleep
- `D`: Uninterruptible sleep (I/O wait)
- `Z`: Zombie
- `T`: Stopped
- `t`: Traced (debugged)
- `W`: Paging (older kernels)
- `X`: Dead
- `<`: High priority
- `N`: Low priority (nice)
- `+`: In foreground process group
- `l`: Multi-threaded

### Process Creation: Fork & Exec

#### Fork System Call

```c
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

int main() {
    pid_t pid = fork();
    
    if (pid < 0) {
        perror("fork failed");
        exit(1);
    } else if (pid == 0) {
        // Child process (PID = 0 in child context)
        printf("Child: PID=%d, PPID=%d\n", getpid(), getppid());
        exit(0);
    } else {
        // Parent process (PID = child's actual PID)
        printf("Parent: Child PID=%d\n", pid);
        wait(NULL);  // Wait for child to exit
    }
    return 0;
}
```

**Fork Behavior:**
1. Creates exact copy of parent process memory space
2. Child inherits file descriptors, signal handlers, environment
3. Returns 0 in child, child's PID in parent
4. Both execute from point of fork() forward

**Copy-on-Write (CoW) Optimization:**
- Initially, child and parent share memory pages
- When either writes to a page, kernel creates separate copy
- Reduces fork overhead significantly

#### Exec System Call

```c
#include <unistd.h>
#include <stdio.h>

int main() {
    char *argv[] = {"ls", "-la", "/tmp", NULL};
    
    // Replace current process image with new program
    execv("/bin/ls", argv);
    
    // Code below never executes if execv succeeds
    perror("execv failed");
    return 1;
}
```

**Exec Variants:**
- `execl()`: List of arguments
- `execv()`: Vector (array) of arguments
- `execle()`: List with custom environment
- `execve()`: Vector with custom environment (only true syscall)
- `execlp()`: List with PATH search
- `execvp()`: Vector with PATH search

**Exec Behavior:**
1. Replaces process image (code, data, heap, stack)
2. Preserves: PID, PPID, file descriptors, signal handlers, environment
3. Does NOT fork—same process continues with new program

### Fork + Exec Pattern

```c
#include <unistd.h>
#include <sys/wait.h>
#include <stdio.h>

int main() {
    pid_t pid = fork();
    
    if (pid == 0) {
        // Child: Replace with new program
        char *argv[] = {"python3", "script.py", NULL};
        execvp("python3", argv);
        perror("execvp failed");  // Only if execvp fails
    } else if (pid > 0) {
        // Parent: Wait for child
        int status;
        waitpid(pid, &status, 0);
        printf("Child exited with status: %d\n", WEXITSTATUS(status));
    }
    return 0;
}
```

This pattern (fork + exec) is how the shell launches programs.

### Exit & Zombie Processes

```c
#include <unistd.h>
#include <stdlib.h>

int main() {
    // Option 1: Normal exit
    exit(EXIT_SUCCESS);  // Calls atexit() handlers, flushes buffers
    
    // Option 2: Immediate exit (no cleanup)
    _exit(EXIT_SUCCESS);
    
    // Option 3: Return from main
    return 0;  // Equivalent to exit(return_value)
}
```

**Zombie Process:**
- Occurs when child exits but parent hasn't called `wait()` or `waitpid()`
- Child's task_struct remains allocated to preserve exit status
- Parent retrieves exit status via `wait()`
- If parent dies without waiting, init (PID 1) adopts zombie and harvests it

---

## 3. Process Scheduling & Context Switching

### The Completely Fair Scheduler (CFS)

Modern Linux uses the **Completely Fair Scheduler** (since kernel 2.6.23), replacing the older O(1) scheduler.

**Core Concept:** Track "virtual runtime" (vruntime) to ensure all processes get fair CPU time.

### Virtual Runtime (vruntime)

```
vruntime = actual_runtime × (NICE_0_LOAD / weight)
```

- Process with lower vruntime runs next
- Niceness value (-20 to +19) adjusts weight
- Nice -20 (high priority) = weight 88761
- Nice +19 (low priority) = weight 15

**Nice Value Impact:**
```
Nice = -20: 88761 weight (highest priority)
Nice = -10: 9548 weight
Nice = 0:   1024 weight (default)
Nice = +10: 110 weight
Nice = +19: 15 weight (lowest priority)
```

### Red-Black Tree Scheduling

The CFS maintains a **red-black tree** of runnable processes:

```
                    Process_A (vruntime=100)
                   /                      \
        Process_B (vruntime=80)      Process_C (vruntime=120)
       /                                          \
Process_D (vruntime=70)                    Process_E (vruntime=130)

Leftmost node (Process_D with vruntime=70) runs next
```

**Scheduler Operations:**
1. Pick leftmost process (lowest vruntime)
2. Run for timeslice (sched_latency / nr_running)
3. Update vruntime during execution
4. Re-insert into tree

### Context Switching

**Context switch** is the process of saving one process's state and loading another's.

**What Gets Saved:**
```c
struct context {
    unsigned long rsp;      // Stack pointer
    unsigned long rbp;      // Base pointer
    unsigned long rax, rbx, rcx, rdx;  // General-purpose registers
    unsigned long rsi, rdi;
    unsigned long r8-r15;   // Extended registers (x86-64)
    unsigned long rip;      // Instruction pointer (return address)
    unsigned long rflags;   // Status flags (carry, zero, overflow, etc.)
    unsigned long cr3;      // Page table base (memory context)
    unsigned long fs_base, gs_base;  // Segment registers (TLS)
    // ... FPU, SIMD registers if used
};
```

**Context Switch Overhead:**
1. **Direct costs** (CPU cycles):
   - Save old process registers to kernel stack
   - Load new process registers from kernel stack
   - Flush TLB (Translation Lookaside Buffer) or switch page tables
   - ~1-2 microseconds per switch (depends on hardware)

2. **Indirect costs** (cache effects):
   - L1/L2/L3 CPU cache becomes stale
   - New process loads its cache lines (cache miss penalty)
   - Can cost 100-1000 microseconds in cache refill time

**Frequency of Context Switches:**
```bash
# View context switches for a process
cat /proc/<PID>/status | grep voluntary_ctxt_switches

# Global context switch rate
cat /proc/stat | grep ctxt
```

### Scheduling Classes & Priority

Linux implements multiple scheduling classes:

```
┌─────────────────────────────────────┐
│  SCHED_DEADLINE (Deadline-based)    │ (rt_priority doesn't apply)
├─────────────────────────────────────┤
│  SCHED_FIFO / SCHED_RR              │ Real-time (priority 1-99)
│  (Fixed priority with preemption)   │
├─────────────────────────────────────┤
│  SCHED_NORMAL / SCHED_BATCH         │ Timeshare (nice -20 to +19)
│  (CFS, vruntime-based)              │
├─────────────────────────────────────┤
│  SCHED_IDLE                         │ Lowest priority background
└─────────────────────────────────────┘

Higher classes preempt lower classes
```

**Set Process Scheduling Class:**
```bash
# Use chrt for real-time scheduling
chrt -p -f 10 <PID>        # SCHED_FIFO, priority 10
chrt -p -r 50 <PID>        # SCHED_RR, priority 50
chrt -p -b 0 <PID>         # SCHED_BATCH (timeshare)
chrt -p -i 0 <PID>         # SCHED_IDLE
```

### CPU Affinity

Bind process to specific CPU cores to improve cache locality:

```bash
# Run process on CPUs 0 and 2
taskset -c 0,2 ./my_program

# Check current affinity
taskset -p <PID>

# Change affinity of running process
taskset -p -c 1,3 <PID>
```

---

## 4. Memory Management & Address Spaces

### Virtual Address Space Layout

Each process has a 64-bit virtual address space on x86-64:

```
0xFFFFFFFFFFFFFFFF ┌─────────────────────────────┐
                   │   Kernel Space              │
                   │   (mapped in all contexts)  │
0xFFFF800000000000 ├─────────────────────────────┤
                   │   (gap - not accessible)   │
0x00007FFFFFFFFFFF ├─────────────────────────────┤
                   │   Stack (grows down)        │
                   │   ~8MB initial size         │
0x00007FFFFF000000 ├─────────────────────────────┤
                   │   Memory-mapped region      │
                   │   (malloc, libraries)       │
0x00005555????00000 ├─────────────────────────────┤
                   │   Heap (grows up)           │
0x???????????????? ├─────────────────────────────┤
                   │   BSS (uninitialized data)  │
0x???????????????? ├─────────────────────────────┤
                   │   Data (initialized data)   │
0x???????????????? ├─────────────────────────────┤
                   │   Text (executable code)    │
0x0000555555554000 └─────────────────────────────┘
0x0000000000000000    (typically unused)
```

**Address Space Randomization (ASLR):**
- Modern Linux randomizes base addresses of stack, heap, libraries
- Reduces predictability for exploit development
- Can be disabled: `echo 0 > /proc/sys/kernel/randomize_va_space`

### Memory Segments

| Segment | Contents | Characteristics | Viewable Via |
|---------|----------|-----------------|--------------|
| **Text** | Executable code | Read-only (usually) | `readelf -S binary` |
| **Data** | Initialized global/static vars | Writable | `objdump -d binary` |
| **BSS** | Uninitialized data | Zero-filled at startup | `size binary` |
| **Heap** | Dynamic memory (malloc) | Expands upward | `cat /proc/PID/maps` |
| **Stack** | Local variables, return addresses | Expands downward | `gdb` stack inspection |
| **Memory-mapped** | Libraries, anonymous maps | Shared/private | `cat /proc/PID/maps` |

### Process Memory Map

```bash
cat /proc/<PID>/maps
```

Example output:
```
55555554f000-55555554f000 r-xp 00000000 08:01 265133 /home/user/prog
55555554f000-55555575f000 r--p 00000000 08:01 265133 /home/user/prog
55555575f000-55555576f000 rw-p 00010000 08:01 265133 /home/user/prog
55555576f000-55555578f000 rw-p 00000000 00:00 0      [heap]
7ffff7a00000-7ffff7bdf000 r-xp 00000000 08:01 265138 /lib64/libc.so.6
...
7ffffffff000-7ffffffff000 rw-p 00000000 00:00 0      [stack]
```

**Columns:**
1. Address range (virtual)
2. Permissions (r/w/x, p=private/s=shared)
3. Offset in file
4. Device (major:minor)
5. Inode number
6. File path (or [heap], [stack], etc.)

### Page Tables & Memory Translation

Virtual address → Physical address translation happens in **page tables**.

```
Virtual Address (64-bit): [L4 index][L3 index][L2 index][L1 index][Page offset]
                           9 bits     9 bits     9 bits     9 bits    12 bits

Each level is a page table:
                     ┌──────────────────┐
                     │ Page Global Dir   │ (L4)
                     └────────┬─────────┘
                              │
                     ┌────────▼─────────┐
                     │ Page Upper Dir    │ (L3)
                     └────────┬─────────┘
                              │
                     ┌────────▼─────────┐
                     │ Page Middle Dir   │ (L2)
                     └────────┬─────────┘
                              │
                     ┌────────▼─────────┐
                     │ Page Table Entry  │ (L1)
                     │ [Physical Addr]   │
                     └──────────────────┘

Translation Lookaside Buffer (TLB):
Caches recent translations, much faster than walking page tables
```

### Copy-on-Write (CoW)

When a process forks, kernel uses CoW to save memory:

```
Parent & Child initially share pages (marked read-only in hardware):

Parent Memory     Child Memory
    A                 A  (shared)
    B                 B  (shared)
    C                 C  (shared)

Parent writes to A:
1. CPU raises page fault (write to read-only page)
2. Kernel creates copy of page A for parent
3. Parent now has private A

Parent Memory     Child Memory
    A'                A  (separate)
    B                 B  (shared)
    C                 C  (shared)
```

This optimization makes fork very cheap.

---

## 5. Inter-Process Communication (IPC)

### Process Relationships

```
init (PID 1)
├── systemd services
├── shell
│   └── child processes
│       └── grandchild processes
└── ...
```

**Parent-Child Relationships:**
- Parent process spawns child via fork+exec
- Parent can wait on child exit
- If parent dies before child, init becomes foster parent
- Child can send signals to parent

### Signals

Signals are **asynchronous notifications** to processes.

```c
#include <signal.h>
#include <stdio.h>
#include <unistd.h>

void signal_handler(int signum) {
    printf("Received signal %d\n", signum);
}

int main() {
    // Register handler for SIGTERM
    signal(SIGTERM, signal_handler);
    
    // Or using sigaction (more portable)
    struct sigaction sa;
    sa.sa_handler = signal_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    sigaction(SIGTERM, &sa, NULL);
    
    pause();  // Sleep until signal received
    return 0;
}
```

**Common Signals:**

| Signal | Default | Meaning | Catchable |
|--------|---------|---------|-----------|
| SIGHUP | Terminate | Hangup | Yes |
| SIGINT | Terminate | Interrupt (Ctrl+C) | Yes |
| SIGQUIT | Core Dump | Quit | Yes |
| SIGKILL | Terminate | Kill (cannot catch) | **No** |
| SIGSTOP | Stop | Stop process | **No** |
| SIGTERM | Terminate | Graceful terminate | Yes |
| SIGCONT | Continue | Resume stopped process | Yes |
| SIGCHLD | Ignore | Child process exited | Yes |
| SIGPIPE | Terminate | Write to closed pipe | Yes |

### Pipes

Connect stdin/stdout of processes:

```bash
# Unnamed pipe (created by shell)
cat /var/log/syslog | grep "error" | wc -l

# Named pipe (FIFO)
mkfifo /tmp/my_pipe
cat > /tmp/my_pipe &
cat < /tmp/my_pipe
```

**Pipe internals:**
```c
#include <unistd.h>
#include <stdio.h>

int main() {
    int pipefd[2];  // pipefd[0] = read end, pipefd[1] = write end
    
    if (pipe(pipefd) == -1) {
        perror("pipe");
        return 1;
    }
    
    pid_t pid = fork();
    
    if (pid == 0) {
        // Child: read from pipe
        close(pipefd[1]);  // Close write end
        char buffer[100];
        read(pipefd[0], buffer, sizeof(buffer));
        printf("Child received: %s\n", buffer);
        close(pipefd[0]);
    } else {
        // Parent: write to pipe
        close(pipefd[0]);  // Close read end
        write(pipefd[1], "Hello from parent\n", 18);
        close(pipefd[1]);
    }
    return 0;
}
```

### Message Queues

POSIX message queues enable asynchronous messaging:

```c
#include <mqueue.h>
#include <stdio.h>
#include <string.h>

int main() {
    struct mq_attr attr;
    attr.mq_maxmsg = 10;
    attr.mq_msgsize = 256;
    
    // Create message queue
    mqd_t mq = mq_open("/my_queue", O_CREAT | O_RDWR, 0644, &attr);
    
    // Send message
    char msg[] = "Hello from process A";
    mq_send(mq, msg, strlen(msg), 0);
    
    // Receive message (blocks if queue empty)
    char buffer[256];
    mq_receive(mq, buffer, 256, NULL);
    printf("Received: %s\n", buffer);
    
    mq_close(mq);
    mq_unlink("/my_queue");
    return 0;
}
```

### Shared Memory

Multiple processes access same memory region:

```c
#include <sys/shm.h>
#include <stdio.h>
#include <string.h>

int main() {
    // Create shared memory segment (1KB)
    int shmid = shmget(IPC_PRIVATE, 1024, IPC_CREAT | 0644);
    
    // Attach to process's address space
    char *shmaddr = (char *)shmat(shmid, NULL, 0);
    
    // Write data
    strcpy(shmaddr, "Shared data from process");
    
    // Other processes can attach and read
    // shmaddr = (char *)shmat(shmid, NULL, 0);
    // printf("%s\n", shmaddr);
    
    // Cleanup
    shmdt(shmaddr);
    shmctl(shmid, IPC_RMID, NULL);
    return 0;
}
```

---

## Summary

Understanding process fundamentals is critical for:
- Diagnosing performance issues (context switches, CPU affinity)
- Debugging zombie processes and resource leaks
- Developing efficient multi-process applications
- Understanding security implications of process isolation
- Configuring process-level security policies

In Part 2, we'll explore how to configure and manage processes using systemd.
