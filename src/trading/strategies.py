from dataclasses import dataclass

from .models import Candle, Side


@dataclass
class Signal:
    side: Side
    reason: str


@dataclass
class GridConfig:
    spacing_atr: float = 1.0
    max_levels: int = 3


class GridStrategy:
    def __init__(self, config: GridConfig | None = None):
        self.config = config or GridConfig()

    def generate_signal(
        self,
        candle: Candle,
        atr_value: float,
        reference_price: float,
    ) -> Signal | None:
        if atr_value <= 0:
            return None

        spacing = atr_value * self.config.spacing_atr

        if candle.close <= reference_price - spacing:
            return Signal(Side.BUY, "grid_lower_level")

        if candle.close >= reference_price + spacing:
            return Signal(Side.SELL, "grid_upper_level")

        return None