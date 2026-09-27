from decimal import Decimal

from .models import Fill, Position, Side


class Portfolio:

    def __init__(self):
        self.position = Position()
        self.realized_pnl = Decimal("0")

    def apply_fill(self, fill):

        fill_price = Decimal(str(fill.price))
        fees = Decimal(str(fill.fees))

        signed_qty = (
            fill.quantity
            if fill.side == Side.BUY
            else -fill.quantity
        )

        old_qty = self.position.quantity
        old_avg = self.position.average_price

        # ==============================================
        # Opening / adding to existing position
        # ==============================================

        if (
            old_qty == 0
            or (old_qty > 0) == (signed_qty > 0)
        ):

            new_qty = old_qty + signed_qty

            total_cost = (
                old_avg * abs(old_qty)
                + fill_price * abs(signed_qty)
            )

            self.position.quantity = new_qty

            self.position.average_price = (
                total_cost / abs(new_qty)
                if new_qty
                else Decimal("0")
            )

            self.realized_pnl -= fees

            return

        # ==============================================
        # Closing / reversing position
        # ==============================================

        closing_qty = min(
            abs(old_qty),
            abs(signed_qty),
        )

        if old_qty > 0:

            self.realized_pnl += (
                fill_price - old_avg
            ) * closing_qty

        else:

            self.realized_pnl += (
                old_avg - fill_price
            ) * closing_qty

        self.realized_pnl -= fees

        new_qty = old_qty + signed_qty

        # Completely flat
        if new_qty == 0:

            self.position = Position()

        # Reversal
        elif (
            (new_qty > 0)
            != (old_qty > 0)
        ):

            self.position.quantity = new_qty

            self.position.average_price = (
                fill_price
            )

        # Partial close
        else:

            self.position.quantity = new_qty

    def unrealized_pnl(self, mark_price):

        mark_price = Decimal(
            str(mark_price)
        )

        if self.position.is_flat:
            return Decimal("0")

        if self.position.is_long:

            return (
                mark_price
                - self.position.average_price
            ) * self.position.quantity

        return (
            self.position.average_price
            - mark_price
        ) * abs(self.position.quantity)

    def total_pnl(self, mark_price):

        return (
            self.realized_pnl
            + self.unrealized_pnl(mark_price)
        )