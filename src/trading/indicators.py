from __future__ import annotations

import numpy as np
import pandas as pd


def true_range(data: pd.DataFrame) -> pd.Series:
    previous_close = data["close"].shift(1)

    ranges = pd.concat(
        [
            data["high"] - data["low"],
            (data["high"] - previous_close).abs(),
            (data["low"] - previous_close).abs(),
        ],
        axis=1,
    )

    return ranges.max(axis=1)


def atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
    if period <= 0:
        raise ValueError("ATR period must be positive")

    tr = true_range(data)

    # Wilder-style smoothing.
    return tr.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period,
    ).mean()


def sma(data: pd.DataFrame, period: int) -> pd.Series:
    if period <= 0:
        raise ValueError("SMA period must be positive")

    return data["close"].rolling(period).mean()


def returns(data: pd.DataFrame) -> pd.Series:
    return data["close"].pct_change()