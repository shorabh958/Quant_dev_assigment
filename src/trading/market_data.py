from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import AsyncIterator, Callable


@dataclass(frozen=True)
class MarketTick:
    symbol: str
    exchange: str
    price: float
    quantity: int
    timestamp: float


class TickFeed:

    async def stream(self) -> AsyncIterator[MarketTick]:
        raise NotImplementedError


class SimulatedTickFeed(TickFeed):

    def __init__(self, ticks):
        self.ticks = list(ticks)

    async def stream(self):
        for tick in self.ticks:
            yield tick
            await asyncio.sleep(0)


class ResilientTickFeed:

    def __init__(
        self,
        source_factory: Callable[
            [], AsyncIterator[MarketTick]
        ],
        max_reconnects: int = 5,
        reconnect_delay: float = 0.05,
    ):
        self.source_factory = source_factory
        self.max_reconnects = max_reconnects
        self.reconnect_delay = reconnect_delay

    async def stream(self):

        attempts = 0

        while attempts < self.max_reconnects:

            try:
                source = self.source_factory()

                async for tick in source:
                    attempts = 0
                    yield tick

                # Normal stream completion is NOT
                # considered a connection failure.
                return

            except Exception:

                attempts += 1

                if attempts >= self.max_reconnects:
                    raise

                await asyncio.sleep(
                    self.reconnect_delay * attempts
                )