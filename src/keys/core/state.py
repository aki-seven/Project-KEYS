from dataclasses import dataclass, field
from typing import Set

@dataclass
class Finding:

    type: str
    severity: str
    source: str
    description: str

@dataclass
class IAIState:
    target: str = ""

    # discovered intelligence
    tcp_ports: set[int] = field(default_factory=set)

    udp_ports: set[int] = field(default_factory=set)

    services: dict[str, dict[int, str]] = field(
        default_factory=lambda: {
            "tcp": {},
            "udp": {}
        }
    )

    recommended_services: set[str] = field(
        default_factory=set
    )

    findings: list[Finding] = field(
        default_factory=list
    )
        
    def add_port(
        self,
        protocol: str,
        port: int
    ):

        if protocol == "tcp":
            self.tcp_ports.add(port)

        elif protocol == "udp":
            self.udp_ports.add(port)


    def add_service(
        self,
        protocol: str,
        port: int,
        service: str
    ):

        self.services[protocol][port] = service

    def add_recommended_service(
        self,
        service: str
    ):

        self.recommended_services.add(
            service
        )

    def add_finding(
        self,
        finding: Finding
    ):

        self.findings.append(finding)

global_state = IAIState()
