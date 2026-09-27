import asyncio

import httpx
import pytest

from trading.broker import (
    ResilientTickStream,
    Tick,
)
from trading.broker_adapter import (
    BrokerCredentials,
    RESTBrokerClient,
    RetryPolicy,
)
from trading.execution import OrderState
from trading.execution_service import (
    ExecutionRequest,
    OrderExecutionService,
)


def test_rest_broker_auth_and_order():

    received = {}

    def handler(request):

        received["authorization"] = request.headers[
            "Authorization"
        ]

        received["idempotency"] = request.headers[
            "X-Idempotency-Key"
        ]

        return httpx.Response(
            200,
            json={
                "order_id": "ORD-1",
                "status": "FILLED",
                "filled_quantity": 2,
            },
        )

    transport = httpx.MockTransport(handler)

    client = RESTBrokerClient(
        "https://broker.test",
        BrokerCredentials(
            api_key="demo-key",
            access_token="demo-token",
        ),
        transport=transport,
    )

    response = client.place_order(
        client_order_id="CLIENT-1",
        symbol="NIFTY",
        side="BUY",
        quantity=2,
        price=100.0,
    )

    assert response["status"] == "FILLED"

    assert (
        received["authorization"]
        == "token demo-key:demo-token"
    )

    assert (
        received["idempotency"]
        == "CLIENT-1"
    )

    client.close()


def test_execution_service_is_idempotent():

    calls = []

    def handler(request):

        calls.append(request)

        return httpx.Response(
            200,
            json={
                "order_id": "ORD-1",
                "status": "FILLED",
                "filled_quantity": 1,
            },
        )

    client = RESTBrokerClient(
        "https://broker.test",
        BrokerCredentials(
            api_key="key",
            access_token="token",
        ),
        transport=httpx.MockTransport(handler),
    )

    service = OrderExecutionService(client)

    request = ExecutionRequest(
        client_order_id="CLIENT-100",
        symbol="NIFTY",
        side="BUY",
        quantity=1,
        price=100,
    )

    first = service.submit(request)
    second = service.submit(request)

    assert first is second
    assert first.state == OrderState.FILLED

    # Broker receives exactly one request.
    assert len(calls) == 1

    client.close()


def test_execution_service_updates_state():

    def handler(request):

        return httpx.Response(
            200,
            json={
                "order_id": "ORD-2",
                "status": "FILLED",
                "filled_quantity": 3,
            },
        )

    client = RESTBrokerClient(
        "https://broker.test",
        BrokerCredentials(
            api_key="key",
            access_token="token",
        ),
        transport=httpx.MockTransport(handler),
    )

    service = OrderExecutionService(client)

    order = service.submit(
        ExecutionRequest(
            client_order_id="CLIENT-200",
            symbol="BANKNIFTY",
            side="SELL",
            quantity=3,
            price=200,
        )
    )

    assert order.state == OrderState.FILLED
    assert order.filled_quantity == 3

    client.close()


def test_rest_retry_on_server_error():

    attempts = []

    def handler(request):

        attempts.append(1)

        if len(attempts) < 3:
            return httpx.Response(
                500,
                json={"error": "temporary"},
            )

        return httpx.Response(
            200,
            json={
                "status": "FILLED",
                "filled_quantity": 1,
            },
        )

    client = RESTBrokerClient(
        "https://broker.test",
        BrokerCredentials(
            api_key="key",
            access_token="token",
        ),
        retry_policy=RetryPolicy(
            max_attempts=3,
            backoff_seconds=0,
        ),
        transport=httpx.MockTransport(handler),
    )

    response = client.place_order(
        client_order_id="RETRY-1",
        symbol="NIFTY",
        side="BUY",
        quantity=1,
        price=100,
    )

    assert response["status"] == "FILLED"
    assert len(attempts) == 3

    client.close()


def test_tick_stream_consumes_ticks():

    async def source():

        yield Tick(
            symbol="NIFTY",
            price=100,
            timestamp=1,
        )

        yield Tick(
            symbol="NIFTY",
            price=101,
            timestamp=2,
        )

    stream = ResilientTickStream(
        lambda: source(),
        reconnect_attempts=2,
    )

    async def collect():

        result = []

        async for tick in stream.stream():

            result.append(tick)

            if len(result) == 2:
                break

        return result

    ticks = asyncio.run(
        collect()
    )

    assert len(ticks) == 2
    assert ticks[0].price == 100
    assert ticks[1].price == 101


def test_tick_stream_reconnects():

    calls = []

    async def source():

        calls.append(1)

        if len(calls) == 1:
            raise ConnectionError(
                "connection dropped"
            )

        yield Tick(
            symbol="NIFTY",
            price=105,
            timestamp=10,
        )

    stream = ResilientTickStream(
        lambda: source(),
        reconnect_attempts=3,
    )

    async def collect():

        async for tick in stream.stream():
            return tick

    tick = asyncio.run(
        collect()
    )

    assert tick.price == 105
    assert len(calls) == 2