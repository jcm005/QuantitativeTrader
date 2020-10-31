from __future__ import annotations
from abc import ABC, abstractmethod

import access as a
from trader import QuantTrader
from analyzer import Analyzer
import logging
import notification_sys
import order
import order_builder



class Creator(ABC):
    """
       The OrderFactory class declares the factory method that is supposed to return an
       object of a Strategy class. The stratfact's subclasses usually provide the
       implementation of this method.
       """

    @abstractmethod
    def factory_method(self):  # this is like the main.py for strategy
        """
        Goingto use this to grab files from access.py to gain position insight
        :return:
        """
        pass

    def run(self):
        strategy = self.factory_method()
        print('Sorting Orders')


class OrderFactory(Creator):

    def __init__(self,params):
        self.params = params


    def factory_method(self):
        """
        Thinking out loud what if this returns a buy object each buy object has the parameter set
        3 buy objects
        :return:
        """
        if self.ref == 'sma1':
            return Builder1(self.params)
        elif self.ref == 'ctl':
            return Builder2(self.params)
        elif self.ref == 'sdr':
            return Builder1(self.params)
        elif self.ref == 'pj':
            return Builder2(self.params)
        elif self.ref == 'dt':
            return Builder1(self.params)
        elif self.ref == 'sma1ws':
            return Builder1(self.params)
        elif self.ref == 'ctlws':
            return Builder2(self.params)
        elif self.ref == 'sdrws':
            return Builder1(self.params)
        elif self.ref == 'pjws':
            return Builder2(self.params)


    def load_order(self):
        logging.info('-- Getting Order Type --')
        order = self.factory_method()
        logging.info('-- Sending Order --')
        return order

class ProfitFactory(Creator):

    """ all thought the purpose of a factory is to return objects this just returns a price
    maybe in the furute it will return more attributes"""

    def __init__(self, current_price):
        self.price = current_price


    def factory_method(self):
        # add some thing here to mitigate errors
        # maybe add some logarithmic functions that this factory points to to have a more accurate tree

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

        return self.profit

    def load_profit(self):

        profit = self.factory_method()
        return profit


class Product(ABC):
    """
    Strategy interface declares all the operation that all the concrete products
    must implement
    """
    def __init__(self):
        self
        pass

    @abstractmethod
    def build_order(self):
        pass

    def operatiokn(self):
        # a framework of infrastrucutre function.
        pass

    def run(self):
        pass


class Builder1(Product):

    """Thin different builder style logic instructions"""
    def __init__(self, params):

        self.params = params
        self.ticker = params.symbol
        self.price = params.current_price



    def build_order(self):

        self.initiate_order()
        print()


class Builder2(Product):

    def __init__(self):
        pass


class Builder3(Product):

    def __init__(self):
        pass

def get_order(parameters):
    # maybe call get profit here so we can load the profit into the order
    return OrderFactory(parameters).load_order()

def get_profit(price):
    return ProfitFactory(price).load_profit()



if __name__ == '__main__':

# --------------------------------------------------
    #price = 430
    #profit = get_profit(price)
    #print(profit)
# --------------------------------------------------

    #order = get_order(ref)

# --------------------------------------------------
    pass