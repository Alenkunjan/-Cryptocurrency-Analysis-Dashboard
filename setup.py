"""
PROJECT SETUP AND VERIFICATION GUIDE
=======================================
Cryptocurrency Analysis Dashboard - Complete Implementation Guide
"""

import os
import sys
from pathlib import Path

print("=" * 70)
print("CRYPTOCURRENCY ANALYSIS DASHBOARD - SETUP VERIFICATION")
print("=" * 70)

PROJECT_DIR = Path(__file__).parent
REQUIREMENTS = [
    "requirements.txt",
    "app.py",
    "database.py",
    "data_acquisition.py",
    "data_processing.py",
    "utils.py",
    "pages/dashboard.py"
]

DATA_FILES = [
    "data/",
    "data/metrics_table.csv",
]

print("\n1️⃣  CHECKING PROJECT STRUCTURE...")
print("-" * 70)

all_files_exist = True
for file in REQUIREMENTS:
    filepath = PROJECT_DIR / file
    exists = "✓" if filepath.exists() else "✗"
    status = "EXISTS" if filepath.exists() else "MISSING"
    print(f"   {exists} {file:<40} {status}")
    if not filepath.exists():
        all_files_exist = False

if all_files_exist:
    print("\n✓ All required files are present!")
else:
    print("\n✗ Some files are missing. Please ensure all files are in place.")

print("\n2️⃣  DEPENDENCY CHECK...")
print("-" * 70)

try:
    import streamlit
    print(f"   ✓ streamlit {streamlit.__version__}")
except ImportError:
    print("   ✗ streamlit - NOT INSTALLED")

try:
    import pandas
    print(f"   ✓ pandas {pandas.__version__}")
except ImportError:
    print("   ✗ pandas - NOT INSTALLED")

try:
    import numpy
    print(f"   ✓ numpy {numpy.__version__}")
except ImportError:
    print("   ✗ numpy - NOT INSTALLED")

try:
    import plotly
    print(f"   ✓ plotly {plotly.__version__}")
except ImportError:
    print("   ✗ plotly - NOT INSTALLED")

try:
    import requests
    print(f"   ✓ requests {requests.__version__}")
except ImportError:
    print("   ✗ requests - NOT INSTALLED")

print("\n3️⃣  INSTALLATION INSTRUCTIONS...")
print("-" * 70)
print("""
To complete the setup, run these commands in your terminal:

1. Install dependencies:
   pip install -r requirements.txt

2. Initialize database (if not done):
   python database.py

3. Fetch and store cryptocurrency data (MILESTONE 1):
   python data_acquisition.py

4. Calculate financial metrics (MILESTONE 2):
   python data_processing.py

5. Run the Streamlit application:
   streamlit run app.py

Then navigate to the Dashboard page after logging in.
""")

print("\n4️⃣  PROJECT MILESTONES...")
print("-" * 70)
print("""
✓ MILESTONE 1: Data Acquisition and Setup
  ├─ Environment and libraries setup
  ├─ API integration (CoinGecko/Binance)
  ├─ Data storage (CSV/Parquet format)
  ├─ Missing value handling
  └─ Time-series formatting
  
  Run: python data_acquisition.py

✓ MILESTONE 2: Data Processing and Calculation
  ├─ Log-return calculation
  ├─ Daily and annualized volatility
  ├─ Sharpe ratio calculation
  ├─ Beta coefficient (vs BTC)
  ├─ Moving averages
  └─ Rolling window volatility
  
  Run: python data_processing.py

✓ MILESTONE 3: Visualization and Dashboard
  ├─ Interactive Plotly visualizations
  ├─ Time-series price and volatility graphs
  ├─ Risk-return scatter plots
  ├─ Multi-crypto comparisons
  ├─ Date-range filtering
  ├─ Portfolio analysis
  └─ Export functionality
  
  Access: Dashboard page in Streamlit app
""")

print("\n5️⃣  FEATURE SUMMARY...")
print("-" * 70)
print("""
Data Acquisition Module (data_acquisition.py):
  • CryptoDataFetcher: Fetches data from APIs
  • DataStorage: Saves/loads CSV and Parquet formats
  • DataPreprocessor: Handles cleaning and formatting
  • fetch_and_store_all_cryptos(): Main execution function

Data Processing Module (data_processing.py):
  • ReturnsCalculator: Log and simple returns
  • VolatilityCalculator: Daily and annualized volatility
  • RiskMetrics: Sharpe, Beta, Sortino, Max Drawdown
  • MetricsCalculator: Comprehensive metrics
  • calculate_metrics_for_all(): Generates metrics table

Utilities Module (utils.py):
  • CacheManager: Caches data in Streamlit
  • DataFilter: Filters by date, volatility, Sharpe
  • ChartBuilder: Creates interactive visualizations
  • MetricsFormatter: Formats display values
  • DataSummary: Portfolio statistics

Dashboard (pages/dashboard.py):
  • Key metrics display (price, change, vol, Sharpe)
  • Price and volume chart with OHLCV
  • Rolling volatility analysis
  • Risk-return scatter plot
  • Multi-crypto comparison charts
  • Detailed metrics table
  • Portfolio analysis summary
  • Date range and asset selection
  • Data export functionality
""")

print("\n6️⃣  DATA STRUCTURE...")
print("-" * 70)
print("""
Saved Data Format (data/ directory):
  ├─ bitcoin_data.csv/parquet
  ├─ ethereum_data.csv/parquet
  ├─ solana_data.csv/parquet
  ├─ cardano_data.csv/parquet
  ├─ dogecoin_data.csv/parquet
  └─ metrics_table.csv

DataFrame Columns (Price Data):
  • Date: Trading date
  • Open: Opening price
  • High: Highest price
  • Low: Lowest price
  • Close: Closing price
  • Volume: Trading volume
  • Year, Month, Quarter, DayOfWeek: Temporal features

Metrics Table Columns:
  • Cryptocurrency: Asset name
  • Current_Price: Latest price in USD
  • Price_Change_%: Percentage change from period start
  • Daily_Volatility_%: Daily standard deviation
  • Annual_Volatility_%: Annualized volatility
  • Sharpe_Ratio: Risk-adjusted return
  • Sortino_Ratio: Downside risk-adjusted return
  • Max_Drawdown_%: Peak-to-trough decline
  • Beta: Sensitivity to Bitcoin
  • Data_Points: Number of records
  • Date_Range: Period covered
""")

print("\n7️⃣  TROUBLESHOOTING...")
print("-" * 70)
print("""
Issue: "ModuleNotFoundError" when running dashboard
Solution: Run data_acquisition.py and data_processing.py first

Issue: API rate limits (too many requests)
Solution: Data is cached with TTL. Adjust caching in utils.py if needed

Issue: No data in metrics table
Solution: Ensure data_processing.py runs without errors first

Issue: Dashboard shows "No data available"
Solution: Check if data/ directory exists and contains CSV files

Issue: Slow performance
Solution: Reduce date range in dashboard, increase cache TTL (ttl parameter)
""")

print("\n8️⃣  NEXT STEPS...")
print("-" * 70)
print("""
1. Install dependencies:
   pip install -r requirements.txt

2. Run data acquisition (first time):
   python data_acquisition.py

3. Generate metrics:
   python data_processing.py

4. Start the application:
   streamlit run app.py

5. Login with:
   Username: admin
   Password: 1234

6. Navigate to Dashboard page to view analytics
""")

print("\n" + "=" * 70)
print("Setup verification complete!")
print("=" * 70 + "\n")
