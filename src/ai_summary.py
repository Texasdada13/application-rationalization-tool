"""
AI Executive Summary Generator
Generates automated executive narratives and insights from portfolio data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime


class ExecutiveSummaryGenerator:
    """
    Generate executive-level summaries and insights from application portfolio data.
    Uses rule-based logic and statistical analysis (no external AI APIs).
    """

    def __init__(self):
        """Initialize the AI summary generator"""
        self.insights_cache = []

    def analyze_portfolio_health(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate overall portfolio health metrics

        Args:
            df: Portfolio DataFrame with app data

        Returns:
            Dictionary with portfolio health metrics
        """
        if df is None or df.empty:
            return {
                'total_apps': 0,
                'avg_health': 0,
                'avg_business_value': 0,
                'total_cost': 0,
                'avg_score': 0,
                'health_rating': 'Unknown',
                'cost_per_app': 0
            }

        total_apps = len(df)
        avg_health = float(df['Tech Health'].mean()) if 'Tech Health' in df.columns else 0
        avg_business_value = float(df['Business Value'].mean()) if 'Business Value' in df.columns else 0
        total_cost = float(df['Cost'].sum()) if 'Cost' in df.columns else 0
        avg_score = float(df['Composite Score'].mean()) if 'Composite Score' in df.columns else 0
        cost_per_app = total_cost / total_apps if total_apps > 0 else 0

        # Determine overall health rating
        if avg_score >= 75:
            health_rating = 'Excellent'
        elif avg_score >= 60:
            health_rating = 'Good'
        elif avg_score >= 45:
            health_rating = 'Fair'
        elif avg_score >= 30:
            health_rating = 'Poor'
        else:
            health_rating = 'Critical'

        return {
            'total_apps': total_apps,
            'avg_health': round(avg_health, 1),
            'avg_business_value': round(avg_business_value, 1),
            'total_cost': round(total_cost, 2),
            'avg_score': round(avg_score, 1),
            'health_rating': health_rating,
            'cost_per_app': round(cost_per_app, 2)
        }

    def identify_critical_issues(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Identify applications with critical issues (low health, high cost, etc.)

        Args:
            df: Portfolio DataFrame

        Returns:
            List of critical issue dictionaries
        """
        issues = []

        if df is None or df.empty:
            return issues

        # Issue 1: Low health + high cost (money pit)
        if all(col in df.columns for col in ['Tech Health', 'Cost', 'Application Name']):
            avg_cost = df['Cost'].mean()
            money_pits = df[(df['Tech Health'] < 40) & (df['Cost'] > avg_cost)]

            if len(money_pits) > 0:
                total_waste = money_pits['Cost'].sum()
                issues.append({
                    'type': 'critical',
                    'category': 'Money Pit Applications',
                    'message': f'{len(money_pits)} high-cost applications with poor technical health are consuming ${total_waste:,.0f} annually',
                    'count': len(money_pits),
                    'impact': total_waste,
                    'apps': money_pits['Application Name'].tolist()[:5]  # Top 5
                })

        # Issue 2: Very low composite scores
        if 'Composite Score' in df.columns:
            critical_apps = df[df['Composite Score'] < 30]

            if len(critical_apps) > 0:
                issues.append({
                    'type': 'critical',
                    'category': 'Critical Score Applications',
                    'message': f'{len(critical_apps)} applications have critically low scores (below 30) and require immediate attention',
                    'count': len(critical_apps),
                    'impact': 0,
                    'apps': critical_apps['Application Name'].tolist()[:5] if 'Application Name' in df.columns else []
                })

        # Issue 3: High business value but low tech health
        if all(col in df.columns for col in ['Business Value', 'Tech Health', 'Application Name']):
            at_risk = df[(df['Business Value'] > 70) & (df['Tech Health'] < 40)]

            if len(at_risk) > 0:
                issues.append({
                    'type': 'critical',
                    'category': 'At-Risk Strategic Assets',
                    'message': f'{len(at_risk)} high-value applications have poor technical health and risk operational disruption',
                    'count': len(at_risk),
                    'impact': 0,
                    'apps': at_risk['Application Name'].tolist()[:5]
                })

        # Issue 4: Retire candidates consuming significant budget
        if all(col in df.columns for col in ['Action Recommendation', 'Cost']):
            retire_apps = df[df['Action Recommendation'].isin(['Retire', 'Eliminate', 'Immediate Action Required'])]

            if len(retire_apps) > 0 and retire_apps['Cost'].sum() > 0:
                retire_cost = retire_apps['Cost'].sum()
                issues.append({
                    'type': 'warning',
                    'category': 'Retirement Candidates',
                    'message': f'{len(retire_apps)} applications recommended for retirement are consuming ${retire_cost:,.0f} annually',
                    'count': len(retire_apps),
                    'impact': retire_cost,
                    'apps': retire_apps['Application Name'].tolist()[:5] if 'Application Name' in df.columns else []
                })

        return issues

    def detect_cost_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detect unusual cost patterns in the portfolio

        Args:
            df: Portfolio DataFrame

        Returns:
            List of cost anomaly dictionaries
        """
        anomalies = []

        if df is None or df.empty or 'Cost' not in df.columns:
            return anomalies

        # Calculate cost statistics
        mean_cost = df['Cost'].mean()
        median_cost = df['Cost'].median()
        std_cost = df['Cost'].std()

        # Anomaly 1: Outliers (3 standard deviations from mean)
        if std_cost > 0:
            outliers = df[df['Cost'] > (mean_cost + 3 * std_cost)]

            if len(outliers) > 0:
                outlier_cost = outliers['Cost'].sum()
                anomalies.append({
                    'type': 'warning',
                    'category': 'Cost Outliers',
                    'message': f'{len(outliers)} applications have exceptionally high costs (3σ above average) totaling ${outlier_cost:,.0f}',
                    'count': len(outliers),
                    'impact': outlier_cost,
                    'apps': outliers['Application Name'].tolist()[:5] if 'Application Name' in df.columns else []
                })

        # Anomaly 2: Top 20% consuming disproportionate budget
        top_20_pct_count = max(1, int(len(df) * 0.2))
        top_apps = df.nlargest(top_20_pct_count, 'Cost')
        top_cost_share = (top_apps['Cost'].sum() / df['Cost'].sum()) * 100 if df['Cost'].sum() > 0 else 0

        if top_cost_share > 80:  # Pareto principle - more than 80% is concerning
            anomalies.append({
                'type': 'warning',
                'category': 'Cost Concentration',
                'message': f'Top 20% of applications consume {top_cost_share:.1f}% of total budget, indicating high cost concentration risk',
                'count': top_20_pct_count,
                'impact': top_apps['Cost'].sum(),
                'apps': top_apps['Application Name'].tolist()[:5] if 'Application Name' in df.columns else []
            })

        # Anomaly 3: Low value but high cost
        if 'Business Value' in df.columns:
            low_value_high_cost = df[(df['Business Value'] < 40) & (df['Cost'] > median_cost)]

            if len(low_value_high_cost) > 0:
                waste = low_value_high_cost['Cost'].sum()
                anomalies.append({
                    'type': 'warning',
                    'category': 'Low ROI Applications',
                    'message': f'{len(low_value_high_cost)} low-value applications cost ${waste:,.0f} annually with minimal business benefit',
                    'count': len(low_value_high_cost),
                    'impact': waste,
                    'apps': low_value_high_cost['Application Name'].tolist()[:5] if 'Application Name' in df.columns else []
                })

        return anomalies

    def find_opportunities(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Identify investment and optimization opportunities

        Args:
            df: Portfolio DataFrame

        Returns:
            List of opportunity dictionaries
        """
        opportunities = []

        if df is None or df.empty:
            return opportunities

        # Opportunity 1: High value apps worth investing in
        if all(col in df.columns for col in ['Business Value', 'Tech Health', 'Application Name']):
            invest_candidates = df[(df['Business Value'] > 70) & (df['Tech Health'] > 60)]

            if len(invest_candidates) > 0:
                opportunities.append({
                    'type': 'opportunity',
                    'category': 'Strategic Investment Targets',
                    'message': f'{len(invest_candidates)} high-performing applications are ideal candidates for strategic investment and enhancement',
                    'count': len(invest_candidates),
                    'impact': 0,
                    'apps': invest_candidates['Application Name'].tolist()[:5]
                })

        # Opportunity 2: Quick wins (moderate value, fixable health issues)
        if all(col in df.columns for col in ['Business Value', 'Tech Health', 'Cost', 'Application Name']):
            avg_cost = df['Cost'].mean()
            quick_wins = df[
                (df['Business Value'] >= 50) &
                (df['Business Value'] <= 70) &
                (df['Tech Health'] >= 40) &
                (df['Tech Health'] <= 60) &
                (df['Cost'] < avg_cost)
            ]

            if len(quick_wins) > 0:
                opportunities.append({
                    'type': 'opportunity',
                    'category': 'Quick Win Improvements',
                    'message': f'{len(quick_wins)} moderate-value applications could deliver quick wins with targeted improvements',
                    'count': len(quick_wins),
                    'impact': 0,
                    'apps': quick_wins['Application Name'].tolist()[:5]
                })

        # Opportunity 3: Consolidation candidates
        if 'Action Recommendation' in df.columns:
            consolidate = df[df['Action Recommendation'] == 'Consolidate']

            if len(consolidate) > 0 and 'Cost' in df.columns:
                potential_savings = consolidate['Cost'].sum() * 0.3  # Assume 30% savings
                opportunities.append({
                    'type': 'opportunity',
                    'category': 'Consolidation Potential',
                    'message': f'{len(consolidate)} applications could be consolidated, potentially saving ${potential_savings:,.0f} annually',
                    'count': len(consolidate),
                    'impact': potential_savings,
                    'apps': consolidate['Application Name'].tolist()[:5] if 'Application Name' in df.columns else []
                })

        # Opportunity 4: Cloud migration candidates
        if 'Action Recommendation' in df.columns:
            migrate = df[df['Action Recommendation'] == 'Migrate']

            if len(migrate) > 0:
                opportunities.append({
                    'type': 'opportunity',
                    'category': 'Cloud Migration Pipeline',
                    'message': f'{len(migrate)} applications are ready for cloud migration to improve scalability and reduce costs',
                    'count': len(migrate),
                    'impact': 0,
                    'apps': migrate['Application Name'].tolist()[:5] if 'Application Name' in df.columns else []
                })

        return opportunities

    def generate_recommendations(self, df: pd.DataFrame, issues: List[Dict],
                                 opportunities: List[Dict]) -> List[Dict[str, Any]]:
        """
        Generate prioritized action recommendations

        Args:
            df: Portfolio DataFrame
            issues: List of identified issues
            opportunities: List of identified opportunities

        Returns:
            List of recommendation dictionaries with priorities and timelines
        """
        recommendations = []

        # Recommendation 1: Address critical issues first
        critical_issues = [i for i in issues if i['type'] == 'critical']
        if critical_issues:
            top_issue = critical_issues[0]
            recommendations.append({
                'action': f'Address {top_issue["category"]}: {top_issue["count"]} applications need immediate remediation',
                'priority': 'high',
                'timeline': '30 days',
                'impact': f'Mitigate critical operational and financial risks',
                'category': 'Risk Mitigation'
            })

        # Recommendation 2: Retire low-value apps
        if df is not None and not df.empty and 'Action Recommendation' in df.columns:
            retire_count = len(df[df['Action Recommendation'].isin(['Retire', 'Eliminate'])])
            if retire_count > 0 and 'Cost' in df.columns:
                retire_cost = df[df['Action Recommendation'].isin(['Retire', 'Eliminate'])]['Cost'].sum()
                if retire_cost > 0:
                    recommendations.append({
                        'action': f'Initiate retirement process for {retire_count} end-of-life applications',
                        'priority': 'high',
                        'timeline': '60 days',
                        'impact': f'Free up ${retire_cost:,.0f} in annual budget for strategic investments',
                        'category': 'Cost Optimization'
                    })

        # Recommendation 3: Invest in strategic assets
        strategic_opps = [o for o in opportunities if 'Strategic' in o.get('category', '')]
        if strategic_opps:
            top_opp = strategic_opps[0]
            recommendations.append({
                'action': f'Allocate resources to enhance {top_opp["count"]} high-value strategic applications',
                'priority': 'medium',
                'timeline': '90 days',
                'impact': 'Maximize ROI on business-critical applications',
                'category': 'Strategic Investment'
            })

        # Recommendation 4: Quick wins
        quick_win_opps = [o for o in opportunities if 'Quick Win' in o.get('category', '')]
        if quick_win_opps:
            qw = quick_win_opps[0]
            recommendations.append({
                'action': f'Execute quick-win improvements on {qw["count"]} moderate-value applications',
                'priority': 'medium',
                'timeline': '60 days',
                'impact': 'Deliver visible improvements with minimal investment',
                'category': 'Operational Excellence'
            })

        # Recommendation 5: Cost optimization
        cost_anomalies = [a for a in issues if 'Cost' in a.get('category', '')]
        if cost_anomalies and len(cost_anomalies) > 0:
            anomaly = cost_anomalies[0]
            if anomaly.get('impact', 0) > 0:
                recommendations.append({
                    'action': f'Optimize spending on {anomaly["count"]} high-cost applications through renegotiation or consolidation',
                    'priority': 'medium',
                    'timeline': '90 days',
                    'impact': f'Potential savings of ${anomaly["impact"] * 0.2:,.0f} (20% reduction target)',
                    'category': 'Cost Optimization'
                })

        # Recommendation 6: Establish governance
        if df is not None and not df.empty and len(df) > 20:
            recommendations.append({
                'action': 'Implement ongoing portfolio governance with quarterly reviews and automated tracking',
                'priority': 'low',
                'timeline': '120 days',
                'impact': 'Ensure sustained portfolio health and prevent technical debt accumulation',
                'category': 'Governance'
            })

        return recommendations[:5]  # Return top 5 recommendations

    def create_executive_narrative(self, df: pd.DataFrame,
                                   health_metrics: Dict,
                                   issues: List[Dict],
                                   opportunities: List[Dict]) -> str:
        """
        Generate a 3-4 paragraph executive summary narrative

        Args:
            df: Portfolio DataFrame
            health_metrics: Portfolio health metrics
            issues: Identified issues
            opportunities: Identified opportunities

        Returns:
            Executive narrative string
        """
        if df is None or df.empty:
            return "No portfolio data available for analysis. Please upload application data to generate insights."

        # Paragraph 1: Portfolio Overview
        total_apps = health_metrics['total_apps']
        total_cost = health_metrics['total_cost']
        avg_score = health_metrics['avg_score']
        health_rating = health_metrics['health_rating']

        p1 = f"Your application portfolio consists of {total_apps} applications with a total annual cost of ${total_cost:,.0f}. "
        p1 += f"The portfolio maintains an average health score of {avg_score:.1f}/100, indicating {health_rating.lower()} overall health. "

        if 'Action Recommendation' in df.columns:
            action_counts = df['Action Recommendation'].value_counts()
            top_action = action_counts.index[0] if len(action_counts) > 0 else "Unknown"
            top_count = action_counts.iloc[0] if len(action_counts) > 0 else 0
            p1 += f"Analysis reveals {top_count} applications recommended for '{top_action}', representing the primary strategic action needed."

        # Paragraph 2: Critical Issues
        critical_issues = [i for i in issues if i['type'] == 'critical']
        warning_issues = [i for i in issues if i['type'] == 'warning']

        if critical_issues:
            p2 = f"Critical analysis identifies {len(critical_issues)} major concern areas requiring immediate attention. "
            for issue in critical_issues[:2]:  # Top 2 critical issues
                p2 += f"{issue['message']}. "
        elif warning_issues:
            p2 = f"Portfolio review highlights {len(warning_issues)} areas warranting management focus. "
            p2 += f"{warning_issues[0]['message']}. "
        else:
            p2 = "The portfolio demonstrates strong health metrics with no critical issues identified at this time. "
            p2 += "Continued monitoring and proactive maintenance will sustain this positive trajectory."

        # Paragraph 3: Opportunities
        if opportunities:
            p3 = f"Strategic analysis reveals {len(opportunities)} key opportunities for portfolio optimization. "
            for opp in opportunities[:2]:  # Top 2 opportunities
                p3 += f"{opp['message']}. "

            # Add impact if available
            total_opportunity_impact = sum([o.get('impact', 0) for o in opportunities])
            if total_opportunity_impact > 0:
                p3 += f"Pursuing these opportunities could yield ${total_opportunity_impact:,.0f} in annual benefits."
        else:
            p3 = "The portfolio is currently optimized with limited immediate optimization opportunities. "
            p3 += "Focus should remain on maintaining current performance levels and monitoring for emerging needs."

        # Paragraph 4: Strategic Recommendation
        if avg_score < 50:
            p4 = "Given the current portfolio health rating, immediate executive action is recommended to address critical gaps and prevent operational disruption. "
            p4 += "A focused 90-day improvement plan should prioritize high-risk applications while establishing governance frameworks for sustained improvement."
        elif avg_score < 70:
            p4 = "The portfolio shows moderate health with clear improvement pathways. "
            p4 += "Recommended next steps include targeted investments in strategic applications, systematic retirement of legacy systems, and implementation of ongoing portfolio governance practices."
        else:
            p4 = "The portfolio demonstrates strong performance and strategic alignment. "
            p4 += "Maintain current trajectory through continued investment in high-value applications, proactive technical debt management, and quarterly portfolio reviews to sustain excellence."

        return f"{p1}\n\n{p2}\n\n{p3}\n\n{p4}"

    def generate_full_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Orchestrate all analysis methods to generate complete AI summary

        Args:
            df: Portfolio DataFrame

        Returns:
            Complete summary dictionary with all insights
        """
        try:
            # Handle empty or None data
            if df is None or df.empty:
                return {
                    'success': False,
                    'error': 'No portfolio data available',
                    'overview': 'No data loaded',
                    'narrative': 'Please upload application portfolio data to generate AI insights.',
                    'insights': [],
                    'recommendations': [],
                    'generated_at': datetime.now().isoformat()
                }

            # Run all analysis methods
            health_metrics = self.analyze_portfolio_health(df)
            issues = self.identify_critical_issues(df)
            cost_anomalies = self.detect_cost_anomalies(df)
            opportunities = self.find_opportunities(df)

            # Combine all insights
            all_insights = issues + cost_anomalies + opportunities

            # Generate recommendations
            recommendations = self.generate_recommendations(df, issues + cost_anomalies, opportunities)

            # Create narrative
            narrative = self.create_executive_narrative(df, health_metrics, issues + cost_anomalies, opportunities)

            # Create overview
            overview = f"Portfolio of {health_metrics['total_apps']} applications | "
            overview += f"Health: {health_metrics['health_rating']} ({health_metrics['avg_score']:.1f}/100) | "
            overview += f"Annual Cost: ${health_metrics['total_cost']:,.0f}"

            result = {
                'success': True,
                'overview': overview,
                'narrative': narrative,
                'insights': all_insights,
                'recommendations': recommendations,
                'health_metrics': health_metrics,
                'generated_at': datetime.now().isoformat()
            }

            # Convert numpy/pandas types to native Python types for JSON serialization
            import json
            result = json.loads(json.dumps(result, default=str))

            return result

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'overview': 'Error generating summary',
                'narrative': f'An error occurred while analyzing the portfolio: {str(e)}',
                'insights': [],
                'recommendations': [],
                'generated_at': datetime.now().isoformat()
            }   
