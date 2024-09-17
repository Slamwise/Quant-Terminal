from classes.base import Indicator

class SMAIndicator(Indicator):
    def calculate(self, data):
        period = self.parameters.get('period', 14)
        return data.rolling(window=period).mean()
