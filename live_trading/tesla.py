from order import Order
#from order import *

# Order module can also place order so rewrite this in the future


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
            if volatility_coefficient > 1:
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

