from order2 import Order

class QuantTrader():

    def __init__(self,ticker,price,profit,log_file=None):
        '''price has to be an iterable type'''
        self.price = price
        self.ticker = ticker
        self.log = log_file
        self.over_night =[]
        self.profit = profit

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
            order_ctl = symbol.buy(order_class='bracket',order_type='market',
                                             qty=qty,tif='gtc',
                                             profit=self.profit,
                                             stop_limit_price=self.price[-1] - (self.profit/2),
                                             stop_price=self.price[-1] - (self.profit/2.25))
            return order_ctl
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
            symbol = Order(self.ticker,self.price[-1])
            order_1 = symbol.buy(order_type='market', order_class='oto',
                               qty=qty, tif='gtc', profit=self.profit)
            return order_1
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


if __name__ == '__main__':

    price = []
    for i in range(0,475):
        price.append(i)

    if 3000 > price[-1] >= 1000:
        profit = 100
    elif 1000 > price[-1] > 850:
        profit = 80
    elif 850 >= price[-1] > 600:
        profit = 65
    elif 600 >= price[-1] > 400:
        profit = 40
    elif 400 >= price[-1]:
        profit = 30
    tesla = QuantTrader('TSLA',price,profit)
    over_night = tesla.Back_logger()
    back_log = tesla.Back_log_volatility(over_night)
    print(back_log)