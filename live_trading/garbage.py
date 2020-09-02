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
back_log_volatility = True

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
    global over_night, back_log_volatility
    connection_log = _reopen('log_on2.txt')
    log = _reopen('action2.txt')
    print("\nConnecting --> ")

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

    #there will be a back log failure on mondays


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

    candles = _reopen('candle2.txt')
    log = _reopen('action2.txt')
    order_log = _reopen('order2.txt')

    global current_tick, previous_tick, rolling_ten, back_log_volatility, simple_moving_average_10, simple_moving_average_30
    previous_tick = current_tick
    message = a.clean_and_load(message)

# ====================================

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

    print(f'{latest_candle}\n')
# ====================================================
    _high = minute_candlestick['high']
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

    # ---- DIFFERENCE BETWEEN PRICES ----

    _volatility_coeff = minute_candlestick[-1]['volatilty']

# ---- DIFFERENCE IN THE VOLATILITY COEFFICIENTS ----

    v_param = (minute_candlestick[-1]['v_factor'] - minute_candlestick[-2]['v_factor'])

    log.write(f'Time: {_time}, High: {_high}, V_param: {v_param}\n')

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
    try:
#if statement here with boolean to make sure this runs once
        if back_log_volatility:
            back_log = Tesla.Back_log_volatility(Tesla.Back_logger())
            if back_log:
                back_log_volatility = False
        else:
            log.write(f'Backlog conditions not satisifed')
    except:
            log.write('Back Logging Function Failed\n')
            print('Back Logging Function Failed')

# =======================================================
#               STrategy
# =======================================================

    if len(minute_candlestick) > 1:
        volatility_coefficient = (minute_candlestick[-1]['v_factor'] - minute_candlestick[-2]['v_factor'])
        try:
            rolling_ten.append(minute_candlestick[-1]['v_factor'])
            simple_moving_average_10.append(minute_candlestick[-1]['high'])
            simple_moving_average_30.append(minute_candlestick[-1]['high'])
        except:
            log.write('Rolling_ten and SMA_HIGH appending failure\n')
        print('-- Active --')
        log.write('-- Strategy Activated --\n')
    else:
        print('Pending Action\n')
        return

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

    try:
        if len(rolling_ten) > 10:
            rolling_10 = rolling_ten[-10:]
            summed_up = sum(rolling_10)
            roll = summed_up/10
            log.write(f'Rolling_10: {roll}\n')
    except:
        log.write('Rolling_10 Failure\n')


# =======================================================
#               LOGIC
# =======================================================

    # WITH NO POSITION HERE
    if not position:
        log.write(f'There is no shares for {ticker}\n')
        if _high < 5000:
            if volatility_coefficient > 1:
                log.write(f'Buy Condition high Sma_1: {volatility_coefficient}')
                order_sma_1 = Tesla.buy_order(order_type='market', order_class='oto', qty=1, tif='gtc')
                order.log(f'Time: {_time} order sma 1: \n{order_sma_1}\n')
                return
            try:
                if roll > .5:
                    log.write(f'Condition: Rolling_10: {roll}\n')

                    order_sdr = Tesla.Stop_Drop_and_Roll()
                    order_ctl = Tesla.Climb_the_ladder()

                    if order_sdr:
                        order.log(f'Time: {_time} order_sdr:\n{order_sdr}\n')
                        return
                    elif order_ctl:
                        order.log(f'Time: {_time} order_ctl:\n{order_ctl}\n')
                        return
                    else:
                        pass
            except:
                log.write('Rolling_10 inactive\n')

            order_price_Jump = Tesla.Price_jump()
            if order_price_Jump:
                log.write(f'Price Jump')
                order_log.write(f'Time: {_time}, order price jump:\n{order_price_Jump}\n')
            else:
                pass

    # WITH A POSITION
    else:

        qty_pos = position['qty']
        cost_basis = position['cost_basis']
        avg_price = position['avg_entry_price']

        log.write(f'{qty_pos} Shares of {ticker.upper()} @ avg_cost: {avg_price}\n')
        print(f'{qty_pos} Shares of {ticker.upper()} @ {avg_price}')
        print(f'High: {_high}')


        if _high < 5000:
            if volatility_coefficient > 1:
                log.write(
                    f'Attempting an order of {ticker} @ {_high} with volatility_coefficent of {volatility_coefficient}\n')
                log.write('Buying Ref #1 with position\n')

                order_2 = tsla.buy(order_type='market', order_class='oto',
                                   qty=1, tif='gtc', profit=profit)
                order_log.write(f'Order 1: \n{order_2}\n')
                return

            try:
                if roll > .5:
                    log.write(f'Condition: Rolling_10: {roll}\n')

                    if SMA_HIGH_10 - _high >= (SMA_HIGH_10 * .025):
                        log.write(f'STOP DROP AND ROLL CONDITION with Share\n'
                                  f' SMA_HIGH_10: {SMA_HIGH_10}\n'
                                  f' _high : {_high}\n')

                        order_SDRws = tsla.buy(order_class='oto', order_type='market',
                                             qty=1, tif='gtc', profit=profit)
                        order_log.write(f'order_sdrws:\n{order_SDRws}\n')
                        return

                    if (_high - SMA_HIGH_30) > (_high * .0125):
                        log.write(f'CLIMB WITH LADDER with Share\n'
                                  f' SMA_HIGH_30: {SMA_HIGH_30}\n'
                                  f' _high : {_high}\n')

                        order_ctlws = tsla.buy(order_class='bracket', order_type='market',
                                             qty=1, tif='gtc',
                                             profit=profit,
                                             stop_limit_price=_high - (profit / 2),
                                             stop_price=_high - (profit / 2.25))

                        order_log.write(f'order_ctlws:\n{order_ctlws}\n')
                        return
            except:
                log.write('Rolling_10 inactive\n')

            try:
                if (_high - SMA_HIGH_30) > (_high*.02):
                    log.write(f'Stand alone sudden increase in price'
                              f'_high: {_high} Sma_high_30: {SMA_HIGH_30}\n')

                    order_stand_alone = tsla.buy(order_class='bracket', order_type='market',
                                           qty=1, tif='gtc',
                                           profit=profit,
                                           stop_limit_price=_high - (profit / 2),
                                           stop_price=_high - (profit / 2.25))
                    order_log.write(f'Order_stand_alone:\n {order_stand_alone}\n')
                    return
            except:
                pass

    if volatility_coefficient > 1 and roll > .5:
        log.write(f'Double standard SMA_1: {volatility_coefficient} roll: {roll}\n')

        order_double_trouble = tsla.buy(order_class='oto',order_type='market',
                                        qty=1, tif='gtc', profit=profit,
                                        stop_limit_price=_high- (profit /2),
                                        stop_price= _high - (profit/ 2.25),
                                        )
        order_log.write(f'order double trouble:\n{order_double_trouble}\n')
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
