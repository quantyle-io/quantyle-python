import requests
import json
import sys
from functools import reduce  # forward compatibility for Python 3
import operator
import matplotlib.pyplot as plt

def getFromDict(dataDict, mapList):
    # access data in a nested dictionary via a list of keys
    return reduce(operator.getitem, mapList, dataDict)

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
        
        self.strategy = strategy
        self.print_once = True

    def start(self):
        params = {
            "strategy": json.dumps({
                "signals": self.strategy.signals,
                "buy_trigger": self.strategy.buy_trigger,
                "sell_trigger": self.strategy.sell_trigger,
            })}

        response = requests.get(
            url='http://localhost:8001/api/Baseline-Backtest/', ## UPDATE BEFORE DEPLOYMENT
            headers={"Authorization": "Token " + self.auth_token},
            params=params,
        ).json()
        self.task_id = response['task_id']

    def get_progress(self, verbose=False):
        # NOTES ON PROGRESS FUNCTION for baseline_backtest_task:
        # state: STARTING_BASELINE_BACKTEST
        #   meta=None
        # state: BASELINE_BACKTEST_PROGRESS
        #   finished backtest, moving onto the next one,
        #   meta={'asset': asset, "broker_name": broker_name, "market_cond": market_cond}
        # state: FINISHED_BASELINE_BACKTEST
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
            if response["state"] == "STARTING_BASELINE_BACKTEST":
                print("-------- Starting Baseline Backtest --------")
            elif response["state"] == "BASELINE_BACKTEST_PROGRESS" and self.print_once:
                backtest = "asset: {a},  broker: {b}, market: {m}".format(a=response["details"]["asset"], b=response["details"]["broker_name"], m=response["details"]["market_cond"])
                print('\n' + backtest)
                self.print_once = False
            elif response["state"] == "PROGRESS":
                self.print_once = True
                sys.stdout.write(str(response["details"]) + '             \r')
            elif response["state"] == "FINISHED_BASELINE_BACKTEST":
                print(" -------- Finished Baseline Backtest -------- ")
                self.response = response

        return response
    
    def plot_baseline_backtest(self, metric, color='C0', setup_charts=True):
        # plots baseline backtest results
        # metrics is a list of keys cooresponding to location in performance_metrics dictionary

        # setup some reference variables before looping through
        markers = ['o', '+', 's', '*', 'v', '^', 'h', 'x', 'd']  # kinda janky, but I doubt that we'll ever have 9+ assets in the baseline backtest, so whatever

        if setup_charts:
            # creates the figures & axis, adds baseline_backtest common labels, and reference lines
            print(metric)
            print(" ".join(metric))

            fig1, ax1 = plt.subplots()
            ax1.set_title("No Fees Broker")
            ax1.set_xlabel("bull market "+" ".join(metric))
            ax1.set_ylabel("bear market "+" ".join(metric))

            fig2, ax2 = plt.subplots()
            ax2.set_title("Max Fees Broker")
            ax2.set_xlabel("bull market "+" ".join(metric))
            ax2.set_ylabel("bear market "+" ".join(metric))

            axs = {"noFees": ax1, "maxFees": ax2}

            # add asset marker labels to legend
            marker_counter = 0
            for asset in self.response["details"]["baseline_backtests_info"]["assets"]:
                marker = markers[marker_counter]
                marker_counter += 1
                ax1.scatter([], [], marker=marker, color='black', label=asset)
                ax2.scatter([], [], marker=marker, color='black', label=asset)

        marker_counter = 0
        for asset in self.response["details"]["baseline_backtests_info"]["assets"]:
            print("ASSET: ", asset)
            marker = markers[marker_counter]
            marker_counter += 1
            for broker in self.response["details"]["baseline_backtests_info"]["brokers"]:
                print("broker: ", broker)
                ax = axs[broker]
                bear_result = [x["performance_metrics"] for x in self.response["details"]["results"] if (x["asset"] == asset and x["broker_name"] == broker and x["market_cond"] == "bear")][0]
                bull_result = [x["performance_metrics"] for x in self.response["details"]["results"] if (x["asset"] == asset and x["broker_name"] == broker and x["market_cond"] == "bull")][0]
                bull_value = getFromDict(bull_result, metric)
                bear_value = getFromDict(bear_result, metric)
                print("bull ", " ".join(metric), ": ", bull_value, ", bear ", " ".join(metric), ": ", bear_value)
                ax.scatter(bull_value, bear_value, color=color, marker=marker, label=None)

        ax1.scatter([], [], color=color, label=self.strategy.strategy_name)
        ax2.scatter([], [], color=color, label=self.strategy.strategy_name)
        ax1.legend(loc='best')
        ax2.legend(loc='best')

