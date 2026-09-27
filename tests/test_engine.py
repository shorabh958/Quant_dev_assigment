import numpy as np
import pandas as pd

from trading.engine import QuantEngine
from trading.risk import RiskManager
from trading.strategies import (
    GridConfig,
    GridStrategy,
)
from trading.trading_costs import CostModel
from trading.walkforward_engine import (
    run_walk_forward,
)


def make_data(rows=150):

    np.random.seed(7)

    returns = np.random.normal(
        0,
        0.01,
        rows,
    )

    close = (
        100
        * np.exp(
            np.cumsum(returns)
        )
    )

    return pd.DataFrame(
        {
            "open": close,
            "high": close * 1.01,
            "low": close * 0.99,
            "close": close,
            "volume": np.full(
                rows,
                1000,
            ),
        },
        index=pd.date_range(
            "2026-01-01",
            periods=rows,
            freq="5min",
        ),
    )


def make_engine():

    return QuantEngine(
        strategy=GridStrategy(
            GridConfig(
                spacing_atr=0.5,
                max_levels=3,
                pyramid_quantity=1,
            )
        ),
        risk_manager=RiskManager(),
        cost_model=CostModel(),
    )


def test_engine_returns_result():

    result = make_engine().run(
        make_data()
    )

    assert result.initial_capital == 100000
    assert result.final_equity > 0


def test_engine_has_valid_metrics():

    result = make_engine().run(
        make_data()
    )

    assert result.max_drawdown >= 0
    assert result.trades >= 0
    assert result.blocked_orders >= 0


def test_engine_preserves_capital_type():

    result = make_engine().run(
        make_data()
    )

    assert isinstance(
        result.final_equity,
        type(result.initial_capital),
    )


def test_walk_forward_runs():

    results = run_walk_forward(
        make_engine(),
        make_data(200),
        train_size=100,
        test_size=25,
    )

    assert len(results) == 4


def test_walk_forward_has_oos_windows():

    results = run_walk_forward(
        make_engine(),
        make_data(200),
        train_size=100,
        test_size=25,
    )

    for result in results:

        assert result.train_rows == 100
        assert result.test_rows == 25
        assert result.max_drawdown >= 0


def test_engine_rejects_missing_columns():

    data = make_data().drop(
        columns=["volume"]
    )

    try:
        make_engine().run(data)
        assert False
    except ValueError as exc:
        assert "volume" in str(exc)