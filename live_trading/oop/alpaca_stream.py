import json
import logging as log
import websocket
from datetime import datetime

class WebConnection:

    def __init__(self,api_key):

        self._api = api_key
        log.basicConfig(level=log.DEBUG,
                            filename='connect.log',
                            filemode='a')

    def _subscribe(self,ws,channel=None):
        # THIS MAY NOT BE A PRIVATE FUNCTION ASK COLE
        """

        :param ws: websocket object must be passed for the sending of data
        :param channel: in the format of 'AM' + '<desired ticker>'
        :return: None
        """

        if channel == None:
            log.warning('Please supply a channel for more infomation please see polygon.io/websockets')
        auth_data = {
            'action': 'auth',
            'params': self._api
        }
        channel_data = {
            'action': 'subscribe',
            'params': channel
        }

        ws.send(json.dumps(auth_data))
        ws.send(json.dumps(channel_data))

    def log(self,txt):
        if txt == 'open':
            log.info('Log on Success @ %s' % datetime.now())
        elif txt == 'close':
            log.warning('Connection lost @ %s' % datetime.now())


if __name__ == '__main__':

    wc = WebConnection()
    wc.alpaca_connection()