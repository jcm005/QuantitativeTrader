from pytz import timezone
import pytz
from datetime import datetime
import logging
import trader
import json
import spy
import pandas as pd
import back_logger as bl
import stream_tools

class Analyzer:
    """
    This class analyzes data in order to build candles and
    prepare data to be analyze for influencing the strategy factory for
    strategy decision.
    """

    def __init__(self):

        self._minute_candlestick = []
        self._current_tick = None
        self._previous_tick = None
        self._back_log = None
        self.est = timezone('US/Eastern')
        self.count = 1
        self._market_open = False
        self.spy = False
        self.spy_500 = None


        self.spy_percent_change_history = []
        self.ticker_percent_change_history = []

        logging.basicConfig(level=logging.DEBUG,
                            filename='algorithm.log',
                            filemode='w',
                            # format=fmt
                            )

    @classmethod
    def sma(cls, data, window=10):
        """
        Creates simple moving average
        :param window:
        :param data: must be an iterable
        :return: will default an sma of window 10
        """
        try:
            if len(data) >= window:
                rolling = sum(data[-window:]) / window
                return rolling
            else:
                return False

        except TypeError:
            return 'Data type is None'

    def load(self,message, ticker):
        """
        This method checks what type of
        incoming message is recieved then redirects it in teh right direction
        :param message:
        :param ticker:
        :return:
        """
        self._current_tick = json.loads(message)[0]
        if self._current_tick['ev'] == 'status':
            logging.info(self._current_tick)
            return False
        else:
            if self._current_tick['sym'] == ticker:
                return True
            elif self._current_tick['sym'] == 'SPY':
                try:
                    self.spy_500 = spy.Builder(self._current_tick).run()
                    #self.spy_percent_change_history.append(self.spy_500['pct_change'])
                    self.spy = True
                except:
                    logging.warning(self._current_tick)
                    logging.warning('Spy Builder Failure/Insert Methodology for SPY_500')
                return False

    def _candle_builder(self):

        self.time = stream_tools.StreamTools.time_converter(self._current_tick['e'])
        self.volatility_data = self._current_tick['h'] - self._current_tick['l']
        self.hlmean = (self._current_tick['h'] + self._current_tick['l']) / 2
        self.v_factor = (self.volatility_data / self.hlmean) * 100
        self.ticker = self._current_tick['sym']

        self._minute_candlestick.append({
            'symbol': self._current_tick['sym'],
            'time': self.time,
            'open': self._current_tick['o'],
            'high': self._current_tick['h'],
            'low': self._current_tick['l'],
            'close': self._current_tick['c'],
            'hlmean': round(self.hlmean, ndigits=2),
            'volume': self._current_tick['v'],
            'today_volume': self._current_tick['av']/1000000,
            'volatility': round(self.volatility_data, ndigits=2),
            'v_factor': round(self.v_factor, ndigits=2),
        })
        print(self._minute_candlestick[-1])

    def _run_analytics(self):
        '''Processes candles and creates indicators and parameters'''

        # ------------------------------ BASICS ----------------------------
        self._high = [i['high'] for i in self._minute_candlestick]
        self._low = [i['low'] for i in self._minute_candlestick]
        self._v_factor = [i['v_factor'] for i in self._minute_candlestick]
        self._time = self._minute_candlestick[-1]['time']
        self._volume = self._minute_candlestick[-1]['volume']
        self._today_volume = self._minute_candlestick[-1]['today_volume'] / 1000000

        logging.info('Time: %s' % self._time)

        # ------------------------------ ROLLINGS ------------------------------
        try:
            self._market_open = self._current_tick['op']
        except:
            logging.warning('Market is not open yet, market_open price is now premarket price.')
        try:
            self._percent_change = round(((self._high[-1] - self._market_open) / self._market_open) * 100, ndigits=3)
            self.ticker_percent_change_history.append(self._percent_change)
        except:
            logging.warning('Percent change')

        try:
            self.spy_percent_change_history.append(self.spy_500['pct_change'])
        except:
            logging.warning('SPY_PCT_CHANGE')

        if len(self._minute_candlestick) > 1:
            self.vp = self._minute_candlestick[-1]['v_factor'] - self._minute_candlestick[-2]['v_factor']
            logging.info('-- Time: %s, High: %s, Low: %s, Stream VP: %s, V/P Ratio: %s --'
                     % (self.time, self._high[-1], self._low[-1], round(self.vp, ndigits=3), self._v_factor[-1]))
            print('Time: %s, High: %s, Low: %s, Stream VP: %s, V/P Ratio: %s '
                  % (self.time, self._high[-1], self._low[-1], self.vp, self._v_factor[-1]))
        else:
            self.vp = False

        if len(self._minute_candlestick) >= 10:
            self.rolling_v_10 = self.sma(self._v_factor, window=10)
            self.rolling_high_10 = self.sma(self._high, window=10)
            if self.rolling_v_10 != False or self.rolling_high_10 != False:
                logging.info('Rolling_v_10 %s' % self.rolling_v_10)
                logging.info('Rolling_high_10 %s' % self.rolling_high_10)
        else:
            self.rolling_v_10, self.rolling_high_10 = False, False

        if len(self._minute_candlestick) >= 30:
            self.rolling_high_30 = self.sma(self._high, window=30)
            if self.rolling_high_30 != False or self.rolling_high_30 != None:
                logging.info('Rolling_high_30 %s' % self.rolling_high_30)
        else:
            self.rolling_high_30 = False
        return

    def _market_analyzer(self):

        p = {
            'high': self._high,
            'low': self._low,
            'market_open': self._market_open,
            'rolling_v_10': self.rolling_v_10,
            'rolling_high_10': self.rolling_high_10,
            'rolling_high_30': self.rolling_high_30,
            'vp': self.vp,
            'over_night' : self.over_night_params,
            'ticker_pct_change': self.ticker_percent_change_history,
        }
        try:
            p['spy_market_pct_change'] = self.spy_percent_change_history
        except:
            pass

        return p

    def run(self):

        # if this runs first expect a missing SPY data not ready yet message.
        self._candle_builder()
        self._run_analytics() # try market open here if none then we get it in backlog

        while self.count == 1:  # Runs once
            self.over_night_params = bl.BackLog(self.ticker).run()
            if self._market_open == False:
                self._market_open = float(self.over_night_params['premarket'])
                self._percent_change = round(((self._high[-1] - self._market_open) / self._market_open) * 100,
                                             ndigits=3)
                self.ticker_percent_change_history.append(self._percent_change)
                print(self._market_open, self.ticker_percent_change_history)

            logging.info('-- %s market open %s --' % (self.ticker, self._market_open))
            self.count = 0
            break

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
                   'pct_change',
                   ]

        self.df = pd.DataFrame(self._minute_candlestick,columns=columns)
        self.df['date'] = [i.split(',')[0] for i in self.df['time']]
        self.df['day'] = [i.split(',')[1] for i in self.df['time']]
        self.df['time'] = [i.split(',')[-1] for i in self.df['time']]

        tpl = len(self.ticker_percent_change_history)
        spl = len(self.spy_percent_change_history)

        if len(self.df.time) == len(self.ticker_percent_change_history):
            self.df['pct_change'] = [i for i in self.ticker_percent_change_history]

        if self.spy:
            try:
                self.df['spy_pct_change'] = [i for i in self.spy_percent_change_history]
                print('try loop')
            except ValueError:
                self.spy_percent_change_history.append(0)

                self.df['spy_pct_change'] = [i for i in self.spy_percent_change_history]
                print(self.df['spy_pct_change'])
            except:
                print(self.df['spy_pct_change'])
                pass
            if spl == tpl and spl > 1:
                self.df_corr_2 = self.df[['pct_change', 'spy_pct_change']].corr()['pct_change']['spy_pct_change']
                self.df['pct_corr'] = self.df_corr_2
                print(self.df_corr_2,'PCT_CORR')
                logging.info('Pct_Corr: %s' % self.df_corr_2)
        else:
            while len(self.spy_percent_change_history) < 1:
                self.spy_percent_change_history.append(0)
                self.df['spy_pct_change'] = [i for i in self.spy_percent_change_history]
                print('while loop')

                break

        # ----------------------------------------------------------
        print('spl',spl, 'tpl', tpl, 'time', len(self.df.time))

        if tpl > 0:
            self.df_corr_1 = self.df[['volume', 'volatility']].corr()['volume']['volatility']
            self.df['volume:volatility'] = self.df_corr_1
            print(self.df_corr_1, 'Volume Corr')
            logging.info('Volume Corr: %s' % self.df_corr_1)

        #print(self.df)
        return self.df

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


if __name__ == '__main__':


    # These must be kept clean because this is ran when imported
   #back_log = bl.BackLog('TSLA')
   #back_log.main()

    #b = stream_tools.StreamTools.time_converter(1536036818784)
    #print(b)
   # message = [{"ev":"AM","sym":"TSLA","v":35177,"av":15407555,"op":446.24,"vw":438.9615,"o":438.72,"c":438.91,"h":439.2199,"l":438.72,"a":441.0544,"z":43,"n":1,"s":1603121220000,"e":1603121280000}]
   # ticker = 'TSLA'
   # dp = Analyzer().load()

    pass

