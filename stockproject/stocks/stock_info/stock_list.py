import requests
from datetime import datetime, timedelta
import random
from bs4 import BeautifulSoup
import yfinance as yf
import json
import pandas as pd
import time
from tiingo import TiingoClient


finnhub_key = 'crqt1lpr01qq1umo36igcrqt1lpr01qq1umo36j0' #aws secrets
news_key = '14eb091dc9394ce3be313c8b99f2d117' #aws secrets
tiingo_key = '549301be0ae75d793587aa29d593c2b24ab5f465' #aws_secrets
logo_dev_key = 'pk_LUFlDispSXSaLbqzvvchZw' #aws_secrets


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
        return f'failed to retrieve stock list: {resp.status_code} {resp.text}'

def get_stock_list():
    file_path = 'nasdaq_screener_1729123840337.csv'
    df = pd.read_csv(file_path)

    print(df.columns)

    stock_list = df.to_dict('records')

    return stock_list

def get_logo(symbol):
    return f"https://img.logo.dev/ticker/{symbol}?token={logo_dev_key}"

def get_current_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info  
        if 'quoteType' in info and info['quoteType'] != 'NONE':
            try:
                stock_history = stock.history(period="1d")
                if stock_history.empty:
                    current_price = None
                else:
                    current_price = stock_history['Close'].iloc[0]
            except (IndexError, ValueError):
                stock_history = stock.history(period="1mo")
                if stock_history.empty:
                    current_price = None
                else:
                    current_price = stock_history['Close'].iloc[-1]
            
            prev_close = stock.info.get('previousClose', None)

            if (prev_close is not None) and (current_price is not None):
                price_change = current_price - prev_close
                price_change_percentage = (price_change / prev_close) * 100
            else:
                price_change = None
                price_change_percentage = None
        else:
            current_price = None
            price_change = None
            price_change_percentage = None
    except Exception as e:
        current_price = None
        price_change = None
        price_change_percentage = None
    
    return {
        'price': current_price,
        'price_change': price_change,
        'price_change_percent': price_change_percentage
    }
                
def recent_news(stock_symbol):
    url = 'https://newsapi.org/v2/everything'

    curr_date = datetime.now().strftime('%Y-%m-%d')
    earliest_date = (datetime.now() - timedelta(days=31)).strftime('%Y-%m-%d')

    params = {
        'q': stock_symbol,
        'from': earliest_date,
        'to': curr_date,
        'language': 'en',
        'sortBy': 'relevancy',
        'pageSize': 100, 
        'apikey': news_key
    }
    resp = requests.get(url, params=params)

    if resp.status_code == 200:
        return resp.json()['articles']
    else:
        return f'failed to retrieve news articles: {resp.status_code} {resp.text}'

def get_stocks_info():
    stock_list = US_stock_list()
    stocks = []

    for stock in stock_list[:100]:
        curr_data = get_current_data(stock['symbol'])
        logo = get_logo(stock['symbol'])
        stock_info = {
            'logo': logo,
            'name': stock['description'],
            'symbol': stock['symbol'],
            'price': curr_data['price'],
            'price_change': curr_data['price_change'],
            'price_change_percent': curr_data['price_change_percent'],
            'day_trade_rating': round(random.uniform(1, 5), 2),
            'swing_trade_rating': round(random.uniform(1, 5), 2),
            'scalp_trade_rating': round(random.uniform(1, 5), 2),
            'position_trade_rating': round(random.uniform(1, 5), 2)
        }
        stocks.append(stock_info)
    
    return stocks

stocks = get_stocks_info()
i = 1
for stock in stocks[:10]:
    print(f"{i}: {stock}\n")
    i += 1

