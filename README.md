# 📊 Cryptocurrency Analysis Dashboard

A comprehensive 3-milestone project for cryptocurrency data acquisition, analysis, and visualization.

## 🎯 Project Overview

This project implements a complete cryptocurrency analysis platform with data acquisition, statistical analysis, and interactive visualizations.

### Three Milestones:

1. **Milestone 1: Data Acquisition (Week 1-2)**
   - Fetch crypto data from CoinGecko API
   - Store in CSV/Parquet format
   - Basic preprocessing and validation

2. **Milestone 2: Data Processing (Week 3-4)**
   - Calculate financial metrics (returns, volatility, Sharpe, Beta)
   - Generate comprehensive metrics table
   - Rolling window analysis

3. **Milestone 3: Dashboard (Week 5-6)**
   - Interactive Streamlit dashboard
   - Plotly visualizations
   - Risk-return analysis
   - Multi-crypto comparisons
4.** Milestone 4: Risk Classification & Reporting (Week 7–8)

   -Risk level categorization (Low, Medium, High)
   -Highlight high-risk cryptocurrencies in dashboard
   -Generate reports (CSV, PDF, PNG export)
   -Final validation and documentation  

---

## 📁 Project Structure

```
InfosysIn/
├── app.py                    # Login & main app
├── database.py              # User management
├── data_acquisition.py      # Milestone 1: Data fetching
├── data_processing.py       # Milestone 2: Metrics calculation
├── utils.py                 # Utilities & helpers
├── setup.py                 # Setup verification
├── requirements.txt         # Dependencies
├── pages/
│   └── dashboard.py        # Milestone 3: Dashboard
└── data/                   # Stored cryptocurrency data
    ├── bitcoin_data.csv
    ├── ethereum_data.csv
    ├── solana_data.csv
    ├── cardano_data.csv
    ├── dogecoin_data.csv
    └── metrics_table.csv
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Milestone 1: Data Acquisition

```bash
python data_acquisition.py
```

This fetches 1 year of historical data for 5 cryptocurrencies:
- Bitcoin (BTC)
- Ethereum (ETH)
- Solana (SOL)
- Cardano (ADA)
- Dogecoin (DOGE)

**Output:**
- `data/bitcoin_data.csv` and `.parquet`
- `data/ethereum_data.csv` and `.parquet`
- etc.

### 3. Run Milestone 2: Data Processing

```bash
python data_processing.py
```

This calculates financial metrics for all cryptocurrencies.

**Output:**
- `data/metrics_table.csv` with:
  - Annual Volatility
  - Sharpe Ratio
  - Beta (vs Bitcoin)
  - Max Drawdown
  - And more...

### 4. Start the Dashboard

```bash
streamlit run app.py
```

**Login:**
- Username: `admin`
- Password: `1234`

Navigate to **Dashboard** page to see all visualizations.

---

## 📊 Module Documentation

### 1. Data Acquisition (`data_acquisition.py`)

#### Classes:

**CryptoDataFetcher**
- `fetch_historical_data(crypto_id, days)` - Get price history
- `fetch_current_price(crypto_id)` - Get current price & metrics
- `fetch_binance_24h_data(symbol)` - Get Binance 24h stats

**DataStorage**
- `save_to_csv(df, crypto_id)` - Save as CSV
- `save_to_parquet(df, crypto_id)` - Save as Parquet
- `load_from_csv(crypto_id)` - Load from CSV
- `load_from_parquet(crypto_id)` - Load from Parquet

**DataPreprocessor**
- `handle_missing_values(df, method)` - Fill NaN values
- `format_timeseries(df)` - Format for analysis
- `validate_data_consistency(df)` - Check data quality

#### Main Function:
```python
fetch_and_store_all_cryptos(days=365)
```

### 2. Data Processing (`data_processing.py`)

#### Classes:

**ReturnsCalculator**
- `log_returns(prices)` - Calculate log returns
- `simple_returns(prices)` - Calculate simple returns
- `cumulative_returns(prices)` - Calculate cumulative returns

**VolatilityCalculator**
- `daily_volatility(returns, window)` - Daily volatility
- `annualized_volatility(returns)` - Annualized volatility
- `rolling_volatility(returns, window)` - Rolling volatility

**RiskMetrics**
- `sharpe_ratio(returns)` - Sharpe ratio
- `beta_coefficient(asset_returns, benchmark_returns)` - Beta vs benchmark
- `max_drawdown(returns)` - Maximum drawdown
- `sortino_ratio(returns)` - Sortino ratio

**MetricsCalculator**
```python
calc = MetricsCalculator(df, "Bitcoin")
metrics = calc.calculate_all_metrics(benchmark_returns)
```

### 3. Utilities (`utils.py`)

#### CacheManager
```python
metrics = CacheManager.load_metrics()
data = CacheManager.load_crypto_data("bitcoin")
prices = CacheManager.get_latest_prices()
```

#### ChartBuilder
```python
fig_price = ChartBuilder.create_price_chart(df, "Bitcoin")
fig_vol = ChartBuilder.create_volatility_chart(df, rolling_vol)
fig_scatter = ChartBuilder.create_risk_return_scatter(metrics_df)
fig_compare = ChartBuilder.create_comparison_chart(metrics_df, "Sharpe_Ratio")
```

#### MetricsFormatter
```python
MetricsFormatter.format_price(100.5)              # "$100.50"
MetricsFormatter.format_percentage(5.2)           # "🟢 +5.20%"
MetricsFormatter.get_risk_level(45)               # "🟡 Medium Risk"
MetricsFormatter.get_quality_badge(0.8)           # "⭐⭐ Good"
```

---

## 📈 Key Metrics Explained

### Volatility
- **Daily Volatility**: Standard deviation of daily returns
- **Annual Volatility**: Daily volatility × √252
- Formula: $\sigma_{annual} = \sigma_{daily} \times \sqrt{252}$

### Sharpe Ratio
Measures risk-adjusted returns.
$$\text{Sharpe} = \frac{\overline{r} - r_f}{\sigma}$$

Where:
- $\overline{r}$ = Mean annual return
- $r_f$ = Risk-free rate (2%)
- $\sigma$ = Annual volatility

### Beta Coefficient
Measures sensitivity to benchmark (BTC).
$$\beta = \frac{\text{Cov}(r_i, r_m)}{\text{Var}(r_m)}$$

### Sortino Ratio
Like Sharpe but only considers downside volatility:
$$\text{Sortino} = \frac{\overline{r} - r_f}{\sigma_{down}}$$

### Max Drawdown
Peak-to-trough decline:
$$\text{Max Drawdown} = \frac{\text{Trough} - \text{Peak}}{\text{Peak}}$$

---

## 🎨 Dashboard Features

### Key Metrics Section
- Current price
- Price change (%)
- Annual volatility
- Sharpe ratio

### Charts (4 Tabs)

1. **Price & Volume**
   - Candlestick-style chart
   - Volume bars
   - Date range filtering

2. **Volatility**
   - 30-day rolling volatility
   - Trend analysis
   - Risk visualization

3. **Risk-Return**
   - Scatter plot (all assets)
   - X-axis: Annual Volatility
   - Y-axis: Sharpe Ratio
   - Color: Sharpe Ratio intensity

4. **Comparison**
   - Bar charts comparing cryptos
   - Selectable metrics
   - Sortable data

### Detailed Metrics Table
- All calculated metrics
- Export to CSV
- Interactive filtering
- Responsive layout

### Portfolio Analysis
- Average volatility across assets
- Average Sharpe ratio
- Best and worst performers
- Most volatile and stable assets

---

## 🔧 Configuration

### Risk-Free Rate
Edit in `data_processing.py`:
```python
RISK_FREE_RATE = 0.02  # 2% annual
```

### Cryptocurrencies
Edit in `data_acquisition.py`:
```python
CRYPTOS = ["bitcoin", "ethereum", "solana", "cardano", "dogecoin"]
```

### Cache TTL (Time-To-Live)
In `utils.py`:
```python
@st.cache_data(ttl=3600)  # 1 hour
def load_metrics():
    ...
```

### Date Range
Default in `pages/dashboard.py`:
```python
start_date = datetime.now() - timedelta(days=90)
```

---

## 📊 Sample Output

### Metrics Table Example:
```
Cryptocurrency    Current_Price  Annual_Volatility_%  Sharpe_Ratio  Beta
Bitcoin           65000          45.2                  0.85          1.00
Ethereum          3500           52.1                  0.72          1.15
Solana            140            68.5                  0.55          1.42
Cardano           0.67           58.3                  0.48          1.28
Dogecoin          0.28           72.1                  0.32          1.35
```

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'data_acquisition'"
**Solution:** Ensure you're running from the project root directory.

### Issue: API Rate Limit Error
**Solution:** The dashboard caches data. Wait a few minutes before refreshing.

### Issue: "No data available" in dashboard
**Solution:** Run `python data_acquisition.py` first to fetch data.

### Issue: Slow dashboard performance
**Solution:** 
- Reduce date range
- Increase cache TTL
- Close unused browser tabs

### Issue: Dashboard login fails
**Solution:** 
- Ensure database.py has been run
- Default credentials: admin / 1234
- Check `users.db` file exists

---

## 📚 Resources

### APIs Used
- [CoinGecko API](https://www.coingecko.com/api) - Free crypto data
- [Binance API](https://binance-docs.github.io/apidocs/) - Real-time prices

### Libraries
- **Streamlit**: Web app framework
- **Pandas**: Data manipulation
- **NumPy**: Numerical computing
- **Plotly**: Interactive visualizations
- **Requests**: HTTP library

### Learning Materials
- Volatility calculation
- Sharpe ratio explained
- Beta coefficient analysis
- Time series analysis

---

## 📝 License

Educational project for learning cryptocurrency analysis.

---

## 👨‍💻 Author

Created as a comprehensive learning project demonstrating:
- Data acquisition from APIs
- Statistical analysis
- Interactive visualizations
- Full-stack data application

---

## ✅ Checklist

### Setup
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run data acquisition: `python data_acquisition.py`
- [ ] Run data processing: `python data_processing.py`
- [ ] Start app: `streamlit run app.py`

### Dashboard Navigation
- [ ] Login with admin/1234
- [ ] Click "Dashboard" in sidebar
- [ ] Explore different charts
- [ ] Try date range filters
- [ ] Download metrics CSV

### Features to Test
- [ ] Key metrics updates
- [ ] Price & volume chart
- [ ] Volatility analysis
- [ ] Risk-return scatter
- [ ] Multi-crypto comparison
- [ ] Portfolio summary
- [ ] Data export

---

## 🎓 Learning Outcomes

After completing this project, you'll understand:

✓ Fetching and storing financial data
✓ Calculating financial metrics
✓ Time-series analysis
✓ Risk and return concepts
✓ Building interactive dashboards
✓ Data visualization best practices
✓ Python data science workflow

---

