from dataclasses import dataclass
from decimal import Decimal

from .models import Candle, Fill, Side
from .portfolio import Portfolio
from .risk import RiskManager


@dataclass
class BacktestConfig:
    slippage_bps: float = 1.0
    fee_per_order: Decimal = Decimal("20")


class BacktestEngine:

    def __init__(
        self,
        strategy,
        config=None,
        risk_manager=None,
    ):
        self.strategy = strategy

        # Backwards-compatible constructor:
        #
        # BacktestEngine(strategy)
        # BacktestEngine(strategy, BacktestConfig(...))
        # BacktestEngine(strategy, config=..., risk_manager=...)
        #
        if isinstance(config, BacktestConfig):
            self.config = config
        else:
            self.config = BacktestConfig()

        self.risk_manager = (
            risk_manager
            if risk_manager is not None
            else RiskManager()
        )

    def _execution_price(self, price, side):

        slippage = Decimal(
            str(self.config.slippage_bps / 10000)
        )

        base_price = Decimal(str(price))

        if side == Side.BUY:
            return base_price * (
                Decimal("1") + slippage
            )

        return base_price * (
            Decimal("1") - slippage
        )

    def run(self, data):

        required = {
            "open",
            "high",
            "low",
            "close",
            "volume",
            "atr",
        }

        missing = required - set(data.columns)

        if missing:

            missing_text = ", ".join(
                column.upper()
                for column in sorted(missing)
            )

            raise ValueError(
                f"Missing required columns: {missing_text}"
            )

        if len(data) < 2:
            return Portfolio()

        portfolio = Portfolio()

        reference_price = float(
            data.iloc[0]["close"]
        )

        pending_signal = None

        for i in range(1, len(data)):

            row = data.iloc[i]

            timestamp = data.index[i]

            candle = Candle(
                timestamp=timestamp,
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=float(row["volume"]),
            )

            # ==============================================
            # Execute previous-bar signal at current open
            # ==============================================

            if pending_signal is not None:

                current_position = (
                    portfolio.position.quantity
                )

                quantity = (
                    self.risk_manager.allowed_quantity(
                        current_position,
                        pending_signal.quantity,
                    )
                )

                if quantity > 0:

                    fill_price = self._execution_price(
                        candle.open,
                        pending_signal.side,
                    )

                    fill = Fill(
                        order_id=f"BT-{i}",
                        timestamp=timestamp,
                        side=pending_signal.side,
                        quantity=quantity,
                        price=fill_price,
                        fees=self.config.fee_per_order,
                    )

                    portfolio.apply_fill(fill)

            # ==============================================
            # Generate signal using current close
            # ==============================================

            pending_signal = (
                self.strategy.generate_signal(
                    candle=candle,
                    atr_value=float(row["atr"]),
                    reference_price=reference_price,
                    current_position=portfolio.position.quantity,
                )
            )

            if pending_signal is not None:
                reference_price = candle.close

        return portfolio