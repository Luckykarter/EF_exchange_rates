# Coding home task

The task is to write a simple program that connects to exchanges and writes timestamped ask/bid quotes.

### Task

1. Write a simple program that connect to exchanges via (public) websocket, subscribes to required topics in order to write the following data every second:
```
timestamp - in seconds
exchange
market
bid_price
bid_size
ask_price
ask_size
```

### Example output:
```CSV
# timestamp, exchange, market, bid_price, bid_size, ask_price, ask_size
1589301725, Binance, btcusdt, 8903.64, 0.999, 8904.27, 0.18
1589301725, FTX, BTC-PERP, 8912.0, 1.7676, 8913.0, 4.1907
1589301726, Binance, btcusdt, 8903.71, 2.0, 8904.11, 1.16
1589301726, FTX, BTC-PERP, 8910.5, 1.1335, 8913.0, 5.3237
1589301727, Binance, btcusdt, 8903.61, 0.005, 8903.62, 5.95
1589301727, FTX, BTC-PERP, 8910.5, 1.1335, 8913.0, 5.3237
1589301728, Binance, btcusdt, 8903.61, 0.993, 8904.0, 0.001
1589301728, FTX, BTC-PERP, 8909.0, 3.4298, 8913.0, 4.1907
1589301729, Binance, btcusdt, 8903.54, 0.099, 8904.99, 0.266
1589301729, FTX, BTC-PERP, 8909.0, 1.1337, 8913.0, 5.3237
```


2. add a new column, "mid price 1 hour ago" which writes the mid price (`(ask+bid)/2`) of each market, exactly 1 hour ago.

3. choose 1 exchange and subscribe to `trades` from the chosen exchange. print them as well alongside the orderbook data. 
4. _question: what new information can you learn about the orderbook updates, based on the data in these trades. how could you improve the accuracy of the orderbook updates based on this new information?_

5. implement an improved "orderbook" feed based on this data (you can print in high time resolution to show the effect).
6. _question: what can be the problems when using this additional data? how would you overcome these problems?_

## Exchanges and Markets:
choose 2 of the following exchanges and connect to their public Websocket.


| Exchange | Market  | Documentation |
| -------- | ------- | ------------- |
| Binance  | btcusdt | https://binance-docs.github.io/apidocs/futures/en/#websocket-market-streams          |
| FTX      | BTC-PERP| https://docs.ftx.com/#websocket-api          |
| Bitmex   | XBTUSD  | https://www.bitmex.com/app/wsAPI          |

## Submission

Please attach code and a document describing your process and answering the questions presented.
Partial submissions are also welcome. it's ok not to complete all the steps, however describing the steps you would take having more time is expected.