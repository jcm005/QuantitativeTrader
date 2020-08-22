import websocket, json, requests, sys
from streamkeys import *
import ssl
from datetime import datetime
import dateutil.parser
import access as a
import time
import pytz
from pytz import timezone
from tesla import *

est = pytz.timezone('US/Eastern')
minutes_processed = {}
minute_candlestick = []
current_tick = None
previous_tick = None
in_position = False

candles = open('candle.txt', 'a')
connection_log = open('log_on.txt', 'a')
log = open('action.txt', 'a')

candles.truncate(0)
log.truncate(50)

def _reopen(file):
    file_to_repoen = open(file, 'a')
    return file_to_repoen

def time_converter(some_time):

    newtime = datetime.fromtimestamp(some_time / 1000)

    newtimes = newtime.strftime('%Y-%m-%d, %a, %H:%M')
    return newtimes

def check_time():
    connection_log = _reopen('log_on.txt')
    print('Checking Time')
    connection_log.write('Checking Time\n')

    tiz = timezone('US/Eastern')
    right_now = pytz.utc.localize(datetime.utcnow()).astimezone(tiz)
    right_now = datetime.strftime(right_now, '%H:%M:%S')
    print((right_now[:2]))
    connection_log.write(f'{right_now[:2]}\n')
    if 6  < int(right_now[:2]) < 23:
        print('Good... reconnecting')
        connection_log.write(f'Good..Reconnecting, the time is :{right_now}\n')
        try:
            socket = "wss://alpaca.socket.polygon.io/stocks"
            ws = websocket.WebSocketApp(socket,
                                        on_open=onn_open,
                                        on_message=tesla,
                                        on_error=on_error,
                                        on_close=on_close
                                        )
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        except:
            print('Connection Failed')
            connection_log.write('Connection Failed')

            try:
                socket = "wss://alpaca.socket.polygon.io/stocks"
                ws = websocket.WebSocketApp(socket,
                                            on_open=onn_open,
                                            on_message=tesla,
                                            on_error=on_error,
                                            on_close=on_close
                                            )
                ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            except:
                print('Connection Failed')
    else:
        print('The Day Has Ended')
        connection_log.write('The day has ended\n')
# ----------------------------WEB-SOCKET FUNCTIONS BELOW ------------------
def onn_open(ws):
    connection_log = _reopen('log_on.txt')
    print("\nConnecting...")
    auth_data = {
        "action": "auth",
        "params": PAPER_KEY
    }
    ws.send(json.dumps(auth_data))
    channel_data = {
        "action": "subscribe",
        "params": "AM.TSLA"
    }
    ws.send(json.dumps(channel_data))
    print("\nConnected...")
    connection_log.write(f'Logged In @ {datetime.now()}\n')
    connection_log.close()

def on_error(ws, error):
    print(error)

def on_close(ws):
    global connection_log
    tiz = timezone('US/Eastern')
    right_now = pytz.utc.localize(datetime.utcnow()).astimezone(tiz)
    right_now = datetime.strftime(right_now, '%H:%M:%S')
    log = _reopen('action.txt')
    connection_log = _reopen('log_on.txt')
    log.write('Lost Connection See Log_on.txt\n')
    connection_log.write(f'Connection Closed {right_now} \nWorking on Re-establishing Connection...@{datetime.now()}\n')
    check_time()
    connection_log.close()
    log.close()
# -----------------------------


if __name__ == '__main__':
    socket = "wss://alpaca.socket.polygon.io/stocks"
    ws = websocket.WebSocketApp(socket,
                                on_open=onn_open,
                                on_message=tesla,
                                on_error=on_error,
                                on_close=on_close
                                )
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
