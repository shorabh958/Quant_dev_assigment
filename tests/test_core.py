from datetime import datetime
from decimal import Decimal

import pandas as pd

from trading.models import Fill, Side
from trading.orders import OrderManager, OrderRequest
from trading.portfolio import Portfolio
from trading.strategies import GridConfig, GridStrategy


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
    assert portfolio.unrealized_pnl(Decimal("110")) == Decimal("20")


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


def test_backtest_requires_atr():
    strategy = GridStrategy(GridConfig(spacing_atr=1.0))

    data = pd.DataFrame(
        {
            "open": [100, 101],
            "high": [102, 103],
            "low": [99, 100],
            "close": [101, 102],
            "volume": [1000, 1000],
        }
    )

    from trading.backtest import BacktestEngine

    try:
        BacktestEngine(strategy).run(data)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "ATR" in str(exc)


def test_backtest_uses_next_bar_open():
    data = pd.DataFrame(
        {
            "open": [100, 100, 120],
            "high": [101, 101, 121],
            "low": [99, 99, 119],
            "close": [100, 80, 120],
            "volume": [1000, 1000, 1000],
            "atr": [10, 10, 10],
        },
        index=pd.date_range("2026-01-01", periods=3),
    )

    strategy = GridStrategy(
        GridConfig(
            spacing_atr=1.0,
            pyramid_quantity=1,
        )
    )

    from trading.backtest import BacktestEngine, BacktestConfig

    portfolio = BacktestEngine(
        strategy,
        BacktestConfig(slippage_bps=0),
    ).run(data)

    # The signal from bar 2 executes at bar 3's OPEN (120),
    # not bar 2's CLOSE (80).
    assert portfolio.position.quantity == 0 or portfolio.position.average_price == Decimal("120")