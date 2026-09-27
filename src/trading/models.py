from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, Enum):
    NEW = "NEW"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class Order:
    order_id: str
    side: Side
    quantity: int
    price: Decimal
    status: OrderStatus = OrderStatus.NEW


@dataclass
class Position:
    quantity: int = 0
    average_price: Decimal = Decimal("0")

    @property
    def is_long(self) -> bool:
        return self.quantity > 0

    @property
    def is_short(self) -> bool:
        return self.quantity < 0

    @property
    def is_flat(self) -> bool:
        return self.quantity == 0


@dataclass
class Fill:
    order_id: str
    timestamp: datetime
    side: Side
    quantity: int
    price: Decimal
    fees: Decimal = Decimal("0")