# retailanalyticplatform

# Retail Analytic Platform – Instacart Market Basket

![Python](https://img.shields.io/badge/Python-3.11-blue)
![DuckDB](https://img.shields.io/badge/DuckDB-Analytics-orange)
![Dataset](https://img.shields.io/badge/Data-Kaggle-green)
![Status](https://img.shields.io/badge/Project-In%20Progress-yellow)

Retail analytics project based on the Instacart Market Basket dataset.

The objective is to build a complete analytics pipeline including:

- data ingestion
- data modeling with a star schema
- retail analytics
- market basket analysis
- customer analytics
- demand forecasting

This project demonstrates practical data engineering and business intelligence workflows using Python and DuckDB.

## Dataset

Source: Kaggle – Instacart Market Basket Analysis

The dataset contains over:

- 3.4 million orders
- 200k customers
- 50k products
- 30+ million order-product relationships

Files used:

- `orders.csv`
- `products.csv`
- `aisles.csv`
- `departments.csv`
- `order_products__prior.csv`
- `order_products__train.csv`

## Project Architecture

```text
Kaggle Dataset
      ↓
Python Ingestion
      ↓
DuckDB
      ↓
Star Schema
      ↓
Retail Analytics
      ↓
Market Basket Analysis
      ↓
Customer Analytics
      ↓
Forecasting
```

## Data Model

The analytical model is built around the order-item grain:

1 row = 1 product in 1 order

This grain supports:

- basket size analysis
- product popularity analysis
- reorder behavior analysis
- customer segmentation
- market basket analysis
- time-based order exploration

## Star schema

```mermaid
erDiagram
    FACT_ORDER_ITEMS {
        INTEGER order_id
        INTEGER customer_id
        INTEGER product_id
        INTEGER order_day_id
        INTEGER order_time_id
        INTEGER order_number
        DOUBLE days_since_prior_order
        VARCHAR eval_set
        INTEGER basket_size
        INTEGER add_to_cart_order
        INTEGER reordered
        BOOLEAN is_weekend
    }

    DIM_PRODUCT {
        INTEGER product_id
        VARCHAR product_name
        INTEGER aisle_id
        VARCHAR aisle
        INTEGER department_id
        VARCHAR department
    }

    DIM_CUSTOMER {
        INTEGER customer_id
        INTEGER first_order_number
        INTEGER last_order_number
        INTEGER total_orders
        DOUBLE avg_days_between_orders
    }

    DIM_ORDER_DAY {
        INTEGER order_day_id
        INTEGER order_dow
        VARCHAR day_name
        BOOLEAN is_weekend
    }

    DIM_ORDER_TIME {
        INTEGER order_time_id
        INTEGER order_hour_of_day
        VARCHAR hour_label
        VARCHAR time_bucket
    }

    FACT_ORDER_ITEMS }o--|| DIM_PRODUCT : product_id
    FACT_ORDER_ITEMS }o--|| DIM_CUSTOMER : customer_id
    FACT_ORDER_ITEMS }o--|| DIM_ORDER_DAY : order_day_id
    FACT_ORDER_ITEMS }o--|| DIM_ORDER_TIME : order_time_id
```

## Current Progress

Completed so far:

- raw Instacart data downloaded and stored in data/raw
- source files loaded into DuckDB
- analytical star schema created in the mart schema
- fact table built at the order-item grain
- core dimensions created:
	dim_product
	dim_customer
	dim_order_day
	dim_order_time

## Repository Structure

```text
retail-analytic-platform
│
├── data
│   ├── raw
│   └── warehouse
│
├── ingestion
│
├── modeling
│
├── analytics
│
├── notebooks
│
└── README.md
```

## Planned Analyses

- Retail Analytics
	- average basket size
	- most popular products
	- department-level product demand
	- purchase patterns by day of week and hour of day
- Market Basket Analysis
	- product association rules
	- frequently bought together products
	- cross-sell opportunities
- Customer Analytics
	- purchase frequency
	- reorder behavior
	- customer segmentation
- Forecasting
	- product demand forecasting
	- department-level demand trends
	
## Technologies

- Python
- DuckDB
- Pandas
- Matplotlib
- Kaggle dataset

## Example Visualization

Coming soon.
