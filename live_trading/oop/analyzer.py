from pytz import timezone
import pytz
from datetime import datetime
import logging
import trader
import json

class Analyzer:

    _params = {}

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

    def load(self,message):
        self.current_tick = json.loads(message)[0]

    def _candle_builder(self):

        self.time = trader.StreamTools.time_converter(self.current_tick['e'])
        self.volatility_data = self.current_tick['h'] - self.current_tick['l']
        self.hlmean = (self.current_tick['h'] + self.current_tick['l']) / 2
        self.v_factor = (self.volatility_data / self.hlmean) * 100

        self.minute_candlestick.append({
            'symbol': self.current_tick['sym'],
            'time': self.time,
            'open': self.current_tick['o'],
            'high': self.current_tick['h'],
            'low': self.current_tick['l'],
            'close': self.current_tick['c'],
            'hlmean': round(self.hlmean, ndigits=2),
            'volume': self.current_tick['v'],
            'today_volume': self.current_tick['av'],
            'volatilty': round(self.volatility_data, ndigits=2),
            'v_factor': round(self.v_factor, ndigits=2),

        })
       # logging.info(self.minute_candlestick[-1])
        print(self.minute_candlestick[-1])

    def _run_analytics(self):
        '''Processes candles and creates indicators and parameters'''

        logging.info('-- Running Analytcis -- ')

        # we may  be able to avoid this with decorator
        self._high = [i['high'] for i in self.minute_candlestick]
        self._low = [i['low'] for i in self.minute_candlestick]
        self._v_factor = [i['v_factor'] for i in self.minute_candlestick]
        self._time = self.minute_candlestick[-1]['time']

        # This is what is passed for the volatility buy
        if len(self.minute_candlestick) > 1:
            self.vp = self.minute_candlestick[-1]['v_factor'] - self.minute_candlestick[-2]['v_factor']
            logging.info('Time: %s, High: %s, Low: %s, Stream VP: %s, V/P Ratio: %s '
                     % (self.time, self._high[-1], self._low[-1], round(self.vp, ndigits=3), self._v_factor[-1]))
            print('Time: %s, High: %s, Low: %s, Stream VP: %s, V/P Ratio: %s '
                  % (self.time, self._high[-1], self._low[-1], self.vp, self._v_factor[-1]))

        if len(self.minute_candlestick) >= 10:
            self.rolling_v_10 = self.sma(self._v_factor, window=10)
            self.rolling_high_10 = self.sma(self._high, window=10)
            if self.rolling_v_10 != False or self.rolling_high_10 != False:
                logging.info('Rolling_v_10 %s' % self.rolling_v_10)
                logging.info('Rolling_high_10 %s' % self.rolling_high_10)
        else:
            self.rolling_v_10, self.rolling_high_10 = None, None

        if len(self.minute_candlestick) >= 30:
            self.rolling_high_30 = self.sma(self._high, window=30)
            if self.rolling_high_30 != False or self.rolling_high_30 != None:
                logging.info('Rolling_high_30 %s' % self.rolling_high_30)
        else:
            self.rolling_high_30 = None

        return

    def run(self):

        if self.current_tick['ev'] == 'status':
            logging.info(self.current_tick)
            return
        self._candle_builder()
        self._run_analytics()

    def metrics(self):
        '''Exporting data for offline analysis and eventually SQL dumping/warehousing'''
        import pandas as pd
        columns = ['symbol', 'date', 'day', 'time', 'open', 'high', 'low', 'close', 'hlmean', 'volume',
                   'today_volume',
                   'volatility', 'v_factor']
        self.df = pd.read_csv('candle2.txt', names=columns)

        for i in columns:
            self.df[i] = self.data_frame_prep(self.df, parameter=i)
        self.df.to_csv('metrics.txt', mode='w')

        # save the data we can do correlation else where

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

