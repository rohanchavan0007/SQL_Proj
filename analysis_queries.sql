
-- Total Sales by Product Category
SELECT
    p.category,
    SUM(s.sales) AS total_sales
FROM
    sales s
JOIN
    products p ON s.product_id = p.product_id
GROUP BY
    p.category
ORDER BY
    total_sales DESC;

-- Total Sales and Profit by Region
SELECT
    o.region,
    SUM(s.sales) AS total_sales,
    SUM(s.profit) AS total_profit
FROM
    sales s
JOIN
    orders o ON s.order_id = o.order_id
GROUP BY
    o.region
ORDER BY
    total_sales DESC;

-- Monthly Sales Trend
SELECT
    DATE_FORMAT(o.order_date, '%Y-%m') AS sales_month,
    SUM(s.sales) AS monthly_sales
FROM
    sales s
JOIN
    orders o ON s.order_id = o.order_id
GROUP BY
    sales_month
ORDER BY
    sales_month;

-- Top 10 Customers by Sales
SELECT
    o.customer_name,
    SUM(s.sales) AS total_sales_by_customer
FROM
    sales s
JOIN
    orders o ON s.order_id = o.order_id
GROUP BY
    o.customer_name
ORDER BY
    total_sales_by_customer DESC
LIMIT 10;

-- Sales and Profit by Ship Mode
SELECT
    o.ship_mode,
    SUM(s.sales) AS total_sales,
    SUM(s.profit) AS total_profit
FROM
    sales s
JOIN
    orders o ON s.order_id = o.order_id
GROUP BY
    o.ship_mode
ORDER BY
    total_sales DESC;


