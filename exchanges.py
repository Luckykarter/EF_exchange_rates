import maya  # for parsing datetime in Trades


class Exchange:
    # this is an abstract class to describe necessary attributes and methods required for each exchange
    # and define output columns

    def __init__(self, id: int, name: str, url: str, subscribe: dict, unsubscribe: dict):
        self.id = id
        self.name = name
        self.url = url
        self.subscribe = subscribe
        self.unsubscribe = unsubscribe
        self.mid_price = dict()

    def validate_response(self, response):
        pass

    def get_timestamp(self, data):
        pass

    def get_bids(self, data):
        pass

    def get_asks(self, data):
        pass

    def get_market(self, data):
        pass

    def skip_line(self, data):
        return False

    def _free_mid_price(self, timestamp):
        # remove historical data that is earlier than we need
        to_remove = timestamp - 1
        if to_remove in self.mid_price:
            self.mid_price.pop(to_remove)


class Binance(Exchange):
    def __init__(self, id: int):
        id = abs(id)
        name = "Binance"
        url = "wss://fstream.binance.com/ws/btcusdt"
        subscribe = {"method": "SUBSCRIBE",
                     "params": ["btcusdt@depth"],
                     "id": id
                     }
        unsubscribe = {"method": "UNSUBSCRIBE",
                       "params": ["btcusdt@depth"],
                       "id": id
                       }
        Exchange.__init__(self, id, name, url, subscribe, unsubscribe)

    def validate_response(self, response: dict):
        if response.get("id") != self.id:
            raise AssertionError("Bad Response.\nExpected id: {}, Received: {}".format(self.id, response.get("id")))

    def get_timestamp(self, data):
        val = int(data.get("E"))
        return str(val // 1000)

    def get_bids(self, data):
        return data.get("b")

    def get_asks(self, data):
        return data.get("a")

    def get_market(self, data):
        return data.get("s")


class FTX(Exchange):
    def __init__(self, id: int):
        name = "FTX"
        url = "wss://ftx.com/ws/"
        subscribe = {"channel": "orderbook",
                     "market": "BTC-PERP",
                     "op": "subscribe"}

        unsubscribe = {"channel": "orderbook",
                       "market": "BTC-PERP",
                       "op": "unsubscribe"}

        Exchange.__init__(self, id, name, url, subscribe, unsubscribe)

    def get_timestamp(self, data):
        return str(int(data.get("data").get("time")))

    def _get_from_deal_data(self, data, type):
        deal_data = data.get("data")
        if isinstance(deal_data, dict):
            return deal_data.get(type)
        return None

    def get_bids(self, data):
        return self._get_from_deal_data(data, "bids")

    def get_asks(self, data):
        return self._get_from_deal_data(data, "asks")

    def get_market(self, data):
        return data.get("market")

    def skip_line(self, data):
        if data.get("type") == "partial":
            return True
        return False


class FTX_trades(FTX):
    def __init__(self, id):
        FTX.__init__(self, id)
        self.name += "_trades"
        self.subscribe["channel"] = "trades"
        self.unsubscribe["channel"] = "trades"

    def _get_from_deal_data(self, data, type):
        deal_data = data.get("data")
        if not deal_data:
            return None
        return [(deal["price"], deal["size"]) for deal in deal_data if deal["side"] == type]

    def get_timestamp(self, data):
        deal_data = data.get("data")
        if not deal_data:
            return None
        return maya.parse(deal_data[0].get("time")).epoch

    def get_bids(self, data):
        return self._get_from_deal_data(data, "sell")

    def get_asks(self, data):
        return self._get_from_deal_data(data, "buy")
