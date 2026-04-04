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

CREATE OR REPLACE VIEW mart.v_customer_summary AS
SELECT
    customer_id,
    COUNT(DISTINCT order_id) AS total_orders,
    AVG(basket_size) AS avg_basket_size,
    AVG(days_since_prior_order) AS avg_days_between_orders,
    SUM(reordered) AS total_reordered_items
FROM mart.fact_order_items
GROUP BY customer_id;

CREATE OR REPLACE VIEW mart.v_product_summary AS
SELECT
    f.product_id,
    p.product_name,
    p.department,
    p.aisle,
    COUNT(*) AS times_ordered,
    SUM(f.reordered) AS times_reordered
FROM mart.fact_order_items f
JOIN mart.dim_product p
    ON f.product_id = p.product_id
GROUP BY
    f.product_id,
    p.product_name,
    p.department,
    p.aisle;

CREATE OR REPLACE VIEW mart.v_orders_by_day AS
SELECT
    d.day_name,
    d.order_dow,
    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(*) AS total_items
FROM mart.fact_order_items f
JOIN mart.dim_order_day d
    ON f.order_day_id = d.order_day_id
GROUP BY
    d.day_name,
    d.order_dow
ORDER BY d.order_dow;

CREATE OR REPLACE VIEW mart.v_orders_by_hour AS
SELECT
    t.order_hour_of_day,
    t.time_bucket,
    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(*) AS total_items
FROM mart.fact_order_items f
JOIN mart.dim_order_time t
    ON f.order_time_id = t.order_time_id
GROUP BY
    t.order_hour_of_day,
    t.time_bucket
ORDER BY t.order_hour_of_day;

SELECT COUNT(*) FROM mart.dim_product;
SELECT COUNT(*) FROM mart.dim_customer;
SELECT COUNT(*) FROM mart.dim_order_day;
SELECT COUNT(*) FROM mart.dim_order_time;
SELECT COUNT(*) FROM mart.fact_order_items;
SELECT COUNT(DISTINCT order_id) FROM mart.fact_order_items;

SELECT MIN(order_time_id), MAX(order_time_id) FROM mart.fact_order_items;
SELECT MIN(order_day_id), MAX(order_day_id) FROM mart.fact_order_items;