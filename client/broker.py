class broker():
    def __init__(self, exchange_id, product_id, starting_cash, taker_fee, maker_fee):
        self.exchange_id = exchange_id
        self.product_id = product_id
        self.starting_cash = starting_cash
        self.taker_fee = taker_fee
        self.maker_fee = maker_fee