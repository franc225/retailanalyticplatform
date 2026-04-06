CREATE OR REPLACE VIEW mart.v_customer_summary AS
WITH customer_orders AS (
    SELECT DISTINCT
        customer_id,
        order_id,
        basket_size,
        days_since_prior_order
    FROM mart.fact_order_items
),
customer_reorders AS (
    SELECT
        customer_id,
        SUM(reordered) AS total_reordered_items
    FROM mart.fact_order_items
    GROUP BY customer_id
)
SELECT
    co.customer_id,
    COUNT(co.order_id) AS total_orders,
    AVG(co.basket_size) AS avg_basket_size,
    AVG(co.days_since_prior_order) AS avg_days_between_orders,
    cr.total_reordered_items
FROM customer_orders co
JOIN customer_reorders cr
    ON co.customer_id = cr.customer_id
GROUP BY
    co.customer_id,
    cr.total_reordered_items;

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

CREATE OR REPLACE VIEW mart.v_basket_size_distribution AS
SELECT
    basket_size,
    COUNT(DISTINCT order_id) AS total_orders
FROM mart.fact_order_items
GROUP BY basket_size
ORDER BY basket_size;

CREATE OR REPLACE VIEW mart.v_department_summary AS
SELECT
    p.department,
    COUNT(*) AS total_items_ordered,
    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(DISTINCT f.customer_id) AS total_customers,
    SUM(f.reordered) AS total_reordered_items
FROM mart.fact_order_items f
JOIN mart.dim_product p
    ON f.product_id = p.product_id
GROUP BY p.department
ORDER BY total_items_ordered DESC;