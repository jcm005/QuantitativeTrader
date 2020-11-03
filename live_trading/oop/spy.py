import trader
import logging
import stream_tools


class Builder:

    def __init__(self, message):

        self.current_tick = message
        self.candles = []

        try:
            self.time = stream_tools.StreamTools.time_converter(self.current_tick['e'])
        except:
            logging.warning('StreamTool Instantiation Error, Check For Proper Import')

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
        Prepares the parameters to be sent into strat factory

        :return:
        """

        self._high = [i['high'] for i in self.candles]
        self._low = [i['low'] for i in self.candles]
        self._time = self.time

        if self._market_open:
            self.percent_change = round(((self._high[-1] - self._market_open) / self._market_open) * 100 ,ndigits=3)
            logging.info('SPY_500: PCT_CHANGE: %s' % self.percent_change)
        else:
            self.percent_change = round(((self._high[-1] - self._low[0]) / self._low[0]) * 100 ,ndigits=3)
            print('Market Is Not Open Yet')


        p = {
            'Time': self.time,                  # just time
            'high':self._high,                  # This is a list
            'low':self._low,                    # This is a list
            'market_open':self._market_open,    # single value
            'pct_change': self.percent_change,  # single value
        }
        return p


if __name__ == '__main__':
    pass