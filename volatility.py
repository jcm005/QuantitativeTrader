import pandas as pd
#import seaborn as sns
import matplotlib.pyplot as plt
import pygal
from data_grabber import *
import matplotlib.units as units
#========================================
#========================================

# will be measurning volatility as the difference
# between high and low price of the stock
#import format must be in the order of time, ohlc, volume

#========================================
#========================================
asset = ['AMZN']
time_interval = 'minute'
df= None

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
    times = df.timestamp
    time = df['time'] = [time[12:] for time in times]

#================================
#================================
    rolling_mean_10 = df.vola_coeff.rolling(window=5).mean()
    rolling_mean_20 = df.vola_coeff.rolling(window=10).mean()
    #rolling_mean_10 = rolling_mean_10.fillna(rolling_mean_10[9])
    #rolling_mean_20 = rolling_mean_20.fillna(rolling_mean_20[19])
# ================================
# ================================
    fig, axs = plt.subplots(4, figsize=(12, 12))
    fig.suptitle(
        f'{symbol}:: n--> {(time[0][:10])} {time[-1:][:10]}')
    fig.subplots_adjust(hspace=.5)
    plt.xticks(ticks=None)
    axs[0].plot(time, df.high )
    axs[0].set_title('High')

    axs[1].plot(times, df.vola_coeff)
    axs[1].set_title('Volatility Coefficent')
    axs[1].set_ylabel('Percentage of Volatiltiy')

    axs[2].plot(time, rolling_mean_10, rolling_mean_20)
    axs[2].set_title('Rolling Means (5) (10)')
    axs[2].set_ylabel('Percentage of Volatiltiy')

    axs[3].plot(time, df.volume)
    axs[3].set_title('Volume')
# ================================
# ================================
    if __name__ == '__main__':
        fig.savefig(f'./Analysis/{symbol}_{time_interval}.png')
    return df
if __name__ =='__main__':
    for symbol in asset:
        df = read_and_clean(df,symbol)
        df = volatility(df,symbol)
        #df.to_csv(f'./Data/{symbol}_{time_interval}_intraday_trading.csv')

#============================================





