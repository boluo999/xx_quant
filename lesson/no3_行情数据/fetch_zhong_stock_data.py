# -*- encoding: utf-8 -*-
'''
@File    :   fetch_zhong_stock_data.py
@Desc    :   用开源的akshare库, 获取证券数据
'''

# here put the import lib


import akshare as ak

print("start ~~")
stock_zh_a_minute_df = ak.stock_zh_a_minute(symbol='sh600519', period='60', adjust="qfq")
stock_zh_a_minute_df.to_csv("/Users/macos/project23/backtest_study/bt_proj/b_data/stock_519.csv", index=0)

print(stock_zh_a_minute_df)