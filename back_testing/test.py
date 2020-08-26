import pandas as pd
from volatility import *

import backtrader as bt
import backtrader.feeds as btfeeds
from data_grabber import *

asset = ['TSLA']
start_date = '2020-07-13'           # ticker symbols to be tested
time_interval = 'minute'            # collect data per each ---
time_delt = 1
time_period =1

def strat_runner(asset,strat_name, cash=10000.0,test=False ):

    cerebro = bt.Cerebro()
    cerebro.addstrategy(strat_name)
    for symbol in asset:
        path =  f'{symbol}_{time_interval}_intraday_trading.csv'
        data  = btfeeds.GenericCSVData(
            dataname=f'Data/{path}',
            nullvalue=0.0,
            dtformat= '%Y-%m-%d %H:%M:%S',
            tmformat='%H:%M:%S',
            datetime=0,
            high=2,
            low=3,
            time=-1,
            open=1,
            close=4,
            volume=5,
            openinterest=-1)
        for i in data:
            print(i)

        cerebro.adddata(data)

    cerebro.broker.set_cash(cash)
    cerebro.broker.setcommission(commission=0.001)

    print('Starting Cash Amount Is %.2f' % cerebro.broker.get_cash())
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Final portfolio: %.2f' % cerebro.broker.getvalue())
    print('Final Cash Amount Is %.2f' % cerebro.broker.get_cash())

    cerebro.plot(iplot=False)

    if test:
       # Skipps the logging process if test mode is of
        logger()

    data_flusher(asset, time_interval)
def logger():
    anss  = input('Do you want to log this information: y/n ? \n')
    if anss == 'y':
        log__ = open('log.txt','a')
        log__.write(f'Assets: {asset},Start Date: {start_date},Time interval: {time_interval},Time Period: {time_period},Time Delt: {time_delt}\n')
    else:
        pass

#===============================
#===============================
class SummerHaus05042020(bt.Strategy):
    params = dict(
        pfast = 10,
        pslow = 30
    )
    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''


        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
    def __init__(self):
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.bar_executed = 0
        self.bought = []
        self.temporary = 0
        self.transactions = []

        self.dataclose = self.datas[0].close
        self.high = self.datas[0].high
        self.low = self.datas[0].low
        self.succesful = []
        self.failure = []
        self.opened =[]

        self.volatility = (self.high - self.low)
        self.hlmean = (self.high + self.low) / 2
        self.vole_coeff = (self.volatility / self.hlmean) * 100
        self.sma_1 = bt.indicators.MovingAverageSimple(self.vole_coeff,
                                                        plotname='SMA_1',
                                                        subplot=True,
                                                        period=1)

        self.sma_5 = bt.indicators.MovingAverageSimple(self.vole_coeff,
                                                     plotname='SMA_5',
                                                       subplot=True,
                                                     period=5)
        self.sma_10 = bt.indicators.MovingAverageSimple(self.vole_coeff,
                                                     plotname='SMA_10',
                                                     subplot=True,
                                                     period=10)
        self.sma_20 = bt.indicators.MovingAverageSimple(self.vole_coeff,
                                                        plotname='SMA_20',
                                                        subplot=False,
                                                        period=100)

        rolling_1 = bt.ind.SMA(period=self.p.pfast,subplot=True)
        rolling_2 = bt.ind.SMA(period=self.p.pslow,subplot=True)
        self.crossover = bt.ind.CrossOver(rolling_1,self.high[0])



    def next(self):

        def volatility(self, variable, num, ref):
            """compares the current volatility with the previous volatitlty and takes in a reference number
             the number given is the condition for volatility"""
            if (variable[0] - variable[1]) >= num:
                self.log(f'Volatility Condition >= {num}; Satisfied! Ref#:{ref}')
                return True
            else:
                return False
        def tesla(self):

            if not self.position:

                if self.high[0] <900:
                    if volatility(self,self.sma_1,1,1):
                        self.log('Buy attempt :: ref -- (#1) < 900 %.2f, sma[0] :%.2f, sma[-1] :%.2f' % (self.high[0],self.sma_1[0],self.sma_1[-1]))
                        self.order = self.buy(size=1, price=self.high[0])

                if self.high[0] > 900:
                    if volatility(self,self.sma_1,1,1):
                        self.log('Buy attempt :: ref -- (##### > 900 ')
                        self.order = self.buy(size=1, price=self.high[0])
                if self.sma_10[0] > 3:
                    self.log('Buying for sma 10')
                    self.order = self.buy(price=self.high[0])
            if self.position:

                if len(self.bought) > 5:
                    pass
                for i in self.bought:
                    if self.sma_10[0] > 3:
                        print('SMA 10 ---> ')
                        self.log(f'Buying for sma 10 {self.high[0]}')
                        self.order = self.buy(price=self.high[0])
                    if i < 500:
                        if i < 300:
        #SELL COMMAND FOR LESS THEN 300
                            if (self.high[-1] - i) > 20:
                                self.log('SELL CREATE < 200 , %.2f' % self.dataclose[0])
                                self.order = self.sell()
                                self.bought.remove(i)
        #BUY COMMAND FOR LESS THAN 300

                            if (self.sma_1[0] - self.sma_1[-2]) > 1:
                                self.log('Buy attempt :: ref -- (#2) < 800 %.2f' % self.high[0])
                                self.order = self.buy(size=1, price=self.high[0])

            #------------------------------------------------------------------::
        #BUY COMMAND FOR LESS THEN 500
                        else:
                            if (i - self.high[-1]) > 80: # greater then 300
                                self.log('Buy attempted with possesion > 300 already  %.2f' % self.high[0])
                                self.order = self.buy(size=1, price=(i - self.high[-1]))
        #SELL COMMAND FOR LESS THEN 500
            # IF PRICE DIFFERS BY 50 THEN BUY
                            if (self.high[0] - i ) > 50:
                                self.log('SELL CREATE < 500 , %.2f' % self.dataclose[0])
                                self.order = self.sell()
                                self.bought.remove(i)
                        #------------------------------------------------------------------::
        #IF I IS GREATER THEN 500
                    elif i > 500:
                #IF VOLATILITY DIFFERENCE IS GREATER THEN 1.5
                        if (self.sma_10[0] - self.sma_10[-2]) > 1.5:
                            # THE STOCK IS SO VOLATILE THAT I WILL BUY SHARE EXTREMELY LOW BECAUSE ITS MOVING

                            if (i - self.high[-1]) > 200:
                                #BUY IF A THE HIGH IS 200 LOWER THEN AN ALREADY OBTAINED POSITION
                                self.log('THE MARKET IS VERY VOLATILE --BUY--  %.2f' % self.high[0])
                                self.order = self.buy()
                        #------------------------------------------------------------------::

        # BUY COMMAND FOR GREATER THAN 500
                        if (i - self.high[-1]) > 100:
                            #self.log('Buy attempted with possesion  > 500 already  %.2f' % self.high[0])
                            self.order = self.buy()

    # SELL COMMAND FOR GREATER THAN 500
                    if (self.high[0] - i) > 100:
                        #print(f'High: {self.high[0]}, i-value: {i}')
                        self.log('SELL CREATE:: REF -- (#3), High: %.2f, i : %.2f' % (self.dataclose[0],i))
                        self.order = self.sell(size=1,price=(self.high[0]))
                        self.bought.remove(i)

                    if self.high[0] > 900:
                        if (self.sma_1[0] - self.sma_1[-1]) > 1:
                            self.log('Buy attempt ~ ref > 900)')
                            self.order = self.buy(size=1, price=self.high[0])

        def mod_tesla(self):
            ''' 37% return '''
        # NO POSITION
            if not self.position:

                # enter momentum thing here with ties to volatility

                if self.high[0] < 900:
                    if self.sma_10[0] >=.5:
                        self.log(f'Lower 900 -- High: {self.high[0]} sma_10: {self.sma_10[0]}')
                        self.order = self.buy()
                    if self.sma_1[0] - self.sma_1[-1] >= 1:
                        self.log(f'Lower 900 -- High: {self.high[0]} sma_1: {self.sma_1[0]-self.sma_1[-1]}')
                        self.order = self.buy()
                else:
                    # -- BUY --
                    if self.sma_10[0] >= .5:
                        self.log(f'sma_10  -- High: {self.high[0]} sma_10: {self.sma_10[0]}')
                        self.order = self.buy()
                    if self.sma_1[0] - self.sma_1[-1] >= 1:
                        self.log(f'higher 900 -- High: {self.high[0]} sma_1: {self.sma_1[0]-self.sma_1[-1]}')
                        self.order = self.buy()
                    # -- SELL --

        # WITH POSITION
            else:
                for i in self.bought:
                    if i > 1000:
                        if self.high[0] - i >= 120:
                            self.log(f'Selling --120 -- High: {self.high[0]} profit: {self.high[0] -i}')
                            self.order = self.sell()
                            self.bought.remove(i)
                    if 1000> i > 700:
                        if self.high[0] - i >= 100:
                            self.log(f'Selling --100 -- High: {self.high[0]} profit: {self.high[0] -i}')
                            self.order = self.sell()
                            self.bought.remove(i)
                    if 700> i > 500:
                        if self.high[0] - i >= 80:
                            self.log(f'Selling-- 80 -- High: {self.high[0]} profit: {self.high[0] -i}')
                            self.order = self.sell()
                            self.bought.remove(i)
                    if 500> i > 350:
                        if self.high[0] - i >= 50:
                            self.log(f'Selling-- 50 -- High: {self.high[0]} profit: {self.high[0] -i}')
                            self.order = self.sell()
                            self.bought.remove(i)
                    if 350 > i:
                        if self.high[0] - i >= 30:
                            self.log(f'Selling-- 30 -- High: {self.high[0]} profit: {self.high[0] -i}')
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
        def mod_tesla_2(self):
            if not self.position:
                # enter momentum thing here with ties to volatility
                if self.sma_10[0] >= .5:
                    self.log(f'Lower 900 -- High: {self.high[0]} sma_10: {self.sma_10[0]}')
                    self.order = self.buy()
                if self.sma_1[0] - self.sma_1[-1] >= 1:
                    self.log(f'Lower 900 -- High: {self.high[0]} sma_1: {self.sma_1[0] - self.sma_1[-1]}')
                    self.order = self.buy()

                #TO RISKY
              #  if self.crossover > 0:
               #     self.log(f'crossover')
               #     self.order = self.buy()

            # with position
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
                    self.log(f'P-ROLLING -- High: {self.high[0]} sma_10: {self.sma_10[0]}')
                    self.order = self.buy()
                if self.sma_1[0] - self.sma_1[-1] >= 1:
                    self.log(f'P-VOLATILTIY -- High: {self.high[0]} sma_1: {self.sma_1[0] - self.sma_1[-1]}')
                    self.order = self.buy()

                if self.high[-5] - self.high[0] > 50:
                    self.log('BIG PRICE DROP')
                    self.order = self.buy()

               # if self.crossover < 0:
                #    self.log(f'crossover')
                 #   self.order = self.sell()


       # mod_tesla(self)
        mod_tesla_2(self)
    def notify_order(self, order):

        self.trade_info = {
            'Successful_trades': len(self.succesful),
            'Opened': len(self.bought),
        }

        if order.status in [order.Submitted, order.Accepted]:
            return
        # order fcan be rejected if not enough cash is present
        if order.status in [order.Completed]:
            if order.isbuy():

                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f \n' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                self.bought.append(self.buyprice)
                print(f'Opened shares: {self.bought}')

                # print(self.position)
            elif order.issell():
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
                self.sellprice = order.executed.price

                self.succesful.append(self.sellprice)
                print(f'Opened shares: {self.bought}\n')

            self.bar_executed = len(self)



        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            # self.log('order canceled/margin/rejected')
            # self.failure.append(order.status)
            pass
                #  self.order = self.sell()
    def notify_trade(self, trade):
        if trade.isclosed:
            self.log('Operation Profit::, Gross %.2f, Net %.2f' % (trade.pnl, trade.pnlcomm))
            self.transactions.append(trade.pnl)
            print(self.trade_info)
            print(f'Opened shares: {self.bought}')
            print(self.position)


if __name__ == '__main__':
    data_flusher(asset, time_interval) # here in case program fails it will not double data
    Acummator(asset,start_date,time_interval,time_delt,time_period)
    strat_runner(asset,SummerHaus05042020,100000,test=False)
