import pandas as pd
from exchange import Exchange
from indicators import Indicators
from model import TradingModel

class Backtest:
    def __init__(self, exchange, symbol, timeframe='1h', limit=1000):
        self.exchange = exchange
        self.symbol = symbol
        self.timeframe = timeframe
        self.limit = limit
        self.indicators = Indicators(exchange)
        self.model = TradingModel(self.indicators)

    def run(self, sl_percent=0.02, tp_percent=0.03):
        ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.timeframe, self.limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        trades = []
        balance = 1000  # So du ban dau gia dinh
        position = None

        for i, row in df.iterrows():
            price = row['close']
            decision = self.model.decide(self.symbol, price, sl_percent, tp_percent)
            if decision and not position:
                position = {
                    'side': decision['side'],
                    'entry_price': price,
                    'stop_loss': decision['stop_loss'],
                    'take_profit': decision['take_profit'],
                    'amount': 0.01
                }
            elif position:
                if (position['side'] == 'buy' and (price <= position['stop_loss'] or price >= position['take_profit'])) or \
                   (position['side'] == 'sell' and (price >= position['stop_loss'] or price <= position['take_profit'])):
                    exit_price = price
                    profit = (exit_price - position['entry_price']) * position['amount'] if position['side'] == 'buy' else \
                             (position['entry_price'] - exit_price) * position['amount']
                    balance += profit
                    trades.append({
                        'entry_time': df['timestamp'].iloc[i-1],
                        'exit_time': df['timestamp'].iloc[i],
                        'side': position['side'],
                        'entry_price': position['entry_price'],
                        'exit_price': exit_price,
                        'profit': profit
                    })
                    position = None

        return {'final_balance': balance, 'trades': pd.DataFrame(trades)}
