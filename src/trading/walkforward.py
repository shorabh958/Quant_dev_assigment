from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class WalkForwardWindow:
    train: pd.DataFrame
    test: pd.DataFrame


def generate_windows(
    data,
    train_size,
    test_size,
):

    if train_size <= 0:
        raise ValueError(
            "train_size must be positive"
        )

    if test_size <= 0:
        raise ValueError(
            "test_size must be positive"
        )

    start = 0

    while (
        start
        + train_size
        + test_size
        <= len(data)
    ):

        train_end = (
            start + train_size
        )

        test_end = (
            train_end + test_size
        )

        yield WalkForwardWindow(
            train=data.iloc[
                start:train_end
            ],
            test=data.iloc[
                train_end:test_end
            ],
        )

        start += test_size


@dataclass(frozen=True)
class WalkForwardResult:
    window: int
    train_size: int
    test_size: int
    train_start: object
    train_end: object
    test_start: object
    test_end: object


def evaluate_walk_forward(
    data,
    train_size,
    test_size,
):

    results = []

    for index, window in enumerate(
        generate_windows(
            data,
            train_size,
            test_size,
        ),
        start=1,
    ):

        results.append(
            WalkForwardResult(
                window=index,
                train_size=len(
                    window.train
                ),
                test_size=len(
                    window.test
                ),
                train_start=(
                    window.train.index[0]
                ),
                train_end=(
                    window.train.index[-1]
                ),
                test_start=(
                    window.test.index[0]
                ),
                test_end=(
                    window.test.index[-1]
                ),
            )
        )

    return results