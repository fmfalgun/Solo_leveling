# Project 2: Wireless Protocol Security - Detailed Project Timeline & Gantt Chart
## Week-by-Week Execution Plan with Milestones & Dependencies

---

## EXECUTIVE TIMELINE

```
Project Duration: 12 Weeks (300-400 hours)
Recommended Start: January 2026 (Post-Project 1)
Expected Completion: March-April 2026
Pace: 25-35 hours/week sustained effort
Critical Path: Phase 3-4 (Weeks 3-8)
```

---

## PHASE-LEVEL GANTT CHART

```
PHASE TIMELINE (12 WEEKS)
═══════════════════════════════════════════════════════════════════════════════

PHASE 1: RESEARCH & THREAT ANALYSIS (2 weeks, 50 hours)
├─ Week 1: Threat Landscape & Protocol Study
│  └─ ███████████████████ 40%
├─ Week 2: Testing Strategy & Hardware Planning  
│  └─ ████████████████████ 100%
└─ Deliverables: Threat model, protocol reference, CVE matrix

PHASE 2: HARDWARE SETUP & CONFIGURATION (2 weeks, 40 hours)
├─ Week 2-3: Device Procurement & Firmware Flashing
│  └─ ████████████████████ 100%
├─ Ubertooth One (3 hours)      █████████
├─ CC2531 x2 (4 hours)          ██████████████
├─ XBee S3B x3 (12 hours)       ████████████████████████████████████████
├─ NRF52840 x2 (10 hours)       ██████████████████████████████
└─ Network Integration (5 hours) ███████████████

PHASE 3: PACKET CAPTURE & ANALYSIS (3 weeks, 80 hours)
├─ Week 3: Capture Infrastructure (40 hours)
│  └─ ████████████████████ 100%
├─ Week 4-5: Baseline Traffic Collection & Parsing (40 hours)
│  └─ ███████████████████ 90%
├─ Database Schema & Setup (8 hours)      ████████████████
├─ Multi-device Sniffer Dev (15 hours)    ██████████████████████████████
├─ Traffic Collection (20 hours)          ████████████████████████████████████████
├─ Protocol Parsing (20 hours)            ████████████████████████████████████████
└─ Cryptographic Analysis (10 hours)      ████████████████████

PHASE 4: VULNERABILITY EXPLOITATION (4 weeks, 120 hours)
├─ Week 5-8: Active Exploitation & Tool Development
├─ Key Extraction Attacks (25 hours)      ██████████████████████████████████████████████████
├─ Session Hijacking (20 hours)           ████████████████████████████████████████
├─ Replay Attacks (15 hours)              ██████████████████████████████
├─ DoS Implementation (15 hours)          ██████████████████████████████
├─ Protocol Fuzzer (25 hours)             ██████████████████████████████████████████████████
├─ Device Impersonation (10 hours)        ████████████████████
└─ Exploitation Testing (10 hours)        ████████████████████

PHASE 5: TOOL INTEGRATION & DOCUMENTATION (3 weeks, 100 hours)
├─ Week 8-10: Toolkit Development
├─ Integrated CLI Framework (30 hours)    ██████████████████████████████████████████████████████████████
├─ Automated Reporting (25 hours)         ██████████████████████████████████████████████████
├─ Web Dashboard Dev (25 hours)           ██████████████████████████████████████████████████
├─ API Documentation (15 hours)           ██████████████████████████████
└─ User Guides (5 hours)                  ██████████

PHASE 6: TESTING & VALIDATION (3 weeks, 80 hours)
├─ Week 10-12: Real-World Device Testing
├─ Smart Lock Assessment (15 hours)       ██████████████████████████████
├─ Sensor Device Testing (10 hours)       ████████████████████
├─ Cross-Device Compatibility (10 hours)  ████████████████████
├─ Performance Benchmarking (15 hours)    ██████████████████████████████
├─ Bug Fixes & Refinement (20 hours)      ████████████████████████████████████████
└─ Final Documentation (10 hours)         ████████████████████

PHASE 7: PUBLICATION & CAREER IMPACT (Ongoing, 50+ hours)
├─ Responsible Disclosure (10 hours)      ████████████████████
├─ Technical Paper Writing (30 hours)     ██████████████████████████████████████████████████████████████
├─ Blog Post Series (25 hours)            ██████████████████████████████████████████████████
├─ Conference Talk Prep (20 hours)        ████████████████████████████████████████
└─ Community Engagement (ongoing)

TOTAL PROJECT DURATION: 12 weeks (300-400 hours)
```

---

## WEEKLY DETAILED BREAKDOWN

### WEEK 1: Threat Assessment & Protocol Study (50 hours)

```
Day 1-2 (Tuesday-Wednesday): Threat Landscape Research
├─ MITRE IoT ATT&CK framework analysis
│  └─ Extract 50+ relevant attack techniques
├─ CVE database correlation
│  └─ Identify 30+ related vulnerabilities
├─ Threat model documentation
│  └─ Create STRIDE analysis (6 categories × 5-10 each)
└─ Deliverable: 20-page threat assessment document

Day 3-4 (Thursday-Friday): Protocol Specification Study
├─ IEEE 802.15.4 core specification reading (8 hours)
│  └─ Document: PHY/MAC layers, frame formats
├─ Zigbee Alliance documents (8 hours)
│  └─ Document: NWK layer, clustering, routing
├─ Bluetooth 5.0 specification (10 hours)
│  └─ Document: Link layer, GAT T/ATT profiles
└─ Deliverable: 30-page protocol reference guide

HOURS: 40 hours research + 10 hours documentation = 50 hours total
```

### WEEK 2: Tool Evaluation & Hardware Planning (40 hours)

```
Day 1-2: Tool Ecosystem Analysis
├─ Killerbee evaluation (4 hours)
├─ Z3c fuzzer testing (4 hours)
├─ Sweyntooth assessment (4 hours)
├─ BtleJack hijacking tool (4 hours)
└─ Deliverable: 15-page tool comparison matrix

Day 3-4: Hardware Planning & Ordering
├─ Supplier research & pricing (2 hours)
├─ Create procurement checklist (1 hour)
├─ Estimate lead times (1 hour)
├─ Order placement ($2,000+ hardware) (1 hour)
├─ Budget tracking spreadsheet (1 hour)
└─ Deliverable: Procurement documentation, tracking sheet

Day 5: Week 1-2 Summary & Preparation for Phase 2
├─ Consolidate all documentation (2 hours)
├─ Create testing schedule (2 hours)
├─ Risk assessment (2 hours)
└─ Deliverable: Combined Phase 1 report (50+ pages)

HOURS: 30 hours analysis + 10 hours planning = 40 hours total
```

### WEEK 3: Ubertooth & CC2531 Configuration (40 hours)

```
Monday-Tuesday: Ubertooth One Setup (3-4 hours)
├─ Unbox, inspect, document serial number
├─ USB driver installation & verification
├─ Firmware download & flashing
├─ BLE capture test (channel 37/38/39)
├─ Scapy integration wrapper
└─ Deliverable: Operational Ubertooth, config docs

Wednesday: CC2531 Sniffer Setup (2-3 hours)
├─ Firmware flashing (sniffer mode)
├─ Wireshark plugin installation
├─ Test Zigbee frame capture
└─ Deliverable: Sniffer operational, Wireshark working

Thursday: CC2531 Coordinator Setup (2-3 hours)
├─ Firmware flashing (coordinator mode)
├─ Network creation (PAN ID 0xAAAA, Channel 15)
├─ Device pairing test
└─ Deliverable: Coordinator operational, network active

Friday: XBee Initial Setup (4-5 hours, continuing into next week)
├─ XCTU installation & configuration
├─ Serial connection setup
├─ Firmware identification
├─ AT mode testing
└─ Deliverable: XBees detected in XCTU

HOURS: 13-18 hours device setup + 22-27 hours concurrent tool development = 40 hours
```

### WEEK 4: XBee & NRF52840 Configuration (40 hours)

```
Monday-Wednesday: XBee S3B Setup (12-15 hours)
├─ Device #1: Fuzzer configuration
│  ├─ TX power maximization (ATPL FF)
│  ├─ API mode setup (ATAP 2)
│  └─ Custom firmware (optional)
├─ Device #2: Sniffer configuration
│  ├─ Monitor mode (ATMM 1)
│  └─ Frame buffering
└─ Device #3: Device simulator
   └─ Valid profile loading & response setup

Thursday-Friday: NRF52840 DK Setup (15-18 hours)
├─ nRF5 SDK installation
├─ GCC ARM toolchain setup
├─ J-Link driver installation
├─ Firmware programming
├─ BLE example compilation
├─ UART debugging
└─ Deliverable: Both DKs operational, BLE advertising verified

HOURS: 27-33 hours hardware setup + 7-13 hours integration = 40 hours
```

### WEEK 5: Capture Infrastructure & Initial Traffic Collection (50 hours)

```
Monday-Tuesday: Multi-Device Sniffer Development (20 hours)
├─ Python threading architecture (5 hours)
├─ USB multi-device handling (5 hours)
├─ Packet queue aggregation (3 hours)
├─ PCAP file writing (4 hours)
├─ Database schema design (3 hours)
└─ Deliverable: Multi-device sniffer operational

Wednesday-Friday: Traffic Collection & Initial Analysis (30 hours)
├─ Start continuous multi-device capture (10+ hour runs)
├─ Collect 20-30 GB PCAP data
├─ Device discovery & inventory
├─ Interaction sequence capture (lock/unlock, sensor reads)
├─ Edge case scenarios (out of range, rejoin)
└─ Deliverable: 50GB+ PCAP collection, device inventory

HOURS: 50 hours sustained effort
```

### WEEK 6: Protocol Parsing & Analysis (60 hours)

```
Full Week: Deep Protocol Analysis & Decoding
├─ IEEE 802.15.4 MAC parser (12 hours)
│  └─ Frame type, address fields, security metadata
├─ Zigbee NWK parser (12 hours)
│  └─ Header parsing, frame reassembly, route tracking
├─ BLE Link Layer parser (12 hours)
│  └─ PDU types, CRC validation, channel classification
├─ Cryptographic analysis (15 hours)
│  └─ Key material detection, encryption mode identification
├─ Traffic pattern recognition (9 hours)
│  └─ Device fingerprinting, behavior profiling
└─ Deliverable: 100+ identified vulnerabilities, analysis database

HOURS: 60 hours focused analysis work
```

### WEEK 7: Vulnerability Exploitation - Part 1 (60 hours)

```
Monday-Tuesday: Key Extraction Attacks (15 hours)
├─ Static key identification & extraction (5 hours)
├─ Weak KDF cracking setup (5 hours)
├─ Rainbow table lookups (3 hours)
├─ Validate recovered keys (2 hours)
└─ Deliverable: 3+ extracted encryption keys

Wednesday-Thursday: Replay Attacks (15 hours)
├─ Command identification (3 hours)
├─ Frame extraction & modification (4 hours)
├─ Replay implementation (4 hours)
├─ Testing & verification (4 hours)
└─ Deliverable: Working replay PoC, device behavior logs

Friday: Session Hijacking Setup (10 hours)
├─ Connection tracking (3 hours)
├─ Channel prediction (3 hours)
├─ Packet injection framework (4 hours)
└─ Deliverable: Hijacking framework skeleton

HOURS: 40 hours active exploitation + 20 hours documentation = 60 hours
```

### WEEK 8: Vulnerability Exploitation - Part 2 (60 hours)

```
Monday: Session Hijacking Implementation (15 hours)
├─ BLE takeover mechanism
├─ Timing synchronization
├─ Verify successful hijack
└─ Deliverable: BLE hijacking PoC

Tuesday: DoS Implementation (15 hours)
├─ BLE advertisement flooding
├─ Zigbee coordinator spoofing
├─ Network disruption testing
└─ Deliverable: DoS implementations, impact metrics

Wednesday-Friday: Fuzzing & Crash Discovery (30 hours)
├─ Protocol fuzzer development (10 hours)
├─ Mutation strategy implementation (5 hours)
├─ Fuzzing campaign (1000-5000 mutants) (10 hours)
├─ Crash analysis & categorization (5 hours)
└─ Deliverable: Crash corpus, minimal reproducers

HOURS: 60 hours exploitation intensive work
```

### WEEK 9: Tool Integration & Automation (50 hours)

```
Monday-Tuesday: Integrated CLI Toolkit (20 hours)
├─ Main framework architecture
├─ Subcommand system (sniff, parse, exploit, fuzz, report)
├─ Configuration file support
├─ Logging & error handling
└─ Deliverable: Working CLI tool

Wednesday-Thursday: Automated Reporting (15 hours)
├─ PDF report generation (ReportLab)
├─ JSON export functionality
├─ MITRE ATT&CK mapping
├─ HTML summary generation
└─ Deliverable: Automated report generation

Friday: Dashboard Foundation (15 hours)
├─ Flask backend setup
├─ Database API endpoints
├─ Basic visualization (Plotly)
└─ Deliverable: Dashboard running locally

HOURS: 50 hours active development
```

### WEEK 10: Dashboard & Documentation (50 hours)

```
Monday-Wednesday: Web Dashboard Development (25 hours)
├─ Interactive attack timeline
├─ Device topology visualization
├─ Traffic statistics dashboard
├─ Real-time update capability
└─ Deliverable: Fully functional web dashboard

Thursday-Friday: API Documentation & Guides (25 hours)
├─ API reference (20+ pages)
├─ Installation guide
├─ Quick-start guide
├─ Troubleshooting guide
├─ Example notebooks
└─ Deliverable: 50+ pages documentation

HOURS: 50 hours documentation & development
```

### WEEK 11: Real-World Device Testing (50 hours)

```
Monday: Smart Lock Assessment (15 hours)
├─ Identify target lock model
├─ Capture pairing sequence
├─ Attempt key extraction
├─ Test replay attacks
├─ Document findings
└─ Deliverable: Smart lock vulnerability report

Tuesday-Wednesday: Sensor Device Testing (15 hours)
├─ Identify sensor model
├─ Capture normal operation
├─ Attempt data spoofing
├─ Verify robustness
└─ Deliverable: Sensor security assessment

Thursday-Friday: Cross-Device Testing (20 hours)
├─ Test toolkit on 5+ device models
├─ Document compatibility
├─ Create device-specific configs
├─ Fix any compatibility issues
└─ Deliverable: Compatibility matrix, config pack

HOURS: 50 hours hands-on testing
```

### WEEK 12: Performance Testing & Finalization (50 hours)

```
Monday-Tuesday: Performance Benchmarking (15 hours)
├─ Capture rate measurement
├─ CPU/memory profiling
├─ Database performance testing
├─ Optimization & tuning
└─ Deliverable: Performance report

Wednesday: Final Bug Fixes & Polish (15 hours)
├─ Bug fixing from testing phase
├─ Code cleanup & refactoring
├─ Documentation updates
├─ Final review & QA
└─ Deliverable: Production-ready code

Thursday-Friday: Release & Handoff (20 hours)
├─ Final documentation complete
├─ GitHub repository clean & organized
├─ README & getting started guides
├─ Release v1.0 on GitHub
└─ Deliverable: Public release, official documentation

HOURS: 50 hours finalization work
```

### WEEK 13+: Publication & Career Impact (Ongoing)

```
Responsible Disclosure (10 hours)
├─ Vendor identification
├─ Vulnerability notifications
├─ 90-day embargo management
└─ CVE coordination

Technical Paper Writing (30-40 hours)
├─ Paper research & organization
├─ Writing & revision
├─ Peer review incorporation
├─ Conference submission
└─ Venue: arXiv, IEEE S&P, NDSS, USENIX

Blog Post Series (20-25 hours)
├─ 5-8 blog posts (1000-2000 words each)
├─ Publication on Medium, Dev.to, personal blog
└─ Promotion through security channels

Conference Talk (15-20 hours)
├─ Talk submission to Black Hat, DefCon, etc.
├─ Slide deck creation (50-60 slides)
├─ Demo video recording (3-5 videos)
└─ Event preparation & presentation

TOTAL ONGOING: 50+ hours beyond Week 12
```

---

## CRITICAL PATH ANALYSIS

**Critical Path (Longest Sequence):**
```
Week 3-4: Hardware Setup (80 hours)
  ↓
Week 5-6: Traffic Collection & Parsing (110 hours)
  ↓
Week 7-8: Exploitation & Vulnerability Finding (120 hours)
  ↓
Week 9-10: Tool Integration & Documentation (100 hours)
  ↓
Week 11-12: Real-World Testing & Release (100 hours)

CRITICAL PATH DURATION: 12 weeks
SLACK: Minimal (hardware procurement lead times are critical)
```

**Dependencies:**
- Phase 2 (Hardware) → Phase 3 (Capture) → Phase 4 (Exploitation)
- Phase 4 (Exploits) → Phase 5 (Integration) → Phase 6 (Testing)
- All phases → Phase 7 (Publication)

---

## RESOURCE ALLOCATION BY WEEK

| Week | Phase | Hours | Key Activity | Milestone |
|---|---|---|---|---|
| 1 | P1 | 50 | Research & protocol study | Threat model complete |
| 2 | P1-P2 | 40 | Tool eval & hardware order | Devices ordered |
| 3 | P2 | 40 | Ubertooth & CC2531 setup | 2/6 devices operational |
| 4 | P2 | 40 | XBee & NRF52840 setup | All 6 devices operational ✓ |
| 5 | P3 | 50 | Capture infrastructure & traffic | 50GB PCAP collected |
| 6 | P3-P4 | 60 | Protocol parsing & initial exploits | 100+ vulns identified |
| 7 | P4 | 60 | Key extraction & replay attacks | 5+ working exploits |
| 8 | P4-P5 | 60 | DoS & fuzzing, tool integration | Integrated toolkit ready |
| 9 | P5 | 50 | CLI & reporting automation | Production tools complete |
| 10 | P5 | 50 | Dashboard & documentation | Documentation complete |
| 11 | P6 | 50 | Real-world device testing | Real-world validation ✓ |
| 12 | P6 | 50 | Performance & release | v1.0 released on GitHub |
| 13+ | P7 | 50+ | Publication & career impact | Papers submitted, talks accepted |

**TOTAL: 300-400 hours over 12 weeks (25-35 hours/week)**

---

## MILESTONE CHECKLIST

### Monthly Milestones

**End of Month 1 (Week 4):**
- [ ] All hardware operational (6/6 devices)
- [ ] Multi-device capture infrastructure working
- [ ] Initial 50GB traffic collected
- [ ] Phase 1-2 documentation complete

**End of Month 2 (Week 8):**
- [ ] 100+ vulnerabilities identified & documented
- [ ] 5+ working exploitation PoCs
- [ ] Key extraction demonstrated
- [ ] Fuzzing framework operational
- [ ] Phase 3-4 complete

**End of Month 3 (Week 12):**
- [ ] Integrated toolkit v1.0 released
- [ ] Real-world device testing complete
- [ ] 100+ pages documentation
- [ ] GitHub repository public with 5,000+ stars (goal)
- [ ] All phases complete

**Ongoing (Week 13+):**
- [ ] Technical paper published
- [ ] Blog series (5-8 posts) published
- [ ] Conference talk accepted
- [ ] Industry consulting inquiries received

---

## DECISION GATES & GO/NO-GO CRITERIA

### Phase 1→2 Gate (End of Week 2)
**Decision:** Proceed with hardware procurement?
**Go Criteria:**
- ✓ Threat model satisfactory
- ✓ Budget approved
- ✓ Time commitment confirmed
- ✓ Hardware suppliers identified

### Phase 2→3 Gate (End of Week 4)
**Decision:** Hardware sufficiently operational for traffic collection?
**Go Criteria:**
- ✓ All 6 devices working
- ✓ Multi-device capture verified
- ✓ Zero device conflicts
- ✓ PCAP file writing operational

### Phase 3→4 Gate (End of Week 6)
**Decision:** Ready for exploitation phase?
**Go Criteria:**
- ✓ 50GB+ traffic collected
- ✓ 100+ vulnerabilities identified
- ✓ Protocol parsers working
- ✓ Vulnerability analysis complete

### Phase 4→5 Gate (End of Week 8)
**Decision:** Exploitation sufficiently comprehensive for tooling?
**Go Criteria:**
- ✓ 5+ working exploits
- ✓ Crash corpus (100+ crashes)
- ✓ Fuzzing producing results
- ✓ Key extraction successful

### Phase 5→6 Gate (End of Week 10)
**Decision:** Tools production-ready for real-world testing?
**Go Criteria:**
- ✓ CLI tool working
- ✓ Documentation complete
- ✓ Dashboard operational
- ✓ API stable

### Phase 6→7 Gate (End of Week 12)
**Decision:** Ready for public release & publication?
**Go Criteria:**
- ✓ Real-world testing successful
- ✓ No critical bugs
- ✓ Responsible disclosure plan ready
- ✓ GitHub repository clean

---

**Timeline Version:** 1.0  
**Last Updated:** December 15, 2025  
**Estimated Completion:** April 15, 2026  
**Status:** Ready for Execution
