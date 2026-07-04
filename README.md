<div align="center">

```
    ██╗  ██╗ ████████╗ ██╗   ██╗ ███████╗
    ██║ ██╔╝ ██╔═════╝ ╚██╗ ██╔╝ ██╔════╝
    █████╔╝  ██████╗    ╚████╔╝  ███████╗
    ██╔═██╗  ██╔═══╝     ╚██╔╝   ╚════██║
    ██║  ██╗ ████████╗    ██║    ███████║
    ╚═╝  ╚═╝ ╚═══════╝    ╚═╝    ╚══════╝
```

# KEYS — Initial Access Intelligence (IAI)

**Modular reconnaissance and enumeration framework for offensive security workflows.**

Async execution · Service-aware automation · YAML-driven scans · Live TUI

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OS: Linux](https://img.shields.io/badge/OS-Kali%20Linux-informational?logo=linux)](https://www.kali.org/)

</div>

---

## Overview

KEYS is a Python-based reconnaissance orchestration framework built around:

- **YAML-driven scan definitions** — add new tools without touching Python
- **Async concurrent execution** — run multiple scans in parallel
- **Resource locking** — prevent tool conflicts on the same target
- **Scan fingerprinting** — SHA256-based duplicate prevention
- **Live TUI** — real-time monitoring via Textual
- **Service-aware automation** — scans respond to discovered intelligence

### Use Cases

| Scenario | Fit |
|---|---|
| Penetration testing | ✅ |
| HTB / CTF workflows | ✅ |
| Internal security assessments | ✅ |
| Lab environments | ✅ |
| Recon automation research | ✅ |

---

## Features

| Feature | Description |
|---|---|
| Async scan orchestration | Concurrent execution via asyncio workers |
| YAML scan definitions | Config-driven — no hardcoded scan logic |
| Live TUI | Real-time Textual-based terminal interface |
| Resource locking | Prevents conflicting scans on same service |
| Duplicate prevention | SHA256 fingerprinting per scan |
| Queue + scheduler | Concurrency-aware dispatching |
| State tracking | Centralized ports, services, findings |
| Automatic logging | All output saved to `~/Intel/Reports/` |
| Theme engine | 4 built-in themes with live switching |
| Modular tooling | Nmap, FFUF, Gobuster, Nuclei, Hydra & more |

---

## Supported Tools

| Category | Tools |
|---|---|
| **Network** | Nmap, Masscan |
| **Web** | FFUF, Gobuster, Feroxbuster, Nikto, Nuclei, WPScan |
| **SMB** | Enum4Linux, SMBMap, SMBClient, NetExec |
| **Brute Force** | Hydra |
| **SMTP** | smtp-user-enum |
| **SNMP** | snmpwalk |

---

## Architecture

```
                    ┌──────────────────────┐
                    │     Textual TUI      │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │    Worker Manager    │
                    └──────────┬───────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                 │
     ┌────────▼────────┐              ┌─────────▼────────┐
     │    Scheduler    │              │ Resource Locking  │
     └────────┬────────┘              └──────────────────┘
              │
     ┌────────▼────────┐
     │ Execution Context│
     └────────┬────────┘
              │
     ┌────────▼────────┐
     │   Async Workers  │
     └────────┬────────┘
              │
     ┌────────▼────────┐
     │  External Tools  │
     └─────────────────┘
```

<details>
<summary><strong>Execution Pipeline (click to expand)</strong></summary>

1. **Bootstrap Validation** — checks Python version, packages, and system tools before startup
2. **Config Loading** — scans loaded dynamically from `config/scans/` YAML files
3. **Scheduling** — queue ordering, concurrency limits, duplicate prevention
4. **Resource Locking** — key: `(target, service, port, protocol)` — prevents conflicts
5. **Worker Execution** — isolated async workers with live output streaming
6. **State Tracking** — centralized discovery of ports, services, and findings

</details>

<details>
<summary><strong>Concurrency Model (click to expand)</strong></summary>

- `asyncio` + async subprocesses
- Queue-based scheduling
- Resource locks per service
- Batched UI updates
- Cancellable scan workers

</details>

---

## Installation

### Prerequisites

- **Python** 3.10+
- **OS** — Kali Linux (or any Debian-based distro with pentesting tools)

### Quick Start

```bash
git clone https://github.com/aki-seven/Project-KEYS.git
cd Project-KEYS
pip install .
```

### System Tools (Kali/Debian)

```bash
sudo apt install nmap ffuf gobuster feroxbuster hydra
```

Additional tools (manual install):

```bash
# nuclei
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# nikto
sudo apt install nikto

# wpscan
gem install wpscan

# netexec
pip install netexec
```

### Docker

```bash
docker build -t keys .
docker run -it keys <target>
```

---

## Usage

```bash
# Basic usage
keys <target>

# Examples
keys 10.10.10.10
keys example.com
```

### Keybindings

| Key | Action |
|---|---|
| `Ctrl+Q` | Quit |
| `Ctrl+S` | Save scan log |
| `Ctrl+T` | Cycle theme |

---

## Configuration

### Themes

Change theme in `src/keys/config/theme.json`:

```json
{"theme": "ghostwire"}
```

Available themes:

| Theme | Style |
|---|---|
| `ghostwire` | Black + Cyan/Steel |
| `bloodmoon` | Dark + Red |
| `emberstrike` | Dark + Orange |
| `offsec` | Classic offsec green |

### Wordlists

Edit wordlist paths in `src/keys/config/scans/wordlists.yaml` to match your distro.

### Adding New Scans

Create a YAML file in `src/keys/config/scans/`:

```yaml
scans:
  - category: Enumeration
    subcategory: Custom
    group: MyTool

    name: My Custom Scan
    tool: mytool
    services:
      - http

    command: mytool -u {target} -w {wordlist}

    parameters:
      target:
        type: string
        default: ""
      wordlist:
        type: file
        default: "/usr/share/wordlists/common.txt"

    description: Custom scan description
```

The framework auto-loads it at startup — no code changes needed.

---

## Project Structure

```
Keys/
├── src/keys/
│   ├── config/          # YAML scan definitions + theme config
│   │   └── scans/
│   │       ├── network/
│   │       ├── web/
│   │       ├── smb/
│   │       ├── ftp/
│   │       ├── smtp/
│   │       ├── snmp/
│   │       ├── databases/
│   │       └── brute_force/
│   ├── core/            # Bootstrap, config loader, state, parsers, tools
│   ├── execution/       # Scheduler, workers, locks, events, logging
│   ├── tui/             # Textual app, components, modals, themes
│   └── main.py          # Entry point
├── config/              # Project-level config
├── dockerfile
├── pyproject.toml
├── requirements.txt
└── README.md
```

| Directory | Purpose |
|---|---|
| `core/` | Bootstrap validation, config parsing, state management, tool registry |
| `execution/` | Scheduler, workers, queue, locks, contexts, fingerprinting, logging |
| `tui/` | Textual widgets, modals, themes, status bars, event handling |
| `config/scans/` | YAML scan definitions — framework behavior driven from here |

---

## Logging

All scan output is automatically logged:

```
~/Intel/Reports/<target>/<scan-name>/
```

Each execution gets a dedicated log file with full output.

---

## Security Notice

> **This framework is intended for authorized testing, lab environments, research, and education only.**
> Do not use against systems without explicit permission. Unauthorized access is illegal.

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.10+ |
| Async | asyncio |
| TUI | Textual |
| Rich output | Rich |
| Config | YAML + Pydantic |
| Packaging | pyproject.toml (setuptools) |

---

## Author

**aki-seven** — [GitHub](https://github.com/aki-seven)
