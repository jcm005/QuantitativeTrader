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
from trader import QuantTrader, StreamTrader

st = StreamTrader()
class WebSocketStreaming():

    def __init__(self):
        self.st = StreamTrader()



def web_socket_sign_on(self):

    socket = "wss://alpaca.socket.polygon.io/stocks"
    ws = websocket.WebSocketApp(socket,
                                on_open=onn_open,
                                on_message=tesla,
                                on_error=on_error,
                                on_close=on_close
                                )
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

def check_time():
    global st
    st.connection_log('Checking time')
    right_now = st.localize_time()
    st.connection_log('Right Now %s' %  (right_now[:2]))

    if 6  < int(right_now[:2]) < 23:
        st.connection_log('Time is good. The current time is %s' % (right_now))

        try:
            st.connection_log('Trying to sign on attempt  1')
            web_socket_sign_on()
        except:

            try:
                st.connection_log('Trying to sign on attempt  2')
                web_socket_sign_on()
            except:
                print('Connection Failed')
    else:
        st.connection_log('The day has ended')

# -----------------------------------
#  --- WEB-SOCKET FUNCTIONS BELOW ---
#  ----------------------------------
def onn_open(ws):
    global st

    print('connecting')
    try:
        BackLog = QuantTrader('TSLA',price=0,profit=0)
        back_log = BackLog.Back_logger()
    except:
        st.log('Back log failed')

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
    st.connection_log('Connected at %s' % (st.localize_time()))

def on_error(ws, error):
    global st
    st.connection_log(error)

def on_close(ws):
    global st

    now  = st.localize_time()
    st.log('lost connection')
    st.connection_log('Connection Closed at %s' % (now))
    st.connection_log('Trying to Reconnect')
    check_time()

# -----------------------------
def tesla(ws, message):

    tsla = StreamTrader()
    tsla.previous_tick = tsla.current_tick

    message = a.clean_and_load(message)
    tsla.current_tick = json.loads(message)

    latest_candle = tsla.candle_builder()
    tsla.candle_log(latest_candle)
    print(f'{latest_candle}\n')

# ====================================================

    _high = [i['high'] for i in minute_candlestick]
    _v_factor = [i['v_factor'] for i in minute_candlestick]
    _time = minute_candlestick[-1]['time']

    profit = tsla.profit_tree(self._high[-1])


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
        print(f'Back log is :{back_log_order}')
        back_log = None
        pass

# =======================================================
#               STrategy
# =======================================================

    if len(minute_candlestick) > 1:
        volatility_coefficient = (minute_candlestick[-1]['v_factor'] - minute_candlestick[-2]['v_factor'])
        pass

# =======================================================
#               INDICATORS
# =======================================================

    rolling_v_10 = Tesla.Sma(_v_factor, int=10)

# =======================================================
#               LOGIC
# =======================================================

    if not position:

        log.write(f'There is no shares for {ticker}\n')
        log.write(f'rolling_v_10: {rolling_v_10}')

        if Tesla.Volatility(volatility_coefficient,parameter=1) != False:
            order = Tesal.buy_order(ref='sma1')
            log.write(f'Ordered: order_sma_1')
            order_log.write(f'Time: {_time} Ordered Order_sma_1:\n{order}\n')
            return

        if rolling_v_10 > .5:

            if Tesla.Climb_the_ladder() != False:
                order = Tesla.buy_order(ref='ctl')
                log.write(f'Ordered: order_ctl')
                order_log.write(f'Time: {_time} Ordered Order_ctl:\n{order}\n')
                return

            if Tesla.Stop_Drop_and_Roll() != False:
                order = Tesla.buy_order(ref='sdr')
                log.write(f'Ordered: order_sdr')
                order_log.write(f'Time: {_time} Ordered Order_sdr:\n{order}\n')
                return
            pass

        if Tesla.Price_jump() != False:
            order = Tesla.buy_order(ref='pj')
            log.write(f'Ordered: order_price_jump')
            order_log.write(f'Time: {_time}, Order Price Jump:\n{order}\n')
            return

    # WITH A POSITION
    else:

        qty_pos = position['qty']
        cost_basis = position['cost_basis']
        avg_price = position['avg_entry_price'].split('.')[0]

        log.write(f'{qty_pos} Shares of {ticker.upper()} @ avg_cost: {avg_price}\n')
        print(f'{qty_pos} Shares of {ticker.upper()} @ {avg_price}')

        if Tesla.Volatility(volatility_coefficient, parameter=1) != False:
            order = Tesal.buy_order(ref='sma1ws')
            log.write(f'Ordered: order_sma_1 ws')
            order_log.write(f'Time: {_time} Ordered Order_sma_1 ws:\n{order}\n')
            return

        if rolling_v_10 > .5:

            if Tesla.Climb_the_ladder() != False:
                order = Tesla.buy_order(ref='ctlws')
                log.write(f'Ordered: order_ctl ws')
                order_log.write(f'Time: {_time} Ordered Order_ctl ws:\n{order}\n')
                return

            if Tesla.Stop_Drop_and_Roll() != False:
                order = Tesla.buy_order(ref='sdrws')
                log.write(f'Ordered: order_sdr ws')
                order_log.write(f'Time: {_time} Ordered Order_sdr ws:\n{order}\n')
                return
            pass

        if Tesla.Price_jump() != False:
            order = Tesla.buy_order(ref='pjws')
            log.write(f'Ordered: order_price_jump ws')
            order_log.write(f'Time: {_time}, Order Price Jump ws:\n{order}\n')
            return

# THis works for both

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
