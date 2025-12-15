# Project 2: Wireless Protocol Security - Complete Developer Tools & Hardware Stack
## From Lab Setup to Production Deployment

---

## PART 1: WIRELESS HARDWARE & EQUIPMENT

### 1.1 Primary Wireless Transceivers

| Device | Type | Protocol | Frequency | Capabilities | Cost | Use Case | Setup Time |
|---|---|---|---|---|---|---|---|
| **Ubertooth One** | USB Sniffer | BLE/802.15.4 | 2.4 GHz ISM | Full BLE packet capture, Bluetooth jamming | $200 | BLE analysis, monitoring | 2-3 hours |
| **CC2531 USB Dongle** | USB Coordinator | Zigbee | 2.4 GHz ISM | Zigbee network join, packet capture, ZLL | $30 x2 | Zigbee coordinator + sniffer | 1-2 hours each |
| **XBee S3B Module** | Serial/USB | Zigbee/802.15.4 | 2.4 GHz ISM | Full stack analysis, firmware updates | $40 x3 | Device simulation, fuzzing | 3-4 hours each |
| **NRF52840 DK** | Development Kit | BLE 5.0 + 802.15.4 | 2.4 GHz ISM | Full BLE/Thread stack, firmware development | $80 x2 | Custom BLE exploitation, fuzzing | 4-5 hours each |
| **Raspberry Pi 4 8GB** | Single-Board Computer | N/A (hosts devices) | N/A | Central analysis workstation, packet processing | $120 | Gateway, data aggregation, database | 2 hours |
| **Software-Defined Radio (USRP)** | Generic RF | Configurable | 1 MHz - 6 GHz | Frequency analysis, signal inspection (optional) | $400-$1,000 | Advanced RF analysis (optional) | 5-6 hours |

### 1.2 Supporting Hardware & Accessories

| Item | Purpose | Specifications | Cost | Notes |
|---|---|---|---|---|
| **USB Hub (7-port)** | Connect multiple devices | USB 3.0, powered | $30 | Essential for connecting all transceivers |
| **RF Shielded Box/Faraday Cage** | Isolation & measurement | 1m x 1m x 1m aluminum or wood | $300-$1,000 | Optional but recommended for clean testing |
| **RF Attenuator (10dB, 20dB)** | Signal level control | 2.4 GHz rated | $20-40 | Prevent receiver saturation |
| **SMA Adapters & Cables** | Cable connections | Various connectors | $50 | Ensure devices can connect without damage |
| **Logic Analyzer (24-channel)** | Protocol-level analysis | 1 GHz sampling | $30-50 | Capture SPI/UART debug signals |
| **Oscilloscope (100 MHz+)** | Signal inspection | Digital or analog | $200-$500 | Optional for advanced RF work |
| **Smart Lock Test Device** | Real-world target | Zigbee/BLE enabled | $50-200 | Yale, Logitech Circle, Philips Hue |
| **Temperature/Humidity Sensor** | IoT device testing | Zigbee certified | $30-100 | Legitimate IoT endpoint |
| **Industrial Wireless Controller** | OT/ICS testing | Zigbee DIN rail | $200-500 | Rockwell, Honeywell devices (optional) |

---

## PART 2: DEVELOPMENT ENVIRONMENT SETUP

### 2.1 Operating System & System Configuration

| Component | Recommended | Version | Installation | Rationale |
|---|---|---|---|---|
| **Primary OS** | Linux (Arch/Garuda XFCE) | Latest | Native installation or VM | Native wireless driver support, full control |
| **Secondary OS** | Linux (Ubuntu/Debian) | 22.04 LTS | Virtual machine | Compatibility with community tools |
| **Virtualization** | KVM/QEMU | Latest | `pacman -S qemu virt-manager` | Hardware passthrough for USB devices |
| **Kernel Modules** | USB driver stack | Latest 6.0+ | `modprobe usbserial ftdi_sio` | Device recognition |
| **Permissions** | udev rules | custom | `/etc/udev/rules.d/99-usb.rules` | Non-root device access |

### 2.2 Programming Languages & Frameworks

| Language | Version | Installation | Purpose | Use Case |
|---|---|---|---|---|
| **Python** | 3.10+ | `pacman -S python python-pip` | Primary development | All analysis tools, fuzzing, automation |
| **C/C++** | GCC 12.2+ | `pacman -S gcc cmake` | Performance-critical tools | Packet processing, real-time analysis |
| **Go** | 1.19+ | `pacman -S go` | High-performance services | Distributed analysis (optional) |
| **Rust** | 1.65+ | `pacman -S rustup` | System-level tools | Memory-safe packet manipulation |
| **Bash/Zsh** | Latest | Built-in | Scripting & automation | Deployment, CI/CD pipelines |

### 2.3 Core Wireless Security Tools

| Tool | Type | Installation | Version | Purpose | Cost |
|---|---|---|---|---|---|
| **Wireshark** | Network Sniffer | `pacman -S wireshark` | 4.0+ | Protocol analysis, PCAP visualization | Free |
| **Scapy** | Packet Library | `pip install scapy` | 2.5+ | Custom packet creation/manipulation | Free |
| **TShark** | CLI Wireshark | `pacman -S wireshark-cli` | 4.0+ | Automated packet analysis | Free |
| **tcpdump** | Raw Capture | `pacman -S tcpdump` | Latest | Low-level packet capture | Free |
| **GNU Radio** | SDR Framework | `pacman -S gnuradio` | 3.10+ | Signal processing, frequency analysis | Free |
| **CubicSDR** | SDR Visual | `pacman -S cubicsdr` | Latest | Real-time spectrum visualization | Free |
| **Burp Suite** | Web Security | Download from burp | Community | API testing for wireless gateways | Free/Pro |
| **Metasploit Framework** | Exploitation Platform | `pacman -S metasploit` | 6.0+ | Pre-built exploits (reference) | Free |

### 2.4 Zigbee & BLE-Specific Tools

| Tool | Purpose | Installation | Features | Cost |
|---|---|---|---|---|
| **Z3c-js** | Zigbee Fuzzing | `npm install -g z3c-js` | Protocol fuzzing, vulnerability discovery | Free |
| **Zigbee2MQTT** | Zigbee Gateway | Docker or pip | Device bridging, network analysis | Free |
| **XCTU** | XBee Configuration | Download from Digi | Device programming, firmware updates | Free |
| **nRF Connect** | Nordic BLE Tools | Download/APK | Device scanning, GATT exploration | Free |
| **Bluez** | Linux Bluetooth | `pacman -S bluez` | BLE client/server, GATT tools | Free |
| **btmon** | Bluetooth Monitor | `pacman -S bluez` | Real-time protocol logging | Free |
| **BtleJack** | BLE Hijacking | `git clone + make` | Session takeover, packet injection | Free |
| **nRF Sniffer for Wireshark** | Capture Plugin | Download from Nordic | BLE packet capture in Wireshark | Free |

### 2.5 Cryptography & Key Analysis Libraries

| Library | Purpose | Installation | Features | Language |
|---|---|---|---|---|
| **PyCryptodome** | Cryptographic Ops | `pip install pycryptodome` | AES, SHA, HMAC implementations | Python |
| **cryptography** | Modern Cryptography | `pip install cryptography` | High-level API, key derivation | Python |
| **libsodium** | Secret Box Encryption | `pacman -S libsodium` | Authenticated encryption | C/C++ |
| **OpenSSL** | SSL/TLS & Crypto | `pacman -S openssl` | Certificate handling, encryption | CLI/Library |
| **SageMath** | Symbolic Math | `pacman -S sagemath` | Elliptic curve analysis, discrete log | Python |
| **SymPy** | Symbolic Computation | `pip install sympy` | Mathematical problem solving | Python |

### 2.6 Reverse Engineering & Firmware Analysis

| Tool | Purpose | Installation | Features | Cost |
|---|---|---|---|---|
| **Ghidra** | Disassembler/Decompiler | Download from NSA | ARM/Thumb analysis, scripting API | Free |
| **IDA Free** | Interactive Disassembler | Download from Hex-Rays | Industry standard, plugin ecosystem | Free |
| **Radare2** | Reversing Framework | `pacman -S radare2` | Command-line, scriptable, powerful | Free |
| **Binwalk** | Firmware Extractor | `pip install binwalk` | Binary analysis, component extraction | Free |
| **Firmwalker** | Firmware Scanner | `git clone` | Search for security artifacts | Free |
| **Flashrom** | Firmware Programmer | `pacman -S flashrom` | Read/write chip firmware | Free |
| **J-Link Tools** | SEGGER Debug | Download | On-chip debugging, firmware extraction | Free/Commercial |

### 2.7 Data Processing & Analysis

| Library | Purpose | Installation | Performance | Use Case |
|---|---|---|---|---|
| **NumPy** | Numerical Computing | `pip install numpy` | Fast array operations | Signal processing |
| **Pandas** | Data Analysis | `pip install pandas` | Tabular data manipulation | Traffic analysis |
| **SciPy** | Scientific Computing | `pip install scipy` | Signal filtering, statistics | Frequency analysis |
| **Matplotlib** | Visualization | `pip install matplotlib` | 2D plotting | Result visualization |
| **Plotly** | Interactive Plots | `pip install plotly` | Web-based charts | Dashboard integration |
| **Scikit-learn** | Machine Learning | `pip install scikit-learn` | Classification, clustering | Traffic pattern detection |

### 2.8 Development Tools & Workflow

| Tool | Purpose | Installation | Use Case |
|---|---|---|---|
| **VS Code** | Code Editor | `pacman -S code` | Primary IDE with extensions |
| **Git** | Version Control | `pacman -S git` | Repository management |
| **GitHub CLI** | Git Automation | `pacman -S github-cli` | Remote repository ops |
| **Docker** | Containerization | `pacman -S docker` | Reproducible environments |
| **Docker Compose** | Multi-container | `pip install docker-compose` | Full stack orchestration |
| **Jupyter Lab** | Interactive Notebooks | `pip install jupyterlab` | EDA and experimentation |
| **Pytest** | Testing Framework | `pip install pytest` | Automated test suites |
| **Poetry** | Dependency Management | `pip install poetry` | Python project management |
| **Black** | Code Formatter | `pip install black` | Python code standardization |
| **Pylint** | Static Analysis | `pip install pylint` | Code quality assurance |

---

## PART 3: HARDWARE CONFIGURATION PROCEDURES

### 3.1 Ubertooth One Setup (2-3 hours)

```bash
# Install Ubertooth tools
pacman -S ubertooth python-ubertooth

# Verify device
ubertooth-util -s

# Update firmware (if needed)
ubertooth-util -l ubertooth_one_fw.bin

# Start BLE sniffing
ubertooth-btle -c 37 -l ble_capture.pcap

# Alternative: Use with Wireshark
# Settings → Interfaces → nRF Sniffer for Wireshark
```

### 3.2 CC2531 Configuration (1-2 hours per device)

```bash
# Flash CC2531 with sniffer firmware
cd /path/to/cc-tool
./cc-tool -e -w -v -I ihex Zigbee-2.4GHz-Sniffer.hex

# Verify in dmesg
dmesg | grep -i ftdi

# Capture Zigbee frames
wireshark &  # Use Zigbee2MQTT plugin
```

### 3.3 XBee S3B Configuration (3-4 hours per device)

```bash
# Install XCTU (Windows/Mac) or use command-line
# Serial connection at /dev/ttyUSB0

# Read current configuration
miniterm.py /dev/ttyUSB0 9600

# Enter AT mode: +++
# Read firmware: ATVR
# Write new config: ATID 1234

# Enable API mode: ATAP 2
# Save settings: ATWR

# Verify XCTU discovery
```

---

## PART 4: NETWORK ARCHITECTURE FOR TESTING

```
┌─────────────────────────────────────────────────────────────┐
│                 Isolated Testing Network                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        Primary Analysis Workstation (Arch Linux)     │  │
│  │  - Wireshark, TShark, custom Python tools            │  │
│  │  - USB Hub (7-port) for device connections          │  │
│  │  - PostgreSQL for traffic storage                    │  │
│  └──────────┬───────────────────────────────────────────┘  │
│             │                                               │
│  ┌──────────┴───────────────────────────────────────────┐  │
│  │  USB Connections (non-blocking, parallel capture)   │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │ ├─ /dev/ttyUSB0 → Ubertooth One (BLE)               │  │
│  │ ├─ /dev/ttyUSB1 → CC2531 #1 (Zigbee sniffer)        │  │
│  │ ├─ /dev/ttyUSB2 → CC2531 #2 (Zigbee coordinator)   │  │
│  │ ├─ /dev/ttyUSB3 → XBee S3B #1 (Device sim)          │  │
│  │ ├─ /dev/ttyUSB4 → XBee S3B #2 (Fuzzer)              │  │
│  │ ├─ /dev/ttyUSB5 → NRF52840 DK (Debug)               │  │
│  │ └─ /dev/ttyUSB6 → Logic Analyzer                     │  │
│  └────────────┬──────────────────────────────────────────┘  │
│               │                                             │
│  ┌────────────┴──────────────────────────────────────────┐ │
│  │           2.4 GHz RF Environment                      │ │
│  │  (RF Shielded Box or Anechoic Chamber, optional)    │ │
│  ├──────────────────────────────────────────────────────┤ │
│  │ • Smart Lock (Zigbee, test target)                   │ │
│  │ • Temperature Sensor (Zigbee, legitimate endpoint)   │ │
│  │ • BLE Beacon (active broadcast monitoring)           │ │
│  │ • Industrial Wireless Switch (optional target)        │ │
│  │ • Wireless Router (interference reference)           │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Data Flow:
┌─ Live Capture → TShark → PCAP files → PostgreSQL
├─ PCAP → Wireshark (interactive analysis)
├─ Raw packets → Python fuzzer → Modified packets → XBee transmit
└─ Results → JSON reports → Web dashboard
```

---

## PART 5: INSTALLATION CHECKLIST

### Phase 1: System Preparation (1 hour)

```bash
# Update system
sudo pacman -Syu

# Install core tools
sudo pacman -S \
  build-essential cmake git wget curl \
  python python-pip python-virtualenv \
  libusb libusb-compat libftdi \
  wireshark tcpdump \
  docker docker-compose

# Create project directory
mkdir -p ~/projects/wireless-security
cd ~/projects/wireless-security

# Create Python venv
python -m venv venv
source venv/bin/activate
```

### Phase 2: Wireless Tools Installation (2-3 hours)

```bash
# Ubertooth
git clone https://github.com/greatscottgadgets/ubertooth.git
cd ubertooth/host
mkdir build && cd build
cmake ..
make && sudo make install

# CC2531 tools
sudo pacman -S cc-tool

# Install Python wireless libraries
pip install \
  scapy==2.5.0 \
  pycryptodome==3.16.0 \
  cryptography==38.0.0 \
  paho-mqtt==1.6.1 \
  pyserial==3.5 \
  paramiko==2.12.0 \
  construct==2.10.68 \
  pwntools==4.8.0
```

### Phase 3: Development Tools (1-2 hours)

```bash
# Install Ghidra
pacman -S ghidra

# Install Radare2
pacman -S radare2 r2pm

# Install reverse engineering tools
pip install \
  capstone==4.0.2 \
  keystone-engine==0.9.2 \
  unicorn==1.0.3

# Install data analysis
pip install \
  numpy pandas scipy matplotlib seaborn \
  scikit-learn jupyter jupyterlab
```

### Phase 4: Hardware Driver Setup (30 min - 1 hour)

```bash
# Create udev rules for non-root access
sudo tee /etc/udev/rules.d/99-wireless.rules << EOF
# Ubertooth
SUBSYSTEMS=="usb", ATTRS{idVendor}=="1d50", ATTRS{idProduct}=="6002", MODE="0666"

# CC2531 (FTDI)
SUBSYSTEMS=="usb", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", MODE="0666"

# XBee
SUBSYSTEMS=="usb", ATTRS{idVendor}=="0403", MODE="0666"

# NRF52840
SUBSYSTEMS=="usb", ATTRS{idVendor}=="1366", MODE="0666"
EOF

# Reload udev rules
sudo udevadm control --reload
sudo udevadm trigger
```

---

## PART 6: COST SUMMARY

| Category | Items | Estimated Cost |
|---|---|---|
| **Wireless Devices** | 6 main transceivers | $1,000 |
| **Supporting Hardware** | Cables, hub, adapters | $200 |
| **Shielded Testing Environment** | RF box or cage | $300-$1,000 |
| **Measurement Equipment** | Oscilloscope, analyzer (optional) | $500-$1,000 |
| **Target Devices** | Smart lock, sensors | $200-$500 |
| **Software (Commercial)** | IDA, Burp Suite pro (optional) | $0-$1,500 |
| **Cloud Resources** | EC2, S3 for data (optional) | $50-$100/month |
| **Development Setup** | Laptop/workstation (existing) | $0 |
| **TOTAL FIRST SETUP** | **All hardware + software** | **$2,250-$5,000** |
| **MONTHLY OPERATIONAL** | Colocation, cloud, subscriptions | **$50-$200** |

---

**Document Version:** 1.0  
**Last Updated:** December 15, 2025  
**Setup Time Estimate:** 20-25 hours total
