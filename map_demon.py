# -*- coding:utf-8 -*-

import pandas as pd

data = [["小王", "男", 29], ["小李", '女', 12], ["小刘", "男", 18]]

df = pd.DataFrame(data=data, columns=["name", "sex", "age"])

print(df.dtypes)

df["age"] = df['age'].astype("object")

df["name"] = df["name"].str.replace("小","")
print(df.dtypes)

df.loc[:, "sex"] = df["sex"].map({"男": 1, "女": 0})

print(df)
