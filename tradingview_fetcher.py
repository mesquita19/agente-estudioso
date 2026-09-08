"""
Buscador de velas do TradingView
"""

import pandas as pd
import random
from datetime import datetime, timedelta
from typing import List, Dict

class TradingViewFetcher:
    def __init__(self):
        pass
    
    def get_candles(self, asset: str, timeframe: str, from_date: str, to_date: str) -> List[Dict]:
        """Gera dados realistas para demonstração"""
        candles = []
        start = datetime.strptime(from_date, "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(to_date, "%Y-%m-%d %H:%M:%S")
        
        base_prices = {
            "EURUSD": 1.09,
            "GBPUSD": 1.27,
            "USDJPY": 145.0,
            "GBPJPY": 185.0,
            "AUDUSD": 0.65,
            "USDCAD": 1.36,
            "BTCUSD": 56000,
            "ETHUSD": 2300
        }
        
        base_price = base_prices.get(asset, 100.0)
        current_price = base_price
        interval_minutes = int(timeframe)
        
        current_time = start
        while current_time <= end:
            change = (current_price * 0.0005) * random.choice([1, -1, 1, -1, 0.5])
            open_price = current_price
            close_price = current_price + change
            high_price = max(open_price, close_price) + abs(change) * 0.5
            low_price = min(open_price, close_price) - abs(change) * 0.5
            
            candles.append({
                'open': round(open_price, 5),
                'high': round(high_price, 5),
                'low': round(low_price, 5),
                'close': round(close_price, 5),
                'volume': int(1000 + (5000 * abs(change))),
                'timestamp': current_time.strftime("%Y-%m-%d %H:%M:%S")
            })
            
            current_price = close_price
            current_time += timedelta(minutes=interval_minutes)
        
        return candles