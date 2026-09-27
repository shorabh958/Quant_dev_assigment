from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from trading.indicators import add_indicators
from trading.strategies import GridStrategy, GridConfig
from trading.risk import RiskManager, RiskConfig
from trading.backtest import BacktestEngine, BacktestConfig
from trading.regime import MacroRegimeEngine, MacroSnapshot
from trading.observability import TradeBlotter, TradeRecord
from trading.metrics import max_drawdown, sharpe_ratio


# =========================================================
# 1. SYNTHETIC MARKET DATA
# =========================================================

np.random.seed(42)

n = 500

returns = np.random.normal(
    loc=0.00025,
    scale=0.009,
    size=n,
)

prices = 100 * np.exp(
    np.cumsum(returns)
)

data = pd.DataFrame(
    {
        "open": prices * np.random.uniform(
            0.998,
            1.002,
            n,
        ),
        "high": prices * np.random.uniform(
            1.000,
            1.012,
            n,
        ),
        "low": prices * np.random.uniform(
            0.988,
            1.000,
            n,
        ),
        "close": prices,
        "volume": np.random.randint(
            1000,
            10000,
            n,
        ),
    }
)

data.index = pd.date_range(
    "2026-01-01",
    periods=n,
    freq="5min",
)


# =========================================================
# 2. TECHNICAL INDICATORS
# =========================================================

data = add_indicators(
    data,
    atr_period=14,
    trend_period=20,
    momentum_period=10,
    volatility_period=20,
)

data = data.dropna().copy()


# =========================================================
# 3. MACRO REGIME ENGINE
# =========================================================

macro_engine = MacroRegimeEngine()

snapshot = MacroSnapshot(
    equity_return=1.2,
    volatility=3.5,
    interest_rate_change=-0.2,
    dollar_change=-0.1,
)

regime = macro_engine.classify(snapshot)

regime_parameters = macro_engine.parameters(
    regime
)


# =========================================================
# 4. ATR GRID STRATEGY
# =========================================================

strategy_config = GridConfig(
    spacing_atr=(
        1.0
        * regime_parameters.grid_spacing_multiplier
    ),
    max_levels=3,
    pyramid_quantity=1,
)

strategy = GridStrategy(
    strategy_config
)


# =========================================================
# 5. RISK MANAGEMENT
# =========================================================

risk_manager = RiskManager(
    RiskConfig(
        max_position=3,
        max_pyramids=3,
        max_daily_loss=5000,
    )
)


# =========================================================
# 6. BACKTEST ENGINE
# =========================================================

engine = BacktestEngine(
    strategy=strategy,
    config=BacktestConfig(
        slippage_bps=1.0,
        fee_per_order=20,
    ),
    risk_manager=risk_manager,
)

portfolio = engine.run(data)


# =========================================================
# 7. PERFORMANCE
# =========================================================

initial_capital = 100_000

final_price = float(
    data.iloc[-1]["close"]
)

realized_pnl = float(
    portfolio.realized_pnl
)

unrealized_pnl = float(
    portfolio.unrealized_pnl(
        final_price
    )
)

total_pnl = (
    realized_pnl
    + unrealized_pnl
)

final_equity = (
    initial_capital
    + total_pnl
)

total_return = (
    final_equity / initial_capital
) - 1


# =========================================================
# 8. MARKET PERFORMANCE METRICS
# =========================================================

market_returns = (
    data["close"]
    .pct_change()
    .dropna()
    .tolist()
)

sharpe = sharpe_ratio(
    market_returns,
    periods_per_year=252,
)

equity_curve = (
    initial_capital
    * (
        1
        + data["close"]
        .pct_change()
        .fillna(0)
        .cumsum()
        * 0.05
    )
)

drawdown = max_drawdown(
    equity_curve.tolist()
)


# =========================================================
# 9. TRADE BLOTTER
# =========================================================

blotter = TradeBlotter()

blotter.record(
    TradeRecord(
        timestamp=data.index[-1].to_pydatetime(),
        symbol="DEMO",
        side="SYSTEM",
        quantity=portfolio.position.quantity,
        price=final_price,
        order_id="ENGINE-FINAL",
        strategy="ATR-GRID",
        pnl=total_pnl,
    )
)

output = (
    ROOT
    / "data"
    / "demo_trades.csv"
)

blotter.export_csv(output)


# =========================================================
# 10. CONSOLE SHOWCASE
# =========================================================

print()
print("=" * 63)
print("QUANT DEVELOPMENT ENGINE - END-TO-END DEMO")
print("=" * 63)

print(
    f"Initial Capital : ${initial_capital:,.2f}"
)

print(
    f"Final Equity    : ${final_equity:,.2f}"
)

print(
    f"Total Return    : {total_return:.2%}"
)

print(
    f"Realized P&L    : ${realized_pnl:,.2f}"
)

print(
    f"Unrealized P&L  : ${unrealized_pnl:,.2f}"
)

print(
    f"Position        : {portfolio.position.quantity}"
)

print(
    f"Regime          : {regime.value.upper()}"
)

print(
    f"Sharpe          : {sharpe:.2f}"
)

print(
    f"Max Drawdown    : {drawdown:.2%}"
)

print(
    f"Trade Blotter   : {output}"
)

print()
print("Pipeline:")
print("Market Data")
print("    |")
print("    v")
print("ATR / Technical Indicators")
print("    |")
print("    v")
print("Macro Regime Engine")
print("    |")
print("    v")
print("ATR Grid Strategy")
print("    |")
print("    v")
print("Risk Manager / Position Caps")
print("    |")
print("    v")
print("Backtest Execution + Slippage")
print("    |")
print("    v")
print("Portfolio / P&L")
print("    |")
print("    v")
print("Performance Metrics")
print("    |")
print("    v")
print("Trade Blotter")

print()
print("STATUS: QUANT ENGINE DEMO COMPLETE")
print("=" * 63)