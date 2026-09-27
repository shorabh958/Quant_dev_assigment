from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "demo_trades.csv"
OUTPUT = ROOT / "data" / "demo_report.png"


def build_dashboard():
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing {INPUT}. Run run_demo.py first.")

    trades = pd.read_csv(INPUT)

    if trades.empty:
        raise ValueError("Trade report is empty.")

    trades["pnl"] = pd.to_numeric(
        trades.get("pnl", 0), errors="coerce"
    ).fillna(0)

    initial_capital = 100_000
    equity = initial_capital + trades["pnl"].cumsum()

    total_return = equity.iloc[-1] / initial_capital - 1
    peak = equity.cummax()
    drawdown = (equity - peak) / peak
    max_drawdown = drawdown.min()

    closed = trades[trades["side"] == "SELL"]
    win_rate = (
        (closed["pnl"] > 0).mean()
        if not closed.empty
        else 0
    )

    fig, ax = plt.subplots(figsize=(11, 6))

    ax.plot(
        range(len(equity)),
        equity,
        linewidth=2,
        label="Equity",
    )

    buys = trades[trades["side"] == "BUY"]
    sells = trades[trades["side"] == "SELL"]

    ax.scatter(
        buys.index,
        initial_capital + trades.loc[buys.index, "pnl"].cumsum(),
        marker="^",
        label="BUY",
    )

    ax.scatter(
        sells.index,
        initial_capital + trades.loc[sells.index, "pnl"].cumsum(),
        marker="v",
        label="SELL",
    )

    ax.set_title(
        f"Quant Trading Demo | "
        f"Return: {total_return:.2%} | "
        f"Win Rate: {win_rate:.2%} | "
        f"Max DD: {max_drawdown:.2%}"
    )
    ax.set_xlabel("Trade")
    ax.set_ylabel("Equity")
    ax.legend()
    ax.grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(OUTPUT, dpi=150)
    plt.close(fig)

    print(f"Dashboard saved: {OUTPUT}")


if __name__ == "__main__":
    build_dashboard()