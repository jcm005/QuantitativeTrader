import websocket, json, requests, sys
from streamkeys import *
import ssl
from datetime import datetime
import dateutil.parser
import access as a
import time
import pytz
from pytz import timezone
from keys import *

# DO I DARE PUT IN BACKFILLING DATA Function -- i did i did it


est = pytz.timezone('US/Eastern')
minutes_processed = {}
minute_candlestick = []
rolling_ten = []
over_night = []
current_tick = None
previous_tick = None
in_position = False
back_log_volatility = False

candles = open('candle.txt', 'a')
connection_log = open('log_on.txt', 'a')
log = open('action.txt', 'a')
order_log = open('order.txt','a')

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

def intiate_order(
        symbol,
        qty=1,
        order_type='market',
        side=None,
        time_in_force='day',
        limit_price=None,
        stop_price=None,
        order_class=None,
        stop_limit_price=None):
    '''INTIATION OF AN ORDER TO BE PASSED IN ACCESS.PY PLACE_ORDER COMMAND'''
    global log
    log.write('Initiating Order\n')
    order = {
        'symbol': symbol,
        'qty': qty,
        'side': side,
        'type': order_type,
        'time_in_force': time_in_force,
        # append this into the dictionary if order type is limit or stop limit
        # 'stop_price':int,
        # https://alpaca.markets/docs/api-documentation/api-v2/orders/
    }

    if order_class == 'bracket':
        order['order_class'] = 'bracket'
        order['take_profit'] = {
            'limit_price': limit_price
        }
        order['stop_loss'] = {
            'stop_price': stop_price,
            'limit_price': stop_limit_price
        }
    # OCO ORDER CURRENTLY NOT WORKING HOWEVER NOT MY MAIN CONCERN ATM

    elif order_class == 'oco':
        order['type'] = order_type
        order['order_class'] = 'oco'
        order['take_profit'] = {
            'limit_price': limit_price
        }
        order['stop_loss'] = {
            'stop_price': stop_price,
            'limit_price': stop_limit_price
        }
        return order
    else:
        pass

    if order_type == 'market':
        return order
    if order_type == 'limit':
        order['limit_price'] = limit_price
        return order
    if order_type == 'stop':
        order['limit_price'] = limit_price
        order['stop_price'] = stop_price
        return order


def order_sequence(order,
                   current_price,
                   order_details='detailed'):
    '''
     FUNCTION TAKES IN A INITIATED ORDER CREATES THE SELL ORDER PAIRING WITH LIMIT
     SET AT SELL_OFF_POINT AND RETURNS DETAILED ORDER WHETHER SIMPLE OR ORIGINAL

    :param order: INITIATED_ORDER SEE STREAM2.PY
    :param sell_off_point: YOUR TAKE PROFIT PARAMETER
    :param order_details: SIMPLE OR DETAILED ORDER INFOMATION DEFUALT == DETIALED
    :return: BUY AND SELL AS ORDER DETAILS
    '''
    order_buy = order
    global log
    _reopen(log)
    log.write('Sending Order\n')
    try:
        ordered_B, status = a.place_order(order_buy)
        buy = a.order_details(ordered_B, order_details)
    except:
        buy = 'Order_Buy_Failed'
    # --------------------------
    #       Sell Order
    # --------------------------
    order_sell = order
    order_sell['side'] = 'sell'
    order_sell['type'] = 'limit'
    # --------------------------------------------------
    #  INITIATING PROFIT MARGINS
    # --------------------------------------------------
    if current_price >= 800:
        order_sell['limit_price'] = current_price + 100
    if 500 < current_price < 800:
        order_sell['limit_price'] = current_price + 50
    if 200 < current_price < 500:
        order_sell['limit_price'] = current_price + 30
    try:
        log.write(f'Order Sell = :{order_sell}')
        ordered_S, status = a.place_order(order_sell)
        sell = a.order_details(ordered_S, order_details)
        log.write(f'sell  = :{sell}')
    except:
        sell = 'Order_Sell_Failed'

    return buy, sell


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
    global over_night
    connection_log = _reopen('log_on.txt')
    log = _reopen('action.txt')

    print("\nConnecting --> ")

    try:
        back_logger('TSLA')
        over_night = back_logger('TSLA')
        print(len(over_night))

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

    candles = _reopen('candle.txt')
    log = _reopen('action.txt')
    order_log = _reopen('order.txt')

#   CHECK FOR OPEN ORDERS AND RETURN IF ANY ARE PRESENT
# ===================================
    global current_tick, previous_tick, rolling_ten, back_log_volatility
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
# ===================================
    _high = minute_candlestick[-1]['high']
    _time = minute_candlestick[-1]['time']
    # difference between prices
    _volatility_coeff = minute_candlestick[-1]['volatilty']
    #differnece in the volatility percentage of price
    v_param = (minute_candlestick[-1]['v_factor'] - minute_candlestick[-2]['v_factor'])
    log.write(f'Time: {_time}, High: {_high}, V_param: {v_param}\n')
# ======================================================
#       ^^^^ GENERIC STRATEGY INFORMATION ^^^^^^
# =======================================================
#                   START STRATEGY HERE
# =======================================================
    position = a.get_position_for(ticker)
    account = a.get_account()

    buying_power = account['buying_power'].split('.')[0]
   # print(buying_power)

# =======================================================
#               Back log volatility buy
# =======================================================
    try:
        if back_log_volatility:
            log.write(f'Condition: Back log volatility.\n')
            log.write(f'Attempting Buy --(Ref #10101)-- Price:{_high}: back log volatility {back_log_volatility}\n')
            order_buy = intiate_order(symbol=ticker, order_type='market', side='buy')
            buy, sell = order_sequence(order_buy, current_price=_high, order_details='simple')
            order_log.write(f'{buy}\n')
            order_log.write(f'\n{sell}')

    except:
        print('failure back log volatility')

# =======================================================
#               STrategy
# =======================================================

    if len(minute_candlestick) > 1 and int(buying_power) > _high:
        volatility_coefficient = (minute_candlestick[-1]['v_factor'] - minute_candlestick[-2]['v_factor'])
        try:
            rolling_ten.append(minute_candlestick[-1]['v_factor'])
        except:
            log.write('Rolling ten appending failure\n')
        print('-- Active --')
        log.write('-- Strategy Activated --\n')
    else:
        print('Pending Action\n')
        return

# BIG DROP
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
#               LOGIC
# =======================================================

    # WITH NO POSITION HERE
    if not position:
        log.write(f'There is no shares for {ticker}\n')
        print('NS')
        if _high < 5000:
            if volatility_coefficient > 1:
                log.write(f'Condition: Volatility Coeff: {volatility_coefficient}\n')
                log.write(f'Attempting Buy --(Ref #1)-- Price:{_high}, Volatility_Coeff: {volatility_coefficient}\n')
                order_buy = intiate_order(symbol=ticker, order_type='market', side='buy')
                buy, sell = order_sequence(order_buy, current_price=_high, order_details='simple')
                order_log.write(f'{buy}\n')
                order_log.write(f'\n{sell}')

            try:
                if roll > .5:
                    log.write(f'Condition: Rolling_10: {roll}\n')
                    log.write(f'Attempting Buy --(Ref #101)-- Price:{_high}, rolling_10: {roll}\n')
                    order_buy = intiate_order(symbol=ticker, order_type='market', side='buy')
                    buy, sell = order_sequence(order_buy, current_price=_high, order_details='simple')
                    order_log.write(f'{buy}\n')
                    order_log.write(f'\n{sell}')
            except:
                log.write('Rolling_10 inactive\n')

    # WITH A POSITION
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
                order_buy = intiate_order(symbol=ticker, order_type='market', side='buy')
                buy, sell = order_sequence(order_buy, current_price=_high, order_details='simple')
                order_log.write(f'{buy}\n')
                order_log.write(f'\n{sell}\n')
        if 300 < _high < 500:
            if volatility_coefficient > 1:
                log.write(
                    f'Attempting an order of {ticker} @ {_high} with volatility_coefficent of {volatility_coefficient}\n')
                log.write('Buying Ref #2\n')
                order_buy = intiate_order(symbol=ticker, order_type='market', side='buy')
                buy, sell = order_sequence(order_buy, current_price=_high, order_details='simple')
                order_log.write(f'{buy}\n')
                order_log.write(f'\n{sell}')

        if 500 <= _high < 4000:
            if volatility_coefficient > 1:
                print(
                    f'Attempting an order of {ticker} @ {_high} with v_param of {volatility_coefficient}')
                print('Buying Ref #4')
                order_buy = intiate_order(symbol=ticker, order_type='market', side='buy')
                buy, sell = order_sequence(order_buy, current_price=_high, order_details='simple')
                order_log.write(f'{buy}\n')
                order_log.write(f'\n{sell}')

            try:
                if roll > .5:
                    log.write(f'Condition: Rolling_10: {roll}\n')
                    log.write(f'Attempting Buy --(Ref #101)-- Price:{_high}, rolling_10: {rolling_10}\n')
                    order_buy = intiate_order(symbol=ticker, order_type='market', side='buy')
                    buy, sell = order_sequence(order_buy, current_price=_high, order_details='simple')
                    order_log.write(f'{buy}\n')
                    order_log.write(f'\n{sell}\n')
            except:
                pass
    # NOT IDEAL BUT IT MAY WORK
        # maybe use close or low price....????
    #  SHARE DEFICIT

        try:
            if (avg_price - _high) > 80:
                log.write(f'Price is lower than avg share price: {avg_price - _high}\n')
                order_buy = intiate_order(symbol=ticker, order_type='market', side='buy')
                buy, sell = order_sequence(order_buy, current_price=_high, order_details='simple')
                order_log.write(f'{buy}\n')
                order_log.write(f'\n{sell}\n')
        except:
            log.write('No share deficit\n')


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
