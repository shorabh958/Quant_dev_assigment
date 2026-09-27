import logging


class AlertManager:
    def __init__(self):
        self.logger = logging.getLogger("quant.alerts")

    def alert(self, message: str):
        self.logger.warning("TRADING ALERT: %s", message)

    def position_limit(self, symbol: str):
        self.alert(f"Position limit reached: {symbol}")

    def connection_lost(self):
        self.alert("Market-data connection lost")

    def circuit_breaker(self):
        self.alert("CIRCUIT BREAKER TRIGGERED")