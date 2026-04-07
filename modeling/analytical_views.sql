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

SET preserve_insertion_order = false;
SET threads = 2;
SET temp_directory = 'C:/dev/retailanalyticplatform/.duckdb_tmp/';

CREATE OR REPLACE TABLE mart.top_products_for_basket AS
SELECT product_id
FROM mart.v_product_summary
ORDER BY times_ordered DESC
LIMIT 300;

CREATE OR REPLACE TABLE mart.filtered_order_items AS
SELECT f.order_id, f.product_id
FROM mart.fact_order_items f
JOIN mart.top_products_for_basket tp
  ON f.product_id = tp.product_id
WHERE f.basket_size >= 2;

CREATE OR REPLACE TABLE mart.product_pairs AS
SELECT
    f1.product_id AS product_1,
    f2.product_id AS product_2,
    COUNT(*) AS pair_count
FROM mart.filtered_order_items f1
JOIN mart.filtered_order_items f2
    ON f1.order_id = f2.order_id
   AND f1.product_id < f2.product_id
GROUP BY 1, 2;

CREATE OR REPLACE VIEW mart.v_product_pair_summary AS
SELECT
    p1.product_name AS product_1,
    p2.product_name AS product_2,
    pp.pair_count
FROM mart.product_pairs pp
JOIN mart.dim_product p1
  ON pp.product_1 = p1.product_id
JOIN mart.dim_product p2
  ON pp.product_2 = p2.product_id
ORDER BY pp.pair_count DESC;

CREATE OR REPLACE VIEW mart.v_association_rules AS
WITH product_counts AS (
    SELECT
        product_id,
        COUNT(DISTINCT order_id) AS product_orders
    FROM mart.filtered_order_items
    GROUP BY product_id
),
total_orders AS (
    SELECT COUNT(DISTINCT order_id) AS total_orders
    FROM mart.filtered_order_items
)
SELECT
    pp.product_1,
    pp.product_2,
    pp.pair_count,
    pc1.product_orders AS product_1_orders,
    pc2.product_orders AS product_2_orders,
    pp.pair_count * 1.0 / t.total_orders AS support,
    pp.pair_count * 1.0 / pc1.product_orders AS confidence,
    (pp.pair_count * 1.0 / pc1.product_orders) /
    (pc2.product_orders * 1.0 / t.total_orders) AS lift
FROM mart.product_pairs pp
JOIN product_counts pc1 ON pp.product_1 = pc1.product_id
JOIN product_counts pc2 ON pp.product_2 = pc2.product_id
CROSS JOIN total_orders t;

CREATE OR REPLACE VIEW mart.v_association_rules_named AS
SELECT
    ar.product_1,
    p1.product_name AS product_1_name,
    ar.product_2,
    p2.product_name AS product_2_name,
    ar.pair_count,
    ar.product_1_orders,
    ar.product_2_orders,
    ar.support,
    ar.confidence,
    ar.lift
FROM mart.v_association_rules ar
JOIN mart.dim_product p1
    ON ar.product_1 = p1.product_id
JOIN mart.dim_product p2
    ON ar.product_2 = p2.product_id;

CREATE OR REPLACE VIEW mart.v_customer_reorder AS
SELECT
    customer_id,
    total_orders,
    total_items,
    total_reordered_items,
    total_reordered_items * 1.0 / total_items AS reorder_rate
FROM mart.v_customer_metrics;

CREATE OR REPLACE VIEW mart.v_customer_segments AS
SELECT
    customer_id,
    total_orders,
    CASE
        WHEN total_orders >= 50 THEN 'Power Users'
        WHEN total_orders >= 20 THEN 'Frequent Customers'
        WHEN total_orders >= 10 THEN 'Regular Customers'
        ELSE 'Occasional Customers'
    END AS customer_segment
FROM mart.v_customer_metrics;

CREATE OR REPLACE VIEW mart.v_customer_metrics AS
WITH customer_orders AS (
    SELECT DISTINCT
        customer_id,
        order_id,
        basket_size,
        days_since_prior_order,
        order_number
    FROM mart.fact_order_items
),
customer_items AS (
    SELECT
        customer_id,
        COUNT(*) AS total_items,
        SUM(reordered) AS total_reordered_items
    FROM mart.fact_order_items
    GROUP BY customer_id
)
SELECT
    co.customer_id,
    COUNT(co.order_id) AS total_orders,
    ci.total_items,
    ci.total_reordered_items,
    ci.total_reordered_items * 1.0 / ci.total_items AS reorder_rate,
    AVG(co.basket_size) AS avg_basket_size,
    AVG(co.days_since_prior_order) AS avg_days_between_orders,
    MAX(co.order_number) AS last_order_number
FROM customer_orders co
JOIN customer_items ci
    ON co.customer_id = ci.customer_id
GROUP BY
    co.customer_id,
    ci.total_items,
    ci.total_reordered_items;

CREATE OR REPLACE VIEW mart.v_product_demand_weekly AS
SELECT
    f.relative_week_index,
    f.product_id,
    p.product_name,
    p.department,
    COUNT(DISTINCT f.order_id) AS orders_count,
    COUNT(*) AS units_sold
FROM mart.fact_order_items f
INNER JOIN mart.dim_product p
    ON f.product_id = p.product_id
GROUP BY
    f.relative_week_index,
    f.product_id,
    p.product_name,
    p.department;

CREATE OR REPLACE VIEW mart.v_top_product_demand_weekly AS
WITH ranked_products AS (
    SELECT
        product_id,
        SUM(units_sold) AS total_units_sold
    FROM mart.v_product_demand_weekly
    GROUP BY product_id
    ORDER BY total_units_sold DESC
    LIMIT 20
)
SELECT
    v.relative_week_index,
    v.product_id,
    v.product_name,
    v.department,
    v.orders_count,
    v.units_sold
FROM mart.v_product_demand_weekly v
INNER JOIN ranked_products rp
    ON v.product_id = rp.product_id;

CREATE OR REPLACE VIEW mart.v_department_demand_weekly AS
SELECT
    f.relative_week_index,
    p.department,
    COUNT(DISTINCT f.order_id) AS orders_count,
    COUNT(*) AS units_sold
FROM mart.fact_order_items f
INNER JOIN mart.dim_product p
    ON f.product_id = p.product_id
GROUP BY
    f.relative_week_index,
    p.department;

CREATE OR REPLACE VIEW mart.v_top_department_demand_weekly AS
WITH ranked_departments AS (
    SELECT
        department,
        SUM(units_sold) AS total_units_sold
    FROM mart.v_department_demand_weekly
    GROUP BY department
    ORDER BY total_units_sold DESC
    LIMIT 10
)
SELECT
    v.relative_week_index,
    v.department,
    v.orders_count,
    v.units_sold
FROM mart.v_department_demand_weekly v
INNER JOIN ranked_departments rd
    ON v.department = rd.department;

CREATE OR REPLACE TABLE mart.export_top_product_demand_weekly AS
WITH top_products AS (
    SELECT
        f.product_id
    FROM mart.fact_order_items f
    GROUP BY f.product_id
    ORDER BY COUNT(*) DESC
    LIMIT 5
),
recent_weeks AS (
    SELECT MAX(relative_week_index) AS max_week
    FROM mart.fact_order_items
)
SELECT
    f.relative_week_index,
    f.product_id,
    p.product_name,
    p.department,
    COUNT(DISTINCT f.order_id) AS orders_count,
    COUNT(*) AS units_sold
FROM mart.fact_order_items f
INNER JOIN top_products tp
    ON f.product_id = tp.product_id
INNER JOIN mart.dim_product p
    ON f.product_id = p.product_id
CROSS JOIN recent_weeks rw
WHERE f.relative_week_index >= rw.max_week - 52
GROUP BY
    f.relative_week_index,
    f.product_id,
    p.product_name,
    p.department;

CREATE OR REPLACE TABLE mart.export_department_demand_weekly AS
WITH recent_weeks AS (
    SELECT MAX(relative_week_index) AS max_week
    FROM mart.fact_order_items
)
SELECT
    f.relative_week_index,
    p.department,
    COUNT(DISTINCT f.order_id) AS orders_count,
    COUNT(*) AS units_sold
FROM mart.fact_order_items f
INNER JOIN mart.dim_product p
    ON f.product_id = p.product_id
CROSS JOIN recent_weeks rw
WHERE f.relative_week_index >= rw.max_week - 52
GROUP BY
    f.relative_week_index,
    p.department;