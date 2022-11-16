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