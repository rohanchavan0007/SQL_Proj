import streamlit as st
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time

# Database connection details
DB_CONFIG = {
    'host': 'localhost',
    'database': 'retail_sales',
    'user': 'root',
    'password': 'root'
}

@st.cache_data
def get_data_from_db(query):
    """Execute SQL query and return DataFrame"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        df = pd.read_sql(query, connection)
        connection.close()
        return df
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return pd.DataFrame()

def execute_custom_query(query):
    """Execute custom SQL query and return results"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        start_time = time.time()
        cursor.execute(query)
        execution_time = time.time() - start_time
        
        if query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(results, columns=columns)
            connection.close()
            return df, execution_time, None
        else:
            connection.commit()
            affected_rows = cursor.rowcount
            connection.close()
            return None, execution_time, f"Query executed successfully. {affected_rows} rows affected."
    except Exception as e:
        return None, 0, f"Error: {str(e)}"

def main():
    st.set_page_config(
        page_title="Advanced Retail Sales Dashboard",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🚀 Advanced Retail Sales Insights Dashboard")
    st.markdown("---")

    # Sidebar
    st.sidebar.title("🧭 Navigation")
    page = st.sidebar.selectbox("Choose a page", [
        "📊 Overview", 
        "💰 Sales Analysis", 
        "📦 Product Analysis", 
        "👤 Customer Analysis", 
        "🌍 Regional Analysis",
        "🔍 SQL Query Editor",
        "📈 Advanced Analytics",
        "⚡ Performance Monitor"
    ])

    if page == "📊 Overview":
        show_overview()
    elif page == "💰 Sales Analysis":
        show_sales_analysis()
    elif page == "📦 Product Analysis":
        show_product_analysis()
    elif page == "👤 Customer Analysis":
        show_customer_analysis()
    elif page == "🌍 Regional Analysis":
        show_regional_analysis()
    elif page == "🔍 SQL Query Editor":
        show_sql_editor()
    elif page == "📈 Advanced Analytics":
        show_advanced_analytics()
    elif page == "⚡ Performance Monitor":
        show_performance_monitor()

def show_overview():
    st.header("📈 Sales Overview")
    
    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime(2014, 1, 1))
    with col2:
        end_date = st.date_input("End Date", value=datetime(2017, 12, 31))
    
    # Key metrics with date filter
    col1, col2, col3, col4 = st.columns(4)
    
    # Total Sales with date filter
    total_sales_query = f"""
    SELECT SUM(s.sales) as total_sales 
    FROM sales s 
    JOIN orders o ON s.order_id = o.order_id 
    WHERE o.order_date BETWEEN '{start_date}' AND '{end_date}'
    """
    total_sales_df = get_data_from_db(total_sales_query)
    if not total_sales_df.empty:
        total_sales = total_sales_df['total_sales'].iloc[0] or 0
        col1.metric("Total Sales", f"${total_sales:,.2f}")
    
    # Total Profit with date filter
    total_profit_query = f"""
    SELECT SUM(s.profit) as total_profit 
    FROM sales s 
    JOIN orders o ON s.order_id = o.order_id 
    WHERE o.order_date BETWEEN '{start_date}' AND '{end_date}'
    """
    total_profit_df = get_data_from_db(total_profit_query)
    if not total_profit_df.empty:
        total_profit = total_profit_df['total_profit'].iloc[0] or 0
        col2.metric("Total Profit", f"${total_profit:,.2f}")
    
    # Total Orders with date filter
    total_orders_query = f"""
    SELECT COUNT(DISTINCT s.order_id) as total_orders 
    FROM sales s 
    JOIN orders o ON s.order_id = o.order_id 
    WHERE o.order_date BETWEEN '{start_date}' AND '{end_date}'
    """
    total_orders_df = get_data_from_db(total_orders_query)
    if not total_orders_df.empty:
        total_orders = total_orders_df['total_orders'].iloc[0] or 0
        col3.metric("Total Orders", f"{total_orders:,}")
    
    # Average Order Value
    if total_orders > 0 and total_sales > 0:
        avg_order_value = total_sales / total_orders
        col4.metric("Avg Order Value", f"${avg_order_value:,.2f}")

    st.markdown("---")

    # Monthly Sales Trend using view
    st.subheader("📅 Monthly Sales & Profit Trend")
    monthly_trend_df = get_data_from_db("SELECT * FROM monthly_sales_profit_view")
    
    if not monthly_trend_df.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly_trend_df['sales_month'], 
            y=monthly_trend_df['monthly_sales'],
            mode='lines+markers',
            name='Sales',
            line=dict(color='blue', width=3)
        ))
        fig.add_trace(go.Scatter(
            x=monthly_trend_df['sales_month'], 
            y=monthly_trend_df['monthly_profit'],
            mode='lines+markers',
            name='Profit',
            line=dict(color='green', width=3),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Monthly Sales and Profit Trend',
            xaxis_title='Month',
            yaxis=dict(title='Sales ($)', side='left'),
            yaxis2=dict(title='Profit ($)', side='right', overlaying='y'),
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

def show_sql_editor():
    st.header("🔍 SQL Query Editor")
    st.markdown("Execute custom SQL queries against the retail sales database.")
    
    # Query templates
    st.subheader("📋 Query Templates")
    template_options = {
        "Custom Query": "",
        "Sales by Category (View)": "SELECT * FROM sales_by_category_view;",
        "Monthly Trends (View)": "SELECT * FROM monthly_sales_profit_view;",
        "Top 10 Products (Stored Procedure)": "CALL GetTopNProductsBySales(10);",
        "Customer Lifetime Value (CTE)": """
WITH CustomerSales AS (
    SELECT
        o.customer_id,
        o.customer_name,
        SUM(s.sales) AS total_sales,
        COUNT(DISTINCT s.order_id) AS total_orders
    FROM sales s
    JOIN orders o ON s.order_id = o.order_id
    GROUP BY o.customer_id, o.customer_name
)
SELECT 
    customer_name,
    total_sales,
    total_orders,
    (total_sales / total_orders) AS avg_order_value
FROM CustomerSales
ORDER BY total_sales DESC
LIMIT 20;
        """,
        "Sales Performance by Region": """
SELECT 
    o.region,
    COUNT(DISTINCT o.customer_id) as customers,
    COUNT(DISTINCT s.order_id) as orders,
    SUM(s.sales) as total_sales,
    SUM(s.profit) as total_profit,
    AVG(s.sales) as avg_sale_amount
FROM sales s
JOIN orders o ON s.order_id = o.order_id
GROUP BY o.region
ORDER BY total_sales DESC;
        """
    }
    
    selected_template = st.selectbox("Select a template:", list(template_options.keys()))
    
    # Query input
    query = st.text_area(
        "SQL Query:", 
        value=template_options[selected_template],
        height=200,
        help="Enter your SQL query here. Use SELECT statements to retrieve data."
    )
    
    col1, col2, col3 = st.columns([1, 1, 4])
    
    with col1:
        execute_button = st.button("▶️ Execute Query", type="primary")
    
    with col2:
        if st.button("📋 Save Query"):
            if 'saved_queries' not in st.session_state:
                st.session_state.saved_queries = []
            st.session_state.saved_queries.append({
                'query': query,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.success("Query saved!")
    
    if execute_button and query.strip():
        with st.spinner("Executing query..."):
            result_df, execution_time, error_msg = execute_custom_query(query)
            
            if error_msg:
                st.error(error_msg)
            elif result_df is not None:
                st.success(f"Query executed successfully in {execution_time:.3f} seconds")
                
                # Display results
                st.subheader("📊 Query Results")
                st.dataframe(result_df, use_container_width=True)
                
                # Download option
                csv = result_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                # Basic visualization if numeric columns exist
                numeric_cols = result_df.select_dtypes(include=['number']).columns.tolist()
                if len(numeric_cols) > 0:
                    st.subheader("📈 Quick Visualization")
                    chart_type = st.selectbox("Chart Type:", ["Bar Chart", "Line Chart", "Scatter Plot"])
                    
                    if len(result_df.columns) >= 2:
                        x_col = st.selectbox("X-axis:", result_df.columns.tolist())
                        y_col = st.selectbox("Y-axis:", numeric_cols)
                        
                        if chart_type == "Bar Chart":
                            fig = px.bar(result_df.head(20), x=x_col, y=y_col)
                        elif chart_type == "Line Chart":
                            fig = px.line(result_df, x=x_col, y=y_col)
                        else:
                            fig = px.scatter(result_df, x=x_col, y=y_col)
                        
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.success(f"Query executed successfully in {execution_time:.3f} seconds")
    
    # Query History
    if 'saved_queries' in st.session_state and st.session_state.saved_queries:
        st.subheader("📚 Saved Queries")
        for i, saved_query in enumerate(st.session_state.saved_queries):
            with st.expander(f"Query {i+1} - {saved_query['timestamp']}"):
                st.code(saved_query['query'], language='sql')
                if st.button(f"Load Query {i+1}", key=f"load_{i}"):
                    st.rerun()

def show_advanced_analytics():
    st.header("📈 Advanced Analytics")
    
    # Customer Lifetime Value Analysis
    st.subheader("💎 Customer Lifetime Value Analysis")
    
    clv_query = """
    WITH CustomerSales AS (
        SELECT
            o.customer_id,
            o.customer_name,
            SUM(s.sales) AS total_sales,
            COUNT(DISTINCT s.order_id) AS total_orders,
            MIN(o.order_date) AS first_order,
            MAX(o.order_date) AS last_order
        FROM sales s
        JOIN orders o ON s.order_id = o.order_id
        GROUP BY o.customer_id, o.customer_name
    ),
    RankedCustomers AS (
        SELECT
            customer_id,
            customer_name,
            total_sales,
            total_orders,
            first_order,
            last_order,
            DATEDIFF(last_order, first_order) AS customer_lifespan_days,
            ROW_NUMBER() OVER (ORDER BY total_sales DESC) as sales_rank
        FROM CustomerSales
    )
    SELECT
        customer_name,
        total_sales,
        total_orders,
        sales_rank,
        customer_lifespan_days,
        (total_sales / total_orders) AS average_order_value,
        CASE 
            WHEN customer_lifespan_days > 0 
            THEN (total_sales / customer_lifespan_days) * 365 
            ELSE total_sales 
        END AS estimated_annual_value
    FROM RankedCustomers
    ORDER BY estimated_annual_value DESC
    LIMIT 20;
    """
    
    clv_df = get_data_from_db(clv_query)
    if not clv_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.scatter(
                clv_df, 
                x='average_order_value', 
                y='estimated_annual_value',
                size='total_orders',
                hover_name='customer_name',
                title='Customer Value Analysis'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.dataframe(clv_df[['customer_name', 'total_sales', 'estimated_annual_value']], use_container_width=True)
    
    # Cohort Analysis
    st.subheader("👥 Customer Cohort Analysis")
    
    cohort_query = """
    WITH CustomerCohorts AS (
        SELECT 
            o.customer_id,
            DATE_FORMAT(MIN(o.order_date), '%Y-%m') AS cohort_month,
            DATE_FORMAT(o.order_date, '%Y-%m') AS order_month
        FROM orders o
        GROUP BY o.customer_id, DATE_FORMAT(o.order_date, '%Y-%m')
    ),
    CohortSizes AS (
        SELECT 
            cohort_month,
            COUNT(DISTINCT customer_id) AS cohort_size
        FROM CustomerCohorts
        GROUP BY cohort_month
    )
    SELECT 
        cc.cohort_month,
        cc.order_month,
        COUNT(DISTINCT cc.customer_id) AS customers,
        cs.cohort_size,
        ROUND(COUNT(DISTINCT cc.customer_id) * 100.0 / cs.cohort_size, 2) AS retention_rate
    FROM CustomerCohorts cc
    JOIN CohortSizes cs ON cc.cohort_month = cs.cohort_month
    GROUP BY cc.cohort_month, cc.order_month, cs.cohort_size
    ORDER BY cc.cohort_month, cc.order_month;
    """
    
    cohort_df = get_data_from_db(cohort_query)
    if not cohort_df.empty:
        # Create cohort heatmap
        cohort_pivot = cohort_df.pivot(index='cohort_month', columns='order_month', values='retention_rate')
        
        fig = px.imshow(
            cohort_pivot.values,
            x=cohort_pivot.columns,
            y=cohort_pivot.index,
            title='Customer Retention Heatmap (%)',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)

def show_performance_monitor():
    st.header("⚡ Performance Monitor")
    
    # Database statistics
    st.subheader("📊 Database Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    # Table sizes
    table_stats_query = """
    SELECT 
        table_name,
        table_rows,
        ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
    FROM information_schema.tables 
    WHERE table_schema = 'retail_sales'
    ORDER BY size_mb DESC;
    """
    
    table_stats_df = get_data_from_db(table_stats_query)
    if not table_stats_df.empty:
        with col1:
            st.metric("Total Tables", len(table_stats_df))
        with col2:
            total_rows = table_stats_df['table_rows'].sum()
            st.metric("Total Rows", f"{total_rows:,}")
        with col3:
            total_size = table_stats_df['size_mb'].sum()
            st.metric("Total Size", f"{total_size:.2f} MB")
        
        st.subheader("📋 Table Statistics")
        st.dataframe(table_stats_df, use_container_width=True)
    
    # Query performance testing
    st.subheader("🏃‍♂️ Query Performance Testing")
    
    performance_queries = {
        "Simple Aggregation": "SELECT COUNT(*) FROM sales;",
        "Join Query": "SELECT COUNT(*) FROM sales s JOIN orders o ON s.order_id = o.order_id;",
        "Complex Aggregation": "SELECT region, SUM(sales) FROM sales s JOIN orders o ON s.order_id = o.order_id GROUP BY region;",
        "View Query": "SELECT COUNT(*) FROM sales_by_category_view;",
        "Stored Procedure": "CALL GetTopNProductsBySales(5);"
    }
    
    if st.button("🚀 Run Performance Tests"):
        results = []
        
        for query_name, query in performance_queries.items():
            with st.spinner(f"Testing {query_name}..."):
                _, execution_time, error = execute_custom_query(query)
                results.append({
                    'Query Type': query_name,
                    'Execution Time (s)': f"{execution_time:.4f}",
                    'Status': 'Success' if not error else 'Error'
                })
        
        results_df = pd.DataFrame(results)
        st.dataframe(results_df, use_container_width=True)
        
        # Performance chart
        if not results_df.empty:
            results_df['Execution Time (numeric)'] = results_df['Execution Time (s)'].astype(float)
            fig = px.bar(
                results_df, 
                x='Query Type', 
                y='Execution Time (numeric)',
                title='Query Performance Comparison'
            )
            st.plotly_chart(fig, use_container_width=True)

def show_sales_analysis():
    st.header("💰 Sales Analysis")
    
    # Use views for better performance
    st.subheader("📊 Sales by Category (Using SQL View)")
    category_df = get_data_from_db("SELECT * FROM sales_by_category_view")
    
    if not category_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(category_df, x='category', y='total_sales',
                        title='Sales by Category',
                        labels={'category': 'Category', 'total_sales': 'Total Sales ($)'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.pie(category_df, values='total_sales', names='category',
                        title='Sales Distribution by Category')
            st.plotly_chart(fig, use_container_width=True)

    # Advanced filtering
    st.subheader("🔍 Advanced Sales Filtering")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_region = st.selectbox("Select Region:", ["All"] + list(get_data_from_db("SELECT DISTINCT region FROM orders")['region']))
    with col2:
        selected_category = st.selectbox("Select Category:", ["All"] + list(get_data_from_db("SELECT DISTINCT category FROM products")['category']))
    with col3:
        min_sales = st.number_input("Minimum Sales Amount:", min_value=0.0, value=0.0)
    
    # Build dynamic query based on filters
    where_conditions = []
    if selected_region != "All":
        where_conditions.append(f"o.region = '{selected_region}'")
    if selected_category != "All":
        where_conditions.append(f"p.category = '{selected_category}'")
    if min_sales > 0:
        where_conditions.append(f"s.sales >= {min_sales}")
    
    where_clause = " AND " + " AND ".join(where_conditions) if where_conditions else ""
    
    filtered_query = f"""
    SELECT 
        o.region,
        p.category,
        SUM(s.sales) as total_sales,
        SUM(s.profit) as total_profit,
        COUNT(*) as transaction_count
    FROM sales s
    JOIN orders o ON s.order_id = o.order_id
    JOIN products p ON s.product_id = p.product_id
    WHERE 1=1 {where_clause}
    GROUP BY o.region, p.category
    ORDER BY total_sales DESC
    """
    
    filtered_df = get_data_from_db(filtered_query)
    if not filtered_df.empty:
        st.subheader("📈 Filtered Results")
        st.dataframe(filtered_df, use_container_width=True)
        
        if len(filtered_df) > 0:
            fig = px.treemap(
                filtered_df, 
                path=['region', 'category'], 
                values='total_sales',
                title='Sales Treemap by Region and Category'
            )
            st.plotly_chart(fig, use_container_width=True)

def show_product_analysis():
    st.header("📦 Product Analysis")
    
    # Top products using stored procedure
    st.subheader("🏆 Top Products (Using Stored Procedure)")
    
    n_products = st.slider("Number of top products:", min_value=5, max_value=50, value=10)
    
    if st.button("🔍 Get Top Products"):
        top_products_df = get_data_from_db(f"CALL GetTopNProductsBySales({n_products})")
        if not top_products_df.empty:
            fig = px.bar(
                top_products_df, 
                x='total_sales', 
                y='product_name',
                orientation='h',
                title=f'Top {n_products} Products by Sales'
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(top_products_df, use_container_width=True)

def show_customer_analysis():
    st.header("👤 Customer Analysis")
    
    # Customer segmentation using advanced SQL
    st.subheader("🎯 Customer Segmentation")
    
    segmentation_query = """
    WITH CustomerMetrics AS (
        SELECT 
            o.customer_id,
            o.customer_name,
            COUNT(DISTINCT s.order_id) as order_frequency,
            SUM(s.sales) as total_sales,
            AVG(s.sales) as avg_order_value,
            DATEDIFF(CURDATE(), MAX(o.order_date)) as days_since_last_order
        FROM sales s
        JOIN orders o ON s.order_id = o.order_id
        GROUP BY o.customer_id, o.customer_name
    )
    SELECT 
        customer_name,
        order_frequency,
        total_sales,
        avg_order_value,
        days_since_last_order,
        CASE 
            WHEN order_frequency >= 10 AND total_sales >= 1000 THEN 'VIP'
            WHEN order_frequency >= 5 AND total_sales >= 500 THEN 'Loyal'
            WHEN order_frequency >= 2 AND total_sales >= 200 THEN 'Regular'
            ELSE 'New'
        END as customer_segment
    FROM CustomerMetrics
    ORDER BY total_sales DESC
    LIMIT 100;
    """
    
    segmentation_df = get_data_from_db(segmentation_query)
    if not segmentation_df.empty:
        # Customer segment distribution
        segment_counts = segmentation_df['customer_segment'].value_counts()
        
        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(values=segment_counts.values, names=segment_counts.index,
                        title='Customer Segment Distribution')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.scatter(
                segmentation_df, 
                x='order_frequency', 
                y='total_sales',
                color='customer_segment',
                hover_name='customer_name',
                title='Customer Segmentation Analysis'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(segmentation_df, use_container_width=True)

def show_regional_analysis():
    st.header("🌍 Regional Analysis")
    
    # Regional performance with stored procedure
    st.subheader("🗺️ Regional Performance Analysis")
    
    region_analysis_query = """
    SELECT 
        o.region,
        o.state,
        COUNT(DISTINCT o.customer_id) as unique_customers,
        COUNT(DISTINCT s.order_id) as total_orders,
        SUM(s.sales) as total_sales,
        SUM(s.profit) as total_profit,
        AVG(s.sales) as avg_order_value,
        SUM(s.profit) / SUM(s.sales) * 100 as profit_margin_pct
    FROM sales s
    JOIN orders o ON s.order_id = o.order_id
    GROUP BY o.region, o.state
    ORDER BY total_sales DESC;
    """
    
    regional_df = get_data_from_db(region_analysis_query)
    if not regional_df.empty:
        # Regional performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_regions = regional_df['region'].nunique()
            st.metric("Total Regions", total_regions)
        
        with col2:
            total_states = regional_df['state'].nunique()
            st.metric("Total States", total_states)
        
        with col3:
            avg_profit_margin = regional_df['profit_margin_pct'].mean()
            st.metric("Avg Profit Margin", f"{avg_profit_margin:.1f}%")
        
        with col4:
            top_region = regional_df.groupby('region')['total_sales'].sum().idxmax()
            st.metric("Top Region", top_region)
        
        # Regional visualizations
        region_summary = regional_df.groupby('region').agg({
            'total_sales': 'sum',
            'total_profit': 'sum',
            'unique_customers': 'sum',
            'total_orders': 'sum'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(region_summary, x='region', y='total_sales',
                        title='Total Sales by Region')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.scatter(region_summary, x='total_sales', y='total_profit',
                           size='unique_customers', hover_name='region',
                           title='Sales vs Profit by Region')
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📊 Detailed Regional Data")
        st.dataframe(regional_df, use_container_width=True)

if __name__ == "__main__":
    main()

