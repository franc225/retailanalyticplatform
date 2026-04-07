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

COPY (
    SELECT *
    FROM mart.v_department_demand_weekly
) TO 'data/exports/department_demand_timeseries.csv'
WITH (HEADER, DELIMITER ',');

COPY (
    SELECT *
    FROM mart.v_top_product_demand_weekly
) TO 'data/exports/top_product_demand_timeseries.csv'
WITH (HEADER, DELIMITER ',');

COPY mart.export_top_product_demand_weekly
TO 'data/exports/top_product_demand_timeseries.parquet'
(FORMAT PARQUET);

COPY mart.export_department_demand_weekly
TO 'data/exports/department_demand_timeseries.parquet'
(FORMAT PARQUET);

COPY (
    SELECT
        days_since_prior_order
    FROM orders
    WHERE days_since_prior_order IS NOT NULL
) TO 'data/exports/reorder_intervals.csv'
WITH (HEADER, DELIMITER ',');

COPY (
    SELECT
        user_id,
        COUNT(*) AS total_orders,
        AVG(days_since_prior_order) AS avg_reorder_days
    FROM orders
    WHERE days_since_prior_order IS NOT NULL
    GROUP BY user_id
) TO 'data/exports/customer_reorder_behavior.csv'
WITH (HEADER, DELIMITER ',');

COPY (
    SELECT
        relative_week_index,
        COUNT(DISTINCT customer_id) AS active_customers,
        COUNT(DISTINCT order_id) AS active_orders,
        COUNT(*) AS total_items
    FROM mart.fact_order_items
    WHERE relative_week_index > 0
    GROUP BY relative_week_index
    ORDER BY relative_week_index
) TO 'data/exports/customer_lifetime_curve.csv'
WITH (HEADER, DELIMITER ',');

COPY (
    WITH customer_first_week AS (
        SELECT
            customer_id,
            MIN(relative_week_index) AS cohort_week
        FROM mart.fact_order_items
        WHERE relative_week_index > 0
        GROUP BY customer_id
    ),
    customer_activity AS (
        SELECT DISTINCT
            f.customer_id,
            f.relative_week_index
        FROM mart.fact_order_items f
        WHERE f.relative_week_index > 0
    )
    SELECT
        cfw.cohort_week,
        ca.relative_week_index,
        ca.relative_week_index - cfw.cohort_week AS cohort_age,
        COUNT(DISTINCT ca.customer_id) AS active_customers
    FROM customer_first_week cfw
    JOIN customer_activity ca
        ON cfw.customer_id = ca.customer_id
       AND ca.relative_week_index >= cfw.cohort_week
    GROUP BY
        cfw.cohort_week,
        ca.relative_week_index,
        cohort_age
    ORDER BY
        cfw.cohort_week,
        ca.relative_week_index
) TO 'data/exports/customer_reorder_cohorts.csv'
WITH (HEADER, DELIMITER ',');