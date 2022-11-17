class broker():
    def __init__(self, exchange_id="GDAX", product_id="BTC-USD", starting_cash=10000, taker_fee=0.004, maker_fee=0.006, trade_size=1):
        self.exchange_id = exchange_id
        self.product_id = product_id
        self.starting_cash = starting_cash
        self.taker_fee = taker_fee
        self.maker_fee = maker_fee
        self.trade_size = trade_size