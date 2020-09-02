from trader import QuantTrader
#price = [i for i in range(0,475)]
price = 10
profit = 10

Tesla = QuantTrader('TSLA',price=price,profit=profit)

back_log = Tesla.Back_logger()
print(back_log)