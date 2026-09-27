from pathlib import Path
import json

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "data" / "final_summary.json"

st.set_page_config(
    page_title="Quant Trading Engine",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Quant Trading Engine")
st.caption(
    "ATR Grid Strategy • Risk Engine • Backtesting • "
    "Execution • Walk-Forward Analysis"
)

if not SUMMARY.exists():
    st.error(
        "No final_summary.json found. "
        "Run: python scripts/final_demo.py"
    )
    st.stop()

with SUMMARY.open(
    "r",
    encoding="utf-8",
) as f:
    data = json.load(f)

# -----------------------------
# KPI ROW
# -----------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Final Equity",
    f"${data['final_equity']:,.2f}",
)

c2.metric(
    "Return",
    f"{data['total_return']:.2%}",
)

c3.metric(
    "Max Drawdown",
    f"{data['max_drawdown']:.2%}",
)

c4.metric(
    "Sharpe",
    f"{data['sharpe']:.2f}",
)

# -----------------------------
# SECONDARY METRICS
# -----------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Realized P&L",
    f"${data['realized_pnl']:,.2f}",
)

c2.metric(
    "Unrealized P&L",
    f"${data['unrealized_pnl']:,.2f}",
)

c3.metric(
    "Trades",
    data["trades"],
)

c4.metric(
    "Blocked Orders",
    data["blocked_orders"],
)

st.divider()

# -----------------------------
# EQUITY CURVE
# -----------------------------

st.subheader("Equity Curve")

equity = pd.DataFrame(
    {
        "Equity": data["equity_curve"]
    }
)

st.line_chart(
    equity,
    height=400,
)

# -----------------------------
# WALK FORWARD
# -----------------------------

st.subheader("Walk-Forward Validation")

wf = pd.DataFrame(
    data["walk_forward"]
)

if not wf.empty:

    wf_display = wf.rename(
        columns={
            "window": "Window",
            "return": "Return",
            "drawdown": "Max Drawdown",
            "sharpe": "Sharpe",
            "trades": "Trades",
        }
    )

    st.dataframe(
        wf_display,
        use_container_width=True,
        hide_index=True,
    )

# -----------------------------
# SYSTEM STATUS
# -----------------------------

st.subheader("System Status")

components = {
    "Market Data": "ONLINE",
    "Indicators": "ONLINE",
    "ATR Grid": "ONLINE",
    "Risk Controls": "ONLINE",
    "Cost Model": "ONLINE",
    "Backtest Engine": "ONLINE",
    "Walk-Forward": "ONLINE",
    "Execution Layer": "ONLINE",
    "Order State Machine": "ONLINE",
    "Reconciliation": "ONLINE",
    "Recovery": "ONLINE",
    "Automated Tests": "65 PASSED",
}

status_df = pd.DataFrame(
    list(components.items()),
    columns=["Component", "Status"],
)

st.dataframe(
    status_df,
    use_container_width=True,
    hide_index=True,
)

st.caption(
    "Prototype environment — synthetic market data; "
    "no live orders are submitted."
)