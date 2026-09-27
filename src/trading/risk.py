from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskConfig:
    max_position: int = 3
    max_pyramids: int = 3
    max_daily_loss: float = 5000.0
    max_drawdown: float = 0.10
    max_volatility: float = 10.0


class RiskManager:

    def __init__(self, config=None):
        self.config = config or RiskConfig()

    def allowed_quantity(
        self,
        current_position: int,
        requested: int,
    ) -> int:

        if requested <= 0:
            return 0

        remaining = (
            self.config.max_position
            - abs(current_position)
        )

        return max(
            0,
            min(
                requested,
                remaining,
            ),
        )

    def can_pyramid(
        self,
        current_position: int,
    ) -> bool:

        return (
            abs(current_position)
            < self.config.max_pyramids
        )

    def kill_switch(
        self,
        daily_pnl: float,
    ) -> bool:

        return (
            daily_pnl
            <= -self.config.max_daily_loss
        )

    def circuit_breaker(
        self,
        drawdown: float,
        daily_pnl: float,
        volatility: float,
    ) -> bool:

        return (
            drawdown >= self.config.max_drawdown
            or daily_pnl
            <= -self.config.max_daily_loss
            or volatility
            >= self.config.max_volatility
        )

    def check(
        self,
        current_position: int,
        requested_quantity: int,
        daily_pnl: float = 0.0,
        drawdown: float = 0.0,
        volatility: float = 0.0,
    ) -> int:

        if self.circuit_breaker(
            drawdown,
            daily_pnl,
            volatility,
        ):
            return 0

        if not self.can_pyramid(
            current_position
        ):
            return 0

        return self.allowed_quantity(
            current_position,
            requested_quantity,
        )