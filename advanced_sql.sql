
-- Advanced SQL Features for Retail Sales Dashboard

-- 1. View: sales_by_category_view
-- Provides total sales and profit for each product category.
CREATE OR REPLACE VIEW sales_by_category_view AS
SELECT
    p.category,
    SUM(s.sales) AS total_sales,
    SUM(s.profit) AS total_profit
FROM
    sales s
JOIN
    products p ON s.product_id = p.product_id
GROUP BY
    p.category
ORDER BY
    total_sales DESC;

-- 2. View: monthly_sales_profit_view
-- Provides monthly sales and profit trends.
CREATE OR REPLACE VIEW monthly_sales_profit_view AS
SELECT
    DATE_FORMAT(o.order_date, 
    '%Y-%m') AS sales_month,
    SUM(s.sales) AS monthly_sales,
    SUM(s.profit) AS monthly_profit
FROM
    sales s
JOIN
    orders o ON s.order_id = o.order_id
GROUP BY
    sales_month
ORDER BY
    sales_month;

-- 3. Stored Procedure: GetTopNProductsBySales
-- Returns the top N products based on total sales.
DELIMITER //
CREATE PROCEDURE GetTopNProductsBySales(IN n INT)
BEGIN
    SELECT
        p.product_name,
        SUM(s.sales) AS total_sales
    FROM
        sales s
    JOIN
        products p ON s.product_id = p.product_id
    GROUP BY
        p.product_name
    ORDER BY
        total_sales DESC
    LIMIT n;
END //
DELIMITER ;

-- 4. Stored Procedure: GetSalesByRegionAndDateRange
-- Returns sales and profit for a specific region within a date range.
DELIMITER //
CREATE PROCEDURE GetSalesByRegionAndDateRange(
    IN region_name VARCHAR(255),
    IN start_date DATE,
    IN end_date DATE
)
BEGIN
    SELECT
        o.city,
        SUM(s.sales) AS total_sales,
        SUM(s.profit) AS total_profit
    FROM
        sales s
    JOIN
        orders o ON s.order_id = o.order_id
    WHERE
        o.region = region_name AND o.order_date BETWEEN start_date AND end_date
    GROUP BY
        o.city
    ORDER BY
        total_sales DESC;
END //
DELIMITER ;

-- 5. Complex Query: Customer Lifetime Value (CLV) using CTEs and Window Functions
-- Calculates CLV for each customer based on their total sales and order count.
WITH CustomerSales AS (
    SELECT
        o.customer_id,
        o.customer_name,
        SUM(s.sales) AS total_sales,
        COUNT(DISTINCT s.order_id) AS total_orders
    FROM
        sales s
    JOIN
        orders o ON s.order_id = o.order_id
    GROUP BY
        o.customer_id, o.customer_name
),
RankedCustomers AS (
    SELECT
        customer_id,
        customer_name,
        total_sales,
        total_orders,
        ROW_NUMBER() OVER (ORDER BY total_sales DESC) as sales_rank
    FROM
        CustomerSales
)
SELECT
    customer_id,
    customer_name,
    total_sales,
    total_orders,
    sales_rank,
    (total_sales / total_orders) AS average_order_value, -- Simple CLV proxy
    (total_sales * 0.1) AS estimated_clv -- Example: 10% of total sales as CLV
FROM
    RankedCustomers
ORDER BY
    estimated_clv DESC;

-- 6. Materialized View (simulated using a regular table and insert/update logic)
-- For performance, we can create a summary table that is periodically updated.
-- This is a common pattern when true materialized views are not directly supported or desired.
CREATE TABLE IF NOT EXISTS daily_sales_summary (
    summary_date DATE PRIMARY KEY,
    total_daily_sales DECIMAL(10, 2),
    total_daily_profit DECIMAL(10, 2)
);

-- Example of how to populate/update this summary table (this would typically be part of an ETL job)
-- INSERT INTO daily_sales_summary (summary_date, total_daily_sales, total_daily_profit)
-- SELECT
--     o.order_date,
--     SUM(s.sales),
--     SUM(s.profit)
-- FROM
--     sales s
-- JOIN
--     orders o ON s.order_id = o.order_id
-- GROUP BY
--     o.order_date
-- ON DUPLICATE KEY UPDATE
--     total_daily_sales = VALUES(total_daily_sales),
--     total_daily_profit = VALUES(total_daily_profit);

-- 7. Trigger: after_sales_insert_update
-- Updates product stock or logs changes (example: simple log table)
CREATE TABLE IF NOT EXISTS sales_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    action_type VARCHAR(50),
    order_id VARCHAR(255),
    product_id VARCHAR(255),
    old_quantity INT,
    new_quantity INT,
    log_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DELIMITER //
CREATE TRIGGER after_sales_insert_update
AFTER INSERT ON sales
FOR EACH ROW
BEGIN
    INSERT INTO sales_log (action_type, order_id, product_id, new_quantity)
    VALUES (
        'INSERT',
        NEW.order_id,
        NEW.product_id,
        NEW.quantity
    );
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER after_sales_update
AFTER UPDATE ON sales
FOR EACH ROW
BEGIN
    IF OLD.quantity <> NEW.quantity THEN
        INSERT INTO sales_log (action_type, order_id, product_id, old_quantity, new_quantity)
        VALUES (
            'UPDATE',
            NEW.order_id,
            NEW.product_id,
            OLD.quantity,
            NEW.quantity
        );
    END IF;
END //
DELIMITER ;


