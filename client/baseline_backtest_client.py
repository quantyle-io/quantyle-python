import requests
import json
import sys


class BaselineBacktestClient():
    # Client Class for interfacing with the Baseline Backtest API call

    def __init__(self, strategy,  auth_token=None):
        # where strategy is a class with signals and buy/sell triggers
        if auth_token is None:
            auth_file = open('auth_keys.json')
            auth_data = json.load(auth_file)
            auth_key = auth_data['Auth_token']
            self.auth_token = auth_key
        else:
            self.auth_token = auth_token
        
        self.strategy_signals = strategy.signals
        self.buy_trigger = strategy.buy_trigger
        self.sell_trigger = strategy.sell_trigger
        self.print_once = True

    def start(self):
        params = {
            "strategy": json.dumps({
                "signals": self.strategy_signals,
                "buy_trigger": self.buy_trigger,
                "sell_trigger": self.sell_trigger,
            })}

        response = requests.get(
            url='http://localhost:8001/api/Baseline-Backtest/', ## UPDATE BEFORE DEPLOYMENT
            headers={"Authorization": "Token " + self.auth_token},
            params=params,
        ).json()
        self.task_id = response['task_id']

    def get_progress(self, verbose=False):
        # NOTES ON PROGRESS FUNCTION for baseline_backtest_task:
        # state: BASELINE_BACKTEST_PROGRESS
        #   finished backtest, moving onto the next one,
        #   meta={'asset': asset, "broker_name": broker_name, "market_cond": market_cond}
        # state: BASELINE_BACKTEST_FINISHED
        #   finished all backtests
        #   meta={'results': baselines_backtest_results}
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
            if response["state"] == "PARAMETER_SCAN_PROGRESS" and self.print_once:
                backtest_status = "backtest: {b} of {t}".format(b=response["details"]["backtest"], t=response["details"]["total"])
                print('\n' + backtest_status)
                self.print_once = False
            elif response["state"] == "PROGRESS":
                self.print_once = True
                sys.stdout.write(str(response["details"]) + '             \r')
            elif response["state"] == "PARAMETER_SCAN_FINISHED":
                print(" -------- Finished Parameter Scan -------- ")
        
        if verbose:
            # print progress information:
            if response["state"] == "BASELINE_BACKTEST_PROGRESS" and self.print_once:
                backtest = "asset: {a},  broker: {b}, market: {m}".format(a=response["details"]["asset"], b=response["details"]["broker_name"], m=response["details"]["market_cond"])
                print('\n' + backtest)
                self.print_once = False
            elif response["state"] == "PROGRESS":
                self.print_once = True
                sys.stdout.write(str(response["details"]) + '             \r')
            elif response["state"] == "BASELINE_BACKTEST_FINISHED":
                print(" -------- Finished Baseline Backtest -------- ")

        return response
