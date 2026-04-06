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