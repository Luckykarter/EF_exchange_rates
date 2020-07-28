import json
import threading

from resources.connector import ConnectToWS
from resources.exchanges import Exchange


class Subscribe(threading.Thread):
    def __init__(self, exchange: Exchange, serializer):
        threading.Thread.__init__(self)
        self.threadID = "{}-{}".format(exchange.name, exchange.id)
        self.exchange = exchange
        self.serializer = serializer
        self.running = False  # TODO: make concurrent stopper

    def run(self):
        self.running = True

        print("Subscribing to {}...".format(self.exchange.name))
        try:
            with ConnectToWS(self.exchange.url) as ws:
                ws.send(json.dumps(self.exchange.subscribe))
                result = json.loads(ws.recv())
                self.exchange.validate_response(result)

                while self.running:
                    data = ws.recv()
                    self.serializer.print_line(self.exchange, json.loads(data))

                ws.send(json.dumps(self.exchange.unsubscribe))

        except Exception as e:
            print(e)
            print("Please try again later")
            exit(1)
