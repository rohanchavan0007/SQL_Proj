
CREATE DATABASE IF NOT EXISTS retail_sales;
USE retail_sales;

CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(255) PRIMARY KEY,
    order_date DATE,
    ship_date DATE,
    ship_mode VARCHAR(255),
    customer_id VARCHAR(255),
    customer_name VARCHAR(255),
    segment VARCHAR(255),
    country VARCHAR(255),
    city VARCHAR(255),
    state VARCHAR(255),
    postal_code VARCHAR(255),
    region VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(255) PRIMARY KEY,
    category VARCHAR(255),
    sub_category VARCHAR(255),
    product_name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS sales (
    row_id INT PRIMARY KEY,
    order_id VARCHAR(255),
    product_id VARCHAR(255),
    sales DECIMAL(10, 2),
    quantity INT,
    discount DECIMAL(10, 2),
    profit DECIMAL(10, 2),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);


