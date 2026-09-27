from __future__ import annotations

import pandas as pd


def true_range(data: pd.DataFrame) -> pd.Series:
    prev_close = data["close"].shift(1)

    return pd.concat(
        [
            data["high"] - data["low"],
            (data["high"] - prev_close).abs(),
            (data["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)


def atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
    if period <= 0:
        raise ValueError("period must be positive")

    return true_range(data).ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period,
    ).mean()


def sma(data: pd.DataFrame, period: int = 20) -> pd.Series:
    if period <= 0:
        raise ValueError("period must be positive")

    return data["close"].rolling(period).mean()


def ema(data: pd.DataFrame, period: int = 20) -> pd.Series:
    if period <= 0:
        raise ValueError("period must be positive")

    return data["close"].ewm(
        span=period,
        adjust=False,
        min_periods=period,
    ).mean()


def momentum(data: pd.DataFrame, period: int = 10) -> pd.Series:
    if period <= 0:
        raise ValueError("period must be positive")

    return data["close"].diff(period)


def volatility(data: pd.DataFrame, period: int = 20) -> pd.Series:
    if period <= 0:
        raise ValueError("period must be positive")

    return data["close"].pct_change().rolling(period).std()


def volume_sma(data: pd.DataFrame, period: int = 20) -> pd.Series:
    if period <= 0:
        raise ValueError("period must be positive")

    return data["volume"].rolling(period).mean()


def add_indicators(
    data: pd.DataFrame,
    atr_period: int = 14,
    trend_period: int = 20,
    momentum_period: int = 10,
    volatility_period: int = 20,
) -> pd.DataFrame:

    result = data.copy()

    result["atr"] = atr(result, atr_period)
    result["sma"] = sma(result, trend_period)
    result["ema"] = ema(result, trend_period)
    result["momentum"] = momentum(result, momentum_period)
    result["volatility"] = volatility(result, volatility_period)
    result["volume_sma"] = volume_sma(result, trend_period)

    return result