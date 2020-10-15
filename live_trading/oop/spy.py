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
        print(self.candles[-1])


    def run(self):

        self._high = [i['high'] for i in self.candles]
        self._low = [i['low'] for i in self.candles]
        self._time = self.time

        if self._market_open:
            self.percent_change = round(((self._high[-1] - self._market_open) / self._market_open) * 100 ,ndigits=3)
            logging.info('SPY_500: PCT_CHANGE: %s' % self.percent_change)
            print('SPY_500: PCT_CHANGE %s' % self.percent_change)
        else:
            self.percent_change = False
            print('Market Is Not Open Yet')

        p = {
            'Time': self.time,
            'high':self._high,
            'low':self._low,
            'market_open':self._market_open,
            'pct_change': self.percent_change,
        }

        return p


if __name__ == '__main__':
    pass