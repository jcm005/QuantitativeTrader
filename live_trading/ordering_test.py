import access as a
#put initiated order into order sequence
ticker = 'TSLA'
_high  = [400,500,600]

file = open('candles.txt','a')
file.write(f'{_high[2]}')

def intiate_order(
        symbol,
        qty=1,
        order_type='market',
        side=None,
        time_in_force='day',
        limit_price=None,
        stop_price=None,
        order_class=None,
        stop_limit_price=None
):
    '''INTIATION OF AN ORDER TO BE PASSED IN ACCESS.PY PLACE_ORDER COMMAND'''
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
    elif order_class == 'oco':
        order['type'] = 'limit'
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
def order_sequence(order,current_price,order_details='detailed'):
    '''
     FUNCTION TAKES IN A INITIATED ORDER CREATES THE SELL ORDER PAIRING WITH LIMIT
     SET AT SELL_OFF_POINT AND RETURNS DETAILED ORDER WHETHER SIMPLE OR ORIGINAL

    :param order: INITIATED_ORDER SEE STREAM2.PY
    :param sell_off_point: YOUR TAKE PROFIT PARAMETER
    :param order_details: SIMPLE OR DETAILED ORDER INFOMATION DEFUALT == DETIALED
    :return: BUY AND SELL AS ORDER DETAILS
    '''
    print(current_price)
    order_buy = order
    try:
        ordered_B,status = a.place_order(order_buy)
        buy = a.order_details(ordered_B, order_details)
    except:
        return 'Order_Buy_Failed'
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
    if 500 <current_price < 800:
        order_sell['limit_price'] = current_price + 50
    if 200 < current_price < 500:
        order_sell['limit_price'] = current_price + 30
    print(order_sell['limit_price'])
    try:
        ordered_S,status = a.place_order(order_sell)
        sell = a.order_details(ordered_S, order_details)
    except:
        sell = 'Order_Sell_Failed'

    return buy,sell





if __name__ == '__main__':
    order_buy = intiate_order(symbol=ticker,
                                  # order_class='bracket',
                                  # price=_high,
                                  order_type='market',
                                  side='buy',
                                  )


    print(order_sequence(order=order_buy,current_price=_high,order_details='simple'))


    # need a function to clean order details so wwe can then
    # append this iinformation to either a file output or a list







