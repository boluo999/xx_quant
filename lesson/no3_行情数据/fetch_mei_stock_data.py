# -*- encoding: utf-8 -*-
'''
@File    :   fetch_mei_stock_data.py
@Desc    :   获取美股数据
'''

# here put the import lib
import yfinance as yf

# 获取苹果股票的一小时级别K线数据
apple = yf.Ticker("AAPL")
data = apple.history(period="1y", interval="1h")


data.to_csv("/Users/macos/project23/backtest_study/bt_proj/b_data/AAPL_1h.csv")
# 打印数据
print(data)
