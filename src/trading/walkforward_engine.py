from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .engine import QuantEngine


@dataclass(frozen=True)
class WalkForwardResult:
    window: int
    train_rows: int
    test_rows: int
    return_pct: float
    max_drawdown: float
    sharpe: float
    trades: int


def run_walk_forward(
    engine: QuantEngine,
    data: pd.DataFrame,
    train_size: int,
    test_size: int,
):

    if train_size <= 0 or test_size <= 0:
        raise ValueError(
            "Window sizes must be positive"
        )

    results = []

    start = 0
    window_number = 1

    while (
        start + train_size + test_size
        <= len(data)
    ):

        train = data.iloc[
            start:start + train_size
        ]

        test = data.iloc[
            start + train_size:
            start + train_size + test_size
        ]

        # Training segment is deliberately kept
        # separate from the out-of-sample test.
        _ = train

        result = engine.run(test)

        results.append(
            WalkForwardResult(
                window=window_number,
                train_rows=len(train),
                test_rows=len(test),
                return_pct=result.total_return,
                max_drawdown=result.max_drawdown,
                sharpe=result.sharpe,
                trades=result.trades,
            )
        )

        start += test_size
        window_number += 1

    return results