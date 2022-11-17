<img src=".logo-v3.png" alt="drawing" width="780"/>

# Quantyle.io

Quantyle.io is a algorithmic trading strategy development, backtesting, and live execution tool for traditional securities and cryptocurrency markets. Our software provides a robust backtesting system that allows for complex strategies to be run on a variety of assets. We offer several analytics and optimization features that greatly improve success rates, as well as live trading signals from your own tested strategies that can be interfaced on any platform you choose to use.

## Installation

1. Clone quantyle-python repository from `https://github.com/quantyle-io/quantyle-python`
2. Create your virtual environment `python3 -m venv virtualenv`
3. Activate your virtual environment `source virtualenv/bin/activate`
4. Install system requirements from requirements.txt file `pip install -r requirements.txt`
5. Get API key from `https://quantyle.io/settings` in the API tab
6. make a file `auth_keys.json` in the same directory as your scripts containing:

{
    "Auth_token": "your-auth-token"
}

## API features

1. Build and backtest custom strategies
2. Live strategy execution: Pass `live=True`
3. Optimization of Strategy parameters: Pass `combo=True`
4. Save a backtest to the backtest database: Pass `save=True`
5. Retrieve list of your saved strategies from the backtest database: Pass `retrieve=True` 
6. Retrieve list of parameters for a specific strategy from the backtest database: Pass `retrieve=strategy_name` 

for a rich set of examples detailing how to use each feature with python scripts see the examples folder

## Disclaimer
Quantyle is not responsible for any profits or losses made using this software. 