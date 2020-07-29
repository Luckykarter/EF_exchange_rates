# EF_exchange_rates
Home coding task for Efficient Frontier

Explanation of the solution and task description can be found in [EXPLANATION.md](https://github.com/Luckykarter/EF_exchange_rates/blob/master/EXPLANATION.md)

This app subscribes to public WebSockets of exchanges Binance and FTX in order to print orders bids and asks price/size every second.
The sources of data and update interval can be configured using the command line parameters.

To execute app:
`python exchangerates.py`

Command line possible arguments:
| Argument  | Description  |
|---|---|
| -h --help | Display arguments description |
| --raw     | Print raw data received from exchanges | 
| --delay DELAY | Specify custom delay for output in seconds (default: 1.0 second) |
| --mid-price-ago MID_PRICE_AGO | Specify time for mid-price historical data in hours (default: 1.0 hour) |
| EXCHANGE | Positional argument (can be multiple) - specify data sources. If not provided - all are used |
                        
### Used libraries:
#### websocket-client
Simple easy-to-use low-level client for WebSocket. Other options are Flask, Django or websockets (not chosen since for Django/Flask application becomes heavy, websockets requires async programming and more complicated to maintain)

#### maya
Single purpose - parse datetime timestamp from trades channel to print it in required format

#### PrettyTable
Used for formatting output as a table

### Solution concept:

The main thread of application fires up concurrent threads per each data-channel (i.e. exchange).
Each thread subscribes to a dedicated channel (via WebSocket) and continuously gets data from it.
Each portion of data is serialized and printed to console

#### Modules structure:
- `class Subscribe` - responsible for subscription and unsubscription to a certain exchange
- `class Exchange` - abstract class for definition of the necessary structures/methods to subscribe and print data
  - `class Binance` -  contains data to subscribe to Binance orderbook and logic to print data from it
  - `class FTX` - contains data to subscribe to FTX orderbook and logic to print data from it
    - `class FTX_trades` - contains data to subscribe to FTX trades and logic to print data from it
- `class Serializer` - responsible for serializing and printing formatted or raw data with the given delay in console
- `class ConnectToWS` - connector for establishing WebSocket connection


