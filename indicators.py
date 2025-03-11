import pandas as pd
import talib
from config import RSI_PERIOD, MA_PERIOD

class Indicators:
    def __init__(self, exchange):
        self.exchange = exchange
        self.ohlcv_cache = {}

    def fetch_ohlcv(self, symbol, timeframe='1h', limit=100):
        cache_key = f"{symbol}_{timeframe}_{limit}"
        if cache_key not in self.ohlcv_cache or time.time() - self.ohlcv_cache[cache_key]['timestamp'] > 60:
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit)
                    self.ohlcv_cache[cache_key] = {'data': ohlcv, 'timestamp': time.time()}
                    return ohlcv
                except ccxt.NetworkError as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(2 ** attempt)
        return self.ohlcv_cache[cache_key]['data']

    def get_indicators(self, symbol, timeframe='1h'):
        ohlcv = self.fetch_ohlcv(symbol, timeframe)
        close = pd.Series([x[4] for x in ohlcv])
        if len(close) < RSI_PERIOD:
            raise Exception("Du lieu khong du de tinh RSI")
        rsi = talib.RSI(close, timeperiod=RSI_PERIOD)[-1]
        ma = talib.SMA(close, timeperiod=MA_PERIOD)[-1]
        return {'rsi': rsi, 'ma': ma}
