# Project 2: Wireless Protocol Security - Implementation Checklist
## Phase-by-Phase Quick Reference & Progress Tracking

---

## PHASE 1: RESEARCH & THREAT ANALYSIS (Weeks 1-2, ~50 hours)

### Week 1: Vulnerability Landscape Assessment

**Threat Research**
- [ ] Access MITRE IoT ATT&CK framework (attack_types.json)
- [ ] Identify 50+ relevant attack techniques for wireless IoT
- [ ] Map attacks to Zigbee/BLE capabilities
- [ ] Document attack prerequisites & tool requirements
- [ ] Deliverable: Threat matrix document (20+ pages)

**Protocol Specification Study**
- [ ] Download IEEE 802.15.4 standard (2.4 GHz PHY/MAC)
- [ ] Read Zigbee Alliance specifications (Docs 1-3)
- [ ] Study Bluetooth 5.0 core specification (1000+ pages)
- [ ] Analyze GATT/ATT profile specifications
- [ ] Create protocol layer diagrams (visual documentation)
- [ ] Deliverable: Protocol reference guide (30 pages)

**Existing Tool Evaluation**
- [ ] Evaluate Killerbee capabilities & limitations
- [ ] Test Z3c fuzzer on sample Zigbee network
- [ ] Assess Sweyntooth (BLE vulnerability scanner)
- [ ] Review nRF Sniffer for Wireshark integration
- [ ] Compare open-source vs commercial tools
- [ ] Create tool capability matrix (comparison table)
- [ ] Deliverable: Tool ecosystem analysis (15 pages)

**CVE & Vulnerability Database Correlation**
- [ ] Search NVD for Zigbee CVEs (50+ results expected)
- [ ] Cross-reference BLE vulnerability advisories
- [ ] Categorize by vendor, severity, attack vector
- [ ] Identify patterns in vulnerability disclosure
- [ ] Map known vulnerabilities to target devices
- [ ] Deliverable: CVE correlation spreadsheet + analysis

### Week 2: Threat Modeling & Testing Strategy

**Threat Model Development**
- [ ] Create STRIDE threat model for Zigbee networks
  - [ ] Spoofing attacks (5 vectors)
  - [ ] Tampering attacks (8 vectors)
  - [ ] Repudiation attacks (3 vectors)
  - [ ] Information disclosure (5 vectors)
  - [ ] Denial of service (6 vectors)
  - [ ] Elevation of privilege (4 vectors)
- [ ] Identify 25-30 unique attack scenarios
- [ ] Prioritize by likelihood × impact
- [ ] Deliverable: Threat model diagram + scenario matrix

**Attack Surface Mapping**
- [ ] Identify network entry points (5-10 points)
- [ ] Document communication protocols & frequencies
- [ ] List potential targets (3-5 devices)
- [ ] Document security assumptions for each component
- [ ] Create data flow diagrams (DFD)
- [ ] Deliverable: Attack surface visualization

**Testing Plan & Scope**
- [ ] Define test objectives (what will we measure?)
- [ ] Set scope boundaries (what's in/out of scope?)
- [ ] Document responsible disclosure process
  - [ ] 90-day vendor notification window
  - [ ] Public disclosure timeline
  - [ ] CVE coordination (if applicable)
- [ ] Establish ethical guidelines & legal compliance
- [ ] Create testing schedule (weekly milestones)
- [ ] Deliverable: Test plan document (20+ pages)

**Hardware Validation Plan**
- [ ] List all devices (Ubertooth, CC2531 x2, XBee x3, NRF5284 x2)
- [ ] Define acceptance criteria for each device
- [ ] Plan device ordering (lead times, suppliers)
- [ ] Budget allocation ($1,200-$2,000 expected)
- [ ] Deliverable: Hardware procurement plan + budget

---

## PHASE 2: HARDWARE SETUP & CONFIGURATION (Weeks 2-3, ~40 hours)

### Hardware Procurement

**Wireless Devices**
- [ ] Order Ubertooth One ($200)
- [ ] Order CC2531 dongles (x2, $30 each)
- [ ] Order XBee S3B modules (x3, $40 each)
- [ ] Order NRF52840 DK (x2, $80 each)
- [ ] Order Raspberry Pi 4 8GB ($120)
- [ ] Verify delivery & inspect for damage
- [ ] Document serial numbers & checksums
- [ ] **Subtotal: ~$1,000**

**Supporting Hardware & Accessories**
- [ ] USB 3.0 hub (7-port) - $30
- [ ] USB cables & connectors (assorted) - $30
- [ ] RF shielded enclosure (optional) - $300-$1,000
- [ ] SMA adapters & attenuators - $50
- [ ] Test devices (smart lock, sensor) - $100-$200
- [ ] **Subtotal: ~$210-$1,310**

### Device Configuration

**Ubertooth One Setup** (2-3 hours)
- [ ] Connect USB device
- [ ] Verify detection: `lsusb | grep 1d50:6002`
- [ ] Install ubertooth-tools: `pacman -S ubertooth`
- [ ] Test firmware: `ubertooth-util -s`
- [ ] Update firmware if needed
- [ ] Verify BLE capture: `ubertooth-btle -c 37` (should see advertisements)
- [ ] Create Python wrapper for scapy integration
- [ ] Deliverable: Operational Ubertooth, firmware logs

**CC2531 USB Dongle Setup** (2-4 hours, one hour per device)

**Device #1: Sniffer Mode**
- [ ] Download CC2531 sniffer firmware
- [ ] Install cc-tool: `pacman -S cc-tool`
- [ ] Backup original firmware
- [ ] Flash sniffer firmware: `cc-tool -e -w -v firmware.hex`
- [ ] Verify detection: `lsusb | grep 0451:16a8`
- [ ] Install FTDI drivers
- [ ] Configure Wireshark ZigBee plugin
- [ ] Test packet capture on active Zigbee network
- [ ] Deliverable: Operational sniffer, capture logs

**Device #2: Coordinator Mode**
- [ ] Flash coordinator firmware (alternative bin)
- [ ] Configure network parameters:
  - [ ] PAN ID: 0xAAAA (example)
  - [ ] Channel: 15 (2.405 GHz)
  - [ ] Security: Enabled initially
- [ ] Create/form network
- [ ] Test device joining
- [ ] Deliverable: Operational coordinator, network logs

**XBee S3B Configuration** (3-4 hours per device)

**All 3 Modules:**
- [ ] Install XCTU (Digi tools)
- [ ] Serial connection at 9600 baud
- [ ] Enter AT command mode: `+++` (wait for OK)
- [ ] Read current configuration: `ATVR` (get firmware)
- [ ] Configure for testing:
  - [ ] Module #1: Fuzzer (TX power max: ATPL FF)
  - [ ] Module #2: Sniffer (Monitor mode: ATMM 1)
  - [ ] Module #3: Device simulator (valid profile)
- [ ] Save settings: `ATWR`
- [ ] Exit AT mode: `ATCN`
- [ ] Verify all devices in XCTU
- [ ] Deliverable: 3 configured XBee devices, config files

**NRF52840 DK Setup** (4-5 hours per device)

**Both Development Kits:**
- [ ] Install nRF5 SDK & tools
- [ ] Install J-Link driver (SEGGER)
- [ ] Connect via J-Link debugger
- [ ] Program BLE examples
- [ ] Compile custom firmware (if needed)
- [ ] Test UART debug output
- [ ] Deliverable: Both DKs operational, firmware logs

### Network Integration

**Multi-Device USB Connection**
- [ ] Connect all devices to powered USB hub
- [ ] Verify all devices: `lsusb` (should show 6 devices)
- [ ] Document /dev/ttyUSB* mappings:
  - [ ] /dev/ttyUSB0 → Ubertooth
  - [ ] /dev/ttyUSB1 → CC2531 Sniffer
  - [ ] /dev/ttyUSB2 → CC2531 Coordinator
  - [ ] /dev/ttyUSB3 → XBee Module 1
  - [ ] /dev/ttyUSB4 → XBee Module 2
  - [ ] /dev/ttyUSB5 → XBee Module 3
- [ ] Create udev rules for non-root access
- [ ] Test parallel operation (all devices simultaneously)
- [ ] Deliverable: Device mapping documentation

**Driver & Permission Setup**
- [ ] Install required libraries:
  - [ ] libusb: `pacman -S libusb`
  - [ ] libftdi: `pacman -S libftdi`
  - [ ] pyserial: `pip install pyserial`
- [ ] Create custom udev rules file
- [ ] Test non-root device access
- [ ] Deliverable: udev rules, permission configuration

---

## PHASE 3: PROTOCOL SNIFFING & ANALYSIS (Weeks 3-5, ~80 hours)

### Week 3: Capture Infrastructure Setup

**Multi-Device Capture System**
- [ ] Develop threaded packet sniffer (Python)
  - [ ] 6 independent reader threads
  - [ ] Non-blocking USB I/O
  - [ ] Packet queue aggregation
- [ ] Implement PCAP file writing
  - [ ] Wireshark-compatible format
  - [ ] Timestamp annotations
  - [ ] Protocol metadata
- [ ] Test with individual devices first
- [ ] Verify parallel capture (all 6 devices)
- [ ] Deliverable: Operational multi-device sniffer

**Database Schema Design**
- [ ] Design PostgreSQL schema:
  - [ ] packets table (device, timestamp, frame_hex)
  - [ ] parsed_frames table (protocol, src, dst, type)
  - [ ] cryptographic_metadata table (key_material, entropy)
- [ ] Create indexes for performance
- [ ] Test insertion rate (1000+ packets/sec)
- [ ] Deliverable: Schema definition, initialization scripts

**Wireshark Integration**
- [ ] Install dissector plugins
  - [ ] nRF Sniffer for BLE
  - [ ] ZigBee protocol analyzer
  - [ ] IEEE 802.15.4 MAC layer
- [ ] Create custom display filters
  - [ ] BLE specific: `bt.addr == xx:xx:xx:xx:xx:xx`
  - [ ] Zigbee specific: `zbee_nwk.cluster == 0x0101`
- [ ] Verify packet visualization
- [ ] Deliverable: Configured Wireshark environment

### Weeks 4-5: Baseline Traffic Collection

**Normal Traffic Capture**
- [ ] Start multi-device sniffer (continuous, 8-10 hours)
  - [ ] BLE capture on channels 37-39
  - [ ] Zigbee capture on channels 11-26
- [ ] Collect 50GB+ of PCAP data
- [ ] Store in organized directories by protocol/date
- [ ] Document capture conditions (time, location, devices)
- [ ] Deliverable: Raw PCAP files, capture logs

**Device Discovery & Fingerprinting**
- [ ] Identify all accessible wireless devices (20-50 expected)
  - [ ] BLE devices (phones, wearables, beacons)
  - [ ] Zigbee devices (locks, sensors, controllers)
  - [ ] WiFi devices (routers, access points)
- [ ] Document for each device:
  - [ ] MAC address
  - [ ] Device type/manufacturer
  - [ ] Protocol version
  - [ ] Advertised capabilities
- [ ] Create device inventory spreadsheet
- [ ] Deliverable: Device inventory, discovery logs

**Interaction Traffic Capture**
- [ ] Smart lock unlock sequence (capture 10 times)
- [ ] Temperature sensor readings (capture 20 times)
- [ ] Device pairing sequence (capture 5 times)
- [ ] Configuration changes (capture 5 times)
- [ ] Deliverable: Interaction traffic PCAP files

### Week 5: Protocol Decoding & Analysis

**Packet Parsing Implementation**
- [ ] Build IEEE 802.15.4 MAC frame parser
  - [ ] Frame type classification
  - [ ] Address field extraction
  - [ ] Security metadata parsing
- [ ] Build Zigbee NWK parser
  - [ ] Header field extraction
  - [ ] Frame reassembly (fragmented frames)
  - [ ] Route discovery tracking
- [ ] Build BLE Link Layer parser
  - [ ] PDU type classification
  - [ ] Connection handle mapping
  - [ ] CRC validation
- [ ] Deliverable: Protocol parsers (300+ lines Python)

**Cryptographic Analysis**
- [ ] Scan for static/weak encryption keys
  - [ ] Look for repeated 16-byte sequences (AES keys)
  - [ ] Check entropy of potential keys
- [ ] Analyze key derivation methods
  - [ ] Identify KDF algorithms
  - [ ] Extract salt/nonce values
- [ ] Classify encryption modes
  - [ ] CBC vs CCM vs CTR
  - [ ] IV/nonce reuse detection
- [ ] Deliverable: Crypto analysis report, suspicious packets flagged

**Traffic Pattern Analysis**
- [ ] Build statistical profiles for each device
  - [ ] Packet size distribution
  - [ ] Inter-arrival time analysis
  - [ ] Payload entropy distribution
- [ ] Identify anomalies
  - [ ] Out-of-pattern traffic
  - [ ] Unusual timing/sizes
  - [ ] Potential malformed packets
- [ ] Visualize patterns (matplotlib graphs)
- [ ] Deliverable: Pattern analysis report, visualizations

**Vulnerability Signature Matching**
- [ ] Cross-reference against CVE database
  - [ ] Check firmware versions against known CVEs
  - [ ] Match protocol violations against documented issues
- [ ] Identify weak cryptography
  - [ ] No encryption/authentication
  - [ ] Hardcoded credentials
  - [ ] Known broken algorithms (DES, MD5)
- [ ] Flag suspicious configurations
  - [ ] Default credentials still active
  - [ ] Debug interfaces exposed
  - [ ] Unnecessary services enabled
- [ ] Deliverable: Vulnerability list, risk assessment

---

## PHASE 4: VULNERABILITY EXPLOITATION (Weeks 5-8, ~120 hours)

### Cryptographic Attacks

**Static Key Extraction**
- [ ] Capture pairing sequence (1-2 hours)
- [ ] Extract potential key candidates (10-20 candidates)
- [ ] Test each key against known plaintexts
- [ ] Validate with historical traffic decryption
- [ ] Document recovered key & implications
- [ ] Estimate device compromise scope (all data readable?)
- [ ] Deliverable: Recovered key, decrypted traffic samples

**Weak Key Derivation Cracking**
- [ ] Identify KDF algorithm (PBKDF2, bcrypt, etc.)
- [ ] Extract salt/nonce if possible
- [ ] Estimate key space size (6-digit PIN? 16-digit code?)
- [ ] Brute-force or rainbow table lookup
  - [ ] BLE PIN (1M space): 1-10 hours CPU
  - [ ] Zigbee install code: weeks-to-months (not feasible)
- [ ] Validate cracked key
- [ ] Deliverable: Cracking methodology, time estimates

**Replay Attack Proof-of-Concept**
- [ ] Identify command packet (lock unlock, sensor read)
- [ ] Extract frame bytes (16-256 bytes)
- [ ] Craft injection payload
- [ ] Transmit replay (using XBee fuzzer)
- [ ] Observe device behavior
  - [ ] Lock cycles unlock/lock
  - [ ] Sensor responds multiple times
  - [ ] No error detection/prevention
- [ ] Document implications (unauthorized control)
- [ ] Deliverable: Replay PoC code, captured evidence

### Protocol Exploitation

**Device Impersonation**
- [ ] Capture legitimate device's advertising/communication
- [ ] Clone identity (MAC address, service UUIDs)
- [ ] Transmit as impersonator
- [ ] Test interaction with nearby devices
  - [ ] Do they respond to imposter?
  - [ ] Can we receive data meant for legitimate device?
- [ ] Deliverable: Impersonation code, test results

**Session Hijacking Attempt**
- [ ] Identify active connection between two devices
- [ ] Capture connection parameters
  - [ ] Access address (BLE)
  - [ ] Channel map & hop sequence
  - [ ] Connection handle
- [ ] Predict next packet/channel
- [ ] Inject spoofed packets
- [ ] Attempt to take over session
- [ ] Document success rate (may be low due to timing)
- [ ] Deliverable: Hijacking code, success statistics

**Denial-of-Service Implementations**
- [ ] Implement BLE advertisement flooding
  - [ ] Generate 100-1000 advertisements/second
  - [ ] Observe target device CPU/battery impact
- [ ] Implement Zigbee network disruption
  - [ ] Spoof coordinator beacon
  - [ ] Accept joining devices (rogue network)
  - [ ] Fragment legitimate network
- [ ] Measure impact (availability loss %)
- [ ] Deliverable: DoS implementations, impact metrics

### Fuzzing & Vulnerability Discovery

**Protocol Fuzzer Development**
- [ ] Implement mutation strategies:
  - [ ] Bit-flip (random bit inversion)
  - [ ] Byte replacement (random values)
  - [ ] Truncation (remove trailing bytes)
  - [ ] Extension (add random bytes)
  - [ ] Field manipulation (modify specific fields)
- [ ] Generate 1000-5000 mutant packets
- [ ] Transmit via XBee modules
- [ ] Capture responses/crashes
- [ ] Deliverable: Fuzzer code, crash corpus

**Crash Analysis**
- [ ] Categorize crashes by type
  - [ ] Reboot (device restarts)
  - [ ] Hang (no response for 10+ seconds)
  - [ ] Memory corruption (malformed output)
  - [ ] Service crash (but device recovers)
- [ ] Analyze crash-causing payloads
  - [ ] Extract triggering conditions
  - [ ] Document minimal reproducer
- [ ] Estimate exploitability (can we leverage crash?)
- [ ] Deliverable: Crash analysis report, minimal reproducers

---

## PHASE 5: TOOL DEVELOPMENT & AUTOMATION (Weeks 8-10, ~100 hours)

### Tool Implementation

**Integrated Exploitation Toolkit**
- [ ] Create main CLI tool (project2_security_toolkit.py)
  - [ ] Subcommands: sniff, parse, exploit, fuzz, report
  - [ ] Configuration file support (YAML/JSON)
  - [ ] Logging & verbosity levels
- [ ] Package for distribution
  - [ ] Requirements.txt with all dependencies
  - [ ] Setup.py for pip installation
  - [ ] Docker containerization (optional)
- [ ] Deliverable: Working toolkit, CLI documentation

**Automated Reporting**
- [ ] PDF report generation (ReportLab)
  - [ ] Executive summary (2-3 pages)
  - [ ] Technical findings (10-20 pages)
  - [ ] Attack scenarios (5-10 pages)
  - [ ] Recommendations (3-5 pages)
- [ ] JSON export for further analysis
  - [ ] Structured vulnerability data
  - [ ] MITRE ATT&CK mapping
  - [ ] Risk scoring
- [ ] HTML dashboard (Flask + Plotly)
  - [ ] Interactive charts
  - [ ] Attack timeline visualization
  - [ ] Device topology graph
- [ ] Deliverable: Report templates, automation scripts

**Web Dashboard**
- [ ] Develop Flask backend
  - [ ] API endpoints for analysis results
  - [ ] Database integration
  - [ ] Authentication (optional)
- [ ] Create Plotly visualizations
  - [ ] Attack timeline
  - [ ] Device topology
  - [ ] Traffic heatmaps
- [ ] Deploy locally (Flask dev server)
- [ ] Deliverable: Running dashboard (localhost:5000)

### Documentation

**API Reference**
- [ ] Document all major classes/functions
  - [ ] Input parameters
  - [ ] Return values/types
  - [ ] Exceptions/errors
  - [ ] Usage examples
- [ ] Create notebook examples (Jupyter)
  - [ ] Basic sniffing example
  - [ ] Protocol analysis example
  - [ ] Exploitation example
- [ ] Deliverable: API docs (20+ pages), example notebooks

**User Guides**
- [ ] Installation guide (setup from scratch)
- [ ] Quick-start guide (first capture in 5 minutes)
- [ ] Attack methodology guide (step-by-step)
- [ ] Troubleshooting guide (common issues)
- [ ] Deliverable: 4 comprehensive guides (30+ pages total)

---

## PHASE 6: TESTING & VALIDATION (Weeks 10-12, ~80 hours)

### Real-World Device Testing

**Smart Lock Assessment**
- [ ] Identify lock model (Yale Connect example)
- [ ] Capture pairing & lock/unlock sequences
- [ ] Attempt key extraction
- [ ] Test replay attacks
- [ ] Attempt session hijacking
- [ ] Document all findings
- [ ] Deliverable: Smart lock report (10+ pages)

**Sensor Device Testing**
- [ ] Identify sensor model
- [ ] Capture normal readings
- [ ] Attempt to spoof sensor readings
- [ ] Test data injection
- [ ] Verify sensor robustness
- [ ] Deliverable: Sensor assessment report

### Cross-Device Compatibility

**Multi-Vendor Testing**
- [ ] Test toolkit against 5+ different device models
  - [ ] At least 2 Zigbee devices
  - [ ] At least 2 BLE devices
  - [ ] At least 1 mixed protocol device
- [ ] Document compatibility issues
- [ ] Create device-specific configurations
- [ ] Deliverable: Compatibility matrix

### Performance Benchmarking

**Capture Performance**
- [ ] Measure packet capture rate (packets/second)
- [ ] Measure CPU usage (single-core %)
- [ ] Measure memory usage (MB)
- [ ] Measure disk I/O (MB/sec)
- [ ] Target: 500+ packets/sec, <40% CPU
- [ ] Deliverable: Performance report

**Analysis Performance**
- [ ] Measure parsing speed (packets/second)
- [ ] Measure database insertion rate
- [ ] Measure query response times
- [ ] Target: Process 10,000+ packets in <30 seconds
- [ ] Deliverable: Performance metrics

---

## PHASE 7: PUBLICATION & DISCLOSURE (Weeks 12+)

### Responsible Disclosure

**Vendor Notification**
- [ ] Identify affected vendors (5-10 expected)
- [ ] Locate security contact email
- [ ] Draft vulnerability notification (template)
- [ ] Send with 90-day embargo (deadline for fix)
- [ ] Coordinate with vendors on disclosure
- [ ] Deliverable: Disclosure emails, responses

**CVE Coordination**
- [ ] Determine if CVE assignment needed
- [ ] Contact MITRE for assignment (if novel)
- [ ] Document CVE details
- [ ] Publish advisory on GitHub/website
- [ ] Deliverable: Published advisories

### Research Publication

**Technical Paper**
- [ ] Write 15-20 page research paper
  - [ ] Abstract & introduction
  - [ ] Methodology & tools
  - [ ] Findings & vulnerabilities
  - [ ] Impact assessment
  - [ ] Recommendations
- [ ] Submit to security conference (NDSS, IEEE S&P, etc.)
- [ ] Deliverable: Published paper (arXiv preprint at minimum)

**Blog Post Series**
- [ ] Write 5-8 blog posts (1000-2000 words each)
  - [ ] "Wireless Protocol Analysis 101"
  - [ ] "Finding Zigbee Vulnerabilities"
  - [ ] "BLE Security Deep Dive"
  - [ ] "Practical Exploitation Techniques"
  - [ ] "Building Custom Security Tools"
- [ ] Post on Medium, Dev.to, personal blog
- [ ] Deliverable: Published blog series (5,000+ words)

**Conference Talk**
- [ ] Propose talk to security conference
  - [ ] Target: DefCon, Black Hat, USENIX, etc.
  - [ ] Submission deadline: 3-6 months before event
- [ ] Create presentation slides (50-60 slides)
- [ ] Record demo videos (3-5 videos, 5-10 min each)
- [ ] Deliverable: Conference submission, slides, demos

---

## SUCCESS METRICS CHECKLIST

### Technical Achievements
- [ ] Operate 6 wireless devices simultaneously
- [ ] Capture 50GB+ of wireless traffic
- [ ] Identify 25+ unique vulnerabilities
- [ ] Extract 3+ encryption keys
- [ ] Demonstrate 5+ working exploits
- [ ] Develop 8+ production tools
- [ ] Test on 5+ real-world device models

### Portfolio Metrics
- [ ] GitHub repository (8+ connected projects)
- [ ] 2,000+ GitHub stars
- [ ] 3+ technical papers/blog posts published
- [ ] 1+ conference talk accepted
- [ ] 10+ security researchers using toolkit
- [ ] Industry recognition (tweets, mentions)

### Career Impact
- [ ] Resume enhanced with major security project
- [ ] Demonstrable expertise in wireless security
- [ ] Network expanded (security community connections)
- [ ] Potential consulting/employment opportunities
- [ ] Speaking invitations received
- [ ] High-level security roles within reach

---

**Document Version:** 1.0  
**Last Updated:** December 15, 2025  
**Estimated Total Time:** 300-400 hours over 12 weeks
**Status:** Ready for Execution
