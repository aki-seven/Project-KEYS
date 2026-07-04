import re

PORT_REGEX = re.compile(
    r"(\d+)\/(tcp|udp)\s+open\s+([^\s]+)"
)

def extract_ports(line: str):

    match = PORT_REGEX.search(line)

    if not match:
        return None

    port = int(match.group(1))

    protocol = match.group(2)

    service = match.group(3) or "unknown"

    return (
        port,
        protocol,
        service
    )