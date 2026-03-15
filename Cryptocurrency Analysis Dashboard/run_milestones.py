"""
QUICK START EXECUTION GUIDE
Run this script to execute all milestones in sequence
"""

import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def run_milestone(script_name, description):
    """Run a milestone script."""
    print_header(description)
    script_path = PROJECT_DIR / script_name
    
    if not script_path.exists():
        print(f"❌ Error: {script_name} not found!")
        return False
    
    try:
        print(f"Running: {script_path}")
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(PROJECT_DIR),
            capture_output=False
        )
        
        if result.returncode == 0:
            print(f"\n✓ {description} completed successfully!")
            return True
        else:
            print(f"\n❌ {description} failed!")
            return False
    except Exception as e:
        print(f"❌ Error running {script_name}: {str(e)}")
        return False

if __name__ == "__main__":
    print_header("CRYPTOCURRENCY ANALYSIS DASHBOARD - EXECUTION GUIDE")
    
    print("This script will execute all project milestones:\n")
    print("1. Milestone 1: Data Acquisition (fetch & store)")
    print("2. Milestone 2: Data Processing (calculate metrics)")
    print("3. Milestone 3: Dashboard (interactive visualizations)")
    print("\n⚠️  This process may take several minutes on first run.")
    print("🔗 Ensure you have internet connection for API calls.\n")
    
    input("Press ENTER to start, or Ctrl+C to cancel...\n")
    
    # Milestone 1
    success_m1 = run_milestone(
        "data_acquisition.py",
        "MILESTONE 1: Data Acquisition & Setup"
    )
    
    if not success_m1:
        print("\n❌ Milestone 1 failed. Cannot proceed.")
        sys.exit(1)
    
    # Milestone 2
    success_m2 = run_milestone(
        "data_processing.py",
        "MILESTONE 2: Data Processing & Calculation"
    )
    
    if not success_m2:
        print("\n⚠️  Milestone 2 had issues, but you can continue to dashboard.")
    
    # Summary
    print_header("EXECUTION SUMMARY")
    print(f"✓ Milestone 1 (Data Acquisition):     {'COMPLETED' if success_m1 else 'FAILED'}")
    print(f"✓ Milestone 2 (Data Processing):      {'COMPLETED' if success_m2 else 'FAILED'}")
    print(f"\nNext Step: Start the dashboard with:")
    print(f"    streamlit run app.py")
    print(f"\nDefault Login:")
    print(f"    Username: admin")
    print(f"    Password: 1234")
    print(f"\nThen navigate to the Dashboard page.\n")
