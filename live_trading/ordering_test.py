from order import Order

if __name__ == '__main__':
    current_price = 2070
    tsla = Order('TSLA', current_price)


    buy = tsla.buy(order_class='bracket',
                   order_type='market',
                   qty='1', tif='gtc',
                # USE THIS ONLY FOR LIMIT TYPE ORDER
                   limit_price=0,
                # UNCOMMENT, FOR THE USE OF BRACKETT ORDERS
                   profit=100,
                   stop_limit_price=current_price - 2,
                   stop_price=current_price - .5
                   )
print(buy)


