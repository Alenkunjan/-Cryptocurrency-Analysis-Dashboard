"""
Milestone 4 - Part 1: Risk Classification and Analysis
Categorizes cryptocurrencies based on risk metrics and thresholds.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from enum import Enum
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"


class RiskLevel(Enum):
    """Risk level classification."""
    LOW = "Low Risk"
    MEDIUM = "Medium Risk"
    HIGH = "High Risk"
    CRITICAL = "Critical Risk"


class RiskThresholds:
    """Define risk classification thresholds."""
    
    # Volatility thresholds (annual %)
    LOW_VOLATILITY = 40
    MEDIUM_VOLATILITY = 60
    HIGH_VOLATILITY = 80
    
    # Sharpe ratio thresholds (risk-adjusted return)
    EXCELLENT_SHARPE = 1.0
    GOOD_SHARPE = 0.5
    FAIR_SHARPE = 0.0
    POOR_SHARPE = -0.5
    
    # Max drawdown thresholds (%)
    LOW_DRAWDOWN = -30
    MEDIUM_DRAWDOWN = -50
    HIGH_DRAWDOWN = -70
    
    # Beta thresholds (sensitivity to BTC)
    LOW_BETA = 0.8
    HIGH_BETA = 1.3
    
    # Composite risk scores
    SAFE_SCORE = 30
    MODERATE_SCORE = 60


class RiskClassifier:
    """Classify cryptocurrencies by risk levels."""
    
    @staticmethod
    def classify_volatility(annual_volatility: float) -> Tuple[RiskLevel, str]:
        """
        Classify volatility level.
        
        Args:
            annual_volatility: Annual volatility percentage
            
        Returns:
            Tuple of (RiskLevel, description)
        """
        if annual_volatility <= RiskThresholds.LOW_VOLATILITY:
            return RiskLevel.LOW, "Stable"
        elif annual_volatility <= RiskThresholds.MEDIUM_VOLATILITY:
            return RiskLevel.MEDIUM, "Moderate"
        elif annual_volatility <= RiskThresholds.HIGH_VOLATILITY:
            return RiskLevel.HIGH, "Volatile"
        else:
            return RiskLevel.CRITICAL, "Extremely Volatile"
    
    @staticmethod
    def classify_sharpe_ratio(sharpe: float) -> Tuple[RiskLevel, str]:
        """
        Classify based on Sharpe ratio (risk-adjusted return quality).
        
        Args:
            sharpe: Sharpe ratio value
            
        Returns:
            Tuple of (RiskLevel, quality description)
        """
        if sharpe >= RiskThresholds.EXCELLENT_SHARPE:
            return RiskLevel.LOW, "Excellent Returns"
        elif sharpe >= RiskThresholds.GOOD_SHARPE:
            return RiskLevel.LOW, "Good Returns"
        elif sharpe >= RiskThresholds.FAIR_SHARPE:
            return RiskLevel.MEDIUM, "Fair Returns"
        elif sharpe >= RiskThresholds.POOR_SHARPE:
            return RiskLevel.HIGH, "Poor Returns"
        else:
            return RiskLevel.CRITICAL, "Extremely Poor Returns"
    
    @staticmethod
    def classify_drawdown(max_drawdown: float) -> Tuple[RiskLevel, str]:
        """
        Classify based on maximum drawdown.
        
        Args:
            max_drawdown: Maximum drawdown percentage (negative)
            
        Returns:
            Tuple of (RiskLevel, description)
        """
        if max_drawdown >= RiskThresholds.LOW_DRAWDOWN:
            return RiskLevel.LOW, "Manageable Downside"
        elif max_drawdown >= RiskThresholds.MEDIUM_DRAWDOWN:
            return RiskLevel.MEDIUM, "Moderate Downside"
        elif max_drawdown >= RiskThresholds.HIGH_DRAWDOWN:
            return RiskLevel.HIGH, "Significant Downside"
        else:
            return RiskLevel.CRITICAL, "Severe Downside"
    
    @staticmethod
    def classify_beta(beta: float) -> Tuple[RiskLevel, str]:
        """
        Classify based on beta coefficient (correlation with BTC).
        
        Args:
            beta: Beta coefficient
            
        Returns:
            Tuple of (RiskLevel, description)
        """
        if beta < 0 or beta == 0:
            return RiskLevel.LOW, "Not Correlated"
        elif beta <= RiskThresholds.LOW_BETA:
            return RiskLevel.LOW, "Low Correlation (Diversifier)"
        elif beta <= RiskThresholds.HIGH_BETA:
            return RiskLevel.MEDIUM, "Moderate Correlation"
        else:
            return RiskLevel.HIGH, "High Correlation"
    
    @staticmethod
    def calculate_composite_risk_score(
        volatility: float,
        sharpe: float,
        drawdown: float,
        beta: float
    ) -> float:
        """
        Calculate composite risk score (0-100).
        
        Args:
            volatility: Annual volatility (%)
            sharpe: Sharpe ratio
            drawdown: Max drawdown (%)
            beta: Beta coefficient
            
        Returns:
            Composite risk score (0-100)
        """
        # Normalize each metric to 0-100 scale
        
        # Volatility component (0-100, higher vol = higher risk)
        vol_score = min(100, (volatility / 100) * 100)
        
        # Sharpe component (lower sharpe = higher risk)
        sharpe_score = max(0, min(100, (1 - (sharpe + 2) / 4) * 100))
        
        # Drawdown component (worse drawdown = higher risk)
        drawdown_score = min(100, max(0, (abs(drawdown) / 80) * 100))
        
        # Beta component (deviation from 1 = higher risk)
        beta_score = min(100, abs(beta - 1) * 50)
        
        # Weighted composite (40% vol, 30% sharpe, 20% drawdown, 10% beta)
        composite = (
            vol_score * 0.40 +
            sharpe_score * 0.30 +
            drawdown_score * 0.20 +
            beta_score * 0.10
        )
        
        return round(composite, 2)
    
    @staticmethod
    def classify_composite_score(score: float) -> RiskLevel:
        """Classify risk level based on composite score."""
        if score <= RiskThresholds.SAFE_SCORE:
            return RiskLevel.LOW
        elif score <= RiskThresholds.MODERATE_SCORE:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH


class RiskAnalyzer:
    """Comprehensive risk analysis for a cryptocurrency."""
    
    def __init__(self, crypto_name: str, metrics_row: pd.Series):
        """
        Initialize risk analyzer.
        
        Args:
            crypto_name: Name of cryptocurrency
            metrics_row: Row from metrics DataFrame
        """
        self.crypto_name = crypto_name
        self.metrics = metrics_row
        self.classifier = RiskClassifier()
    
    def generate_risk_report(self) -> Dict:
        """
        Generate comprehensive risk report for the cryptocurrency.
        
        Returns:
            Dictionary with all risk classifications and analysis
        """
        volatility = self.metrics.get('Annual_Volatility_%', 0)
        sharpe = self.metrics.get('Sharpe_Ratio', 0)
        drawdown = self.metrics.get('Max_Drawdown_%', 0)
        beta = self.metrics.get('Beta', 0)
        price_change = self.metrics.get('Price_Change_%', 0)
        
        # Individual classifications
        vol_level, vol_desc = self.classifier.classify_volatility(volatility)
        sharpe_level, sharpe_desc = self.classifier.classify_sharpe_ratio(sharpe)
        drawdown_level, drawdown_desc = self.classifier.classify_drawdown(drawdown)
        beta_level, beta_desc = self.classifier.classify_beta(beta)
        
        # Composite score
        composite_score = self.classifier.calculate_composite_risk_score(
            volatility, sharpe, drawdown, beta
        )
        overall_risk = self.classifier.classify_composite_score(composite_score)
        
        # Risk warnings
        warnings = self._generate_warnings(volatility, sharpe, drawdown, beta, price_change)
        
        # Recommendations
        recommendations = self._generate_recommendations(overall_risk, warnings)
        
        return {
            "Cryptocurrency": self.crypto_name.capitalize(),
            "Overall_Risk_Level": overall_risk.value,
            "Composite_Risk_Score": composite_score,
            "Volatility_Level": vol_level.value,
            "Volatility_Description": vol_desc,
            "Sharpe_Level": sharpe_level.value,
            "Sharpe_Description": sharpe_desc,
            "Drawdown_Level": drawdown_level.value,
            "Drawdown_Description": drawdown_desc,
            "Beta_Level": beta_level.value,
            "Beta_Description": beta_desc,
            "Volatility_%": round(volatility, 2),
            "Sharpe_Ratio": round(sharpe, 2),
            "Max_Drawdown_%": round(drawdown, 2),
            "Beta": round(beta, 2),
            "Price_Change_%": round(price_change, 2),
            "Risk_Warnings": warnings,
            "Recommendations": recommendations,
        }
    
    def _generate_warnings(self, vol: float, sharpe: float, dd: float, beta: float, price_change: float) -> list:
        """Generate risk warnings based on thresholds."""
        warnings = []
        
        if vol > RiskThresholds.HIGH_VOLATILITY:
            warnings.append("⚠️ Extremely high volatility - high price swings expected")
        elif vol > RiskThresholds.MEDIUM_VOLATILITY:
            warnings.append("⚠️ High volatility - significant price movements likely")
        
        if sharpe < -0.5:
            warnings.append("⚠️ Negative risk-adjusted returns - not compensating for risk")
        
        if dd < -70:
            warnings.append("⚠️ Severe maximum drawdown - significant historical losses")
        elif dd < -50:
            warnings.append("⚠️ High maximum drawdown - substantial downside exposure")
        
        if beta > 1.5:
            warnings.append("⚠️ Very high beta - amplifies BTC movements")
        
        if price_change < -50:
            warnings.append("🔴 Large downtrend - significant price decline observed")
        elif price_change > 100:
            warnings.append("📈 Large uptrend - check for sustainability")
        
        return warnings if warnings else ["✓ No major warnings"]
    
    def _generate_recommendations(self, risk_level: RiskLevel, warnings: list) -> list:
        """Generate investment recommendations based on risk profile."""
        recommendations = []
        
        if risk_level == RiskLevel.LOW:
            recommendations.append("✓ Suitable for conservative investors")
            recommendations.append("✓ Consider core position allocation")
            recommendations.append("Consider dollar-cost averaging for stability")
        
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.append("⚠️ Suitable for moderate-risk investors")
            recommendations.append("⚠️ Limit position size to 5-10% of portfolio")
            recommendations.append("⚠️ Use stop-loss orders for downside protection")
            recommendations.append("Monitor price levels regularly")
        
        elif risk_level == RiskLevel.HIGH:
            recommendations.append("🔴 High-risk, speculative asset")
            recommendations.append("🔴 Limited position size (2-5% max)")
            recommendations.append("🔴 Implement strict risk management")
            recommendations.append("Only for experienced traders")
            recommendations.append("Use technical analysis for entry/exit points")
        
        else:  # CRITICAL
            recommendations.append("🔴 EXTREME RISK - Speculative only")
            recommendations.append("🔴 Minimal position size (< 2%)")
            recommendations.append("🔴 Only funds you can afford to lose")
            recommendations.append("Consider avoiding or exiting positions")
        
        return recommendations


def generate_risk_classification_report(metrics_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate risk classification for all cryptocurrencies.
    
    Args:
        metrics_df: DataFrame with cryptocurrency metrics
        
    Returns:
        DataFrame with risk classifications
    """
    risk_reports = []
    
    for idx, row in metrics_df.iterrows():
        crypto_name = row['Cryptocurrency'].lower()
        analyzer = RiskAnalyzer(crypto_name, row)
        report = analyzer.generate_risk_report()
        risk_reports.append(report)
    
    risk_df = pd.DataFrame(risk_reports)
    
    # Save report
    report_path = DATA_DIR / "risk_classification_report.csv"
    risk_df.to_csv(report_path, index=False)
    logger.info(f"✓ Risk classification report saved: {report_path}")
    
    return risk_df


def load_risk_report() -> pd.DataFrame:
    """Load existing risk classification report."""
    path = DATA_DIR / "risk_classification_report.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


if __name__ == "__main__":
    print("\n" + "="*70)
    print("MILESTONE 4 - PART 1: RISK CLASSIFICATION AND ANALYSIS")
    print("="*70 + "\n")
    
    # Load metrics
    metrics_path = DATA_DIR / "metrics_table.csv"
    if metrics_path.exists():
        metrics_df = pd.read_csv(metrics_path)
        
        # Generate risk classifications
        risk_df = generate_risk_classification_report(metrics_df)
        
        print("\nRisk Classification Summary:")
        print("="*70)
        for idx, row in risk_df.iterrows():
            print(f"\n{row['Cryptocurrency'].upper()}")
            print(f"  Overall Risk Level: {row['Overall_Risk_Level']}")
            print(f"  Composite Score: {row['Composite_Risk_Score']}/100")
            print(f"  Volatility: {row['Volatility_%']:.2f}% ({row['Volatility_Level']})")
            print(f"  Sharpe Ratio: {row['Sharpe_Ratio']:.2f} ({row['Sharpe_Level']})")
            print(f"  Max Drawdown: {row['Max_Drawdown_%']:.2f}%")
            print(f"  Beta: {row['Beta']:.2f} ({row['Beta_Level']})")
            print(f"\n  Warnings:")
            for warning in risk_df.iloc[idx]['Risk_Warnings']:
                print(f"    {warning}")
            print(f"\n  Recommendations:")
            for rec in risk_df.iloc[idx]['Recommendations']:
                print(f"    {rec}")
    else:
        print("❌ Metrics file not found. Run data_processing.py first.")
