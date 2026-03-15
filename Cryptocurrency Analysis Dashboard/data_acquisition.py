"""
Milestone 1: Data Acquisition and Setup
This module handles fetching crypto price data from APIs and storing it locally.
"""

import os
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data storage paths
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

CRYPTOS = ["bitcoin", "ethereum", "solana", "cardano", "dogecoin"]
CRYPTO_IDS = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
    "cardano": "ADA",
    "dogecoin": "DOGE"
}


class CryptoDataFetcher:
    """Fetch and store cryptocurrency data from CoinGecko and Binance APIs."""
    
    def __init__(self):
        self.coingecko_url = "https://api.coingecko.com/api/v3"
        self.binance_url = "https://api.binance.com/api/v3"
        
    def fetch_historical_data(self, crypto_id: str, days: int = 365) -> pd.DataFrame:
        """
        Fetch historical price data from CoinGecko API.
        
        Args:
            crypto_id: Cryptocurrency ID (e.g., 'bitcoin')
            days: Number of days of historical data (default: 365)
            
        Returns:
            DataFrame with columns: Date, Open, High, Low, Close, Volume
        """
        try:
            logger.info(f"Fetching {days}-day data for {crypto_id}...")
            
            url = f"{self.coingecko_url}/coins/{crypto_id}/market_chart"
            params = {
                "vs_currency": "usd",
                "days": days,
                "interval": "daily"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extract prices and volumes
            prices = data.get("prices", [])
            volumes = data.get("total_volumes", [])
            
            if not prices:
                logger.warning(f"No data returned for {crypto_id}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame({
                "Date": [datetime.fromtimestamp(p[0]/1000) for p in prices],
                "Close": [p[1] for p in prices],
                "Volume": [v[1] if v else 0 for v in volumes]
            })
            
            df["Date"] = pd.to_datetime(df["Date"]).dt.date
            df = df.sort_values("Date").reset_index(drop=True)
            
            # Calculate OHLC using Close prices (simplified - use rolling)
            df["Open"] = df["Close"].fillna(method="ffill")
            df["High"] = df["Close"].rolling(window=1).max()
            df["Low"] = df["Close"].rolling(window=1).min()
            
            logger.info(f"✓ Successfully fetched {len(df)} records for {crypto_id}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {crypto_id}: {str(e)}")
            return None
    
    def fetch_current_price(self, crypto_id: str) -> dict:
        """
        Fetch current price and market data from CoinGecko.
        
        Args:
            crypto_id: Cryptocurrency ID
            
        Returns:
            Dictionary with current price and market metrics
        """
        try:
            url = f"{self.coingecko_url}/simple/price"
            params = {
                "ids": crypto_id,
                "vs_currencies": "usd",
                "include_market_cap": "true",
                "include_24hr_vol": "true",
                "include_24hr_change": "true"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json().get(crypto_id, {})
            
        except Exception as e:
            logger.error(f"Error fetching current price for {crypto_id}: {str(e)}")
            return {}
    
    def fetch_binance_24h_data(self, symbol: str) -> dict:
        """
        Fetch 24-hour statistics from Binance.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            
        Returns:
            Dictionary with 24h stats
        """
        try:
            url = f"{self.binance_url}/ticker/24hr"
            params = {"symbol": symbol}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching Binance data for {symbol}: {str(e)}")
            return {}


class DataStorage:
    """Handle saving and loading cryptocurrency data."""
    
    @staticmethod
    def save_to_csv(df: pd.DataFrame, crypto_id: str) -> bool:
        """Save DataFrame to CSV format."""
        try:
            filepath = DATA_DIR / f"{crypto_id}_data.csv"
            df.to_csv(filepath, index=False)
            logger.info(f"✓ Saved {crypto_id} data to CSV: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving CSV for {crypto_id}: {str(e)}")
            return False
    
    @staticmethod
    def save_to_parquet(df: pd.DataFrame, crypto_id: str) -> bool:
        """Save DataFrame to Parquet format."""
        try:
            filepath = DATA_DIR / f"{crypto_id}_data.parquet"
            df.to_parquet(filepath, index=False)
            logger.info(f"✓ Saved {crypto_id} data to Parquet: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving Parquet for {crypto_id}: {str(e)}")
            return False
    
    @staticmethod
    def load_from_csv(crypto_id: str) -> pd.DataFrame:
        """Load DataFrame from CSV format."""
        try:
            filepath = DATA_DIR / f"{crypto_id}_data.csv"
            if filepath.exists():
                df = pd.read_csv(filepath)
                df["Date"] = pd.to_datetime(df["Date"])
                logger.info(f"✓ Loaded {crypto_id} from CSV")
                return df
            return None
        except Exception as e:
            logger.error(f"Error loading CSV for {crypto_id}: {str(e)}")
            return None
    
    @staticmethod
    def load_from_parquet(crypto_id: str) -> pd.DataFrame:
        """Load DataFrame from Parquet format."""
        try:
            filepath = DATA_DIR / f"{crypto_id}_data.parquet"
            if filepath.exists():
                df = pd.read_parquet(filepath)
                logger.info(f"✓ Loaded {crypto_id} from Parquet")
                return df
            return None
        except Exception as e:
            logger.error(f"Error loading Parquet for {crypto_id}: {str(e)}")
            return None


class DataPreprocessor:
    """Handle data preprocessing and cleaning."""
    
    @staticmethod
    def handle_missing_values(df: pd.DataFrame, method: str = "ffill") -> pd.DataFrame:
        """
        Handle missing values in the dataset.
        
        Args:
            df: Input DataFrame
            method: 'ffill' (forward fill), 'bfill' (backward fill), or 'interpolate'
            
        Returns:
            DataFrame with missing values handled
        """
        df = df.copy()
        
        if method == "ffill":
            df = df.fillna(method="ffill").fillna(method="bfill")
        elif method == "bfill":
            df = df.fillna(method="bfill").fillna(method="ffill")
        elif method == "interpolate":
            df = df.interpolate(method="linear")
        
        logger.info(f"Missing values handled using method: {method}")
        return df
    
    @staticmethod
    def format_timeseries(df: pd.DataFrame) -> pd.DataFrame:
        """
        Format data for time-series analysis.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Properly formatted DataFrame
        """
        df = df.copy()
        
        # Ensure Date column is datetime
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
        
        # Sort by date
        df = df.sort_values("Date").reset_index(drop=True)
        
        # Ensure no duplicates
        df = df.drop_duplicates(subset=["Date"])
        
        # Create additional datetime features
        df["Year"] = df["Date"].dt.year
        df["Month"] = df["Date"].dt.month
        df["Quarter"] = df["Date"].dt.quarter
        df["DayOfWeek"] = df["Date"].dt.dayofweek
        
        logger.info("Time-series formatting completed")
        return df
    
    @staticmethod
    def validate_data_consistency(df: pd.DataFrame) -> bool:
        """
        Validate data consistency and quality.
        
        Args:
            df: Input DataFrame
            
        Returns:
            True if data is valid, False otherwise
        """
        checks = {
            "Empty DataFrame": len(df) > 0,
            "Date column exists": "Date" in df.columns,
            "Close price column": "Close" in df.columns,
            "No infinite values": not np.isinf(df.select_dtypes(include=[np.number])).any().any(),
            "Positive prices": (df["Close"] > 0).all(),
        }
        
        all_valid = all(checks.values())
        
        for check_name, result in checks.items():
            status = "✓" if result else "✗"
            logger.info(f"{status} {check_name}")
        
        return all_valid


def fetch_and_store_all_cryptos(days: int = 365) -> dict:
    """
    Main function to fetch and store data for all cryptocurrencies.
    
    Args:
        days: Number of days of historical data
        
    Returns:
        Dictionary with results for each cryptocurrency
    """
    fetcher = CryptoDataFetcher()
    storage = DataStorage()
    preprocessor = DataPreprocessor()
    
    results = {}
    
    for crypto in CRYPTOS:
        logger.info(f"\n{'='*50}")
        logger.info(f"Processing: {crypto.upper()}")
        logger.info(f"{'='*50}")
        
        # Fetch data
        df = fetcher.fetch_historical_data(crypto, days)
        
        if df is None:
            results[crypto] = {"status": "FAILED", "error": "API fetch failed"}
            continue
        
        # Preprocess
        df = preprocessor.handle_missing_values(df)
        df = preprocessor.format_timeseries(df)
        
        # Validate
        is_valid = preprocessor.validate_data_consistency(df)
        
        if not is_valid:
            results[crypto] = {"status": "FAILED", "error": "Data validation failed"}
            continue
        
        # Store
        csv_ok = storage.save_to_csv(df, crypto)
        parquet_ok = storage.save_to_parquet(df, crypto)
        
        results[crypto] = {
            "status": "SUCCESS",
            "records": len(df),
            "date_range": f"{df['Date'].min()} to {df['Date'].max()}",
            "csv_saved": csv_ok,
            "parquet_saved": parquet_ok
        }
    
    return results


if __name__ == "__main__":
    # Run data acquisition
    print("\n" + "="*60)
    print("MILESTONE 1: DATA ACQUISITION AND SETUP")
    print("="*60 + "\n")
    
    results = fetch_and_store_all_cryptos(days=365)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for crypto, result in results.items():
        print(f"\n{crypto.upper()}:")
        for key, value in result.items():
            print(f"  {key}: {value}")
