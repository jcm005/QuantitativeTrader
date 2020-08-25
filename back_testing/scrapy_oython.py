def volatility(self,variable,num,ref):
    """compares the current volatility with the previous volatitlty and takes in a reference number
     the number given is the condition for volatility"""
    if (variable[0] - variable[1]) >= num:
        self.log(f'Volatility Condition >= {num};Satisfied Ref{ref}')
        return true
    else:
        return false



def mod_tesla(self):

    if not self.position:
        if self.high[0] < 900:
            if self.sma_10[0] > 3:
                self.log(f'Lower 900 -- High: {self.high[0]} sma_10: {self.sma_10[0]}')
                self.order = self.buy()
        else:
            if self.sma_10[0] > 3:
                self.log(f'higher 900 -- High: {self.high[0]} sma_10: {self.sma_10[0]}')
                self.order = self.buy()