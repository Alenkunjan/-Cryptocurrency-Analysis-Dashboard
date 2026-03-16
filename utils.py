"""
Utility functions for cryptocurrency analysis dashboard.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import streamlit as st
from datetime import datetime, timedelta
import os

# Get the parent directory (project root)
PROJECT_ROOT = Path(__file__).parent.absolute()
DATA_DIR = PROJECT_ROOT / "data"


class CacheManager:
    """Manage data caching for the dashboard."""
    
    @staticmethod
    @st.cache_data(ttl=3600)
    def load_metrics():
        """Load cached metrics from CSV."""
        # Try multiple path options to ensure we find the file
        possible_paths = [
            DATA_DIR / "metrics_table.csv",
            Path("data") / "metrics_table.csv",
            Path(__file__).parent / "data" / "metrics_table.csv",
        ]
        
        for path in possible_paths:
            path = Path(path).absolute()
            if path.exists():
                try:
                    df = pd.read_csv(path)
                    return df
                except Exception as e:
                    continue
        
        return pd.DataFrame()
    
    @staticmethod
    @st.cache_data(ttl=3600)
    def load_crypto_data(crypto_name: str):
        """Load cached cryptocurrency data."""
        try:
            # Try loading directly from CSV
            possible_paths = [
                DATA_DIR / f"{crypto_name}_data.csv",
                Path("data") / f"{crypto_name}_data.csv",
                Path(__file__).parent / "data" / f"{crypto_name}_data.csv",
            ]
            
            for path in possible_paths:
                path = Path(path).absolute()
                if path.exists():
                    df = pd.read_csv(path)
                    df['Date'] = pd.to_datetime(df['Date'])
                    return df
            
            return None
        except Exception as e:
            return None
    
    @staticmethod
    @st.cache_data(ttl=600)
    def get_latest_prices():
        """Get latest prices from all cryptos."""
        import requests
        import time
        import logging
        from pathlib import Path
        import pandas as pd
        
        max_retries = 3
        retry_delay = 3  # seconds
        
        for attempt in range(max_retries):
            try:
                # Fetch all prices in a single API call to avoid rate limiting
                url = "https://api.coingecko.com/api/v3/simple/price"
                params = {
                    "ids": "bitcoin,ethereum,solana,cardano,dogecoin",
                    "vs_currencies": "usd"
                }
                
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                result = response.json()
                
                prices = {}
                for crypto in ["bitcoin", "ethereum", "solana", "cardano", "dogecoin"]:
                    prices[crypto] = result.get(crypto, {}).get("usd", 0)
                
                return prices
            
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429 and attempt < max_retries - 1:
                    # Rate limited, wait and retry with exponential backoff
                    wait_time = retry_delay * (2 ** attempt)
                    logging.warning(f"Rate limited (attempt {attempt+1}/{max_retries}). Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    logging.error(f"Error fetching prices (HTTP {e.response.status_code})")
                    break
            
            except Exception as e:
                logging.error(f"Error fetching prices: {str(e)}")
                break
        
        # Fallback: Try to get last known prices from CSV files
        try:
            data_dir = Path(__file__).parent / "data"
            prices = {}
            for crypto in ["bitcoin", "ethereum", "solana", "cardano", "dogecoin"]:
                csv_file = data_dir / f"{crypto}_data.csv"
                if csv_file.exists():
                    df = pd.read_csv(csv_file)
                    if not df.empty and 'Close' in df.columns:
                        # Get the last close price from the CSV
                        prices[crypto] = float(df['Close'].iloc[-1])
                    else:
                        prices[crypto] = 0
                else:
                    prices[crypto] = 0
            return prices
        except Exception as e:
            logging.error(f"Fallback failed: {str(e)}")
            return {}



class DataFilter:
    """Filter and prepare data for visualizations."""
    
    @staticmethod
    def filter_by_date_range(df: pd.DataFrame, start_date: datetime, 
                             end_date: datetime) -> pd.DataFrame:
        """Filter dataframe by date range."""
        mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
        return df[mask].copy()
    
    @staticmethod
    def filter_by_volatility_range(metrics_df: pd.DataFrame, 
                                   min_vol: float, max_vol: float) -> pd.DataFrame:
        """Filter metrics by volatility range."""
        mask = (metrics_df['Annual_Volatility_%'] >= min_vol) & \
               (metrics_df['Annual_Volatility_%'] <= max_vol)
        return metrics_df[mask].copy()
    
    @staticmethod
    def filter_by_sharpe_range(metrics_df: pd.DataFrame, 
                               min_sharpe: float, max_sharpe: float) -> pd.DataFrame:
        """Filter metrics by Sharpe ratio range."""
        mask = (metrics_df['Sharpe_Ratio'] >= min_sharpe) & \
               (metrics_df['Sharpe_Ratio'] <= max_sharpe)
        return metrics_df[mask].copy()


class ChartBuilder:
    """Build interactive charts for the dashboard."""
    
    @staticmethod
    def create_price_chart(df: pd.DataFrame, crypto_name: str):
        """Create price trend chart."""
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            subplot_titles=(f"{crypto_name} Price", f"{crypto_name} Volume"),
            vertical_spacing=0.12,
            row_heights=[0.7, 0.3]
        )
        
        # Price line
        fig.add_trace(
            go.Scatter(x=df['Date'], y=df['Close'],
                      name='Price',
                      line=dict(color='#00d2ff', width=2),
                      mode='lines'),
            row=1, col=1
        )
        
        # Volume bar
        colors = ['green' if df['Close'].iloc[i] >= df['Close'].iloc[i-1] 
                 else 'red' for i in range(1, len(df))]
        colors.insert(0, 'gray')
        
        fig.add_trace(
            go.Bar(x=df['Date'], y=df['Volume'],
                   name='Volume',
                   marker=dict(color=colors, opacity=0.5)),
            row=2, col=1
        )
        
        fig.update_layout(
            height=600,
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,1)',
            plot_bgcolor='rgba(0,0,0,1)',
            hovermode='x unified',
            showlegend=True,
            font=dict(color='rgba(229, 230, 235, 0.95)'),
            legend=dict(bgcolor='rgba(0,0,0,0.4)', bordercolor='rgba(255,255,255,0.2)')
        )
        
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
        fig.update_yaxes(title_text="Volume (USD)", row=2, col=1)
        
        return fig
    
    @staticmethod
    def create_volatility_chart(df: pd.DataFrame, rolling_vol: pd.Series):
        """Create volatility trend chart."""
        import plotly.graph_objects as go
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=rolling_vol,
            fill='tozeroy',
            name='Rolling Volatility',
            line=dict(color='#ff6b6b'),
            hovertemplate='<b>%{x}</b><br>Volatility: %{y:.2f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title="30-Day Rolling Volatility",
            xaxis_title="Date",
            yaxis_title="Volatility (%)",
            hovermode='x unified',
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,1)',
            plot_bgcolor='rgba(0,0,0,1)',
            font=dict(color='rgba(229, 230, 235, 0.95)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.12)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.12)'),
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_risk_return_scatter(metrics_df: pd.DataFrame):
        """Create risk-return scatter plot."""
        import plotly.graph_objects as go
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=metrics_df['Annual_Volatility_%'],
            y=metrics_df['Sharpe_Ratio'],
            mode='markers+text',
            text=metrics_df['Cryptocurrency'],
            textposition="top center",
            marker=dict(
                size=12,
                color=metrics_df['Sharpe_Ratio'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Sharpe Ratio"),
                line=dict(width=2, color='white')
            ),
            hovertemplate='<b>%{text}</b><br>' +
                         'Risk (Ann. Vol): %{x:.2f}%<br>' +
                         'Return (Sharpe): %{y:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Risk-Return Profile",
            xaxis_title="Annual Volatility (%)",
            yaxis_title="Sharpe Ratio",
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,1)',
            plot_bgcolor='rgba(0,0,0,1)',
            font=dict(color='rgba(229, 230, 235, 0.95)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.12)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.12)'),
            legend=dict(bgcolor='rgba(0,0,0,0.4)', bordercolor='rgba(255,255,255,0.2)'),
            height=500,
            hovermode='closest'
        )
        
        return fig
    
    @staticmethod
    def create_comparison_chart(metrics_df: pd.DataFrame, metric_name: str):
        """Create multi-crypto comparison chart."""
        import plotly.graph_objects as go
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=metrics_df['Cryptocurrency'],
            y=metrics_df[metric_name],
            marker=dict(
                color=metrics_df[metric_name],
                colorscale='Plasma',
                showscale=True
            ),
            hovertemplate='<b>%{x}</b><br>' + f'{metric_name}: %{{y:.2f}}<extra></extra>'
        ))
        
        fig.update_layout(
            title=f"{metric_name} - Multi Crypto Comparison",
            xaxis_title="Cryptocurrency",
            yaxis_title=metric_name,
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,1)',
            plot_bgcolor='rgba(0,0,0,1)',
            font=dict(color='rgba(229, 230, 235, 0.95)'),
            legend=dict(bgcolor='rgba(0,0,0,0.4)', bordercolor='rgba(255,255,255,0.2)'),
            height=450
        )
        
        return fig


class MetricsFormatter:
    """Format metrics for display."""
    
    @staticmethod
    def format_price(value: float) -> str:
        """Format price with USD symbol."""
        return f"${value:,.2f}"
    
    @staticmethod
    def format_percentage(value: float) -> str:
        """Format percentage."""
        symbol = "+" if value >= 0 else ""
        color = "🟢" if value >= 0 else "🔴"
        return f"{color} {symbol}{value:.2f}%"
    
    @staticmethod
    def format_ratio(value: float) -> str:
        """Format ratio (Sharpe, Beta, etc)."""
        return f"{value:.2f}"
    
    @staticmethod
    def get_risk_level(volatility: float) -> str:
        """Classify risk level based on volatility."""
        if volatility < 30:
            return "🟢 Low Risk"
        elif volatility < 60:
            return "🟡 Medium Risk"
        else:
            return "🔴 High Risk"
    
    @staticmethod
    def get_quality_badge(sharpe_ratio: float) -> str:
        """Get quality badge based on Sharpe ratio."""
        if sharpe_ratio >= 1.0:
            return "⭐ Excellent"
        elif sharpe_ratio >= 0.5:
            return "⭐⭐ Good"
        elif sharpe_ratio >= 0:
            return "⭐⭐⭐ Fair"
        else:
            return "⭐⭐⭐⭐ Poor"


class DataSummary:
    """Generate summary statistics."""
    
    @staticmethod
    def get_portfolio_stats(metrics_df: pd.DataFrame) -> dict:
        """Calculate portfolio-level statistics."""
        if len(metrics_df) == 0:
            return {}
        
        return {
            "Average_Volatility": metrics_df['Annual_Volatility_%'].mean(),
            "Average_Sharpe": metrics_df['Sharpe_Ratio'].mean(),
            "Max_Volatility": metrics_df['Annual_Volatility_%'].max(),
            "Min_Volatility": metrics_df['Annual_Volatility_%'].min(),
            "Highest_Sharpe": metrics_df['Sharpe_Ratio'].max(),
            "Total_Assets": len(metrics_df)
        }
    
    @staticmethod
    def get_best_worst(metrics_df: pd.DataFrame) -> dict:
        """Get best and worst performers."""
        if len(metrics_df) == 0:
            return {}
        
        return {
            "Best_Sharpe": metrics_df.loc[metrics_df['Sharpe_Ratio'].idxmax(), 'Cryptocurrency'],
            "Worst_Sharpe": metrics_df.loc[metrics_df['Sharpe_Ratio'].idxmin(), 'Cryptocurrency'],
            "Most_Volatile": metrics_df.loc[metrics_df['Annual_Volatility_%'].idxmax(), 'Cryptocurrency'],
            "Most_Stable": metrics_df.loc[metrics_df['Annual_Volatility_%'].idxmin(), 'Cryptocurrency'],
        }


def init_session_state():
    """Initialize session state variables."""
    if "selected_crypto" not in st.session_state:
        st.session_state.selected_crypto = "bitcoin"
    
    if "date_range" not in st.session_state:
        st.session_state.date_range = (
            datetime.now() - timedelta(days=90),
            datetime.now()
        )
    
    if "metrics_df" not in st.session_state:
        st.session_state.metrics_df = CacheManager.load_metrics()


def get_crypto_emoji(crypto_name: str) -> str:
    """Get emoji for cryptocurrency."""
    emojis = {
        "bitcoin": "₿",
        "ethereum": "Ξ",
        "solana": "◎",
        "cardano": "₳",
        "dogecoin": "Ð"
    }
    return emojis.get(crypto_name.lower(), "💰")
