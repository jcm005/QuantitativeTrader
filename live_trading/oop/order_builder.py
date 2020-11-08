from __future__ import annotations
from abc import ABC, abstractmethod, abstractproperty
from typing import Any
import order_factory
import logging
from streamkeys import *
import access as a
import requests, json, time


class Builder(ABC):
    """
    The Builder interface specifies methods for creating the different parts of
    the Product objects.
    """
    @abstractmethod
    def setTicker(self):
        pass

    @abstractmethod
    def setOrderType(self, txt) -> None:
        pass
    @abstractmethod
    def setQty(self, num=1) -> None:
        pass

    @abstractmethod
    def setTif(self, txt) -> None:
        # add list of options and check against all those
        pass

    @abstractmethod
    def setSide(self, txt='buy') -> None:
        pass

    @abstractmethod
    def getProfit(self) -> None:
        pass

    @abstractmethod
    def setStopPrice(self) -> None:
        pass

    @abstractmethod
    def setLimitPrice(self) -> None:
        pass

    @abstractmethod
    def setStopLimitPrice(self) -> None:
        pass

    @abstractmethod
    def setOrderClass(self, txt) -> None:
        pass


class ConcreteBuilder1(Builder):
    """
    The Concrete Builder classes follow the Builder interface and provide
    specific implementations of the building steps. Your program may have
    several variations of Builders, implemented differently.
    """

    def __init__(self,ticker,current_price, paper=False) -> None:
        """
        A fresh builder instance should contain a blank product object, which is
        used in further assembly.
        """
        self.paper = paper
        self.price = current_price
        self.symbol = ticker
        self.reset() # may be a redundancy here
        self.getProfit()


    def reset(self) -> None:
        self._product = Order(self.paper)

    @property
    def product(self) -> Product1:
        """
        Concrete Builders are supposed to provide their own methods for
        retrieving results. That's because various types of builders may create
        entirely different products that don't follow the same interface.
        Therefore, such methods cannot be declared in the base Builder interface
        (at least in a statically typed programming language).

        Usually, after returning the end result to the client, a builder
        instance is expected to be ready to start producing another product.
        That's why it's a usual practice to call the reset method at the end of
        the `getProduct` method body. However, this behavior is not mandatory,
        and you can make your builders wait for an explicit reset call from the
        client code before disposing of the previous result.
        """
        product = self._product
        self.reset()
        return product

    def setTicker(self):
        self._product.add({'symbol':self.symbol})

    def setOrderType(self,txt) -> None:
        l = ['market', 'limit']
        # does not support soley stop limit and stop orders
        if txt.lower() in l:
            if txt.lower() == 'market':
                self._product.add({'type': txt})
            elif txt.lower() == 'limit':
                self._product.add({'type': txt})
                self._product.add({'limit_price':self.price -10})
        else:
            logging.warning('!! Invalid Order Type; Please Enter "market" or "limit" !!')

    def setQty(self, num=1) -> None:
        self._product.add({'qty': num})

    def setTif(self, txt) -> None:
        # add list of options and check against all those
        self._product.add({'time_in_force': txt})

    def setSide(self, txt='buy') -> None:
        self._product.add({'side':txt})

    def getProfit(self) -> None:
        self.profit = order_factory.get_profit(self.price)

    def setStopPrice(self) -> None:
        self._product.add("PartA1")

    def setLimitPrice(self) -> None:
        self._product.add("PartA1")

    def setStopLimitPrice(self) -> None:
        self._product.add("PartA1")

    def setOrderClass(self,txt) -> None:
        l = ['oto','bracket']
        if txt.lower() in l:
            if txt.lower() == 'oto':
                self._product.add({'order_class':txt})
                self._product.add({'take_profit':{
                    'limit_price': self.price + self.profit
                }})
            elif txt.lower() == 'bracket':
                stop_price = round(self.price - (self.profit/2.25))
                stop_limit_price =  round(self.price - (self.profit / 2))
                if stop_price < (self.price/1.001):
                    logging.info('Stop Price is < price/1001')

                self._product.add({'order_class':'bracket'})
                self._product.add({'take_profit': {
                    'limit_price': self.price + self.profit
                }})

                # stop price will probably be made in profit factory as well

                self._product.add({'stop_loss':{
                    'stop_price': stop_price,
                    'limit_price': stop_limit_price
                }})

        else:
            logging.warning('!! Invalid Order Class; Please Enter "oto" or "bracket" !!')

class Order:
    """
    It makes sense to use the Builder pattern only when your products are quite
    complex and require extensive configuration.

    Unlike in other creational patterns, different concrete builders can produce
    unrelated products. In other words, results of various builders may not
    always follow the same interface.
    """

    def __init__(self, paper=False) -> None:

        self.paper = paper

        if self.paper:
            self.BASE_URL = "https://paper-api.alpaca.markets"
        else:
            self.BASE_URL = "https://api.alpaca.markets"

        self.ORDER_URL = f'{self.BASE_URL}/v2/orders'
        self.order = {}

    def add(self, txt: Any) -> None:
        self.order.update(txt)
        pass

    def show_order(self):
        print(self.order)

    def byte_decoder(self, need_decoded):
        """
        DECODES THE OUTPUT OF A REQUEST.GET()
         FUNCTION RETURNING A DICTIONARY
         """

        decoded = need_decoded.content.decode('utf-8')
        dumper = json.loads(decoded)
        return dumper

    def send_order(self): # calling the .product earses the self.order

        if self.paper:
            HEADERS = {'APCA-API-KEY-ID': PAPER_KEY, 'APCA-API-SECRET-KEY': SECRET_KEY}
        else:
            HEADERS = {'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY': SECRET__KEY}

        order_sender = self.byte_decoder(
            requests.post(
                self.ORDER_URL,
                json=self.order,
                headers=HEADERS
            ))
        logging.info('order: %s' % order_sender)
        print(order_sender)


class Director:
    """
    The Director is only responsible for executing the building steps in a
    particular sequence. It is helpful when producing products according to a
    specific order or configuration. Strictly speaking, the Director class is
    optional, since the client can control builders directly.
    """

    def __init__(self) -> None:
        self._builder = None

    @property
    def builder(self) -> Builder:
        return self._builder

    @builder.setter
    def builder(self, builder: Builder) -> None:
        """
        The Director works with any builder instance that the client code passes
        to it. This way, the client code may alter the final type of the newly
        assembled product.
        """
        self._builder = builder

    def prepare_simple_order(self, txt) -> None:
        self.builder.setTicker()
        self.builder.setSide()
        self.builder.setOrderType(txt)
        self.builder.setTif('day')
        self.builder.setQty()

    def prepare_oto_order(self,txt) -> None:
        self.builder.setTicker()
        self.builder.setSide()
        self.builder.setOrderType(txt)
        self.builder.setOrderClass('oto')
        self.builder.setTif('gtc')
        self.builder.setQty()

    def prepare_bracket_order(self) -> None:
        self.builder.setTicker()
        self.builder.setSide()
        self.builder.setOrderType('market')
        self.builder.setOrderClass('bracket')
        self.builder.setTif('gtc')
        self.builder.setQty()




if __name__ == "__main__":
    """
    The client code creates a builder object, passes it to the director and then
    initiates the construction process. The end result is retrieved from the
    builder object.
    """

    price = 380
    director = Director() # think of as CEO
    builder = ConcreteBuilder1('TSLA',price, paper=True) # think of as employee

    director.builder = builder

    print('-----------------------')
    print("Market order: ")
    director.prepare_simple_order('market')
    market_order = builder.product
    market_order.show_order()
    #market_order.send_order()
    print('-----------------------')

    print('-----------------------')
    print("Oto order: ")
    director.prepare_oto_order('limit')
    oto_order = builder.product
    oto_order.show_order()
    #oto_order.send_order()
    print('-----------------------')

    print('-----------------------')
    print("Bracket order: ")
    director.prepare_bracket_order()
    bk_order = builder.product
    bk_order.show_order()
    #bk_order.send_order()
    print('-----------------------')

    print('-----------------------')
    print("Limit order: ")
    director.prepare_simple_order('limit')
    lm_order = builder.product
    lm_order.show_order()
    lm_order.send_order()
    print('-----------------------')