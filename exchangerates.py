import exchanges
from parameters import parser
from serializer import Serializer
from subscribe import Subscribe

args = parser.parse_args()
# Subscribe to exchanges in threads
threads = []

# use one common serializer to print data from the sources
serializer = Serializer(delay=args.delay,
                        raw_data=args.raw,
                        mid_price_ago=args.mid_price_ago)

# fire up only given sources (if given - otherwise - all of them)
exchanges_set = set([e.lower() for e in args.exchanges])

if not exchanges_set or "binance" in exchanges_set:
    threads.append(Subscribe(exchanges.Binance(id=1), serializer))

if not exchanges_set or "ftx" in exchanges_set:
    threads.append(Subscribe(exchanges.FTX(id=1), serializer))

if not exchanges_set or "ftx_trades" in exchanges_set:
    threads.append(Subscribe(exchanges.FTX_trades(id=1), serializer))

if not threads:
    print("Unknown exchanges given. Try use -h for help")

for thread in threads:
    thread.start()
