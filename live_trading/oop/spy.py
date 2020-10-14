import trader
import logging



class Builder:

    def __init__(self, message):

        self.current_tick = message
        self.candles = []
        self.time = trader.StreamTools.time_converter(self.current_tick['e'])

        try:
            self._market_open = self.current_tick['op']
        except:
            self._market_open = False

        self.candles.append({
            'symbol': self.current_tick['sym'],
            'time': self.time,
            'open': self.current_tick['o'],
            'high': self.current_tick['h'],
            'low': self.current_tick['l'],
            'close': self.current_tick['c'],
            'market_open':self._market_open
        })

    def run(self):
        """
        Synonymos to cnadle builder
        :return:
        """
        self._high = [i['high'] for i in self.candles]
        if self._market_open:
            self.percent_change = round(((self._high[-1] - self._market_open) / self._market_open) * 100 ,ndigits=3)

            print(self.percent_change)
        return None


if __name__ == '__main__':

    pass