from __future__ import annotations
from abc import ABC,abstractmethod

import access as a
from trader import QuantTrader
from analyzer import Analyzer
import logging

# Objects returned by a factory method are often referred to as products.
# in this case they will return strategies

# CREATOR CREATES NEW CONCRETES
class Creator(ABC):
    """
       The Strategy FActory class declares the factory method that is supposed to return an
       object of a Strategy class. The stratfact's subclasses usually provide the
       implementation of this method.
       """

    @abstractmethod
    def factory_method(self): # this is like the main.py for strategy
        """
        Goingto use this to grab files from access.py to gain position insight
        :return:
        """
        pass

    def run(self):

        strategy = self.factory_method()
        print('Loading Strategy')

# STRATEGY DECISION TREE
class ConcreteCreator(Creator):


    def __init__(self,parameter):
        # dont want errors if the parameter is not yet created
        self.par = parameter
        self.high = parameter['high']
        self.low = parameter['low']
        self.volume = None
        self.vp = None
        if parameter['rolling_v_10'] != None:
            self.rolling_v_10 = parameter['rolling_v_10']
        else:
            self.rolling_v_10 = False

    def factory_method(self):
        '''TREE'''

        print('-- Welcome to the Factory --> Evaluating Parameters...\n')
        logging.info('-- Welcome to the Factory --> Evaluating Parameters...\n')

        if self.rolling_v_10 != False and self.rolling_v_10 > .6:
            return RagingBull(self.high)
        else:
            return DoNothing(self.high)


    def run_factory(self):

        print('Factory Live')
        logging.info('-- Factory Live --')
        strategy = self.factory_method()
        logging.info('Loading up the %s Strategy' % strategy)
        return strategy

# BASIC STRATEGY FRAMEWORK
class Strategy(ABC):
    """
    Strategy interface declares all the operation that all the concrete products
    must implement
    """

    @abstractmethod
    def build_strategy(self):
        print('Enter logic for microstrategies here')

    def operation(self,high):
        """
        framework functions that will always
        run no matter what strategy is being called
        """
        logging.info('-- Checking Price Jump --')
        QuantTrader(high,'TSLA').price_jump(ref='pj')


    def run(self):

        high = self.high
        logging.info('Building Strategy')
        self.build_strategy()
        self.operation(high)

    def log(self):
        pass


class RagingBull(Strategy):

    def __init__(self,high):
        self.high = high

    def __str__(self):
        return 'RagingBull'

    def build_strategy(self):

        print('Welcome to raging bull where we got chronic volatitlity')
        QuantTrader(self.high,'TSLA').climb_the_ladder(ref='ctlws')


class DoNothing(Strategy):

    def __init__(self,high):
        self.high = high

    def __str__(self):
        return 'DoNothing'

    def build_strategy(self):
        logging.info('Running Default Functions')
        return

# IGNORE THIS FOR NOW -- INTERESTING TAKE IN AN OBJECTS AND RUNS ITS FUNCTION
def client_code(creator: Creator) -> creator.run():

    """
    The client code workks with an instance of a concrete creator, albeit through
    its base interface. As long as the client keeps working with the creator via
    the base interface, you can pass it any creator's subclass.
    """
    #creator.build()
    creator.run()


def get_strategy(parameters):
    """

    :param parameters: taken in parameters as a dictionary,
    :return: the strategy to be executed in strategy.run() in main.py
    """
    return ConcreteCreator(parameters).run_factory()

if __name__ == "__main__":


    strategy = get_strategy(parameters=10)
    strategy.run()




