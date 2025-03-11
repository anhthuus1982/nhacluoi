import threading

class WebSocketManager:
    def __init__(self):
        self.clients = {}
        self.threads = {}

    def add_client(self, symbol, callback):
        client = WebSocketClient(callback)
        self.clients[symbol] = client
        thread = threading.Thread(target=client.subscribe, args=(symbol,))
        thread.start()
        self.threads[symbol] = thread

    def stop(self):
        for client in self.clients.values():
            client.running = False
        for thread in self.threads.values():
            thread.join()
