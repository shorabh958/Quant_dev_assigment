from decimal import Decimal

from .models import Fill, Position, Side


class Portfolio:
    def __init__(self):
        self.position = Position()
        self.realized_pnl = Decimal("0")

    def apply_fill(self, fill: Fill) -> None:
        signed_qty = (
            fill.quantity if fill.side == Side.BUY else -fill.quantity
        )

        old_qty = self.position.quantity
        old_avg = self.position.average_price

        # Opening or adding to a position.
        if old_qty == 0 or (old_qty > 0) == (signed_qty > 0):
            new_qty = old_qty + signed_qty
            total_cost = old_avg * abs(old_qty) + fill.price * abs(signed_qty)

            self.position.quantity = new_qty
            self.position.average_price = (
                total_cost / abs(new_qty) if new_qty else Decimal("0")
            )
            return

        # Closing/reducing an existing position.
        closing_qty = min(abs(old_qty), abs(signed_qty))

        if old_qty > 0:
            self.realized_pnl += (
                fill.price - old_avg
            ) * closing_qty
        else:
            self.realized_pnl += (
                old_avg - fill.price
            ) * closing_qty

        new_qty = old_qty + signed_qty

        if new_qty == 0:
            self.position = Position()
        elif (new_qty > 0) != (old_qty > 0):
            # Position reversed: remaining quantity starts at fill price.
            self.position.quantity = new_qty
            self.position.average_price = fill.price
        else:
            self.position.quantity = new_qty

    def unrealized_pnl(self, mark_price: Decimal) -> Decimal:
        if self.position.is_flat:
            return Decimal("0")

        if self.position.is_long:
            return (
                mark_price - self.position.average_price
            ) * self.position.quantity

        return (
            self.position.average_price - mark_price
        ) * abs(self.position.quantity)

    def total_pnl(self, mark_price: Decimal) -> Decimal:
        return self.realized_pnl + self.unrealized_pnl(mark_price)