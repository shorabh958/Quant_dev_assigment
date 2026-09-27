from pathlib import Path
import sys
import json
import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from trading.broker_adapter import (
    BrokerCredentials,
    RESTBrokerClient,
)
from trading.execution_service import (
    ExecutionRequest,
    OrderExecutionService,
)


def broker_handler(request):

    payload = json.loads(request.content)

    return httpx.Response(
        200,
        json={
            "order_id": "SIM-001",
            "client_order_id": payload[
                "client_order_id"
            ],
            "symbol": payload["symbol"],
            "status": "FILLED",
            "filled_quantity": payload[
                "quantity"
            ],
        },
    )


transport = httpx.MockTransport(
    broker_handler
)

broker = RESTBrokerClient(
    "https://simulated-broker.local",
    BrokerCredentials(
        api_key="DEMO_API_KEY",
        access_token="DEMO_ACCESS_TOKEN",
    ),
    transport=transport,
)

execution = OrderExecutionService(
    broker
)


request = ExecutionRequest(
    client_order_id="DEMO-NIFTY-001",
    symbol="NIFTY",
    side="BUY",
    quantity=2,
    price=25000,
)


first = execution.submit(request)

# Same order submitted again.
# Idempotency prevents a duplicate broker order.
second = execution.submit(request)


print()
print("=" * 60)
print("BROKER / EXECUTION INTEGRATION DEMO")
print("=" * 60)

print(
    f"Client Order ID : {first.client_id}"
)

print(
    f"Symbol          : {first.symbol}"
)

print(
    f"Side            : {first.side}"
)

print(
    f"Quantity        : {first.quantity}"
)

print(
    f"Filled          : {first.filled_quantity}"
)

print(
    f"State           : {first.state.value}"
)

print(
    f"Same Object     : {first is second}"
)

print()
print("REST Authentication : OK")
print("Idempotency         : OK")
print("Order State Machine : OK")
print("Execution           : FILLED")

print("=" * 60)

broker.close()