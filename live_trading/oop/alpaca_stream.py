import json
import logging as log
import websocket
from datetime import datetime
import spy

class WebConnection:
    """
    will insert in the future multiple channel susbription methods
    """
    def __init__(self,api_key):

        self._api = api_key
        log.basicConfig(level=log.DEBUG,
                            filename='connect.log',
                            filemode='a')

    def _subscribe(self, ws, type='AM.', channel=None):
        # THIS MAY NOT BE A PRIVATE FUNCTION ASK COLE
        """

        :param ws: websocket object must be passed for the sending of data
        :param channel: in the format of 'AM' + '<desired ticker>'
        :return: None
        """

        if channel == None:
            log.warning('Please supply a channel. for more information please see polygon.io/websockets')

        auth_data = {
            'action': 'auth',
            'params': self._api
        }
        channel_data = {
            'action': 'subscribe',
            'params': type + channel
        }
        ws.send(json.dumps(auth_data))
        ws.send(json.dumps(channel_data))

    def _subscribe_w_spy(self, ws, channel=None):
        """Allows for dual channel subscription for indicator comparison
            will only support AM. type
        """

        if channel == None:
            log.warning('Please supply a channel for more information please see polygon.io/websockets')

        auth_data = {
            'action': 'auth',
            'params': self._api
        }
        channel_data = {
            'action': 'subscribe',
            'params':  'AM.SPY' + ',' + 'AM.' + channel,
        }
        ws.send(json.dumps(auth_data))
        ws.send(json.dumps(channel_data))


class Message:

    def __init__(self, message, ticker):

        self.message = json.loads(message)[0]
        self.status = self.message['ev']
        self.ticker = ticker
        self.spy = None

    def check_status(self):

        if self.status == 'status':
            log.info(self.message)
            return False
        else:
            return True

    def check_symbol(self):

        if self.status == 'AM':
            if self.message['sym'] == self.ticker:
                return True
            elif self.message['sym'] == 'SPY':
                try:
                    self.spy_500 = spy.Builder(self.message).run()
                    self.spy = True
                except:
                    log.warning(self.message)
                    log.warning('Spy Builder Failure/Insert Methodology for SPY_500')
                return False

if __name__ == '__main__':

    wc = WebConnection()
    wc.alpaca_connection()