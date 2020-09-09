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
    strm.log('\n')
# ======================================================
#          GENERIC  INFORMATION

# ------    DO Not edit this     ------
    strm.previous_tick = strm.current_tick
    message = a.clean_and_load(message)
    strm.current_tick = json.loads(message)

    if strm.current_tick['ev'] == 'status':
        strm.log(strm.current_tick)
        strm.connection_log(strm.current_tick)

# ---------------------------------------
    latest_candle = strm.candle_builder()
    if latest_candle == None:
        return
    print(latest_candle)

# =======================================================
#         START STRATEGY HERE
    strm.log('Starting Strategy\ninitiating QuantTrader')

    # we might be able to initiate this inside the init function of StreamTrader
    qt = QuantTrader('TSLA',strm._high,profit=strm.profit)
    strm.log('Position and account check')
    position = a.get_position_for(qt.ticker.upper())
    account = a.get_account()
    buying_power = account['buying_power'].split('.')[0]
    qty_pos = position['qty']
    cost_basis = position['cost_basis']
    avg_price = position['avg_entry_price'].split('.')[0]

    strm.log('Check Cleared')


# =======================================================
#               Back log volatility buy
# =======================================================
    strm.log('Checking back log')
    #back_log = qt.Back_logger()
    if back_log:
        back_log = qt.Back_logger()
        back_log_order = qt.Back_log_volatility(back_log)
        print(f'Back log is :{back_log_order}')
        back_log = None
        pass
#----------------------------------------------------------

    strm.log('-- Running through the strategies --')
    if not position:
        print(f'stream vp : {strm.vp}')
        strm.log('There are no shares for %s' % qt.ticker)
        if qt.Volatility(strm.vp,parameter=1) != False:
            order = qt.buy_order(ref='sma1')
            strm.log(f'Ordered: order_sma_1')
            strm.order_log(f'Time: {strm.time} Ordered Order_sma_1:\n{order}\n')
            return

        if strm.rolling_v_10 > .5:

            if qt.Climb_the_ladder() != False:
                order = qt.buy_order(ref='ctl')
                strm.log(f'Ordered: order_ctl')
                strm.order_log(f'Time: {strm.time} Ordered Order_ctl:\n{order}\n')
                return

            if qt.Stop_Drop_and_Roll() != False:
                order = qt.buy_order(ref='sdr')
                strm.log(f'Ordered: order_sdr')
                strm.order_log(f'Time: {strm.time} Ordered Order_sdr:\n{order}\n')
                return
            pass

        if qt.Price_jump() != False:
            order = qt.buy_order(ref='pj')
            strm.log(f'Ordered: order_price_jump')
            strm.order_loge(f'Time: {strm.time}, Order Price Jump:\n{order}\n')
            return

    # WITH A POSITION
    else:

        strm.log('%s Shares of %s @ avg_cost: %s' % (qty_pos, qt.ticker.upper(),avg_price))
        print(f'stream vp : {strm.vp}')


        qt.Volatility(volatility=strm.vp, ref='sma1ws',parameter=1)


        if strm.rolling_v_10 != None and strm.rolling_v_10 > .5:
            qt.Climb_the_ladder(ref='ctlws')
            qt.Stop_Drop_and_Roll(ref='sdrws')


        if strm.rolling_high_30 != None:

            if qt.Price_jump() != False:
                order = qt.buy_order(ref='pjws')
                strm.log(f'Ordered: order_price_jump ws')
                strm.order_log(f'Time: {strm.time}, Order Price Jump ws:\n{order}\n')
                return


# THis works for both

    if strm.rolling_v_10 != None:
        if strm.vp > 1 and strm.rolling_v_10 > .5:
            strm.log(f'Double standard SMA_1: {strm.vp} roll: {strm.rolling_v_10}\n')

            return

 # =======================================================
 #               OUTRO
 # =======================================================

    positions = a.get_position()
    open_orders = a.get_orders()


    strm.log(f'Number Of Positions Held ::{len(positions)}')
    strm.log(f'Open orders: {len(open_orders)}\n ---------------')

    print(f'Number Of Positions Held :: {len(positions)}')
    print(f'Open orders: {len(open_orders)}\n ---------------\n')


if __name__ == '__main__':


    socket = "wss://alpaca.socket.polygon.io/stocks"
    ws = websocket.WebSocketApp(socket,
                                on_open=onn_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close
                                )
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
