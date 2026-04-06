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