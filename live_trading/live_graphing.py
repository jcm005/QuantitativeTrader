import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
from dash.dependencies import Input, Output
import ast
import pandas as pd

# pip install pyorbital

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
    low = []
    volatility_coeff = []
    volatility = []
    for i in some_list:
        high.append(i['high'])
        time.append(i['time'][12:])
        low.append(i['low'])
        volatility_coeff.append(i['v_factor'])
        volatility.append(i['volatilty'])
    return time,high,low, volatility_coeff, volatility

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    html.Div([
        html.H4('Volatility Analysis'),
        html.Div(id='live-update-text'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=10*1000, # in milliseconds
            n_intervals=0
        )
    ])
)


@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_metrics(n):

    style = {'padding': '5px', 'fontSize': '16px'}
    return [
        html.Span('High:', style=style),
        html.Span('V_factor:', style=style),
        html.Span('Time:', style=style)
    ]


# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    time1, high,low, v_factor, volatility = data_sender()
    data = {
        'time': [],
        'high': [],
        'low': [],
        'v_factor': [],
        'volatility' : [],
        'rolling_v_10': [],
        'rolling_v_20' : [],

    }

    # Collect some data
    #may be redundeant get rid of this
    for i in range(len(time1)):
        data['time'].append(time1[i])
        data['high'].append(high[i])
        data['v_factor'].append(v_factor[i])
        data['low'].append(low[i])
        data['volatility'].append(volatility[i])

    rolling_v = pd.DataFrame(data['v_factor'])
    rolling_10 = rolling_v[0].rolling(window=10).mean()
    print(rolling_10)



    # Create the graph with subplots
    fig = plotly.subplots.make_subplots(rows=3, cols=1, vertical_spacing=0.2)
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 10
    }
    fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}

    fig.append_trace({
        'x': data['time'],
        'y': data['high'],
        'name': 'High',
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 1, 1)
    fig.append_trace({
        'x': data['time'],
        'y': data['v_factor'],
        'text': data['time'],
        'name': 'v_factor',
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 2, 1)
    fig.append_trace({
        'x': data['time'],
        'y': data['low'],
        'name': 'low',
        'mode':'lines+markers'


    }, 1, 1)
    fig.append_trace({
        'x': data['time'],
        'y': rolling_10,
        'name': 'rolling',
        'mode': 'lines+markers'

    }, 3, 1)


    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
