from pybit import WebSocket
import time

class WebSocketClient:
    def __init__(self, callback):
        self.callback = callback
        self.ws = None
        self.running = False
        self.connect()

    def connect(self):
        self.ws = WebSocket("wss://stream.bybit.com/realtime")

    def subscribe(self, symbol):
        self.running = True
        self.ws.subscribe(f"trade.{symbol}", self.handle_message)
        while self.running:
            if not self.ws.connected:
                self.reconnect()
            self.ws.ping()  # Giu ket noi song
            time.sleep(10)

    def handle_message(self, msg):
        try:
            price = float(msg['data'][0]['price'])
            self.callback(price)
        except Exception as e:
            print(f"Loi WebSocket: {e}")
            self.reconnect()

    def reconnect(self):
        max_retries = 5
        for attempt in range(max_retries):
            try:
                self.ws = WebSocket("wss://stream.bybit.com/realtime")
                self.subscribe(self.ws.subscriptions[0].split('.')[1])
                print("Ket noi lai WebSocket thanh cong!")
                return
            except Exception as e:
                time.sleep(2 ** attempt)
        raise Exception("Khong the ket noi lai WebSocket sau 5 lan thu!")
