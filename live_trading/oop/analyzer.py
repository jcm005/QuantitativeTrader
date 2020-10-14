from pytz import timezone
import pytz
from datetime import datetime
import logging
import trader
import json
import spy
import pandas as pd

class Analyzer:
    """
    This class analyzes data in order to build candles and
    prepare data to be analyze for influencing the strategy factory for
    strategy decision.
    """

    def __init__(self):
        '''
        '''
        #self.__dict__ = self._params

        self.minutes_processed = {}
        self.minute_candlestick = []
        self.current_tick = None
        self.previous_tick = None
        self.in_position = False
        self.back_log = None
        self.est = timezone('US/Eastern')
        self.count = 1

        logging.basicConfig(level=logging.DEBUG,
                            filename='algorithm.log',
                            filemode='w',
                            # format=fmt
                            )

    @classmethod
    def sma(cls, data, window=10):
        '''
        Creates simple moving average
        :param data: must be an iterable
        :param int: desired rolling average window
        :return: will default an sma of window 10
        '''
        # Does not work if data is of the nonetype
        if len(data) >= window:
            rolling = sum(data[-window:]) / window
            return rolling
        else:
            return False

    def load(self,message, ticker):

        self.current_tick = json.loads(message)[0]
        if self.current_tick['ev'] == 'status':
            logging.info(self.current_tick)
            return False
        else:
            if self.current_tick['sym'] == ticker:
                return True
            elif self.current_tick['sym'] == 'SPY':
                try:
                    spy_500 = spy.Builder(self.current_tick)
                    self.spy_500 = spy_500.run()
                except:
                    logging.warning('Insert Data Methodology for Spy_500')
                return False


    def _candle_builder(self):

        self.time = trader.StreamTools.time_converter(self.current_tick['e'])
        self.volatility_data = self.current_tick['h'] - self.current_tick['l']
        self.hlmean = (self.current_tick['h'] + self.current_tick['l']) / 2
        self.v_factor = (self.volatility_data / self.hlmean) * 100
        self.ticker = self.current_tick['sym']
        self.minute_candlestick.append({
            'symbol': self.current_tick['sym'],
            'time': self.time,
            'open': self.current_tick['o'],
            'high': self.current_tick['h'],
            'low': self.current_tick['l'],
            'close': self.current_tick['c'],
            'hlmean': round(self.hlmean, ndigits=2),
            'volume': self.current_tick['v'],
            'today_volume': self.current_tick['av']/1000000,
            'volatility': round(self.volatility_data, ndigits=2),
            'v_factor': round(self.v_factor, ndigits=2),

        })
        print(self.minute_candlestick[-1])

    def _run_analytics(self):
        '''Processes candles and creates indicators and parameters'''

        # ------------------------------ BASICS ----------------------------
        self._high = [i['high'] for i in self.minute_candlestick]
        self._low = [i['low'] for i in self.minute_candlestick]
        self._v_factor = [i['v_factor'] for i in self.minute_candlestick]
        self._time = self.minute_candlestick[-1]['time']
        self._volume = self.minute_candlestick[-1]['volume']
        self._today_volume = self.minute_candlestick[-1]['today_volume'] / 1000000

        # ------------------------------ ROLLINGS ------------------------------
        try:
            self._market_open = self.current_tick['op']
            logging.info('self.marketopen %s ' % self._market_open)
        except:
            logging.warning('Market is not open yet, market_open price is now yesterday closing price.')

        if len(self.minute_candlestick) > 1:
            self.vp = self.minute_candlestick[-1]['v_factor'] - self.minute_candlestick[-2]['v_factor']
            logging.info('-- Time: %s, High: %s, Low: %s, Stream VP: %s, V/P Ratio: %s --'
                     % (self.time, self._high[-1], self._low[-1], round(self.vp, ndigits=3), self._v_factor[-1]))
            print('Time: %s, High: %s, Low: %s, Stream VP: %s, V/P Ratio: %s '
                  % (self.time, self._high[-1], self._low[-1], self.vp, self._v_factor[-1]))
        else:
            self.vp = False     # vp is the volatility buying parameter

        if len(self.minute_candlestick) >= 10:
            self.rolling_v_10 = self.sma(self._v_factor, window=10)
            self.rolling_high_10 = self.sma(self._high, window=10)
            if self.rolling_v_10 != False or self.rolling_high_10 != False:
                logging.info('Rolling_v_10 %s' % self.rolling_v_10)
                logging.info('Rolling_high_10 %s' % self.rolling_high_10)
        else:
            self.rolling_v_10, self.rolling_high_10 = False, False

        if len(self.minute_candlestick) >= 30:
            self.rolling_high_30 = self.sma(self._high, window=30)
            if self.rolling_high_30 != False or self.rolling_high_30 != None:
                logging.info('Rolling_high_30 %s' % self.rolling_high_30)
        else:
            self.rolling_high_30 = False
        return

    def _back_logger(self):
        """
        gains insight to market after hours and the result can be manipulated to have market opening orders ready
        over_night: returns:  list of candles from last night

        *** doesnt work over weekend yet ***

        """

        import alpaca_trade_api as tradeapi
        from keys import API__KEY, SECRET_KEY
        from datetime import datetime, timedelta
        time_interval = 'minute'
        self.over_night = []

        raw_past = timedelta(days=1)
        raw_now = datetime.now()
        yesterday = raw_now - raw_past
        start = datetime.strftime(yesterday, '%Y-%m-%d')
        final = datetime.strftime(raw_now, '%Y-%m-%d')
        api = tradeapi.REST(API__KEY, SECRET_KEY, api_version='v2')
        # for manually grabbing data and doing an analysis by hand or ipython file
        data = api.polygon.historic_agg_v2(self.ticker, 1, time_interval, start, final)
        spy_500 = api.polygon.historic_agg_v2('SPY', 1, time_interval, start, final)
        for bar in data:

            # catenuated the last few items from the time stamp
            # to removve errors unsure what this information provides
            _open = str(bar.open)
            _high = str(bar.high)
            _low = str(bar.low)
            _close = str(bar.close)
            _volume = str(int(bar.volume))

            x = str(bar.timestamp)
            hour = int(x[11:13])
            day = int(x[8:10])
            if day == int(start[-2:]):  # Checks if it is previous day or not
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
        self._market_open = float(self.over_night[-1]['high'])
        return self.over_night

# -------------------------------------------
    def _market_analyzer(self):

        self._percent_change = round(((self._high[-1] - self._market_open) / self._market_open) * 100, ndigits=3)
        print('percent change %s' % self._percent_change)

        p = {
            'high': self._high,
            'low': self._low,
            'market_open': self._market_open,
            'rolling_v_10': self.rolling_v_10,
            'rolling_high_10': self.rolling_high_10,
            'rolling_high_30': self.rolling_high_30,
            'vp': self.vp,
            'over_night' : self.over_night
        }
        p2 = {}
        return p
# -------------------------------------------

    def run(self):

        self._candle_builder()
        self._run_analytics()
        while self.count == 1:  # Runs once
            logging.info('-- Running Back Logs --')
            self._back_logger()
            self.count = 0
            logging.info('-- Yesterday Closing Price: %s --' % self._market_open)
            break
        self._market_analyzer()


# THIS MAY REPLACE MARKET ANALYZER
    # WILL HAVE TO CHANGE SOME THINGS IN THE __INIT__ IN STRAT FACTORY.

    def metrics(self):
        '''Exporting data for offline analysis and eventually SQL dumping/warehousing'''
        import pandas as pd
        columns = ['symbol',
                   'date', 'day', 'time',
                   'open',
                   'high',
                   'low',
                   'close',
                   'hlmean', 'volume',
                   'today_volume',
                   'volatility', 'v_factor',
                   'pct_change']

        self.df = pd.DataFrame(self.minute_candlestick,columns=columns)
        self.df['date'] = [i.split(',')[0] for i in self.df['time']]
        self.df['day'] = [i.split(',')[1] for i in self.df['time']]
        self.df['time'] = [i.split(',')[-1] for i in self.df['time']]
        self.df['pct_change'] = self._percent_change
        #self.df['corr_1'] = self.df.corr(self.df.volatility,self.df.volume)
        print(self.df.head())
        print(self.df.corr())

#obsolete i believe
    def data_frame_prep(self, data, parameter='data_name'):
        '''rewrites a dataframe to be easuly manipulatible and uploading fors sql'''
        __slots__ = ['day', 'time']
        if parameter in __slots__:
            return [i for i in data[parameter]]
        elif parameter == 'symbol':
            return (data[parameter][0]).split(':')[1]
        elif parameter == 'date':
            return [(i.split(':')[1]) for i in data[parameter]]
        elif parameter == 'v_factor':
            v_factor = [i.strip('}') for i in data[parameter]]
            return [float(i.split(':')[1]) for i in v_factor]
        else:
            return [float(i.split(':')[1]) for i in data[parameter]]

