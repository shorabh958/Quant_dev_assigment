import math


def total_return(equity):
    if not equity:
        return 0.0
    return equity[-1] / equity[0] - 1


def max_drawdown(equity):
    if not equity:
        return 0.0

    peak = equity[0]
    worst = 0.0

    for value in equity:
        peak = max(peak, value)
        drawdown = (peak - value) / peak if peak else 0
        worst = max(worst, drawdown)

    return worst


def sharpe_ratio(returns, periods_per_year=252):
    if len(returns) < 2:
        return 0.0

    mean = sum(returns) / len(returns)

    variance = sum((x - mean) ** 2 for x in returns) / (len(returns) - 1)

    std = math.sqrt(variance)

    if std == 0:
        return 0.0

    return mean / std * math.sqrt(periods_per_year)