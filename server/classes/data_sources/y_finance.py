import yfinance as yf
from classes.data_sources.base import RESTDataSource

class YFinanceDataSource(RESTDataSource):
    def __init__(self, name, symbol):
        super().__init__(name, f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}")
        self.symbol = symbol

    async def fetch_data(self):
        # Use yfinance to fetch data instead of making a direct API call
        ticker = yf.Ticker(self.symbol)
        data = ticker.history(period="1d")
        return data.to_dict(orient="records")[0]  # Return the latest day's data

    async def check_health(self):
        try:
            ticker = yf.Ticker(self.symbol)
            ticker.info  # This will raise an exception if the symbol is invalid
            return True
        except:
            return False