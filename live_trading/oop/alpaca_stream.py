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

    def _subscribe(self,channel=None):
        # THIS MAY NOT BE A PRIVATE FUNCTION ASK COLE
        """

        :param channel_data: Websocket prefix + . + channel name like AM.TSLA
        'action': 'subsctibe , 'params': channel you want to subscribe to
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

        return auth_data,channel_data

    def log(self,txt):
        if txt == 'open':
            log.info('Log on Success @ %s' % datetime.now())
        elif txt == 'close':
            log.warning('Connection lost @ %s' % datetime.now())


if __name__ == '__main__':

    wc = WebConnection()
    wc.alpaca_connection()