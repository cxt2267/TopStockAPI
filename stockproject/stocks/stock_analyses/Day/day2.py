import requests
import threading
import queue
import numpy as np
import yfinance as yf

finnhub_key = 'crqt1lpr01qq1umo36igcrqt1lpr01qq1umo36j0'
twelve_data_key = '36d39ccc172449c091471d1fd7c99b9f'
nasdaq_key = 'yUsnbQkLKvTCUhKNrM9x'

def get_stock_list():
    url = 'https://finnhub.io/api/v1/stock/symbol'
    params = {
        'exchange': 'US',
        'token': finnhub_key
    }
    resp = requests.get(url, params=params)

    if resp.status_code == 200:
        return resp.json()
    else:
        raise Exception(f'failed to retrieve stock list: {resp.status_code} {resp.text}')

def day_trade_rating(stock_symbol, result_queue):
    stock = yf.Ticker(stock_symbol)

    data = stock.history(period="1d", interval="1m")

    if data.empty:
        result_queue.put((stock_symbol, -1, f"No data available for {stock_symbol}"))
        return -1, f"No data available for {stock_symbol}"

    prices = np.array(data['Close'].values)
    volumes = np.array(data['Volume'].values)

    price_changes = np.diff(prices)
    average_change = np.mean(price_changes) / prices[0] * 100  
    volatility = np.std(prices)  
    average_volume = np.mean(volumes)  

    info = stock.info
    pe_ratio = info.get('trailingPE', 0)  
    if not isinstance(pe_ratio, (int, float)):
        pe_ratio = 0
    market_cap = info.get('marketCap', 0)  

    # Moving Averages
    short_moving_average = np.mean(prices[-5:])  
    long_moving_average = np.mean(prices[-20:])  

    # RSI Calculation
    gains = np.where(price_changes > 0, price_changes, 0)
    losses = np.where(price_changes < 0, -price_changes, 0)
    average_gain = np.mean(gains[-14:]) 
    average_loss = np.mean(losses[-14:])
    rs = average_gain / average_loss if average_loss != 0 else 0
    rsi = 100 - (100 / (1 + rs))

    # Initialize ratings for each criterion
    ratings = {}
    reasoning = []

    # Price Movement Rating
    if average_change >= 3:
        ratings['price_movement'] = 5
        reasoning.append("Strong average price change indicating potential for profit.")
    elif average_change >= 1:
        ratings['price_movement'] = 4
        reasoning.append("Moderate average price change; may be suitable for day trading.")
    elif average_change >= 0:
        ratings['price_movement'] = 3
        reasoning.append("Low average price change; not favorable for day trading.")
    else:
        ratings['price_movement'] = 1
        reasoning.append("Negative average price change; avoid.")

    # Volatility Rating
    if volatility < 2:
        ratings['volatility'] = 5
        reasoning.append("Low volatility suggests stability, which is ideal for day trading.")
    elif volatility < 4:
        ratings['volatility'] = 4
        reasoning.append("Moderate volatility may present some risk.")
    elif volatility < 6:
        ratings['volatility'] = 3
        reasoning.append("High volatility increases risk for day traders.")
    else:
        ratings['volatility'] = 1
        reasoning.append("Very high volatility; unsuitable for day trading.")

    # Volume Rating
    if average_volume > 1000000:
        ratings['volume'] = 5
        reasoning.append("High trading volume indicates strong interest and liquidity.")
    elif average_volume > 500000:
        ratings['volume'] = 4
        reasoning.append("Moderate trading volume; may still be suitable for day trading.")
    elif average_volume > 100000:
        ratings['volume'] = 3
        reasoning.append("Low trading volume suggests limited liquidity; proceed with caution.")
    else:
        ratings['volume'] = 1
        reasoning.append("Very low trading volume; avoid.")

    if short_moving_average > long_moving_average:
        ratings['moving_averages'] = 5
        reasoning.append("Short-term moving average above long-term indicates bullish trend.")
    elif short_moving_average < long_moving_average:
        ratings['moving_averages'] = 1
        reasoning.append("Short-term moving average below long-term indicates bearish trend.")
    else:
        ratings['moving_averages'] = 3
        reasoning.append("Moving averages are flat; mixed signals.")

    if rsi < 30:
        ratings['rsi'] = 5
        reasoning.append("RSI indicates the stock is oversold; potential for price increase.")
    elif rsi < 50:
        ratings['rsi'] = 4
        reasoning.append("RSI indicates a balanced condition; suitable for trading.")
    elif rsi < 70:
        ratings['rsi'] = 3
        reasoning.append("RSI indicates the stock is nearing overbought conditions; caution advised.")
    else:
        ratings['rsi'] = 1
        reasoning.append("RSI above 70 indicates overbought conditions; avoid.")

    if pe_ratio < 15:
        ratings['pe_ratio'] = 5
        reasoning.append("P/E ratio indicates the stock is undervalued, potentially attractive for traders.")
    elif pe_ratio < 25:
        ratings['pe_ratio'] = 3
        reasoning.append("P/E ratio is reasonable; cautious optimism.")
    else:
        ratings['pe_ratio'] = 1
        reasoning.append("P/E ratio suggests the stock is overvalued, caution advised.")

    if market_cap > 10**10:  # Large cap
        ratings['market_cap'] = 5
        reasoning.append("Large market cap indicates stability and less volatility.")
    elif market_cap < 10**9:  # Small cap
        ratings['market_cap'] = 2
        reasoning.append("Small market cap may lead to higher volatility and risk.")
    else:
        ratings['market_cap'] = 3
        reasoning.append("Mid-cap stock; moderate risk and stability.")

    weights = {
        'price_movement': 0.25,
        'volatility': 0.20,
        'volume': 0.20,
        'moving_averages': 0.15,
        'rsi': 0.10,
        'pe_ratio': 0.05,
        'market_cap': 0.05
    }

    weighted_average = sum(ratings[criterion] * weights[criterion] for criterion in ratings)

    final_rating = round(min(max(weighted_average, 1.00), 5.00), 2)

    result_queue.put((stock_symbol, final_rating, " | ".join(reasoning)))
    return final_rating, " | ".join(reasoning)

unfound = []
stocks = get_stock_list()
stock_symbols = [stock['symbol'] for stock in stocks[:19000]]
'''for stock in stocks[:10]:
    rating, explanation = day_trade_rating(stock["symbol"])
    if rating == -1:
        #print(f"{stock["symbol"]}: no data found")
        unfound.append(stock["symbol"])
        continue 
    #print(f"{stock["symbol"]}: Rating = {rating}, Reasoning = {explanation}")

print(len(unfound)/len(stocks))'''

result_queue = queue.Queue()
#threads = []
#results = []

'''for stock in stocks[:1000]:
    threads.append(threading.Thread(target=day_trade_rating, args=(stock["symbol"], result_queue)))

for i in range(len(stocks[:1000])):
    threads[i].start()

for j in range(len(stocks[:1000])):
    threads[j].join()

for k in range(len(stocks[:1000])):
    results.append(result_queue.get())

print(results[:1000])'''

def worker(stock_symbols, result_queue):
    for stock_symbol in stock_symbols:
        day_trade_rating(stock_symbol, result_queue)

def all_day_trade_ratings(stock_symbols, num_threads=10):
    batch_size = len(stock_symbols) // num_threads
    threads = []

    for i in range(num_threads):
        start_idx = i * batch_size
        end_idx = (i + 1) * batch_size if i != num_threads - 1 else len(stock_symbols)
        thread = threading.Thread(target=worker, args=(stock_symbols[start_idx:end_idx], result_queue))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    results = []
    while not result_queue.empty():
        results.append(result_queue.get())

    return results

num_threads = 10000

final_results = all_day_trade_ratings(stock_symbols, num_threads)

for result in final_results[:300]:
    print(result)

print(len(final_results))