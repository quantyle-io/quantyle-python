from datetime import datetime as dt
from client import QuantyleClient

# Strategy Parameters
strategy = {
    'start_date': str(dt(year=2020, month=9, day=1, hour=8, minute=1).isoformat()),
    'end_date': str(dt(year=2022, month=9, day=10, hour=8, minute=1).isoformat()),
    'exchange_id': 'GDAX',
    'product_id': 'BTC-USD', 
    'starting_cash': 500000,
    'trade_size': 1,
    'taker_fee': 0.0001,
    'maker_fee': 0.0001,
    'signals': [
        {'id': 'MACD', 
        'name': 'macd1', 
        'color': '#a7595f', 
        'p': {'inputs': ['close'], 
            'fast_period': 9, 
            'slow_period': 26}, 
        },
        {'id': 'MACD',
        'name': 'macd2', 
        'color': '#44ea11', 
        'p': {'inputs': ['close'], 
            'fast_period': 18, 
            'slow_period': 52}, 
        }
    ],
    'buy_trigger': 'macd1 < macd2',
    'sell_trigger': 'macd1 > macd2'
}

process = QuantyleClient(strategy)
# live=True for live execution, live=False for backtests (False by default)
response = process.run(live=False)