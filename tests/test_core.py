from datetime import datetime
from decimal import Decimal

import pandas as pd

from trading.models import Candle, Fill, Side
from trading.orders import OrderManager, OrderRequest
from trading.portfolio import Portfolio


def test_order_manager_is_idempotent():
    manager = OrderManager()

    order = OrderRequest(
        client_order_id="ABC-1",
        side="BUY",
        quantity=1,
    )

    first = manager.place(order)
    second = manager.place(order)

    assert first is second
    assert len(manager.orders) == 1


def test_long_position_pnl():
    portfolio = Portfolio()

    portfolio.apply_fill(
        Fill(
            order_id="1",
            timestamp=datetime.now(),
            side=Side.BUY,
            quantity=2,
            price=Decimal("100"),
        )
    )

    assert portfolio.position.quantity == 2
    assert portfolio.position.average_price == Decimal("100")

    assert portfolio.unrealized_pnl(
        Decimal("110")
    ) == Decimal("20")


def test_position_close_realizes_pnl():
    portfolio = Portfolio()

    portfolio.apply_fill(
        Fill(
            order_id="1",
            timestamp=datetime.now(),
            side=Side.BUY,
            quantity=1,
            price=Decimal("100"),
        )
    )

    portfolio.apply_fill(
        Fill(
            order_id="2",
            timestamp=datetime.now(),
            side=Side.SELL,
            quantity=1,
            price=Decimal("110"),
        )
    )

    assert portfolio.position.is_flat
    assert portfolio.realized_pnl == Decimal("10")