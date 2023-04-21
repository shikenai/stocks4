import datetime as dt
import preprocessing
import pandas as pd
import os
t = dt.datetime.now()
pd.set_option('display.max_rows', 270)
pd.set_option('display.max_columns', 20)
df_brands = pd.read_csv(os.path.join(os.getcwd(), 'data', 'nikkei_listed_20230415.csv'))
df_trades = pd.read_csv(os.path.join(os.getcwd(), 'data', 'nikkei_trades_20230415test.csv'))

preprocessing.main(df_trades)

elapsed_time = dt.datetime.now() - t
minutes, seconds = divmod(elapsed_time.total_seconds(), 60)
print(f"{minutes:.0f}分{seconds:.0f}秒")