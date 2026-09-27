from __future__ import annotations

from dataclasses import dataclass

from .broker_adapter import (
    BrokerCredentials,
    RESTBrokerClient,
)


@dataclass(frozen=True)
class KiteConfig:
    api_key: str
    access_token: str


class KiteBrokerAdapter:

    """
    Broker-neutral execution boundary.

    The strategy/execution engine talks to this interface,
    rather than directly depending on a broker implementation.
    """

    def __init__(
        self,
        client: RESTBrokerClient,
    ):
        self.client = client

    def place_order(
        self,
        *,
        client_order_id,
        symbol,
        side,
        quantity,
        price,
    ):
        return self.client.place_order(
            client_order_id=client_order_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
        )

    def get_positions(self):
        return self.client.get_positions()

    def close(self):
        self.client.close()