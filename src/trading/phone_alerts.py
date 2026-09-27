from __future__ import annotations

from dataclasses import dataclass
import httpx


@dataclass(frozen=True)
class AlertMessage:
    title: str
    message: str
    severity: str = "INFO"


class AlertChannel:
    def send(self, alert: AlertMessage) -> bool:
        raise NotImplementedError


class ConsoleAlertChannel(AlertChannel):

    def send(self, alert: AlertMessage) -> bool:
        print(
            f"[ALERT][{alert.severity}] "
            f"{alert.title}: {alert.message}"
        )
        return True


class TelegramAlertChannel(AlertChannel):

    def __init__(
        self,
        bot_token: str,
        chat_id: str,
        client=None,
    ):
        self.bot_token = bot_token
        self.chat_id = chat_id

        self.client = client or httpx.Client(
            timeout=5.0
        )

    def send(self, alert: AlertMessage) -> bool:

        url = (
            "https://api.telegram.org/"
            f"bot{self.bot_token}/sendMessage"
        )

        payload = {
            "chat_id": self.chat_id,
            "text": (
                f"[{alert.severity}] "
                f"{alert.title}\n"
                f"{alert.message}"
            ),
        }

        response = self.client.post(
            url,
            json=payload,
        )

        if response.status_code >= 400:
            return False

        return True

    def close(self):
        self.client.close()


class AlertRouter:

    def __init__(
        self,
        channels=None,
    ):
        self.channels = channels or [
            ConsoleAlertChannel()
        ]

    def send(
        self,
        title: str,
        message: str,
        severity: str = "INFO",
    ):

        alert = AlertMessage(
            title=title,
            message=message,
            severity=severity,
        )

        results = []

        for channel in self.channels:
            try:
                results.append(
                    channel.send(alert)
                )
            except Exception:
                results.append(False)

        return all(results)