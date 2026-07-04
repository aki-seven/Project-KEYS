from keys.execution.context import (
    ResourceKey
)


class ResourceLockManager:

    def __init__(self):

        self.active_resources: set[
            ResourceKey
        ] = set()

    def acquire(
        self,
        resource_key: ResourceKey
    ) -> bool:

        if resource_key in self.active_resources:
            return False

        self.active_resources.add(
            resource_key
        )

        return True

    def release(
        self,
        resource_key: ResourceKey
    ):

        self.active_resources.discard(
            resource_key
        )

    def is_locked(
        self,
        resource_key: ResourceKey
    ) -> bool:

        return (
            resource_key
            in self.active_resources
        )