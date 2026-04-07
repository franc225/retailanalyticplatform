COPY mart.v_customer_summary
TO 'data/exports/customer_summary.csv'
(HEADER, DELIMITER ',');

COPY mart.v_product_summary
TO 'data/exports/product_summary.csv'
(HEADER, DELIMITER ',');

COPY mart.v_orders_by_day
TO 'data/exports/orders_by_day.csv'
(HEADER, DELIMITER ',');

COPY mart.v_orders_by_hour
TO 'data/exports/orders_by_hour.csv'
(HEADER, DELIMITER ',');

COPY mart.v_basket_size_distribution
TO 'data/exports/basket_size_distribution.csv'
(HEADER, DELIMITER ',');

COPY mart.v_department_summary
TO 'data/exports/department_summary.csv'
(HEADER, DELIMITER ',');

COPY (
    SELECT *
    FROM mart.v_association_rules
    WHERE pair_count >= 50
      AND confidence >= 0.05
      AND lift > 1
    ORDER BY lift DESC
    LIMIT 200
)
TO 'data/exports/association_rules.csv'
(HEADER, DELIMITER ',');

COPY (
    SELECT *
    FROM mart.v_association_rules_named
    WHERE pair_count >= 50
      AND confidence >= 0.05
      AND lift > 1
    ORDER BY lift DESC
    LIMIT 200
)
TO 'data/exports/association_rules.csv'
(HEADER, DELIMITER ',');

COPY (
SELECT
    total_orders
FROM mart.v_customer_metrics
)
TO 'data/exports/customer_frequency.csv'
(HEADER, DELIMITER ',');

COPY (
SELECT *
FROM mart.v_customer_reorder
)
TO 'data/exports/customer_reorder.csv'
(HEADER, DELIMITER ',');

COPY (
SELECT *
FROM mart.v_customer_segments
)
TO 'data/exports/customer_segments.csv'
(HEADER, DELIMITER ',');

COPY (
    SELECT *
    FROM mart.v_customer_metrics
)
TO 'data/exports/customer_metrics.csv'
(HEADER, DELIMITER ',');