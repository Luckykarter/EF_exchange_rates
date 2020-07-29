import time

import maya  # for parsing datetime in Trades
import requests


class Exchange:
    # this class describes necessary attributes and methods required for each exchange
    # and contains logic that is common for every exchange

    def __init__(self, _id: int, name: str, url: str, subscribe: dict, unsubscribe: dict):
        self.id = _id
        self.name = name
        self.url = url
        self.subscribe = subscribe
        self.unsubscribe = unsubscribe
        self.mid_price = dict()
        self.api_interval = 0  # resolution of API data in seconds

        # when initialised - get from API historical orderbook for one hour ago
        end_time = time.time()
        start_time = end_time - 3600
        self.update_mid_price(start_time, end_time)

    def validate_response(self, response):
        pass

    def get_timestamp(self, data) -> int:
        pass

    def get_bids(self, data):
        pass

    def get_asks(self, data):
        pass

    def get_market(self, data):
        pass

    def skip_line(self, data):
        return False

    def update_mid_price(self, start_time, end_time):
        pass

    def _calc_mid_price(self, high, low, timestamp):
        mid_price = round((high + low) / 2, 2)
        self.mid_price[timestamp] = mid_price

    def get_mid_price(self, timestamp):
        if timestamp in self.mid_price:
            return self.mid_price[timestamp]

        # There is minimum resolution of API for historical data
        # Adjust search to closest available time
        for inc in range(1, self.api_interval + 1):
            for direction in (-1, 1):
                new_time = timestamp + inc * direction
                if new_time in self.mid_price:
                    return self.mid_price[new_time]
        return 0

    def free_mid_price(self, timestamp):
        # remove historical data that is earlier than we need
        to_remove = timestamp - 1
        if to_remove in self.mid_price:
            self.mid_price.pop(to_remove)


class Binance(Exchange):
    def __init__(self, _id: int):
        _id = abs(_id)
        name = "Binance"
        url = "wss://fstream.binance.com/ws/btcusdt"
        subscribe = {"method": "SUBSCRIBE",
                     "params": ["btcusdt@depth"],
                     "id": _id
                     }
        unsubscribe = {"method": "UNSUBSCRIBE",
                       "params": ["btcusdt@depth"],
                       "id": _id
                       }
        Exchange.__init__(self, _id, name, url, subscribe, unsubscribe)
        self.api_interval = 60

    def validate_response(self, response: dict):
        if response.get("id") != self.id:
            raise AssertionError("Bad Response.\nExpected id: {}, Received: {}".format(self.id, response.get("id")))

    def get_timestamp(self, data) -> int:
        val = int(data.get("E"))
        return val // 1000

    def get_bids(self, data):
        return data.get("b")

    def get_asks(self, data):
        return data.get("a")

    def get_market(self, data):
        return data.get("s")

    def update_mid_price(self, start_time, end_time):
        # Binance has the following restriction on historical data:
        # If both startTime and endTime are sent, time between startTime and endTime must be less than 1 hour.
        # Thus, give start/end a bit less
        while end_time - start_time >= 3600:
            end_time -= 1

        url = "https://fapi.binance.com"
        url += "/fapi/v1/klines"
        url += "?symbol=btcusdt"
        url += "&interval=1m"
        url += "&startTime={}".format(start_time)
        url += "&endTime={}".format(end_time)

        data = requests.get(url).json()
        for deal in data:
            timestamp = int(deal[0] // 1000)
            high = float(deal[2])
            low = float(deal[3])
            self._calc_mid_price(high, low, timestamp)


class FTX(Exchange):
    def __init__(self, _id: int):
        name = "FTX"
        url = "wss://ftx.com/ws/"
        self.market = "BTC-PERP"
        subscribe = {"channel": "orderbook",
                     "market": self.market,
                     "op": "subscribe"}

        unsubscribe = {"channel": "orderbook",
                       "market": self.market,
                       "op": "unsubscribe"}

        Exchange.__init__(self, _id, name, url, subscribe, unsubscribe)
        self.api_interval = 15

    def get_timestamp(self, data) -> int:
        return int(data.get("data").get("time", 0))

    def _get_from_deal_data(self, data, typ):
        deal_data = data.get("data")
        if isinstance(deal_data, dict):
            return deal_data.get(typ)
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

    def update_mid_price(self, start_time, end_time):
        url = "https://ftx.com/api"
        url += "/markets/{market_name}".format(market_name=self.market)
        url += "/candles?resolution=15"
        url += "&start_time={start_time}".format(start_time=start_time)
        url += "&end_time={end_time}".format(end_time=end_time)

        data = requests.get(url).json()
        data = data.get("result")

        for deal in data:
            timestamp = int(deal.get("time") // 1000)
            self._calc_mid_price(deal.get("high"), deal.get("low"), timestamp)


class FTXTrades(FTX):
    def __init__(self, _id):
        FTX.__init__(self, _id)
        self.name += "_trades"
        self.subscribe["channel"] = "trades"
        self.unsubscribe["channel"] = "trades"

    def _get_from_deal_data(self, data, typ):
        deal_data = data.get("data")
        if not deal_data:
            return None
        return [(deal["price"], deal["size"]) for deal in deal_data if deal["side"] == typ]

    def get_timestamp(self, data) -> int:
        deal_data = data.get("data")
        if isinstance(deal_data[0], dict):
            return maya.parse(deal_data[0].get("time")).epoch
        return 0

    def get_bids(self, data):
        return self._get_from_deal_data(data, "sell")

    def get_asks(self, data):
        return self._get_from_deal_data(data, "buy")
