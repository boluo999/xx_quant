# -*- encoding: utf-8 -*-
'''
@File    :   fetch_tiekuang_data.py
@Desc    :   None
'''

# here put the import lib
import akshare as ak

futures_zh_daily_sina_df = ak.futures_zh_daily_sina(symbol="I0")
futures_zh_daily_sina_df.to_csv("/Users/macos/project23/backtest_study/bt_proj/b_data/tiekuang_1D.csv", index=0)
print(futures_zh_daily_sina_df)
# print(ak.match_main_contract(symbol="DCE"))