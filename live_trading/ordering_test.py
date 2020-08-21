from order import Order

if __name__ == '__main__':
    current_price = 2000
    tsla = Order('TSLA', current_price)


    buy = tsla.buy(order_class=None,
                   order_type='limit',
                   qty='1', tif='gtc',
                # USE THIS ONLY FOR LIMIT TYPE ORDER
                   limit_price=current_price -100,
                # UNCOMMENT, FOR THE USE OF BRACKETT ORDERS
                   profit=0,
                   stop_limit_price=None,
                   stop_price=None
                   )
print(buy)


