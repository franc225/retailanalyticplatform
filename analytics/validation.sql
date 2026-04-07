SELECT COUNT(*) FROM mart.dim_product;
SELECT COUNT(*) FROM mart.dim_customer;
SELECT COUNT(*) FROM mart.dim_order_day;
SELECT COUNT(*) FROM mart.dim_order_time;
SELECT COUNT(*) FROM mart.fact_order_items;
SELECT COUNT(DISTINCT order_id) FROM mart.fact_order_items;

SELECT MIN(order_time_id), MAX(order_time_id) FROM mart.fact_order_items;
SELECT MIN(order_day_id), MAX(order_day_id) FROM mart.fact_order_items;

SELECT COUNT(*) FROM mart.v_customer_summary;
SELECT COUNT(*) FROM mart.v_product_summary;
SELECT COUNT(*) FROM mart.v_orders_by_day;
SELECT COUNT(*) FROM mart.v_orders_by_hour;

SELECT * FROM mart.v_orders_by_day;
SELECT * FROM mart.v_orders_by_hour LIMIT 24;

SELECT *
FROM mart.orders_enriched
ORDER BY customer_id, order_number
LIMIT 20;

SELECT
    COUNT(*) AS total_rows,
    SUM(CASE WHEN relative_day_index IS NULL THEN 1 ELSE 0 END) AS null_relative_day,
    SUM(CASE WHEN relative_week_index IS NULL THEN 1 ELSE 0 END) AS null_relative_week
FROM mart.orders_enriched;

SELECT COUNT(*) AS null_weeks
FROM mart.fact_order_items
WHERE relative_week_index IS NULL;

SELECT *
FROM mart.v_product_demand_weekly
WHERE units_sold < orders_count
LIMIT 20;

SELECT
    product_id,
    product_name,
    COUNT(DISTINCT relative_week_index) AS active_weeks
FROM mart.v_product_demand_weekly
GROUP BY product_id, product_name
ORDER BY active_weeks DESC;

SELECT COUNT(*) FROM mart.v_department_demand_weekly;

SELECT *
FROM mart.v_department_demand_weekly
WHERE units_sold < orders_count
LIMIT 20;

SELECT
    department,
    COUNT(DISTINCT relative_week_index) AS active_weeks
FROM mart.v_department_demand_weekly
GROUP BY department
ORDER BY active_weeks DESC;

SELECT
    MIN(relative_week_index) AS min_week,
    MAX(relative_week_index) AS max_week,
    COUNT(DISTINCT relative_week_index) AS total_weeks
FROM mart.fact_order_items;

SELECT
    MIN(relative_day_index) AS min_day,
    MAX(relative_day_index) AS max_day
FROM mart.fact_order_items;