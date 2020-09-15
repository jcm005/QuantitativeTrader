import websocket
import ssl
import dateutil.parser

class __WebSocket:

    def __init__(self,socket):
        self._socket = socket
        self.on_open = None
        self.on_message = None
        self.on_close = None
        self.on_error = None

    def create_connection(self):
        '''Creates connection'''
        self._ws = websocket.WebSocketApp(self._socket,
                                    on_open=on_open,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)

    def run_socket(self):
        '''Runs the socket'''
        self._ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})



if __name__ == '__main__':
    ws = __WebSocket(socket="wss://alpaca.socket.polygon.io/stocks")
    ws.create_connection()
    ws.run_socket()