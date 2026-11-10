import asyncio

from main import RequestIDMiddleware
from utils.logging_config import request_id_context


def test_request_id_middleware_resets_context_after_request():
    observed_request_ids = []
    response_messages = []

    async def mock_app(scope, receive, send):
        observed_request_ids.append(request_id_context.get())

        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [],
        })

        await send({
            "type": "http.response.body",
            "body": b"OK",
        })

    async def receive():
        return {
            "type": "http.request",
            "body": b"",
            "more_body": False,
        }

    async def send(message):
        response_messages.append(message)

    middleware = RequestIDMiddleware(mock_app)

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/test",
        "headers": [],
    }

    initial_request_id = request_id_context.get()

    async def run_request():
        await middleware(scope, receive, send)

    asyncio.run(run_request())

    # Middleware generated a request ID.
    assert observed_request_ids[0] != "-"

    # Response contains the same request ID.
    response_headers = dict(response_messages[0]["headers"])

    assert (
        response_headers[b"x-request-id"].decode()
        == observed_request_ids[0]
    )

    # Previous context was restored after the request.
    assert request_id_context.get() == initial_request_id