# Linux Processes: Comprehensive Technical Guide
## Part 4: Custom Daemon Development in C and Python

---

## Table of Contents
1. Daemon Fundamentals
2. Creating Daemons in C
3. Creating Daemons in Python
4. Process Forking & Daemonization
5. Practical Examples: Security Tools
6. Signal Handling in Daemons
7. Inter-Process Communication Patterns
8. Testing & Debugging Daemons

---

## 1. Daemon Fundamentals

### What is a Daemon?

A **daemon** is a background process that:
- Runs without a controlling terminal
- Has no stdin/stdout/stderr connected to the terminal
- Is immune to terminal signals (Ctrl+C won't kill it)
- Runs continuously or periodically
- Has PID > 1 (not init)
- Is usually a child of init or systemd

**Difference between process and daemon:**
```
Regular Process            Daemon Process
├─ Attached to terminal    ├─ No terminal attachment
├─ stdin/stdout/stderr     ├─ stdin/stdout → /dev/null
├─ Killed by Ctrl+C        ├─ Survives terminal close
├─ Foreground execution    └─ Background execution
└─ Limited lifetime            (until explicit kill)
```

### Daemonization Steps

Converting a regular process to a daemon requires:

1. **Fork child process** - Parent exits
2. **Make child session leader** - `setsid()` to create new session
3. **Change directory** - Usually to `/` or `/var/run`
4. **Reset file descriptors** - Close/redirect stdin/stdout/stderr
5. **Reset permissions** - Clear umask
6. **Signal handling** - Ignore HUP, handle TERM/INT
7. **PID file** - Record daemon's PID
8. **Lock file** - Prevent multiple instances

### Process Hierarchy for Daemon

```
Regular foreground process:
  ┌─ Shell (bash)
  └─ └─ Process (PID 1234)
           └─ stdin/stdout/stderr from terminal
           └─ Process group same as shell

Daemon process:
  ┌─ Init/Systemd (PID 1)
  └─ └─ Daemon (PID 5678)
           ├─ No controlling terminal
           ├─ New session (different from shell)
           ├─ stdin/stdout/stderr → /dev/null
           └─ Process group != shell
```

---

## 2. Creating Daemons in C

### Complete C Daemon Template

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <syslog.h>
#include <errno.h>
#include <string.h>

/* Global flag for graceful shutdown */
volatile sig_atomic_t shutdown_flag = 0;

/* Signal handler for clean shutdown */
void signal_handler(int signum) {
    if (signum == SIGTERM || signum == SIGINT) {
        shutdown_flag = 1;
    }
}

/* Daemonize the process */
int daemonize(const char *pidfile_path) {
    pid_t pid;
    int fd;
    
    /* Step 1: Fork to background */
    pid = fork();
    if (pid < 0) {
        perror("fork");
        return -1;
    }
    
    /* Parent exits */
    if (pid > 0) {
        exit(EXIT_SUCCESS);
    }
    
    /* Step 2: Create new session (become session leader) */
    if (setsid() < 0) {
        perror("setsid");
        return -1;
    }
    
    /* Step 3: Change working directory to root */
    if (chdir("/") < 0) {
        perror("chdir");
        return -1;
    }
    
    /* Step 4: Reset file descriptors */
    
    /* Redirect stdin to /dev/null */
    fd = open("/dev/null", O_RDONLY);
    if (fd < 0) {
        perror("open /dev/null");
        return -1;
    }
    if (dup2(fd, STDIN_FILENO) < 0) {
        perror("dup2 stdin");
        return -1;
    }
    close(fd);
    
    /* Redirect stdout/stderr to syslog or file */
    fd = open("/var/log/mydaemon.log", O_WRONLY | O_CREAT | O_APPEND, 0644);
    if (fd < 0) {
        perror("open logfile");
        return -1;
    }
    if (dup2(fd, STDOUT_FILENO) < 0 || dup2(fd, STDERR_FILENO) < 0) {
        perror("dup2 stdout/stderr");
        return -1;
    }
    close(fd);
    
    /* Step 5: Reset umask */
    umask(0);
    
    /* Step 6: Set up syslog */
    openlog("mydaemon", LOG_PID, LOG_DAEMON);
    
    /* Step 7: Write PID file */
    if (pidfile_path) {
        FILE *pf = fopen(pidfile_path, "w");
        if (pf) {
            fprintf(pf, "%d\n", getpid());
            fclose(pf);
        } else {
            syslog(LOG_WARNING, "Cannot write PID file: %s", pidfile_path);
        }
    }
    
    return 0;
}

/* Main daemon loop */
int main(int argc, char *argv[]) {
    /* Pre-daemonize: check for required files */
    if (access("/etc/mydaemon.conf", R_OK) < 0) {
        fprintf(stderr, "Config file not found: /etc/mydaemon.conf\n");
        exit(EXIT_FAILURE);
    }
    
    /* Daemonize */
    if (daemonize("/var/run/mydaemon.pid") < 0) {
        syslog(LOG_ERR, "Daemonization failed");
        exit(EXIT_FAILURE);
    }
    
    /* Now we're a daemon - use syslog for logging */
    syslog(LOG_INFO, "mydaemon started (PID %d)", getpid());
    
    /* Set up signal handlers */
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = signal_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    
    if (sigaction(SIGTERM, &sa, NULL) < 0 || 
        sigaction(SIGINT, &sa, NULL) < 0) {
        syslog(LOG_ERR, "sigaction failed");
        exit(EXIT_FAILURE);
    }
    
    /* Ignore SIGHUP (terminal hangup) */
    signal(SIGHUP, SIG_IGN);
    
    /* Ignore broken pipe */
    signal(SIGPIPE, SIG_IGN);
    
    /* Main daemon loop */
    while (!shutdown_flag) {
        /* Perform periodic work */
        syslog(LOG_DEBUG, "Daemon working...");
        
        /* Sleep for 10 seconds */
        sleep(10);
    }
    
    /* Cleanup */
    syslog(LOG_INFO, "mydaemon shutting down");
    unlink("/var/run/mydaemon.pid");
    closelog();
    
    return EXIT_SUCCESS;
}
```

### Compilation & Usage

```bash
# Compile
gcc -o mydaemon mydaemon.c

# Test (run in foreground for debugging)
./mydaemon
# Ctrl+C to test signal handling

# Deploy
sudo cp mydaemon /usr/local/bin/
sudo mkdir -p /var/log
sudo touch /var/log/mydaemon.log
sudo chmod 644 /var/log/mydaemon.log
```

### Advanced C Daemon Features

#### Using syslog for logging

```c
#include <syslog.h>

/* Initialize */
openlog("mydaemon", LOG_PID | LOG_CONS, LOG_DAEMON);

/* Log messages */
syslog(LOG_ERR, "Error: %s", strerror(errno));
syslog(LOG_WARNING, "Warning message");
syslog(LOG_INFO, "Info message");
syslog(LOG_DEBUG, "Debug: PID=%d", getpid());

/* Cleanup */
closelog();
```

#### Lockfile for single instance

```c
#include <sys/file.h>

int lock_pidfile(const char *pidfile) {
    int fd = open(pidfile, O_CREAT | O_WRONLY, 0644);
    if (fd < 0) return -1;
    
    /* Try to get exclusive lock (fails if another daemon holds it) */
    if (flock(fd, LOCK_EX | LOCK_NB) < 0) {
        close(fd);
        return -1;  /* Another instance already running */
    }
    
    /* Truncate and write PID */
    ftruncate(fd, 0);
    dprintf(fd, "%d\n", getpid());
    
    /* Don't close fd - keep lock held */
    return fd;
}
```

#### Handling SIGHUP for config reload

```c
volatile sig_atomic_t reload_config = 0;

void sighup_handler(int sig) {
    reload_config = 1;
}

int main() {
    signal(SIGHUP, sighup_handler);
    
    while (!shutdown_flag) {
        if (reload_config) {
            syslog(LOG_INFO, "Reloading configuration");
            reload_config = 0;
            /* Call config loading function */
        }
        
        /* Main work */
        sleep(1);
    }
}
```

---

## 3. Creating Daemons in Python

### Complete Python Daemon Class

```python
#!/usr/bin/env python3

import sys
import os
import signal
import logging
import time
from pathlib import Path
from daemon import DaemonContext
from daemon.pidfile import PIDFile

class MyDaemon:
    """Base daemon class for custom services"""
    
    def __init__(self, pidfile, user=None, group=None, logfile=None):
        self.pidfile = pidfile
        self.user = user
        self.group = group
        self.logfile = logfile or '/var/log/mydaemon.log'
        self.shutdown_event = False
        
        # Setup logging
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
    
    def _setup_logging(self):
        """Configure logging to file and syslog"""
        import logging.handlers
        
        # File handler
        file_handler = logging.handlers.RotatingFileHandler(
            self.logfile,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        # Syslog handler
        syslog_handler = logging.handlers.SysLogHandler(
            address='/dev/log',
            facility=logging.handlers.SysLogHandler.LOG_DAEMON
        )
        syslog_handler.setFormatter(logging.Formatter(
            '%(name)s[%(process)d]: %(levelname)s: %(message)s'
        ))
        
        # Configure root logger
        logging.basicConfig(
            level=logging.DEBUG,
            handlers=[file_handler, syslog_handler]
        )
    
    def signal_handler(self, signum, frame):
        """Handle signals"""
        if signum in (signal.SIGTERM, signal.SIGINT):
            self.logger.info(f"Received signal {signum}, shutting down")
            self.shutdown_event = True
        elif signum == signal.SIGHUP:
            self.logger.info("Received SIGHUP, reloading configuration")
            self.reload_config()
    
    def setup_signals(self):
        """Register signal handlers"""
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGHUP, self.signal_handler)
        signal.signal(signal.SIGPIPE, signal.SIG_IGN)
    
    def reload_config(self):
        """Override in subclass"""
        self.logger.info("Configuration reload not implemented")
    
    def run(self):
        """Main daemon loop - override in subclass"""
        raise NotImplementedError("Subclass must implement run()")
    
    def start(self):
        """Start daemon with proper context"""
        pidfile_ctx = PIDFile(self.pidfile) if self.pidfile else None
        
        context_kwargs = {
            'detach_process': True,
            'pidfile': pidfile_ctx,
            'umask': 0o022,
            'working_directory': '/',
        }
        
        # Set user/group if specified
        if self.user or self.group:
            uid = os.getuid() if self.user is None else pwd.getpwnam(self.user).pw_uid
            gid = os.getgid() if self.group is None else grp.getgrnam(self.group).gr_gid
            context_kwargs['uid'] = uid
            context_kwargs['gid'] = gid
        
        with DaemonContext(**context_kwargs):
            self.setup_signals()
            self.logger.info(f"Daemon started (PID {os.getpid()})")
            
            try:
                self.run()
            except Exception as e:
                self.logger.exception(f"Daemon crashed: {e}")
                raise
            finally:
                self.logger.info("Daemon stopped")

# Example subclass
class SecurityScannerDaemon(MyDaemon):
    """Security scanning daemon"""
    
    def __init__(self, config_file, **kwargs):
        super().__init__(**kwargs)
        self.config_file = config_file
        self.config = {}
        self.reload_config()
    
    def reload_config(self):
        """Load configuration from YAML"""
        import yaml
        try:
            with open(self.config_file, 'r') as f:
                self.config = yaml.safe_load(f)
            self.logger.info(f"Configuration loaded from {self.config_file}")
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
    
    def run(self):
        """Main scanning loop"""
        while not self.shutdown_event:
            try:
                self.perform_scan()
            except Exception as e:
                self.logger.exception(f"Scan failed: {e}")
            
            # Sleep before next iteration
            time.sleep(self.config.get('scan_interval', 300))
    
    def perform_scan(self):
        """Perform actual security scan"""
        self.logger.debug("Starting security scan")
        # Implement scanning logic here
        self.logger.debug("Scan complete")

if __name__ == '__main__':
    import pwd
    import grp
    
    daemon = SecurityScannerDaemon(
        config_file='/etc/security-scanner/config.yaml',
        pidfile='/var/run/security-scanner.pid',
        user='scanner',
        group='scanner',
        logfile='/var/log/security-scanner.log'
    )
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'start':
            daemon.start()
        elif sys.argv[1] == 'stop':
            # Kill daemon using pidfile
            try:
                with open(daemon.pidfile, 'r') as f:
                    pid = int(f.read().strip())
                os.kill(pid, signal.SIGTERM)
            except:
                print("Failed to stop daemon")
        else:
            print(f"Usage: {sys.argv[0]} [start|stop]")
    else:
        daemon.start()
```

### Installation with python-daemon

```bash
# Install python-daemon package
pip install python-daemon

# Make script executable
chmod +x /usr/local/bin/security-scanner

# Run directly
python3 /usr/local/bin/security-scanner start
```

### Simpler Python Daemon (without external library)

```python
#!/usr/bin/env python3

import os
import sys
import signal
import logging
import time
import atexit
from pathlib import Path

class SimpleDaemon:
    """Minimal daemon without external dependencies"""
    
    def __init__(self, pidfile, logfile=None):
        self.pidfile = pidfile
        self.logfile = logfile or '/var/log/daemon.log'
        self.shutdown = False
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.logfile),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def daemonize(self):
        """Fork into background"""
        try:
            # First fork
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # Exit parent
        except OSError as e:
            self.logger.error(f"fork #1 failed: {e}")
            sys.exit(1)
        
        # Decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)
        
        try:
            # Second fork
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # Exit from second parent
        except OSError as e:
            self.logger.error(f"fork #2 failed: {e}")
            sys.exit(1)
        
        # Redirect file descriptors
        with open('/dev/null', 'r') as null_in:
            os.dup2(null_in.fileno(), sys.stdin.fileno())
        
        with open(self.logfile, 'a+') as log_file:
            os.dup2(log_file.fileno(), sys.stdout.fileno())
            os.dup2(log_file.fileno(), sys.stderr.fileno())
        
        # Write PID file
        atexit.register(self.delpidfile)
        pid = str(os.getpid())
        with open(self.pidfile, 'w') as f:
            f.write(f"{pid}\n")
        
        self.logger.info(f"Daemon started with PID {pid}")
    
    def delpidfile(self):
        """Remove PID file on exit"""
        try:
            os.remove(self.pidfile)
        except:
            pass
    
    def signal_handler(self, signum, frame):
        """Handle signals"""
        if signum in (signal.SIGTERM, signal.SIGINT):
            self.logger.info("Shutting down")
            self.shutdown = True
    
    def run_loop(self):
        """Main daemon loop"""
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        
        while not self.shutdown:
            try:
                self.do_work()
            except Exception as e:
                self.logger.exception(f"Error in loop: {e}")
            
            time.sleep(10)
    
    def do_work(self):
        """Override in subclass"""
        self.logger.info("Performing work...")
    
    def start(self):
        """Start daemon"""
        self.daemonize()
        self.run_loop()

if __name__ == '__main__':
    daemon = SimpleDaemon('/var/run/mydaemon.pid')
    daemon.start()
```

---

## 4. Process Forking & Daemonization

### Fork Syscall Behavior

```c
#include <unistd.h>

pid_t pid = fork();

if (pid < 0) {
    /* Fork failed */
    perror("fork");
    exit(1);
} else if (pid == 0) {
    /* Child process (PID returned by fork is 0) */
    printf("I'm child, my PID is %d\n", getpid());
    exit(0);
} else {
    /* Parent process (PID is child's actual PID) */
    printf("I'm parent, child PID is %d\n", pid);
    wait(NULL);  /* Wait for child */
}
```

### Session & Process Group

```c
#include <unistd.h>
#include <sys/types.h>

int main() {
    /* Create new session (become session leader) */
    pid_t sid = setsid();
    /* 
    After setsid():
    - Process becomes session leader
    - Process is no longer in parent's process group
    - Process has no controlling terminal
    - Only way to get terminal is explicit open()
    */
    
    return 0;
}
```

---

## 5. Practical Examples: Security Tools

### Network Scanner Daemon (Python)

```python
#!/usr/bin/env python3

import socket
import subprocess
import logging
from SimpleDaemon import SimpleDaemon

class NetworkScannerDaemon(SimpleDaemon):
    """Scan network for open ports"""
    
    def __init__(self, targets_file, **kwargs):
        super().__init__(**kwargs)
        self.targets_file = targets_file
        self.targets = []
        self.load_targets()
    
    def load_targets(self):
        """Load scan targets from file"""
        try:
            with open(self.targets_file) as f:
                self.targets = [line.strip() for line in f if line.strip()]
            self.logger.info(f"Loaded {len(self.targets)} targets")
        except Exception as e:
            self.logger.error(f"Failed to load targets: {e}")
    
    def do_work(self):
        """Scan targets for open ports"""
        for target in self.targets:
            self.scan_target(target)
    
    def scan_target(self, target):
        """Scan single target"""
        try:
            result = subprocess.run(
                ['nmap', '-p', '22,80,443,8080', '-sV', target],
                capture_output=True,
                timeout=300
            )
            
            if result.returncode == 0:
                self.logger.info(f"Scan complete for {target}")
                # Process results
            else:
                self.logger.warning(f"Scan failed for {target}")
        except subprocess.TimeoutExpired:
            self.logger.warning(f"Scan timeout for {target}")
        except Exception as e:
            self.logger.error(f"Scan error for {target}: {e}")

if __name__ == '__main__':
    daemon = NetworkScannerDaemon(
        targets_file='/etc/scanner/targets.txt',
        pidfile='/var/run/network-scanner.pid',
        logfile='/var/log/network-scanner.log'
    )
    daemon.start()
```

### Wireless Monitoring Daemon (C)

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <syslog.h>
#include <string.h>

volatile sig_atomic_t shutdown_flag = 0;

void signal_handler(int sig) {
    shutdown_flag = 1;
}

int monitor_wireless() {
    /* Execute wireless scanning command */
    int ret = system("iwlist wlan0 scan | grep -E 'SSID|Frequency|Signal'");
    return ret;
}

int main() {
    /* Daemonize */
    if (fork() > 0) exit(0);
    setsid();
    if (fork() > 0) exit(0);
    chdir("/");
    
    /* Redirect I/O */
    close(0); close(1); close(2);
    open("/dev/null", O_RDONLY);
    open("/var/log/wireless-monitor.log", O_WRONLY | O_CREAT);
    open("/var/log/wireless-monitor.log", O_WRONLY | O_CREAT);
    
    openlog("wireless-monitor", LOG_PID, LOG_DAEMON);
    
    /* Setup signals */
    signal(SIGTERM, signal_handler);
    signal(SIGINT, signal_handler);
    signal(SIGHUP, SIG_IGN);
    
    syslog(LOG_INFO, "Wireless monitor started");
    
    /* Main loop */
    while (!shutdown_flag) {
        if (monitor_wireless() == 0) {
            syslog(LOG_DEBUG, "Scan complete");
        } else {
            syslog(LOG_WARNING, "Scan failed");
        }
        sleep(60);  /* Scan every minute */
    }
    
    syslog(LOG_INFO, "Wireless monitor stopped");
    closelog();
    
    return 0;
}
```

---

## 6. Signal Handling in Daemons

### Standard Signal Behavior

```c
#include <signal.h>

int main() {
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    
    /* Setup SIGTERM (graceful shutdown) */
    sa.sa_handler = handle_sigterm;
    sigaction(SIGTERM, &sa, NULL);
    
    /* Setup SIGCHLD (child process exit) */
    sa.sa_handler = handle_sigchld;
    sigaction(SIGCHLD, &sa, NULL);
    
    /* Setup SIGHUP (config reload) */
    sa.sa_handler = handle_sighup;
    sigaction(SIGHUP, &sa, NULL);
    
    /* Ignore SIGPIPE (broken pipe) */
    signal(SIGPIPE, SIG_IGN);
    
    /* Don't ignore SIGINT - allow Ctrl+C in testing */
    sa.sa_handler = handle_sigterm;
    sigaction(SIGINT, &sa, NULL);
}

void handle_sigterm(int sig) {
    shutdown_flag = 1;
}

void handle_sighup(int sig) {
    reload_config_flag = 1;
}

void handle_sigchld(int sig) {
    /* Reap zombie child processes */
    int status;
    while (waitpid(-1, &status, WNOHANG) > 0);
}
```

### Signal Safety

Only certain functions are safe to call from signal handlers:

```c
/* Safe functions (signal-safe): */
write(2, buf, len);           /* Write to file descriptor */
exit(code);                   /* Exit immediately */
signal(sig, handler);         /* Reset handler */
sigaction(sig, &sa, NULL);    /* Register handler */

/* UNSAFE - never call from signal handler: */
printf("Error\n");            /* Not signal-safe (uses locks) */
syslog(LOG_ERR, "Error");     /* Not signal-safe */
malloc/free                   /* Not signal-safe (uses locks) */
pthread functions             /* Not signal-safe */

/* Workaround - set volatile flag and check in main loop: */
volatile sig_atomic_t flag = 0;

void handler(int sig) {
    flag = 1;  /* Only set flag - that's safe */
}

int main() {
    while (1) {
        if (flag) {
            /* Safe to call non-signal-safe functions here */
            syslog(LOG_INFO, "Handling signal");
            flag = 0;
        }
        sleep(1);
    }
}
```

---

## 7. Inter-Process Communication Patterns

### Daemon Configuration via Environment

```python
import os

config = {
    'debug': os.getenv('DAEMON_DEBUG', 'false').lower() == 'true',
    'log_level': os.getenv('DAEMON_LOG_LEVEL', 'INFO'),
    'scan_interval': int(os.getenv('SCAN_INTERVAL', '300')),
}
```

### Daemon Communication via Unix Sockets

```c
#include <sys/socket.h>
#include <sys/un.h>
#include <string.h>

/* Create listening socket */
int create_control_socket(const char *path) {
    int sock = socket(AF_UNIX, SOCK_STREAM, 0);
    
    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, path, sizeof(addr.sun_path) - 1);
    
    unlink(path);  /* Remove old socket */
    
    if (bind(sock, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("bind");
        return -1;
    }
    
    listen(sock, 5);
    return sock;
}

/* In main loop */
int control_socket = create_control_socket("/var/run/mydaemon.sock");

/* Accept commands from clients */
int client = accept(control_socket, NULL, NULL);
char command[256];
read(client, command, sizeof(command));

if (strcmp(command, "reload") == 0) {
    reload_config();
    write(client, "OK\n", 3);
}

close(client);
```

---

## 8. Testing & Debugging Daemons

### Test in Foreground Mode

```c
/* Add command-line flag to disable daemonization */
int main(int argc, char *argv[]) {
    int foreground = 0;
    
    if (argc > 1 && strcmp(argv[1], "--foreground") == 0) {
        foreground = 1;
    }
    
    if (!foreground) {
        daemonize("/var/run/mydaemon.pid");
    }
    
    /* Rest of code... */
}

/* Usage: */
/* Foreground testing: */
/* ./mydaemon --foreground */
/* Background: */
/* ./mydaemon */
```

### Debugging with strace

```bash
# Attach strace to running daemon
sudo strace -p $(pgrep mydaemon) -f -e trace=file,network

# Run in foreground with full trace
strace -f ./mydaemon --foreground

# Trace open files
lsof -p $(pgrep mydaemon)
```

### Log Analysis

```bash
# Monitor daemon logs in real-time
tail -f /var/log/mydaemon.log

# Search for errors
grep "ERROR\|WARN" /var/log/mydaemon.log

# Check recent activity
journalctl -u mydaemon.service -f
```

### Process Inspection

```bash
# Check daemon details
ps aux | grep mydaemon
ps -eLf | grep mydaemon  # Show threads

# Check open files/sockets
lsof -p $(pgrep mydaemon)

# Check resource usage
top -p $(pgrep mydaemon)

# Check signals registered
cat /proc/$(pgrep mydaemon)/status | grep SigCgt
```

---

## Summary

This completes the comprehensive Linux processes guide covering:
1. **Kernel fundamentals** (Part 1)
2. **Systemd configuration** (Part 2)
3. **SysV and init alternatives** (Part 3)
4. **Daemon development** (Part 4)

Next steps for implementation:
- Choose appropriate init system for your distribution
- Write service configuration files
- Develop daemons following patterns in this guide
- Test thoroughly before deployment
- Monitor via logs and system tools
- Implement graceful shutdown handling
- Document process management procedures

For security-critical applications, add:
- Privilege dropping (setuid/setgid)
- Capability limitations (CAP_*)
- Seccomp filtering
- AppArmor/SELinux policies
- Secure signal handling
- Resource limits via cgroups
