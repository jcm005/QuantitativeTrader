from datetime import datetime




class Trader():

    def sign_on(self,ws):
        connection_log = _reopen('log_on.txt')
        auth_data = {
            "action": "auth",
            "params": PAPER_KEY
        }
        ws.send(json.dumps(auth_data))
        channel_data = {
            "action": "subscribe",
            "params": f"AM.{self.symbol}"
        }
        ws.send(json.dumps(channel_data))
        print("\nConnected...")
        connection_log.write(f'Logged In @ {datetime.now()}\n')
        connection_log.close()

    def __init__(self):
        self.symbol = symbol
        self.on_open = self.sign_on


if __name__ == '__main__':
    trader = Trader()
    socket = "wss://alpaca.socket.polygon.io/stocks"
    ws = websocket.WebSocketApp(socket,
                                on_open=trader.on_open,
                                on_message=tesla,
                                on_error=on_error,
                                on_close=on_close
                                )
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
