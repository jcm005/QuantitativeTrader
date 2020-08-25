import requests, json
from streamkeys import *
import alpaca_trade_api as tradeapi
from datetime import datetime
#for non paper we can use tradeapi.REST(insert keys here)

BASE_URL = "https://paper-api.alpaca.markets"
ACCOUNT_URL = f'{BASE_URL}/v2/account'
ORDERS_URL = f'{BASE_URL}/v2/orders'
POSITIONS_URL = f'{BASE_URL}/v2/positions'
POSITION_FOR_URL = f'{BASE_URL}/v2/positions/'
HEADERS = {'APCA-API-KEY-ID': PAPER_KEY, 'APCA-API-SECRET-KEY':SECRET__KEY}

#requests.get(ACCOUNT_URL,headers=HEADERS)
#api = tradeapi.REST(API_KEY, SECRET_KEY, api_version='v2')


def clean_and_load(message):
    # DO NOT MODIFY THIS CODE BELOW THIS CLEANS THE INPUT !!!!
    message = message.strip(message[0])
    message = message.strip(message[-1])
    return message
    # DO NOT MODIFY THIS CODE ABOVE THIS CLEANS THE INPUT !!!!
    # LOADS AND CONVERTS DATETIME ALLOCATION OF SOME ALIAS
def byte_decoder(need_decoded):
    '''DECODES THE OUTPUT OF A REQUEST.GET()
     FUNCTION RETURNING A DICTIONARY'''
    decoded = need_decoded.content.decode('utf-8')
    dumper = json.loads(decoded)
    return dumper
def get_account():
    '''For now returns all account infor this function can
    be used to clean the outputted information
    PRINTING ACCOUNT WILL GIVE US RESPONSE CODE
    '''
    account = requests.get(ACCOUNT_URL,headers=HEADERS)
    return byte_decoder(account)
def get_orders():
    '''Catered to getting any open positions '''
    preface = requests.get(ORDERS_URL,headers=HEADERS)
    return byte_decoder(preface)
def get_position():
    custom_position = requests.get(POSITIONS_URL,headers=HEADERS)
    return byte_decoder(custom_position)
def get_position_for(symbol):
    '''IF no position function will return a dictionary with
    a message saying there is no position therefore
    we will make the function return a false
    IF there is a position the function  will
     return the positions'''
    position_for = requests.get(f'{POSITION_FOR_URL}{symbol}',headers=HEADERS)
    decoded =  byte_decoder(position_for)

    try:
        if decoded['message'] == 'position does not exist':
            decoded = False
            return decoded

    except:
        return decoded
def place_order(order):
    '''
    SENDS ORDER TO ALPACA FOR PROCESSING
    :param order: DICTIONARY PERFERABLLY JSON FORMAT
    :return: DICTIONARY THAT WAS OUTPUTTED FROM BYTE_DECODEDR AND A BOOLEAN BASED ON SUCCESSION OR NOT
    '''
    preface = requests.post(ORDERS_URL,json=order,headers=HEADERS)
    return byte_decoder(preface),True
def order_details(raw_order,output='detailed'):
    '''
    :param raw_order: PASS IN A DICTIONARY GIVEN BY PLACE ORDER
    :param output: PASS 'simple' FOR BASIC ORDER INFO OR 'detailed' for detailed out
    :return: WILL RETURN ORDER DETAILS AS A DICT
    '''

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


if __name__ == '__main__':

    position = get_position_for('TSLA')
    if position:
        qty_pos = position['qty']
        cost_basis = position['cost_basis']
        avg_price = position['avg_entry_price']
    else:
        pass
    order = get_orders()
    print(order)