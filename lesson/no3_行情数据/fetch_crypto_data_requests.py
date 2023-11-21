# -*- encoding: utf-8 -*-
'''
@File    :   .py
@Desc    :   通过api 请求数据
'''

# here put the import lib
import requests

proxy = {
    "http": "http://192.168.1.2:7890",
    "https": "https://192.168.1.2:7890"
}

# # Binance API endpoint
url = "https://api.binance.com/api/v3/klines"
# allPrice = requests.get("https://api.binance.com/api/v3/ticker/price")  # 获取所有现货交易对最新价格

params = {
    "symbol": "BTCUSDT",     # Trading pair symbol
    "interval": "1m",        # Kline interval (e.g., 1m, 5m, 1h, 1d)
    "limit": 500,            # Number of Klines to retrieve (maximum: 1000)
}

response = requests.get(url, params=params)  # 若需要proxy， 将参数传入 proxies=proxy
klines = response.json()
print(klines)