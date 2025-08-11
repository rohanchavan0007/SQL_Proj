# Retail Sales Insights Dashboard

A comprehensive data analytics dashboard built with Python, SQL, and Streamlit for analyzing retail sales data from a superstore dataset.

## 🚀 Project Overview

This project demonstrates a complete data pipeline and analytics solution that includes:
- **Data Extraction, Transformation, and Loading (ETL)** using Python and Pandas
- **Database Design and Management** with MySQL
- **Advanced SQL Analytics** for business insights
- **Interactive Dashboard** built with Streamlit
- **Data Visualizations** using Plotly, Matplotlib, and Seaborn

## 📊 Features

### Dashboard Pages
1. **Overview** - Key metrics and monthly sales trends
2. **Sales Analysis** - Sales by ship mode and customer segments
3. **Product Analysis** - Category performance and top sub-categories
4. **Customer Analysis** - Top customers and purchasing patterns
5. **Regional Analysis** - Geographic sales distribution

### Key Metrics Tracked
- Total Sales Revenue
- Total Profit
- Number of Orders
- Customer Count
- Monthly Sales Trends
- Regional Performance
- Product Category Analysis
- Customer Segmentation

## 🛠️ Tech Stack

- **Backend & Database**: MySQL, SQL
- **Data Processing**: Python, Pandas
- **Database Connectivity**: mysql-connector-python
- **Dashboard**: Streamlit
- **Visualizations**: Plotly, Matplotlib, Seaborn
- **Dataset**: Superstore Sales Dataset (Kaggle)

## 📁 Project Structure

```
retail_sales_dashboard/
├── Sample-Superstore.csv      # Raw dataset
├── schema.sql                 # Database schema definition
├── etl_script.py             # ETL pipeline script
├── analysis_queries.sql      # SQL queries for analytics
├── dashboard.py              # Streamlit dashboard application
└── README.md                 # Project documentation
```

## 🔧 Setup Instructions

### Prerequisites
- Python 3.7+
- MySQL Server
- Git (optional)

### Installation Steps

1. **Clone or Download the Project**
   ```bash
   # If using git
   git clone <repository-url>
   cd retail_sales_dashboard
   
   # Or download and extract the project files
   ```

2. **Install Required Python Packages**
   ```bash
   pip install pandas mysql-connector-python streamlit matplotlib seaborn plotly
   ```

3. **Setup MySQL Database**
   ```bash
   # Start MySQL service
   sudo service mysql start
   
   # Configure MySQL root user (if needed)
   sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY ''; FLUSH PRIVILEGES;"
   ```

4. **Run the ETL Pipeline**
   ```bash
   python3 etl_script.py
   ```
   This will:
   - Create the `retail_sales` database
   - Create tables (orders, products, sales)
   - Load data from the CSV file

5. **Launch the Dashboard**
   ```bash
   streamlit run dashboard.py
   ```
   The dashboard will be available at `http://localhost:8501`

## 📈 Database Schema

### Tables Structure

**orders**
- order_id (Primary Key)
- order_date, ship_date
- ship_mode, customer_id, customer_name
- segment, country, city, state, postal_code, region

**products**
- product_id (Primary Key)
- category, sub_category, product_name

**sales**
- row_id (Primary Key)
- order_id (Foreign Key), product_id (Foreign Key)
- sales, quantity, discount, profit

## 🔍 Key SQL Queries

The project includes several analytical SQL queries:

1. **Total Sales by Product Category**
2. **Sales and Profit by Region**
3. **Monthly Sales Trend Analysis**
4. **Top 10 Customers by Sales**
5. **Performance by Ship Mode**

## 📊 Dashboard Features

### Interactive Elements
- **Navigation Sidebar**: Switch between different analysis pages
- **Real-time Data**: Connects directly to MySQL database
- **Responsive Charts**: Interactive Plotly visualizations
- **Key Metrics Cards**: Quick overview of important KPIs

### Visualization Types
- Line charts for trends
- Bar charts for comparisons
- Pie charts for distributions
- Scatter plots for correlations
- Data tables for detailed views

## 🚀 Usage Guide

1. **Start the Application**: Run `streamlit run dashboard.py`
2. **Navigate Pages**: Use the sidebar to switch between analysis views
3. **Explore Data**: Interact with charts and visualizations
4. **Analyze Trends**: Review monthly sales patterns and regional performance
5. **Identify Insights**: Use the data to make business decisions

## 📝 Business Insights

The dashboard helps answer key business questions:
- Which product categories generate the most revenue?
- What are the seasonal sales patterns?
- Which regions are performing best?
- Who are the top customers?
- How do different shipping modes affect sales?

## 🔧 Customization

### Adding New Metrics
1. Create SQL queries in `analysis_queries.sql`
2. Add new functions in `dashboard.py`
3. Update the navigation menu

### Modifying Visualizations
- Edit chart configurations in `dashboard.py`
- Add new chart types using Plotly or Matplotlib
- Customize colors and styling

## 🐛 Troubleshooting

### Common Issues

**MySQL Connection Error**
```bash
# Ensure MySQL is running
sudo service mysql start

# Check MySQL status
sudo service mysql status
```

**Package Import Errors**
```bash
# Reinstall required packages
pip install --upgrade pandas mysql-connector-python streamlit plotly
```

**Data Loading Issues**
- Verify CSV file is in the correct directory
- Check file encoding (should be latin1 or utf-8)
- Ensure MySQL user has proper permissions

## 📊 Sample Data

The project uses the Superstore Sales dataset which includes:
- **9,994 rows** of sales transactions
- **21 columns** with order, customer, and product information
- **Date range**: 2014-2017
- **Geographic coverage**: United States
- **Product categories**: Office Supplies, Furniture, Technology

## 🎯 Learning Outcomes

This project demonstrates:
- **ETL Pipeline Development** with Python and Pandas
- **Database Design** and SQL query optimization
- **Data Visualization** best practices
- **Dashboard Development** with Streamlit
- **Business Intelligence** and analytics skills

## 📄 License

This project is for educational purposes. The dataset is sourced from Kaggle and all credits go to the original authors.

## 🤝 Contributing

Feel free to fork this project and submit pull requests for improvements:
- Add new visualizations
- Implement additional analytics
- Improve the UI/UX
- Add data export features

## 📞 Support

For questions or issues:
1. Check the troubleshooting section
2. Review the setup instructions
3. Ensure all dependencies are installed correctly

---

**Built with ❤️ using Python, SQL, and Streamlit**

