# -*- encoding: utf-8 -*-
'''
@File    :   event_drive_backtest.py
@Desc    :   事件驱动回测框架。
    最简单版本， 主要是为了学习理解。
    速度比向量化方式更慢， 但用循环 逐行读取数据的方式很类似实际交易情况。 是必要的学习内容。
    向量化方法回测相对于事件驱动回测优点在于直观与计算效率高, 但是对于复杂策略或者模拟真实交易情形时, 向量方法复原能力较弱. 
    引入适当的回测框架可以实现代码在不同策略下的重复利用, 这也体现出了模块化编程的思想. 
'''


# here put the import lib
# here put the import lib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from decimal import *

plt.style.use("seaborn")



class TickData:
    """
    结构化数据
    TickData对象, 用于记录日期(date), 收盘价(close). 这里将使用均值回归策略(MeanRevertingStrategy)进行回测, 仅需要记录日期和收盘价信息. 在使用更复杂策略回测时, 可以相应地改变数据结构. 
    """
    def __init__(self, date, close):
        self.date = date
        self.close = close


class MarketDataSource:
    """
    2、数据获取, 清洗与模拟
    MarketDataSource对象记录了标的(symbol), 开始与结束时间(start, end). 在MarketDataSource中, 定义download_data和clean_data方法用于下载和清洗数据, 定义start_simulation方法对数据(DataFrame对象)进行逐行迭代, 产生价格信息(tick_data). 将价格信息传递给策略(strategy), 判断是否产生交易信号以及相应地改变头寸. 
    """
    def __init__(self, symbol, start, end):
        self.symbol = symbol
        self.start = start
        self.end = end
        self.data = None

    def load_data(self, path):
        # self.data = ts.get_k_data(self.symbol, self.start, self.end)
        # csv_path = "./kline_data/btc1m.csv"
        df = pd.read_csv(path, float_precision="round_trip", parse_dates=["open_time"], index_col="open_time")
        self.data = df.loc[self.start : self.end]

    # def clean_data(self):
    #     self.data.index = pd.to_datetime(self.data.open_time)
    #     self.data = self.data.sort_index()

    def start_simulation(self, strategy, position):
        for date, row in self.data.iterrows():
            # 定义数据
            tick_data = TickData(date, row["close"])
            # 将数据传入 价格量等数据传入 strategy类， 并更新类中的仓位、side、order（需判定）等信息
            strategy.event_tick(tick_data)
            strategy.event_position(position)
            strategy.event_order()
            if strategy.order is not None:
                # 如果stg中order 不为空，则将其中 date、side、price、qty 传入 position 类
                # position 类会模拟交易，计算仓位、资产总额、Pnl 等
                position.operate(strategy.order.date, strategy.order.is_buy, strategy.order.price, strategy.order.qty)


class Position:
    """
    头寸管理
    Position对象记录头寸相关信息. operate方法用于计算每次交易时现金(cash), 证券资产(net), 策略净值(net_value)变化情况, display方法用于打印出头寸中现金, 证券资产和净值信息. 
    """
    def __init__(self):
        self.buys = 0
        self.sells = 0
        self.net = 0
        self.cash = 0
        self.net_value = 0
        # 加一条pnl值
        self.rpnl = pd.DataFrame()
        # 加初始本金
        self.baseMoney = 100000

    def operate(self, date, is_buy, price, qty):
        if is_buy:
            self.buys += qty
            self.net = self.buys - self.sells
            print("Date: {}, Trade: Buy, Price: {}, Qty: {}, position: {}".format(date.strftime("%Y-%m-%d %H:%M"), price, qty, self.net))

        else:
            self.sells += qty
            self.net = self.buys - self.sells
            print("Date: {}, Trade: Sell, Price: {}, Qty: {}, position: {}".format(date.strftime("%Y-%m-%d %H:%M"), price, qty, self.net))
        self.cash += price * qty * (-1 if is_buy else 1)
        self.net_value = self.cash + self.net * price
        # 增加了pnl
        self.rpnl.loc[date, "rPnl"] = self.net_value
        self.rpnl.loc[date, "netv"] = (self.baseMoney + self.net_value) / self.baseMoney
        self.rpnl.loc[date, "price"] = price
        self.rpnl.loc[date, "position"] = self.net

    def display(self):
        print("Position Info: Cash剩余现金: {}, net持仓量: {}, NetValue净增长: {}".format(self.cash, self.net, self.net_value))
        adf = self.rpnl.copy()
        adf = adf.assign(returnss=lambda x: adf["price"] / adf["price"].shift(1) - 1)
        adf = adf.assign(gprice=adf["returnss"].cumsum() + 1)
        adf[["gprice", "netv"]].plot(figsize=(12, 8), title="BTC_meanRevert", fontsize=12)
        plt.show()


class Order:
    # 4、交易指令
    def __init__(self, date, is_buy, price, qty):
        self.date = date
        self.is_buy = is_buy
        self.price = price
        self.qty = qty


class MeanRevertingStrategy:
    """
    均值回归策略
    初始化MeanRevertingStrategy需要给定计算均值周期(cycle), 买卖信号产生的阈值(buy_threshold, sell_threshold). event_tick, event_position方法分别用于接收MarketDataSource.start_simulation迭代产生的价格数据和头寸信息, event_order方法判断是否产生交易指令(order), 并将order记录为策略的属性值. 
    """
    def __init__(self, cycle=20, buy_threshold=-1.5, sell_threshold=1.3):
        self.cycle = cycle
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.prices = pd.DataFrame()
        self.is_long = False
        self.is_short = False
        self.order = None

    def event_tick(self, tick_data):
        self.prices.loc[tick_data.date, "close"] = tick_data.close

    def event_position(self, position):
        # position.net 是现有仓位
        if position.net > 0:
            self.is_long, self.is_short = True, False
        elif position.net < 0:
            self.is_long, self.is_short = False, True
        else:
            self.is_long = self.is_short = False

    def event_order(self):
        if len(self.prices) < self.cycle:
            self.order = None
        else:
            # 计算因子 z值
            z = self.calculate_z_score()
            # 执行判断
            if self.is_long is False and z < self.buy_threshold:
                self.order = Order(self.prices.index[-1], is_buy=True, price=self.prices.close[-1], qty=1)
            elif self.is_short is False and z > self.sell_threshold:
                self.order = Order(self.prices.index[-1], is_buy=False, price=self.prices.close[-1], qty=1)
            else:
                self.order = None

    def calculate_z_score(self):
        window = self.prices[-self.cycle :]
        ret = window["close"].pct_change().dropna()
        z = ((ret[-1]) - ret.mean()) / ret.std()
        return z


class BackTester:
    """
    回测对象
    建立回测对象的实例需要初始化代码, 起止时间. check_position方法用于检测当前回测对象的实例是否已经存在头寸. start_back_test方法整合了MarketDataSource中的方法, 产生回测信息. 
    """
    def __init__(self, symbol, start, end):
        self.symbol = symbol
        self.start = start
        self.end = end
        self.position = None
        self.strategy = None

    def check_position(self):
        if self.position is None:
            self.position = Position()
        else:
            return None

    def start_back_test(self, path):
        market_data_source = MarketDataSource(self.symbol, self.start, self.end)
        market_data_source.load_data(path)
        # market_data_source.clean_data()
        print("Start Simulation: ")
        # 下面是主循环， 开始跑循环. 传入策略 与 仓位两个参数
        market_data_source.start_simulation(self.strategy, self.position)
        self.position.display()  # 画图
        print("Completed. ")


if __name__ == "__main__":
    # 执行回测
    _path = "market_data/btc5m.csv"
    back_tester = BackTester("BTCUSDT", "2021-12-01", "2022-03-01")
    back_tester.check_position()
    back_tester.strategy = MeanRevertingStrategy()
    back_tester.start_back_test(_path)
