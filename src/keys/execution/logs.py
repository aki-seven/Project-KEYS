from pathlib import Path

from keys.execution.context import (
    ExecutionContext
)


class ScanLogger:

    def __init__(
        self,
        context: ExecutionContext
    ):

        self.context = context

        safe_tool = (
            context.name
            .lower()
            .replace(" ", "-")
            .replace("/", "-")
        )

        self.log_dir = (
            Path.home()
            / "Intel"
            / "Reports"
            / context.target
            / safe_tool
        )

        self.log_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.log_path = (
            self.log_dir
            / f"{context.scan_id}.log"
        )

    def write_line(
        self,
        line: str
    ):

        with open(
            self.log_path,
            "a",
            encoding="utf-8"
        ) as logfile:

            logfile.write(
                line + "\n"
            )