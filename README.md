<img src=".logo-v3.png" alt="drawing" width="780"/>

# Quantyle.io

Quantyle.io is a securities trading tool for both traditional and cryptocurrency markets. 
Our software provides a robust backtesting system that allows for complex strateties to be
run on a variety of assets. We offer several analytics and 
optimization features that greatly improve success rates, as well as live trading signals 
from your own tested strategies that can be implimented on any platform you choose to use.


## Installation

1. Clone quantyle-python repository from `https://github.com/quantyle-io/quantyle-python`
2. Create your virtual environment `python3 -m venv virtualenv`
3. Activate your virtual environment `source virtualenv/bin/activate`
4. Install system requirements from requirements.txt file `pip install -r requirements.txt`
5. Get API key from `https://quantyle.io/settings` in the API tab
6. Create a file called `auth_keys.json` in the main directory and add API key to that file

## Using the API

1. Build your strategy in backtest_api.py
2. Pass `live=True` for live trading signals
3. Pass `combo=True` for backtest optimization
4. Pass `save=True` to save a strategy
5. Pass `retrieve=True` to view saved strategy names
6. Pass `retrieve=strategy_name` to view strategy parameters by name

## Disclaimer
Quantyle is not responsible for any profits or losses made using this software. 