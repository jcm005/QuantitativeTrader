from order import Order
from pytz import timezone
import pytz
from datetime import datetime


#  QUANT TRADER WILL PROBABLY BE USING THE LOGGING FUNCTOIN FROM STREAM TRADER
#   AS WELL AS INDICATORS MADE BY STREAM TRADER
#    SO IN FUNCTION IN QT MAYBE MAKE AN INSTANCE -- NO THIS WONT WORK ALL INFO WILL BE SEPERATE
# INSTEAD LETS MAKE QUNAT TRADER A CHILD CLASS WITH DECORATOR OR CLASS METHODS OR STATIC METHODS FURTHER RESEARCH NEEDED TO BE DON HERE
class QuantTrader():

    def __init__(self, ticker, price, profit, log_file=None):
        '''price has to be an iterable type'''
        self.price = price
        self.ticker = ticker
        self.log = log_file
        self.over_night = []
        self.profit = profit
        self.log = StreamTrader.log
        self.order_log = StreamTrader.order_log

    def __repr__(self):
        return 'QuantTrader ticker=%s' % (self.ticker)

    def buy_order(self, ref, qty):
        symbol = Order(self.ticker, self.price[-1])
        if ref == 'sma1':
            order = symbol.buy(order_class='bracket', order_type='market',
                               qty=qty, tif='gtc',
                               profit=self.profit,
                               stop_limit_price=self.price[-1] - (self.profit / 2),
                               stop_price=self.price[-1] - (self.profit / 2.25)
                               )
            self.order_log('Order: %s \n %s' % (ref, order))
            return order
        elif ref == 'ctl':
            order = symbol.buy(order_class='bracket', order_type='market',
                               qty=qty, tif='gtc',
                               profit=self.profit,
                               stop_limit_price=self.price[-1] - (self.profit / 2),
                               stop_price=self.price[-1] - (self.profit / 2.25)
                               )
            self.order_log('Order: %s \n %s' % (ref, order))
            return order
        elif ref == 'sdr':
            order = symbol.buy(order_class='oto', order_type='market',
                               qty=qty, tif='gtc', profit=self.profit)

            self.order_log('Order: %s \n %s' % (ref, order))
            return order
        elif ref == 'pj':
            order = 'PJ Not supported yet'

            order_log('Order: %s \n %s' % (ref, order))
            return order
        elif ref == 'dt':
            order = symbol.buy(order_class='oto', order_type='market',
                               qty=1, tif='gtc', profit=profit,
                               stop_limit_price=_high - (profit / 2),
                               stop_price=_high - (profit / 2.25))
            self.order_log('Order: %s \n %s' % (ref, order))
            return order
        elif ref == 'sma1ws':
            order = symbol.buy(order_class='bracket', order_type='market',
                               qty=qty, tif='gtc',
                               profit=self.profit,
                               stop_limit_price=self.price[-1] - (self.profit / 2),
                               stop_price=self.price[-1] - (self.profit / 2.25)
                               )
            self.order_log('Order: %s \n %s' % (ref, order))
            return order
        elif ref == 'ctlws':
            order = symbol.buy(order_class='bracket', order_type='market',
                               qty=qty, tif='gtc',
                               profit=self.profit,
                               stop_limit_price=self.price[-1] - (self.profit / 2),
                               stop_price=self.price[-1] - (self.profit / 2.25)
                               )
            self.order_log('Order: %s \n %s' % (ref, order))
            return order
        elif ref == 'sdrws':
            order = symbol.buy(order_class='oto', order_type='market',
                               qty=qty, tif='gtc', profit=self.profit)

            order_log('Order: %s \n %s' % (ref, order))
            return order
        elif ref == 'pjws':
            order = 'PJ Not supported yet'
            self.order_log('Order: %s \n %s' % (ref, order))
            return order
        elif ref == 'dtws':
            order = symbol.buy(order_class='oto', order_type='market',
                               qty=1, tif='gtc', profit=profit,
                               stop_limit_price=_high - (profit / 2),
                               stop_price=_high - (profit / 2.25))
            self.order_log('Order: %s \n %s' % (ref, order))
            return order

    def Back_logger(self):
        """
        gains insight to market after hours and the result can be manipulated to have market opening orders ready
        over_night: returns:  list of candles from last night

        *** doesnt work over weekend yet ***

        """

        import alpaca_trade_api as tradeapi
        from keys import API__KEY, SECRET_KEY
        from datetime import datetime, timedelta
        time_interval = 'minute'

        raw_past = timedelta(days=1)
        raw_now = datetime.now()
        yesterday = raw_now - raw_past
        start = datetime.strftime(yesterday, '%Y-%m-%d')
        final = datetime.strftime(raw_now, '%Y-%m-%d')
        api = tradeapi.REST(API__KEY, SECRET_KEY, api_version='v2')
        # for manually grabbing data and doing an analysis by hand or ipython file
        data = api.polygon.historic_agg_v2(self.ticker, 1, time_interval, start, final)
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
        return self.over_night

    def Back_log_volatility(self, data):
        '''Checks if over night data is a go for a market opening buy'''
        if len(data) > 2:
            last_night = (data[0])
            this_morn = (data[-1])
            if int(this_morn['high'].split('.')[0]) - int(last_night['high'].split('.')[0]) >= 25:
                symbol = Order(self.ticker, self.price[-1])
                order_back_log = symbol.buy(order_type='market', order_class='oto',
                                            qty=1, tif='gtc', profit=self.profit)
                return order_back_log
            else:
                return False

    @classmethod
    def Sma(cls, data, int=10):
        '''
        Creates simple moving average
        :param data: must be an iterable
        :param int: desired rolling average window
        :return: will default an sma of window 10
        '''

        if len(data) >= int:
            cls.sma = sum(data[-int:]) / int
            return cls.sma
            print(f'Rolling_{int} = {cls.sma}')
        else:
            return False

    # ----------------------------------------------------------------------
    #  ___ Strategies___

    # all these strategies just need to be called once called if the following
    # conditions are met they will execute a buy with appropiate logging
    # ----------------------------------------------------------------------


    def climb_the_ladder(self, ref, qty=1):

        '''
        If the price difference between sma_30 and high is above a threshold buy

        :param ref: Reference for the buy order
        :param qty: Qty of shares desired
        :return: Order or None is not successful
        '''

        self.log('Trying ctl')
        self.sma_30 = self.Sma(self.price, int=30)
        if self.sma_30 != False:
            threshold = (self.price[-1] * 0.0125)
            self.log('Threshold: %s' % (threshold) )
            if (self.price[-1] - self.sma_30) > (threshold):
                self.log('Climbing The Ladder Satisfied')
                order = self.buy_order(ref, qty)
                return order
            else:
                self.log('CTL Lower than Threshold')
                pass
        else:
            self.log('Need more candles to work with')

    def stop_drop_and_roll(self, ref, qty=1):
        '''If the price is dropping quicker then rolling 10 can catch up it will buy'''

        self.sma_10 = self.Sma(self.price, int=10)
        if self.sma_10 != False:
            threshold = (self.sma_10 * 0.025)
            self.log('Threshold: %s' % threshold)
            if (self.sma_10 - self.price[-1]) > (threshold):
                self.log('Stop Drop and Roll Satisfied')
                order = self.buy_order(ref, qty)
                return order
            else:
                self.log('SDR Lower Than Threshold')
                pass
        else:
            self.log('Need more candles to work with')

    def Volatility(self, volatility, ref, qty=1, parameter=1):
        '''Given a parameter this function equates indicators for a volatility by
        influenced by the sma1 buy'''
        if volatility > parameter:
            self.log('Volatility Order Satisfied')
            order = self.buy_order(ref, qty)
            return order
        else:
            pass

    def price_jump(self, ref, qty=1):
        '''If the current price jumps over sma_30 threshold buy'''
        self.sma_30 = self.Sma(self.price, int=30)
        if (self.price[-1] - self.sma_30) > (self.price[-1] * .02):
            self.log('Price Jump Satisfied')
            order = self.buy_order(ref, qty)
            return order
        else:
            self.log('Price Jump Not Satisfied')
            return

    def double_trouble(self, param1, param2, qty=1):
        if param1 > 1 and param2 > .5:
            self.log('Double Standard Satisfied')
            order = self.buy_order(ref='dt', qty=qty)
            return order
        else:
            self.log('Double Trouble Not Satisfied')
            return


# ===============================================================================
# ===============================================================================
# ===============================================================================
# ===============================================================================
# ===============================================================================

class StreamTrader:
    def __init__(self):
        '''
        '''
        self.minutes_processed = {}
        self.minute_candlestick = []
        self.current_tick = None
        self.previous_tick = None
        self.in_position = False
        self.back_log = None
        self.est = timezone('US/Eastern')

        self.action = open('action.txt', 'a')
        self.candles = open('candle.txt', 'a')
        self.log_on = open('log_on.txt', 'a')
        self.order = open('order.txt', 'a')

    def __str__(self):
        return 'A Framework for trading with data streamed from polygon io'

    def __repr__(self):
        pass

    # -------------  Log Functions  ----------------

    @classmethod
    def log(cls, txt):
        cls.action = open('action.txt', 'a')
        cls.action.write(f'{txt}\n')
        cls.action.close()
        return

    @classmethod
    def order_log(cls, txt):
        cls.order = open('order.txt', 'a')
        cls.order.write(f'{txt}\n')
        cls.order.close()

    def candle_log(self, txt):
        self.candles = open('candle.txt', 'a')
        self.candles.write(f'{txt}\n')
        self.candles.close()
        return

    def connection_log(self, txt):
        self.log_on = open('log_on.txt', 'a')
        self.log_on.write(f'{txt}\n')
        self.log_on.close()

    def log_scrubber(self):

        self.candles.truncate(0)
        self.action.truncate(50)
        self.order.truncate(0)
        print('Initiating Logs')

    def close_logs(self):
        self.log_on.close()
        self.candles.close()
        self.order.close()
        self.action.close()

    def reopen(self, file):
        if file == self.action:
            opened_file = open('action2.txt', 'a')
            return opened_file
        elif file == self.log_on:
            opened_file = open('log_on2.txt', 'a')
            return opened_file

    # ---------------  Proccesing   -----------------------

    def time_converter(self, some_time):
        '''Convert date time object to a string'''
        newtime = datetime.fromtimestamp(some_time / 1000)
        newtimes = newtime.strftime('%Y-%m-%d, %a, %H:%M')
        return newtimes

    def localize_time(self):
        '''Default set to eastern time, when runnign on a virtual machine timezone may be off'''
        self.right_now = pytz.utc.localize(datetime.utcnow()).astimezone(self.est)
        self.right_now = datetime.strftime(self.right_now, '%H:%M:%S')

        return self.right_now

    def run_analytics(self):
        '''Processes candles and creates indicators and parameters'''
        # we may  be able to avoid this with decorator

        self._high = [i['high'] for i in self.minute_candlestick]
        self._low = [i['low'] for i in self.minute_candlestick]
        self._v_factor = [i['v_factor'] for i in self.minute_candlestick]
        self.time = self.latest_candle['time']
        self.profit = self.profit_tree(self._high[-1])

        # This is what is passed for the volatility buy
        if len(self.minute_candlestick) > 1:
            self.vp = self.minute_candlestick[-1]['v_factor'] - self.minute_candlestick[-2]['v_factor']
            self.log('Time: %s, High: %s, Low: %s, Stream VP: %s, V/P Ratio: %s '
                     % (self.time, self._high[-1], self._low[-1], round(self.vp,ndigits=3), self._v_factor[-1]))
            print('Time: %s, High: %s, Low: %s, Stream VP: %s, V/P Ratio: %s '
                  % (self.time, self._high[-1], self._low[-1], self.vp, self._v_factor[-1]))

        if len(self.minute_candlestick) >= 10:
            self.rolling_v_10 = QuantTrader.Sma(self._v_factor, int=10)
            self.rolling_high_10 = QuantTrader.Sma(self._high, int=10)
            if self.rolling_v_10 != False or self.rolling_high_10 != False:
                self.log('Rolling_v_10 %s' % self.rolling_v_10)
                self.log('Rolling_high_10 %s' % self.rolling_high_10)
        else:
            self.rolling_v_10, self.rolling_high_10 = None, None

        if len(self.minute_candlestick) >= 30:
            self.rolling_high_30 = QuantTrader.Sma(self._high, int=30)
            if self.rolling_high_30 != False or self.rolling_high_30 != None:
                self.log('Rolling_high_30 %s' % self.rolling_high_30)
        else:
            self.rolling_high_30 = None
        return

    def candle_builder(self):

        # Handles errors in the stream data
        if self.current_tick['ev'] == 'status':
            self.log(self.current_tick)
            self.connection_log(self.current_tick)
            return

        # Specific Attributes to Include in Candle
        self.time = self.time_converter(self.current_tick['e'])
        self.volatility_data = self.current_tick['h'] - self.current_tick['l']
        self.hlmean = (self.current_tick['h'] + self.current_tick['l']) / 2
        self.v_factor = (self.volatility_data / self.hlmean) * 100

        # Build Candle
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

        # Analytics
        self.latest_candle = self.minute_candlestick[-1]
        self.candle_log(self.latest_candle)
        self.log('--- Running Analytics ---')
        self.run_analytics()
        return self.latest_candle

    def profit_tree(self, price):
        '''Passing the current price here will dictate the appropiate take profit price for the buy order'''
        if 3000 > price >= 1000:
            profit = 100
        elif 1000 > price > 850:
            profit = 80
        elif 850 >= price > 600:
            profit = 30
        elif 600 >= price > 400:
            profit = 20
        elif 400 >= price:
            profit = 15

        return profit

    def metrics(self):
        '''Exporting data for offline analysis and eventually SQL dumping/warehousing'''
        import pandas as pd
        columns = ['symbol', 'date', 'day', 'time', 'open', 'high', 'low', 'close', 'hlmean', 'volume', 'today_volume',
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


if __name__ == '__main__':
    order_log = StreamTrader.order_log

# Test for sma
    #sma = QuantTrader.Sma([i for i in range(0,11)],int=10)
    #print(sma)

# Test for STD

   # qt =  QuantTrader('TSLA',price=[i for i in range(0,31)],profit=10)
   # qt.climb_the_ladder(ref='ctlws')

    price  = 400
    qt = QuantTrader('TSLA',price=price,profit=StreamTrader().profit_tree(price))

    back_log = qt.Back_logger()
    print(back_log)