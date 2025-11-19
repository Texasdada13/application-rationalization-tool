"""
Advanced Report Generator
Multi-format report generation (PDF, Excel, PowerPoint) with executive summaries
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
from io import BytesIO


class AdvancedReportGenerator:
    """Generate comprehensive reports in multiple formats"""

    REPORT_TYPES = {
        'executive_summary': {
            'name': 'Executive Summary Report',
            'description': 'High-level overview for C-suite',
            'sections': ['portfolio_overview', 'key_metrics', 'top_risks', 'recommendations']
        },
        'technical_deep_dive': {
            'name': 'Technical Deep Dive',
            'description': 'Detailed technical analysis',
            'sections': ['portfolio_overview', 'tech_health', 'dependencies', 'modernization']
        },
        'financial_analysis': {
            'name': 'Financial Analysis Report',
            'description': 'Cost breakdown and optimization opportunities',
            'sections': ['cost_overview', 'tco_breakdown', 'hidden_costs', 'optimization']
        },
        'risk_compliance': {
            'name': 'Risk & Compliance Report',
            'description': 'Risk assessment and compliance status',
            'sections': ['risk_overview', 'compliance_status', 'mitigation_plans', 'audit_trail']
        },
        'roadmap_strategy': {
            'name': 'Strategic Roadmap Report',
            'description': 'Prioritized action plan with timeline',
            'sections': ['roadmap_overview', 'phase_breakdown', 'quick_wins', 'resources']
        }
    }

    def __init__(self, df_applications: pd.DataFrame):
        """Initialize with application portfolio data"""
        self.df = df_applications.copy()
        self.report_data = {}
        self.generated_at = datetime.now()

    def generate_portfolio_overview(self) -> Dict[str, Any]:
        """Generate high-level portfolio overview"""

        total_apps = len(self.df)
        total_cost = self.df['Cost'].sum()
        avg_health = self.df['Tech Health'].mean()
        avg_value = self.df['Business Value'].mean()

        # Category breakdown
        category_stats = self.df.groupby('Category').agg({
            'Application Name': 'count',
            'Cost': 'sum',
            'Tech Health': 'mean',
            'Business Value': 'mean'
        }).round(2)

        # Health distribution
        health_distribution = {
            'Critical (1-3)': len(self.df[self.df['Tech Health'] <= 3]),
            'Poor (4-5)': len(self.df[(self.df['Tech Health'] > 3) & (self.df['Tech Health'] <= 5)]),
            'Fair (6-7)': len(self.df[(self.df['Tech Health'] > 5) & (self.df['Tech Health'] <= 7)]),
            'Good (8-9)': len(self.df[(self.df['Tech Health'] > 7) & (self.df['Tech Health'] <= 9)]),
            'Excellent (10)': len(self.df[self.df['Tech Health'] == 10])
        }

        # Value distribution
        value_distribution = {
            'Low Value (1-3)': len(self.df[self.df['Business Value'] <= 3]),
            'Medium Value (4-6)': len(self.df[(self.df['Business Value'] > 3) & (self.df['Business Value'] <= 6)]),
            'High Value (7-10)': len(self.df[self.df['Business Value'] > 6])
        }

        return {
            'summary': {
                'total_applications': total_apps,
                'total_annual_cost': total_cost,
                'average_health_score': round(avg_health, 2),
                'average_business_value': round(avg_value, 2),
                'report_date': self.generated_at.strftime('%Y-%m-%d %H:%M:%S')
            },
            'category_breakdown': category_stats.to_dict('index'),
            'health_distribution': health_distribution,
            'value_distribution': value_distribution
        }

    def generate_key_metrics(self) -> Dict[str, Any]:
        """Generate key performance metrics"""

        # TIME Framework distribution
        time_distribution = {}
        for idx, row in self.df.iterrows():
            health = row['Tech Health']
            value = row['Business Value']

            if health <= 5 and value <= 6:
                category = 'Eliminate'
            elif health > 5 and value <= 6:
                category = 'Tolerate'
            elif health <= 5 and value > 6:
                category = 'Migrate'
            else:
                category = 'Invest'

            time_distribution[category] = time_distribution.get(category, 0) + 1

        # Cost efficiency
        high_cost_low_value = len(self.df[(self.df['Cost'] > self.df['Cost'].median()) &
                                           (self.df['Business Value'] <= 5)])

        low_cost_high_value = len(self.df[(self.df['Cost'] < self.df['Cost'].median()) &
                                           (self.df['Business Value'] >= 7)])

        # Technical debt estimate (apps with health < 5)
        technical_debt_apps = self.df[self.df['Tech Health'] < 5]
        technical_debt_cost = technical_debt_apps['Cost'].sum()

        return {
            'time_framework': time_distribution,
            'efficiency_metrics': {
                'high_cost_low_value_apps': high_cost_low_value,
                'low_cost_high_value_apps': low_cost_high_value,
                'cost_efficiency_ratio': round(low_cost_high_value / max(high_cost_low_value, 1), 2)
            },
            'technical_debt': {
                'affected_applications': len(technical_debt_apps),
                'annual_cost_at_risk': technical_debt_cost,
                'percentage_of_portfolio': round(len(technical_debt_apps) / len(self.df) * 100, 1)
            }
        }

    def generate_top_risks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Identify top risk applications"""

        risks = []

        for idx, row in self.df.iterrows():
            app_name = row['Application Name']
            health = row['Tech Health']
            value = row['Business Value']
            cost = row['Cost']

            # Calculate risk score
            health_risk = (10 - health) * 10
            criticality = value * 10
            cost_exposure = min(100, (cost / 500000) * 100)

            risk_score = (health_risk * 0.4 + criticality * 0.35 + cost_exposure * 0.25)

            # Risk factors
            risk_factors = []
            if health <= 3:
                risk_factors.append('Critical technical health')
            if value >= 8:
                risk_factors.append('Mission-critical application')
            if cost > 200000:
                risk_factors.append('High cost exposure')

            risks.append({
                'app_name': app_name,
                'risk_score': round(risk_score, 1),
                'health': health,
                'business_value': value,
                'annual_cost': cost,
                'risk_factors': risk_factors
            })

        # Sort by risk score
        risks.sort(key=lambda x: x['risk_score'], reverse=True)

        return risks[:limit]

    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""

        recommendations = []

        # 1. Retirement candidates
        retire_candidates = self.df[(self.df['Tech Health'] <= 3) & (self.df['Business Value'] <= 4)]
        if len(retire_candidates) > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'Rationalization',
                'action': 'Retire low-value, unhealthy applications',
                'impact': f'{len(retire_candidates)} applications identified',
                'estimated_savings': retire_candidates['Cost'].sum(),
                'timeline': '6-12 months',
                'details': f'Applications: {", ".join(retire_candidates["Application Name"].head(5).tolist())}'
            })

        # 2. Modernization priorities
        modernize_candidates = self.df[(self.df['Tech Health'] <= 5) & (self.df['Business Value'] >= 7)]
        if len(modernize_candidates) > 0:
            recommendations.append({
                'priority': 'urgent',
                'category': 'Modernization',
                'action': 'Modernize critical applications with poor health',
                'impact': f'{len(modernize_candidates)} critical applications at risk',
                'estimated_savings': modernize_candidates['Cost'].sum() * 0.2,
                'timeline': '3-6 months',
                'details': f'Applications: {", ".join(modernize_candidates["Application Name"].head(5).tolist())}'
            })

        # 3. Cost optimization
        high_cost_apps = self.df[self.df['Cost'] > self.df['Cost'].quantile(0.75)]
        if len(high_cost_apps) > 0:
            recommendations.append({
                'priority': 'medium',
                'category': 'Cost Optimization',
                'action': 'Review and optimize high-cost applications',
                'impact': f'Top 25% of applications by cost',
                'estimated_savings': high_cost_apps['Cost'].sum() * 0.15,
                'timeline': '3-9 months',
                'details': f'{len(high_cost_apps)} applications consuming {(high_cost_apps["Cost"].sum() / self.df["Cost"].sum() * 100):.1f}% of budget'
            })

        # 4. Consolidation opportunities
        category_counts = self.df['Category'].value_counts()
        overlapping_categories = category_counts[category_counts > 5]
        if len(overlapping_categories) > 0:
            recommendations.append({
                'priority': 'medium',
                'category': 'Consolidation',
                'action': 'Consolidate redundant applications in overlapping categories',
                'impact': f'{len(overlapping_categories)} categories with 5+ applications',
                'estimated_savings': self.df['Cost'].sum() * 0.10,
                'timeline': '6-18 months',
                'details': f'Categories: {", ".join(overlapping_categories.head(3).index.tolist())}'
            })

        return recommendations

    def generate_cost_breakdown(self) -> Dict[str, Any]:
        """Generate detailed cost breakdown"""

        total_cost = self.df['Cost'].sum()

        # By category
        category_costs = self.df.groupby('Category')['Cost'].sum().sort_values(ascending=False)

        # By health tier
        health_tiers = {
            'Critical (1-3)': self.df[self.df['Tech Health'] <= 3]['Cost'].sum(),
            'Poor (4-5)': self.df[(self.df['Tech Health'] > 3) & (self.df['Tech Health'] <= 5)]['Cost'].sum(),
            'Fair (6-7)': self.df[(self.df['Tech Health'] > 5) & (self.df['Tech Health'] <= 7)]['Cost'].sum(),
            'Good (8-9)': self.df[(self.df['Tech Health'] > 7) & (self.df['Tech Health'] <= 9)]['Cost'].sum(),
            'Excellent (10)': self.df[self.df['Tech Health'] == 10]['Cost'].sum()
        }

        # By value tier
        value_tiers = {
            'Low Value (1-3)': self.df[self.df['Business Value'] <= 3]['Cost'].sum(),
            'Medium Value (4-6)': self.df[(self.df['Business Value'] > 3) & (self.df['Business Value'] <= 6)]['Cost'].sum(),
            'High Value (7-10)': self.df[self.df['Business Value'] > 6]['Cost'].sum()
        }

        # Top 10 most expensive
        top_10_expensive = self.df.nlargest(10, 'Cost')[['Application Name', 'Cost', 'Tech Health', 'Business Value']].to_dict('records')

        return {
            'total_annual_cost': total_cost,
            'cost_by_category': category_costs.to_dict(),
            'cost_by_health': health_tiers,
            'cost_by_value': value_tiers,
            'top_10_expensive': top_10_expensive,
            'average_cost_per_app': round(total_cost / len(self.df), 2)
        }

    def generate_executive_summary_report(self) -> Dict[str, Any]:
        """Generate complete executive summary report"""

        return {
            'report_type': 'executive_summary',
            'report_title': 'Application Portfolio - Executive Summary',
            'generated_at': self.generated_at.isoformat(),
            'sections': {
                'portfolio_overview': self.generate_portfolio_overview(),
                'key_metrics': self.generate_key_metrics(),
                'top_risks': self.generate_top_risks(limit=10),
                'recommendations': self.generate_recommendations()
            }
        }

    def generate_financial_analysis_report(self) -> Dict[str, Any]:
        """Generate financial analysis report"""

        return {
            'report_type': 'financial_analysis',
            'report_title': 'Application Portfolio - Financial Analysis',
            'generated_at': self.generated_at.isoformat(),
            'sections': {
                'portfolio_overview': self.generate_portfolio_overview(),
                'cost_breakdown': self.generate_cost_breakdown(),
                'key_metrics': self.generate_key_metrics(),
                'recommendations': [r for r in self.generate_recommendations()
                                   if r['category'] in ['Cost Optimization', 'Rationalization']]
            }
        }

    def generate_technical_report(self) -> Dict[str, Any]:
        """Generate technical deep dive report"""

        # Technical health analysis
        health_stats = self.df.groupby('Category').agg({
            'Tech Health': ['mean', 'min', 'max', 'count']
        }).round(2)

        # Apps needing attention
        critical_apps = self.df[self.df['Tech Health'] <= 3][
            ['Application Name', 'Tech Health', 'Business Value', 'Cost', 'Category']
        ].to_dict('records')

        poor_apps = self.df[(self.df['Tech Health'] > 3) & (self.df['Tech Health'] <= 5)][
            ['Application Name', 'Tech Health', 'Business Value', 'Cost', 'Category']
        ].to_dict('records')

        return {
            'report_type': 'technical_deep_dive',
            'report_title': 'Application Portfolio - Technical Analysis',
            'generated_at': self.generated_at.isoformat(),
            'sections': {
                'portfolio_overview': self.generate_portfolio_overview(),
                'health_statistics': health_stats.to_dict(),
                'critical_applications': critical_apps,
                'poor_health_applications': poor_apps,
                'recommendations': [r for r in self.generate_recommendations()
                                   if r['category'] in ['Modernization', 'Consolidation']]
            }
        }

    def export_to_json(self, report_data: Dict[str, Any]) -> str:
        """Export report to JSON format"""
        return json.dumps(report_data, indent=2, default=str)

    def export_to_excel(self, report_data: Dict[str, Any]) -> BytesIO:
        """Export report to Excel format with multiple sheets"""

        output = BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Summary sheet
            summary = report_data['sections']['portfolio_overview']['summary']
            df_summary = pd.DataFrame([summary])
            df_summary.to_excel(writer, sheet_name='Summary', index=False)

            # Category breakdown
            if 'category_breakdown' in report_data['sections']['portfolio_overview']:
                df_categories = pd.DataFrame.from_dict(
                    report_data['sections']['portfolio_overview']['category_breakdown'],
                    orient='index'
                )
                df_categories.to_excel(writer, sheet_name='Category Breakdown')

            # Top risks
            if 'top_risks' in report_data['sections']:
                df_risks = pd.DataFrame(report_data['sections']['top_risks'])
                df_risks.to_excel(writer, sheet_name='Top Risks', index=False)

            # Recommendations
            if 'recommendations' in report_data['sections']:
                df_recommendations = pd.DataFrame(report_data['sections']['recommendations'])
                df_recommendations.to_excel(writer, sheet_name='Recommendations', index=False)

            # Cost breakdown (if available)
            if 'cost_breakdown' in report_data['sections']:
                cost_data = report_data['sections']['cost_breakdown']
                if 'top_10_expensive' in cost_data:
                    df_expensive = pd.DataFrame(cost_data['top_10_expensive'])
                    df_expensive.to_excel(writer, sheet_name='Top 10 Expensive', index=False)

            # Full portfolio data
            self.df.to_excel(writer, sheet_name='Full Portfolio', index=False)

        output.seek(0)
        return output

    def export_to_csv(self, report_data: Dict[str, Any]) -> str:
        """Export report summary to CSV format"""

        # Create summary CSV
        rows = []

        # Add summary section
        if 'portfolio_overview' in report_data['sections']:
            summary = report_data['sections']['portfolio_overview']['summary']
            for key, value in summary.items():
                rows.append({'Section': 'Portfolio Overview', 'Metric': key, 'Value': value})

        # Add key metrics
        if 'key_metrics' in report_data['sections']:
            metrics = report_data['sections']['key_metrics']
            for section, data in metrics.items():
                if isinstance(data, dict):
                    for key, value in data.items():
                        rows.append({'Section': f'Metrics - {section}', 'Metric': key, 'Value': value})

        df_export = pd.DataFrame(rows)
        return df_export.to_csv(index=False)

    def generate_report(self, report_type: str = 'executive_summary') -> Dict[str, Any]:
        """Generate report of specified type"""

        if report_type not in self.REPORT_TYPES:
            return {'error': f'Unknown report type: {report_type}'}

        if report_type == 'executive_summary':
            return self.generate_executive_summary_report()
        elif report_type == 'financial_analysis':
            return self.generate_financial_analysis_report()
        elif report_type == 'technical_deep_dive':
            return self.generate_technical_report()
        else:
            # Default to executive summary structure
            return self.generate_executive_summary_report()

    def get_available_reports(self) -> Dict[str, Any]:
        """Get list of available report types"""
        return self.REPORT_TYPES
