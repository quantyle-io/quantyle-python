from datetime import datetime as dt
import client as QuantyleClient
import time

# Example of running a backtest with the quantyle-client api
# 1. define a strategy
# 2. define the backtest (broker, date ranges)
# 3. run the backtest
# 4. wait for the backtest to finish
# 5. analyze the results



##### 1. define a strategy 
# in this example a simple MACD strategy

strategy_signals = [
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
buy_trigger = 'macd1 < macd2'
sell_trigger = 'macd1 > macd2'

my_strategy = QuantyleClient.strategy(strategy_signals, buy_trigger, sell_trigger, strategy_name="toshi_smells")

##### 2. define the backtest (broker, date ranges)
# declare the broker conditions for the backtesting
my_broker = QuantyleClient.broker(exchange_id="GDAX", product_id="BTC-USD", starting_cash=500000, taker_fee=0.0001, maker_fee=0.0001)

# declare backtest date range in isoformat
start_date = str(dt(year=2022, month=9, day=1, hour=8, minute=1).isoformat())
end_date = str(dt(year=2022, month=9, day=10, hour=8, minute=1).isoformat())

# QuantyleClient.backtestClient organizes all the inputs from above into a class setup to make the API call
my_backtest = QuantyleClient.backtestClient(broker=my_broker, start_date=start_date, end_date=end_date, strategy=my_strategy)


##### 3. run the backtest
# makes the API call
my_backtest.start()

##### 4. wait for the backtest to finish
# this is a distinct step because it a user may want to make multiple make multiple API calls concurrently
# in which case the user needs to have logic in place to handle each call, waiting for each distinct response
# This is the easiest handling, making one api call, and waiting for it to complete
response = my_backtest.get_progress()
while not response["state"] == "COMPLETE":
    time.sleep(1)
    response = my_backtest.get_progress(verbose=True) # use verbose toggle to print out progress information to terminal

##### 5. analyze the results
# completed backtest, response now has the backtest performance metrics 
print(response)
# results = response["details"]["results"]
# print(results)