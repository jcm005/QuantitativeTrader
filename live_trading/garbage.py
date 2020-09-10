import websocket, json, requests, sys
from streamkeys2 import *
import ssl
import dateutil.parser
import access2 as a
import time
from keys import *
from order2 import Order
from trader import QuantTrader, StreamTrader
back_log = None

strm = StreamTrader()
strm.log_scrubber()
ticker = 'TSLA'

def web_socket_sign_on():
    strm.connection_log('trying to sign on ')
    socket = "wss://alpaca.socket.polygon.io/stocks"
    ws = websocket.WebSocketApp(socket,
                                on_open=onn_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close
                                )
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

def check_time():
    global strm

    strm.connection_log('Checking time')
    right_now = strm.localize_time()
    strm.connection_log('Right Now %s' %  (right_now[:2]))

    if 6  < int(right_now[:2]) < 23:
        strm.connection_log('Time is good. The current time is %s' % (right_now))

        try:
            strm.connection_log('Trying to sign on attempt  1')
            web_socket_sign_on()
        except:

            try:
                strm.connection_log('Trying to sign on attempt  2')
                web_socket_sign_on()
            except:
                print('Connection Failed')
    else:
        strm.connection_log('The day has ended')

# -----------------------------------
#  --- WEB-SOCKET FUNCTIONS BELOW ---
#  ----------------------------------


def onn_open(ws):
    global strm,back_log,ticker

    print('Connecting')
    strm.connection_log('Connecting')
    try:
        BackLog = QuantTrader(ticker,price=0,profit=0)
        back_log = BackLog.Back_logger()
        strm.log('Back Log Success')
    except:
        strm.log('Back log failed')

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

    print("Connected")
    strm.connection_log('Connected at %s' % (strm.localize_time()))
    strm.log('Connected at %s' % (strm.localize_time()))

def on_error(ws, error):
    global strm
    strm.connection_log(error)

def on_close(ws):
    global strm
    strm.log('Saving metrics')
    strm.metrics()
    now  = strm.localize_time()
    strm.log('Lost Connection')
    strm.connection_log('Connection Closed at %s' % (now))
    strm.connection_log('Trying to Reconnect')
    check_time()

# -----------------------------
def on_message(ws, message):
    global strm, back_log

# ======================================================
#          GENERIC  INFORMATION

# ------    DO Not edit this     ------
    strm.previous_tick = strm.current_tick
    message = a.clean_and_load(message)
    strm.current_tick = json.loads(message)     # strm.current_tick is the manipulatable data
# ---------------------------------------
    latest_candle = strm.candle_builder()       # Handling of stream data --> into candles
    if latest_candle == None:
        return

# =======================================================
#         START STRATEGY HERE

    qt = QuantTrader('TSLA',strm._high,profit=strm.profit)

    position = a.get_position_for(qt.ticker.upper())
    account = a.get_account()
    buying_power = account['buying_power'].split('.')[0]


# =======================================================
#               Back log volatility buy
# =======================================================
    if back_log != None:
        back_log = qt.Back_logger()
        back_log_order = qt.Back_log_volatility(back_log)
        print(f'Back log is :{back_log_order}')
        back_log = None
        pass
# =======================================================

    strm.log('-- Running Strategies --')
    try:
        strm.log(f'Stream VP : {round(strm.vp)}')
    except:
        pass

# WITH NOT POSITION
    if not position:
        strm.log('There are no shares for %s' % qt.ticker)

        # Running sma1
        qt.Volatility(volatility=strm.vp, ref='sma1', parameter=1)

        # Checking chronic volatility
        if strm.rolling_v_10 != None and strm.rolling_v_10 > .5:
            qt.Climb_the_ladder(ref='ctl')
            qt.Stop_Drop_and_Roll(ref='sdr')

        # Checking for sudden increase in price
        if strm.rolling_high_30 != None:
            qt.Price_jump(ref='pj')

# WITH A POSITION
    else:

        # ============   Grabbing Share Information   ============
        si = a.share_info(qt.ticker.upper())
        # =======================================================

        strm.log('%s Shares of %s @ avg_cost: %s' % (si['qty_pos'], qt.ticker.upper(),si['avg_price']))
        print(f'stream vp : {strm.vp}')

        # Running sma1
        qt.Volatility(volatility=strm.vp, ref='sma1ws',parameter=1)
        # Checking chronic volatility
        if strm.rolling_v_10 != None and strm.rolling_v_10 > .5:
            strm.log('Trying SDR CTL')

            # MAy need to put if statement making sure strm.rolliing_high_30 works

            qt.Stop_Drop_and_Roll(ref='sdrws')
            qt.Climb_the_ladder(ref='ctlws')

        # Checking for sudden increase in price
        if strm.rolling_high_30 != None:
            strm.log('Checking PJ')
            qt.Price_jump(ref='pjws')


# THis works for both

    if strm.rolling_v_10 != None:
        if strm.vp > 1 and strm.rolling_v_10 > .5:
            strm.log('DT')
            strm.log(f'Double standard SMA_1: {strm.vp} roll: {strm.rolling_v_10}\n')
            return

 # =======================================================
 #               OUTRO
 # =======================================================

    positions = a.get_position()
    open_orders = a.get_orders()


    strm.log(f'Number Of Positions Held ::{len(positions)}')
    strm.log(f'Open orders: {len(open_orders)}\n  '
             f'---------------------------------------------\n')

    print(f'Number Of Positions Held :: {len(positions)}')
    print(f'Open orders: {len(open_orders)}\n'
          f' ---------------------------------------------\n')


if __name__ == '__main__':


    socket = "wss://alpaca.socket.polygon.io/stocks"
    ws = websocket.WebSocketApp(socket,
                                on_open=onn_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close
                                )
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
