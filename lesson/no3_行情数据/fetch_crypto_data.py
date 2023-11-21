# -*- encoding: utf-8 -*-
'''
@File    :   fetch_crypto_data.py
@Desc    :   用ccxt 获取crypto数据
'''

# here put the import lib

import json
import numpy
import pandas as pd
from datetime import datetime, timezone

# 交易所接口
import ccxt

# 代理
inParas = {
    "http_prox": "socks5h://127.0.0.1:7890",      # "socks5h://127.0.0.1:7890"
    "https_prox": "socks5h://127.0.0.1:7890",     # "socks5h://127.0.0.1:7890"
}


# 实例化交易所API接口
def LogIn():
    api_key = "111"  # 在只获取行情数据时， 不需要真实的交易密钥
    seceret_key = "222"  # 在只获取行情数据时， 不需要真实的交易密钥
    binance = ccxt.binance({"timeout": 15000, "enableRateLimit": True, "proxies": {"http": inParas["http_prox"], "https": inParas["https_prox"]}, "apiKey": api_key, "secret": seceret_key})
    print("登录成功")
    return binance


def get_klines(exchange, symbolName: str, sttime, level: str):
    kline = exchange.fapiPublicGetKlines({"symbol": symbolName, "interval": level, "startTime": sttime, "limit": 1500})
    the_df = pd.DataFrame(kline, columns=["open_time", "open", "high", "low", "close", "volume", "close_time", "deal_amount", "deal_num", "active_volume", "active_amount", "nosence"])
    the_df["open_time"] = pd.to_datetime(the_df["open_time"], unit="ms")
    return the_df


def run():
    start_date = int(datetime(2023, 1, 1, 0, 0).timestamp() * 1000)
    sym = "BTCUSDT"
    level = "5m"
    cex = LogIn()
    rdf = get_klines(cex, sym, start_date, level)
    print(rdf)


if __name__ == "__main__":
    run()
