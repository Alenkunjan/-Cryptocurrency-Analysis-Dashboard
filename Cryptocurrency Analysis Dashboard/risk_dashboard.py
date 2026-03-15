"""
Milestone 4 - Dashboard Risk Visualization
Provides visual components for risk classification in the dashboard.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from risk_classification import RiskLevel


class RiskVisualizer:
    """Create visual representations of risk levels."""
    
    @staticmethod
    def get_risk_color(risk_level: str) -> str:
        """Get color for risk level."""
        if "Low" in risk_level:
            return "#27AE60"  # Green
        elif "Medium" in risk_level:
            return "#F39C12"  # Orange
        elif "High" in risk_level:
            return "#E74C3C"  # Red
        else:
            return "#8B0000"  # Dark Red
    
    @staticmethod
    def get_risk_emoji(risk_level: str) -> str:
        """Get emoji for risk level."""
        if "Low" in risk_level:
            return "🟢"
        elif "Medium" in risk_level:
            return "🟡"
        elif "High" in risk_level:
            return "🔴"
        else:
            return "🔴"
    
    @staticmethod
    def create_risk_gauge(crypto_name: str, risk_score: float, risk_level: str) -> go.Figure:
        """
        Create risk gauge chart.
        
        Args:
            crypto_name: Name of cryptocurrency
            risk_score: Risk score (0-100)
            risk_level: Risk level string
            
        Returns:
            Plotly figure
        """
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=risk_score,
            title={'text': f"{crypto_name} - Risk Score"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': RiskVisualizer.get_risk_color(risk_level)},
                'steps': [
                    {'range': [0, 30], 'color': "#90EE90"},
                    {'range': [30, 60], 'color': "#FFD700"},
                    {'range': [60, 80], 'color': "#FFA500"},
                    {'range': [80, 100], 'color': "#FF6B6B"}
                ],
                'threshold': {
                    'line': {'color': '#E74C3C', 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))
        
        fig.update_layout(
            height=400,
            template='plotly_dark',
            font={'color': 'white'},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    @staticmethod
    def create_risk_heatmap(risk_df: pd.DataFrame) -> go.Figure:
        """
        Create risk heatmap showing multiple risk factors.
        
        Args:
            risk_df: DataFrame with risk data
            
        Returns:
            Plotly figure
        """
        # Normalize risk scores (lower is better)
        data_for_heatmap = []
        cryptos = []
        
        for _, row in risk_df.iterrows():
            cryptos.append(row['Cryptocurrency'])
            
            # Extract numeric values
            vol_score = min(100, (row['Volatility_%'] / 100) * 100)
            sharpe_score = max(0, min(100, (1 - (row['Sharpe_Ratio'] + 2) / 4) * 100))
            dd_score = min(100, max(0, (abs(row['Max_Drawdown_%']) / 80) * 100))
            
            data_for_heatmap.append([vol_score, sharpe_score, dd_score])
        
        fig = go.Figure(data=go.Heatmap(
            z=data_for_heatmap,
            x=['Volatility Risk', 'Sharpe Risk', 'Drawdown Risk'],
            y=cryptos,
            colorscale='RdYlGn_r',
            text=[[f'{val:.0f}' for val in row] for row in data_for_heatmap],
            texttemplate='%{text}',
            textfont={"size": 12},
            colorbar=dict(title="Risk Score")
        ))
        
        fig.update_layout(
            title="Risk Factor Heatmap",
            height=400,
            template='plotly_dark',
            font={'color': 'white'}
        )
        
        return fig
    
    @staticmethod
    def create_risk_summary_table(risk_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create risk summary table for display.
        
        Args:
            risk_df: DataFrame with risk data
            
        Returns:
            Formatted DataFrame
        """
        summary = risk_df[[
            'Cryptocurrency',
            'Overall_Risk_Level',
            'Composite_Risk_Score',
            'Volatility_%',
            'Sharpe_Ratio',
            'Max_Drawdown_%'
        ]].copy()
        
        summary.columns = [
            'Crypto',
            'Risk Level',
            'Score',
            'Volatility %',
            'Sharpe',
            'Max DD %'
        ]
        
        return summary


class RiskWarningPanel:
    """Display risk warnings and notifications."""
    
    @staticmethod
    def display_warnings(crypto_name: str, warnings: list):
        """Display warning messages."""
        if warnings and len(warnings) > 0:
            for warning in warnings:
                if "No major warnings" in warning:
                    st.info(f"✓ {crypto_name}: {warning}")
                else:
                    st.warning(f"{crypto_name}: {warning}")
    
    @staticmethod
    def display_recommendations(recommendations: list):
        """Display investment recommendations."""
        if recommendations and len(recommendations) > 0:
            for rec in recommendations:
                if "Suitable" in rec or "✓" in rec:
                    st.success(rec)
                elif "Only" in rec or "EXTREME" in rec or "Minimal" in rec:
                    st.error(rec)
                else:
                    st.info(rec)


def display_risk_cards(risk_df: pd.DataFrame):
    """
    Display risk cards for quick overview.
    
    Args:
        risk_df: DataFrame with risk data
    """
    cols = st.columns(len(risk_df))
    
    for idx, (_, row) in enumerate(risk_df.iterrows()):
        with cols[idx]:
            risk_level = row['Overall_Risk_Level']
            score = row['Composite_Risk_Score']
            emoji = RiskVisualizer.get_risk_emoji(risk_level)
            color = RiskVisualizer.get_risk_color(risk_level)
            
            st.metric(
                f"{emoji} {row['Cryptocurrency']}",
                f"{score:.0f}/100",
                delta=risk_level
            )
