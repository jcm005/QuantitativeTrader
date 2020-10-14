import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
from streamkeys import *
import pandas as pd

pd.set_option('max_rows', None)

start_date = '2020-10-12'
asset = ['TSLA']
time_interval = 'minute'
time_delt = 1  # difference in days between end time and start time, lowe number is suggested so no data lost
time_period = 1  # time_period * time_delt = number of days need for data accumualation


def grab_data(asset, train_date_s, train_date_e, time_interval='day'):
    """Retrieves historical data based on passed values of the polygon api

        asset:  pass in your desired ticker symbols
        time_interval =  defaulted to day --> minute, hour,day,month,year
        start and end date in the format 'yyyy-mm-dd'

    """
    api = tradeapi.REST(API_KEY, SECRET_KEY, api_version='v2')

    for symbol in asset:
        file_path = f'./Data/{symbol}_{time_interval}_intraday_trading.csv'
        data_file = open(file_path, 'a')
        data = api.polygon.historic_agg_v2(symbol, 1, time_interval, train_date_s, train_date_e)
        for bar in data:
            x = str(bar.timestamp)
            y = x[:-6]
            if y[-8:] == '00:00:00':
                y = y[:10]+ ' ' +  '09:00:00'
                print(y)

            _open = str(bar.open)
            _high = str(bar.high)
            _low = str(bar.low)
            _close = str(bar.close)
            _volume = str(int(bar.volume))
            data_file.write(f'{y}' + ',' + _open + ',' + _high + ',' + _low + ',' + _close + ',' + _volume + '\n')
    data_file.close()

def Acummator(asset, start_date, time_interval, time_delt, time_period):
    """A better way of advancing time """

    print(f'Grabbing...Data...')
    end = ''
    future = timedelta(days=time_delt)
    pre_start = datetime.strptime(start_date, '%Y-%m-%d')

    if time_period == 0:
        end = pre_start + future
        final_end = str(end)[:-9]
        print(final_end)

        final_start = str(pre_start)[:-9]
        grab_data(asset, final_start, final_end, time_interval)
    else:
        try:
            for i in range(0, time_period):
                print(i)
                end = pre_start + future
                final_end = str(end)[:-9]
                # PREVENTS 500 ERROR

                final_start = str(pre_start)[:-9]
                grab_data(asset, final_start, final_end, time_interval)
                pre_start = end
        except TypeError:
            print(f'The End Date has not existed yet please try a time period < {time_period}')


def data_flusher(asset, time_interval):
    """Removes data from file """

    for symbol in asset:
        file_path = f'./Data/{symbol}_{time_interval}_intraday_trading.csv'

        clean = open(file_path, 'w')
        clean.truncate(0)

    clean.close()


if __name__ == '__main__':

    print('Performing data_grabber test with inputted parameters')
    data_flusher(asset, time_interval)
    print('Cleaned')
    Acummator(asset, start_date, time_interval, time_delt, time_period)
    ans = input('Do you want to flush: y/n?\n')
    if ans == 'y':
        data_flusher(asset, time_interval)
    else:
        pass
