# Project 2: Wireless Protocol Security - Complete UML Architecture & System Design
## Phase-by-Phase Tool Integration and Module Dependencies

---

## PART 1: SYSTEM ARCHITECTURE OVERVIEW

### 1.1 High-Level Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    WIRELESS PROTOCOL SECURITY FRAMEWORK                   │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                    HARDWARE ABSTRACTION LAYER                      │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │  ┌─────────┐  ┌────────┐  ┌──────────┐  ┌────────┐  ┌──────────┐  │  │
│  │  │Ubertooth│  │CC2531  │  │XBee S3B  │  │NRF5284 │  │USRP (opt)│  │  │
│  │  │(BLE)    │  │(Zigbee)│  │(802.15.4)│  │(BLE 5) │  │(SDR)     │  │  │
│  │  └────┬────┘  └───┬────┘  └─────┬────┘  └───┬────┘  └────┬─────┘  │  │
│  │       └────────────┴──────────────┴──────────┴──────────┴─────────┘   │
│  │                           Driver Interface                            │
│  │              (libusb, pyserial, udev rules)                          │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                    ↓                                      │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                    PACKET CAPTURE & DECODING LAYER                 │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │  ┌──────────────────────────────────────────────────────────────┐  │  │
│  │  │  Live Capture Engines                                        │  │  │
│  │  │  • BLE Advertisement Sniffer (Ubertooth)                    │  │  │
│  │  │  • Zigbee Frame Capture (CC2531/XBee)                       │  │  │
│  │  │  • 802.15.4 PHY Layer Analysis (GNU Radio optional)         │  │  │
│  │  └──────────────────────────────────────────────────────────────┘  │  │
│  │                           ↓                                          │  │
│  │  ┌──────────────────────────────────────────────────────────────┐  │  │
│  │  │  Protocol Decoders                                           │  │  │
│  │  │  • BLE Link Layer (PDU parsing)                              │  │  │
│  │  │  • Zigbee Network Layer (NWK frame reassembly)               │  │  │
│  │  │  • IEEE 802.15.4 MAC (frame validation)                      │  │  │
│  │  │  • GATT/GAP attribute resolution                             │  │  │
│  │  └──────────────────────────────────────────────────────────────┘  │  │
│  │                           ↓                                          │  │
│  │  ┌──────────────────────────────────────────────────────────────┐  │  │
│  │  │  PCAP Export & Storage                                       │  │  │
│  │  │  • Wireshark-compatible capture files                        │  │  │
│  │  │  • PostgreSQL time-series database                           │  │  │
│  │  │  • Elasticsearch for searching                               │  │  │
│  │  └──────────────────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                    ↓                                      │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                    ANALYSIS & EXPLOITATION LAYER                   │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │  ┌──────────────────────────────────────────────────────────────┐  │  │
│  │  │  Vulnerability Detection Engines                             │  │  │
│  │  │  • Cryptographic weakness scanner                            │  │  │
│  │  │  • Session tracking & hijacking analyzer                     │  │  │
│  │  │  • Replay attack detector                                    │  │  │
│  │  │  • Fuzzing framework (AFL-like)                              │  │  │
│  │  │  • Anomaly detection (ML-based)                              │  │  │
│  │  └──────────────────────────────────────────────────────────────┘  │  │
│  │                           ↓                                          │  │
│  │  ┌──────────────────────────────────────────────────────────────┐  │  │
│  │  │  Exploitation Toolkit                                        │  │  │
│  │  │  • Key extraction (brute-force, side-channel)                │  │  │
│  │  │  • Packet injection framework                                │  │  │
│  │  │  • Device impersonation & spoofing                           │  │  │
│  │  │  • Session takeover mechanisms                               │  │  │
│  │  │  • Denial-of-service attack generators                       │  │  │
│  │  └──────────────────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                    ↓                                      │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                    REPORTING & VISUALIZATION LAYER                 │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │  ┌──────────────────────────────────────────────────────────────┐  │  │
│  │  │  Analysis Reports                                            │  │  │
│  │  │  • PDF vulnerability assessments                             │  │  │
│  │  │  • JSON/CSV export for further analysis                      │  │  │
│  │  │  • MITRE ATT&CK mapping                                      │  │  │
│  │  │  • Responsible disclosure templates                          │  │  │
│  │  └──────────────────────────────────────────────────────────────┘  │  │
│  │                           ↓                                          │  │
│  │  ┌──────────────────────────────────────────────────────────────┐  │  │
│  │  │  Web Dashboard                                               │  │  │
│  │  │  • Real-time packet statistics                               │  │  │
│  │  │  • Device discovery & topology                               │  │  │
│  │  │  • Attack timeline visualization                             │  │  │
│  │  │  • Threat intelligence integration                           │  │  │
│  │  └──────────────────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## PART 2: PHASE-BY-PHASE EXECUTION SEQUENCE

### Phase 1: Research & Threat Analysis (Week 1-2)

```
Research Phase Timeline
═══════════════════════════════════════════════════════════════════════════

Week 1: Threat Landscape & Protocol Deep-Dive
│
├─→ Vulnerability Research Module
│   │
│   ├─ MITRE IoT ATT&CK database analysis (2-3 days)
│   │  [Tools: JSON parsing, grep, custom Python scripts]
│   │
│   ├─ IEEE 802.15.4 specification study (1-2 days)
│   │  [Tools: PDF reader, protocol analyzer, note-taking]
│   │
│   ├─ Zigbee Alliance documentation review (2-3 days)
│   │  [Tools: Specification PDFs, Wireshark ZigBee dissector]
│   │
│   ├─ BLE 5.0 Core Specification analysis (2-3 days)
│   │  [Tools: Bluetooth SIG docs, nRF Connect analysis]
│   │
│   └─ CVE/Vulnerability Database correlation (1-2 days)
│      [Tools: NVD search, cvedetails.com, GitHub security advisories]
│
├─→ Tool Ecosystem Comparison
│   │
│   ├─ Existing Zigbee tools evaluation
│   │  (Z3c, Zigbee2MQTT, Killerbee) → Analysis matrix
│   │
│   ├─ BLE security tooling review
│   │  (BtleJack, Sweyntooth, nRF Sniffer) → Capabilities vs gaps
│   │
│   └─ Commercial IDS comparison
│      (Fortinet, Palo Alto) → Feature requirements
│
└─→ Threat Model Development
    │
    ├─ Attack surface mapping (5 major categories × 10 attack vectors)
    │  [Tools: Draw.io, custom threat matrix]
    │
    ├─ Risk assessment (likelihood × impact)
    │  [Tools: Spreadsheet, heat map visualization]
    │
    └─ Testing prioritization (rank by criticality)
       [Tools: Decision matrix, stakeholder feedback]

        ↓ (Output: 50+ page threat analysis document)

═══════════════════════════════════════════════════════════════════════════

Week 2: Hardware Validation & Testing Plan
│
├─→ Device Capability Assessment
│   │
│   ├─ Ubertooth One validation
│   │  ├─ BLE packet capture verification
│   │  ├─ Frequency hopping tracking capability
│   │  └─ Range testing (5m, 10m, 25m)
│   │     [Tools: ubertooth-util, custom range test script]
│   │
│   ├─ CC2531 Zigbee testing
│   │  ├─ Network join capability
│   │  ├─ Frame capture accuracy
│   │  └─ Multiple frequency testing (11-26)
│   │     [Tools: XCTU, Wireshark, Zigbee2MQTT]
│   │
│   └─ Cross-device communication
│      [Tools: Python pyserial, multithreading library]
│
├─→ Testing Methodology Design
│   │
│   ├─ Real-world device target selection
│   │  ├─ Smart lock (Yale Connect)
│   │  ├─ Temperature sensor (Zigbee certified)
│   │  ├─ BLE beacon (generic manufacturer)
│   │  └─ Industrial controller (optional)
│   │     [Tools: Device specifications, vendor datasheets]
│   │
│   ├─ Exploitation scenario planning
│   │  ├─ Key extraction methodology
│   │  ├─ Session hijacking approach
│   │  ├─ DoS attack vectors
│   │  └─ Firmware modification possibilities
│   │
│   └─ Responsible disclosure framework
│      [Tools: GitHub security advisories template, email drafts]
│
└─→ Project Timeline & Milestones
    │
    ├─ Define critical path (longest dependencies)
    ├─ Resource allocation (hardware sharing schedule)
    ├─ Risk mitigation (hardware backup plans)
    └─ Success criteria (what constitutes completion)

        ↓ (Output: Comprehensive testing plan, threat model document)
```

### Phase 2: Hardware Setup & Configuration (Week 2-3)

```
Hardware Configuration Phase
═══════════════════════════════════════════════════════════════════════════

Week 2-3: Device Firmware & Driver Installation
│
├─→ Ubertooth One Setup (2-3 hours)
│   │
│   ├─ USB driver verification
│   │  [Tools: lsusb, dmesg, udev rules]
│   │
│   ├─ Firmware flashing
│   │  ├─ Download latest ubertooth_one_fw.bin
│   │  ├─ Verify checksum
│   │  └─ Flash with ubertooth-util -l
│   │     [Tools: ubertooth-util, libusb]
│   │
│   ├─ BLE capture capability test
│   │  ├─ ubertooth-btle -c 37 (start sniffing)
│   │  ├─ Verify 4-6 BLE advertisements/sec
│   │  └─ Capture to PCAP file
│   │     [Tools: ubertooth-btle, Wireshark]
│   │
│   └─ Integration testing
│      └─ Custom Python wrapper (scapy integration)
│         [Tools: Python, scapy, ctypes]
│
├─→ CC2531 USB Dongle Setup (1-2 hours × 2 devices)
│   │
│   ├─ Device #1: Sniffer Role
│   │  │
│   │  ├─ Sniffer firmware flashing
│   │  │  [Tools: cc-tool, ihex format]
│   │  │
│   │  ├─ Wireshark plugin installation
│   │  │  ├─ nRF Sniffer for Wireshark addon
│   │  │  └─ FT232R USB UART driver setup
│   │  │     [Tools: Wireshark, libftdi]
│   │  │
│   │  └─ Capture validation
│   │     [Tools: Wireshark, custom protocol analyzers]
│   │
│   └─→ Device #2: Coordinator Role
│      │
│      ├─ Coordinator firmware flashing
│      │  [Tools: ZigBee Coordinator firmware bin]
│      │
│      ├─ Network formation
│      │  ├─ Create new Zigbee network (PAN ID)
│      │  ├─ Set 802.15.4 channel (11-26)
│      │  └─ Extended address configuration
│      │     [Tools: XCTU, Zigbee2MQTT config]
│      │
│      └─ Permit joining setup
│         └─ Allow test devices to join (1-2 hours open)
│            [Tools: Zigbee2MQTT, custom join scripts]
│
├─→ XBee S3B Module Configuration (3-4 hours × 3 devices)
│   │
│   ├─ Device #1: Fuzzer Input
│   │  │
│   │  ├─ API mode activation (ATAP 2)
│   │  ├─ Custom firmware (optional, for injection)
│   │  └─ TX power maximization (ATPL FF)
│   │     [Tools: XCTU, Python serial, pyx bee]
│   │
│   ├─ Device #2: Sniffer
│   │  │
│   │  ├─ Monitor mode (ATMM 1)
│   │  ├─ Frame buffering setup
│   │  └─ Data rate optimization
│   │     [Tools: XCTU, digi-xbee Python]
│   │
│   └─ Device #3: Device Simulation
│      │
│      ├─ Valid device profile loading
│      ├─ Address assignment
│      └─ Response generation patterns
│         [Tools: XCTU, device specification sheets]
│
├─→ NRF52840 DK Setup (4-5 hours × 2 devices)
│   │
│   ├─ Development environment
│   │  ├─ nRF5 SDK installation
│   │  ├─ GCC ARM toolchain setup
│   │  └─ J-Link debug probe drivers
│   │     [Tools: Nordic semiconductor tools]
│   │
│   ├─ Firmware programming
│   │  ├─ BLE 5.0 examples compilation
│   │  ├─ Flash & softdevice installation
│   │  └─ UART debug interface testing
│   │     [Tools: nrfjprog, make, GCC]
│   │
│   ├─ Custom firmware development
│   │  ├─ BLE peripheral mode (for hijacking tests)
│   │  ├─ Central scanner mode (for discovery)
│   │  └─ Custom advertising payloads
│   │     [Tools: nRF5 SDK, C compiler, VSCode]
│   │
│   └─ Debugging & verification
│      └─ J-Link RTT viewer for debug output
│         [Tools: J-Link tools, SEGGER IDE]
│
├─→ Network Integration
│   │
│   ├─ USB hub connection
│   │  ├─ All 6 devices connected simultaneously
│   │  ├─ Device enumeration verification
│   │  └─ /dev/ttyUSB* assignment documentation
│   │     [Tools: lsusb, dmesg, udev rules]
│   │
│   └─ Driver conflict resolution
│      └─ Ensure parallel operation (no conflicts)
│         [Tools: system logging, concurrent testing]
│
└─→ Testing & Validation
    │
    ├─ Individual device tests (30 min each)
    ├─ Multi-device operation test
    └─ Expected outcomes:
       • All 6 devices operational
       • Parallel packet capture confirmed
       • Zero device conflicts
       • Ready for Phase 3

        ↓ (Output: All devices operational, configuration documentation)
```

### Phase 3: Protocol Sniffing & Analysis (Week 3-5)

```
Protocol Analysis Phase
═══════════════════════════════════════════════════════════════════════════

Week 3: Capture Infrastructure & PCAP Pipeline (40 hours)
│
├─→ Multi-Device Capture System (Python)
│   │
│   ├─ Threaded packet reader
│   │  ├─ 6 simultaneous device readers (non-blocking)
│   │  ├─ Packet queue aggregation
│   │  └─ Real-time PCAP writer
│   │     [Tools: Python threading, dpkt, scapy, libpcap]
│   │
│   ├─ Packet filtering & tagging
│   │  ├─ Protocol identification
│   │  ├─ Device MAC address tracking
│   │  └─ Signal strength (RSSI) annotation
│   │     [Tools: Custom Python, socket library]
│   │
│   └─ Database insertion
│      ├─ PostgreSQL schema design
│      ├─ Time-series partitioning
│      └─ Index optimization for queries
│         [Tools: SQLAlchemy, psycopg2, TimescaleDB]
│
├─→ Wireshark Integration
│   │
│   ├─ Custom dissector development
│   │  ├─ Zigbee NWK layer custom fields
│   │  ├─ BLE advertisement payload annotation
│   │  └─ IEEE 802.15.4 security parsing
│   │     [Tools: Wireshark Lua API, C dissectors]
│   │
│   ├─ Filter creation
│   │  ├─ BLE filter: bt.addr == xx:xx:xx:xx:xx:xx
│   │  ├─ Zigbee filter: zbee_nwk.src == 0x1234
│   │  └─ Combined protocol filtering
│   │
│   └─ Visualization setup
│      └─ Packet flow graphs, timeline views
│         [Tools: Wireshark GUI, tshark]
│
├─→ Traffic Dataset Collection (30 hours)
│   │
│   ├─ Baseline traffic capture
│   │  ├─ Normal device operation (6-8 hours)
│   │  ├─ Multiple frequency channels
│   │  └─ Store 50GB+ of PCAP data
│   │     [Tools: tcpdump, capture scripts]
│   │
│   ├─ Device discovery phase
│   │  ├─ BLE advertisement scanning (2 hours)
│   │  ├─ Zigbee network scanning (2 hours)
│   │  └─ Catalog 20-50 unique devices
│   │     [Tools: nRF Connect, Zigbee2MQTT scan]
│   │
│   ├─ Interaction traffic
│   │  ├─ Smart lock unlock sequences (5-10 captures)
│   │  ├─ Sensor reading requests (10-20 captures)
│   │  └─ Configuration changes (5-10 captures)
│   │     [Tools: Device APIs, custom control scripts]
│   │
│   └─ Edge case scenarios
│      ├─ Out-of-range recovery
│      ├─ Network rejoin procedures
│      └─ Interference handling
│         [Tools: RF interference generator (optional), range tests]
│
└─→ Deliverable: Raw packet collection, 50GB+ PCAP files, database populated

═══════════════════════════════════════════════════════════════════════════

Week 4-5: Protocol Decoding & Analysis (50 hours)
│
├─→ Protocol Dissector Implementation
│   │
│   ├─ IEEE 802.15.4 MAC Frame Parser
│   │  ├─ Frame type identification (data, ack, beacon, cmd)
│   │  ├─ Address field extraction (16-bit, 64-bit)
│   │  ├─ Security suite detection
│   │  └─ FCS (frame check sequence) validation
│   │     [Tools: Python bit manipulation, struct module]
│   │
│   ├─ Zigbee Network Layer Dissector
│   │  ├─ NWK header parsing
│   │  ├─ Frame reassembly (fragmented frames)
│   │  ├─ Route discovery tracking
│   │  └─ Cluster & endpoint association
│   │     [Tools: Construct library, custom state machine]
│   │
│   ├─ BLE Link Layer Dissector
│   │  ├─ PDU type parsing (advertising, data, control)
│   │  ├─ CRC validation
│   │  ├─ Channel classification
│   │  └─ Connection handle mapping
│   │     [Tools: Scapy, cryptography lib]
│   │
│   └─ GATT/ATT Service Discovery
│      ├─ Service UUID parsing
│      ├─ Characteristic enumeration
│      ├─ Descriptor mapping
│      └─ Property flags annotation
│         [Tools: Python, uuid library]
│
├─→ Cryptographic Signature Analysis
│   │
│   ├─ Key Material Detection
│   │  ├─ AES-CCM authentication tags
│   │  ├─ Nonce/IV pattern recognition
│   │  └─ Repeated sequence detection
│   │     [Tools: PyCryptodome, NumPy, entropy analysis]
│   │
│   ├─ Encryption Mode Identification
│   │  ├─ Plaintext vs ciphertext heuristics
│   │  ├─ Block size estimation
│   │  └─ Key reuse patterns
│   │     [Tools: Custom Python analyzer]
│   │
│   └─ Cryptographic Material Leakage
│      ├─ Timing analysis
│      ├─ Power analysis artifacts (if side-channel)
│      └─ Plaintext predictability
│         [Tools: Statistical analysis, matplotlib]
│
├─→ Traffic Pattern Recognition
│   │
│   ├─ Device Identification
│   │  ├─ Packet size distribution
│   │  ├─ Timing intervals (inter-arrival times)
│   │  ├─ Frequency of use
│   │  └─ Manufacturer-specific fingerprints
│   │     [Tools: NumPy, pandas, scikit-learn]
│   │
│   ├─ Behavior Profiling
│   │  ├─ Normal vs anomalous patterns
│   │  ├─ Time-of-day variations
│   │  ├─ Seasonal patterns
│   │  └─ State machine transitions
│   │     [Tools: Matplotlib, Plotly visualization]
│   │
│   └─ Network Topology Mapping
│      ├─ Device relationships
│      ├─ Hop count distributions
│      ├─ Preferred routes
│      └─ Network resilience patterns
│         [Tools: NetworkX, graph visualization]
│
├─→ Vulnerability Signature Matching
│   │
│   ├─ Known CVE Detection
│   │  ├─ Cross-reference against CVE database
│   │  ├─ Firmware version fingerprinting
│   │  └─ Configuration weakness identification
│   │     [Tools: Python regex, CVE API queries]
│   │
│   ├─ Weak Crypto Detection
│   │  ├─ Static keys (never-changing encryption)
│   │  ├─ Hardcoded credentials in traffic
│   │  ├─ Null encryption/authentication
│   │  └─ DES/MD5 usage (deprecated crypto)
│   │     [Tools: Custom analyzers, entropy checks]
│   │
│   └─ Protocol Violations
│      ├─ Out-of-order frame sequences
│      ├─ Unexpected state transitions
│      ├─ Timeout violations
│      └─ Range/bounds violations
│         [Tools: State machine analyzer, custom rules]
│
└─→ Deliverable: Analysis database, 100+ identified vulnerabilities, threat catalog

        ↓ (Output: Comprehensive protocol analysis, vulnerability matrix)
```

---

## PART 3: CORE MODULE SPECIFICATIONS

### Module Specifications Table

| Phase | Module | Function | Primary Tools | Dependencies | Output Format | Persistence |
|---|---|---|---|---|---|---|
| **P1** | Threat Analyzer | MITRE ATT&CK mapping | Python, JSON | GitHub API | JSON attack matrix | Git repo |
| **P2** | HW Controller | Device initialization | libusb, PySerial | udev rules | Device state file | `/tmp/hw_state.json` |
| **P2** | Firmware Manager | Flash/verify firmware | ubertooth-util, cc-tool | Device drivers | Flash logs | SQLite |
| **P3** | Packet Sniffer | Multi-device capture | Python threads, libpcap | HW layer | PCAP files (50GB) | PostgreSQL |
| **P3** | Protocol Parser | IEEE 802.15.4 decode | Scapy, Construct | Raw PCAP | Structured records | PostgreSQL |
| **P3** | Crypto Analyzer | Key material detection | PyCryptodome | Packet data | Vulnerability list | JSON |
| **P4** | Fuzzer | Protocol fuzzing | Python, AFL | Packet templates | Crash corpus | Filesystem |
| **P4** | Key Cracker | Brute-force decryption | PyCryptodome, OpenSSL | Ciphertexts | Recovered keys | Secure vault |
| **P4** | Packet Injector | Craft & transmit | XBee S3B, Python | Packet spec | Injection logs | JSON |
| **P5** | Report Generator | PDF vulnerability reports | ReportLab, Jinja2 | Analysis data | PDF documents | Filesystem |
| **P6** | Dashboard API | Web visualization | Flask, Plotly | Database, analysis | Interactive HTML | Web server |

---

## PART 4: DATA FLOW DIAGRAM

```
Raw Hardware Signals
        │
        ↓
    ┌───────────────────────┐
    │ Packet Capture Layer  │
    │  (6 devices parallel) │
    └───────────┬───────────┘
                │
        ┌───────┴──────────────────┬─────────────┬──────────┐
        ↓                          ↓             ↓          ↓
   ┌─────────┐           ┌──────────────┐  ┌────────┐  ┌──────────┐
   │Ubertooth│           │CC2531 Sniffer│  │XBee    │  │NRF52840  │
   │(BLE)    │           │(Zigbee)      │  │(Mixed) │  │(BLE+802) │
   └────┬────┘           └──────┬───────┘  └───┬────┘  └────┬─────┘
        │                       │              │            │
        └───────────────────────┴──────────────┴────────────┘
                                │
                                ↓
                    ┌─────────────────────────┐
                    │ PCAP File Aggregator    │
                    │ (Threaded, non-blocking)│
                    └────────────┬────────────┘
                                │
                    ┌───────────┴───────────┐
                    ↓                       ↓
            ┌──────────────┐        ┌──────────────┐
            │ PCAP Files   │        │PostgreSQL    │
            │ (50GB+)      │        │(indexed)     │
            └──────┬───────┘        └───────┬──────┘
                   │                        │
                   └────────────┬───────────┘
                                ↓
                    ┌─────────────────────────┐
                    │ Protocol Parsers        │
                    │ • 802.15.4 MAC          │
                    │ • Zigbee NWK           │
                    │ • BLE Link Layer       │
                    │ • GATT/ATT             │
                    └────────────┬────────────┘
                                │
                                ↓
                    ┌─────────────────────────┐
                    │ Vulnerability Analysis  │
                    │ • Crypto weaknesses     │
                    │ • Protocol violations   │
                    │ • Known CVEs            │
                    │ • Fuzzing crashes       │
                    └────────────┬────────────┘
                                │
                    ┌───────────┴───────────┐
                    ↓                       ↓
            ┌──────────────┐        ┌──────────────┐
            │ JSON Report  │        │ PDF Report   │
            │ (structured) │        │ (formatted)  │
            └──────────────┘        └──────────────┘
                                │
                                ↓
                    ┌─────────────────────────┐
                    │ Web Dashboard           │
                    │ (Flask + Plotly)        │
                    │ - Attack Timeline       │
                    │ - Device Topology       │
                    │ - Threat Intelligence   │
                    └─────────────────────────┘
```

---

**Document Version:** 1.0  
**Last Updated:** December 15, 2025  
**Architecture Review Status:** Complete
