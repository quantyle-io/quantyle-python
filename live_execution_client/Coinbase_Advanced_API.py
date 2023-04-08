import requests
from requests.auth import AuthBase
import time
import math
import base64
import hmac
import hashlib
import json
import uuid
import datetime


class CoinbaseAdvancedAuth(AuthBase):
    """
    python requests authenitification class for Coinbase api v3
    # https://docs.cloud.coinbase.com/advanced-trade-api/docs/rest-api-auth
    """
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

    def get_auth_headers(self, timestamp, message):
        # encodes message, aka signature, and puts it in the headers dict
        signature = hmac.new(self.secret_key.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).digest().hex()
        return {
            'accept': 'application/json',
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
        }

    def __call__(self, request):
        # formats the request per the Authentification requirements of Coinbase API v3:
        # request.method = GET or POST (Capitalized)
        # request.url = "https://api.coinbase.com/api/v3/brokerage/accounts" (example)
        # request.message = timestamp + request.method + path_url + body (and then encoded with api secret key as seed)
        # path_url = "/api/v3/brokerage/accounts" (example)

        # convenient to extract path_url from request.url by removing "https://api.coinbase.com" and any querying values, i.e. anything after "?"
        path_url = request.url.replace("https://api.coinbase.com", "").split('?')[0]
        timestamp = str(int(time.time()))  # Coinbase only takes timestamp as integer (aka +/- 30sec)
        message = timestamp + request.method + path_url + str(request.body or '')
        request.headers.update(self.get_auth_headers(timestamp, message))
        return request


class CoinbaseAdvanced():
    """
    HTTP/REST Client for Coinbase api v3

    License Note: 
    Quantyle is not responsible for USER Broker communications or interactions. 
    Quantyle is providing a Coinbase Rest API for user convenience to facilitate their broker communications, but does not gurantee accuracy.
    By using this library the USER accepts all responsibility for accurate broker communications, including any errors that may be introduced by this interface library.
    """

    def __init__(self, api_key, api_secret):
        self.api_url = "https://api.coinbase.com"
        self.timeout = 10
        self.session = requests.Session()
        self.auth = CoinbaseAdvancedAuth(api_key, api_secret)

    def get(self, path_url, params=None, debug=False):
        # This is a parent method for all GET calls
        # query parameters "params" are passed as a dictionary
        if debug:
            print("params: ", params)
        response = self.session.request(
            method='GET',
            url=self.api_url + path_url,
            timeout=self.timeout,
            auth=self.auth,
            params=params
        ).json()
        return response

    def post(self, path_url, data, debug=False):
        # POST request, with body (aka data) parameters, 
        # data is passed as a dictionary
        # This is a parent method for all POST calls
        if debug:
            print(data)
        data = json.dumps(data)
        response = self.session.request(
            method='POST',
            url=self.api_url + path_url,
            timeout=self.timeout,
            auth=self.auth,
            data=data
        ).json()
        return response

    def format_date(self, date, debug=False):
        # Some outstanding confusion about v3 api datetime format:
        # https://forums.coinbasecloud.dev/t/create-order-request-body/2260/10
        # API actually expects it in the ISO_OFFSET_DATE_TIME format. example: 2022-12-27T04:16:47.571-05:00
        date = date.astimezone(datetime.timezone.utc).isoformat()
        if debug: 
            print("formatted date: ", date)
        return date

    # -----------------------------------------------------------------------------------
    # --------------- ACCOUNTS ----------------------------------------------------------
    # -----------------------------------------------------------------------------------

    def list_accounts(self, debug=False):
        # lists your coinbase accounts, wallets etc
        path_url = "/api/v3/brokerage/accounts"
        return self.get(path_url, debug=debug)

    def get_account(self, account_uuid, debug=False):
        # https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_getaccount
        # Get a list of information about an account, given an account UUID.
        path_url = "/api/v3/brokerage/accounts/" + account_uuid
        return self.get(path_url, debug=debug)

    # -----------------------------------------------------------------------------------
    # --------------- ORDERS ------------------------------------------------------------
    # -----------------------------------------------------------------------------------

    # --------------- create_orders ---------------------

    def create_order(self, product_id, side, order_configuration, client_order_id=str(uuid.uuid1()), debug=False):
        # https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_postorder
        # product_id = e.g. 'BTC-USD'
        # side = possible values: UNKNOWN_ORDER_SIDE, BUY, SELL
        # client_order_id = Client set unique uuid for this order
        # order_configuration = specification of order type.

        # parent function for all "create_order" requests
        # - market_market_ioc
        # - limit_limit_gtc
        # - limit_limit_gtd
        # - stop_limit_stop_limit_gtc
        # - stop_limit_stop_limit_gtd

        path_url = "/api/v3/brokerage/orders"
        data = {
            "client_order_id": client_order_id,
            "product_id": product_id,
            "side": side,
            "order_configuration": order_configuration
        }
        return self.post(path_url, data, debug=debug)

    def create_market_market_ioc(self, product_id, side, quote_size="", base_size="", client_order_id=str(uuid.uuid1()), debug=False):
        # Create an order with a specified product_id (asset-pair), side (buy/sell), etc.
        # quote_size = Amount of quote currency to spend on order. Required for BUY orders.
        # base_size = Amount of base currency to spend on order. Required for SELL orders.

        order_configuration = {"market_market_ioc": {}}
        if side == "BUY":
            order_configuration["market_market_ioc"]["quote_size"] = str(quote_size)
        elif side == "SELL":
            order_configuration["market_market_ioc"]["base_size"] = str(base_size)
        else:
            # raise error
            print("bad side")
            return None
        return self.create_order(product_id, side, order_configuration, client_order_id, debug=debug)

    def create_limit_limit_gtc(self, product_id, side, base_size, limit_price, post_only=True, client_order_id=str(uuid.uuid1()), debug=False):
        # base_size: Amount of base currency to spend on order
        # limit_price: Ceiling price for which the order should get filled
        # The Post-Only Limit order option ensures that the limit order will be added to the order book and not match a pre-existing order. 
        # If your order would cause a match with a pre-existing order, your post-only limit order will be canceled

        order_configuration = {"limit_limit_gtc": {}}
        order_configuration["limit_limit_gtc"]["base_size"] = str(base_size)
        order_configuration["limit_limit_gtc"]["limit_price"] = str(limit_price)
        order_configuration["limit_limit_gtc"]["post_only"] = post_only
        return self.create_order(product_id, side, order_configuration, client_order_id, debug=debug)

    def create_limit_limit_gtd(self, product_id, side, base_size, limit_price, end_time, post_only=True, client_order_id=str(uuid.uuid1()), debug=False):
        # base_size: Amount of base currency to spend on order
        # limit_price: Ceiling price for which the order should get filled
        # end_time: Time at which the order should be cancelled if it's not filled. (pass as datetime object)
        # The Post-Only Limit order option ensures that the limit order will be added to the order book and not match a pre-existing order. 
        # If your order would cause a match with a pre-existing order, your post-only limit order will be canceled

        if not isinstance(end_time, datetime.date):
            print("please pass end_date as a datetime object.")
            return None

        order_configuration = {"limit_limit_gtd": {}}
        order_configuration["limit_limit_gtd"]["base_size"] = str(base_size)
        order_configuration["limit_limit_gtd"]["limit_price"] = str(limit_price)
        order_configuration["limit_limit_gtd"]["end_time"] = self.format_date(end_time, debug)
        order_configuration["limit_limit_gtd"]["post_only"] = post_only
        return self.create_order(product_id, side, order_configuration, client_order_id, debug=debug)

    def stop_limit_stop_limit_gtc(self, product_id, side, base_size, limit_price, stop_price, stop_direction, client_order_id=str(uuid.uuid1()), debug=False):
        # base_size: Amount of base currency to spend on order
        # limit_price: Ceiling price for which the order should get filled
        # stop_price: Price at which the order should trigger - 
        # if stop direction is Up, then the order will trigger when the last trade price goes above this, otherwise order will trigger when last trade price goes below this price.
        # stop_direction: UNKNOWN_STOP_DIRECTION, STOP_DIRECTION_STOP_UP, STOP_DIRECTION_STOP_DOWN

        order_configuration = {"stop_limit_stop_limit_gtc": {}}
        order_configuration["stop_limit_stop_limit_gtc"]["base_size"] = str(base_size)
        order_configuration["stop_limit_stop_limit_gtc"]["limit_price"] = str(limit_price)
        order_configuration["stop_limit_stop_limit_gtc"]["stop_price"] = str(stop_price)
        order_configuration["stop_limit_stop_limit_gtc"]["stop_direction"] = stop_direction
        return self.create_order(product_id, side, order_configuration, client_order_id, debug=debug)

    def stop_limit_stop_limit_gtd(self, product_id, side, base_size, limit_price, stop_price, stop_direction, end_time, client_order_id=str(uuid.uuid1()), debug=False):
        # base_size: Amount of base currency to spend on order
        # limit_price: Ceiling price for which the order should get filled
        # stop_price: Price at which the order should trigger - 
        # if stop direction is Up, then the order will trigger when the last trade price goes above this, otherwise order will trigger when last trade price goes below this price.
        # stop_direction: UNKNOWN_STOP_DIRECTION, STOP_DIRECTION_STOP_UP, STOP_DIRECTION_STOP_DOWN

        if not isinstance(end_time, datetime.date):
            print("please pass end_date as a datetime object.")
            return None

        order_configuration = {"stop_limit_stop_limit_gtd": {}}
        order_configuration["stop_limit_stop_limit_gtd"]["base_size"] = str(base_size)
        order_configuration["stop_limit_stop_limit_gtd"]["limit_price"] = str(limit_price)
        order_configuration["stop_limit_stop_limit_gtd"]["stop_price"] = str(stop_price)
        order_configuration["stop_limit_stop_limit_gtd"]["stop_direction"] = stop_direction
        order_configuration["stop_limit_stop_limit_gtd"]["end_time"] = self.format_date(end_time, debug)
        return self.create_order(product_id, side, order_configuration, client_order_id, debug=debug)

    def get_order(self, order_id, debug=False):
        # https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_gethistoricalorder
        # get a single order by order ID
        path_url = "/api/v3/brokerage/orders/historical/" + order_id
        return self.get(path_url, debug=debug)

    def cancel_orders(self, order_ids, debug=False):
        # https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_cancelorders
        # Initiate cancel requests for one or more orders.
        # order_ids passed as a list of strings
        path_url = "/api/v3/brokerage/orders/batch_cancel"
        data = {
            "order_ids": order_ids,
        }
        return self.post(path_url, data, debug=debug)

    def list_orders(self, product_id=None, order_status=None, limit=None, start_date=None, end_date=None, user_native_currency=None, order_type=None, order_side=None, cursor=None, product_type=None, order_placement_source=None, debug=False):
        # https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_gethistoricalorders
        # Get a list of orders filtered by optional query parameters (product_id, order_status, etc)
        path_url = "/api/v3/brokerage/orders/historical/batch"

        possible_queries = ["product_id", "order_status", "limit", "start_date", "end_date", "user_native_currency", "order_type", "order_side", "cursor", "product_type", "order_placement_source"]
        params = {}
        for query in possible_queries:
            if eval(query) is not None:
                if query == "start_date" or query == "end_date":
                    params[query] = self.format_date(eval(query))
                else:
                    params[query] = eval(query)

        return self.get(path_url, params=params, debug=debug)

    def list_fills(self, order_id=None, product_id=None, start_sequence_timestamp=None, end_sequence_timestamp=None, limit=None, cursor=None, debug=False):
        # https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_getfills
        # Get a list of fills filtered by optional query parameters (product_id, order_id, etc).
        path_url = "/api/v3/brokerage/orders/historical/fills"

        possible_queries = ["order_id", "product_id", "limit", "start_sequence_timestamp", "end_sequence_timestamp", "limit", "cursor"]
        params = {}
        for query in possible_queries:
            if eval(query) is not None:
                if query == "start_sequence_timestamp" or query == "end_sequence_timestamp":
                    params[query] = self.format_date(eval(query))
                else:
                    params[query] = eval(query)

        return self.get(path_url, params=params, debug=debug)

    # -----------------------------------------------------------------------------------
    # ------------------------ PRODUCTS -------------------------------------------------
    # -----------------------------------------------------------------------------------

    def list_products(self, limit=None, offset=None, product_type=None, debug=False):
        # https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_getproducts
        # Get a list of the available currency pairs for trading.
        path_url = "/api/v3/brokerage/products"
        possible_queries = ["limit", "offset", "product_type"]

        params = {}
        for query in possible_queries:
            if debug: 
                print(query, eval(query))
            if eval(query) is not None:
                params[query] = eval(query)

        return self.get(path_url, params=params, debug=debug)

    def get_product(self, product_id, debug=False): 
        # https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_getproduct
        # Get information on a single product by product ID.
        path_url = "/api/v3/brokerage/products/" + product_id
        return self.get(path_url)

    def get_product_candles(self, product_id, start, end, granularity="UNKNOWN_GRANULARITY", debug=False):
        # https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_getcandles
        granularity_options = ["ONE_MINUTE", "FIVE_MINUTE", "FIFTEEN_MINUTE", "THIRTY_MINUTE", "ONE_HOUR", "TWO__HOUR", "SIX_HOUR", "ONE_DAY"]
        if granularity not in granularity_options:
            print("granularity must be one of: ")
            print(granularity_options)
            return None

        path_url = "/api/v3/brokerage/products/{product_id}/candles".format(product_id=product_id)
        params = {
            "start": self.format_date(start), 
            "end": self.format_date(end)
        }
        return self.get(path_url, params=params, debug=debug)

    def get_market_trades(self, product_id, limit, debug=False):
        # https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_getmarkettrades
        path_url = "/api/v3/brokerage/products/{product_id}/ticker".format(product_id=product_id)
        params = {
            "limit": limit
        }
        return self.get(path_url, params=params, debug=debug)

    # --------------------------------------------------------------------------------------------------
    # -------------------------------- FEES ------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------

    def get_transactions_summary(self, start_date=None, end_date=None, user_native_currency=None, product_type=None, debug=False):
        # https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_gettransactionsummary
        path_url = "/api/v3/brokerage/transaction_summary"
        possible_queries = ["start_date", "end_date", "user_native_currency", "product_type"]

        params = {}
        for query in possible_queries:
            if debug: 
                print(query, eval(query))
            if eval(query) is not None:
                if query == "start_date" or query == "end_date":
                    params[query] = self.format_date(eval(query))
                else:
                    params[query] = eval(query)
        return self.get(path_url, params=params, debug=debug)

    # --------------------------------------------------------------------------------------------------
    # ------------------------- additional functions ---------------------------------------------------
    # --------------------------------------------------------------------------------------------------

    def get_product_account(self, product, debug=False):
        # gets account for a single product i.e. "BTC"
        accounts = self.list_accounts()
        account = next(account for account in accounts if account["currency"] == product)
        return self.get_account(account["uuid"], debug=debug)

    def calc_max_base_size(self, product_id, debug=False):
        # product_id = "{base_currency_id}-{quote_currency_id}" e.g. "BTC-USD"
        # calculates the max base size available in users account of a product in multiples of product base_increment
        # base_increment is the smallest number of a product that can be traded

        base_currency_id = product_id.split("-")[0]
        account = self.get_product_account(base_currency_id, debug=debug) 
        value = float(account["available_balance"]["value"])  # amount of asset user owns

        product = self.get_product(product_id, debug=debug)
        base_min_size = float(product["base_min_size"])  # the minimum size of a trade for a given asset
        base_increment = float(product["base_increment"])

        max_base_size = base_increment * int(value / base_increment)
        if debug: 
            print("value: ", value)
            print("base_min_size: ", base_min_size)
            print("base_increment: ", base_increment)
            print("max_base_size: ", max_base_size)

        return max_base_size

    def sell_all_market_order(self, product_id, client_order_id=str(uuid.uuid1()), debug=False):
        # sells the max possible amount of a product that a user owns, as a market order
        base_size = self.calc_max_base_size(product_id, debug=debug)
        return self.create_market_market_ioc(product_id, side="SELL", quote_size=None, base_size=base_size, client_order_id=client_order_id, debug=debug)
