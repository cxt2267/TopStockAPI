import requests
import numpy as np

finnhub_key = 'crqt1lpr01qq1umo36igcrqt1lpr01qq1umo36j0'
twelve_data_key = '36d39ccc172449c091471d1fd7c99b9f'
nasdaq_key = 'yUsnbQkLKvTCUhKNrM9x'

def US_stock_list():
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

def analyze_day_trading(stock_symbol):
    time_series_url = f"https://api.twelvedata.com/time_series?symbol={stock_symbol}&interval=1min&apikey={twelve_data_key}&outputsize=100"
    quote_url = f"https://api.twelvedata.com/quote?symbol={stock_symbol}&apikey={twelve_data_key}"
    
    # Fetch minute data 
    response = requests.get(time_series_url)
    if response.status_code != 200:
        raise Exception(f"Error fetching data: {response.json()['message']}")
        return -1
    
    data = response.json().get('values', [])
    
    if not data:
        print(response.json())
        return -1, "No data available for this stock."

    prices = np.array([float(entry['close']) for entry in data])
    volumes = np.array([float(entry['volume']) for entry in data])
    
    # Calculate average price change and volatility
    price_changes = np.diff(prices)
    average_change = np.mean(price_changes) / prices[0] * 100  
    volatility = np.std(prices)  
    average_volume = np.mean(volumes)  

    # Fetch latest quote 
    response_quote = requests.get(quote_url)
    if response_quote.status_code != 200:
        raise Exception(f"Error fetching quote data: {response_quote.json()['message']}")
    
    quote_data = response_quote.json()
    pe_ratio = float(quote_data.get('pe', 0))
    market_cap = float(quote_data.get('market_cap', 0))
    
    # Moving Averages
    short_moving_average = np.mean(prices[-5:])  
    long_moving_average = np.mean(prices[-20:]) 
    
    # RSI Calculation
    gain = np.where(price_changes > 0, price_changes, 0)
    loss = np.where(price_changes < 0, -price_changes, 0)
    average_gain = np.mean(gain[-14:])  
    average_loss = np.mean(loss[-14:])
    rs = average_gain / average_loss if average_loss != 0 else 0
    rsi = 100 - (100 / (1 + rs))
    
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

    # Moving Averages Rating
    if short_moving_average > long_moving_average:
        ratings['moving_averages'] = 5
        reasoning.append("Short-term moving average above long-term indicates bullish trend.")
    elif short_moving_average < long_moving_average:
        ratings['moving_averages'] = 1
        reasoning.append("Short-term moving average below long-term indicates bearish trend.")
    else:
        ratings['moving_averages'] = 3
        reasoning.append("Moving averages are flat; mixed signals.")

    # RSI Rating
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

    # P/E Ratio Rating
    if pe_ratio < 15:
        ratings['pe_ratio'] = 5
        reasoning.append("P/E ratio indicates the stock is undervalued, potentially attractive for traders.")
    elif pe_ratio < 25:
        ratings['pe_ratio'] = 3
        reasoning.append("P/E ratio is reasonable; cautious optimism.")
    else:
        ratings['pe_ratio'] = 1
        reasoning.append("P/E ratio suggests the stock is overvalued, caution advised.")

    # Market Cap Rating
    if market_cap > 10**10:  # Large cap
        ratings['market_cap'] = 5
        reasoning.append("Large market cap indicates stability and less volatility.")
    elif market_cap < 10**9:  # Small cap
        ratings['market_cap'] = 2
        reasoning.append("Small market cap may lead to higher volatility and risk.")
    else:
        ratings['market_cap'] = 3
        reasoning.append("Mid-cap stock; moderate risk and stability.")

    # Define weights for each criterion
    weights = {
        'price_movement': 0.25,
        'volatility': 0.20,
        'volume': 0.20,
        'moving_averages': 0.15,
        'rsi': 0.10,
        'pe_ratio': 0.05,
        'market_cap': 0.05
    }

    # Calculate the weighted average rating
    weighted_average = sum(ratings[criterion] * weights[criterion] for criterion in ratings)
    
    final_rating = round(min(max(weighted_average, 1.00), 5.00), 2)
    final_rating = round(weighted_average, 2)

    return final_rating, " | ".join(reasoning)

stocks = US_stock_list()
ratings = []
highest_rating = {'stock': '', 'rating': 1}
lowest_rating = {'stock': '', 'rating': 5}

for stock in stocks[:3]:
    rating = analyze_day_trading(stock['symbol'])
    if rating == -1:
        continue
    rating_info = {
        'stock': f"{stock['symbol']}",
        'rating': rating
    }
    if rating_info['stock'] == 'WYCC':
        print('WYCC: ' + rating_info['rating'])
    ratings.append(rating_info)
    if rating_info['rating'] < lowest_rating['rating']:
       lowest_rating = rating_info

    if rating_info['rating'] > highest_rating['rating']:
       highest_rating = rating_info

print(f'highest rated: {highest_rating} \n lowest rated: {lowest_rating}')

#stock_symbol = "GOOG"  # Example stock symbol
#day_trading_rating, reasoning = analyze_day_trading(stock_symbol)
#print(f"The day trading rating for {stock_symbol} is: {day_trading_rating} - Reason: {reasoning}")