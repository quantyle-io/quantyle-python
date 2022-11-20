from datetime import datetime as dt
import client as QuantyleClient
import time
import matplotlib.pyplot as plt

# Example of running a baseline backtest with the quantyle-client api
# baseline backtest is a sequence of backtests that the quantyle team has picked out 
# to help users evaluate their strategies in a standardized way that minimizes market type bias

# 1. define a strategy
# 3. run the baseline backtest protocol
# 4. wait for the backtests to finish
# 5. analyze the results

'''
1. Define a strategy
'''
# In this example a simple MACD strategy
strategy_signals = [
        {'id': 'EMA', 
        'name': 'slow_ema', 
        'color': '#a7595f', 
        'p': {'inputs': ['close'], 'period': 26}, 
        },
        {'id': 'EMA',
        'name': 'fast_ema', 
        'color': '#44ea11', 
        'p': {'inputs': ['close'], 'period': 9}, 
        }
    ]

buy_trigger = 'fast_ema > slow_ema'
sell_trigger = 'fast_ema < slow_ema'

# Set strategy class
my_strategy = QuantyleClient.strategy(strategy_signals, buy_trigger, sell_trigger, strategy_name="my_macd")


# Pass Strategy, Broker, and Dates to QuantyleClient.backtestClient
my_baseline_backtest = QuantyleClient.BaselineBacktestClient(strategy=my_strategy)


'''
2. run the baseline backtest
'''
# makes the API call to run the backtest process
my_baseline_backtest.start()


'''
3. wait for the baselines backtests to finish
'''
# This is a distinct step because a user may want to make multiple API calls concurrently
# In this case the user needs to have logic in place to handle each call, waiting for each distinct response
# This is the easiest handling, making one api call, and waiting for it to complete
response = my_baseline_backtest.get_progress()
while not response["state"] == "FINISHED_BASELINE_BACKTEST":
    time.sleep(1)
    response = my_baseline_backtest.get_progress(verbose=True) # use verbose toggle to print out progress information to terminal


'''
4. analyze the results
'''
# Completed backtest, response now has the backtest performance metrics 

# print(response)
# results = response["details"]["performance"]
# print(results)

my_baseline_backtest.plot_baseline_backtest(["return_on_investment"], color='C0')
plt.show()

