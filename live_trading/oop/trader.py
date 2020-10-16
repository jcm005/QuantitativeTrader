from order import Order
from pytz import timezone
import pytz
from datetime import datetime
import analyzer
import logging
import notification_sys
import pandas as pd

#  QUANT TRADER WILL PROBABLY BE USING THE LOGGING FUNCTOIN FROM STREAM TRADER
#   AS WELL AS INDICATORS MADE BY STREAM TRADER
#    SO IN FUNCTION IN QT MAYBE MAKE AN INSTANCE -- NO THIS WONT WORK ALL INFO WILL BE SEPERATE
# INSTEAD LETS MAKE QUNAT TRADER A CHILD CLASS WITH DECORATOR OR CLASS
# METHODS OR STATIC METHODS FURTHER RESEARCH NEEDED TO BE DON HERE

class QuantTrader:

    def __init__(self,price, ticker):
        """
        price has to be an iterable type
        """
       # Analzyer.__init__(self)
        self.price = price
        self.ticker = ticker
        self.over_night = []
        self.sma = analyzer.Analyzer.sma
        try:
            if 3000 > self.price >= 1000:
                self.profit = 100
            elif 1000 > self.price > 850:
                self.profit = 80
            elif 850 >= self.price > 600:
                self.profit = 40
            elif 600 >= self.price > 400:
                self.profit = 30
            elif 400 >= self.price:
                self.profit = 20

        except:
            pass

    def buy_order(self, ref, qty):
        symbol = Order(self.ticker, self.price[-1])
        if ref == 'sma1':
            order = symbol.buy(order_type='market', order_class='oto',
                               qty=qty, tif='gtc', profit=self.profit)
           # self.order_log('Order: %s \n %s' % (ref, order))
            return order
        elif ref == 'ctl':
            order = symbol.buy(order_class='bracket', order_type='market',
                               qty=qty, tif='gtc',
                               profit=self.profit,
                               stop_limit_price=self.price[-1] - (self.profit / 2),
                               stop_price=self.price[-1] - (self.profit / 2.25)
                               )
           # self.order_log('Order: %s \n %s' % (ref, order))
            return order
        elif ref == 'sdr':
            order = symbol.buy(order_class='oto', order_type='market',
                               qty=qty, tif='gtc', profit=self.profit)

           # self.order_log('Order: %s \n %s' % (ref, order))
            return order
        elif ref == 'pj':
            order = symbol.buy(order_class='bracket', order_type='market',
                               qty=qty, tif='day',
                               profit=self.profit,
                               stop_limit_price=self.price[-1] - (self.profit / 4),
                               stop_price=self.price[-1] - (self.profit / 4.25)
                               )

            return order
        elif ref == 'dt':
            order = symbol.buy(order_class='oto', order_type='market',
                               qty=1, tif='gtc', profit=profit,
                               stop_limit_price=_high - (profit / 2),
                               stop_price=_high - (profit / 2.25))
         #   self.order_log('Order: %s \n %s' % (ref, order))
            return order
        elif ref == 'sma1ws':
            order = symbol.buy(order_type='market', order_class='oto',
                               qty=qty, tif='gtc', profit=self.profit)
          #  self.order_log('Order: %s \n %s' % (ref, order))
            return order
        elif ref == 'ctlws':
            order = symbol.buy(order_class='bracket', order_type='market',
                               qty=qty, tif='gtc',
                               profit=self.profit,
                               stop_limit_price=self.price[-1] - (self.profit / 2),
                               stop_price=self.price[-1] - (self.profit / 2.25)
                               )
         #   self.order_log('Order: %s \n %s' % (ref, order))
            return order
        elif ref == 'sdrws':
            order = symbol.buy(order_class='bracket', order_type='market',
                               qty=qty, tif='gtc',
                               profit=self.profit,
                               stop_limit_price=self.price[-1] - (self.profit / 4),
                               stop_price=self.price[-1] - (self.profit / 4.25)
                               )

            return order
        elif ref == 'pjws':
            order = 'PJ Not supported yet'
         #   self.order_log('Order: %s \n %s' % (ref, order))
            return order
        elif ref == 'dtws':
            order = symbol.buy(order_class='oto', order_type='market',
                               qty=1, tif='gtc', profit=profit,
                               stop_limit_price=_high - (profit / 2),
                               stop_price=_high - (profit / 2.25))
        #    self.order_log('Order: %s \n %s' % (ref, order))
            return order

# Back log doesnt belong here
# own module
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

        logging.info('Trying ctl')
        self.sma_30 = self.sma(self.price, window=30)
        if self.sma_30 != False:
            threshold = (self.price[-1] * 0.0125)
            logging.info('Threshold: %s' % (threshold) )
            if (self.price[-1] - self.sma_30) > (threshold):
                logging.info('Climbing The Ladder Satisfied')
                order = self.buy_order(ref, qty)
                notification_sys.create_message('Sending Order %s' % order)

                return order
            else:
                logging.info('CTL Lower than Threshold')

                return False

        else:
            logging.info('Need more candles to work with')
            return False

    def stop_drop_and_roll(self, ref, qty=1):
        '''If the price is dropping quicker then rolling 10 can catch up it will buy'''

        self.sma_10 = self.sma(self.price, window=10)
        if self.sma_10 != False:
            threshold = (self.sma_10 * 0.025)
            logging.info('Threshold: %s' % threshold)
            if (self.sma_10 - self.price[-1]) > (threshold):
                logging.info('Stop Drop and Roll Satisfied')
                order = self.buy_order(ref, qty)

                notification_sys.create_message('Sending Order %s' % order)
                return order
            else:
                logging.info('SDR Lower Than Threshold')
                return False
        else:
            logging.info('Need more candles to work with')
            return False

    def Volatility(self, volatility, ref='sma1', qty=1, parameter=1):
        '''Given a parameter this function equates indicators for a volatility by
        influenced by the sma1 buy'''
        if volatility > parameter:
            logging.info('Volatility Order Satisfied')
            order = self.buy_order(ref, qty)
            notification_sys.create_message('Sending Order %s' % order)

            return order
        else:
            pass

    def price_jump(self, ref, qty=1):
        '''If the current price jumps over sma_30 threshold buy'''
        self.sma_30 = self.sma(self.price, window=30)
        if self.sma_30 != False:
            if (self.price[-1] - self.sma_30) > (self.price[-1] * .02):
                logging.info('Price Jump Satisfied')
                order = self.buy_order(ref, qty)

                notification_sys.create_message('Sending Order %s' % order)
                return order
            else:
                logging.info('Price Jump Not Satisfied')
                return
        else:
            return

    def double_trouble(self, param1, param2, qty=1):
        if param1 > 1 and param2 > .5:
            logging.info('Double Standard Satisfied')
            order = self.buy_order(ref='dt', qty=qty)
            return order
        else:
            logging.info('Double Trouble Not Satisfied')
            return


class StreamTools:
    """
    Tools for the stream
    """

    @classmethod
    def time_converter(cls, some_time):
        """
        Convert date time object to a string
        """
        newtime = datetime.fromtimestamp(some_time / 1000)
        newtimes = newtime.strftime('%Y-%m-%d, %a, %H:%M')
        return newtimes

    @classmethod
    def check_time(cls):
        tz =timezone('US/Eastern')
        right_now = pytz.utc.localize(datetime.utcnow()).astimezone(tz)
        right_now = datetime.strftime(right_now, '%H:%M:%S')
        if int(right_now[0:2]) >= 16 or int(right_now[0:2]) <= 9:
            extended_hours = True
        else:
            extended_hours = False
        print(f'Extended hours are: {extended_hours}')
        return extended_hours

    def localize_time(self):
        """Default set to eastern time, when runnign on a virtual machine timezone may be off"""
        right_now = pytz.utc.localize(datetime.utcnow()).astimezone(self.est)
        right_now = datetime.strftime(right_now, '%H:%M:%S')

        return right_now

    @classmethod
    def export_pd(cls, data=pd.DataFrame()):

        date = cls.localize_time(StreamTools())
        data.to_csv(path='metrics.txt' + date )


if __name__ == '__main__':


    #qt = QuantTrader('TSLA')
    #qt.back_logger()

    data = pd.DataFrame()
    StreamTools.export_pd(data)
