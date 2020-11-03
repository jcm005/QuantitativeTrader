import logging
import alpaca_trade_api as tradeapi
from keys import *
from datetime import datetime, timedelta

class BackLog:

    """
    an object that can be used in analysis.py for the
    grabbing of after hour data for additional indicators
    """

    def __init__(self, ticker):

        logging.info('-- Back Logging --')
        self.ticker = ticker
        self.time_interval = 'minute'
        self.over_night = []
        self.spy_over_night = []
        self.raw_past = timedelta(days=1)
        self.raw_now = datetime.now()
        self.yesterday = self.raw_now - self.raw_past
        self.start = datetime.strftime(self.yesterday, '%Y-%m-%d')
        self.final = datetime.strftime(self.raw_now, '%Y-%m-%d')
        self.api = tradeapi.REST(API__KEY, SECRET_KEY, api_version='v2')

    def request_data(self):

        self.data = self.api.polygon.historic_agg_v2(self.ticker, 1, self.time_interval, self.start, self.final)
        self.spy_500 = self.api.polygon.historic_agg_v2('SPY', 1, self.time_interval, self.start, self.final)

    def decipher(self):


        for bar in self.data:
            _open = str(bar.open)
            _high = str(bar.high)
            _low = str(bar.low)
            _close = str(bar.close)
            _volume = str(int(bar.volume))
            x = str(bar.timestamp)
            hour = int(x[11:13])
            day = int(x[8:10])

            if day == int(self.start[-2:]):  # Checks if it is previous day or not
                if hour >= 16:
                    time = x[:19]
                    self.over_night.append({
                        'time': time,
                        'high': _high,
                    })
            else:
                if hour <= 7:
                    time2 = x[:19]
                    self.over_night.append({
                        'time': time2,
                        'high': _high,
                    })

        logging.info('-- Overnight data --> %s --' % len(self.over_night))

    def analyze(self):

        if self.over_night:

            self.premarket = self.over_night[-1]['high']
            logging.info('-- Pre market Price: %s --' % self.premarket)
        else:
            self.over_night = False
            self.premarket = False

        self.p = {
            'premarket': self.premarket,
            'overnight': self.over_night
        }

        return self.p

    def run(self):

        self.request_data()
        self.decipher()
        self.analyze()
        return self.p


if __name__ == '__main__':
    pass

