from datetime import datetime as dt
import client as QuantyleClient
import time

# Example of conducting a parameter with the quantyle-client api
# 1. define a strategy
# 2. define the parameter scan
# 3. define market scenario (broker, date ranges)
# 4. run the parameter scan
# 5. wait for the parameter scan to finish
# 6. analyze the results

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

'''
2. Define a parameter scan
'''

parameter_scan = {
    "fast_period": {"signal_name":"fast_ema", "parameter":"period", "values":[10, 20, 30]},
    "slow_period": {"signal_name":"slow_ema", "parameter":"period", "values":[50, 100, 150]},
    }

'''
3. define the market scenario (broker, date ranges)
'''
# Declare the broker conditions for the backtesting
my_broker = QuantyleClient.broker(exchange_id="GDAX", product_id="BTC-USD", starting_cash=10000, taker_fee=0.004, maker_fee=0.006, trade_size=1)

# Declare backtest date range in isoformat
start_date = str(dt(year=2022, month=9, day=1, hour=8, minute=1).isoformat())
end_date = str(dt(year=2022, month=9, day=10, hour=8, minute=1).isoformat())

# Pass Strategy, Broker, and Dates to QuantyleClient.backtestClient
my_parameter_scan = QuantyleClient.ParameterScanClient(my_strategy, parameter_scan, my_broker, start_date, end_date)

'''
4. run the parameter scan
'''
# makes the API call to run the parameter scan process
my_parameter_scan.start()


'''
5. wait for the parameter scan to finish
'''
response = my_parameter_scan.get_progress()
while not response["state"] == "PARAMETER_SCAN_FINISHED":
    time.sleep(1)
    response = my_parameter_scan.get_progress(verbose=True) # use verbose toggle to print out progress information to terminal

'''
6. analyze the results
'''
results = response["details"]["results"]
print(results)