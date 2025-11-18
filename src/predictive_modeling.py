"""
Predictive Cost & Risk Modeling Module
Forecasts future portfolio costs and risks without complex ML
"""

import pandas as pd
from typing import Dict, List, Any


class PredictiveModeler:
    """Simple predictive modeling for application portfolio costs and risks"""

    def __init__(self):
        pass

    def forecast_costs(self, df: pd.DataFrame, years: int = 3) -> List[Dict[str, Any]]:
        """
        Forecast total costs for next 1-3 years based on current data

        Args:
            df: Portfolio DataFrame with 'Cost' and 'Tech Health' columns
            years: Number of years to forecast (1-3)

        Returns:
            List of forecast dictionaries with year, projected_cost, growth_rate
        """
        if df is None or df.empty:
            return []

        current_total = df['Cost'].sum()

        # Simple forecast: assume 3% inflation + additional % based on aging systems
        # Lower tech health = higher growth rate
        avg_tech_health = df['Tech Health'].mean() if 'Tech Health' in df.columns else 5.0

        forecasts = []
        for year in range(1, years + 1):
            # Base inflation (3%) + aging factor (up to 5% for poor tech health)
            inflation_rate = 0.03
            aging_rate = 0.05 * (1 - avg_tech_health / 10)  # Scales with poor health
            growth_rate = inflation_rate + aging_rate

            projected_cost = current_total * ((1 + growth_rate) ** year)

            forecasts.append({
                'year': year,
                'projected_cost': float(projected_cost),
                'growth_rate': float(growth_rate)
            })

        return forecasts

    def predict_high_risk_apps(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Predict which apps will become high-risk in next 12 months

        Args:
            df: Portfolio DataFrame

        Returns:
            List of high-risk applications with risk scores
        """
        if df is None or df.empty:
            return []

        # Apps with declining health and increasing costs
        at_risk = df[
            (df['Tech Health'] < 6) &
            (df['Cost'] > df['Cost'].median())
        ].copy()

        if at_risk.empty:
            return []

        # Risk score: combines poor health with high costs
        # (10 - health) gives higher score for lower health
        # Divide cost by 10000 to normalize scale
        at_risk['risk_score'] = (10 - at_risk['Tech Health']) * (at_risk['Cost'] / 10000)
        at_risk = at_risk.sort_values('risk_score', ascending=False)

        # Return top 10 at-risk applications
        result = []
        for _, row in at_risk.head(10).iterrows():
            result.append({
                'name': row['Application Name'],
                'technical_health': float(row['Tech Health']),
                'annual_cost': float(row['Cost']),
                'risk_score': float(row['risk_score'])
            })

        return result

    def calculate_roi_timeline(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate ROI for retirement recommendations

        Args:
            df: Portfolio DataFrame

        Returns:
            Dictionary with ROI analysis including payback period and 3-year ROI
        """
        if df is None or df.empty:
            return {
                'message': 'No data available',
                'savings': 0
            }

        # Find retirement candidates
        retire_candidates = df[
            df['Action Recommendation'].str.contains('Retire|Eliminate', case=False, na=False)
        ]

        if len(retire_candidates) == 0:
            return {
                'message': 'No retirement candidates found',
                'retire_count': 0,
                'annual_savings': 0,
                'migration_cost': 0,
                'payback_months': 0,
                'three_year_roi': 0
            }

        # Assume 70% cost savings from retirement (30% for decommissioning)
        annual_savings = retire_candidates['Cost'].sum() * 0.7

        # Assume $50K migration/decommissioning cost per app
        migration_cost = len(retire_candidates) * 50000

        # Calculate payback period
        if annual_savings > 0:
            payback_months = (migration_cost / annual_savings) * 12
        else:
            payback_months = float('inf')

        # 3-year ROI: (Total 3-year savings - migration cost)
        three_year_roi = (annual_savings * 3) - migration_cost

        return {
            'retire_count': int(len(retire_candidates)),
            'annual_savings': float(annual_savings),
            'migration_cost': float(migration_cost),
            'payback_months': float(payback_months) if payback_months != float('inf') else 0,
            'three_year_roi': float(three_year_roi)
        }

    def generate_predictions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate complete prediction report

        Args:
            df: Portfolio DataFrame

        Returns:
            Dictionary with all prediction analyses
        """
        return {
            'cost_forecast': self.forecast_costs(df, 3),
            'high_risk_apps': self.predict_high_risk_apps(df),
            'roi_analysis': self.calculate_roi_timeline(df)
        }
