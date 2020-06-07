import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
from keys import *
import pandas as pd

# for preparing output of all contents of the dataframe recieved
pd.set_option('max_rows', None)

# make a function that automatically makes end date today

start_date = '2020-05-28'
asset = ['AMZN']  # ticker symbols to be testedp
time_interval = 'minute'  # collect data per each ---
time_delt = 7  # difference in days between end time and start time, lowe number is suggested so no data lost
time_period = 2  # time_period * time_delt = number of days need for data accumualation


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

        # for manually grabbing data and doing an analysis by hand or ipython file
        data = api.polygon.historic_agg_v2(symbol, 1, time_interval, train_date_s, train_date_e)
        for bar in data:
            x = str(bar.timestamp)
            y = x[:-6]
            # catenuated the last few items from the time stamp
            # to removve errors unsure what this information provides
            _open = str(bar.open)
            _high = str(bar.high)
            _low = str(bar.low)
            _close = str(bar.close)
            _volume = str(bar.volume)

            data_file.write(f'{y}' + ',' + _open + ',' + _high + ',' + _low + ',' + _close + ',' + _volume + '\n')

    data_file.close()


def Acummator(asset, start_date, time_interval, time_delt, time_period):
    """A better way of advancing time """

    print(f'Grabbing...Data...')

    end = ''  # INTIALIZING EMPYTY END STRING
    future = timedelta(days=time_delt)  # INTERVALS DATA GRABBER WILL RUN
    pre_start = datetime.strptime(start_date, '%Y-%m-%d')  # CONVERT STRING TO DATETIM

    if time_period == 0:
        end = pre_start + future  # INCREASING END TIME BY A WEEK
        final_end = str(end)[:-9]  # FORMATTING  END TIME BY DROPPING NON FORMATED TIME
        # PREVENTS 500 ERROR

        final_start = str(pre_start)[:-9]
        grab_data(asset, final_start, final_end, time_interval)
    else:
        try:
            for i in range(0, time_period):  # 33o for prensent  INSERT DESIRED AMOUNT OF ITERATIN YOU WANT
                end = pre_start + future  # INCREASING END TIME BY A WEEK
                final_end = str(end)[:-9]  # FORMATTING  END TIME BY DROPPING NON FORMATED TIME
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

    data_flusher(asset, time_interval)
    print('Cleaned')
    Acummator(asset, start_date, time_interval, time_delt, time_period)

    ans = input('Do you wanna flush: y/n?\n')

    if ans == 'y':

        data_flusher(asset, time_interval)
    else:
        pass
