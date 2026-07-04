import hashlib

from keys.execution.context import (
    ExecutionContext
)


def build_fingerprint(
    context: ExecutionContext
) -> str:

    raw = "|".join([
        context.target,
        context.service,
        str(context.port),
        context.protocol,
        context.command.strip()
    ])

    return hashlib.sha256(
        raw.encode()
    ).hexdigest()