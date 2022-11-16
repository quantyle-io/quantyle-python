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






import requests
import json
import time
from .backtest_feed import BacktestFeed

class BacktestClient():
    def __init__(self, url, signals, dates, trade_rules, broker):
        auth_file = open('auth_keys.json')
        auth_data = json.load(auth_file)
        auth_key = auth_data['Auth_token']

        self.host = 'http://localhost:8001/api/'
        self.state_url = 'get-progress/'
        self.url = 'backtest2/'
        self.auth_token = auth_key
        self.session = requests.Session()
        self.strategy = {}
        self.signals = signals
        self.dates = dates
        self.trade_rules = trade_rules
        self.broker = broker
        self.task_id = None
        self.print_once = True

    def run(self, live=False):

        self.strategy.update(**self.signals, **self.dates, **self.trade_rules, **self.broker)

        params = {
            "strategy": json.dumps(self.strategy)}

        

        response = requests.get(
            url=self.host + self.url,
            headers={"Authorization": "Token " + self.auth_token},
            params=params,
        ).json()
        self.task_id = response
        resp = self.get_state(self.state_url)
        while not resp["state"] == 'COMPLETE':
            resp = self.get_state(self.state_url)
            time.sleep(.5)
            print(resp)
        return response

    def get_state(self, state_url):
        params = {"task_id": self.task_id}
        response = requests.get(
            url=self.host + state_url,
            headers={"Authorization": "Token " + self.auth_token},
            params=params,
        ).json()
        response = json.loads(response)
        return response