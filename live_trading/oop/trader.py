from order import Order
from pytz import timezone
import pytz
from datetime import datetime
import analyzer
import logging
import notification_sys
import pandas as pd


class QuantTrader:

    def __init__(self,price, ticker):
        """
        price has to be an iterable type
        """

        self.high = price[-1]      # value
        self.price = price          # list
        self.ticker = ticker
        self.over_night = []
        self.sma = analyzer.Analyzer.sma

# --------------------------------------------------
        # OrderFactory
        if 3000 > self.high >= 1000:
            self.profit = 100
        elif 1000 > self.high > 850:
            self.profit = 80
        elif 850 >= self.high > 600:
            self.profit = 40
        elif 600 >= self.high > 400:
            self.profit = 30
        elif 400 >= self.high:
            self.profit = 20
# --------------------------------------------------

    def buy_order(self, ref, qty):

        symbol = Order(self.ticker, self.high)

        if ref == 'sma1':
            order = symbol.buy(order_type='market', order_class='oto',
                               qty=qty, tif='gtc', profit=self.profit)
           # self.order_log('Order: %s \n %s' % (ref, order))

            notification_sys.create_message(order)
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


# --------------------------------------------------

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

# --------------------------------------------------

if __name__ == '__main__':

   # high = [i for i in range(400,440)]
    #qt = QuantTrader(high, 'TSLA')
    #qt.buy_order(ref='sma1',qty=1)

    pass

