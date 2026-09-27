import httpx

from trading.phone_alerts import (
    AlertMessage,
    AlertRouter,
    ConsoleAlertChannel,
    TelegramAlertChannel,
)


def test_console_alert():

    result = ConsoleAlertChannel().send(
        AlertMessage(
            "TEST",
            "Engine healthy",
        )
    )

    assert result


def test_alert_router():

    router = AlertRouter(
        channels=[
            ConsoleAlertChannel()
        ]
    )

    assert router.send(
        "TEST",
        "Everything OK",
    )


def test_telegram_alert():

    def handler(request):

        return httpx.Response(
            200,
            json={
                "ok": True
            },
        )

    client = httpx.Client(
        transport=httpx.MockTransport(
            handler
        )
    )

    channel = TelegramAlertChannel(
        "TEST_TOKEN",
        "TEST_CHAT",
        client=client,
    )

    result = channel.send(
        AlertMessage(
            "TEST",
            "Engine alert",
        )
    )

    assert result

    channel.close()