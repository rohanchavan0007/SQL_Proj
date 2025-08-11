import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import mysql.connector
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import warnings
warnings.filterwarnings('ignore')

# Database connection details
DB_CONFIG = {
    'host': 'localhost',
    'database': 'retail_sales',
    'user': 'root',
    'password': 'root'
}

def get_data_from_db(query):
    """Execute SQL query and return DataFrame"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        df = pd.read_sql(query, connection)
        connection.close()
        return df
    except Exception as e:
        print(f"Database connection error: {e}")
        return pd.DataFrame()

def prepare_time_series_data():
    """Prepare monthly sales data for forecasting"""
    query = """
    SELECT 
        DATE_FORMAT(o.order_date, '%Y-%m-01') as month_date,
        SUM(s.sales) as monthly_sales,
        SUM(s.profit) as monthly_profit,
        COUNT(DISTINCT s.order_id) as monthly_orders
    FROM sales s
    JOIN orders o ON s.order_id = o.order_id
    GROUP BY DATE_FORMAT(o.order_date, '%Y-%m')
    ORDER BY month_date
    """
    
    df = get_data_from_db(query)
    if not df.empty:
        df['month_date'] = pd.to_datetime(df['month_date'])
        df['month_number'] = range(len(df))
        return df
    return pd.DataFrame()

def linear_forecast(df, periods=6, target_column='monthly_sales'):
    """Simple linear regression forecast"""
    if df.empty or len(df) < 3:
        return pd.DataFrame()
    
    X = df[['month_number']].values
    y = df[target_column].values
    
    # Fit linear regression
    model = LinearRegression()
    model.fit(X, y)
    
    # Generate future predictions
    last_month = df['month_number'].max()
    future_months = np.array([[last_month + i + 1] for i in range(periods)])
    future_predictions = model.predict(future_months)
    
    # Create future dates
    last_date = df['month_date'].max()
    future_dates = [last_date + timedelta(days=30*(i+1)) for i in range(periods)]
    
    forecast_df = pd.DataFrame({
        'month_date': future_dates,
        'predicted_value': future_predictions,
        'forecast_type': 'Linear'
    })
    
    return forecast_df

def polynomial_forecast(df, periods=6, target_column='monthly_sales', degree=2):
    """Polynomial regression forecast"""
    if df.empty or len(df) < 3:
        return pd.DataFrame()
    
    X = df[['month_number']].values
    y = df[target_column].values
    
    # Create polynomial features
    poly_features = PolynomialFeatures(degree=degree)
    X_poly = poly_features.fit_transform(X)
    
    # Fit polynomial regression
    model = LinearRegression()
    model.fit(X_poly, y)
    
    # Generate future predictions
    last_month = df['month_number'].max()
    future_months = np.array([[last_month + i + 1] for i in range(periods)])
    future_months_poly = poly_features.transform(future_months)
    future_predictions = model.predict(future_months_poly)
    
    # Create future dates
    last_date = df['month_date'].max()
    future_dates = [last_date + timedelta(days=30*(i+1)) for i in range(periods)]
    
    forecast_df = pd.DataFrame({
        'month_date': future_dates,
        'predicted_value': future_predictions,
        'forecast_type': f'Polynomial (degree {degree})'
    })
    
    return forecast_df

def moving_average_forecast(df, periods=6, target_column='monthly_sales', window=3):
    """Moving average forecast"""
    if df.empty or len(df) < window:
        return pd.DataFrame()
    
    # Calculate moving average
    recent_values = df[target_column].tail(window).mean()
    
    # Create future dates
    last_date = df['month_date'].max()
    future_dates = [last_date + timedelta(days=30*(i+1)) for i in range(periods)]
    
    forecast_df = pd.DataFrame({
        'month_date': future_dates,
        'predicted_value': [recent_values] * periods,
        'forecast_type': f'Moving Average ({window} months)'
    })
    
    return forecast_df

def seasonal_forecast(df, periods=6, target_column='monthly_sales'):
    """Simple seasonal forecast based on historical patterns"""
    if df.empty or len(df) < 12:
        return pd.DataFrame()
    
    # Extract month from date and calculate seasonal averages
    df['month'] = df['month_date'].dt.month
    seasonal_avg = df.groupby('month')[target_column].mean()
    
    # Generate future predictions based on seasonal patterns
    last_date = df['month_date'].max()
    future_dates = [last_date + timedelta(days=30*(i+1)) for i in range(periods)]
    
    predictions = []
    for date in future_dates:
        month = date.month
        if month in seasonal_avg.index:
            predictions.append(seasonal_avg[month])
        else:
            predictions.append(df[target_column].mean())
    
    forecast_df = pd.DataFrame({
        'month_date': future_dates,
        'predicted_value': predictions,
        'forecast_type': 'Seasonal'
    })
    
    return forecast_df

def calculate_forecast_accuracy(df, target_column='monthly_sales'):
    """Calculate basic forecast accuracy metrics"""
    if df.empty or len(df) < 6:
        return {}
    
    # Use last 6 months as test set
    train_df = df.iloc[:-6]
    test_df = df.iloc[-6:]
    
    if len(train_df) < 3:
        return {}
    
    # Generate forecasts for test period
    linear_pred = linear_forecast(train_df, periods=6, target_column=target_column)
    poly_pred = polynomial_forecast(train_df, periods=6, target_column=target_column)
    ma_pred = moving_average_forecast(train_df, periods=6, target_column=target_column)
    
    accuracy_metrics = {}
    
    # Calculate MAPE (Mean Absolute Percentage Error) for each method
    actual_values = test_df[target_column].values
    
    if not linear_pred.empty and len(linear_pred) == len(actual_values):
        linear_mape = np.mean(np.abs((actual_values - linear_pred['predicted_value'].values) / actual_values)) * 100
        accuracy_metrics['Linear'] = f"{linear_mape:.2f}%"
    
    if not poly_pred.empty and len(poly_pred) == len(actual_values):
        poly_mape = np.mean(np.abs((actual_values - poly_pred['predicted_value'].values) / actual_values)) * 100
        accuracy_metrics['Polynomial'] = f"{poly_mape:.2f}%"
    
    if not ma_pred.empty and len(ma_pred) == len(actual_values):
        ma_mape = np.mean(np.abs((actual_values - ma_pred['predicted_value'].values) / actual_values)) * 100
        accuracy_metrics['Moving Average'] = f"{ma_mape:.2f}%"
    
    return accuracy_metrics

def get_sales_forecasts(periods=6):
    """Get comprehensive sales forecasts using multiple methods"""
    df = prepare_time_series_data()
    
    if df.empty:
        return pd.DataFrame(), {}
    
    # Generate forecasts using different methods
    linear_forecast_df = linear_forecast(df, periods)
    poly_forecast_df = polynomial_forecast(df, periods)
    ma_forecast_df = moving_average_forecast(df, periods)
    seasonal_forecast_df = seasonal_forecast(df, periods)
    
    # Combine all forecasts
    all_forecasts = []
    for forecast_df in [linear_forecast_df, poly_forecast_df, ma_forecast_df, seasonal_forecast_df]:
        if not forecast_df.empty:
            all_forecasts.append(forecast_df)
    
    if all_forecasts:
        combined_forecasts = pd.concat(all_forecasts, ignore_index=True)
    else:
        combined_forecasts = pd.DataFrame()
    
    # Calculate accuracy metrics
    accuracy_metrics = calculate_forecast_accuracy(df)
    
    return combined_forecasts, accuracy_metrics, df

if __name__ == "__main__":
    # Test the forecasting functions
    forecasts, accuracy, historical = get_sales_forecasts()
    print("Forecasts generated:")
    print(forecasts.head())
    print("\nAccuracy metrics:")
    print(accuracy)

