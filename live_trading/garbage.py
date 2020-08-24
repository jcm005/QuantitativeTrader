import websocket, json, requests, sys
from streamkeys import *
import ssl
from datetime import datetime
import dateutil.parser
import access as a
import time
import pytz
from pytz import timezone
from order import Order

# this works tesla cannot be imported has to be inside
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


def tesla(ws, message):
    candles = _reopen('candle.txt')
    log = _reopen('action.txt')

    global current_tick, previous_tick
    previous_tick = current_tick
    message = a.clean_and_load(message)

    current_tick = json.loads(message)

    times = current_tick['e']  # DATA TYPE IS INT
    times = time_converter(times)  # CONVERTS TYPE INT INTO DATETIME OBJECT THEN A STRING

    ticker = current_tick['sym']
    open = current_tick['o']
    high = current_tick['h']
    low = current_tick['l']
    close = current_tick['c']
    volatility = current_tick['h'] - current_tick['l']
    hlmean = (current_tick['h'] + current_tick['l']) / 2
    v_factor = (volatility / hlmean) * 100

    # ADDS NEW CANDLESTICK AS TIME PROGRESSES
    minute_candlestick.append({
        'symbol': ticker,
        'time': times,
        'open': open,
        'high': high,
        'low': low,
        'close': close,
        'hlmean': round(hlmean, ndigits=2),
        'volatilty': round(volatility, ndigits=2),
        'v_factor': round(v_factor, ndigits=2),
    })
    latest_candle = minute_candlestick[-1]
    candles.write(f'{latest_candle}\n')
    print(f'$$::{latest_candle}\n')

    _high = minute_candlestick[-1]['high']
    _time = minute_candlestick[-1]['time']
    _volatility_coeff = minute_candlestick[-1]['volatilty']
    log.write(f'Time: {_time}, High: {_high}, Volatility_Coefficient: {_volatility_coeff}\n')



# =======================================================
#                   START STRATEGY HERE
# =======================================================
    tsla = Order('TSLA',_high)

    position = a.get_position_for(ticker)


    if len(minute_candlestick) > 1:
        volatility_coefficient = (minute_candlestick[-1]['v_factor'] - minute_candlestick[-2]['v_factor'])
        print('Strategy is Running...')
        log.write('Active\n')
    else:
        print('Collecting Information')
        return

# =======================================================
#               WITH NO POSITION HERE
# =======================================================

    if not position:
        log.write('no_position\n')

        if _high < 5000:
            log.write(f'VC: {volatility_coefficient}')

            log.write(f'Condition: Volatility Coeff: {volatility_coefficient}\n')
            log.write(f'Attempting Buy --(Ref #1)-- Price:{_high}, Volatility_Coeff: {volatility_coefficient}\n')

            order_1 = tsla.buy(order_type='market',
                         order_class='bracket',
                         qty=1,tif='gtc',
                         limit_price=0,
                    # === bracket order options  ===
                         profit=100,
                         stop_limit_price=_high - 51, stop_price=_high - 40,
                         )
# tsla has its own logging function. implement this once this is integrated
            log.write(f'Reference 1 Order: {order_1}\n')
            print(order_1)


# =======================================================
#               WITH POSITION HERE
# =======================================================

    else:
        print(f'{qty_pos} Shares of {ticker.upper()}')
        print(f'High: {_high}')

        if _high < 300:

            if volatility_coefficient > 1:
                log.write(
                    f'Attempting an order of {ticker} @ {_high} with volatility_coefficent of {volatility_coefficient}\n')
                log.write('Buying Ref #1 with position\n')
                order_2 = tsla.buy(order_type='market',
                                   order_class='bracket',
                                   qty=5, tif='gtc',
                                   limit_price=0,
                                   # === bracket order options  ===
                                   profit=30,
                                   stop_limit_price=_high - 11, stop_price=_high - 10,
                                   )
                log.write(f'Reference 2 Order: {order_2}\n')
                print(order_2)

        if 300 < _high < 500:
            if volatility_coefficient > 1:
                log.write(
                    f'Attempting an order of {ticker} @ {_high} with volatility_coefficent of {volatility_coefficient}\n')
                log.write('Buying Ref #3\n')

                order_3 = tsla.buy(order_type='market',
                                   order_class='bracket',
                                   qty=2, tif='gtc',
                                   limit_price=0,
                                   # === bracket order options  ===
                                   profit=50,
                                   stop_limit_price=_high - 21, stop_price=_high - 20,
                                   )
                log.write(f'Reference 3 Order: {order_3}\n')
                print(order_3)


        if 500 <= _high < 4000:
            if volatility_coefficient > 1:
                print(
                    f'Attempting an order of {ticker} @ {_high} with volatility_coefficent of {volatility_coefficient}')
                print('Buying Ref #4')
                order_4 = tsla.buy(order_type='market',
                                   order_class='bracket',
                                   qty=1, tif='gtc',
                                   limit_price=0,
                                   # === bracket order options  ===
                                   profit=100,
                                   stop_limit_price=_high - 51, stop_price=_high - 40,
                                   )
                log.write(f'Reference 4 Order: {order_4}\n')
                print(order_4)


    position = a.get_position()
    print(f'NumBer Of Positions Held ::{len(position)}\n')
    open_orders = a.get_orders()
    prin(len(open_orders))
    #log.write(f'Open Orders {open_orders}\n')
   # log.write(f'Current Positions: {position}\n')
    candles.close()
    log.close()



if __name__ == '__main__':
    socket = "wss://alpaca.socket.polygon.io/stocks"
    ws = websocket.WebSocketApp(socket,
                                on_open=onn_open,
                                on_message=tesla,
                                on_error=on_error,
                                on_close=on_close
                                )
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
