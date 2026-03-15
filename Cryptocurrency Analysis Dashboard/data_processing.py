"""
Milestone 2: Data Processing and Calculation
This module handles financial metrics calculation for cryptocurrencies.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Data directory
DATA_DIR = Path(__file__).parent / "data"

RISK_FREE_RATE = 0.02  # 2% annual risk-free rate


class ReturnsCalculator:
    """Calculate various types of returns for price data."""
    
    @staticmethod
    def log_returns(prices: pd.Series) -> pd.Series:
        """
        Calculate log returns using natural logarithm.
        
        Formula: log_return(t) = ln(Price(t) / Price(t-1))
        
        Args:
            prices: Series of prices
            
        Returns:
            Series of log returns
        """
        log_returns = np.log(prices / prices.shift(1))
        return log_returns
    
    @staticmethod
    def simple_returns(prices: pd.Series) -> pd.Series:
        """
        Calculate simple returns.
        
        Formula: simple_return(t) = (Price(t) - Price(t-1)) / Price(t-1)
        
        Args:
            prices: Series of prices
            
        Returns:
            Series of simple returns
        """
        simple_returns = (prices - prices.shift(1)) / prices.shift(1)
        return simple_returns
    
    @staticmethod
    def cumulative_returns(prices: pd.Series) -> pd.Series:
        """
        Calculate cumulative returns from the starting price.
        
        Formula: cum_return(t) = (Price(t) - Price(0)) / Price(0)
        
        Args:
            prices: Series of prices
            
        Returns:
            Series of cumulative returns
        """
        return (prices / prices.iloc[0]) - 1


class VolatilityCalculator:
    """Calculate volatility metrics."""
    
    @staticmethod
    def daily_volatility(returns: pd.Series, window: int = 30) -> float:
        """
        Calculate daily volatility using rolling standard deviation.
        
        Args:
            returns: Series of daily returns
            window: Rolling window size (default 30 days)
            
        Returns:
            Daily volatility (standard deviation of returns)
        """
        daily_vol = returns.std()
        return daily_vol * 100  # Return as percentage
    
    @staticmethod
    def annualized_volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
        """
        Calculate annualized volatility.
        
        Formula: annualized_vol = daily_vol * sqrt(252)
        
        Args:
            returns: Series of daily returns
            periods_per_year: Trading days per year (default 252)
            
        Returns:
            Annualized volatility (%)
        """
        daily_vol = returns.std()
        annualized_vol = daily_vol * np.sqrt(periods_per_year)
        return annualized_vol * 100  # Return as percentage
    
    @staticmethod
    def rolling_volatility(returns: pd.Series, window: int = 30) -> pd.Series:
        """
        Calculate rolling volatility over time.
        
        Args:
            returns: Series of daily returns
            window: Rolling window size
            
        Returns:
            Series of rolling volatility values
        """
        rolling_vol = returns.rolling(window=window).std() * 100
        return rolling_vol


class RiskMetrics:
    """Calculate risk and return metrics."""
    
    @staticmethod
    def sharpe_ratio(returns: pd.Series, risk_free_rate: float = RISK_FREE_RATE, 
                     periods_per_year: int = 252) -> float:
        """
        Calculate Sharpe Ratio.
        
        Formula: Sharpe = (Mean Return - Risk Free Rate) / Volatility
        
        Args:
            returns: Series of daily returns
            risk_free_rate: Annual risk-free rate (default 2%)
            periods_per_year: Trading days per year
            
        Returns:
            Sharpe Ratio value
        """
        excess_return = (returns.mean() * periods_per_year) - risk_free_rate
        volatility = returns.std() * np.sqrt(periods_per_year)
        
        if volatility == 0:
            return 0
        
        sharpe = excess_return / volatility
        return sharpe
    
    @staticmethod
    def beta_coefficient(asset_returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """
        Calculate Beta coefficient vs a benchmark.
        
        Formula: Beta = Covariance(Asset, Benchmark) / Variance(Benchmark)
        
        Args:
            asset_returns: Series of asset returns
            benchmark_returns: Series of benchmark returns
            
        Returns:
            Beta coefficient
        """
        # Align series and remove NaN values
        aligned_data = pd.DataFrame({
            'asset': asset_returns,
            'benchmark': benchmark_returns
        }).dropna()
        
        if len(aligned_data) < 2:
            return 0
        
        covariance = aligned_data['asset'].cov(aligned_data['benchmark'])
        variance = aligned_data['benchmark'].var()
        
        if variance == 0:
            return 0
        
        beta = covariance / variance
        return beta
    
    @staticmethod
    def max_drawdown(returns: pd.Series) -> float:
        """
        Calculate maximum drawdown.
        
        Formula: Max Drawdown = (Trough - Peak) / Peak
        
        Args:
            returns: Series of returns
            
        Returns:
            Maximum drawdown (%)
        """
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_dd = drawdown.min()
        return max_dd * 100  # Return as percentage
    
    @staticmethod
    def sortino_ratio(returns: pd.Series, risk_free_rate: float = RISK_FREE_RATE,
                     periods_per_year: int = 252) -> float:
        """
        Calculate Sortino Ratio (considers only downside volatility).
        
        Args:
            returns: Series of daily returns
            risk_free_rate: Annual risk-free rate
            periods_per_year: Trading days per year
            
        Returns:
            Sortino Ratio value
        """
        excess_return = (returns.mean() * periods_per_year) - risk_free_rate
        downside_returns = returns[returns < 0]
        downside_volatility = downside_returns.std() * np.sqrt(periods_per_year)
        
        if downside_volatility == 0:
            return 0
        
        sortino = excess_return / downside_volatility
        return sortino


class MetricsCalculator:
    """Main class to calculate all metrics for a cryptocurrency."""
    
    def __init__(self, df: pd.DataFrame, crypto_name: str):
        """
        Initialize metrics calculator.
        
        Args:
            df: DataFrame with OHLCV data
            crypto_name: Name of cryptocurrency
        """
        self.df = df.copy()
        self.crypto_name = crypto_name
        self.metrics = {}
    
    def calculate_all_metrics(self, benchmark_returns: pd.Series = None) -> dict:
        """
        Calculate all metrics for the cryptocurrency.
        
        Args:
            benchmark_returns: Returns of benchmark (e.g., BTC) for beta calculation
            
        Returns:
            Dictionary with all calculated metrics
        """
        # Calculate returns
        returns = ReturnsCalculator.log_returns(self.df['Close'].dropna())
        returns = returns.dropna()
        
        if len(returns) == 0:
            logger.warning(f"No valid returns for {self.crypto_name}")
            return None
        
        # Volatility metrics
        daily_vol = VolatilityCalculator.daily_volatility(returns)
        annual_vol = VolatilityCalculator.annualized_volatility(returns)
        
        # Risk metrics
        sharpe = RiskMetrics.sharpe_ratio(returns)
        max_dd = RiskMetrics.max_drawdown(returns)
        sortino = RiskMetrics.sortino_ratio(returns)
        
        # Beta calculation
        beta = 0.0
        if benchmark_returns is not None:
            beta = RiskMetrics.beta_coefficient(returns, benchmark_returns)
        
        # Price metrics
        price_change = ((self.df['Close'].iloc[-1] - self.df['Close'].iloc[0]) / 
                        self.df['Close'].iloc[0]) * 100
        current_price = self.df['Close'].iloc[-1]
        
        self.metrics = {
            "Cryptocurrency": self.crypto_name,
            "Current_Price": round(current_price, 2),
            "Price_Change_%": round(price_change, 2),
            "Daily_Volatility_%": round(daily_vol, 2),
            "Annual_Volatility_%": round(annual_vol, 2),
            "Sharpe_Ratio": round(sharpe, 2),
            "Sortino_Ratio": round(sortino, 2),
            "Max_Drawdown_%": round(max_dd, 2),
            "Beta": round(beta, 2),
            "Data_Points": len(self.df),
            "Date_Range": f"{self.df['Date'].min()} to {self.df['Date'].max()}"
        }
        
        return self.metrics
    
    def get_metrics_dataframe(self) -> pd.DataFrame:
        """Return metrics as a single-row DataFrame."""
        return pd.DataFrame([self.metrics])


def calculate_metrics_for_all(cryptos: list = None) -> pd.DataFrame:
    """
    Calculate metrics for all cryptocurrencies.
    
    Args:
        cryptos: List of cryptocurrency names
        
    Returns:
        DataFrame with metrics for all cryptos
    """
    if cryptos is None:
        cryptos = ["bitcoin", "ethereum", "solana", "cardano", "dogecoin"]
    
    from data_acquisition import DataStorage
    
    storage = DataStorage()
    all_metrics = []
    benchmark_returns = None
    
    # First pass: get benchmark (BTC)
    btc_df = storage.load_from_csv("bitcoin")
    if btc_df is not None:
        benchmark_returns = ReturnsCalculator.log_returns(btc_df['Close'].dropna()).dropna()
    
    # Calculate metrics for each crypto
    for crypto in cryptos:
        logger.info(f"Calculating metrics for {crypto}...")
        
        df = storage.load_from_csv(crypto)
        if df is None:
            logger.warning(f"Could not load data for {crypto}")
            continue
        
        calc = MetricsCalculator(df, crypto.capitalize())
        
        # Pass benchmark returns for beta calculation
        if crypto != "bitcoin":
            calc.calculate_all_metrics(benchmark_returns)
        else:
            calc.calculate_all_metrics()
        
        all_metrics.append(calc.metrics)
    
    # Convert to DataFrame
    metrics_df = pd.DataFrame(all_metrics)
    
    # Save metrics
    metrics_path = DATA_DIR / "metrics_table.csv"
    metrics_df.to_csv(metrics_path, index=False)
    logger.info(f"✓ Metrics saved to {metrics_path}")
    
    return metrics_df


def get_rolling_metrics(crypto: str, window: int = 30) -> pd.DataFrame:
    """
    Calculate rolling metrics for a cryptocurrency.
    
    Args:
        crypto: Cryptocurrency name
        window: Rolling window size
        
    Returns:
        DataFrame with rolling metrics
    """
    from data_acquisition import DataStorage
    
    storage = DataStorage()
    df = storage.load_from_csv(crypto)
    
    if df is None:
        return None
    
    returns = ReturnsCalculator.log_returns(df['Close'].dropna()).dropna()
    
    rolling_metrics = pd.DataFrame({
        'Date': df['Date'][len(df) - len(returns):].reset_index(drop=True),
        'Price': df['Close'][len(df) - len(returns):].reset_index(drop=True),
        'Rolling_Volatility': VolatilityCalculator.rolling_volatility(returns, window),
        'Rolling_Return': returns.rolling(window=window).sum() * 100
    })
    
    return rolling_metrics


if __name__ == "__main__":
    print("\n" + "="*60)
    print("MILESTONE 2: DATA PROCESSING AND CALCULATION")
    print("="*60 + "\n")
    
    metrics_df = calculate_metrics_for_all()
    
    print("\nMetrics Summary:")
    print(metrics_df.to_string())
