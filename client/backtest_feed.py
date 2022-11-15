
import time
import json
from decimal import *
from threading import Thread
from websocket import create_connection, WebSocketConnectionClosedException
# from quantyle_lib.util import _print


class BacktestFeed():
    """
    Websocket Client
    """

    def __init__(
            self,
            url="ws://localhost:8001/ws/backtest/",
            exchange_id='GDAX',
            product_id='ETH-USD',
            message_type="subscribe",
            message_queue={},
            # error_queue=mp.Queue,
            # Make channels a required keyword-only argument; see pep3102
            *,
            # channels=['ticker', 'level2', 'matches', 'user']):
            # channels=['ticker', 'level2']):
            channels=['full']):
        auth_file = open('auth_keys.json')
        auth_data = json.load(auth_file)
        auth_key = auth_data['Auth_token']

        self.url = f"{url}{exchange_id}-{product_id}-backtest?token={auth_key}"
        self.exchange_id = exchange_id
        self.product_id = product_id
        self.channels = channels
        self.type = message_type
        self.stop = True
        self.error = None
        self.ws = None
        self.thread = None
        # the message queue for on_message handler
        self.message_queue = message_queue
        # self.error_queue = error_queue

    def start(self):
        def _go():
            self._connect()
            self._listen()
            self._disconnect()
        self.stop = False
        self.thread = Thread(target=_go)
        self.keepalive = Thread(target=self._keepalive)
        self.thread.start()

    def _connect(self):

        self.ws = create_connection(self.url)

    def _keepalive(self, interval=10):
        while self.ws.connected:
            self.ws.ping("keepalive")
            time.sleep(interval)

    def _listen(self):
        self.keepalive.start()
        while not self.stop:
            try:
                data = self.ws.recv()
                msg = json.loads(data)
            except Exception as e:
                self.on_error(e)
                pass
            else:
                self.on_message(msg)

    def _disconnect(self):
        try:
            if self.ws:
                self.ws.close()
        except WebSocketConnectionClosedException as e:
            pass
        finally:
            self.keepalive.join()

        # _print("Unsubscribed from %s" % self.url, status='WARNING')

    def close(self):
        self.stop = True
        self._disconnect()
        self.thread.join()

    def on_message(self, msg):
        self.message_queue.put(msg)
        # print(msg)

    def on_error(self, e, data=None):
        self.error = e
        self.stop = True
        # self.error_queue.put(['CoinbaseProFeed', 'GDAX', self.product_id, e])
        # _print('GDAX [{}]: {}'.format(self.product_id, e), status='ERROR')