import pandas as pd

path = "data/raw/orders.csv"

df = pd.read_csv(path)

print(df.shape)
print(df.head())