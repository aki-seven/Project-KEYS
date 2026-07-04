import asyncio

from textual.app import App

from keys.execution.context import (
    ExecutionContext
)

from keys.execution.events import (
    ScanOutputBatch
)
from keys.execution.events import (
    ScanOutput
)

from keys.execution.logs import (
    ScanLogger
)

# Todo check commented code. IMPORTANT
import os
import signal

class Worker:

    def __init__(
        self,
        context: ExecutionContext,
        app: App
    ):

        self.context = context

        self.app = app

        self.process: (
            asyncio.subprocess.Process
            | None
        ) = None

        self.output_buffer: list[str] = []

        self.last_flush = (
            asyncio.get_event_loop().time()
        )

        self.logger = ScanLogger(
            context
        )


    async def run(self) -> bool:

        success = False

        try:

            self.process = (
                await asyncio.create_subprocess_shell(
                    self.context.command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT,
                    start_new_session=True
                )
            )

            while True:

                if self.process.stdout is None:
                    break

                try:

                    line = await asyncio.wait_for(
                        self.process.stdout.readline(),
                        timeout=0.5
                    )

                except asyncio.TimeoutError:

                    # if (
                    #     self.process.returncode
                    #     is not None
                    # ):
                    #     break

                    continue

                if not line:
                    break

                decoded_line = (
                    line.decode(
                        "utf-8",
                        errors="replace"
                    ).rstrip()
                )
                
                self.logger.write_line(
                    decoded_line
                )

                self.output_buffer.append(
                    decoded_line
                )

                now = (
                    asyncio.get_event_loop().time()
                )

                if (
                    len(self.output_buffer) >= 50
                    or
                    now - self.last_flush >= 0.2
                ):

                    self.app.post_message(
                        ScanOutputBatch(
                            self.context.scan_id,
                            self.output_buffer.copy()
                        )
                    )

                    self.output_buffer.clear()

                    self.last_flush = now

                # if (
                #     self.process.returncode
                #     is not None
                # ):
                #     break

            try:

                await asyncio.wait_for(
                    self.process.wait(),
                    timeout=3
                )

            except asyncio.TimeoutError:
                pass

            if self.output_buffer:

                self.app.post_message(
                    ScanOutputBatch(
                        self.context.scan_id,
                        self.output_buffer.copy()
                    )
                )

                self.output_buffer.clear()

            success = (
                self.process.returncode == 0
            )

        except asyncio.CancelledError:

            if self.process:

                # self.process.kill()
                
                os.killpg(
                    os.getpgid(
                        self.process.pid
                    ),
                    signal.SIGTERM
                )

                try:

                    await asyncio.wait_for(
                        self.process.wait(),
                        timeout=3
                    )

                except asyncio.TimeoutError:

                    try:

                        os.killpg(
                            os.getpgid(
                                self.process.pid
                            ),
                            signal.SIGKILL
                        )

                    except Exception:
                        pass

            raise

        except Exception as e:

            self.logger.write_line(
                f"ERROR: {str(e)}"
            )

            self.app.post_message(
                ScanOutput(
                    self.context.scan_id,
                    f"ERROR: {str(e)}"
                )
            )

        return success