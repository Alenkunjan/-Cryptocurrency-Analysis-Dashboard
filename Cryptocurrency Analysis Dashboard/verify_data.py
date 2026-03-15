"""
Dashboard Data Verification Script
Checks if all data loads correctly before starting the app
"""

import sys
import pandas as pd
from pathlib import Path

print("=" * 70)
print("DASHBOARD DATA VERIFICATION")
print("=" * 70)

PROJECT_ROOT = Path(__file__).parent.absolute()
DATA_DIR = PROJECT_ROOT / "data"

# Check 1: Verify data files exist
print("\n✓ Checking data files...")
required_files = [
    "bitcoin_data.csv",
    "ethereum_data.csv", 
    "solana_data.csv",
    "cardano_data.csv",
    "dogecoin_data.csv",
    "metrics_table.csv"
]

all_exist = True
for file in required_files:
    filepath = DATA_DIR / file
    exists = filepath.exists()
    status = "✓" if exists else "✗"
    size = f"({filepath.stat().st_size} bytes)" if exists else ""
    print(f"  {status} {file:<25} {size}")
    if not exists:
        all_exist = False

if not all_exist:
    print("\n✗ ERROR: Some data files are missing!")
    sys.exit(1)

# Check 2: Load and verify metrics
print("\n✓ Loading metrics table...")
try:
    metrics_df = pd.read_csv(DATA_DIR / "metrics_table.csv")
    print(f"  ✓ Metrics loaded: {len(metrics_df)} cryptocurrencies")
    print(f"\n  Cryptocurrencies:")
    for _, row in metrics_df.iterrows():
        crypto = row['Cryptocurrency']
        price = row.get('Current_Price', 0)
        vol = row.get('Annual_Volatility_%', 0)
        sharpe = row.get('Sharpe_Ratio', 0)
        print(f"    • {crypto:<12} Price: ${price:>10.2f}  Vol: {vol:>6.2f}%  Sharpe: {sharpe:>6.2f}")
except Exception as e:
    print(f"  ✗ Error loading metrics: {str(e)}")
    sys.exit(1)

# Check 3: Load sample cryptocurrency data
print("\n✓ Loading cryptocurrency data...")
try:
    btc_df = pd.read_csv(DATA_DIR / "bitcoin_data.csv")
    print(f"  ✓ Bitcoin data: {len(btc_df)} records")
    print(f"    Date range: {btc_df['Date'].min()} to {btc_df['Date'].max()}")
except Exception as e:
    print(f"  ✗ Error loading crypto data: {str(e)}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✓ ALL CHECKS PASSED - Dashboard ready to start!")
print("=" * 70)
print("\nNext step: Run the dashboard with:")
print("  streamlit run app.py")
print()
