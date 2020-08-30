try:
    if (avg_price - _high) > 80:
        log.write(f'Price is lower than avg share price: {avg_price - _high}\n')
        order_buy = intiate_order(symbol=ticker, order_type='market', side='buy')
        buy, sell = order_sequence(order_buy, current_price=_high, order_details='simple')
        order_log.write(f'{buy}\n')
        order_log.write(f'\n{sell}\n')
except:
    log.write('No share deficit\n')