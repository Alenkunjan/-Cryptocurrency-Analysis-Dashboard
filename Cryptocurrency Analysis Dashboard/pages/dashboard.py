"""
Milestone 3: Visualization and Dashboard Development
Interactive Streamlit dashboard for cryptocurrency analysis.
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path

# Import custom modules
try:
    from data_acquisition import CryptoDataFetcher, DataStorage
    from data_processing import (ReturnsCalculator, VolatilityCalculator, 
                                 RiskMetrics, MetricsCalculator, calculate_metrics_for_all)
    from utils import (CacheManager, ChartBuilder, DataFilter, MetricsFormatter, 
                      DataSummary, init_session_state, get_crypto_emoji)
    from risk_classification import generate_risk_classification_report, load_risk_report
    from report_generator import generate_all_reports
    from risk_dashboard import RiskVisualizer, RiskWarningPanel, display_risk_cards
except ImportError as e:
    st.error(f"⚠️ Required modules not found: {str(e)}")
    st.stop()

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Crypto Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state (kept for backwards compatibility)
init_session_state()

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Dark mode background */
    .stApp {
        background: linear-gradient(135deg, #060b17 0%, #0b1a3d 60%, #081324 100%);
    }

    /* Global font color (match dark theme) */
    .stApp, .stApp * {
        color: #e5e6eb !important;
    }

    /* Top app layer background */
    div[data-testid="stAppViewContainer"] > div:first-child {
        background: linear-gradient(135deg, rgba(8, 16, 38, 0.95), rgba(15, 26, 48, 0.9));
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
    }

    /* Streamlit toolbar / header bar */
    header, header > div {
        background: linear-gradient(135deg, rgba(10, 22, 40, 0.97), rgba(18, 34, 60, 0.95)) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.12) !important;
    }

    header, header * {
        color: #e5e6eb !important;
    }

    /* Metric card style */
    .metric-card {
        background: linear-gradient(135deg, rgba(18, 33, 62, 0.85) 0%, rgba(27, 50, 90, 0.75) 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 20px;
        border-radius: 12px;
        color: #f4f7ff;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
    }

    /* Hide the default Streamlit sidebar (we're moving controls to the top toolbar) */
    section[data-testid="stSidebar"] {
        display: none !important;
    }

    /* Top toolbar container */
    div[data-testid="stAppViewContainer"] > div:first-child {
        background: linear-gradient(135deg, rgba(8, 16, 38, 0.95), rgba(15, 26, 48, 0.9));
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
    }

    /* Toolbar controls styling */
    .stSelectbox>div>div>div {
        background: rgba(12, 16, 30, 0.65) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        color: #e5e6eb !important;
        border-radius: 8px;
    }

    .stDateInput>div>div>div {
        background: rgba(12, 16, 30, 0.65) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        color: #e5e6eb !important;
        border-radius: 8px;
    }

    .stButton>button {
        background: linear-gradient(135deg, #1a73e8 0%, #00c6ff 100%) !important;
        color: #0b1a3d !important;
        border-radius: 8px;
    }

    /* Table and widget backgrounds */
    div[data-testid="stHorizontalBlock"] > div, div[data-testid="stVerticalBlock"] > div {
        background-color: rgba(15, 26, 48, 0.65) !important;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.07);
    }

    /* Dataframe table background (black theme) */
    div[data-testid="stDataFrame"] {
        background-color: rgba(0, 0, 0, 0.95) !important;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.12);
    }

    div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {
        background-color: rgba(0, 0, 0, 0.85) !important;
        color: #e5e6eb !important;
    }

    /* Stripe rows for readability */
    div[data-testid="stDataFrame"] tr:nth-child(even) td {
        background-color: rgba(255, 255, 255, 0.04) !important;
    }
    div[data-testid="stDataFrame"] tr:nth-child(odd) td {
        background-color: rgba(0, 0, 0, 0.75) !important;
    }

    div[data-testid="stDataFrame"] th {
        background-color: rgba(255, 255, 255, 0.12) !important;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# --- TOP TOOLBAR CONTROLS ---
with st.container():
    toolbar_col1, toolbar_col2, toolbar_col3, toolbar_col4 = st.columns([2, 2, 2, 4])

    with toolbar_col1:
        st.markdown("### ⚙️ Controls")
        milestone_mode = "dashboard"  # Default to main dashboard
        
        cryptos = ["bitcoin", "ethereum", "solana", "cardano", "dogecoin"]
        selected_crypto = st.selectbox(
            "Select Cryptocurrency",
            cryptos,
            format_func=lambda x: f"{get_crypto_emoji(x)} {x.capitalize()}"
        )

    with toolbar_col2:
        st.markdown("### 📅 Filters")
        date_range = st.date_input(
            "Select Date Range",
            value=(datetime.now() - timedelta(days=90), datetime.now()),
            max_value=datetime.now()
        )
        search_query = st.text_input("Search", placeholder="Search metrics...", key="search")

    with toolbar_col3:
        st.markdown("### 🔄 Actions")
        if st.button("Refresh Data"):
            st.cache_data.clear()
            st.experimental_rerun()

    with toolbar_col4:
        st.markdown("### � Status")
        st.info("Dashboard Ready")

# --- MAIN DASHBOARD ---
if milestone_mode == "acquisition":
    st.title("📥 Data Acquisition Dashboard")
    st.caption(f"Milestone 1: Data Collection & Storage | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
elif milestone_mode == "processing":
    st.title("⚙️ Data Processing Dashboard")
    st.caption(f"Milestone 2: Metrics Calculation & Analysis | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
elif milestone_mode == "dashboard":
    st.title("📊 Cryptocurrency Analysis Dashboard")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
elif milestone_mode == "risk":
    st.title("🚨 Risk Classification & Analysis Dashboard")
    st.caption(f"Milestone 4: Advanced Risk Assessment | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Load data conditionally based on milestone
df_current = None
metrics_df = None

if milestone_mode in ["dashboard", "processing"]:
    try:
        df_current = CacheManager.load_crypto_data(selected_crypto)
        
        # Try to load metrics from session state first, then from file
        if "metrics_df" in st.session_state and st.session_state.metrics_df is not None and len(st.session_state.metrics_df) > 0:
            metrics_df = st.session_state.metrics_df
        else:
            # If session state is empty, load directly from file
            metrics_df = CacheManager.load_metrics()
            st.session_state.metrics_df = metrics_df
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.stop()

if milestone_mode == "dashboard" and (df_current is None or len(df_current) == 0):
    st.warning(f"No data available for {selected_crypto}. Please run data acquisition first.")
    st.stop()

# --- MILESTONE CONTENT ---
if milestone_mode == "acquisition":
    # Milestone 1: Data Acquisition Content
    st.header("📥 Data Acquisition Status")
    
    # Check data files
    cryptos = ["bitcoin", "ethereum", "solana", "cardano", "dogecoin"]
    data_status = {}
    
    for crypto in cryptos:
        csv_path = Path(f"data/{crypto}_data.csv")
        parquet_path = Path(f"data/{crypto}_data.parquet")
        data_status[crypto] = {
            "csv": csv_path.exists(),
            "parquet": parquet_path.exists(),
            "size": csv_path.stat().st_size if csv_path.exists() else 0
        }
    
    # Status overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Data Collection Status")
        total_cryptos = len(cryptos)
        available_cryptos = sum(1 for status in data_status.values() if status["csv"])
        
        if available_cryptos >= 5:
            st.success(f"✅ Successfully retrieved and stored daily price data for {available_cryptos} cryptocurrencies")
        else:
            st.warning(f"⚠️ Only {available_cryptos} out of {total_cryptos} cryptocurrencies have data")
        
        st.info("**Required:** At least 5 cryptocurrencies (BTC, ETH, SOL, ADA, DOGE)")
    
    with col2:
        st.subheader("📊 Data Files Overview")
        for crypto, status in data_status.items():
            emoji = "✅" if status["csv"] else "❌"
            size_mb = status["size"] / (1024 * 1024) if status["size"] > 0 else 0
            st.write(f"{emoji} {crypto.capitalize()}: {size_mb:.1f} MB")
    
    # Detailed data preview
    st.divider()
    st.header("🔍 Data Preview")
    
    if data_status[selected_crypto]["csv"]:
        try:
            df_preview = CacheManager.load_crypto_data(selected_crypto)
            if df_preview is not None and len(df_preview) > 0:
                st.subheader(f"Sample data for {selected_crypto.capitalize()}")
                st.dataframe(df_preview.head(10), use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Records", len(df_preview))
                with col2:
                    st.metric("Date Range", f"{df_preview.index.min().date()} to {df_preview.index.max().date()}")
                with col3:
                    st.metric("Columns", len(df_preview.columns))
            else:
                st.warning(f"No data loaded for {selected_crypto}")
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
    else:
        st.warning(f"No data file found for {selected_crypto}. Run data acquisition first.")

elif milestone_mode == "processing":
    # Milestone 2: Data Processing Content
    st.header("⚙️ Data Processing & Metrics Calculation")
    
    # Check if metrics exist
    if metrics_df is not None and len(metrics_df) > 0:
        st.success("✅ Financial metrics calculated for all cryptocurrencies")
        
        # Metrics overview
        st.subheader("📈 Calculated Metrics Overview")
        st.dataframe(metrics_df, use_container_width=True)
        
        # Key statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Assets Analyzed", len(metrics_df))
        
        with col2:
            avg_vol = metrics_df['Annual_Volatility'].mean()
            st.metric("Avg Annual Volatility", f"{avg_vol:.1f}%")
        
        with col3:
            avg_sharpe = metrics_df['Sharpe_Ratio'].mean()
            st.metric("Avg Sharpe Ratio", f"{avg_sharpe:.2f}")
        
        with col4:
            best_performer = metrics_df.loc[metrics_df['Sharpe_Ratio'].idxmax(), 'Asset']
            st.metric("Best Sharpe", best_performer)
        
        # Individual asset metrics
        st.divider()
        st.header("🔍 Individual Asset Analysis")
        
        if selected_crypto in metrics_df['Asset'].str.lower().values:
            asset_metrics = metrics_df[metrics_df['Asset'].str.lower() == selected_crypto].iloc[0]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Current Price", MetricsFormatter.format_price(asset_metrics['Current_Price']))
            
            with col2:
                st.metric("Annual Volatility", f"{asset_metrics['Annual_Volatility']:.1f}%")
            
            with col3:
                st.metric("Sharpe Ratio", f"{asset_metrics['Sharpe_Ratio']:.2f}")
            
            with col4:
                st.metric("Max Drawdown", f"{asset_metrics['Max_Drawdown']:.1f}%")
        else:
            st.warning(f"No metrics found for {selected_crypto}")
            
    else:
        st.warning("⚠️ No metrics data found. Run data processing first.")
        st.info("Run `python data_processing.py` to calculate metrics")

elif milestone_mode == "dashboard":
    # Original Milestone 3 Dashboard Content
    
    # Filter by date range
    if isinstance(date_range[0], (str, pd.Timestamp)):
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1])
    else:
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1])

    df_filtered = DataFilter.filter_by_date_range(df_current, start_date, end_date)

    # --- LIVE PRICES ---
    st.header("🔌 Live Cryptocurrency Prices")
    
    try:
        prices = CacheManager.get_latest_prices()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if 'bitcoin' in prices:
                st.metric(
                    f"{get_crypto_emoji('bitcoin')} Bitcoin",
                    MetricsFormatter.format_price(prices['bitcoin'])
                )
        
        with col2:
            if 'ethereum' in prices:
                st.metric(
                    f"{get_crypto_emoji('ethereum')} Ethereum",
                    MetricsFormatter.format_price(prices['ethereum'])
                )
        
        with col3:
            if 'solana' in prices:
                st.metric(
                    f"{get_crypto_emoji('solana')} Solana",
                    MetricsFormatter.format_price(prices['solana'])
                )
        
        with col4:
            if 'cardano' in prices:
                st.metric(
                    f"{get_crypto_emoji('cardano')} Cardano",
                    MetricsFormatter.format_price(prices['cardano'])
                )
        
        with col5:
            if 'dogecoin' in prices:
                st.metric(
                    f"{get_crypto_emoji('dogecoin')} Dogecoin",
                    MetricsFormatter.format_price(prices['dogecoin'])
                )
    
    except Exception as e:
        st.info("Live prices unavailable at the moment")

    # --- SECTION 1: KEY METRICS ---
    st.header("📈 Key Performance Metrics")

    col1, col2, col3, col4 = st.columns(4)

    if len(df_filtered) > 0:
        current_price = df_filtered['Close'].iloc[-1]
        price_change = ((df_filtered['Close'].iloc[-1] - df_filtered['Close'].iloc[0]) / df_filtered['Close'].iloc[0]) * 100
        
        with col1:
            st.metric(
                "Current Price",
                MetricsFormatter.format_price(current_price)
            )
        
        with col2:
            st.metric(
                "Price Change",
                MetricsFormatter.format_percentage(price_change)
            )
        
        # Calculate volatility
        returns = ReturnsCalculator.log_returns(df_filtered['Close']).dropna()
        annual_vol = VolatilityCalculator.annualized_volatility(returns)
        
        with col3:
            st.metric(
                "Annual Volatility",
                f"{annual_vol:.2f}%",
                delta=MetricsFormatter.get_risk_level(annual_vol)
            )
        
        # Calculate Sharpe ratio
        sharpe = RiskMetrics.sharpe_ratio(returns)
        
        with col4:
            st.metric(
                "Sharpe Ratio",
                MetricsFormatter.format_ratio(sharpe),
                delta=MetricsFormatter.get_quality_badge(sharpe)
            )

    # --- SECTION 2: MAIN CHARTS ---
    st.divider()
    st.header("📊 Analysis Charts")

    # --- SECTION 2: MAIN CHARTS ---
    st.divider()
    st.header("📊 Analysis Charts")

    # 💹 Price & Volume Section
    st.subheader("💹 Price & Volume")
    fig_price = ChartBuilder.create_price_chart(df_filtered, selected_crypto.capitalize())
    st.plotly_chart(fig_price, use_container_width=True)

    st.divider()

    # 📉 Volatility Section
    st.subheader("📉 Volatility")
    if len(returns) > 30:
        rolling_vol = VolatilityCalculator.rolling_volatility(returns, window=30)
        fig_vol = ChartBuilder.create_volatility_chart(df_filtered[30:], rolling_vol[30:])
        st.plotly_chart(fig_vol, use_container_width=True)
    else:
        st.info("Insufficient data for volatility analysis. Need at least 31 data points.")

    st.divider()

    # 🎯 Risk-Return Section
    st.subheader("🎯 Risk-Return")
    if len(metrics_df) > 0:
        fig_scatter = ChartBuilder.create_risk_return_scatter(metrics_df)
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("No metrics data available.")

    st.divider()

    # 📊 Comparison Section
    st.subheader("📊 Comparison")
    if len(metrics_df) > 0:
        metric_choice = st.selectbox(
            "Select Metric to Compare",
            ["Annual_Volatility_%", "Sharpe_Ratio", "Price_Change_%", "Max_Drawdown_%"]
        )
        fig_compare = ChartBuilder.create_comparison_chart(metrics_df, metric_choice)
        st.plotly_chart(fig_compare, use_container_width=True)

    st.divider()

    # 🛡️ Risk Assessment Section
    st.subheader("🛡️ Risk Assessment")
    
    # Generate risk classification if not exists
    risk_path = Path(__file__).parent.parent / "data" / "risk_classification_report.csv"
    if not risk_path.exists():
        with st.spinner("Generating risk classifications..."):
            risk_df = generate_risk_classification_report(metrics_df)
    else:
        risk_df = load_risk_report()
    
    if len(risk_df) > 0:
        # Risk cards overview
        st.markdown("### Quick Risk Overview")
        display_risk_cards(risk_df)
        
        # Risk selection
        risk_crypto = st.selectbox(
            "Select Cryptocurrency for Detailed Risk Analysis",
            risk_df['Cryptocurrency'].tolist()
        )
        
        risk_row = risk_df[risk_df['Cryptocurrency'] == risk_crypto].iloc[0]
        
        # Risk gauge
        col1, col2 = st.columns(2)
        
        with col1:
            fig_gauge = RiskVisualizer.create_risk_gauge(
                risk_row['Cryptocurrency'],
                risk_row['Composite_Risk_Score'],
                risk_row['Overall_Risk_Level']
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col2:
            st.markdown("#### Risk Details")
            st.metric("Overall Risk Level", risk_row['Overall_Risk_Level'])
            st.metric("Risk Score", f"{risk_row['Composite_Risk_Score']:.0f}/100")
            st.metric("Volatility Level", risk_row['Volatility_Level'])
            st.metric("Sharpe Ratio Level", risk_row['Sharpe_Level'])
        
        # Warnings and recommendations
        st.markdown("#### ⚠️ Risk Warnings")
        warnings = risk_row.get('Risk_Warnings', [])
        if isinstance(warnings, str):
            warnings = [warnings]
        
        for warning in warnings:
            if "No major" in str(warning):
                st.success(f"✓ {warning}")
            else:
                st.warning(f"{warning}")
        
        # Recommendations
        st.markdown("#### 💡 Recommendations")
        recommendations = risk_row.get('Recommendations', [])
        if isinstance(recommendations, str):
            recommendations = [recommendations]
        
        for rec in recommendations:
            if "Suitable for conservative" in str(rec) or "✓" in str(rec):
                st.success(rec)
            elif "EXTREME" in str(rec) or "high-risk" in str(rec.lower()):
                st.error(rec)
            else:
                st.info(rec)
        
        # Risk heatmap for all cryptos
        st.markdown("### Risk Factor Heatmap (All Assets)")
        fig_heatmap = RiskVisualizer.create_risk_heatmap(risk_df)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.warning("No risk classification data available.")

    st.divider()

    # 📋 Reports Section
    st.subheader("📋 Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Generate Risk Reports", use_container_width=True):
            with st.spinner("Generating reports..."):
                # Generate risk classifications
                risk_df = generate_risk_classification_report(metrics_df)
                
                # Generate all report types
                reports = generate_all_reports(metrics_df, risk_df)
                
                st.success("✓ Reports generated successfully!")
                
                st.markdown("### 📄 Available Reports:")
                
                # CSV reports
                if reports.get('summary_csv'):
                    with open(reports['summary_csv'], 'rb') as f:
                        st.download_button(
                            label="📥 Download Summary CSV",
                            data=f.read(),
                            file_name="crypto_summary.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                
                if reports.get('detailed_csv'):
                    with open(reports['detailed_csv'], 'rb') as f:
                        st.download_button(
                            label="📥 Download Detailed CSV",
                            data=f.read(),
                            file_name="crypto_detailed.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                
                if reports.get('html_report'):
                    with open(reports['html_report'], 'rb') as f:
                        st.download_button(
                            label="📥 Download HTML Report",
                            data=f.read(),
                            file_name="crypto_report.html",
                            mime="text/html",
                            use_container_width=True
                        )
    
    with col2:
        st.markdown("### 📊 Report Information")
        st.info("""
        **Available Report Types:**
        
        📄 **Summary CSV**
        - Quick overview metrics
        - Risk classifications
        - All cryptocurrencies
        
        📋 **Detailed CSV**
        - Comprehensive metrics
        - Individual risk assessments
        - Warnings & recommendations
        
        🌐 **HTML Report**
        - Professional formatted report
        - Can be opened in any browser
        - Includes charts and analysis
        
        🖼️ **Chart Images** (PNG)
        - Metric comparisons
        - Risk gauge visualizations
        """)
    
    st.divider()
    
    # Recent reports directory
    st.markdown("### 📁 Recent Reports")
    reports_dir = Path(__file__).parent.parent / "reports"
    
    if reports_dir.exists():
        report_files = sorted(reports_dir.glob("*"), key=lambda x: x.stat().st_mtime, reverse=True)
        if report_files:
            for report_file in report_files[:10]:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.caption(f"📄 {report_file.name}")
                with col2:
                    with open(report_file, 'rb') as f:
                        st.download_button(
                            label="↓",
                            data=f.read(),
                            file_name=report_file.name,
                            key=str(report_file)
                        )

    # --- SECTION 3: DETAILED METRICS TABLE ---
    st.divider()
    st.header("📋 Detailed Market Data")

    # Apply search filter
    search_query = st.session_state.get('search', '')
    if search_query:
        filtered_df = metrics_df[metrics_df['Cryptocurrency'].str.contains(search_query, case=False, na=False)]
    else:
        filtered_df = metrics_df

    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("All Cryptocurrencies Metrics")

    with col2:
        if st.button("📥 Export CSV"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="crypto_metrics.csv",
                mime="text/csv"
            )

    if len(filtered_df) > 0:
        st.dataframe(
            filtered_df.drop(['Date_Range'], axis=1),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Cryptocurrency": st.column_config.TextColumn(width="medium"),
                "Current_Price": st.column_config.NumberColumn(format="$%.2f"),
                "Price_Change_%": st.column_config.NumberColumn(format="%.2f%%"),
                "Daily_Volatility_%": st.column_config.NumberColumn(format="%.2f%%"),
                "Annual_Volatility_%": st.column_config.NumberColumn(format="%.2f%%"),
                "Sharpe_Ratio": st.column_config.NumberColumn(format="%.2f"),
                "Sortino_Ratio": st.column_config.NumberColumn(format="%.2f"),
                "Max_Drawdown_%": st.column_config.NumberColumn(format="%.2f%%"),
                "Beta": st.column_config.NumberColumn(format="%.2f"),
                "Data_Points": st.column_config.NumberColumn(format="%d"),
            }
        )
    else:
        st.warning("No matching metrics data found.")

    # --- SECTION 4: PORTFOLIO ANALYSIS ---
    st.divider()
    st.header("🎯 Portfolio Analysis")

    if len(filtered_df) > 0:
        portfolio_stats = DataSummary.get_portfolio_stats(filtered_df)
        best_worst = DataSummary.get_best_worst(filtered_df)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📊 Portfolio Assets", portfolio_stats.get('Total_Assets', 0))
            st.metric("📈 Avg Annual Vol", f"{portfolio_stats.get('Average_Volatility', 0):.2f}%")
        
        with col2:
            st.metric("⭐ Avg Sharpe Ratio", f"{portfolio_stats.get('Average_Sharpe', 0):.2f}")
            st.metric("🏆 Best Performer", best_worst.get('Best_Sharpe', 'N/A'))
        
        with col3:
            st.metric("🔥 Most Volatile", best_worst.get('Most_Volatile', 'N/A'))
            st.metric("🛡️ Most Stable", best_worst.get('Most_Stable', 'N/A'))
elif milestone_mode == "risk":
    # Milestone 4: Risk Classification Content
    try:
        # Load risk report
        risk_report = load_risk_report()
        
        if risk_report is not None and len(risk_report) > 0:
            # Risk Overview Section
            st.header("🎯 Risk Classification Overview")
            
            # Risk Summary Cards
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                low_risk = len(risk_report[risk_report['Risk_Level'].str.contains('Low', na=False)])
                st.metric("🟢 Low Risk Assets", low_risk)
            with col2:
                med_risk = len(risk_report[risk_report['Risk_Level'].str.contains('Medium', na=False)])
                st.metric("🟡 Medium Risk Assets", med_risk)
            with col3:
                high_risk = len(risk_report[risk_report['Risk_Level'].str.contains('High', na=False)])
                st.metric("🔴 High Risk Assets", high_risk)
            with col4:
                total = len(risk_report)
                st.metric("📊 Total Assets", total)
            
            # Risk Classification Table
            st.header("📋 Detailed Risk Classification")
            st.dataframe(risk_report, use_container_width=True)
            
            # Risk Visualization
            st.header("📊 Risk Analysis Charts")
            
            # Risk distribution pie chart
            risk_counts = risk_report['Risk_Level'].value_counts()
            fig_pie = px.pie(
                values=risk_counts.values,
                names=risk_counts.index,
                title="Risk Level Distribution",
                color_discrete_map={
                    'Low Risk': '#27AE60',
                    'Medium Risk': '#F39C12', 
                    'High Risk': '#E74C3C',
                    'Critical Risk': '#8B0000'
                }
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # Risk score vs volatility scatter
            fig_scatter = px.scatter(
                risk_report,
                x='Volatility',
                y='Risk_Score',
                color='Risk_Level',
                size='Sharpe_Ratio',
                hover_data=['Asset'],
                title="Risk Score vs Volatility Analysis",
                color_discrete_map={
                    'Low Risk': '#27AE60',
                    'Medium Risk': '#F39C12',
                    'High Risk': '#E74C3C',
                    'Critical Risk': '#8B0000'
                }
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            
        else:
            st.warning("⚠️ Risk classification report not found. Please run risk classification first.")
            if st.button("Generate Risk Report"):
                with st.spinner("Generating risk classification report..."):
                    generate_risk_classification_report()
                    st.success("✅ Risk report generated! Please refresh the page.")
                    
    except Exception as e:
        st.error(f"Error loading risk data: {str(e)}")
        st.info("💡 Make sure to run the risk classification analysis first.")

# --- FOOTER ---
st.divider()
st.markdown("""
<div style='text-align: center; color: #888; font-size: 12px;'>
    <p>Data Source: CoinGecko API | Last Update: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
    <p>⚠️ This dashboard is for educational purposes. Not financial advice.</p>
</div>
""", unsafe_allow_html=True)
