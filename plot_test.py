import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import pandas as pd
import json
import ast


import plotly.graph_objects as go
from plotly.subplots import make_subplots


def data_sender():
    some_list = []
    columns = ['symbol', 'time', 'open', 'high', 'low', 'close', 'hlmean', 'volatility', 'v_factor']
    file = open('candle.txt', 'r')
    lines = file.readlines()
    for line in lines:
        dd = ast.literal_eval(line)
        some_list.append(dd)
    high = []
    time = []
    volatility_coeff = []
    volatility = []
    for i in some_list:
        high.append(i['high'])
        time.append(i['time'][12:])
        volatility_coeff.append(i['v_factor'])
        volatility.append(i['volatilty'])
    return time,high,volatility_coeff
time, high,volatility_coeff = data_sender()

fig = make_subplots(rows=3,cols=1,
                    subplot_titles=('High','v_factor'))
fig.add_trace(go.Scatter(
    x=time,
    y=high,
    name='High'
),row=1,col=1)

fig.add_trace(go.Scatter(
    x=time,
    y=volatility_coeff,
    name='v_fact'
),row=2,col=1)
#fig.add_trace(go.Scatter(
   # x=time,
   # y=volatility,
   # name='volatility'
#),row=3,col=1)

fig.show()