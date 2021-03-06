import time
from pprint import pp

from prettytable import PrettyTable


class Serializer:
    # this class serves as printer of data from exchanges
    # pretty print for output data
    # columns and example for the lines
    # timestamp,    exchange,   market,     bid_price,  bid_size,   ask_price,  ask_size
    # (seconds since Epoch)
    # 1589301725,   Binance,    btcusdt,    8903.64,    0.999,      8904.27,    0.18
    # 1589301725,   FTX,        BTC - PERP, 8912.0,     1.7676,     8913.0,     4.1907

    def __init__(self, delay=1, raw_data=False):
        self.columns = ["timestamp", "exchange", "market", "bid_price", "bid_size", "ask_price", "ask_size",
                        "mid_price(1hr ago)"]
        self.delay = delay
        self.output = PrettyTable(self.columns, border=False)

        # for debug purposes Serializer can print raw data passed into it in console
        self.raw_data = raw_data

    def print_line(self, exchange, data):

        if self.raw_data:
            pp(data)
            time.sleep(self.delay)
        else:
            if isinstance(data, dict):
                line = self._get_line(exchange, data)
                if line:
                    # no need to keep table in memory - clear it each time before printing
                    self.output.clear_rows()
                    self.output.add_row(line)
                    print(self.output)

                    # print header only once
                    if self.output.header:
                        self.output.header = False
                    time.sleep(self.delay)

    def _get_line(self, exchange, data):
        values = []
        if exchange.skip_line(data):
            return None

        bids = exchange.get_bids(data)
        asks = exchange.get_asks(data)

        # take top bid/ask - i.e. Highest Bid and Lowest Ask
        # skip printing if both empty
        if not bids and not asks:
            return None

        bids = [0.0, 0.0] if not bids else sorted(bids, key=lambda x: float(x[0]))[0]
        asks = [0.0, 0.0] if not asks else sorted(asks, key=lambda x: -float(x[0]))[0]

        # update mid price one hour ago
        timestamp = exchange.get_timestamp(data)
        mid_price = round((float(bids[0]) + float(asks[0])) / 2, 2)
        exchange.mid_price[int(timestamp)] = mid_price

        for column in self.columns:
            if column == "timestamp":
                value = str(timestamp)
            elif column == "exchange":
                value = exchange.name
            elif column == "market":
                value = exchange.get_market(data)
            elif column == "bid_price":
                value = bids[0]
            elif column == "ask_price":
                value = asks[0]
            elif column == "bid_size":
                value = bids[1]
            elif column == "ask_size":
                value = asks[1]
            elif column == self.columns[-1]:
                hour_ago = timestamp - 3600
                value = exchange.get_mid_price(hour_ago)
                if not value:
                    value = "N/A"

                # remove older data
                exchange.free_mid_price(hour_ago)
            else:
                value = ""

            # to make table look prettier - set fixed width
            if not isinstance(value, str):
                value = str(value)
            while len(value) <= max(len(column), 9):
                value += " "
            values.append(value)
        return values
