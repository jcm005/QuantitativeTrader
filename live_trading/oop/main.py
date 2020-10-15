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
    print('Connected\nWaiting for incoming data from API\n')

    # 'Optional stream with spy 500 information ----' stream._subscribe_w_spy(ws, channel=ticker)

def on_close(ws):

    logging.warning('-- Re-establishing connection--')
    logging.warning('-- Saving Metrics --')

    web_socket_start()

def on_error(ws,error):
        pass


def on_message(ws,message):
    logging.info('-------------------')
    while dp.load(message, ticker) == True:
        dp.run()
        strategy = strategy_factory.get_strategy(dp._market_analyzer())
        strategy.run()
        metrics = dp.metrics()
        break

#  FRIST THING TOMORROW TRY TO TAKE OUT SELF.MARKET_ANALYZER OUT OF THE PROGRAM FROM DP.RUN() IT SHOULD RUN FLAWLESSLY
#  THEN WORK ON METRICS

if __name__ == '__main__':

    ticker = 'TSLA'
    socket = "wss://alpaca.socket.polygon.io/stocks"
    dp = analyzer.Analyzer()
    web_socket_start()




