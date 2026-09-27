from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

import pandas as pd

from .indicators import add_indicators
from .metrics import max_drawdown, sharpe_ratio
from .models import Candle, Fill
from .portfolio import Portfolio
from .risk import RiskManager
from .strategies import GridStrategy
from .trading_costs import CostModel


@dataclass(frozen=True)
class EngineResult:
    initial_capital: Decimal
    final_equity: Decimal
    realized_pnl: Decimal
    unrealized_pnl: Decimal
    total_return: float
    max_drawdown: float
    sharpe: float
    trades: int
    blocked_orders: int
    equity_curve: list[float]


class QuantEngine:

    def __init__(
        self,
        strategy,
        risk_manager=None,
        cost_model=None,
        initial_capital=Decimal("100000"),
    ):
        self.strategy = strategy
        self.risk = risk_manager or RiskManager()
        self.costs = cost_model or CostModel()
        self.initial_capital = Decimal(
            str(initial_capital)
        )

    def run(
        self,
        data: pd.DataFrame,
        atr_period: int = 14,
    ) -> EngineResult:

        required = {
            "open",
            "high",
            "low",
            "close",
            "volume",
        }

        missing = required - set(data.columns)

        if missing:
            raise ValueError(
                f"Missing columns: {sorted(missing)}"
            )

        frame = add_indicators(
            data.copy(),
            atr_period=atr_period,
        ).dropna()

        if frame.empty:
            raise ValueError(
                "Not enough data for indicators"
            )

        portfolio = Portfolio()

        reference_price = float(
            frame.iloc[0]["close"]
        )

        pending_signal = None
        blocked_orders = 0
        trade_pnls: list[float] = []

        equity_curve = [
            float(self.initial_capital)
        ]

        for i in range(1, len(frame)):

            row = frame.iloc[i]

            # ------------------------------------------
            # 1. Execute previous-bar signal
            # ------------------------------------------

            if pending_signal is not None:

                current_position = (
                    portfolio.position.quantity
                )

                volatility = float(
                    row["volatility"]
                )

                quantity = self.risk.check(
                    current_position=current_position,
                    requested_quantity=(
                        pending_signal.quantity
                    ),
                    daily_pnl=float(
                        portfolio.realized_pnl
                    ),
                    drawdown=0.0,
                    volatility=volatility * 100,
                )

                if quantity <= 0:

                    blocked_orders += 1

                else:

                    execution_price = (
                        self.costs.execution_price(
                            Decimal(
                                str(row["open"])
                            ),
                            pending_signal.side.value,
                        )
                    )

                    before_realized = (
                        portfolio.realized_pnl
                    )

                    fill = Fill(
                        order_id=f"ENGINE-{i}",
                        timestamp=frame.index[i],
                        side=pending_signal.side,
                        quantity=quantity,
                        price=execution_price,
                        fees=self.costs.total_cost(
                            execution_price,
                            quantity,
                        ),
                    )

                    portfolio.apply_fill(fill)

                    realized_change = (
                        portfolio.realized_pnl
                        - before_realized
                    )

                    if realized_change != 0:
                        trade_pnls.append(
                            float(realized_change)
                        )

            # ------------------------------------------
            # 2. Build current candle
            # ------------------------------------------

            candle = Candle(
                timestamp=frame.index[i],
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=float(row["volume"]),
            )

            # ------------------------------------------
            # 3. Generate next signal
            # ------------------------------------------

            pending_signal = (
                self.strategy.generate_signal(
                    candle=candle,
                    atr_value=float(row["atr"]),
                    reference_price=reference_price,
                    current_position=(
                        portfolio.position.quantity
                    ),
                )
            )

            if pending_signal is not None:
                reference_price = candle.close

            # ------------------------------------------
            # 4. Mark portfolio to market
            # ------------------------------------------

            mark_price = Decimal(
                str(row["close"])
            )

            equity = (
                self.initial_capital
                + portfolio.total_pnl(mark_price)
            )

            equity_curve.append(
                float(equity)
            )

        # ------------------------------------------
        # 5. Final mark
        # ------------------------------------------

        final_mark = Decimal(
            str(frame.iloc[-1]["close"])
        )

        realized_pnl = (
            portfolio.realized_pnl
        )

        unrealized_pnl = (
            portfolio.unrealized_pnl(
                final_mark
            )
        )

        final_equity = (
            self.initial_capital
            + realized_pnl
            + unrealized_pnl
        )

        total_return = float(
            final_equity
            / self.initial_capital
            - Decimal("1")
        )

        # ------------------------------------------
        # 6. Performance metrics
        # ------------------------------------------

        returns = (
            pd.Series(equity_curve)
            .pct_change()
            .dropna()
            .tolist()
        )

        drawdown = max_drawdown(
            equity_curve
        )

        sharpe = sharpe_ratio(
            returns
        )

        # ------------------------------------------
        # 7. Final result
        # ------------------------------------------

        return EngineResult(
            initial_capital=self.initial_capital,
            final_equity=final_equity,
            realized_pnl=realized_pnl,
            unrealized_pnl=unrealized_pnl,
            total_return=total_return,
            max_drawdown=drawdown,
            sharpe=sharpe,
            trades=len(trade_pnls),
            blocked_orders=blocked_orders,
            equity_curve=equity_curve,
        )