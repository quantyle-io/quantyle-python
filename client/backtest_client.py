import requests
import json
import time
import sys
from .backtest_feed import BacktestFeed

class backtestClient():
    def __init__(self, broker, start_date, end_date, strategy):
        auth_file = open('auth_keys.json')
        auth_data = json.load(auth_file)
        auth_key = auth_data['Auth_token']
        self.auth_token = auth_key
        self.session = requests.Session()
        self.host = 'http://localhost:8001/api/backtest2/' # UPDATE BEFORE DEPLOYMENT
        self.name = strategy.strategy_name
        self.exchange_id = broker.exchange_id
        self.product_id = broker.product_id
        self.starting_cash = broker.starting_cash
        self.taker_fee = broker.taker_fee
        self.maker_fee = broker.maker_fee
        self.start_date = start_date
        self.end_date = end_date
        self.signals = strategy.signals
        self.buy_trigger = strategy.buy_trigger
        self.sell_trigger = strategy.sell_trigger

    def start(self):
        params = {
            "strategy": json.dumps({
                "start_date": self.start_date,
                "end_date": self.end_date,
                "exchange_id": self.exchange_id,
                "product_id": self.product_id,
                "starting_cash": self.starting_cash,
                'trade_size': 1,
                "taker_fee": self.taker_fee,
                "maker_fee": self.maker_fee,
                "signals": self.signals,
                "buy_trigger": self.buy_trigger,
                "sell_trigger": self.sell_trigger,
            })}
        
        print(params)

        response = requests.get(
            url=self.host,
            headers={"Authorization": "Token " + self.auth_token},
            params=params,
        ).json()

        print("hello")
        # print(response)
        # self.task_id = response['task_id']
        self.task_id = response

        # response = self.session.request(
        #     method='get',
        #     url=self.host,
        #     params=params,
        # ).json()
        # print(response)
        # self.task_id = response['task_id']
    
    def get_progress(self, verbose=False):
        # NOTES ON PROGRESS FUNCTION for baseline_backtest_task:
        # state: COMPLETE
        #   backtest finished
        # state: PROGRESS
        #   a backtest is actively running
        #   meta={'current': (index + 1), 'total': total_rows}, referring to the rows of data in the backtest window start_date -> end_date

        # assumes run has already been called
        params = {"task_id": self.task_id}
        response = requests.get(
            url='http://localhost:8001/api/get-progress/',
            headers={"Authorization": "Token " + self.auth_token},
            params=params,
        ).json()
        response = json.loads(response)

        if verbose:
            # print progress information:
            if not response["state"] == "COMPLETE":
                self.print_once = True
                print(response)
                # sys.stdout.write(str(response["details"]) + '             \r')
            elif response["state"] == "COMPLETE":
                print(" -------- Finished Backtest -------- ")

        return response



# {'strategy': '{"start_date": "2022-09-01T08:01:00", "end_date": "2022-09-01T08:01:00", "exchange_id": "GDAX", "product_id": "BTC-USD", "starting_cash": 500000, "trade_size": 1, "taker_fee": 0.0001, "maker_fee": 0.0001, "signals": [{"id": "MACD", "name": "macd1", "color": "#a7595f", "p": {"inputs": ["close"], "fast_period": 9, "slow_period": 26}}, {"id": "MACD", "name": "macd2", "color": "#44ea11", "p": {"inputs": ["close"], "fast_period": 18, "slow_period": 52}}], "buy_trigger": "macd1 < macd2", "sell_trigger": "macd1 > macd2"}'}
# {'strategy': '{"start_date": "2020-09-01T08:01:00", "end_date": "2022-09-10T08:01:00", "exchange_id": "GDAX", "product_id": "BTC-USD", "starting_cash": 500000, "trade_size": 1, "taker_fee": 0.0001, "maker_fee": 0.0001, "signals": [{"id": "MACD", "name": "macd1", "color": "#a7595f", "p": {"inputs": ["close"], "fast_period": 9, "slow_period": 26}}, {"id": "MACD", "name": "macd2", "color": "#44ea11", "p": {"inputs": ["close"], "fast_period": 18, "slow_period": 52}}], "buy_trigger": "macd1 < macd2", "sell_trigger": "macd1 > macd2"}'}