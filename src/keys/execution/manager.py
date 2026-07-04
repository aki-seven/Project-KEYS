import asyncio

from textual.app import App

from keys.execution.worker import Worker
from keys.execution.context import (ExecutionContext, ScanState)
from keys.execution.locks import (ResourceLockManager)
from keys.execution.scheduler import (Scheduler)
from keys.execution.events import (
    ScanQueued,
    ScanWaiting,
    QueueUpdated,
    ScanDispatched,
    ScanStarted,
    ScanCompleted
)


class WorkerManager:

    def __init__(
        self,
        app: App,
        max_concurrent: int = 5
    ):

        self.app = app


        self.tasks: dict[
            str,
            asyncio.Task
        ] = {}

        self.processes: dict[
            str,
            asyncio.subprocess.Process
        ] = {}

        self._running = False


        self.lock_manager = (
            ResourceLockManager()
        )

        self.scheduler = Scheduler(
            lock_manager=self.lock_manager,
            max_concurrent=max_concurrent
        )


    async def start(self):

        self._running = True

        self.queue_task = asyncio.create_task(
            self._process_queue()
        )

    def stop(self):

        self._running = False

        if (
            self.queue_task
            and
            not self.queue_task.done()
        ):
            self.queue_task.cancel()

        for task in self.tasks.values():

            if not task.done():
                task.cancel()

        for process in self.processes.values():

            try:
                process.kill()

            except ProcessLookupError:
                pass

    def _broadcast_queue_update(
        self
    ):

        self.app.post_message(
            QueueUpdated(
                self.scheduler.build_queue_snapshot()
            )
        )

    async def _process_queue(self):

        while self._running:

            context = None

            try:

                context = await self.scheduler.dispatch_queue.get()

                self.app.post_message(
                    ScanDispatched(context)
                )

                task = asyncio.create_task(
                    self._run_worker(context)
                )

                self.tasks[
                    context.scan_id
                ] = task

                task.add_done_callback(
                    lambda _,
                    scan_id=context.scan_id:
                    self.tasks.pop(
                        scan_id,
                        None
                    )
                )

            except asyncio.CancelledError:
                raise

            except Exception as e:

                self.app.notify(
                    f"Queue Error: {str(e)}",
                    severity="error"
                )

            finally:

                if context is not None:

                    self.scheduler.dispatch_queue.task_done()

    async def _run_worker(
        self,
        context: ExecutionContext
    ):

        try:

            context.state = (
                ScanState.RUNNING
            )

            self.app.post_message(
                ScanStarted(context)
            )

            worker = Worker(
                context,
                self.app
            )

            worker_task = (
                asyncio.create_task(
                    worker.run()
                )
            )

            for _ in range(100):

                if worker.process is not None:
                    break

                if worker_task.done():

                    await worker_task

                    raise RuntimeError(
                        "Worker failed before "
                        "process initialization"
                    )

                await asyncio.sleep(0.05)

            else:

                raise RuntimeError(
                    "Worker process "
                    "initialization timeout"
                )

            self.processes[
                context.scan_id
            ] = worker.process

            await worker_task

            context.state = (
                ScanState.COMPLETED
            )

            self.app.post_message(
                ScanCompleted(
                    context,
                    success=True
                )
            )

        except asyncio.CancelledError:

            context.state = (
                ScanState.CANCELLED
            )

            self.app.post_message(
                ScanCompleted(
                    context,
                    success=False
                )
            )

            raise

        except Exception:

            context.state = (
                ScanState.FAILED
            )

            self.app.post_message(
                ScanCompleted(
                    context,
                    success=False
                )
            )

            raise

        finally:

            context.queued_reason = ""

            self.lock_manager.release(
                context.resource_key
            )

            await self.scheduler.complete(
                context
            )

            self._broadcast_queue_update()

            self.processes.pop(
                context.scan_id,
                None
            )

    async def stop_scan(
        self,
        scan_id: str
    ):

        queued_context = await (
            self.scheduler.cancel(scan_id)
        )

        if queued_context:

            queued_context.state = (
                ScanState.CANCELLED
            )

            self._broadcast_queue_update()

            self.app.post_message(
                ScanCompleted(
                    queued_context,
                    success=False
                )
            )

            self.app.notify(
                f"Cancelled queued scan "
                f"{scan_id}"
            )

            return

        process = self.processes.get(
            scan_id
        )

        if process:

            process.kill()

            try:

                await asyncio.wait_for(
                    process.wait(),
                    timeout=3
                )

            except asyncio.TimeoutError:
                pass

        task = self.tasks.get(scan_id)

        if task and not task.done():

            task.cancel()

            try:
                await task

            except asyncio.CancelledError:
                pass

        self.processes.pop(
            scan_id,
            None
        )

        self.tasks.pop(
            scan_id,
            None
        )

    async def submit(
        self,
        context: ExecutionContext
    ):

        accepted, dispatched = (
            await self.scheduler.submit(
                context
            )
        )

        self._broadcast_queue_update()

        if not accepted:

            self.app.notify(
                "Scan already active "
                "or queued",
                severity="warning"
            )

            return

        position = (
            self.scheduler
            .get_pending_position(context)
        )

        if not dispatched:

            context.queued_reason = (
                "Waiting for scheduler slot"
            )

            self.app.post_message(
                ScanWaiting(
                    context,
                    position
                )
            )

        else:

            self.app.post_message(
                ScanQueued(context)
            )