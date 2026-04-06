CREATE SCHEMA IF NOT EXISTS mart;

CREATE OR REPLACE TABLE mart.dim_product AS
SELECT
    p.product_id,
    p.product_name,
    p.aisle_id,
    a.aisle,
    p.department_id,
    d.department
FROM products p
LEFT JOIN aisles a
    ON p.aisle_id = a.aisle_id
LEFT JOIN departments d
    ON p.department_id = d.department_id;

CREATE OR REPLACE TABLE mart.dim_customer AS
SELECT
    user_id AS customer_id,
    MIN(order_number) AS first_order_number,
    MAX(order_number) AS last_order_number,
    COUNT(*) AS total_orders,
    AVG(days_since_prior_order) AS avg_days_between_orders
FROM orders
GROUP BY user_id;

CREATE OR REPLACE TABLE mart.dim_order_day AS
SELECT DISTINCT
    order_dow AS order_day_id,
    order_dow,
    CASE order_dow
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END AS day_name,
    CASE
        WHEN order_dow IN (0, 6) THEN TRUE
        ELSE FALSE
    END AS is_weekend
FROM orders;

CREATE OR REPLACE TABLE mart.dim_order_time AS
WITH base AS (
    SELECT DISTINCT
        CAST(order_hour_of_day AS INTEGER) AS hour
    FROM orders
)
SELECT
    hour AS order_time_id,
    hour AS order_hour_of_day,
    LPAD(CAST(hour AS VARCHAR), 2, '0') || ':00' AS hour_label,
    CASE
        WHEN hour BETWEEN 0 AND 5 THEN 'Night'
        WHEN hour BETWEEN 6 AND 11 THEN 'Morning'
        WHEN hour BETWEEN 12 AND 17 THEN 'Afternoon'
        ELSE 'Evening'
    END AS time_bucket
FROM base;

CREATE OR REPLACE TABLE staging_order_items AS
SELECT * FROM order_products_prior
UNION ALL
SELECT * FROM order_products_train;

CREATE OR REPLACE TABLE mart.order_basket_size AS
SELECT
    order_id,
    COUNT(*) AS basket_size
FROM staging_order_items
GROUP BY order_id;

CREATE OR REPLACE TABLE mart.fact_order_items AS
SELECT
    op.order_id,
    o.user_id AS customer_id,
    op.product_id,
    CAST(o.order_dow AS INTEGER) AS order_day_id,
    CAST(o.order_hour_of_day AS INTEGER) AS order_time_id,
    o.order_number,
    CAST(o.days_since_prior_order AS DOUBLE) AS days_since_prior_order,
    o.eval_set,
    COALESCE(obs.basket_size, 0) AS basket_size,
    op.add_to_cart_order,
    op.reordered,
    CASE
        WHEN CAST(o.order_dow AS INTEGER) IN (0, 6) THEN TRUE
        ELSE FALSE
    END AS is_weekend
FROM staging_order_items op
INNER JOIN orders o
    ON op.order_id = o.order_id
LEFT JOIN mart.order_basket_size obs
    ON op.order_id = obs.order_id;