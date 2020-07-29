import argparse

parser = argparse.ArgumentParser(
    description='This app subscribes to public WebSockets of exchanges Binance and FTX\nin order to '
                'print orders bids and asks price/size every second')

parser.add_argument('--raw', action="store_true", help='print raw data received from exchanges')
parser.add_argument('--delay', type=float, default=1.0,
                    help='specify custom delay for output in seconds (default: 1.0 second)')

# TODO: add this configuration (to be included in Exchange)
# parser.add_argument('--mid-price-ago', type=float, default=1.0,
#                     help='specify time for mid-price historical data in hours (default: 1.0 hour)')

parser.add_argument('exchanges', nargs='*', default=[],
                    help='specify exchanges to get data from (default: Binance, FTX, FTX_trades)')
