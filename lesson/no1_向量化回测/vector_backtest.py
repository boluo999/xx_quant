# -*- encoding: utf-8 -*-
'''
@File    :   vector_backtest.py
@Desc    :   向量化计算并执行交易回测。
    原理可以看看excel 以及对应的说明文档 num1说明文档.md
'''

# here put the import lib
import pandas as pd
import matplotlib.pyplot as plt


def get_df_from_csv():
    # 从csv 获取数据
    path = "market_data/btc5m.csv"
    # index 也换成日期了
    df = pd.read_csv(path, float_precision="round_trip", parse_dates=["open_time"], index_col="open_time")
    # float_precision 精度问题, parse_dates 将 x 列设置为时间类型, index_col 将x列设置为索引
    df["date"] = df.index
    # 下面开始做需要的各种数据
    # sigdf = df[["date", "close", "high", "low", "open", "volume"]]
    sigdf = df[["date", "open", "high", "low", "close", "volume"]]
    return sigdf

def vector_calc_factors(df):
    sdf = df.copy()
    # 计算均线
    sdf = sdf.assign(sma10=sdf["close"].rolling(10).mean().shift(1))
    sdf = sdf.assign(sma50=sdf["close"].rolling(50).mean().shift(1))
    # 保留小数位
    sdf = sdf.round({"sma10": 4,"sma50": 4,})
    # 选择输出哪些指标
    adf = sdf[["date", "open", "high", "low", "close", "volume", "sma10", "sma50"]]
    return adf

def exec_stg(df):
    # 执行策略， 得出仓位
    edf = df.copy()
    edf["position"] = edf.apply(lambda x: 1 if x.sma10 > x.sma50  else 0, axis=1)
    return edf

def calc_netValue(df):
    # 计算净值曲线、归一化价格、以及相关评价指标
    cdf = df.copy()
    cdf = cdf.assign(retn=lambda x: cdf["close"] / cdf["close"].shift(1) - 1)
    cdf = cdf.assign(fprice=cdf["retn"].cumsum() + 1)  # 计算归一化的价格变化曲线
    # 计算净值
    cdf["return"] = cdf["retn"] * cdf["position"].shift(1)  # 仓位向下平移1行。 上一行的信号，下一行产生仓位
    cdf["netLine"] = cdf["return"].cumsum() + 1  # 收益简单相加，单利
    return cdf


def hua_tu_here(df):
    # plt.style.available
    plt.style.use("seaborn-darkgrid")
    pdf = df.copy()
    # 画净值图
    stdate = "2021-12-1 0:00"
    enddate = "2022-2-10 9:00"
    fig = plt.figure(figsize=(12, 10))
    # 定义图1，以及它的坐标(距最左边, 距下面, 图长, 图宽)，ylim 是纵轴坐标范围
    ax1 = fig.add_axes([0.1, 0.35, 0.85, 0.5])
    # 图1的数据等信息参数
    # ax1.plot(adf.loc["2022-03-04 22:40":, ["gprice", "netLine", "gpmax", "gpmin"]])
    ax1.plot(pdf.loc[stdate:enddate, ["fprice", "netLine"]])
    plt.show()


if __name__ == "__main__":
    data_df = get_df_from_csv()  # 从csv得到数据
    signal_df = vector_calc_factors(data_df)  # 信号 or 因子计算
    pos_df = exec_stg(signal_df)  # 计算仓位
    rdf = calc_netValue(pos_df)  # 计算净值等
    print("--- 计算完毕!")
    hua_tu_here(rdf)  # 画图

