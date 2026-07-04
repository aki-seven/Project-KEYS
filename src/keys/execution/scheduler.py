import asyncio

from collections import deque

from keys.execution.context import (
    ExecutionContext
)

from keys.execution.locks import (
    ResourceLockManager
)

from keys.execution.fingerprint import (
    build_fingerprint
)


class Scheduler:

    def __init__(
        self,
        lock_manager: ResourceLockManager,
        max_concurrent: int
    ):

        self.lock_manager = (
            lock_manager
        )

        self.max_concurrent = (
            max_concurrent
        )

        self.pending: deque[
            ExecutionContext
        ] = deque()

        self.active_count = 0

        self.active_fingerprints: set[
            str
        ] = set()

        self.pending_fingerprints: set[
            str
        ] = set()

        self.dispatch_queue: asyncio.Queue[
            ExecutionContext
        ] = asyncio.Queue()

    def get_pending_position(
        self,
        context: ExecutionContext
    ) -> int:

        try:
            return (
                list(self.pending)
                .index(context)
                + 1
            )

        except ValueError:
            return -1

    def build_queue_snapshot(
        self
    ) -> list[tuple[str, int]]:

        snapshot = []

        for index, context in enumerate(
            self.pending,
            start=1
        ):

            snapshot.append(
                (
                    context.scan_id,
                    index
                )
            )

        return snapshot

    async def submit(
        self,
        context: ExecutionContext
    ) -> tuple[bool, bool]:

        context.fingerprint = (
            build_fingerprint(context)
        )

        if (
            context.fingerprint
            in self.active_fingerprints
            or
            context.fingerprint
            in self.pending_fingerprints
        ):

            return (False, False)

        self.pending.append(context)

        self.pending_fingerprints.add(
            context.fingerprint
        )

        before_pending = len(
            self.pending
        )

        await self.schedule()

        after_pending = len(
            self.pending
        )

        immediately_dispatched = (
            after_pending < before_pending
        )

        return (
            True,
            immediately_dispatched
        )

    async def schedule(self):

        if not self.pending:
            return

        while (
            self.active_count
            < self.max_concurrent
        ):

            dispatchable = None

            pending_snapshot = list(
                self.pending
            )

            for context in pending_snapshot:

                if self.lock_manager.is_locked(
                    context.resource_key
                ):
                    continue

                dispatchable = context

                break

            if dispatchable is None:
                return

            acquired = self.lock_manager.acquire(
                dispatchable.resource_key
            )

            if not acquired:
                continue

            self.pending.remove(
                dispatchable
            )

            self.pending_fingerprints.discard(
                dispatchable.fingerprint
            )

            self.active_fingerprints.add(
                dispatchable.fingerprint
            )

            self.active_count += 1

            await self.dispatch_queue.put(
                dispatchable
            )

    async def cancel(
        self,
        scan_id: str
    ) -> ExecutionContext | None:

        for context in list(self.pending):

            if context.scan_id != scan_id:
                continue

            self.pending.remove(context)

            self.pending_fingerprints.discard(
                context.fingerprint
            )

            return context

        return None

    async def complete(
        self,
        context: ExecutionContext
    ):
        
        self.active_count = max(
            0,
            self.active_count - 1
        )

        self.active_fingerprints.discard(
            context.fingerprint
        )

        await self.schedule()