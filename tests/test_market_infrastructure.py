import asyncio

import httpx

from trading.broker_adapter import (
    BrokerCredentials,
    RESTBrokerClient,
)
from trading.execution_service import (
    OrderExecutionService,
)
from trading.kite_adapter import KiteBrokerAdapter
from trading.live_engine import (
    LiveSignal,
    LiveTradingEngine,
)
from trading.market_data import (
    MarketTick,
    ResilientTickFeed,
    SimulatedTickFeed,
)
from trading.reconciliation import (
    ReconciliationEngine,
)
from trading.risk import RiskManager


def test_reconciliation_clean():

    engine = ReconciliationEngine()

    result = engine.reconcile(
        {"A": "FILLED"},
        {"A": "FILLED"},
        {"NIFTY": 2},
        {"NIFTY": 2},
    )

    assert result.clean
    assert result.order_mismatches == 0
    assert result.position_mismatches == 0


def test_reconciliation_detects_position_mismatch():

    engine = ReconciliationEngine()

    result = engine.reconcile(
        {},
        {},
        {"NIFTY": 2},
        {"NIFTY": 1},
    )

    assert not result.clean
    assert result.position_mismatches == 1


def test_simulated_tick_feed():

    ticks = [
        MarketTick(
            "NIFTY",
            "NSE",
            25000,
            1,
            1.0,
        ),
        MarketTick(
            "NIFTY",
            "NSE",
            25001,
            2,
            2.0,
        ),
    ]

    async def collect():

        result = []

        async for tick in (
            SimulatedTickFeed(ticks).stream()
        ):
            result.append(tick)

        return result

    result = asyncio.run(collect())

    assert len(result) == 2
    assert result[0].symbol == "NIFTY"


def test_resilient_tick_feed():

    calls = {"count": 0}

    async def source():

        calls["count"] += 1

        if calls["count"] == 1:
            raise RuntimeError("disconnect")

        yield MarketTick(
            "NIFTY",
            "NSE",
            25000,
            1,
            1.0,
        )

    async def collect():

        result = []

        async for tick in (
            ResilientTickFeed(
                source,
                max_reconnects=3,
            ).stream()
        ):
            result.append(tick)

        return result

    result = asyncio.run(collect())

    assert len(result) == 1
    assert calls["count"] >= 2


def test_kite_adapter_delegates():

    def handler(request):

        return httpx.Response(
            200,
            json={
                "status": "FILLED",
                "filled_quantity": 1,
            },
        )

    transport = httpx.MockTransport(handler)

    client = RESTBrokerClient(
        "https://broker.test",
        BrokerCredentials(
            "API",
            "TOKEN",
        ),
        transport=transport,
    )

    adapter = KiteBrokerAdapter(client)

    result = adapter.place_order(
        client_order_id="TEST-001",
        symbol="NIFTY",
        side="BUY",
        quantity=1,
        price=25000,
    )

    assert result["status"] == "FILLED"

    adapter.close()


def test_live_engine_respects_risk():

    def handler(request):

        return httpx.Response(
            200,
            json={
                "status": "FILLED",
                "filled_quantity": 1,
            },
        )

    transport = httpx.MockTransport(handler)

    client = RESTBrokerClient(
        "https://broker.test",
        BrokerCredentials(
            "API",
            "TOKEN",
        ),
        transport=transport,
    )

    service = OrderExecutionService(client)

    engine = LiveTradingEngine(
        service,
        RiskManager(),
    )

    result = engine.execute(
        LiveSignal(
            symbol="NIFTY",
            side="BUY",
            quantity=1,
            price=25000,
            client_order_id="LIVE-001",
        ),
        current_position=0,
    )

    assert result.state.value == "FILLED"

    client.close()


def test_live_engine_blocks_after_limit():

    def handler(request):

        return httpx.Response(
            200,
            json={
                "status": "FILLED",
                "filled_quantity": 1,
            },
        )

    transport = httpx.MockTransport(handler)

    client = RESTBrokerClient(
        "https://broker.test",
        BrokerCredentials(
            "API",
            "TOKEN",
        ),
        transport=transport,
    )

    service = OrderExecutionService(client)

    engine = LiveTradingEngine(
        service,
        RiskManager(),
    )

    result = engine.execute(
        LiveSignal(
            symbol="NIFTY",
            side="BUY",
            quantity=1,
            price=25000,
            client_order_id="LIVE-BLOCKED",
        ),
        current_position=3,
    )

    assert result is None

    client.close()