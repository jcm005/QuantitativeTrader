

class Order():
# LOGGIN FUNCTION FOR OUTPUTTNIG TO LOG FILES
    def __init__(self,symbol,current_price):
        self.symbol = symbol
        self.price = current_price
        # --------------------------
        self.BASE_URL =  "https://paper-api.alpaca.markets"
        self.ORDER_URL = f'{self.BASE_URL}/v2/orders'
        self.candle = open('candle.txt','a')
        # --------------------------

    def byte_decoder(self,need_decoded):
        '''DECODES THE OUTPUT OF A REQUEST.GET()
         FUNCTION RETURNING A DICTIONARY'''
        decoded = need_decoded.content.decode('utf-8')
        dumper = json.loads(decoded)
        return dumper
#maybe make thid a subclass
    def log(self,file,log_info):
        file.write(log_info)

    def order_details(self,raw_order,output='detailed'):
        '''
        :param raw_order:
        :param output:
        :return:
        '''
        print(raw_order)
        try:
            if output == 'simple':
                simple = {
                    'symbol': raw_order['symbol'],
                    'status': raw_order['status'],
                    'order_type': raw_order['order_type'],
                    'side': raw_order['side'],
                    # 'submitted_at': time,
                    'order_id': raw_order['id'],
                }
                return simple
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
        HEADERS = {'APCA-API-KEY-ID': PAPER_KEY, 'APCA-API-SECRET-KEY': SECRET__KEY}

        order_sent = self.byte_decoder(
            requests.post(
                self.ORDER_URL,
                json=order,
                headers=HEADERS
            ))
        status = self.order_details(order_sent,'simple')
        self.log(self.candle,f'Order Status is: {status}\n')
        return order_sent
# DO I WANT TO ADD THE OCO ORDERING BRACKETING? ORDERS
    def buy(self,order_type,qty,tif,profit=0,ref=None):
        self.qty = qty
        self.profit = profit
        order = {
            'symbol':self.symbol,
            'qty':self.qty,
            'side': 'buy',
            'type': order_type,
            'time_in_force': tif
        }
        self.log(self.candle,f'Attempting To Buy With Ref Number: {ref} @ {self.price}\n')
        buy = self.place_order(order)
        if self.profit != 0:
            time.sleep(5)
            self.log(self.candle,f'Attempting To Sell With Ref Number: {ref} @ {self.price + self.profit}\n')
            sell = self.sell()
            return buy,sell
        else:
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