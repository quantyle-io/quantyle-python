class strategy():
    def __init__(self, signals, buy_trigger, sell_trigger, strategy_name="my_strategy"):
        self.strategy_name = strategy_name
        self.signals = signals
        self.buy_trigger = buy_trigger
        self.sell_trigger = sell_trigger