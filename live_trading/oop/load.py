import json
import logging
import spy

class Message:

    def __init__(self, message, ticker):

        self.message = json.loads(message)[0]
        self.status = self.message['ev']
        self.ticker = ticker



    def check_status(self):

        if self.status == 'status':
            logging.info(self.message)
            return False
        else:
            pass

    def check_symbol(self):

        if self.status == 'AM':
            if self.message['sym'] == self.ticker:
                return True
            elif self._current_tick['sym'] == 'SPY':
                try:
                    self.spy_500 = spy.Builder(self._current_tick).run()
                    self.spy = True
                except:
                    logging.warning(self._current_tick)
                    logging.warning('Spy Builder Failure/Insert Methodology for SPY_500')
                return False


if __name__ == '__main__':

    message = [{"ev":"AM","sym":"TSLA","v":35177,"av":15407555,"op":446.24,"vw":438.9615,"o":438.72,"c":438.91,"h":439.2199,"l":438.72,"a":441.0544,"z":43,"n":1,"s":1603121220000,"e":1603121280000}]
    data = Message(message)
    status = data.check_status()
    print(status)
    print(data.spy)