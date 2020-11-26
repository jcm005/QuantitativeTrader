import requests, json
from streamkeys import *
import alpaca_trade_api as tradeapi
from datetime import datetime

# This needs to be changes to an a Account object
#for non paper we can use tradeapi.REST(insert keys here)
#requests.get(ACCOUNT_URL,headers=HEADERS)
#api = tradeapi.REST(API_KEY, SECRET_KEY, api_version='v2')

class Account:

    def __init__(self, paper=False):

        if paper == True:
            self.BASE_URL = "https://paper-api.alpaca.markets"
            self.HEADERS = {'APCA-API-KEY-ID': PAPER_KEY, 'APCA-API-SECRET-KEY': SECRET_KEY}
        else:
            self.BASE_URL = "https://api.alpaca.markets"
            self.HEADERS = {'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY': SECRET__KEY}

        self.ACCOUNT_URL = f'{self.BASE_URL}/v2/account'
        self.ORDERS_URL = f'{self.BASE_URL}/v2/orders'
        self.POSITIONS_URL = f'{self.BASE_URL}/v2/positions'
        self.POSITION_FOR_URL = f'{self.BASE_URL}/v2/positions/'

    def clean_and_load(self,message):
        # DO NOT MODIFY THIS CODE BELOW THIS CLEANS THE INPUT !!!!
        message = message.strip(message[0])
        message = message.strip(message[-1])
        return message
        # DO NOT MODIFY THIS CODE ABOVE THIS CLEANS THE INPUT !!!!
        # LOADS AND CONVERTS DATETIME ALLOCATION OF SOME ALIAS

    def byte_decoder(self,need_decoded):
        """DECODES THE OUTPUT OF A REQUEST.GET()
         FUNCTION RETURNING A DICTIONARY
         """
        decoded = need_decoded.content.decode('utf-8')
        dumper = json.loads(decoded)
        return dumper

    def get_account(self):
        """For now returns all account infor this function can
        be used to clean the outputted information
        PRINTING ACCOUNT WILL GIVE US RESPONSE CODE
        """
        self.account = requests.get(self.ACCOUNT_URL,headers=self.HEADERS)
        return self.byte_decoder(self.account)

    def get_orders(self):
        """
        Catered to getting any open positions
        """
        preface = requests.get(self.ORDERS_URL,headers=self.HEADERS)
        return self.byte_decoder(preface)

    def get_position(self):
        custom_position = requests.get(self.POSITIONS_URL,headers=self.HEADERS)
        return self.byte_decoder(custom_position)

    def get_position_for(self, symbol):
        """
         IF no position function will return a dictionary with
        a message saying there is no position therefore
        we will make the function return a false
        IF there is a position the function  will

         return the positions
        :param symbol:
        :return:
        """
        position_for = requests.get(f'{self.POSITION_FOR_URL}{symbol}',headers=self.HEADERS)
        decoded =  self.byte_decoder(position_for)

        try:
            if decoded['message'] == 'position does not exist':
                decoded = False
                return decoded

        except:
            return decoded

    def place_order(self, order):
        """
        SENDS ORDER TO ALPACA FOR PROCESSING
        :param order: DICTIONARY PERFERABLLY JSON FORMAT
        :return: DICTIONARY THAT WAS OUTPUTTED FROM BYTE_DECODEDR AND A BOOLEAN BASED ON SUCCESSION OR NOT
        """
        preface = requests.post(self.ORDERS_URL,json=order,headers=self.HEADERS)
        return self.byte_decoder(preface),True

    def order_details(self, raw_order, output='detailed'):
        """
        :param raw_order: PASS IN A DICTIONARY GIVEN BY PLACE ORDER
        :param output: PASS 'simple' FOR BASIC ORDER INFO OR 'detailed' for detailed out
        :return: WILL RETURN ORDER DETAILS AS A DICT
        """

        if output == 'simple':
            simple = {
                'symbol':raw_order['symbol'],
                'status':raw_order['status'],
                'order_type':raw_order['order_type'],
                'side':raw_order['side'],
                #'submitted_at': time,
                'order_id':raw_order['id'],
            }
            return simple

        elif output == 'detailed':
            return raw_order

    def account_info(self):
        """
        """
        account = self.get_account()
        information = {
            'cash':account['cash'].split('.')[0],
            'portfolio_value': account['portfolio_value'].split('.')[0],
            'buying_power': account['buying_power'].split('.')[0],
            }
        return information


if __name__ == '__main__':

    pass

    #account = get_account()
    #tsla = get_position_for('TSLA')
    #equity = account['equity']
    #equity = account['equity'].split('.')[0]
    #print(equity)


