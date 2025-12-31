# Quick Start: /proc Process Analysis Suite

## ⚡ 5-Minute Overview

You have **4 comprehensive documents** totaling **2,535 lines** explaining:
1. How Linux processes work
2. How they appear in `/proc`
3. How to build custom services
4. How to monitor everything

---

## 🎯 Pick Your Path

### Path 1: "I Need Answers Fast" ⏱️ (5 min)
**Read:** proc_process_summary_reference.md
→ WHAT'S INSIDE EACH /PROC FILE section
→ EXAMPLE COMMANDS section
**Result:** Quick commands to solve your problem

---

### Path 2: "I'm Debugging Something" 🔍 (15 min)
**Read:** proc_process_summary_reference.md
→ Quick Identification Guide (find what file to check)
→ Practical Debugging Examples (find your scenario)
→ Essential Commands (copy-paste the fix)
**Result:** Diagnose and fix the issue

---

### Path 3: "I'm Building a Service" 🛠️ (1 hour)
**Read:** proc_custom_service_guide.md
→ Part 2: Step-by-step service creation (30 min)
→ Part 4: Monitoring scripts (20 min)
→ Part 6: Debugging (10 min)
**Result:** Working production service + monitoring

---

### Path 4: "I Want Complete Understanding" 📚 (4-6 hours)
**Read in Order:**
1. README_proc_analysis.md (navigation + learning path)
2. proc_process_summary_reference.md (quick reference)
3. proc_process_lifecycle_detailed.md (deep knowledge)
4. proc_custom_service_guide.md (hands-on practice)
**Result:** Complete mastery of process monitoring

---

## 🔥 Most Used Commands (Copy-Paste Ready)

### Check Process State
```bash
PID=12345  # Replace with your PID
cat /proc/$PID/stat | awk '{print "State: " $3 ", CPU: " $14+$15 " jiffies"}'
```

### Monitor Memory Live
```bash
watch -n 1 'cat /proc/'$PID'/statm | awk "{print \$2*4/1024 \" MB\"}"'
```

### Find Service Logs
```bash
PID=$(systemctl show myservice.service -p MainPID | cut -d= -f2)
readlink /proc/$PID/fd/1 /proc/$PID/fd/2
```

### Check If Zombie
```bash
ps aux | grep $PID | grep -q '<defunct>' && echo "ZOMBIE" || echo "OK"
```

### Get CPU Usage %
```bash
awk '{printf "%.1f sec\n", ($14+$15)/100}' /proc/$PID/stat
```

### Find Memory Leak
```bash
for i in {1..60}; do 
  awk '{printf "%s: %.1f MB\n", "'$(date +%H:%M:%S)'", $2*4/1024}' /proc/$PID/statm
  sleep 1
done
```

---

## 📋 Document Quick Reference

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **proc_process_summary_reference.md** | Quick lookup, cheat sheet | When debugging |
| **README_proc_analysis.md** | Navigation, learning path | When getting started |
| **proc_process_lifecycle_detailed.md** | Complete reference | For deep understanding |
| **proc_custom_service_guide.md** | Service creation guide | When building services |

---

## 💡 Key Facts You Need to Know

### What Gets Updated Constantly
```
stat          → Every 1-10ms (CPU times, state)
fd/           → When files opened/closed
statm         → When memory allocated/freed
io            → When bytes read/written
wchan         → When process blocks
```

### Most Important Files
```
stat          → Everything about the process
fd/           → What files/sockets it uses
wchan         → Why it's not running
statm         → Memory usage summary
smaps         → Memory details (for leak detection)
```

### How to Find PID
```bash
# From systemctl (for services)
systemctl show myservice.service -p MainPID | cut -d= -f2

# From process name
ps aux | grep myname | grep -v grep | awk '{print $2}'

# From port (if service listening)
lsof -i :8080 | tail -1 | awk '{print $2}'
```

### What Each State Means
```
S = Sleeping (idle, waiting for event)
R = Running (on CPU right now)
D = Disk sleep (blocked on I/O)
Z = Zombie (exited, parent hasn't wait'd)
T = Stopped (SIGSTOP received)
```

---

## 🎯 START NOW

**Pick your path above → Open the recommended document → Find your answer**

All commands are copy-paste ready. Just replace PID with your process ID!

