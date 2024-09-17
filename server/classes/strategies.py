from classes.base import Strategy
from indicators import SMAIndicator

class MeanReversionStrategy(Strategy):
    def execute(self, data):
        indicator = SMAIndicator('SMA', {'period': 20})
        sma = indicator.calculate(data['price'])
        # Strategy logic here
