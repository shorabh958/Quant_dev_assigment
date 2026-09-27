from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Regime(str, Enum):
    RISK_ON = "risk_on"
    NEUTRAL = "neutral"
    RISK_OFF = "risk_off"
    CRISIS = "crisis"


@dataclass(frozen=True)
class MacroSnapshot:
    equity_return: float
    volatility: float
    interest_rate_change: float
    dollar_change: float


@dataclass(frozen=True)
class RegimeParameters:
    position_multiplier: float
    grid_spacing_multiplier: float
    trading_enabled: bool


class MacroRegimeEngine:
    def score(self, snapshot: MacroSnapshot) -> float:
        score = 0.0

        # Positive equity performance -> risk-on
        score += snapshot.equity_return

        # Rising volatility -> risk-off
        score -= snapshot.volatility

        # Rising rates / dollar strength -> risk-off
        score -= snapshot.interest_rate_change
        score -= snapshot.dollar_change

        return score

    def classify(self, snapshot: MacroSnapshot) -> Regime:
        score = self.score(snapshot)

        if snapshot.volatility >= 8:
            return Regime.CRISIS

        if score >= 2:
            return Regime.RISK_ON

        if score <= -2:
            return Regime.RISK_OFF

        return Regime.NEUTRAL

    def parameters(self, regime: Regime) -> RegimeParameters:
        if regime == Regime.RISK_ON:
            return RegimeParameters(
                position_multiplier=1.0,
                grid_spacing_multiplier=1.0,
                trading_enabled=True,
            )

        if regime == Regime.RISK_OFF:
            return RegimeParameters(
                position_multiplier=0.5,
                grid_spacing_multiplier=1.5,
                trading_enabled=True,
            )

        if regime == Regime.CRISIS:
            return RegimeParameters(
                position_multiplier=0.0,
                grid_spacing_multiplier=2.0,
                trading_enabled=False,
            )

        return RegimeParameters(
            position_multiplier=0.75,
            grid_spacing_multiplier=1.25,
            trading_enabled=True,
        )


@dataclass
class CircuitBreaker:
    max_drawdown: float = 0.10
    max_daily_loss: float = 5000.0
    max_volatility: float = 10.0

    def triggered(
        self,
        drawdown: float,
        daily_pnl: float,
        volatility: float,
    ) -> bool:
        return (
            drawdown >= self.max_drawdown
            or daily_pnl <= -self.max_daily_loss
            or volatility >= self.max_volatility
        )