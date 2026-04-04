CREATE TABLE IF NOT EXISTS orders AS
SELECT * FROM read_csv_auto('data/raw/orders.csv');

CREATE TABLE IF NOT EXISTS products AS
SELECT * FROM read_csv_auto('data/raw/products.csv');

CREATE TABLE IF NOT EXISTS aisles AS
SELECT * FROM read_csv_auto('data/raw/aisles.csv');

CREATE TABLE IF NOT EXISTS departments AS
SELECT * FROM read_csv_auto('data/raw/departments.csv');

CREATE TABLE IF NOT EXISTS order_products_prior AS
SELECT * FROM read_csv_auto('data/raw/order_products__prior.csv');

CREATE TABLE IF NOT EXISTS order_products_train AS
SELECT * FROM read_csv_auto('data/raw/order_products__train.csv');