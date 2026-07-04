FROM kalilinux/kali-rolling

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nmap \
    masscan \
    gobuster \
    ffuf \
    hydra \
    smbclient \
    enum4linux \
    nbtscan \
    snmp \
    && apt clean

WORKDIR /app

COPY requirements.txt .
COPY pyproject.toml .

# Create isolated Python environment
RUN python3 -m venv /opt/venv

# Use the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip inside venv
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install -r requirements.txt

COPY . .

# Install Keys package
RUN pip install .

ENTRYPOINT ["keys"]