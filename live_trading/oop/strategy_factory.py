from __future__ import annotations
from abc import ABC, abstractmethod

import access as a
from trader import QuantTrader
from analyzer import Analyzer
import logging



class Creator(ABC):
    """
       The Strategy FActory class declares the factory method that is supposed to return an
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
        print('Loading Strategy')


class StrategyFactory(Creator):

    def __init__(self, parameter):

        self.par = parameter
        self.high = parameter['high']
        self.low = parameter['low']
        self.volume = None
        self.vp = parameter['vp']
        self.rolling_v_10 =  parameter['rolling_v_10']
        self.market_open = parameter['market_open']
        self.over_night = parameter['over_night']

    def factory_method(self):
        '''TREE'''

        print('-- Evaluating Parameters... --')
        logging.info('-- Evaluating Parameters... --')

        if self.market_open:
            # -- Bull Case --
            if (self.high[-1] - 10) > self.market_open:

                if self.rolling_v_10 != False and self.rolling_v_10 > .5:
                    return RagingBull(self.high)
                else:
                    return SlowBull(self.high,self.vp)

            # -- Bear Case --
            elif (self.market_open - 10) > self.high[-1]:

                if self.rolling_v_10 != False and self.rolling_v_10 > .5:
                    return GrizzlyBear(self.high)
                else:
                    return Hibernation(self.high)

            # -- Small discrepancy in price, check volatility
            else:
                if self.rolling_v_10 != False and self.rolling_v_10 >.5:
                    return BuringEnds(self.high)
                else:
                    return Hibernation(self.high)

        else:
            logging.warning('-- MARKET OPEN FAILURE --')

    def run_factory(self):

        logging.info('-- Factory Live --')
        strategy = self.factory_method()
        logging.info('-- Loading up the %s Strategy --' % strategy)
        if strategy == None:
            return Hibernation(self.high)
        else:
            return strategy


class Strategy(ABC):
    """
    Strategy interface declares all the operation that all the concrete products
    must implement
    """

    @abstractmethod # has to be overwritten
    def build_strategy(self):
        pass

    def operation(self, high):
        """
        framework functions that will always
        run no matter what strategy is being called
        """
        logging.info('-- Starting Defualt Operations --')
        logging.info('-- Checking Price Jump --')
        QuantTrader(high, 'TSLA').price_jump(ref='pj')

    def run(self):
        high = self.high
        logging.info('-- Building Strategy --')
        self.build_strategy()
        self.operation(high)


class RagingBull(Strategy):
    """
    Call this when there high volatility and the
    opening price is lower then the current price

    Idealistic price is moving up all day but volatility causes price to drop
    we know its a bull day we buy on that drop call SDR
    """

    def __init__(self, high):
        self.high = high

    def __str__(self):
        return 'RagingBull'

    def build_strategy(self):
        print('Welcome to raging bull where we got chronic volatitlity')
        QuantTrader(self.high, 'TSLA').stop_drop_and_roll(ref='sdrws')


class Hibernation(Strategy):

    """
    Call this in a non volatile markey
    """
    def __init__(self, high):
        self.high = high

    def __str__(self):
        return 'Hibernation'

    def build_strategy(self):
        pass


class SlowBull(Strategy):
    """
    the idea here is just to run the
    volatility function watch for volatility spikes
    eventaully we will get a small profit
    """

    def __init__(self, high, vp):
        self.vp = vp
        self.high = high

    def __str__(self):
        return 'SlowBull'

    def build_strategy(self):

        print('Welcome to the SlowBull, its a quiet day but we see overall growth')
        logging.info('Welcome to the SlowBull, its a quiet day but we see overall growth')
        QuantTrader(self.high,'TSLA').Volatility(self.vp)


class GrizzlyBear(Strategy):
    """
      Call this when there high volatility and the
      opening price is higher then the current price

      Idealistic price is moving up down day but volatility causes price to raise
      we know its a bear day we buy on that rise call ctl hoping for a turn around

      should we call CTL? CTL has 30 minute overview
      should CTL be made a defualt operations?
      price jump would not be good here because
      yes i think CTL is the best approach, the turning point.

      i think it is important if the back logger cna preface this strategy
      """

    def __init__(self, high):
        self.high = high

    def __str__(self):
        return 'GrizzlyBear'

    def build_strategy(self):
        print('Welcome to GrizzlyBear where we got chronic volatitlity, and falling fast')
        QuantTrader(self.high, 'TSLA').climb_the_ladder(ref='ctlws')


class BurningEnds(Strategy):

    def __init__(self, high):
        self.high = high

    def __str__(self):
        return 'BurningEnds'

    def build_strategy(self):
        print('Welcome to BurningEnds where we got chronic volatitlity, with no significant price movement')

# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------

def client_code(creator: Creator) -> creator.run():
    """
    The client code workks with an instance of a concrete creator, albeit through
    its base interface. As long as the client keeps working with the creator via
    the base interface, you can pass it any creator's subclass.
    """
    # creator.build()
    creator.run()

def get_strategy(parameters):
    """

    :param parameters: taken in parameters as a dictionary,
    :return: the strategy to be executed in strategy.run() in main.py
    """
    return StrategyFactory(parameters).run_factory()


if __name__ == "__main__":

    strategy = get_strategy(parameters=10)
    strategy.run()
