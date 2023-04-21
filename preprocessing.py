import os
import datetime as dt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates


def main(df):
    new_columns = df.iloc[0].tolist()
    df_date = df["Attributes"]
    df.columns = new_columns
    for i in range(1, ((len(new_columns) - 1) // 5) + 1):
        extracted_df = pd.concat([df_date, df[new_columns[i]]], axis=1)
        extracted_df = extracted_df.drop([0, 1])
        extracted_df.columns = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']
        extracted_df["Date"] = pd.to_datetime(extracted_df['Date'])
        extracted_df = extracted_df.astype(
            {'Close': float, 'High': float, 'Open': float, 'Low': float, 'Volume': float})
        extracted_df['brand'] = new_columns[i]
        extracted_df = add_ma(extracted_df, 'Close', [9, 25])
        extracted_df = add_ma(extracted_df, 'High', [9, 25])
        extracted_df = add_ma(extracted_df, 'Low', [9, 25])
        extracted_df = add_macd(extracted_df)
        extracted_df = extracted_df.drop('Volume', axis=1)
        extracted_df = extracted_df.dropna()
        plotter(extracted_df)


def add_ma(df, col, _list):
    for i in _list:
        df[f'{col}_{str(i)}ma'] = df[col].rolling(i).mean()

    return df


def add_macd(df):
    # 普通のmacd
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    macd_df = pd.DataFrame({'macd': macd, 'signal': signal, 'hist': hist})

    # ここからがマグマmacd
    # 'hist_change'は、macdのヒストグラムが転換した箇所　１であれば買いトレンド、-1であれば売りトレンド、どちらでもなければ0
    # 'hist_next_break'は、macdのヒストグラムが前日と同じ動きをすると仮定したときm翌日に-1以上になるもの。
    macd_df['hist_diff'] = macd_df['hist'].diff()
    macd_df['hist+diff'] = macd_df['hist'] + macd_df['hist_diff']
    macd_df['h+d_p'] = macd_df['hist+diff'] > 0
    macd_df['h+d_p_shift'] = macd_df['h+d_p'].shift(1)

    macd_df['h+d_d'] = macd_df['hist+diff'].diff()
    macd_df['hist_next_break'] = np.where(
        (macd_df['h+d_d'] > 0) & (macd_df['hist+diff'] > -1) & (macd_df['hist+diff'] < 0), 1, 0)

    macd_df['hist_change'] = macd_df.apply(
        lambda x: 1 if x['h+d_p'] and not x['h+d_p_shift'] else -1 if not x['h+d_p'] and x['h+d_p_shift'] else 0,
        axis=1)
    macd_df = macd_df.drop(["h+d_p", "h+d_p_shift", 'hist', 'hist_diff', 'hist+diff', 'h+d_d', 'signal', 'macd'],
                           axis=1)
    macd_df = macd_df.dropna()
    df = pd.concat([df, macd_df], axis=1)

    return df


def plotter(df):
    col_list = list(df.columns)
    df = df.drop(['High', 'Low', 'Open'], axis=1)
    print(col_list)
    _c= [c for c in col_list if 'ma' in c]
    print(_c)
    df = df.set_index('Date')
    fig, ax1 = plt.subplots(figsize=(12, 8))

    ax1.plot(df.index, df['Close'], label='Close')
    for c in _c:
        ax1.plot(df.index, df[c], label=c)

    ax2 = ax1.twinx()
    ax2.bar(df.index, df['hist_next_break'], width=0.7, alpha=0.5, color='blue', label='next')
    # ax2.bar(df.index, df['hist_change'] == 1, width=0.7, alpha=0.5, color='red', label='change')
    ax1.legend()
    ax2.legend()

    plt.show()
