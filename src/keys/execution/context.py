from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import time


class ScanState(str, Enum):

    QUEUED = "queued"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"


ResourceKey = tuple[
    str,  # target
    str,  # service
    int,  # port
    str   # protocol
]


@dataclass(slots=True)
class ExecutionContext:

    scan_id: str
    name: str
    category: str
    command: str
    target: str
    service: str
    port: int
    protocol: str
    parameters: dict[str, Any] = field(
        default_factory=dict
    )

    resource_key: ResourceKey = field(
        init=False
    )

    fingerprint: str = ""
    state: ScanState = ScanState.QUEUED

    created_at: float = field(
        default_factory=time.time
    )

    started_at: float | None = None
    completed_at: float | None = None
    queued_reason: str = ""

    def __post_init__(self):

        self.resource_key = (
            self.target,
            self.service,
            self.port,
            self.protocol
        )