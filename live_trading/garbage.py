import websocket, json, requests, sys
from streamkeys2 import *
import ssl
from datetime import datetime
import dateutil.parser
import access as a
import time
import pytz
from pytz import timezone
from order import Order
from keys import *

# this works tesla cannot be imported has to be inside
est = pytz.timezone('US/Eastern')
minutes_processed = {}
minute_candlestick = []
rolling_ten = []
over_night = []
current_tick = None
previous_tick = None
in_position = False
back_log_volatility = False


candles = open('candle2.txt', 'a')
connection_log = open('log_on2.txt', 'a')
log = open('action2.txt', 'a')
order_log = open('order2.txt','a')


candles.truncate(0)
log.truncate(50)
order_log.truncate(0)


def back_logger(ticker, time_interval='minute'):
    """Retrieves historical data based on passed values of the polygon api

        asset:  pass in your desired ticker symbols
        time_interval =  defaulted to day --> minute, hour,day,month,year
        start and end date in the format 'yyyy-mm-dd'

    """
    import alpaca_trade_api as tradeapi
    from datetime import datetime, timedelta
    global over_night

    raw_past = timedelta(days=1)
    raw_now = datetime.now()
    yesterday = raw_now - raw_past
    start = datetime.strftime(yesterday, '%Y-%m-%d')
    final = datetime.strftime(raw_now, '%Y-%m-%d')
    api = tradeapi.REST(API_KEY, SECRET_KEY, api_version='v2')
    # for manually grabbing data and doing an analysis by hand or ipython file

    data = api.polygon.historic_agg_v2(ticker, 1, time_interval, start, final)


    for bar in data:

        # catenuated the last few items from the time stamp
        # to removve errors unsure what this information provides
        _open = str(bar.open)
        _high = str(bar.high)
        _low = str(bar.low)
        _close = str(bar.close)
        _volume = str(int(bar.volume))

        x = str(bar.timestamp)
        hour = int(x[11:13])
        day = int(x[8:10])
        if day == int(start[-2:]): # Checks if it is previous day or not
            if hour >= 16:
                time = x[:19]
                over_night.append({
                    'time': time,
                    'high': _high,
                })
        else:
            if hour <= 7:
                time2 = x[:19]
                over_night.append({
                    'time': time2,
                    'high': _high,
                })

    return over_night

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
    global over_night
    connection_log = _reopen('log_on2.txt')
    log = _reopen('action.txt')
    order_log = _reopen('order2.txt')

    print("\nConnecting --> ")

    try:
        over_night = back_logger('TSLA')
        if len(over_night) > 2:
            last_night = (over_night[0])
            this_morn = (over_night[-1])
            log.write(f'Back logging successful\n Last_night: {last_night}\n this morn: {this_morn}\n')
            if int(this_morn['high'].split('.')[0]) - int(last_night['high'].split('.')[0]) >= 25:
                back_log_volatility = True
                log.write('Volatile pre-markets initiating order --> buy')
            else:
                pass

    except:
        log.write('Back Logging Function Failed\n')
        print('Back Logging Function Failed')


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
    log = _reopen('action2.txt')
    connection_log = _reopen('log_on2.txt')
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


    global current_tick, previous_tick, rolling_ten, back_log_volatility
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

    print(f'{latest_candle}\n')

    _high = minute_candlestick[-1]['high']
    _time = minute_candlestick[-1]['time']
    _volatility_coeff = minute_candlestick[-1]['volatilty']
    log.write(f'Time: {_time}, High: {_high}, Volatility_Coefficient: {_volatility_coeff}\n')

    v_param = (minute_candlestick[-1]['v_factor'] - minute_candlestick[-2]['v_factor'])
    log.write(f'Time: {_time}, High: {_high}, V_param: {v_param}\n')

# =======================================================
#                   START STRATEGY HERE
# =======================================================
    tsla = Order('TSLA',_high)
    position = a.get_position_for(ticker)
    account = a.get_account()

    buying_power = account['buying_power'].split('.')[0]
    print(buying_power)

    try:
        if back_log_volatility:
            log.write(f'Condition: Back log volatility.\n')
            log.write(f'Attempting Buy --(Ref NoRef)-- Price:{_high}: back log volatility {back_log_volatility}\n')

            order_bV = tsla.buy(order_type='market',
                               order_class='bracket',
                               qty=1, tif='day',
                               limit_price= 0,
                               # ===  OTO / Bracket   ===
                              # profit=100,
                               # ===   Bracket   ===
                               #stop_limit_price=_high - 51, stop_price=_high - 40,
                               )
            order_log.write(f'{order_bV}\n')


    except:
        print('failure back log volatility order')

    # BUYING POWER CONDITION MAY NOT HAVE TO BE MET BECAUE OF ALAPCA RULES

    if len(minute_candlestick) > 1 and int(buying_power) > _high:
        volatility_coefficient = (minute_candlestick[-1]['v_factor'] - minute_candlestick[-2]['v_factor'])
        try:
            rolling_ten.append(minute_candlestick[-1]['v_factor'])
        except:
            log.write('Rolling ten appending failure\n')
        print('-- Active --')
        log.write('Strategy Activated..\n')
    else:
        print('Collecting Information')
        return
#BIG DROP
    try:
        if len(minute_candlestick) > 2:
            big_drop_2 = (minute_candlestick[-3]['high'] - minute_candlestick[-1]['low'])
        if len(minute_candlestick) > 4:
            big_drop_4 = (minute_candlestick[-5]['high'] - minute_candlestick[-1]['low'])

        if big_drop_2 > 50:
            log.write(f'Big drop 2 -- Active -- :{big_drop_2}\n')
        if big_drop_4 > 50:
            log.write(f'Big drop 4 -- Active -- :{big_drop_4}\n')
    except:
        log.write('Big drop inactive\n')

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
#               WITH NO POSITION HERE
# =======================================================

    if not position:
        log.write(f'There is no shares for {ticker}\n')
        if _high < 5000:
            if volatility_coefficient > 1:
                log.write(f'Condition: Volatility Coeff: {volatility_coefficient}\n')
                log.write(f'Attempting Buy --(Ref #1)-- Price:{_high}, Volatility_Coeff: {volatility_coefficient}\n')

                order_1 = tsla.buy(order_type='market',
                             order_class='bracket',
                             qty=1,tif='gtc',
                             limit_price=0,
                        # ===  OTO / Bracket   ===
                             profit= 100,
                        # ===   Bracket   ===
                                   stop_limit_price=_high - 51, stop_price=_high - 40,
                             )
                log.write(f'Reference 1 Order: {order_1}\n')
                print(order_1)

            try:
                if roll > .5:
                    log.write(f'Condition: Rolling_10: {roll}\n')
                    log.write(f'Attempting Buy --(Ref #101)-- Price:{_high}, rolling_10: {roll}\n')
                    order_rolling = tsla.buy(order_type='market',
                                       order_class='bracket',
                                       qty=1, tif='gtc',
                                       # ===  OTO / Bracket   ===
                                       profit=100,
                                       # ===   Bracket   ===
                                       stop_limit_price=_high - 51, stop_price=_high - 40,
                                       )
                    log.write(f'Reference 1 Order: {order_rolling}\n')
                    print(order_rolling)
            except:
                log.write('Rolling_10 inactive\n')


# =======================================================
#               WITH POSITION HERE
# =======================================================

    else:
        qty_pos = position['qty']
        cost_basis = position['cost_basis']
        avg_price = position['avg_entry_price']

        log.write(f'{qty_pos} Shares of {ticker.upper()} @ avg_cost: {avg_price}\n')
        print(f'{qty_pos} Shares of {ticker.upper()} @ {avg_price}')
        print(f'High: {_high}')


        if _high < 300:

            if volatility_coefficient > 1:
                log.write(
                    f'Attempting an order of {ticker} @ {_high} with volatility_coefficent of {volatility_coefficient}\n')
                log.write('Buying Ref #1 with position\n')
                order_2 = tsla.buy(order_type='market',
                                   order_class='bracket',
                                   qty=3, tif='gtc',
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
        try:
            if roll > .5:
                log.write(f'Condition: Rolling_10: {roll}\n')
                log.write(f'Attempting Buy --(Ref #101)-- Price:{_high}, rolling_10: {roll}\n')
                order_rolling = tsla.buy(order_type='market',
                                         order_class='bracket',
                                         qty=1, tif='gtc',
                                         limit_price=0,
                                         # ===  OTO / Bracket   ===
                                         profit=100,
                                         # ===   Bracket   ===
                                         stop_limit_price=_high - 51, stop_price=_high - 40,
                                         )
                log.write(f'Reference 1 Order: {order_rolling}\n')
                print(order_rolling)
        except:
            log.write('Rolling_10 inactive\n')

        try:
            if (avg_price - _high) > 80:
                log.write(f'Price is lower than avg share price: {avg_price - _high}\n')
                order_buy = intiate_order(symbol=ticker, order_type='market', side='buy')
                buy, sell = order_sequence(order_buy, current_price=_high, order_details='simple')
                order_log.write(f'{buy}\n')
                order_log.write(f'\n{sell}\n')
        except:
            log.write('No share deficit\n')


    positions = a.get_position()
    print(f'Number Of Positions Held :: {len(positions)}')
    log.write(f'Number Of Positions Held ::{len(positions)}\n')
    open_orders = a.get_orders()
    log.write(f'Open orders: {len(open_orders)}\n ---------------\n\n')
    print(f'Open orders: {len(open_orders)}\n ---------------\n')


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
