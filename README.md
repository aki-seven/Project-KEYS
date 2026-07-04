KEYS — Initial Access Intelligence (IAI)

Modular reconnaissance and enumeration framework built for offensive security workflows.
Designed around asynchronous execution, service-aware automation, YAML-driven extensibility, and a live TUI interface.

Overview

KEYS is a Python-based reconnaissance orchestration framework focused on:

Automated enumeration
Service-aware scan recommendations
Concurrent task execution
Config-driven scan management
Real-time TUI monitoring
Modular offensive tooling integration

Unlike traditional wrapper scripts, KEYS is structured more like an execution platform:

scans are abstracted into YAML definitions
execution is managed through a scheduler
scans are fingerprinted to prevent duplicates
resource locking prevents conflicts
asynchronous workers stream live output
state is centrally tracked and updated in real time

The framework is intended for:

penetration testing
lab environments
HTB / CTF workflows
internal security assessments
reconnaissance automation research
Features
Core Features
Async concurrent scan execution
Live Textual-based TUI
YAML-driven scan definitions
Duplicate scan prevention
Resource locking system
Queue + scheduler architecture
Real-time scan output streaming
Centralized state tracking
Service-aware enumeration
Structured execution contexts
Automatic logging
Theme engine support
Supported Tooling
Network
Nmap
Masscan
Web
FFUF
Gobuster
Feroxbuster
Nikto
Nuclei
WPScan
SMB
Enum4Linux
SMBMap
SMBClient
NetExec
Brute Force
Hydra
SMTP
smtp-user-enum
SNMP
snmpwalk
Architecture
High-Level Design
                +----------------------+
                |      Textual TUI     |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |    Worker Manager    |
                +----------+-----------+
                           |
            +--------------+--------------+
            |                             |
            v                             v
 +-------------------+        +-------------------+
 |     Scheduler     |        | Resource Locking  |
 +-------------------+        +-------------------+
            |
            v
 +-------------------+
 | Execution Context |
 +-------------------+
            |
            v
 +-------------------+
 | Async Workers     |
 +-------------------+
            |
            v
 +-------------------+
 | External Tools    |
 +-------------------+
Execution Pipeline
1. Bootstrap Validation

Before startup, KEYS validates:

Python version
required Python packages
required offensive security tools

Implemented in:

keys/core/bootstrap.py
2. Config Loading

All scans are loaded dynamically from YAML.

keys/config/scans/

Each scan contains:

category
service mapping
parameters
command template
descriptions
tags

Example:

- category: Enumeration
  subcategory: Web
  group: Gobuster

  name: Gobuster Directories
  tool: gobuster

  command: gobuster dir -u {url} -w {wordlist}

No hardcoded scan logic is required.

3. Scheduling

The scheduler:

manages queue order
enforces concurrency limits
prevents duplicate scans
handles dispatch logic

Implemented in:

keys/execution/scheduler.py
4. Resource Locking

KEYS prevents conflicting scans from running simultaneously against the same service.

Resource key structure:

(target, service, port, protocol)

This avoids:

duplicate scans
unnecessary noise
tool collisions

Implemented in:

keys/execution/locks.py
5. Worker Execution

Each scan executes inside an isolated async worker.

Workers:

stream live output
batch UI updates
log all output
support cancellation
manage subprocess lifecycle

Implemented in:

keys/execution/worker.py
6. State Tracking

Global intelligence state tracks:

discovered ports
services
findings
recommended services

Implemented in:

keys/core/state.py
Project Structure
Keys/
├── config/
├── src/
│   └── keys/
│       ├── config/
│       │   └── scans/
│       ├── core/
│       ├── execution/
│       ├── tui/
│       └── main.py
├── requirements.txt
├── pyproject.toml
└── dockerfile
Directory Breakdown
core/

Framework internals.

Contains
bootstrap validation
config parsing
state management
tool registry
output parsers
execution/

Execution engine.

Contains
scheduler
workers
queue manager
locks
execution contexts
fingerprinting
logging

This is effectively the orchestration layer.

tui/

Textual-based live interface.

Contains
widgets
modals
themes
status bars
event handling
config/scans/

YAML scan definitions.

Framework behavior is largely driven from here.

New scans can be added without touching Python code.

Installation
Requirements
Python
Python 3.10+
Linux Tools
nmap
ffuf
gobuster
feroxbuster
nikto
nuclei
hydra
Clone Repository
git clone <repo-url>
cd Keys
Install Python Dependencies
pip install -r requirements.txt

Or:

pip install .
Install System Tools (Debian/Kali)
sudo apt install nmap ffuf gobuster feroxbuster hydra

Some tools require manual installation:

nuclei
nikto
wpscan
netexec
Usage
Launch Framework
keys <target>

Example:

keys 10.10.10.10

Or:

keys example.com
Configuration
Themes

Theme config:

keys/config/theme.json

Available themes:

ghostwire
bloodmoon
emberstrike
offsec
Wordlists

Global wordlists:

keys/config/scans/wordlists.yaml

Modify paths based on your distro.

Adding New Scans

Create a new YAML file:

config/scans/custom/mytool.yaml

Example:

scans:

  - category: Enumeration
    subcategory: Custom

    name: Example Scan
    tool: exampletool

    services:
      - http

    command: exampletool {target}

    parameters:
      target:
        type: string
        default: ""

    description: Example scan

Framework auto-loads it at startup.

Logging

All scan output is logged automatically.

Default path:

~/Intel/Reports/<target>/<scan-name>/

Each execution gets a dedicated log file.

Concurrency Model

KEYS uses:

asyncio
async subprocesses
queue scheduling
resource locks

Benefits:

scalable execution
low blocking overhead
live interactive output
controlled parallelism
Design Philosophy

KEYS was designed around several principles:

1. Config Over Hardcoding

Most framework behavior should come from configuration.

2. Service-Aware Execution

Scans should respond to discovered intelligence dynamically.

3. Orchestration First

The framework is intended to coordinate tools rather than replace them.

4. Extensibility

New scan categories should require minimal code changes.

5. Real-Time Visibility

Operators should always see:

queue state
running scans
output
failures
findings
Current Capabilities
Async scan orchestration
Queue management
TUI execution monitoring
Modular YAML scans
Duplicate prevention
Service-aware scan grouping
Scan fingerprinting
Log persistence
Theme system

Security Notice

This framework is intended for:

authorized testing
lab environments
research
education

Do not use against systems without permission.

Technical Highlights
Scheduler Design

The scheduler supports:

active fingerprint tracking
pending fingerprint tracking
dynamic dispatching
concurrency-aware scheduling
Fingerprinting

Each scan receives a SHA256 fingerprint built from:

target
service
port
protocol
command

This prevents redundant execution.

Resource Isolation

Execution contexts encapsulate:

scan metadata
parameters
runtime state
target intelligence
Packaging

Project uses modern Python packaging via:

pyproject.toml

CLI entrypoint:

[project.scripts]
keys = "keys.main:main"
Tech Stack
Python
asyncio
Textual
Rich
YAML
Pydantic