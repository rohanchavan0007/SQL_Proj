
import pandas as pd
import mysql.connector
from mysql.connector import Error

# Database connection details
DB_CONFIG = {
    'host': 'localhost',
    'database': 'retail_sales',
    'user': 'root',
    'password': 'root'  
}

def create_db_connection(host, user, password, database=None):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            passwd=password,
            database=database
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")
    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

def load_data_to_db(df, connection):
    cursor = connection.cursor()

    # Prepare data for orders table
    orders_df = df[['Order ID', 'Order Date', 'Ship Date', 'Ship Mode', 'Customer ID', 'Customer Name', 'Segment', 'Country', 'City', 'State', 'Postal Code', 'Region']].drop_duplicates(subset=['Order ID'])
    orders_records = orders_df.values.tolist()
    orders_insert_query = """
    INSERT INTO orders (order_id, order_date, ship_date, ship_mode, customer_id, customer_name, segment, country, city, state, postal_code, region)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    order_date = VALUES(order_date),
    ship_date = VALUES(ship_date),
    ship_mode = VALUES(ship_mode),
    customer_id = VALUES(customer_id),
    customer_name = VALUES(customer_name),
    segment = VALUES(segment),
    country = VALUES(country),
    city = VALUES(city),
    state = VALUES(state),
    postal_code = VALUES(postal_code),
    region = VALUES(region);
    """

    # Prepare data for products table
    products_df = df[['Product ID', 'Category', 'Sub-Category', 'Product Name']].drop_duplicates(subset=['Product ID'])
    products_records = products_df.values.tolist()
    products_insert_query = """
    INSERT INTO products (product_id, category, sub_category, product_name)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    category = VALUES(category),
    sub_category = VALUES(sub_category),
    product_name = VALUES(product_name);
    """

    # Prepare data for sales table
    sales_df = df[['Row ID', 'Order ID', 'Product ID', 'Sales', 'Quantity', 'Discount', 'Profit']]
    sales_df['Order ID'] = sales_df['Order ID'].astype(str) # Ensure Order ID is string
    sales_df['Product ID'] = sales_df['Product ID'].astype(str) # Ensure Product ID is string
    sales_records = sales_df.values.tolist()
    sales_insert_query = """
    INSERT INTO sales (row_id, order_id, product_id, sales, quantity, discount, profit)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    order_id = VALUES(order_id),
    product_id = VALUES(product_id),
    sales = VALUES(sales),
    quantity = VALUES(quantity),
    discount = VALUES(discount),
    profit = VALUES(profit);
    """

    try:
        cursor.executemany(orders_insert_query, orders_records)
        connection.commit()
        print("Orders data loaded successfully")

        cursor.executemany(products_insert_query, products_records)
        connection.commit()
        print("Products data loaded successfully")

        cursor.executemany(sales_insert_query, sales_records)
        connection.commit()
        print("Sales data loaded successfully")

    except Error as err:
        print(f"Error loading data: '{err}'")

def main():
    # Create database and tables
    connection = create_db_connection(DB_CONFIG['host'], DB_CONFIG['user'], DB_CONFIG['password']) # Connect without specific DB to create it
    if connection:
        execute_query(connection, "CREATE DATABASE IF NOT EXISTS retail_sales;")
        connection.close()

    connection = create_db_connection(DB_CONFIG['host'], DB_CONFIG['user'], DB_CONFIG['password'], DB_CONFIG['database']) # Connect to the newly created DB
    if connection:
        with open('schema.sql', 'r') as f:
            schema_sql = f.read()
        # Split the schema_sql into individual statements and execute them
        commands = schema_sql.split(';')
        for command in commands:
            if command.strip(): # Ensure command is not empty
                execute_query(connection, command)

        # Load data from CSV
        try:
            df = pd.read_csv('Sample-Superstore.csv', encoding='latin1')
            # Convert date columns to datetime objects
            df['Order Date'] = pd.to_datetime(df['Order Date'], format='%m/%d/%Y')
            df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='%m/%d/%Y')
            load_data_to_db(df, connection)
        except FileNotFoundError:
            print("Error: Sample-Superstore.csv not found. Make sure it's in the same directory as the script.")
        except Exception as e:
            print(f"Error processing CSV or loading data: {e}")
        finally:
            connection.close()

if __name__ == "__main__":
    main()


