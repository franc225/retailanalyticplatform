# retailanalyticplatform

# Retail Analytic Platform – Instacart Market Basket

![Python](https://img.shields.io/badge/Python-3.11-blue)
![DuckDB](https://img.shields.io/badge/DuckDB-Analytics-orange)
![Dataset](https://img.shields.io/badge/Data-Kaggle-green)
![Status](https://img.shields.io/badge/Project-In%20Progress-yellow)

Retail analytics project based on the Instacart Market Basket dataset.

The objective is to build a complete analytics pipeline including:

- data ingestion
- data modeling (star schema)
- retail analytics
- market basket analysis
- customer analytics
- demand forecasting

The project demonstrates practical data engineering and business intelligence workflows using Python and DuckDB.

## Dataset

Source: Kaggle – Instacart Market Basket Analysis

The dataset contains over:

- 3.4 million orders
- 200k customers
- 50k products
- 30 million order-product relationships

Files used:

- orders.csv
- products.csv
- aisles.csv
- departments.csv
- order_products__prior.csv
- order_products__train.csv

## Project Architecture

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

## Repository Structure

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

## Planned Analyses

### Retail Analytics

- average basket size
- most popular products
- sales by department
- purchase patterns by day and hour

### Market Basket Analysis

- product association rules
- frequently bought together products

### Customer Analytics

- purchase frequency
- customer segmentation

### Forecasting

- product demand forecasting

## Technologies

- Python
- DuckDB
- Pandas
- Matplotlib
- Kaggle dataset

## Example Visualization

(coming soon)