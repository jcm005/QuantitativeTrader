import alpaca_trade_api as tradeapi
from streamkeys import *
api = tradeapi.REST('AKF7BISHSY3SBP0M2IS8','URqDMkUgsj4aC9YMw3VwGizmiMfdhbZFPcKb5Gx4', api_version='v2')

response = api.polygon.historic_agg_v2('TSLA', 1, 'day', '2020-06-01', '2020-06-07')
print(response)