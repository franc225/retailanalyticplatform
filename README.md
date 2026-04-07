# retailanalyticplatform

# Retail Analytic Platform – Instacart Market Basket

![Python](https://img.shields.io/badge/Python-3.11-blue)
![DuckDB](https://img.shields.io/badge/DuckDB-Analytics-orange)
![Dataset](https://img.shields.io/badge/Data-Kaggle-green)
![Status](https://img.shields.io/badge/Stage-Customer%20Analytics-brightgreen)

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
Analytical Views
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

## Retail Analytics

Retail analytics is generated from aggregated reporting views built on top of the star schema.

The following datasets are exported for analytical exploration:

- basket size distribution
- orders by day of week
- orders by hour of day
- product popularity
- department demand
- customer ordering behavior

These aggregated datasets are visualized using Python and Matplotlib.

Visualizations include:

- basket size distribution
- orders by day of week
- orders by hour of day
- top products
- top departments
- customer order frequency distribution

## Market Basket Analysis

Market Basket Analysis identifies relationships between products frequently purchased together.

The analysis is built on the order-item fact table and computes association rules between products using DuckDB.

Key metrics include:

- support
- confidence
- lift

The association rules enable identification of:

- frequently bought together products
- cross-sell opportunities
- strong product affinities

The results are exported as CSV and visualized using Python and Matplotlib.

## Customer Analytics

Customer Analytics focuses on understanding behavioral patterns across the customer base.

The analysis uses aggregated customer metrics derived from the order-item fact table.

Key customer metrics include:

- total orders per customer
- reorder rate
- average basket size
- average days between orders

Customers are grouped into behavioral segments based on ordering frequency, enabling identification of:

- occasional buyers
- regular customers
- high-frequency users
- power users

Customer analytics visualizations include:

- purchase frequency distribution
- reorder rate distribution
- orders vs reorder rate
- customer segmentation
- basket size by segment
- ordering cadence by segment
- basket size distribution

The results are exported as CSV datasets and visualized using Python and Matplotlib.

## Star schema

The analytical model follows a classic **star schema** centered on the
`fact_order_items` table at the **order-item grain**.

Each row represents:

1 product × 1 order × 1 customer × 1 timestamp

```mermaid
erDiagram

    FACT_ORDER_ITEMS {
        int order_id FK
        int customer_id FK
        int product_id FK
        int order_day_id FK
        int order_time_id FK
        int add_to_cart_order
        int reordered
        int basket_size
    }

    DIM_PRODUCT {
        int product_id PK
        string product_name
        string aisle
        string department
    }

    DIM_CUSTOMER {
        int customer_id PK
        int total_orders
        float avg_days_between_orders
    }

    DIM_ORDER_DAY {
        int order_day_id PK
        string day_name
        bool is_weekend
    }

    DIM_ORDER_TIME {
        int order_time_id PK
        int order_hour_of_day
        string time_bucket
    }

    DIM_PRODUCT ||--o{ FACT_ORDER_ITEMS : product
    DIM_CUSTOMER ||--o{ FACT_ORDER_ITEMS : customer
    DIM_ORDER_DAY ||--o{ FACT_ORDER_ITEMS : day
    DIM_ORDER_TIME ||--o{ FACT_ORDER_ITEMS : time
```

## Retail Analytics Report

An automated HTML analytics report is generated from the visualization pipeline.

The report includes:

- key retail metrics
- customer behavior insights
- product demand analysis
- temporal order patterns

Features:

- KPI summary
- visualization grid
- interactive image zoom
- responsive layout

Example report structure:

```text
Retail Analytics Report
│
├── Key Metrics
│
├── Orders by Day
├── Orders by Hour
├── Basket Size Distribution
├── Top Products
├── Top Departments
└── Customer Order Distribution
```

## Market Basket Analysis Report

An automated HTML report is generated from the association rule analysis.

The report includes:

- key association metrics
- strongest product associations
- lift distribution
- support vs confidence analysis
- cross-sell opportunities

The report provides an interactive visualization layout with image zoom for detailed inspection.

## Customer Analytics Report

An automated HTML report is generated from the customer analytics pipeline.

The report includes:

- key customer metrics
- behavioral segmentation
- reorder behavior analysis
- basket size analysis
- purchase frequency analysis

Features:

- KPI summary
- behavioral insights
- visualization grid
- interactive image zoom
- responsive layout

Example report structure:

```text
Customer Analytics Report
│
├── Key Metrics
│
├── Purchase Frequency Distribution
├── Reorder Rate Distribution
├── Orders vs Reorder Rate
├── Customer Segmentation
├── Basket Size by Segment
├── Ordering Frequency by Segment
└── Basket Size Distribution
```

## Current Progress

Completed:

Data ingestion
- Instacart dataset downloaded from Kaggle
- raw CSV files stored in `data/raw`
- data loaded into DuckDB

Data modeling
- analytical star schema created in the `mart` schema
- fact table at the order-item grain
- product, customer, day and time dimensions

Retail analytics
- aggregated reporting views
- CSV exports for analytics
- Python visualizations
- automated HTML analytics report

Market basket analysis
- product pair generation
- association rule computation
- support, confidence and lift metrics
- cross-sell opportunity analysis
- automated HTML report with interactive visualizations

Customer analytics
- customer behavior metrics
- purchase frequency analysis
- reorder behavior analysis
- customer segmentation
- automated HTML report with behavioral insights

## Repository Structure

```text
retail-analytic-platform
│
├── data
│   ├── raw
│   ├── warehouse
│   └── exports
│       ├── association_rules.csv
│
├── ingestion
│
├── modeling
│   ├── star_schema.sql
│   └── analytical_views.sql
│
├── analytics
│   ├── validation.sql
│   └── export_views.sql
│   └── retail_visualizations.py
│   └── market_basket_visualizations.py
|
├── reports
│   ├── figures
│   ├── retail_analytics_report.html
│   ├── market_basket_report.html
│   └── customer_analytics_report.html
│
├── notebooks
│
└── README.md
```

## Planned Analyses

- Demand Forecasting
      - product demand forecasting
      - department demand trends
	
## Technologies

```markdown
- Python
- DuckDB
- Pandas
- Matplotlib
- HTML/CSS
- Kaggle dataset
```

## Example Visualization

Example visualizations generated by the pipeline:

- basket size distribution
- orders by hour
- top products
- department demand
- customer order distribution

The full visualization set is available in the generated HTML analytics report.
