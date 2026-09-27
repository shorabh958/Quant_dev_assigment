import asyncio

from trading.broker import (
    BrokerOrder,
    OrderStatus,
    SimulatedBroker,
    Tick,
    TickStream,
)


def test_order_is_idempotent():
    broker = SimulatedBroker()

    order = BrokerOrder(
        client_order_id="ORDER-001",
        symbol="NIFTY",
        side="BUY",
        quantity=1,
        price=25000,
    )

    first = broker.place_order(order)
    second = broker.place_order(order)

    assert first is second
    assert len(broker.orders) == 1
    assert broker.get_position("NIFTY") == 1


def test_sell_updates_position():
    broker = SimulatedBroker()

    broker.place_order(
        BrokerOrder("B1", "NIFTY", "BUY", 2, 25000)
    )
    broker.place_order(
        BrokerOrder("S1", "NIFTY", "SELL", 1, 25100)
    )

    assert broker.get_position("NIFTY") == 1


def test_reconciliation():
    broker = SimulatedBroker()

    broker.place_order(
        BrokerOrder("B1", "BANKNIFTY", "BUY", 1, 50000)
    )

    state = broker.reconcile()

    assert "B1" in state["orders"]
    assert state["positions"]["BANKNIFTY"] == 1


def test_tick_stream():
    async def run():
        stream = TickStream()

        await stream.publish(
            Tick("NIFTY", 25000, 1.0)
        )

        tick = await stream.consume()

        assert tick.symbol == "NIFTY"
        assert tick.price == 25000

    asyncio.run(run())