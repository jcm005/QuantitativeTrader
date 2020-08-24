import websocket, json, requests, sys
from streamkeys import *
import ssl
from datetime import datetime
import dateutil.parser
import access as a
import time
import pytz
from pytz import timezone




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

    #   CHECK FOR OPEN ORDERS AND RETURN IF ANY ARE PRESENT
    # ===================================
    global current_tick, previous_tick
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
    print(f'$$::{latest_candle}\n')
# ===================================
    _high = minute_candlestick[-1]['high']
    _time = minute_candlestick[-1]['time']
    _volatility_coeff = minute_candlestick[-1]['volatilty']
    v_param = (minute_candlestick[-1]['v_factor'] - minute_candlestick[-2]['v_factor'])
    log.write(f'Time: {_time}, High: {_high}, V_param: {v_param}\n')
# ===================================


    from order import Order
    TSLA = Order('TSLA',high)


# =======================================================
#                   START STRATEGY HERE
# =======================================================
    position,position_num = a.get_position_for(ticker)
    qty_pos = position['qty']
    print('\n')

    log.write(f'Position --> {position_num}\n')
    # NEEDS AT LEAST TWO CANDLESTICKS TO BE RAN
    if len(minute_candlestick) > 1:
        # candles = _reopen('candle.txt')
        # log = _reopen('stream2.txt')
        # connection_log = _reopen('log_on.txt')
        volatility_coefficient = (minute_candlestick[-1]['v_factor'] - minute_candlestick[-2]['v_factor'])
        print('Strategy is Running...')
        log.write('Strategy Activated..\n\n')
    else:
        print('Pending Action\n')
        return

    # ========kl;'===============================================

    # =======================================================
    # WITH NO POSITION HERE
    if not position:
        log.write('There is no position\n')
        if _high < 5000:
            print(volatility_coefficient)
            if volatility_coefficient > 1:
                log.write(f'Condition: Volatility Coeff: {volatility_coefficient}\n')
                log.write(f'Attempting Buy --(Ref #1)-- Price:{_high}, Volatility_Coeff: {volatility_coefficient}\n')

                #TSLA.buy(order_type='market',qty=1,tif='gtc',profit=100)

                order_buy = intiate_order(symbol=ticker, order_type='market', side='buy')
                buy, sell = order_sequence(order_buy, current_price=_high, order_details='simple')
                log.write(f'{buy}\n')
                log.write(f'\n{sell}')

    # WITH A POSITION
    else:
        log.write(f'{qty_pos} Shares of {ticker.upper()}')
        print(f'{qty_pos} Shares of {ticker.upper()}')
        print(f'High: {_high}')

        if _high < 300:

            if volatility_coefficient > 1:
                log.write(
                    f'Attempting an order of {ticker} @ {_high} with volatility_coefficent of {volatility_coefficient}\n')
                log.write('Buying Ref #1 with position\n')
                order_buy = intiate_order(symbol=ticker, order_type='market', side='buy')
                buy, sell = order_sequence(order_buy, current_price=_high, order_details='simple')
                log.write(f'{buy}\n')
                log.write(f'\n{sell}\n')
        if 300 < _high < 500:
            if volatility_coefficient > 1:
                log.write(
                    f'Attempting an order of {ticker} @ {_high} with volatility_coefficent of {volatility_coefficient}\n')
                log.write('Buying Ref #2\n')
                order_buy = intiate_order(symbol=ticker, order_type='market', side='buy')
                buy, sell = order_sequence(order_buy, current_price=_high, order_details='simple')
                log.write(f'{buy}\n')
                log.write(f'\n{sell}')
        if 500 <= _high < 4000:
            if volatility_coefficient > 1:
                print(
                    f'Attempting an order of {ticker} @ {_high} with v_param of {volatility_coefficient}')
                print('Buying Ref #4')
                order_buy = intiate_order(symbol=ticker, order_type='market', side='buy')
                buy, sell = order_sequence(order_buy, current_price=_high, order_details='simple')
                print(f'{buy}\n')
                print(f'\n{sell}')
    # ----------------------------------------------------
    # TEST BUY UNDER HERE
    # ----------------------------------------------------
    # else:
    #   # REAL ORDER TERRITORY HERE USE THIS AS BASELINE
    #   print(f'Attempting an order of {ticker} @ {_high}')
    #   print('buying ref -- TEST BUY --')
    #   order_buy = intiate_order(symbol=ticker,order_type='market',side='buy')
    #   buy,sell = order_sequence(order_buy,current_price=_high,order_details='simple')
    #   print(f'{buy}\n')
    #   print(f'\n{sell}')

    position = a.get_position()
    print(f'NumBer Of Positions Held ::{len(position)}\n')
    log.write(f'NumBer Of Positions Held ::{len(position)}\n\n')
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
