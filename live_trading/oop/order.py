import requests, json, time
from streamkeys import *
import access as a
from datetime import datetime
import pytz
from pytz import timezone
import stream_tools

class Order:
    # PLEASE CHECK THE BASE URLS ARE DIRECTED TO THE RIGHT SPOT FOR PAPER OR REAL LIFE TRADING
    def __init__(self,symbol,current_price,paper=False):

        self.symbol = symbol
        self.price = current_price
        self.paper = paper
        # --------------------------
        if self.paper == False:
            self.BASE_URL =  "https://api.alpaca.markets"
        else:
            self.BASE_URL = "https://paper-api.alpaca.markets"
        print(self.BASE_URL)
        self.ORDER_URL = f'{self.BASE_URL}/v2/orders'

        # --------------------------
# maybe make this a steram tool
    def byte_decoder(self,need_decoded):
        """
        DECODES THE OUTPUT OF A REQUEST.GET()
         FUNCTION RETURNING A DICTIONARY
         """

        decoded = need_decoded.content.decode('utf-8')
        dumper = json.loads(decoded)
        return dumper

    def order_details(self,raw_order,output='detailed'):
        """
        :param raw_order:
        :param output:
        :return:
        """

        orders_list = []
        try:
            if raw_order['code']:
                return raw_order
        except:
            pass

        if raw_order['legs'] != None:
            limit_order = raw_order['legs'][0]
            try:
                stop_order = raw_order['legs'][1]
                print(stop_order)
            except:
                pass

        try:
            if output == 'simple':
                simple = {
                    'symbol': raw_order['symbol'],
                    'status': raw_order['status'],
                    'order_type': raw_order['order_type'],
                    'order_class':raw_order['order_class'],
                    'side': raw_order['side'],
                    # 'submitted_at': time,
                    'order_id': raw_order['id'],
                }
                orders_list.append(simple)
                try:
                    if raw_order['legs'] != None:
                        limit_order = raw_order['legs'][0]
                        limit = {
                            'symbol': limit_order['symbol'],
                            'status': limit_order['status'],
                            'order_type': limit_order['order_type'],
                            'limit_price': limit_order['limit_price'],
                            'side': limit_order['side'],
                            # 'submitted_at': time,
                            'order_id': limit_order['id'],
                        }
                except:
                    pass
                    orders_list.append(limit)
                    try:
                        stop_order = raw_order['legs'][1]
                        stop = {
                            'symbol': stop_order['symbol'],
                            'status': stop_order['status'],
                            'order_type': stop_order['order_type'],
                            'limit_price': stop_order['limit_price'],
                            'stop_price': stop_order['stop_price'],
                            'side': stop_order['side'],
                            # 'submitted_at': time,
                            'order_id': stop_order['id'],
                        }
                        orders_list.append(stop)

                    except:
                        pass


                return orders_list
            elif output == 'detailed':
                return raw_order
        except KeyError:
            return 'Order Failed'

    def place_order(self,order):
        '''
        SENDS ORDER TO ALPACA FOR PROCESSING
        :param order: DICTIONARY PREFERABLY JSON FORMAT
        :return: DICTIONARY THAT WAS OUTPUTTED FROM BYTE DECODED,
        ALONG WITH A BOOLEAN BASED ON SUCCESSION STATUS
        '''
        if self.paper == False:
            HEADERS = {'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY': SECRET__KEY}
        else:
            HEADERS = {'APCA-API-KEY-ID': PAPER_KEY, 'APCA-API-SECRET-KEY': SECRET__KEY}

        print(HEADERS)


        order_sent = self.byte_decoder(
            requests.post(
                self.ORDER_URL,
                json=order,
                headers=HEADERS
            ))
        status = self.order_details(order_sent,'simple')
        return status

    def buy(self,
            order_type,
            qty,
            tif,
            profit=0,
            ref=None,
            order_class=None,
            stop_price=None,
            limit_price=None,
            stop_limit_price=None,
            extended_hours=None):

        extended_hours = stream_tools.StreamTools.check_time()

        # replace this with share info in access.py
        try:

            account = a.Account().get_account()
            buying_power = account['buying_power'].split('.')[0]
            equity = account['equity'].split('.')[0]
        except KeyError as e:
            print(e)

        try:
            if buying_power < equity:
                return 'Buying Power is less then equity will not buy for conservative reasons\n'
        except:
            pass

        # INSERT HERE CODE FOR NO BUY BELOW AVERAGE PRICE

        self.qty = qty
        self.profit = profit
        order = {
            'symbol': self.symbol,
            'qty': self.qty,
            'side': 'buy',
            'type': order_type,
            'time_in_force': tif,
        }

        if extended_hours:
            order['time_in_force'] = 'day'
            order['type'] = 'limit'
            order['extended_hours'] = True
            if not limit_price:
                order['limit_price'] = self.price + 10
                print('need a limit price for extended hours')
            else:
                order['limit_price'] = limit_price
            if order_class:
                order_class = None

            print(order)

        # OTO IS GOOD FOR A BUY AND A TAKE PROFIT WITH NO SELLING POINT FOR SAFETY

        if order_class == 'oto':
            order['order_class'] = 'oto'
            order['take_profit'] = {
                'limit_price': self.price + profit
            }
        elif order_class == 'bracket':
            if stop_price < (self.price / 1001):
                return 'stop price has to be greater then current price/1001'

            order['order_class'] = order_class
            order['take_profit'] = {
                'limit_price': self.price + profit
            }
            order['stop_loss'] = {
                'stop_price': stop_price,
                'limit_price': stop_limit_price,
            }
        elif order_type == 'limit':
            order['limit_price'] = limit_price

        buy = self.place_order(order) # returns a simplified order detail status
        return buy

    def sell(self):

        sell_order = {
            'symbol': self.symbol,
            'qty': self.qty,
            'side': 'sell',
            'type': 'limit',
            'time_in_force': 'gtc',
            'limit_price': self.profit + self.price
        }
        sell = self.place_order(sell_order)
        return sell


if __name__ == '__main__':

    current_price = 420
    o = Order('TSLA',current_price,paper=True)
    #o.place_order()
    aa = a.Account().get_account()
    print(aa)

    pass