from textual.message import Message

from keys.execution.context import (
    ExecutionContext
)


class ScanQueued(Message):

    def __init__(
        self,
        context: ExecutionContext
    ):
        self.context = context
        super().__init__()


class ScanStarted(Message):

    def __init__(
        self,
        context: ExecutionContext
    ):
        self.context = context
        super().__init__()

class ScanOutputBatch(Message):

    def __init__(
        self,
        scan_id: str,
        lines: list[str]
    ):

        self.scan_id = scan_id

        self.lines = lines

        super().__init__()

class ScanOutput(Message):

    def __init__(
        self,
        scan_id: str,
        line: str
    ):
        self.scan_id = scan_id
        self.line = line
        super().__init__()


class ScanCompleted(Message):

    def __init__(
        self,
        context: ExecutionContext,
        success: bool
    ):
        self.context = context
        self.success = success
        super().__init__()

class ScanWaiting(Message):

    def __init__(
        self,
        context: ExecutionContext,
        position: int
    ):

        self.context = context
        self.position = position

        super().__init__()

class QueueUpdated(Message):

    def __init__(
        self,
        queue: list[tuple[str, int]]
    ):

        self.queue = queue

        super().__init__()

class ScanDispatched(Message):

    def __init__(
        self,
        context: ExecutionContext
    ):

        self.context = context

        super().__init__()