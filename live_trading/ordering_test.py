from order2 import Order

if __name__ == '__main__':
    _high = 2200
    tsla = Order('TSLA', _high)

    if 3000 > _high >= 1000:
        profit = 100
    elif 1000 > _high > 850:
        profit = 100
    elif 850 >= _high > 600:
        profit = 75
    elif 600 >= _high > 400:
        profit = 50
    elif 400 >= _high:
        profit = 30

    order_ctl = tsla.buy(order_class='bracket', order_type='market',
                         qty=1, tif='gtc',
                         profit=profit,
                         stop_limit_price=_high- (profit /2),
                         stop_price= _high - (profit/ 2.25))

    print(order_ctl)


