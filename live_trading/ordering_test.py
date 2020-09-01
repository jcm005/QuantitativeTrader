from order2 import Order

if __name__ == '__main__':
    _high = 500
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



    roll =  .6
    SMA_HIGH_30 = 515
    SMA_HIGH_10 = 515


    if roll > .5:


        if SMA_HIGH_10 - _high >= (SMA_HIGH_10 * .025):
            print(f'STOP DROP AND ROLL CONDITION with NS\n'
                      f' SMA_HIGH_10: {SMA_HIGH_10}\n'
                      f' _high : {_high}\n')

            order_SDR = tsla.buy(order_class='oto', order_type='market',
                                 qty=1, tif='gtc', profit=profit)

            print(order_SDR)




