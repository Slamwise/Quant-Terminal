import asyncio
import yfinance as yf
from classes.base import DataSource

class YFinanceDataSource(DataSource):
    def __init__(self, name, symbol):
        super().__init__(name)
        self.symbol = symbol

    async def fetch_data(self):
        # Since yfinance doesn't support async, run in executor
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, self._fetch_sync_data)
        return data

    def _fetch_sync_data(self):
        ticker = yf.Ticker(self.symbol)
        data = ticker.history(period="1d")
        return data.to_dict(orient="records")[0]

    async def check_health(self):
        try:
            ticker = yf.Ticker(self.symbol)
            return bool(ticker.info)
        except Exception:
            return False