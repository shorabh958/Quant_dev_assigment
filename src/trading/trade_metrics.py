from __future__ import annotations

import math


def trade_count(trades):
    return len(trades)


def winning_trades(trades):
    return sum(
        1
        for trade in trades
        if trade > 0
    )


def losing_trades(trades):
    return sum(
        1
        for trade in trades
        if trade < 0
    )


def win_rate(trades):

    if not trades:
        return 0.0

    return (
        winning_trades(trades)
        / len(trades)
    )


def profit_factor(trades):

    gains = sum(
        trade
        for trade in trades
        if trade > 0
    )

    losses = abs(
        sum(
            trade
            for trade in trades
            if trade < 0
        )
    )

    if losses == 0:
        return float("inf") if gains else 0.0

    return gains / losses


def expectancy(trades):

    if not trades:
        return 0.0

    return (
        sum(trades)
        / len(trades)
    )


def average_win(trades):

    wins = [
        trade
        for trade in trades
        if trade > 0
    ]

    return (
        sum(wins) / len(wins)
        if wins
        else 0.0
    )


def average_loss(trades):

    losses = [
        trade
        for trade in trades
        if trade < 0
    ]

    return (
        sum(losses) / len(losses)
        if losses
        else 0.0
    )


def trade_sharpe(trades):

    if len(trades) < 2:
        return 0.0

    mean = sum(trades) / len(trades)

    variance = sum(
        (trade - mean) ** 2
        for trade in trades
    ) / (len(trades) - 1)

    std = math.sqrt(variance)

    if std == 0:
        return 0.0

    return mean / std