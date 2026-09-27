from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(
    0,
    str(ROOT / "src"),
)

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


np.random.seed(42)

rows = 500

returns = np.random.normal(
    0.0002,
    0.009,
    rows,
)

close = (
    100
    * np.exp(
        np.cumsum(returns)
    )
)

data = pd.DataFrame(
    {
        "open": close,
        "high": close * np.random.uniform(
            1.001,
            1.012,
            rows,
        ),
        "low": close * np.random.uniform(
            0.988,
            0.999,
            rows,
        ),
        "close": close,
        "volume": np.random.randint(
            1000,
            10000,
            rows,
        ),
    },
    index=pd.date_range(
        "2026-01-01",
        periods=rows,
        freq="5min",
    ),
)


engine = QuantEngine(
    strategy=GridStrategy(
        GridConfig(
            spacing_atr=0.75,
            max_levels=3,
            pyramid_quantity=1,
        )
    ),
    risk_manager=RiskManager(),
    cost_model=CostModel(),
)


result = engine.run(data)

walk_forward = run_walk_forward(
    engine,
    data,
    train_size=300,
    test_size=50,
)


print()
print("=" * 65)
print("QUANT DEVELOPMENT ENGINE - BATCH A")
print("=" * 65)

print(
    f"Initial Capital : "
    f"${result.initial_capital:,.2f}"
)

print(
    f"Final Equity    : "
    f"${result.final_equity:,.2f}"
)

print(
    f"Total Return    : "
    f"{result.total_return:.2%}"
)

print(
    f"Realized P&L    : "
    f"${result.realized_pnl:,.2f}"
)

print(
    f"Unrealized P&L  : "
    f"${result.unrealized_pnl:,.2f}"
)

print(
    f"Trades          : "
    f"{result.trades}"
)

print(
    f"Blocked Orders  : "
    f"{result.blocked_orders}"
)

print(
    f"Max Drawdown    : "
    f"{result.max_drawdown:.2%}"
)

print(
    f"Sharpe          : "
    f"{result.sharpe:.2f}"
)

print()
print(
    f"Walk-Forward Windows : "
    f"{len(walk_forward)}"
)

for window in walk_forward:

    print(
        f"  W{window.window}: "
        f"return={window.return_pct:.2%}, "
        f"DD={window.max_drawdown:.2%}, "
        f"trades={window.trades}"
    )

print()
print("Pipeline:")
print("Market Data")
print("  -> Indicators")
print("  -> Macro / Regime")
print("  -> Strategy")
print("  -> Risk")
print("  -> Cost Model")
print("  -> Portfolio")
print("  -> Metrics")
print("  -> Walk-Forward")

print()
print("STATUS: BATCH A COMPLETE")
print("=" * 65)