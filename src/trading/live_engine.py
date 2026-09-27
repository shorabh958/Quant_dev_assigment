from __future__ import annotations

from dataclasses import dataclass

from .execution_service import (
    ExecutionRequest,
    OrderExecutionService,
)
from .risk import RiskManager


@dataclass(frozen=True)
class LiveSignal:
    symbol: str
    side: str
    quantity: int
    price: float
    client_order_id: str


class LiveTradingEngine:

    def __init__(
        self,
        execution_service: OrderExecutionService,
        risk_manager: RiskManager,
    ):
        self.execution = execution_service
        self.risk = risk_manager

    def execute(
        self,
        signal: LiveSignal,
        current_position: int,
        daily_pnl: float = 0.0,
        drawdown: float = 0.0,
        volatility: float = 0.0,
    ):

        allowed = self.risk.check(
            current_position=current_position,
            requested_quantity=signal.quantity,
            daily_pnl=daily_pnl,
            drawdown=drawdown,
            volatility=volatility,
        )

        if allowed <= 0:
            return None

        request = ExecutionRequest(
            client_order_id=signal.client_order_id,
            symbol=signal.symbol,
            side=signal.side,
            quantity=allowed,
            price=signal.price,
        )

        return self.execution.submit(request)