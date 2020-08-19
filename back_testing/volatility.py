import pandas as pd
from keys import *
import alpaca_trade_api as tradeapi
#import seaborn as sns
import matplotlib.pyplot as plt
import pygal
from datetime import datetime, timedelta
import matplotlib.units as units

import plotly
#========================================
#========================================

# will be measurning volatility as the difference
# between high and low price of the stock
#import format must be in the order of time, ohlc, volume
df= None

#========================================
#========================================

asset = ['TSLA']
time_interval = 'day'
start_date = '2020-01-01'
time_delt = 7
time_period = 32


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

            data_file.write(f'{x}' + ',' + _open + ',' + _high + ',' + _low + ',' + _close + ',' + _volume + '\n')

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

def read_and_clean(df,symbol):
    """Read and cleans the data
     """
    df = pd.read_csv(f'./Data/{symbol}_{time_interval}_intraday_trading.csv')

    df.columns = [col.strip() for col in df.columns]
    df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    return df

def volatility(df,symbol):
    df['volatility'] = df['high'] - df['low']
    df['_hlMean'] = (df['high'] + df['low']) / 2
    df['vola_coeff'] = (df['volatility'] / df['_hlMean']) * 100

    df['day'] = [day[8:10] for day in df.timestamp]
    df['month'] = [month[5:7] for month in df.timestamp]
    df['year'] = [year[:4] for year in df.timestamp]
    df['hour'] = [hour[-8:] for hour in df.timestamp]
    df['time'] = [time[:18] for time in df.timestamp]

    #df['time'] = [time[12:] for time in times]

#================================
#================================
    rolling_mean_10 = df.vola_coeff.rolling(window=10).mean()
    rolling_mean_20 = df.vola_coeff.rolling(window=10).mean()
    #rolling_mean_10 = rolling_mean_10.fillna(rolling_mean_10[9])
    #rolling_mean_20 = rolling_mean_20.fillna(rolling_mean_20[19])
# ================================

    return df

if __name__ =='__main__':
    for symbol in asset:
        data_flusher(asset, time_interval)  # here in case program fails it will not double data
        Acummator(asset, start_date, time_interval, time_delt, time_period)
        df = read_and_clean(df,symbol)
        df = volatility(df,symbol)
        rolling_mean_10 = df.vola_coeff.rolling(window=10).mean()
        rolling_mean_20 = df.vola_coeff.rolling(window=20).mean()

        fig = plotly.subplots.make_subplots(rows=4, cols=1, vertical_spacing=0.2)
        fig['layout']['margin'] = {
            'l': 30, 'r': 10, 'b': 30, 't': 10
        }
        fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}
        print(df['time'])
        fig.append_trace({
            'x': df['time'],
            'y': df['high'],
            'name': 'High',
            'mode': 'lines+markers',
            'type': 'scatter'
        }, 1, 1)
        fig.append_trace({
            'x': df['time'],
            'y': df['vola_coeff'],
            'text': df['time'],
            'name': 'v_factor',
            'mode': 'lines+markers',
            'type': 'scatter'
        }, 2, 1)
        fig.append_trace({
            'x': df['time'],
            'y': rolling_mean_10,
            'text': df['time'],
            'name': 'rolling_v_10',
            'mode': 'lines',
            'type': 'scatter'
        }, 3, 1)
        fig.append_trace({
            'x': df['time'],
            'y': rolling_mean_20,
            'text': df['time'],
            'name': 'rolling_v_20',
            'mode': 'lines',
            'type': 'scatter'
        }, 3, 1)
        #fig.append_trace({'x': df['time'],'y': df['volatility'],'name': 'High','mode': 'lines+markers','type': 'scatter'}, 4, 1)

        fig.show()
        #df.to_csv(f'./Data/{symbol}_{time_interval}_intraday_trading.csv')

#============================================





