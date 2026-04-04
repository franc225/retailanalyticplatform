import pandas as pd
import duckdb

path = "data/raw/orders.csv"

df = pd.read_csv(path)

print(df.shape)
print(df.head())

con = duckdb.connect("data/warehouse/retail.duckdb")

con.execute("""
CREATE TABLE orders AS
SELECT * 
FROM read_csv_auto('data/raw/orders.csv')
""")

con.execute("""
CREATE TABLE products AS
SELECT * 
FROM read_csv_auto('data/raw/products.csv')
""")

con.execute("""
CREATE TABLE order_products_prior AS
SELECT * 
FROM read_csv_auto('data/raw/order_products__prior.csv')
""")

con.sql("SELECT COUNT(*) FROM orders").show()