import os
import ccxt

class Exchange:
    def __init__(self):
        self.exchange = ccxt.bybit({
            'apiKey': os.getenv('API_KEY'),
            'secret': os.getenv('API_SECRET'),
            'enableRateLimit': True,
        })
        # Chỉ dùng leverage nếu giao dịch hợp đồng (linear/inverse)
        try:
            # Ví dụ: đặt leverage 10x cho BTCUSDT (linear)
            self.exchange.set_leverage(10, 'BTCUSDT')
            print("Leverage set successfully for BTCUSDT")
        except Exception as e:
            print(f"Loi dat leverage: {e}")

    def get_balance(self):
        try:
            balance = self.exchange.fetch_balance()
            return balance['total']
        except Exception as e:
            print(f"Loi lay so du: {e}")
            return None
