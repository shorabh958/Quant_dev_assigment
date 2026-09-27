from decimal import Decimal

from trading.risk import (
    RiskConfig,
    RiskManager,
)

from trading.strategies import (
    GridConfig,
    GridStrategy,
    StopAndReverseStrategy,
)

from trading.trading_costs import (
    CostModel,
)

from trading.trade_metrics import (
    trade_count,
    win_rate,
    profit_factor,
    expectancy,
)

from trading.walkforward import (
    generate_windows,
    evaluate_walk_forward,
)

import pandas as pd


def test_risk_position_cap():

    risk = RiskManager(
        RiskConfig(
            max_position=3
        )
    )

    assert (
        risk.allowed_quantity(
            2,
            5,
        )
        == 1
    )


def test_kill_switch():

    risk = RiskManager(
        RiskConfig(
            max_daily_loss=5000
        )
    )

    assert risk.kill_switch(
        -5001
    )

    assert not risk.kill_switch(
        -4999
    )


def test_circuit_breaker():

    risk = RiskManager(
        RiskConfig(
            max_drawdown=0.10,
            max_daily_loss=5000,
            max_volatility=10,
        )
    )

    assert risk.circuit_breaker(
        0.11,
        0,
        2,
    )

    assert risk.circuit_breaker(
        0,
        -6000,
        2,
    )

    assert risk.circuit_breaker(
        0,
        0,
        11,
    )


def test_grid_max_levels():

    strategy = GridStrategy(
        GridConfig(
            max_levels=3,
            pyramid_quantity=1,
        )
    )

    candle = type(
        "Candle",
        (),
        {"close": 90},
    )()

    signal = strategy.generate_signal(
        candle,
        5,
        100,
        3,
    )

    assert signal is None


def test_stop_and_reverse():

    strategy = StopAndReverseStrategy(
        threshold=2
    )

    signal = strategy.generate_signal(
        price=105,
        reference_price=100,
        current_position=-1,
    )

    assert signal is not None
    assert signal.reason == (
        "stop_and_reverse_long"
    )


def test_cost_model():

    costs = CostModel(
        brokerage_per_order=Decimal("20"),
        slippage_bps=Decimal("1"),
    )

    price = Decimal("100")

    execution = costs.execution_price(
        price,
        "BUY",
    )

    assert execution > price

    total = costs.total_cost(
        price,
        10,
    )

    assert total > Decimal("20")


def test_trade_metrics():

    trades = [
        100,
        -50,
        150,
        -25,
    ]

    assert trade_count(trades) == 4

    assert win_rate(trades) == 0.5

    assert profit_factor(
        trades
    ) == 250 / 75

    assert expectancy(
        trades
    ) == 43.75


def test_walk_forward():

    data = pd.DataFrame(
        {
            "close": range(20)
        }
    )

    windows = list(
        generate_windows(
            data,
            train_size=10,
            test_size=5,
        )
    )

    assert len(windows) == 2

    assert len(
        windows[0].train
    ) == 10

    assert len(
        windows[0].test
    ) == 5


def test_walk_forward_evaluation():

    data = pd.DataFrame(
        {
            "close": range(30)
        }
    )

    results = evaluate_walk_forward(
        data,
        train_size=10,
        test_size=5,
    )

    assert len(results) == 4

    assert (
        results[0].train_size
        == 10
    )

    assert (
        results[0].test_size
        == 5
    )