import websocket
import ssl
import dateutil.parser
import alpaca_stream
from streamkeys import *
import trader
import logging
import json
import analyzer
import strategy_factory


#fmt = '%(asctime), -- %(messge)s -- '
logging.basicConfig(level=logging.DEBUG,
                    filename='algorithm.log',
                    filemode='w',
                    #format=fmt
                     )


def web_socket_start():
    ws = websocket.WebSocketApp(socket,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close
                                )
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

def on_open(ws):
    """
    CREATES A WEBCONNECTION OBJECT INSTATIATED WITH THE APIKEY THEN CALLS A
    SUBSCRIPTION FUNCTION AND PREP DATA TO BE SENT THROUGH WEBSOCKETS WS.SEND()

    :param ws:
    :return:
    """
    print('Connecting')
    stream = alpaca_stream.WebConnection(API_KEY)               # instantiate connection object w/apikey
    stream._subscribe(ws,'AM.' + ticker)  #retrive subsciprition data to connection
    logging.info('Connection Successful')
    print('Connected\nWaiting for incoming data from API')

def on_close(ws):

    logging.warning('Re-establishing connection')
    web_socket_start()

def on_error(ws,error):
        pass

def on_message(ws,message):

    logging.info('-------------------')
    while dp.load(message) == True:
        dp.run()
        strategy = strategy_factory.get_strategy(dp._market_analyzer())
        strategy.run()
        break



if __name__ == '__main__':

    ticker = 'TSLA'
    socket = "wss://alpaca.socket.polygon.io/stocks"
    dp = analyzer.Analyzer()        # intializing for data processing
    web_socket_start()              # start connection




