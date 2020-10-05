from __future__ import annotations
from abc import ABC,abstractmethod

import access as a
from trader import QuantTrader
from analyzer import Analyzer


# Objects returned by a factory method are often referred to as products.
# in this case they will return strategies
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



class ConcreteCreator(Creator):

    def __init__(self,parameter):
        # dont want errors if the parameter is not yet created

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
        # need price information in here to evaluete information
        # where am i getting the price infomation from?
        # Analyzer has all the info i need

        print('Welcome to the Factory\nRunning Parameters...\n')
        if self.rolling_v_10 != False:
            if self.rolling_v_10 > .6:
                return RagingBull(self.high)
            else:
                return RagingBull(self.high)
        else:
            return RagingBull(self.high)

    def run_factory(self):

        print('Factory Live')
        strategy = self.factory_method()
        return strategy


class Strategy(ABC):
    """
    Strategy interface declares all the operation that all the concrete products
    must implement
    """

    @abstractmethod
    def build_strategy(self):
        print('Enter logic for microstrategies here')

    def operation(self):
        """
        framework functions that will always
        run no matter what strategy is being called
        """
        #QuantTrader('TSLA').price_jump(ref='pj')
        print('operation firing')

    def run(self):

        self.build_strategy()
        self.operation()

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

def client_code(creator: Creator) -> creator.run():

    """
    The client code workks with an instance of a concrete creator, albeit through
    its base interface. As long as the client keeps working with the creator via
    the base interface, you can pass it any creator's subclass.
    """
    #creator.build()
    creator.run()


def get_strategy(parameters):

    return ConcreteCreator(parameters).run_factory()

if __name__ == "__main__":


    strategy = get_strategy(parameters=10)
    strategy.run()




# -- call concrete creator --> acts as a tree to pick a strategy -->
# -- then return a strategy --> running the buildStratefy in the selected strategy
# --


   # client_code()