from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable

import httpx


class BrokerAPIError(RuntimeError):
    pass


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    backoff_seconds: float = 0.05


@dataclass(frozen=True)
class BrokerCredentials:
    api_key: str
    access_token: str


class RESTBrokerClient:
    """
    Lightweight REST broker adapter.

    Designed so a real Zerodha/Kite adapter can later replace
    the transport without changing the execution layer.
    """

    def __init__(
        self,
        base_url: str,
        credentials: BrokerCredentials,
        retry_policy: RetryPolicy | None = None,
        transport: httpx.BaseTransport | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.credentials = credentials
        self.retry_policy = retry_policy or RetryPolicy()

        self.client = httpx.Client(
            base_url=self.base_url,
            transport=transport,
            timeout=5.0,
        )

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": (
                f"token "
                f"{self.credentials.api_key}:"
                f"{self.credentials.access_token}"
            ),
            "X-Idempotency-Key": "",
        }

    def close(self):
        self.client.close()

    def place_order(
        self,
        *,
        client_order_id: str,
        symbol: str,
        side: str,
        quantity: int,
        price: float,
    ) -> dict[str, Any]:

        headers = self._headers()
        headers["X-Idempotency-Key"] = client_order_id

        payload = {
            "client_order_id": client_order_id,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
        }

        last_error: Exception | None = None

        for attempt in range(
            1,
            self.retry_policy.max_attempts + 1,
        ):

            try:

                response = self.client.post(
                    "/orders",
                    json=payload,
                    headers=headers,
                )

                if response.status_code >= 500:
                    raise BrokerAPIError(
                        f"Broker server error: "
                        f"{response.status_code}"
                    )

                if response.status_code >= 400:
                    raise BrokerAPIError(
                        f"Broker rejected request: "
                        f"{response.status_code}"
                    )

                return response.json()

            except (
                httpx.TimeoutException,
                httpx.NetworkError,
                BrokerAPIError,
            ) as exc:

                last_error = exc

                if attempt >= self.retry_policy.max_attempts:
                    break

                time.sleep(
                    self.retry_policy.backoff_seconds
                    * attempt
                )

        raise BrokerAPIError(
            f"Order placement failed after "
            f"{self.retry_policy.max_attempts} attempts"
        ) from last_error

    def get_positions(self) -> dict[str, int]:

        response = self.client.get(
            "/positions",
            headers=self._headers(),
        )

        if response.status_code >= 400:
            raise BrokerAPIError(
                f"Position request failed: "
                f"{response.status_code}"
            )

        return response.json()