import requests
import csv
import json
import os
import sys 

finnhub_key = 'crqt1lpr01qq1umo36igcrqt1lpr01qq1umo36j0'
alpha_adv_key = 'ETMK08GH4TXB9BW7'
twelve_data_key = '36d39ccc172449c091471d1fd7c99b9f'

#return list of stocks with unretrievable data and exclude them (filter from final list)
#return None if data is unretrievable
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
    
def day_trade_data(symbol):
    stock_quote_url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={finnhub_key}'
    stock_indicator_url = f'https://finnhub.io/api/v1/indicator?symbol={symbol}&resolution=D&indicator=rsi&timeperiod=14&token={finnhub_key}'
    stock_atr_url = f'https://finnhub.io/api/v1/indicator?symbol={symbol}&resolution=D&indicator=atr&timeperiod=14&token={finnhub_key}'

    quote_resp = requests.get(stock_quote_url).json()
    
    indicator_resp = requests.get(stock_indicator_url).json()

    atr_resp = requests.get(stock_atr_url).json()

    stock_data = {
        'current_price': quote_resp['c'],
        'high_price': quote_resp['h'],
        'low_price': quote_resp['l'],
        'price_change_percent': (quote_resp['c'] - quote_resp['pc']) / quote_resp['pc'] * 100,
        'volume': quote_resp['v'],
        'rsi': indicator_resp['rsi'][-1] if 'rsi' in indicator_resp else None, 
        'atr': atr_resp['atr'][-1] if 'atr' in atr_resp else None  
    }
    
    return stock_data

def day_trade_rating(symbol):
    stock_data = day_trade_data(symbol)

    volatility_weight = 0.25
    volume_weight = 0.2
    price_change_weight = 0.2
    rsi_weight = 0.15
    atr_weight = 0.2  

    volatility = (stock_data['high_price'] - stock_data['low_price']) / stock_data['current_price'] * 100
    
    normalized_volatility = min(volatility / 10, 1)
    
    normalized_volume = min(stock_data['volume'] / 1000000, 1)
    
    normalized_price_change = min(abs(stock_data['price_change_percentage']) / 5, 1)
    
    if stock_data['rsi']:
        normalized_rsi = 1 - abs(stock_data['rsi'] - 50) / 50  
    else:
        normalized_rsi = 0.5  

    if stock_data['atr']:
        normalized_atr = min(stock_data['atr'] / 5, 1)  
    else:
        normalized_atr = 0.5  

    rating = (
        (normalized_volatility * volatility_weight) +
        (normalized_volume * volume_weight) +
        (normalized_price_change * price_change_weight) +
        (normalized_rsi * rsi_weight) +
        (normalized_atr * atr_weight)
    ) * 5  
    
    return round(rating, 2)

def day_trade_reasoning(symbol):
    stock_data = day_trade_data(symbol)
    rating = day_trade_rating(symbol)
    
    reasoning = f"Day Trading Rating for {symbol}: {rating}/5\n\n"
    
    volatility = (stock_data['high_price'] - stock_data['low_price']) / stock_data['current_price'] * 100
    if volatility > 2:
        reasoning += f"- The stock shows decent volatility (High-Low price difference: {volatility:.2f}%), which is beneficial for day traders looking to capitalize on short-term price movements.\n"
    else:
        reasoning += f"- The stock's volatility ({volatility:.2f}%) is relatively low, which may limit short-term profit opportunities for day traders.\n"
    
    if stock_data['volume'] > 1000000:
        reasoning += f"- The stock has high trading volume ({stock_data['volume']} shares), ensuring liquidity and ease of entry/exit for day traders.\n"
    else:
        reasoning += f"- The stock's trading volume ({stock_data['volume']} shares) is moderate, which could make it slightly harder to quickly enter or exit trades.\n"
    
    if abs(stock_data['price_change_percentage']) > 2:
        reasoning += f"- The price has moved significantly ({stock_data['price_change_percentage']:.2f}%), indicating potential profit opportunities within the day.\n"
    else:
        reasoning += f"- The price change percentage is small ({stock_data['price_change_percentage']:.2f}%), which might limit quick profit opportunities for day traders.\n"
    
    if stock_data['rsi'] and (stock_data['rsi'] > 70 or stock_data['rsi'] < 30):
        reasoning += f"- The stock's RSI ({stock_data['rsi']:.2f}) indicates it may be overbought or oversold, which could signal a reversal, creating opportunities for day trading.\n"
    elif stock_data['rsi']:
        reasoning += f"- The stock's RSI ({stock_data['rsi']:.2f}) is in a healthy range (30-70), indicating no extreme conditions in the market.\n"
    else:
        reasoning += "- RSI data is unavailable, so it's harder to gauge whether the stock is overbought or oversold.\n"
    
    if stock_data['atr'] and stock_data['atr'] > 2:
        reasoning += f"- The stock's ATR ({stock_data['atr']:.2f}) shows a significant average price movement, making it attractive for day trading opportunities.\n"
    else:
        reasoning += f"- The stock's ATR ({stock_data['atr']:.2f}) shows a moderate average price movement, which may limit short-term gains for day traders.\n"

    return reasoning

'''aapl_data = day_trade_data('AAPL')
aapl_rating = day_trade_rating('AAPL')
aapl_reasoning = day_trade_reasoning('AAPL')
print(aapl_data)

snap_data = day_trade_data('AAPL')
snap_rating = day_trade_rating('SNAP')
snap_reasoning = day_trade_reasoning('SNAP')
print(snap_data)'''

symbol = 'AAM'
stock_quote_url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={finnhub_key}'
stock_indicator_url = f'https://finnhub.io/api/v1/indicator?symbol={symbol}&resolution=D&indicator=rsi&timeperiod=14&token={finnhub_key}'
stock_atr_url = f'https://finnhub.io/api/v1/indicator?symbol={symbol}&resolution=D&indicator=atr&timeperiod=14&token={finnhub_key}'

quote_resp = requests.get(stock_quote_url).json()
#print(quote_resp)
indicator_resp = requests.get(stock_indicator_url).json()
#print(indicator_resp)
atr_resp = requests.get(stock_atr_url).json()
#print(atr_resp)

#get all stocks (symbols)
#test value retrieval for all to see what values come up missing 

def test():
    #retrieve values 
    #conditional to render stocks with values missing (if applicable) 

    stock_list_url = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={alpha_adv_key}'
    stock_list_response = requests.get(stock_list_url)

    if stock_list_response.status_code == 200:
        decoded_content = stock_list_response.content.decode('utf-8')
        
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        stock_lists = list(cr)

        stock_list = US_stock_list()
        if isinstance(stock_list, str):
            return stock_list
        
        symbol_list = []

        for stock in stock_list:  
            symbol_list.append(stock['symbol'])

        missing_vals = []        
        
        for symbol in symbol_list[:5]:
            stock_quote_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={alpha_adv_key}'
            stock_quote_response = requests.get(stock_quote_url)

            global_quote_url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={alpha_adv_key}'
            global_quote_response = requests.get(global_quote_url)

            if global_quote_response.status_code == 200:
                global_quotes = global_quote_response.json()
                print(global_quotes)
            else:
                print(global_quote_response.status_code + " " + global_quote_response.text)
            
            '''if stock_quote_response.status_code == 200:
                stock_quotes = stock_quote_response.json()
                last_refreshed = stock_quotes.get('Meta Data', {}).get('3. Last Refreshed', 'Key not found')
                latest_data = stock_quotes.get('Time Series (1min)',{}).get(last_refreshed,{})
                stock_data = {
                    'current_price': latest_data.get('4. close', None),  
                    'high_price': latest_data.get('2. high', None),
                    'low_price': latest_data.get('3. low', None),
                    #'price_change_percentage': ((float(latest_data.get('4. close', 0)) - float(latest_data.get('1. open', 0))) / float(latest_data.get('1. open', 1)) * 100)
                                                #if latest_data.get('1. open') else 0,  
                    'previous_close': latest_data.get('1. open', None),
                    'volume': latest_data.get('5. volume', None)
                }
                print(f"{symbol}: {stock_data}")
                if (stock_data['current_price'] is None) or (stock_data['high_price'] is None) or (stock_data['low_price'] is None) or (stock_data['previous_close'] is None) or (stock_data['volume'] is None):
                    #print(f"missing value in {symbol}: {stock_data}")
                    missing_vals.append(symbol)
            else:
                print(f"Error: {stock_quote_response.status_code}")'''

        #print(f"num of stocks with missing values: {len(missing_vals)}")
    else:
        print(f"Error: {stock_list_response.status_code}")

test()