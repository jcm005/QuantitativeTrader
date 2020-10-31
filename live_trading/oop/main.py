import websocket
import ssl
import dateutil.parser
import alpaca_stream
from streamkeys import *
import logging
import json
import analyzer
import strategy_factory
import notification_sys
import pandas as pd
import stream_tools



#fmt = '%(level)s: -- %(message)s --'
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
    print('\nConnecting')
    stream = alpaca_stream.WebConnection(API_KEY)
    #stream._subscribe(ws, type='AM.', channel=ticker)
    stream._subscribe_w_spy(ws, channel=ticker)
    logging.info('Connection Successful')
    #notification_sys.create_message('Logging On')
    print('Connected\nWaiting for incoming data from API\n')

def on_close(ws):

    logging.warning('-- Re-establishing connection--')
    logging.warning('-- Saving Metrics --')
    #notification_sys.create_message('System disconnected Reconnecting')

    try:
        metrics = dp.metrics()
        metrics.to_csv('metrics.txt', mode='w')
        #notification_sys.create_message('Metrics Saved')
    except:
        logging.info('Metrics lost')
        #notification_sys.create_message('Metrics lost')

    if stream_tools.StreamTools.stream_timer() == True:
        quit()
    else:
        web_socket_start()

def on_error(ws,error):
    pass

def on_message(ws,message):

    logging.info('--------------------------------------')
    print('-------------------')

    while dp.load(message, ticker) == True:
        dp.run()
        strategy = strategy_factory.get_strategy(dp._market_analyzer())
        strategy.run()
        metrics = dp.metrics()
        break


if __name__ == '__main__':


    ticker = 'TSLA'
    socket = "wss://alpaca.socket.polygon.io/stocks"
    dp = analyzer.Analyzer()
    web_socket_start()




