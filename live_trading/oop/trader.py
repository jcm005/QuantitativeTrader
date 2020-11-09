from order import Order
from pytz import timezone
import pytz
from datetime import datetime
import analyzer
import logging
import notification_sys
import pandas as pd


class QuantTrader:

    def __init__(self,price):
        """
        price has to be an iterable type
        """

        self.high = price[-1]      # value
        self.price = price          # list
        self.over_night = []
        self.sma = analyzer.Analyzer.sma

    def climb_the_ladder(self):
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
            logging.info('Threshold: %s' % (threshold))

            if (self.price[-1] - self.sma_30) > (threshold):
                #notification_sys.create_message('Sending Order %s' % order)
                logging.info('Ctl Satisfied')
                return True
            else:
                logging.info('Ctl Lower Than Threshold')
                return False
        else:
            logging.info('Need More Candles To Work With')
            return False

    def stop_drop_and_roll(self):
        '''If the price is dropping quicker then rolling 10 can catch up it will buy'''

        self.sma_10 = self.sma(self.price, window=10)

        if self.sma_10 != False:
            threshold = (self.sma_10 * 0.025)
            logging.info('Threshold: %s' % threshold)

            if (self.sma_10 - self.price[-1]) > (threshold):
                logging.info('Stop Drop and Roll Satisfied')
                return True
            else:
                logging.info('SDR Lower Than Threshold')
                return False
        else:
            logging.info('Need more candles to work with')
            return False

    def Volatility(self, vp=1):
        '''Given a parameter this function equates indicators for a volatility by
        influenced by the sma1 buy'''
        if vp > 1:
            logging.info('Volatility Order Satisfied')
            return True
        else:
            return False

    def price_jump(self):
        '''If the current price jumps over sma_30 threshold buy'''
        self.sma_30 = self.sma(self.price, window=30)
        if self.sma_30 != False:
            pj = (self.price[-1] - self.sma_30)
            logging.info(pj)
            print(pj)
            print((self.price[-1] * .02))
            logging.info((self.price[-1] * .02))
            if pj  > (self.price[-1] * .02):
                logging.info('Price Jump Satisfied')
                return True
            else:
                logging.info('Price Jump Not Satisfied')
                return False
        else:
            return False

    def double_trouble(self, param1, param2, qty=1):
        if param1 > 1 and param2 > .5:
            logging.info('Double Standard Satisfied')
            return True
        else:
            logging.info('Double Trouble Not Satisfied')
            return False

# --------------------------------------------------

if __name__ == '__main__':


    price = [i for i in range(0,100)]
    a = QuantTrader(price)
    b = a.price_jump()
    print(b)

    pass

