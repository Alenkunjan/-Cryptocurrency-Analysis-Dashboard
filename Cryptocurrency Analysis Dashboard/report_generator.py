"""
Milestone 4 - Part 2: Report Generation
Generates comprehensive reports in CSV, HTML, and image formats.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import kaleido
except ImportError:
    pass

logger = logging.getLogger(__name__)
DATA_DIR = Path(__file__).parent / "data"
REPORTS_DIR = Path(__file__).parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


class ReportGenerator:
    """Generate comprehensive reports for cryptocurrency analysis."""
    
    def __init__(self, metrics_df: pd.DataFrame, risk_df: pd.DataFrame = None):
        """
        Initialize report generator.
        
        Args:
            metrics_df: DataFrame with cryptocurrency metrics
            risk_df: DataFrame with risk classifications
        """
        self.metrics_df = metrics_df
        self.risk_df = risk_df
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.date_str = datetime.now().strftime("%Y%m%d")
    
    def generate_summary_csv(self) -> str:
        """
        Generate summary report as CSV.
        
        Returns:
            Path to generated CSV file
        """
        output_path = REPORTS_DIR / f"crypto_analysis_summary_{self.date_str}.csv"
        
        # Combine metrics and risk data
        if self.risk_df is not None and len(self.risk_df) > 0:
            combined_df = pd.merge(
                self.metrics_df,
                self.risk_df[['Cryptocurrency', 'Overall_Risk_Level', 'Composite_Risk_Score']],
                left_on='Cryptocurrency',
                right_on='Cryptocurrency',
                how='left'
            )
        else:
            combined_df = self.metrics_df
        
        combined_df.to_csv(output_path, index=False)
        logger.info(f"✓ Summary CSV saved: {output_path}")
        return str(output_path)
    
    def generate_detailed_csv(self) -> str:
        """
        Generate detailed report with risk classifications as CSV.
        
        Returns:
            Path to generated CSV file
        """
        if self.risk_df is None or len(self.risk_df) == 0:
            return None
        
        output_path = REPORTS_DIR / f"crypto_detailed_report_{self.date_str}.csv"
        self.risk_df.to_csv(output_path, index=False)
        logger.info(f"✓ Detailed CSV saved: {output_path}")
        return str(output_path)
    
    def generate_html_report(self) -> str:
        """
        Generate comprehensive HTML report.
        
        Returns:
            Path to generated HTML file
        """
        output_path = REPORTS_DIR / f"crypto_report_{self.date_str}.html"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Cryptocurrency Analysis Report</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }}
                body {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 20px;
                    color: #333;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px;
                    text-align: center;
                }}
                .header h1 {{
                    font-size: 2.5em;
                    margin-bottom: 10px;
                }}
                .header p {{
                    font-size: 1.1em;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 40px;
                }}
                .section {{
                    margin-bottom: 40px;
                }}
                .section h2 {{
                    color: #667eea;
                    border-bottom: 2px solid #667eea;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                    font-size: 1.8em;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th {{
                    background-color: #667eea;
                    color: white;
                    padding: 12px;
                    text-align: left;
                }}
                td {{
                    padding: 10px 12px;
                    border-bottom: 1px solid #ddd;
                }}
                tr:hover {{
                    background-color: #f5f5f5;
                }}
                .low-risk {{ color: #28a745; }}
                .medium-risk {{ color: #ffc107; }}
                .high-risk {{ color: #dc3545; }}
                .critical-risk {{ color: #721c24; font-weight: bold; }}
                .metric {{
                    display: inline-block;
                    background: #f8f9fa;
                    padding: 15px;
                    margin: 10px;
                    border-radius: 5px;
                    border-left: 4px solid #667eea;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    border-top: 1px solid #ddd;
                    color: #666;
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Cryptocurrency Analysis Report</h1>
                    <p>Comprehensive Risk Assessment & Performance Analysis</p>
                    <p>Generated: {self.timestamp}</p>
                </div>
                
                <div class="content">
                    {self._generate_summary_section()}
                    {self._generate_metrics_section()}
                    {self._generate_risk_section()}
                    {self._generate_recommendations_section()}
                </div>
                
                <div class="footer">
                    <p>⚠️ This report is for educational purposes only. Not financial advice.</p>
                    <p>Data Source: CoinGecko API | Generated: {self.timestamp}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"✓ HTML report saved: {output_path}")
        return str(output_path)
    
    def _generate_summary_section(self) -> str:
        """Generate summary statistics section."""
        total_assets = len(self.metrics_df)
        avg_vol = self.metrics_df['Annual_Volatility_%'].mean()
        avg_sharpe = self.metrics_df['Sharpe_Ratio'].mean()
        
        return f"""
        <div class="section">
            <h2>📈 Portfolio Summary</h2>
            <div class="metric">
                <strong>Total Assets:</strong> {total_assets}
            </div>
            <div class="metric">
                <strong>Avg Annual Volatility:</strong> {avg_vol:.2f}%
            </div>
            <div class="metric">
                <strong>Avg Sharpe Ratio:</strong> {avg_sharpe:.2f}
            </div>
        </div>
        """
    
    def _generate_metrics_section(self) -> str:
        """Generate metrics table section."""
        html = "<div class='section'><h2>💹 Performance Metrics</h2>"
        html += "<table>"
        html += "<tr><th>Cryptocurrency</th><th>Price</th><th>Change %</th><th>Volatility %</th><th>Sharpe</th><th>Beta</th></tr>"
        
        for _, row in self.metrics_df.iterrows():
            html += f"""
            <tr>
                <td><strong>{row['Cryptocurrency']}</strong></td>
                <td>${row['Current_Price']:.2f}</td>
                <td>{row['Price_Change_%']:.2f}%</td>
                <td>{row['Annual_Volatility_%']:.2f}%</td>
                <td>{row['Sharpe_Ratio']:.2f}</td>
                <td>{row['Beta']:.2f}</td>
            </tr>
            """
        
        html += "</table></div>"
        return html
    
    def _generate_risk_section(self) -> str:
        """Generate risk classification section."""
        if self.risk_df is None or len(self.risk_df) == 0:
            return ""
        
        html = "<div class='section'><h2>🛡️ Risk Assessment</h2>"
        html += "<table>"
        html += "<tr><th>Cryptocurrency</th><th>Risk Level</th><th>Score</th><th>Volatility Level</th></tr>"
        
        for _, row in self.risk_df.iterrows():
            risk_class = f"low-risk" if "Low" in row['Overall_Risk_Level'] else \
                        f"medium-risk" if "Medium" in row['Overall_Risk_Level'] else \
                        f"high-risk" if "High" in row['Overall_Risk_Level'] else "critical-risk"
            
            html += f"""
            <tr>
                <td><strong>{row['Cryptocurrency']}</strong></td>
                <td class="{risk_class}"><strong>{row['Overall_Risk_Level']}</strong></td>
                <td>{row['Composite_Risk_Score']:.0f}/100</td>
                <td>{row['Volatility_Level']}</td>
            </tr>
            """
        
        html += "</table></div>"
        return html
    
    def _generate_recommendations_section(self) -> str:
        """Generate recommendations section."""
        if self.risk_df is None or len(self.risk_df) == 0:
            return ""
        
        html = "<div class='section'><h2>💡 Investment Recommendations</h2>"
        
        for _, row in self.risk_df.iterrows():
            html += f"<div><h3>{row['Cryptocurrency']}</h3>"
            
            if pd.notna(row.get('Recommendations')):
                recs = row['Recommendations']
                if isinstance(recs, str):
                    # Parse recommendations if they're stored as string
                    html += "<ul>"
                    for rec in recs.split(';'):
                        html += f"<li>{rec.strip()}</li>"
                    html += "</ul>"
            
            html += "</div>"
        
        html += "</div>"
        return html
    
    def generate_comparison_chart_image(self) -> str:
        """
        Generate comparison chart as image (PNG).
        
        Returns:
            Path to generated image file
        """
        try:
            output_path = REPORTS_DIR / f"crypto_comparison_{self.date_str}.png"
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=("Annual Volatility %", "Sharpe Ratio", 
                               "Price Change %", "Max Drawdown %"),
                specs=[[{"type": "bar"}, {"type": "bar"}],
                       [{"type": "bar"}, {"type": "bar"}]]
            )
            
            cryptos = self.metrics_df['Cryptocurrency'].tolist()
            
            # Volatility
            fig.add_trace(
                go.Bar(x=cryptos, y=self.metrics_df['Annual_Volatility_%'],
                      name='Volatility', marker_color='#FF6B6B'),
                row=1, col=1
            )
            
            # Sharpe
            fig.add_trace(
                go.Bar(x=cryptos, y=self.metrics_df['Sharpe_Ratio'],
                      name='Sharpe', marker_color='#4ECDC4'),
                row=1, col=2
            )
            
            # Price Change
            fig.add_trace(
                go.Bar(x=cryptos, y=self.metrics_df['Price_Change_%'],
                      name='Price Change', marker_color='#95E1D3'),
                row=2, col=1
            )
            
            # Max Drawdown
            fig.add_trace(
                go.Bar(x=cryptos, y=self.metrics_df['Max_Drawdown_%'],
                      name='Max Drawdown', marker_color='#F38181'),
                row=2, col=2
            )
            
            fig.update_layout(
                height=800,
                title_text=f"Cryptocurrency Metrics Comparison - {self.timestamp}",
                showlegend=False,
                template='plotly_white'
            )
            
            fig.write_image(str(output_path))
            logger.info(f"✓ Comparison chart saved: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.warning(f"Could not generate image report: {str(e)}")
            return None
    
    def generate_risk_gauge_chart(self) -> str:
        """
        Generate risk gauge charts as image.
        
        Returns:
            Path to generated image file
        """
        try:
            if self.risk_df is None or len(self.risk_df) == 0:
                return None
            
            output_path = REPORTS_DIR / f"crypto_risk_gauges_{self.date_str}.png"
            
            # Create subplots for each crypto
            num_cryptos = len(self.risk_df)
            cols = min(3, num_cryptos)
            rows = (num_cryptos + cols - 1) // cols
            
            fig = make_subplots(
                rows=rows, cols=cols,
                subplot_titles=[row['Cryptocurrency'] for _, row in self.risk_df.iterrows()],
                specs=[[{"type": "indicator"}] * cols] * rows
            )
            
            for idx, (_, row) in enumerate(self.risk_df.iterrows()):
                r = (idx // cols) + 1
                c = (idx % cols) + 1
                
                score = row['Composite_Risk_Score']
                
                fig.add_trace(
                    go.Indicator(
                        mode="gauge+number",
                        value=score,
                        title={'text': f"Risk Score"},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': 'darkblue'},
                            'steps': [
                                {'range': [0, 30], 'color': "#90EE90"},
                                {'range': [30, 60], 'color': "#FFD700"},
                                {'range': [60, 100], 'color': "#FF6B6B"}
                            ],
                            'threshold': {
                                'line': {'color': 'red', 'width': 4},
                                'thickness': 0.75,
                                'value': 80
                            }
                        }
                    ),
                    row=r, col=c
                )
            
            fig.update_layout(
                height=300 * rows,
                title_text=f"Risk Assessment Gauges - {self.timestamp}",
                template='plotly_white'
            )
            
            fig.write_image(str(output_path))
            logger.info(f"✓ Risk gauge chart saved: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.warning(f"Could not generate risk gauge chart: {str(e)}")
            return None


def generate_all_reports(metrics_df: pd.DataFrame, risk_df: pd.DataFrame = None):
    """
    Generate all report types.
    
    Args:
        metrics_df: DataFrame with cryptocurrency metrics
        risk_df: DataFrame with risk classifications
        
    Returns:
        Dictionary with paths to generated reports
    """
    generator = ReportGenerator(metrics_df, risk_df)
    
    reports = {
        "summary_csv": generator.generate_summary_csv(),
        "detailed_csv": generator.generate_detailed_csv(),
        "html_report": generator.generate_html_report(),
        "comparison_chart": generator.generate_comparison_chart_image(),
        "risk_gauges": generator.generate_risk_gauge_chart(),
    }
    
    return reports


if __name__ == "__main__":
    print("\n" + "="*70)
    print("MILESTONE 4 - PART 2: REPORT GENERATION")
    print("="*70 + "\n")
    
    # Load data
    metrics_path = DATA_DIR / "metrics_table.csv"
    risk_path = DATA_DIR / "risk_classification_report.csv"
    
    if metrics_path.exists():
        metrics_df = pd.read_csv(metrics_path)
        risk_df = pd.read_csv(risk_path) if risk_path.exists() else None
        
        # Generate reports
        reports = generate_all_reports(metrics_df, risk_df)
        
        print("\nGenerated Reports:")
        print("="*70)
        for report_type, filepath in reports.items():
            if filepath:
                print(f"✓ {report_type:<20}: {filepath}")
            else:
                print(f"✗ {report_type:<20}: Failed to generate")
    else:
        print("❌ Metrics file not found. Run data_processing.py first.")
