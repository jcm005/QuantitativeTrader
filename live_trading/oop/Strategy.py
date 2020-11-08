from __future__ import annotations
from abc import ABC, abstractmethod

import access as a
from trader import QuantTrader
from analyzer import Analyzer
import logging
import notification_sys



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
        # enter another function dictating wheter if the mirco strats are boolean true then get order then we can go another layer to send order
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

        #Make micos boolean and then add logic for ordering here


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
