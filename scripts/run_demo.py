from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# -----------------------------
# 1. Generate synthetic market data
# -----------------------------
np.random.seed(42)

n = 250
returns = np.random.normal(0.0004, 0.012, n)
prices = 100 * np.exp(np.cumsum(returns))

data = pd.DataFrame({
    "close": prices
})

# -----------------------------
# 2. Strategy: SMA crossover
# -----------------------------
data["sma_fast"] = data["close"].rolling(10).mean()
data["sma_slow"] = data["close"].rolling(30).mean()

data["signal"] = 0
data.loc[data["sma_fast"] > data["sma_slow"], "signal"] = 1
data.loc[data["sma_fast"] < data["sma_slow"], "signal"] = -1

# -----------------------------
# 3. Risk + portfolio simulation
# -----------------------------
initial_capital = 100_000
capital = initial_capital
position = 0
entry_price = 0
trades = []

for i in range(30, len(data)):
    price = data.loc[i, "close"]
    signal = data.loc[i, "signal"]

    # Risk rule: max 20% capital per position
    allocation = capital * 0.20
    quantity = int(allocation / price)

    # BUY
    if signal == 1 and position == 0 and quantity > 0:
        position = quantity
        entry_price = price

        trades.append({
            "bar": i,
            "side": "BUY",
            "price": price,
            "quantity": quantity
        })

    # SELL
    elif signal == -1 and position > 0:
        pnl = (price - entry_price) * position
        capital += pnl

        trades.append({
            "bar": i,
            "side": "SELL",
            "price": price,
            "quantity": position,
            "pnl": pnl
        })

        position = 0

# Close remaining position
if position > 0:
    price = data.iloc[-1]["close"]
    pnl = (price - entry_price) * position
    capital += pnl

    trades.append({
        "bar": len(data) - 1,
        "side": "SELL",
        "price": price,
        "quantity": position,
        "pnl": pnl
    })

# -----------------------------
# 4. Performance metrics
# -----------------------------
trade_df = pd.DataFrame(trades)

if "pnl" in trade_df:
    pnl = trade_df["pnl"].dropna()
else:
    pnl = pd.Series(dtype=float)

total_return = (capital / initial_capital) - 1
wins = (pnl > 0).sum()
losses = (pnl < 0).sum()

win_rate = wins / len(pnl) if len(pnl) else 0

equity = [initial_capital]

for value in pnl:
    equity.append(equity[-1] + value)

equity = pd.Series(equity)

drawdown = equity / equity.cummax() - 1
max_drawdown = drawdown.min()

# -----------------------------
# 5. Export report
# -----------------------------
output = ROOT / "data" / "demo_trades.csv"
output.parent.mkdir(exist_ok=True)

trade_df.to_csv(output, index=False)

# -----------------------------
# 6. Demo output
# -----------------------------
print("\n" + "=" * 55)
print(" QUANT DEVELOPMENT ENGINE — END-TO-END DEMO")
print("=" * 55)

print(f"Initial Capital : ${initial_capital:,.2f}")
print(f"Final Capital   : ${capital:,.2f}")
print(f"Total Return    : {total_return:.2%}")
print(f"Trades          : {len(pnl)}")
print(f"Win Rate        : {win_rate:.2%}")
print(f"Max Drawdown    : {max_drawdown:.2%}")
print(f"Report          : {output}")

print("\nPipeline:")
print("Market Data")
print("    ↓")
print("SMA Strategy")
print("    ↓")
print("Risk Control")
print("    ↓")
print("Order Execution Simulation")
print("    ↓")
print("Portfolio")
print("    ↓")
print("Performance Metrics")
print("    ↓")
print("CSV Report")

print("\nSTATUS: DEMO COMPLETE")
print("=" * 55)