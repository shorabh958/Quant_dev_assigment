from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "demo_trades.csv"
OUTPUT = ROOT / "data" / "demo_summary.txt"


def generate():
    trades = pd.read_csv(INPUT)

    pnl = pd.to_numeric(
        trades.get("pnl", 0),
        errors="coerce",
    ).fillna(0)

    closed = trades[trades["side"] == "SELL"]

    capital = 100_000 + pnl.sum()
    returns = capital / 100_000 - 1

    win_rate = (
        (closed["pnl"] > 0).mean()
        if not closed.empty
        else 0
    )

    report = f"""QUANT ENGINE DEMO REPORT

Initial Capital: 100000
Final Capital:   {capital:.2f}
Return:          {returns:.2%}
Trades:          {len(closed)}
Win Rate:        {win_rate:.2%}

Pipeline:
Market Data
-> Strategy
-> Risk
-> Execution
-> Portfolio
-> Metrics
-> Report
"""

    OUTPUT.write_text(report)

    print(report)
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    generate()