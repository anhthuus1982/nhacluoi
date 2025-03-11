import ccxt
from config import SYMBOL, LEVERAGE, MIN_BALANCE, MAX_DRAWDOWN
import time

class Exchange:
    def __init__(self, api_key, secret):
        self.exchange = ccxt.bybit({
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True,
        })
        self.set_leverage(SYMBOL, LEVERAGE)
        self.initial_balance = self.get_balance()

    def set_leverage(self, symbol, leverage):
        try:
            self.exchange.set_leverage(leverage, symbol)
        except Exception as e:
            print(f"Loi dat leverage: {e}")

    def get_balance(self):
        try:
            return self.exchange.fetch_balance()['USDT']['free']
        except Exception as e:
            print(f"Loi lay so du: {e}")
            return 0

    def check_drawdown(self):
        current_balance = self.get_balance()
        drawdown = (self.initial_balance - current_balance) / self.initial_balance
        if drawdown > MAX_DRAWDOWN:
            raise Exception("Vuot qua muc drawdown toi da!")
        return drawdown

    def get_position(self, symbol):
        try:
            positions = self.exchange.fetch_positions([symbol])
            return positions[0] if positions else None
        except Exception as e:
            print(f"Loi lay vi the: {e}")
            return None

    def create_order(self, symbol, side, amount, stop_loss=None, take_profit=None):
        self.check_drawdown()
        if self.get_balance() < MIN_BALANCE:
            raise Exception("So du khong du!")
        if self.get_position(symbol):
            print("Da co vi the mo, bo qua!")
            return None
        order = self.exchange.create_market_order(symbol, side, amount)
        if stop_loss:
            self.exchange.create_order(symbol, 'stop', 'sell' if side == 'buy' else 'buy', amount, None, {'stopPrice': stop_loss})
        if take_profit:
            self.exchange.create_order(symbol, 'limit', 'sell' if side == 'buy' else 'buy', amount, take_profit)
        return order

    def get_price(self, symbol):
        max_retries = 5
        for attempt in range(max_retries):
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                return ticker['last']
            except ccxt.NetworkError as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(2 ** attempt)

    def get_profit(self):
        # Gia su tinh loi nhuan don gian
        return self.get_balance() - self.initial_balance

    def get_recent_trades(self):
        # Gia su lay 5 giao dich gan day
        return self.exchange.fetch_my_trades(symbol=SYMBOL, limit=5)
