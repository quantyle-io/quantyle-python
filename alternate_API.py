from datetime import datetime as dt
from client import BacktestClient

# Strategy Parameters
signals = {
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
    ]
}

dates = {
    'start_date': str(dt(year=2022, month=9, day=1, hour=8, minute=1).isoformat()),
    'end_date': str(dt(year=2022, month=9, day=10, hour=8, minute=1).isoformat())
}

trade_rules = {
    'buy_trigger': 'macd1 < macd2',
    'sell_trigger': 'macd1 > macd2'
}

broker = {
    'exchange_id': 'GDAX',
    'product_id': 'BTC-USD', 
    'trade_size': 1,
    'taker_fee': 0.0001,
    'maker_fee': 0.0001,
}

for i in range (10):

    process = BacktestClient(signals, dates, trade_rules, broker)
    # live=True for live execution, live=False for backtests (False by default)
    response = process.run()