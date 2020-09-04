from order2 import Order
from pytz import timezone
import pytz
from datetime import datetime

class QuantTrader():

    def __init__(self,ticker,price,profit,log_file=None):
        '''price has to be an iterable type'''
        self.price = price
        self.ticker = ticker
        self.log = log_file
        self.over_night =[]
        self.profit = profit

    def buy_order(self,
                  order_type,
                  qty,
                  tif,
                  order_class=None,
                  stop_price=None,
                  limit_price=None,
                  stop_limit_price=None):

        symbol = Order(self.ticker, self.price[-1])
        order = symbol.buy(order_type=order_type,
                           order_class=order_class,
                           qty=qty,
                           tif=tif,
                           profit=self.profit,
                           limit_price=limit_price,
                           stop_price=stop_price,
                           stop_limit_price=stop_limit_price)
        return order

    def Back_logger(self):
        '''
        gains insight to market after hours and the result can be manipulated to have market opening orders ready
        over_night: returns:  list of candles from last night

        *** doesnt work over weekend yet ***

        '''

        import alpaca_trade_api as tradeapi
        from keys import API__KEY,SECRET_KEY
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

    def Back_log_volatility(self,data):
        if len(data) > 2:
            last_night = (data[0])
            this_morn = (data[-1])
            if int(this_morn['high'].split('.')[0]) - int(last_night['high'].split('.')[0]) >= 25:
                symbol = Order(self.ticker,self.price[-1])
                order_back_log = symbol.buy(order_type='market',order_class='oto',
                                      qty=1, tif='gtc',profit=self.profit)
                return order_back_log
            else:
                return False

    def Sma(self,data,int=10):
        '''
        Creates simple moving average
        :param data: must be an iterable
        :param int: desired rolling average window
        :return: will default an sma of window 10
        '''
        try:
            if len(data) >= int:
                self.sma = sum(data[-int:])/int
                return self.sma
                print(f'Rolling_{int} = {self.sma}')
            else:
                pass
        except:
            return False

    def Climb_the_ladder(self,qty=1):
        '''
        When the simple moving average of
        30 is a percentage over the high price
        '''
        symbol = Order(self.ticker,self.price[-1])
        self.sma_30 = self.Sma(self.price,int=30)
        if (self.price[-1] - self.sma_30) > (self.price[-1]*0.0125):
            return True
        else:
            return False

    def Stop_drop_and_roll(self,qty=1):
        symbol = Order(self.ticker,self.price[-1])
        self.sma_10 = self.Sma(self.price,int=10)
        if (self.sma_10 - self.price[-1]) > (self.sma_10*.025):
            order_SDR = symbol.buy(order_class='oto', order_type='market',
                                 qty=qty, tif='gtc', profit=self.profit)
            return order_SDR
        else:
            return False

    def Volatility(self,volatility,qty=1,parameter=1):
        if volatility > parameter:
            return True
        else:
            return False

    def Price_jump(self,qty=1):
        symbol = Order(self.ticker,self.price[-1])
        self.sma_30 = self.Sma(self.price,int=30)
        if (self.price[-1] - self.sma_30) > (self.price[-1]*.02):
            order_stand_alone = symbol.buy(order_class='bracket', order_type='market',
                                         qty=qty, tif='gtc',
                                         profit=self.profit,
                                         stop_limit_price=self.price[-1] - (self.profit / 2),
                                         stop_price=self.price[-1] - (self.profit / 2.1))
            return order_stand_alone
        else:
            pass

    def double_trouble(self,vola_data,qty=1,parameter=1):
        self.vola = vola_data
        self.Sma(self.vola_data,int=10)
        pass


    def buy_order(self,ref):

        symbol = Order(self.ticker, self.price[-1])

        # turn this into a dictionary eventually

        if ref == 'sma1':
            order = symbol.buy(order_type='market', order_class='oto',
                               qty=qty, tif='gtc', profit=self.profit)
            return order
        elif ref == 'ctl':
            order = symbol.buy(order_class='bracket',order_type='market',
                             qty=qty,tif='gtc',
                             profit=self.profit,
                             stop_limit_price=self.price[-1] - (self.profit/2),
                             stop_price=self.price[-1] - (self.profit/2.25)
                               )
            return order
        elif ref == 'sdr':
            order = symbol.buy(order_class='oto', order_type='market',
                                 qty=qty, tif='gtc', profit=self.profit)
            return order
        elif ref == 'pj':
            order = 'PJ Not supported yet'
            return order
        elif ref == 'dt':
            order = symbol.buy(order_class='oto',order_type='market',
                                        qty=1, tif='gtc', profit=profit,
                                        stop_limit_price=_high- (profit /2),
                                        stop_price= _high - (profit/ 2.25))
            return order
        elif ref == 'sma1ws':
            order = symbol.buy(order_type='market', order_class='oto',
                               qty=qty, tif='gtc', profit=self.profit)
            return order
        elif ref == 'ctlws':
            order = symbol.buy(order_class='bracket', order_type='market',
                               qty=qty, tif='gtc',
                               profit=self.profit,
                               stop_limit_price=self.price[-1] - (self.profit / 2),
                               stop_price=self.price[-1] - (self.profit / 2.25)
                               )
            return order
        elif ref == 'sdrws':
            order = symbol.buy(order_class='oto', order_type='market',
                               qty=qty, tif='gtc', profit=self.profit)
            return order
        elif ref == 'pjws':
            order = 'PJ Not supported yet'
            return order
        elif ref == 'dtws':
            order = symbol.buy(order_class='oto', order_type='market',
                               qty=1, tif='gtc', profit=profit,
                               stop_limit_price=_high - (profit / 2),
                               stop_price=_high - (profit / 2.25))
            return order


class StreamTrader():
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

        self.action = open('action2.txt','a')
        self.candles = open('candle2.txt','a')
        self.log_on = open('log_on2.txt','a')
        self.order = open('order2.txt','a')

    # CLEAR OUT FILES

        self.candles.truncate(0)
        self.action.truncate(50)
        self.order.truncate(0)

    def log(self,txt):

        self.action.write(f'{txt}\n')
      #  self.action.close()
        return

    def order_log(self,txt):

        self.order.write(f'{txt}\n')
        #self.order.close()

    def candle_log(self,txt):

        self.candles.write(f'{txt}\n')
        #self.candles.close()
        return

    def connection_log(self,txt):

        self.log_on.write(f'{txt}\n')
        #self.log_on.close()
        return

    def close_logs(self):
        self.log_on.close()
        self.candles.close()
        self.order.close()
        self.action.close()

    def time_converter(self,some_time):
        newtime = datetime.fromtimestamp(some_time / 1000)
        newtimes = newtime.strftime('%Y-%m-%d, %a, %H:%M')
        return newtimes

    def localize_time(self):

        self.right_now = pytz.utc.localize(datetime.utcnow()).astimezone(self.est)
        self.right_now = datetime.strftime(self.right_now, '%H:%M:%S')
        return self.right_now

    def candle_builder(self):

        self.time = self.time_converter(self.current_tick['e'])
        self.volatility_data = self.current_tick['h'] - self.current_tick['l']
        self.hlmean = (self.current_tick['h'] + self.current_tick['l']) / 2
        self.v_factor = (self.volatility_data / self.hlmean) * 100

        self.minute_candlestick.append({
            'symbol':self.current_tick['sym'],
            'time': self.current_tick['time'],
            'open': self.current_tick['o'],
            'high': self.current_tick['h'],
            'low': self.current_tick['l'],
            'close': self.current_tick['c'],
            'hlmean': round(self.hlmean, ndigits=2),
            'volatilty': round(self.volatility_data, ndigits=2),
            'v_factor': round(self.v_factor, ndigits=2),
        })

        latest_candle = self.minute_candlestick[-1]
        return latest_candle

    def profit_tree(self,price):
        if 3000 > price >= 1000:
            profit = 100
        elif 1000 > price > 850:
            profit = 80
        elif 850 >= price > 600:
            profit = 65
        elif 600 >= price > 400:
            profit = 40
        elif 400 >= price:
            profit = 30

        return profit




if __name__ == '__main__':

    test = StreamTrader()
    right_now = test.localize_time()
    test.connection_log('right now %s' % (right_now[:2]))
    print(test.current_tick)
    test.candle_builder()