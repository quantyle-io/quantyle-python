import requests
import json
import time
from .backtest_feed import BacktestFeed


class QuantyleClient():
    def __init__(self, strategy):
        auth_file = open('auth_keys.json')
        auth_data = json.load(auth_file)
        auth_key = auth_data['Auth_token']

        self.host = 'http://localhost:8001/api/'
        self.state_url = 'get-progress/'
        self.auth_token = auth_key
        self.session = requests.Session()
        self.strategy = strategy
        self.task_id = None
        self.print_once = True

    def run(self, live=False):
        if live:
            path = 'run-execution/'
        else:
            path = 'backtest2/'

        params = {
            "strategy": json.dumps(self.strategy)}
        response = requests.get(
            url=self.host + path,
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
