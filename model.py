class TradingModel:
    def __init__(self, indicators):
        self.indicators = indicators

    def decide(self, symbol, price, sl_percent=0.02, tp_percent=0.03):
        indicators = self.indicators.get_indicators(symbol)
        rsi = indicators['rsi']
        ma = indicators['ma']
        if rsi < 30 and price > ma:
            stop_loss = price * (1 - sl_percent)
            take_profit = price * (1 + tp_percent)
            return {'side': 'buy', 'stop_loss': stop_loss, 'take_profit': take_profit}
        elif rsi > 70 and price < ma:
            stop_loss = price * (1 + sl_percent)
            take_profit = price * (1 - tp_percent)
            return {'side': 'sell', 'stop_loss': stop_loss, 'take_profit': take_profit}
        return None
