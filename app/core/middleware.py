import re
import time
import uuid

import structlog
from starlette.types import ASGIApp, Message, Receive, Scope, Send

log = structlog.get_logger()
_VALID_ID = re.compile(r'^[A-Za-z0-9_-]{8,64}$')


def _inbound_request_id(scope: Scope) -> str | None:
    for name, value in scope['headers']:
        if name == b'x-request-id':
            candidate = value.decode('latin-1')
            # Accept only well-formed IDs: stops log injection through crafted headers.
            return candidate if _VALID_ID.match(candidate) else None
    return None


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return
        request_id = _inbound_request_id(scope) or uuid.uuid4().hex
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        status = 500
        start = time.perf_counter()

        async def send_wrapper(message: Message) -> None:
            nonlocal status
            if message['type'] == 'http.response.start':
                status = message['status']
                headers = list(message.get('headers', []))
                headers.append((b'x-request-id', request_id.encode()))
                message['headers'] = headers
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            log.info(
                'request',
                method=scope['method'],
                path=scope['path'],
                status=status,
                duration_ms=round((time.perf_counter() - start) * 1000, 2),
            )