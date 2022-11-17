import requests
import json
import sys


class ParameterScanClient():
    # Client Class for interfacing with the Parameter Scan API call

    def __init__(self, strategy, parameter_scan, broker, start_date, end_date, auth_token=None):
        # where strategy is a class with signals and buy/sell triggers
        # and parameter_scan is a list of dictionary of {period1:[10,20...100],period1:[10,20...100]}
        if auth_token is None:
            auth_file = open('auth_keys.json')
            auth_data = json.load(auth_file)
            auth_key = auth_data['Auth_token']
            self.auth_token = auth_key
        else:
            self.auth_token = auth_token
        self.exchange_id = broker.exchange_id
        self.product_id = broker.product_id
        self.starting_cash = broker.starting_cash
        self.trade_size = broker.trade_size
        self.taker_fee = broker.taker_fee
        self.maker_fee = broker.maker_fee
        self.strategy_signals = strategy.signals
        self.buy_trigger = strategy.buy_trigger
        self.sell_trigger = strategy.sell_trigger
        self.parameter_scan = parameter_scan
        self.start_date = start_date
        self.end_date = end_date
        self.print_once = True
        

    def start(self):
        params = {
            "scan": json.dumps({
                "exchange_id": self.exchange_id,
                "product_id": self.product_id,
                "starting_cash": self.starting_cash,
                'trade_size': self.trade_size,
                "taker_fee": self.taker_fee,
                "maker_fee": self.maker_fee,
                "signals": self.strategy_signals,
                "buy_trigger": self.buy_trigger,
                "sell_trigger": self.sell_trigger,
                "parameter_scan": self.parameter_scan,
                "start_date": self.start_date,
                "end_date": self.end_date,
            })}

        response = requests.get(
            url='http://localhost:8001/api/Parameter-Scan/',
            headers={"Authorization": "Token " + self.auth_token},
            params=params,
        ).json()
        self.task_id = response['task_id']

    def get_progress(self, verbose=False):
        # NOTES ON PROGRESS FUNCTION for parameter_scan_task:
        # state: PARAMETER_SCAN_PROGRESS 
        #   finished a backtest in the scan, moving onto the next one,
        #   meta={'backtest': (count), 'total': len(scan)}
        # state: PARAMETER_SCAN_FINISHED
        #   finished a backtest in the scan, moving onto the next one
        #   meta={'results': 'add results here'}
        # state: PROGRESS
        #   backtest is actively running
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
            if response["state"] == "PARAMETER_SCAN_PROGRESS" and self.print_once:
                backtest_status = "backtest: {b} of {t}".format(b=response["details"]["backtest"], t=response["details"]["total"])
                print('\n' + backtest_status)
                self.print_once = False
            elif response["state"] == "PROGRESS":
                self.print_once = True
                sys.stdout.write(str(response["details"]) + '             \r')
            elif response["state"] == "PARAMETER_SCAN_FINISHED":
                print(" -------- Finished Parameter Scan -------- ")

        return response
