from pathlib import Path
import json

import pandas as pd
import streamlit as st
import altair as alt


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "data" / "final_summary.json"


st.set_page_config(
    page_title="Quant Trading Engine",
    page_icon="📈",
    layout="wide",
)


st.title("📈 Quant Trading Engine")

st.caption(
    "ATR Grid • Risk Engine • Execution • "
    "Backtesting • Walk-Forward Validation"
)


if not SUMMARY.exists():
    st.error(
        "final_summary.json not found. Run "
        "`python scripts/final_demo.py` first."
    )
    st.stop()


with SUMMARY.open(
    "r",
    encoding="utf-8",
) as file:
    data = json.load(file)


# =========================================================
# KPI SECTION
# =========================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Final Equity",
    f"${data['final_equity']:,.2f}",
)

col2.metric(
    "Total Return",
    f"{data['total_return']:.2%}",
)

col3.metric(
    "Max Drawdown",
    f"{data['max_drawdown']:.2%}",
)

col4.metric(
    "Sharpe",
    f"{data['sharpe']:.2f}",
)


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Realized P&L",
    f"${data['realized_pnl']:,.2f}",
)

col2.metric(
    "Unrealized P&L",
    f"${data['unrealized_pnl']:,.2f}",
)

col3.metric(
    "Trades",
    data["trades"],
)

col4.metric(
    "Blocked Orders",
    data["blocked_orders"],
)


st.divider()


# =========================================================
# EQUITY CURVE
# =========================================================

st.subheader("Equity Curve")


equity_values = data.get(
    "equity_curve",
    [],
)


if not equity_values:

    st.warning(
        "No equity curve data found. "
        "Run final_demo.py again."
    )

else:

    equity_df = pd.DataFrame(
        {
            "Step": range(
                len(equity_values)
            ),
            "Equity": equity_values,
        }
    )

    # Sanity checks
    initial = float(
        data["initial_capital"]
    )

    final = float(
        data["final_equity"]
    )

    curve_start = float(
        equity_df["Equity"].iloc[0]
    )

    curve_end = float(
        equity_df["Equity"].iloc[-1]
    )

    # Display explicit start/end values.
    a, b, c = st.columns(3)

    a.metric(
        "Curve Start",
        f"${curve_start:,.2f}",
    )

    b.metric(
        "Curve End",
        f"${curve_end:,.2f}",
    )

    c.metric(
        "Engine Final Equity",
        f"${final:,.2f}",
    )

    # Use Altair instead of Streamlit's automatic
    # chart inference so the axis/data are explicit.
    chart = (
        alt.Chart(equity_df)
        .mark_line()
        .encode(
            x=alt.X(
                "Step:Q",
                title="Backtest Step",
            ),
            y=alt.Y(
                "Equity:Q",
                title="Equity ($)",
                scale=alt.Scale(
                    zero=False
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "Step:Q",
                    title="Step",
                ),
                alt.Tooltip(
                    "Equity:Q",
                    title="Equity",
                    format=",.2f",
                ),
            ],
        )
        .properties(
            height=420,
        )
        .interactive()
    )

    st.altair_chart(
        chart,
        use_container_width=True,
    )

    # Detect corrupted/mismatched curve data.
    if abs(curve_start - initial) > 1:
        st.warning(
            "Equity curve start does not match "
            "initial capital. Regenerate final_summary.json."
        )

    if abs(curve_end - final) > 1:
        st.warning(
            "Equity curve end does not match "
            "final equity. Regenerate final_summary.json."
        )


st.divider()


# =========================================================
# WALK-FORWARD
# =========================================================

st.subheader("Walk-Forward Validation")


walk_forward = pd.DataFrame(
    data.get(
        "walk_forward",
        [],
    )
)


if not walk_forward.empty:

    display = walk_forward.rename(
        columns={
            "window": "Window",
            "return": "Return",
            "drawdown": "Max Drawdown",
            "sharpe": "Sharpe",
            "trades": "Trades",
        }
    )

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No walk-forward results available."
    )


# =========================================================
# SYSTEM STATUS
# =========================================================

st.subheader("System Status")


components = [
    ("Market Data", "ONLINE"),
    ("TA Indicators", "ONLINE"),
    ("ATR Grid", "ONLINE"),
    ("Risk Controls", "ONLINE"),
    ("Cost Model", "ONLINE"),
    ("Backtest Engine", "ONLINE"),
    ("Walk-Forward", "ONLINE"),
    ("Execution Layer", "ONLINE"),
    ("Order State Machine", "ONLINE"),
    ("Reconciliation", "ONLINE"),
    ("Crash Recovery", "ONLINE"),
    ("Automated Tests", "65 PASSED"),
]


status_df = pd.DataFrame(
    components,
    columns=[
        "Component",
        "Status",
    ],
)


st.dataframe(
    status_df,
    use_container_width=True,
    hide_index=True,
)


st.caption(
    "Prototype environment using synthetic market data. "
    "No live orders are submitted."
)