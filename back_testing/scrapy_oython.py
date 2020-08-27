from keys import *
over_night = []

def volatility(self,variable,num,ref):
    """compares the current volatility with the previous volatitlty and takes in a reference number
     the number given is the condition for volatility"""
    if (variable[0] - variable[1]) >= num:
        self.log(f'Volatility Condition >= {num};Satisfied Ref{ref}')
        return true
    else:
        return false


def mod_tesla(self):
    ''' 37% return '''
    # NO POSITION
    if not self.position:

        # enter momentum thing here with ties to volatility

        if self.high[0] < 900:
            if self.sma_10[0] >= .5:
                self.log(f'Lower 900 -- High: {self.high[0]} sma_10: {self.sma_10[0]}')
                self.order = self.buy()
            if self.sma_1[0] - self.sma_1[-1] >= 1:
                self.log(f'Lower 900 -- High: {self.high[0]} sma_1: {self.sma_1[0] - self.sma_1[-1]}')
                self.order = self.buy()
        else:
            # -- BUY --
            if self.sma_10[0] >= .5:
                self.log(f'sma_10  -- High: {self.high[0]} sma_10: {self.sma_10[0]}')
                self.order = self.buy()
            if self.sma_1[0] - self.sma_1[-1] >= 1:
                self.log(f'higher 900 -- High: {self.high[0]} sma_1: {self.sma_1[0] - self.sma_1[-1]}')
                self.order = self.buy()
            # -- SELL --

    # WITH POSITION
    else:
        for i in self.bought:
            if i > 1000:
                if self.high[0] - i >= 120:
                    self.log(f'Selling --120 -- High: {self.high[0]} profit: {self.high[0] - i}')
                    self.order = self.sell()
                    self.bought.remove(i)
            if 1000 > i > 700:
                if self.high[0] - i >= 100:
                    self.log(f'Selling --100 -- High: {self.high[0]} profit: {self.high[0] - i}')
                    self.order = self.sell()
                    self.bought.remove(i)
            if 700 > i > 500:
                if self.high[0] - i >= 80:
                    self.log(f'Selling-- 80 -- High: {self.high[0]} profit: {self.high[0] - i}')
                    self.order = self.sell()
                    self.bought.remove(i)
            if 500 > i > 350:
                if self.high[0] - i >= 50:
                    self.log(f'Selling-- 50 -- High: {self.high[0]} profit: {self.high[0] - i}')
                    self.order = self.sell()
                    self.bought.remove(i)
            if 350 > i:
                if self.high[0] - i >= 30:
                    self.log(f'Selling-- 30 -- High: {self.high[0]} profit: {self.high[0] - i}')
                    self.order = self.sell()
                    self.bought.remove(i)

            if i - self.high[0] > 120:
                self.log(f'CLEARANCE 120 --: {self.high[0]} i: {i}')
                self.order = self.buy()

        if self.sma_10[0] >= .5:
            self.log(f'sma_10 900 -- High: {self.high[0]} sma_10: {self.sma_10[0]}')
            self.order = self.buy()
        if self.sma_1[0] - self.sma_1[-1] >= 1:
            self.log(f'higher 900 -- High: {self.high[0]} sma_1: {self.sma_1[0] - self.sma_1[-1]}')
            self.order = self.buy()




def back_logger(ticker, time_interval='minute'):
    """Retrieves historical data based on passed values of the polygon api

        asset:  pass in your desired ticker symbols
        time_interval =  defaulted to day --> minute, hour,day,month,year
        start and end date in the format 'yyyy-mm-dd'

    """
    import alpaca_trade_api as tradeapi
    from datetime import datetime,timedelta
    raw_past = timedelta(days=1)
    raw_now  = datetime.now()
    yesterday = raw_now - raw_past
    start = datetime.strftime(yesterday,'%Y-%m-%d')
    final = datetime.strftime(raw_now,'%Y-%m-%d')
    api = tradeapi.REST(API_KEY, SECRET_KEY, api_version='v2')
    # for manually grabbing data and doing an analysis by hand or ipython file
    data = api.polygon.historic_agg_v2(ticker, 1, time_interval,start, final)


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
        if day == int(start[-2:]):
            if hour >= 16:
                time = x[:19]
                over_night.append({
                    'time': time,
                    'high': _high,
                })
        else:
            if hour <= 7:
                time2 = x[:19]
                over_night.append({
                    'time': time2,
                    'high' : _high,
                })


    return over_night


if __name__ == '__main__':

    over_night = back_logger('TSLA')
    print(len(over_night))
    print(over_night[0])
    print(over_night[-1])
