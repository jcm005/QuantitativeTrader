from __future__ import annotations
from abc import ABC,abstractmethod

import access as a
import trader
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

    def run(self) -> str:

        strategy = self.factory_method()
        print('Loading Strategy')
        return strategy.build_strategy()



class ConcreteCreator(Creator):
    # maybe Analyzer.__init__()
    def factory_method(self):
        '''TREE'''
        # need price information in here to evaluete information
        # where am i getting the price infomation from?
        # Analyzer has all the info i need


        if len('hello') == 5:
            strategy = RagingBull()
        return strategy.build_strategy()



class Strategy(ABC):
    '''PRiduct interface declares all the operation that all the concrete products
    must implement'''

    @abstractmethod
    def build_strategy(self):
        '''Maybe this can load the strat into on_messages'''
        print('default operation function')
        build_strategy()
        pass

    def log(self):
        pass

class RagingBull(Strategy):

    def build_strategy(self):

        pass


def client_code(creator: Creator) -> creator.run():

    """
    The client code workks with an instance of a concrete creator, albeit through
    its base interface. As long as the client keeps working with the creator via
    the base interface, you can pass it any creator's subclass.
    """
    creator.build()
    creator.run()

if __name__ == "__main__":

    client_code(ConcreteCreator())
    client_code(ConcreteCreator2())

# -- call concrete creator --> acts as a tree to pick a strategy -->
# -- then return a strategy --> running the buildStratefy in the selected strategy
# --


   # client_code()