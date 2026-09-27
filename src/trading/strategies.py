from __future__ import annotations

from dataclasses import dataclass

from .models import Side


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

    def __init__(self, config=None):
        self.config = (
            config
            or GridConfig()
        )

    def generate_signal(
        self,
        candle,
        atr_value,
        reference_price,
        current_position=0,
    ):

        if atr_value <= 0:
            return None

        spacing = (
            atr_value
            * self.config.spacing_atr
        )

        # Do not pyramid beyond configured levels.
        if (
            abs(current_position)
            >= self.config.max_levels
        ):
            return None

        if (
            candle.close
            <= reference_price - spacing
        ):

            return Signal(
                Side.BUY,
                "grid_lower_level",
                self.config.pyramid_quantity,
            )

        if (
            candle.close
            >= reference_price + spacing
        ):

            return Signal(
                Side.SELL,
                "grid_upper_level",
                self.config.pyramid_quantity,
            )

        return None


class StopAndReverseStrategy:

    def __init__(
        self,
        threshold=0.0,
        quantity=1,
    ):

        self.threshold = threshold
        self.quantity = quantity

    def generate_signal(
        self,
        price,
        reference_price,
        current_position,
    ):

        if (
            price
            > reference_price
            + self.threshold
            and current_position <= 0
        ):

            return Signal(
                Side.BUY,
                "stop_and_reverse_long",
                self.quantity,
            )

        if (
            price
            < reference_price
            - self.threshold
            and current_position >= 0
        ):

            return Signal(
                Side.SELL,
                "stop_and_reverse_short",
                self.quantity,
            )

        return None