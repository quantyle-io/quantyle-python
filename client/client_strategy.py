# from backend.quantyle_lib import strategy
import requests

'''
 'exchange_id': 'GDAX', 
'product_id': 'BTC-USD', 
'starting_cash': 500000, 
'taker_fee': 0.0001, 
'maker_fee': 0.0001, 
'signals': [{'id': 'MACD', 
    'name': 'macd', 
    'color': '#a7595f', 
    'p': {'inputs': ['close'], 
        'fast_period': 9, 
        'slow_period': 26}, 
    }], 
'buy_trigger': 'macd < 40', 
'sell_trigger': 'macd > 40', 
'start_date': str(start_date), 
'end_date': str(end_date)
'''

class broker():
    def __init__(self, strategy):
        self.exchange_id = strategy['exchange_id']
        self.product_id = strategy['product_id']
        self.starting_cash = strategy['starting_cash']
        self.taker_fee = strategy['taker_fee']
        self.maker_fee = strategy['maker_fee']


class strategy():
    def __init__(self, strategy):
        self.strategy = strategy
        self.strategy_name = strategy['signals']['name']
        self.buy_trigger = strategy['buy_trigger']
        self.sell_trigger = strategy['sell_trigger']


class example_MACD_strategy(strategy):
    def __init__(self, fast_period, slow_period):
        signals = [
            {
                "id": "fast_ema",
                "type": "ema",
                "period": fast_period,
                "color": "blue",
            },
            {
                "id": "slow_ema",
                "type": "ema",
                "period": slow_period,
                "color": "green",
            },
        ]
        buy_trigger = "self.df.fast_ema > self.df.slow_ema"
        sell_trigger = "self.df.fast_ema < self.df.slow_ema"
        super().__init__(signals, buy_trigger, sell_trigger)
