import websocket, json, requests, sys
from streamkeys2 import *
import ssl
from datetime import datetime
import dateutil.parser
import access2 as a
import time
import pytz
from pytz import timezone
from keys import *
from order2 import Order
from trader import QuantTrader


est = pytz.timezone('US/Eastern')
minutes_processed = {}
minute_candlestick = []
rolling_ten = []
over_night = []
simple_moving_average_10 = []
simple_moving_average_30 = []
current_tick = None
previous_tick = None
in_position = False
back_log = None


candles = open('candle2.txt', 'a')
connection_log = open('log_on2.txt', 'a')
log = open('action2.txt', 'a')
order_log = open('order2.txt','a')

candles.truncate(0)
log.truncate(50)
order_log.truncate(0)



def _reopen(file):
    file_to_repoen = open(file, 'a')
    return file_to_repoen

def time_converter(some_time):

    newtime = datetime.fromtimestamp(some_time / 1000)
    newtimes = newtime.strftime('%Y-%m-%d, %a, %H:%M')
    return newtimes

def check_time():
    connection_log = _reopen('log_on2.txt')
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
    global over_night, back_log
    connection_log = _reopen('log_on2.txt')
    print("\nConnecting --> ")

    try:
        BackLog = QuantTrader('TSLA',price=0,profit=0)
        back_log = BackLog.Back_logger()
    except:
        print('back log fail')

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
    print("Connected <--")
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

    global current_tick, previous_tick, rolling_ten, back_log
    candles = _reopen('candle2.txt')
    log = _reopen('action2.txt')
    order_log = _reopen('order2.txt')


    previous_tick = current_tick
    message = a.clean_and_load(message)
    current_tick = json.loads(message)
# ===================================
    times = current_tick['e']  # DATA TYPE IS INT
    times = time_converter(times)  # CONVERTS TYPE INT INTO DATETIME OBJECT THEN A STRING
# ===================================

    ticker = current_tick['sym']
    open = current_tick['o']
    high = current_tick['h']
    low = current_tick['l']
    close = current_tick['c']
    volatility = current_tick['h'] - current_tick['l']
    hlmean = (current_tick['h'] + current_tick['l']) / 2
    v_factor = (volatility / hlmean) * 100

# ===================================
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
    print(f'{latest_candle}\n')
# ====================================================

    _high = [i['high'] for i in minute_candlestick]
    _v_factor = [i['v_factor'] for i in minute_candlestick]
    _time = minute_candlestick[-1]['time']

# --- PROFIT TREE ---
    if 3000 > _high[-1] >= 1000:
        profit = 100
    elif 1000 > _high[-1] > 850:
        profit = 80
    elif 850 >= _high[-1] > 600:
        profit = 65
    elif 600 >= _high[-1] > 400:
        profit = 40
    elif 400 >= _high[-1]:
        profit = 30
# --- PROFIT TREE ---


# ---- MINUTE VARIANCE ----
    _volatility_coeff = minute_candlestick[-1]['volatilty']
    v_param = (minute_candlestick[-1]['v_factor'] - minute_candlestick[-2]['v_factor'])
    log.write(f'Time: {_time}, High: {_high[-1]}, V_param: {v_param}\n')

# ======================================================
#       ^^^^ GENERIC STRATEGY INFORMATION ^^^^^^
# =======================================================
#                   START STRATEGY HERE
# =======================================================
    Tesla = QuantTrader('TSLA',_high,profit=profit)
    position = a.get_position_for(ticker)
    account = a.get_account()
    buying_power = account['buying_power'].split('.')[0]

# =======================================================
#               Back log volatility buy
# =======================================================
    if back_log:
        back_log_order = Tesla.Back_log_volatility(back_log)
        print(back_log_order)
        back_log = None

# =======================================================
#               STrategy
# =======================================================

    if len(minute_candlestick) > 1:
        volatility_coefficient = (minute_candlestick[-1]['v_factor'] - minute_candlestick[-2]['v_factor'])

# BIG DROP
    try:
        if len(minute_candlestick) > 2:
            big_drop_2 = (minute_candlestick[-3]['high'] - minute_candlestick[-1]['low'])
            if big_drop_2 > 50:
                log.write(f'Big drop 2 -- Active -- :{big_drop_2}\n')

        if len(minute_candlestick) > 4:
            big_drop_4 = (minute_candlestick[-5]['high'] - minute_candlestick[-1]['low'])
            if big_drop_4 > 50:
                log.write(f'Big drop 4 -- Active -- :{big_drop_4}\n')
    except:
        log.write('Big Drop Inactive\n')

# =======================================================
#               INDICATORS
# =======================================================

# =======================================================
#               LOGIC
# =======================================================

    # WITH NO POSITION HERE
    if not position:
        log.write(f'There is no shares for {ticker}\n')
        if _high < 5000:

            order_sma_1 = Tesla.Volatility(volatility_coefficient,parameter=1)
            if order_sma_1 != False:
                log.write(f'Ordered: order_sma_1')
                order_log.write(f'Time: {_time} Ordered Order_sma_1:\n{order_sma_1}\n')
                return


            rolling_v_10 = Tesla.Sma(_v_factor,int=10)
            log.write(f'rolling_v_10: {rolling_v_10}')
            if rolling_v_10 > .5 and rolling_v_10 != False:

                order_ctl = Tesla.Climb_the_ladder()
                order_sdr = Tesla.Stop_Drop_and_Roll()

                if order_ctl != False:
                    log.write(f'Ordered: order_ctl')
                    order_log.write(f'Time: {_time} Ordered Order_ctl:\n{order_ctl}\n')
                    return

                if order_sdr != False:
                    log.write(f'Ordered: order_sdr')
                    order_log.write(f'Time: {_time} Ordered Order_sdr:\n{order_sdr}\n')
                    return

            order_price_Jump = Tesla.Price_jump()
            if order_price_Jump != False:
                log.write(f'Ordered: order_price_jump')
                order_log.write(f'Time: {_time}, Order Price Jump:\n{order_price_Jump}\n')
                return




    # WITH A POSITION
    else:

        qty_pos = position['qty']
        cost_basis = position['cost_basis']
        avg_price = position['avg_entry_price']

        log.write(f'{qty_pos} Shares of {ticker.upper()} @ avg_cost: {avg_price}\n')
        print(f'{qty_pos} Shares of {ticker.upper()} @ {avg_price}')


        if _high < 5000:

            order_sma_1 = Tesla.Volatility(volatility_coefficient, parameter=1)
            if order_sma_1 != False:
                log.write(f'Ordered: order_sma_1')
                order_log.write(f'Time: {_time} Ordered Order_sma_1:\n{order_sma_1}\n')
                return

            rolling_v_10 = Tesla.Sma(_v_factor, int=10)
            log.write(f'rolling_v_10: {rolling_v_10}')
            if rolling_v_10 > .5 and rolling_v_10 != False:

                order_ctl = Tesla.Climb_the_ladder()
                order_sdr = Tesla.Stop_Drop_and_Roll()

                if order_ctl != False:
                    log.write(f'Ordered: order_ctl')
                    order_log.write(f'Time: {_time} Ordered Order_ctl:\n{order_ctl}\n')
                    return

                if order_sdr != False:
                    log.write(f'Ordered: order_sdr')
                    order_log.write(f'Time: {_time} Ordered Order_sdr:\n{order_sdr}\n')
                    return

            order_price_Jump = Tesla.Price_jump()
            if order_price_Jump != False:
                log.write(f'Ordered: order_price_jump')
                order_log.write(f'Time: {_time}, Order Price Jump:\n{order_price_Jump}\n')
                return

    if volatility_coefficient > 1 and rolling_v_10 > .5:
        log.write(f'Double standard SMA_1: {volatility_coefficient} roll: {roll}\n')

        order_double_trouble = tsla.buy(order_class='oto',order_type='market',
                                        qty=1, tif='gtc', profit=profit,
                                        stop_limit_price=_high- (profit /2),
                                        stop_price= _high - (profit/ 2.25),
                                        )
        order_log.write(f'order double trouble:\n{order_double_trouble}\n')
        candles.close()
        log.close()
        order_log.close()
        return

 # =======================================================
 #               OUTRO
 # =======================================================

    positions = a.get_position()
    print(f'Number Of Positions Held :: {len(positions)}')
    log.write(f'Number Of Positions Held ::{len(positions)}\n')
    open_orders = a.get_orders()
    log.write(f'Open orders: {len(open_orders)}\n ---------------\n\n')
    print(f'Open orders: {len(open_orders)}\n ---------------\n')

    #-----------------------
    # close out loggin files
    #-----------------------
    candles.close()
    log.close()
    order_log.close()

if __name__ == '__main__':
    socket = "wss://alpaca.socket.polygon.io/stocks"
    ws = websocket.WebSocketApp(socket,
                                on_open=onn_open,
                                on_message=tesla,
                                on_error=on_error,
                                on_close=on_close
                                )
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
