from __future__ import annotations
from abc import ABC, abstractmethod
import access as a
from trader import QuantTrader
from analyzer import Analyzer
import logging
import notification_sys
import order_factory


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
        self.symbol = parameter['symbol']
        self.high = parameter['high']
        self.low = parameter['low']
        self.volume = None
        self.vp = parameter['vp']
        self.rolling_v_10 =  parameter['rolling_v_10']
        self.market_open = parameter['market_open']
        self.over_night = parameter['over_night']
        self.max = max(self.high)
        self.min = min(self.low)

    def factory_method(self):

        if self.market_open:
            logging.info('Max price: %s  Min price: %s' % (self.max, self.min))

            if (self.high[-1] - 5) > self.market_open:

                logging.info('-- The Market is Bull --')
                if self.rolling_v_10 != False and self.rolling_v_10 > .5:
                    return RagingBull(self.par)
                else:
                    return SlowBull(self.par)

            elif (self.market_open - 5) > self.high[-1]:
                logging.info('-- The market is Bear --')

                if self.rolling_v_10 != False and self.rolling_v_10 > .5:
                    return GrizzlyBear(self.par)
                else:
                    return Hibernation(self.par)

            else:
                if self.rolling_v_10 != False and self.rolling_v_10 >.5:
                    return BuringEnds(self.par)
                else:
                    return Hibernation(self.par)

        else:
            logging.warning('-- Market Open Failure --')
            return Hibernation(self.par)

    def load_factory(self):

        strategy = self.factory_method()
        logging.info('-- Loading up  %s --' % strategy)
        if strategy == None:
            logging.warning('-- Strategy is of NoneType --')
            return Hibernation(self.high)
        else:
            return strategy


class Strategy(ABC):
    """
    Strategy interface declares all the operation that all the concrete products
    must implement
    """

    def __init__(self, params):

        self.high = params['high']
        self.vp  = params['vp']

        self.qt = QuantTrader(self.high)

        self.parameters = {
            'symbol': params['symbol'],
            'price': self.high[-1]
        }

    @abstractmethod
    def build_strategy(self):
        pass

    def operation(self):
        """
        framework functions that will always
        run no matter what strategy is being called
        """

        status = self.qt.price_jump()
        if status:
            self.parameters['ref'] = 'pj'
            order = order_factory.get_order(self.parameters)
            order.build_order()
            order.show_order()
            order.send_order()

    def run(self):

        logging.info('-- Building Strategy --')
        self.build_strategy()
        self.operation()


class RagingBull(Strategy):
    """
    Call this when there high volatility and the
    opening price is lower then the current price

    Idealistic price is moving up all day but volatility causes price to drop
    we know its a bull day we buy on that drop call SDR
    """


    def __str__(self):
        return 'RagingBull'

    def build_strategy(self):

        print('Welcome to raging bull where we got chronic volatitlity')

        status = self.qt.stop_drop_and_roll()
        if status:
            self.parameters['ref'] = 'sdr'
            order = order_factory.get_order(self.parameters)
            order.build_order()
            order.show_order()
            order.send_order()

        else:
            print('SDR not satisfied')
            logging.info('Req not satisfied')


class Hibernation(Strategy):

    """
    Call this in a non volatile markey
    """

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

    def __str__(self):
        return 'SlowBull'

    def build_strategy(self):

        print('Welcome to the SlowBull, its a quiet day but we see overall growth')
        logging.info('Welcome to the SlowBull, its a quiet day but we see overall growth')

        status = self.qt.Volatility(self.vp)
        if status:
            self.parameters['ref'] = 'sma1'
            order = order_factory.get_order(self.parameters)
            order.build_order()
            order.show_order()
            order.send_order()
        else:
            print('SMA! not satisfied')
            logging.info('Not volatilie sma1')


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



    def __str__(self):
        return 'GrizzlyBear'

    def build_strategy(self):
        print('Welcome to GrizzlyBear where we got chronic volatitlity, and falling fast')
        status = self.qt.climb_the_ladder()
        if status:
            self.parameters['ref'] = 'ctl'
            order = order_factory.get_order(self.parameters)
            order.build_order()
            order.show_order()
            order.send_order()
        else:
            print('nope')


class BurningEnds(Strategy):


    def __str__(self):
        return 'BurningEnds'

    def build_strategy(self):
        print('Welcome to BurningEnds where we got chronic volatitlity, with no significant price movement')

# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------


def get_strategy(parameters):
    """

    :param parameters: taken in parameters as a dictionary,
    :return: the strategy to be executed in strategy.run() in main.py
    """
    return StrategyFactory(parameters).load_factory()


if __name__ == "__main__":
    test = False
    if test == True:
        p = {
            'symbol': 'TSLA',
            'high': [i for i in range(1,440)],
            'low': None,
            'rolling_v_10': .6,
            'market_open':400,
            'rolling_high_10': 430,
            'rolling_high_30': 431,
            'vp':1.2,
        }

        strategy = get_strategy(p)
        strategy.run()

        #rage = GrizzlyBear(p)
        #rage.build_strategy()
        #rage.operation()
