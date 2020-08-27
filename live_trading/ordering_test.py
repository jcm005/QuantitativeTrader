from order import Order

if __name__ == '__main__':
    current_price = 2200
    tsla = Order('TSLA', current_price)


    buy = tsla.buy(order_class='oto',
                   order_type='market',
                   qty=1, tif='gtc',
                # USE THIS ONLY FOR LIMIT TYPE ORDER
                   limit_price=0,
                # UNCOMMENT, FOR THE USE OF BRACKETT ORDERS
                   profit=100,
                   #stop_limit_price=current_price - 51,
                   #stop_price=current_price - 40
                   )

   # buy = tsla.buy(order_type='limit',
    #               qty=1, tif='day',
     #              limit_price = current_price + 10,
      #             extended_hours = True,
       #            )
print(buy)


