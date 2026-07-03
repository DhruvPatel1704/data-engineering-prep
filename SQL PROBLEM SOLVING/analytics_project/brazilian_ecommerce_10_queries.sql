-- Brazilian E-Commerce Analytics Project
-- Dataset: Olist dataset — 8 tables, 500k+ rows
-- Database: PostgreSQL via DBeaver



-- Query 1: Monthly revenue trend with month over month growth
-- Business use: track GMV growth for executive reporting

WITH monthly AS (
    SELECT DATE_TRUNC('month', o.order_purchase_timestamp) AS month,
           SUM(oi.price + oi.freight_value)                AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE order_status = 'delivered'
    GROUP BY 1
)
SELECT month,
       ROUND(revenue::NUMERIC, 2) AS revenue,
       ROUND(LAG(revenue) OVER (ORDER BY month)::NUMERIC, 2) AS prev_month,
       ROUND((revenue - LAG(revenue) OVER (ORDER BY month))
           / LAG(revenue) OVER (ORDER BY month) * 100, 2) AS mom_growth_pct
FROM monthly
ORDER BY month;


-- Query 2: Top 10 product categories by revenue with english names
-- Business use: category performance for merchandising team

SELECT pct.product_category_name_english    AS category,
       COUNT(DISTINCT oi.order_id)          AS total_orders,
       SUM(oi.price)                        AS total_revenue,
       ROUND(AVG(oi.price)::NUMERIC, 2)     AS avg_price
FROM order_items oi
INNER JOIN products p ON oi.product_id = p.product_id
INNER JOIN product_category_translation pct
        ON p.product_category_name = pct.product_category_name
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 10;


-- Query 3: Average delivery time by state
-- Business use: SLA compliance monitoring for logistics team

SELECT c.customer_state,
       ROUND(AVG(
           EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_purchase_timestamp)) / 86400
       )::NUMERIC, 1) AS avg_delivery_days,
       COUNT(*)        AS total_orders
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL
GROUP BY c.customer_state
ORDER BY avg_delivery_days DESC;


-- Query 4: Payment method breakdown with revenue share
-- Business use: finance team monitoring payment mix and installment trends

SELECT payment_type                                              AS transactions,
       ROUND(SUM(payment_value)::NUMERIC, 2)                    AS total_value,
       ROUND(AVG(payment_installments)::NUMERIC, 1)             AS avg_installments,
       ROUND(SUM(payment_value) * 100
           / SUM(SUM(payment_value)) OVER ()::NUMERIC, 2)       AS revenue_share_pct
FROM order_payments
GROUP BY payment_type
ORDER BY total_value DESC;


-- Query 5: Review score distribution per product category
-- Business use: product quality monitoring, flag categories with poor ratings

SELECT t.product_category_name_english                              AS category,
       COUNT(r.review_id)                                           AS total_reviews,
       ROUND(AVG(r.review_score)::NUMERIC, 2)                       AS avg_score,
       COUNT(r.review_id) FILTER (WHERE r.review_score >= 4)        AS positive,
       COUNT(r.review_id) FILTER (WHERE r.review_score <= 2)        AS negative,
       ROUND(COUNT(r.review_id) FILTER (WHERE r.review_score <= 2)
           * 100.0 / COUNT(r.review_id), 2)                         AS negative_rate_pct
FROM order_reviews r
INNER JOIN orders o             ON r.order_id = o.order_id
INNER JOIN order_items oi       ON o.order_id = oi.order_id
INNER JOIN products p           ON oi.product_id = p.product_id
INNER JOIN product_category_translation t
                                ON p.product_category_name = t.product_category_name
GROUP BY t.product_category_name_english
HAVING COUNT(r.review_id) > 100
ORDER BY negative_rate_pct DESC
LIMIT 15;


-- Query 6: Top 3 sellers per state ranked by revenue
-- Business use: identify top sellers per region for partnership decisions

WITH seller_metrics AS (
    SELECT s.seller_id,
           s.seller_state,
           COUNT(DISTINCT oi.order_id)      AS total_orders,
           ROUND(SUM(oi.price)::NUMERIC, 2) AS revenue
    FROM order_items oi
    INNER JOIN sellers s ON oi.seller_id = s.seller_id
    GROUP BY s.seller_id, s.seller_state
),
ranked AS (
    SELECT seller_state,
           seller_id,
           total_orders,
           revenue,
           RANK() OVER (
               PARTITION BY seller_state
               ORDER BY revenue DESC
           ) AS seller_rank
    FROM seller_metrics
)
SELECT *
FROM ranked
WHERE seller_rank <= 3
ORDER BY seller_state, seller_rank;


-- Query 7: Orders with no payment record
-- Business use: data quality check — catch orphaned records in pipeline

SELECT o.order_id
FROM orders o
LEFT JOIN order_payments op ON o.order_id = op.order_id
WHERE op.order_id IS NULL;


-- Query 8: Repeat customer analysis
-- Business use: retention team tracking customer purchase frequency
-- Finding: only 3.12% of customers ever placed a second order

WITH customer_orders AS (
    SELECT c.customer_unique_id,
           COUNT(o.order_id) AS total_orders
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_unique_id
)
SELECT COUNT(*)                                                    AS total_customers,
       COUNT(*) FILTER (WHERE total_orders > 1)                    AS repeat_customers,
       ROUND(COUNT(*) FILTER (WHERE total_orders > 1)
           * 100.0 / COUNT(*), 2)                                  AS repeat_rate_pct
FROM customer_orders;


-- Query 9: Late delivery analysis by state
-- Business use: logistics SLA monitoring, identify problem regions

SELECT c.customer_state,
       CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date
            THEN 'Late'
            ELSE 'On time'
       END                  AS delivery_status,
       COUNT(*)              AS total_orders
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
GROUP BY c.customer_state, delivery_status
ORDER BY c.customer_state;


-- Query 10: Revenue by seller state and city using ROLLUP
-- Business use: regional revenue report with state subtotals and grand total
-- ROLLUP generates: (state, city), (state), () automatically

SELECT COALESCE(s.seller_state, 'ALL STATES') AS state,
       COALESCE(s.seller_city,  'ALL CITIES')  AS city,
       COUNT(DISTINCT oi.order_id)              AS total_orders,
       ROUND(SUM(oi.price)::NUMERIC, 2)         AS revenue
FROM order_items oi
INNER JOIN sellers s ON oi.seller_id = s.seller_id
GROUP BY ROLLUP(s.seller_state, s.seller_city)
ORDER BY state, city;