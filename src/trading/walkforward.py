from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class WalkForwardWindow:
    train: pd.DataFrame
    test: pd.DataFrame


def generate_windows(
    data: pd.DataFrame,
    train_size: int,
    test_size: int,
):
    if train_size <= 0 or test_size <= 0:
        raise ValueError("Window sizes must be positive")

    start = 0

    while start + train_size + test_size <= len(data):
        train_end = start + train_size
        test_end = train_end + test_size

        yield WalkForwardWindow(
            train=data.iloc[start:train_end],
            test=data.iloc[train_end:test_end],
        )

        start += test_size