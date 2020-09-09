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

tsla = StreamTrader()
tsla.log_scrubber()

def web_socket_sign_on(self):

    socket = "wss://alpaca.socket.polygon.io/stocks"
    ws = websocket.WebSocketApp(socket,
                                on_open=onn_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close
                                )
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

def check_time():
    global tsla

    tsla.connection_log('Checking time')
    right_now = tsla.localize_time()
    tsla.connection_log('Right Now %s' %  (right_now[:2]))

    if 6  < int(right_now[:2]) < 23:
        tsla.connection_log('Time is good. The current time is %s' % (right_now))

        try:
            tsla.connection_log('Trying to sign on attempt  1')
            web_socket_sign_on()
        except:

            try:
                tsla.connection_log('Trying to sign on attempt  2')
                web_socket_sign_on()
            except:
                print('Connection Failed')
    else:
        tsla.connection_log('The day has ended')

# -----------------------------------
#  --- WEB-SOCKET FUNCTIONS BELOW ---
#  ----------------------------------


def onn_open(ws):
    global tsla,back_log

    print('Connecting')
    tsla.connection_log('Connecting')
    try:
        BackLog = QuantTrader('TSLA',price=0,profit=0)
        back_log = BackLog.Back_logger()
        tsla.log('Back Log Success')
    except:
        tsla.log('Back log failed')

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
    tsla.connection_log('Connected at %s' % (tsla.localize_time()))
    tsla.log('Connected at %s' % (tsla.localize_time()))

def on_error(ws, error):
    global tsla
    tsla.connection_log(error)

def on_close(ws):
    global tsla
    tsla.log('Saving metrics')
    tsla.metrics()
    now  = tsla.localize_time()
    tsla.log('Lost Connection')
    tsla.connection_log('Connection Closed at %s' % (now))
    tsla.connection_log('Trying to Reconnect')
    check_time()

# -----------------------------
def on_message(ws, message):
    global tsla, back_log
    tsla.log('\n')
# ======================================================
#          GENERIC  INFORMATION

# ------    DO Not edit this     ------
    tsla.previous_tick = tsla.current_tick
    message = a.clean_and_load(message)
    tsla.current_tick = json.loads(message)
    latest_candle = tsla.candle_builder()

# ---------------------------------------

    if latest_candle == None:
        return
    print(latest_candle)

# =======================================================
#         START STRATEGY HERE
    tsla.log('Starting Strategy\ninitiating QuantTrader')

    # we might be able to initiate this inside the init function of StreamTrader
    Tesla = QuantTrader('TSLA',tsla._high,profit=tsla.profit)
    tsla.log('Position and account check')
    position = a.get_position_for(Tesla.ticker.upper())
    account = a.get_account()
    buying_power = account['buying_power'].split('.')[0]
    tsla.log('Check Cleared')


# =======================================================
#               Back log volatility buy
# =======================================================
    tsla.log('Checking back log')
    #back_log = Tesla.Back_logger()
    if back_log:
        back_log = Tesla.Back_logger()
        back_log_order = Tesla.Back_log_volatility(back_log)
        print(f'Back log is :{back_log_order}')
        back_log = None
        pass


    if not position:

        tsla.log('There are no shares for %s' % Tesla.ticker)
        if Tesla.Volatility(volatility_coefficient,parameter=1) != False:
            order = Tesla.buy_order(ref='sma1')
            tsla.log(f'Ordered: order_sma_1')
            tsla.order_log(f'Time: {_time} Ordered Order_sma_1:\n{order}\n')
            return

        if tsla.rolling_v_10 > .5:

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

        tsla.log('%s Shares of %s @ avg_cost: %s' % (qty_pos, Tesla.ticker.upper(),avg_price))
        print('%s Shares of %s @ avg_cost: %s' % (qty_pos, Tesla.ticker.upper(),avg_price))

        print(f'tsla vp : {tsla.vp}')
        if Tesla.Volatility(tsla.vp, parameter=1) != False:
            print('Tesla.volatility satisfied')
            order = Tesla.buy_order(ref='sma1ws')
            tsla.log('volatility order ')
            order_log.write(f'Time: {tsla.time} Ordered Order_sma_1 ws:\n{order}\n')
            return

        # this may be a redundant thing if statement

        if tsla.rolling_v_10 != None and tsla.rolling_v_10 > .5:
            print('WS')
            if Tesla.Climb_the_ladder() != False:
                print('ws climb the ldder')
                order = Tesla.buy_order(ref='ctlws')
                tsla.log(f'Ordered: order_ctl ws')
                tsla.order_log(f'Time: {tsla.time} Ordered Order_ctl ws:\n{order}\n')
                return

            if Tesla.Stop_Drop_and_Roll() != False:
                order = Tesla.buy_order(ref='sdrws')
                tsla.log(f'Ordered: order_sdr ws')
                tsla.order_log(f'Time: {tsla.time} Ordered Order_sdr ws:\n{order}\n')
                return
        else:
            pass

        if tsla.rolling_high_30 != None:
            if Tesla.Price_jump() != False:
                order = Tesla.buy_order(ref='pjws')
                tsla.log(f'Ordered: order_price_jump ws')
                tsla.order_log(f'Time: {tsla.time}, Order Price Jump ws:\n{order}\n')
                return


# THis works for both
    if tsla.rolling_v_10 != None:
        if tsla.vp > 1 and tsla.rolling_v_10 > .5:
            tsla.log(f'Double standard SMA_1: {tsla.vp} roll: {tsla.rolling_v_10}\n')

            return

 # =======================================================
 #               OUTRO
 # =======================================================

    positions = a.get_position()
    print(f'Number Of Positions Held :: {len(positions)}')
    tsla.log(f'Number Of Positions Held ::{len(positions)}')
    open_orders = a.get_orders()
    tsla.log(f'Open orders: {len(open_orders)}\n ---------------\n\n')
    print(f'Open orders: {len(open_orders)}\n ---------------\n')

    #-----------------------
    # close out loggin files
    #-----------------------


if __name__ == '__main__':


    socket = "wss://alpaca.socket.polygon.io/stocks"
    ws = websocket.WebSocketApp(socket,
                                on_open=onn_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close
                                )
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
