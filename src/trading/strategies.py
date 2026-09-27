from dataclasses import dataclass

from .models import Candle, Side


@dataclass
class Signal:
    side: Side
    reason: str
    quantity: int = 1


@dataclass
class GridConfig:
    spacing_atr: float = 1.0
    max_levels: int = 3
    pyramid_quantity: int = 1


class GridStrategy:
    def __init__(self, config: GridConfig | None = None):
        self.config = config or GridConfig()

    def generate_signal(
        self,
        candle: Candle,
        atr_value: float,
        reference_price: float,
        current_position: int = 0,
    ) -> Signal | None:

        if atr_value <= 0:
            return None

        spacing = atr_value * self.config.spacing_atr

        if candle.close <= reference_price - spacing:
            return Signal(
                side=Side.BUY,
                reason="grid_lower_level",
                quantity=self.config.pyramid_quantity,
            )

        if candle.close >= reference_price + spacing:
            return Signal(
                side=Side.SELL,
                reason="grid_upper_level",
                quantity=self.config.pyramid_quantity,
            )

        return None


class StopAndReverseStrategy:
    def __init__(self, threshold: float = 0.0):
        self.threshold = threshold

    def generate_signal(
        self,
        price: float,
        reference_price: float,
        current_position: int,
    ) -> Signal | None:

        if price > reference_price + self.threshold:
            if current_position <= 0:
                return Signal(Side.BUY, "stop_and_reverse_long")

        if price < reference_price - self.threshold:
            if current_position >= 0:
                return Signal(Side.SELL, "stop_and_reverse_short")

        return None