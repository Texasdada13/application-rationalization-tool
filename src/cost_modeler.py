"""
Advanced Cost Modeler
Provides TCO breakdown, cost allocation by department, hidden cost identification,
and contract renewal tracking
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import random


class AdvancedCostModeler:
    """Advanced cost modeling with TCO breakdown and allocation analysis"""

    # TCO breakdown percentages (industry averages)
    TCO_BREAKDOWN_DEFAULTS = {
        'licensing': 0.30,      # 30% - Software licenses
        'support': 0.20,        # 20% - Vendor support and maintenance
        'infrastructure': 0.25, # 25% - Servers, storage, network
        'labor': 0.20,          # 20% - Internal staff time
        'training': 0.03,       # 3% - User training
        'other': 0.02           # 2% - Misc costs
    }

    # Cost multipliers by category
    CATEGORY_MULTIPLIERS = {
        'IT & Infrastructure': {'infrastructure': 1.5, 'labor': 1.3},
        'Finance & Accounting': {'support': 1.2, 'training': 1.5},
        'Citizen Services': {'labor': 1.4, 'support': 1.1},
        'Human Resources': {'training': 1.6, 'support': 1.2},
        'Public Safety': {'infrastructure': 1.3, 'labor': 1.5},
        'Operations': {'infrastructure': 1.2, 'labor': 1.3},
        'Compliance & Reporting': {'support': 1.4, 'labor': 1.2},
        'Records Management': {'infrastructure': 1.3, 'support': 1.1}
    }

    def __init__(self, df_applications: pd.DataFrame):
        """Initialize with application portfolio data"""
        self.df = df_applications.copy()
        self.tco_data = None
        self.department_allocations = None
        self.hidden_costs = None

    def calculate_tco_breakdown(self) -> Dict[str, Any]:
        """Calculate detailed TCO breakdown for each application"""

        tco_breakdown = []

        for idx, app in self.df.iterrows():
            app_name = app['Application Name']
            total_cost = app['Cost']
            category = app.get('Category', 'Other')

            # Get base percentages
            breakdown = self.TCO_BREAKDOWN_DEFAULTS.copy()

            # Apply category-specific multipliers
            if category in self.CATEGORY_MULTIPLIERS:
                multipliers = self.CATEGORY_MULTIPLIERS[category]

                # Adjust percentages based on multipliers
                for component, multiplier in multipliers.items():
                    if component in breakdown:
                        breakdown[component] *= multiplier

                # Renormalize to ensure sum = 1.0
                total = sum(breakdown.values())
                breakdown = {k: v / total for k, v in breakdown.items()}

            # Calculate dollar amounts
            component_costs = {
                component: round(total_cost * percentage, 2)
                for component, percentage in breakdown.items()
            }

            tco_breakdown.append({
                'app_name': app_name,
                'category': category,
                'total_cost': total_cost,
                'components': component_costs,
                'percentages': {k: round(v * 100, 1) for k, v in breakdown.items()}
            })

        self.tco_data = tco_breakdown
        return self._aggregate_tco_summary(tco_breakdown)

    def _aggregate_tco_summary(self, tco_breakdown: List[Dict]) -> Dict[str, Any]:
        """Aggregate TCO data across entire portfolio"""

        # Aggregate by component
        component_totals = defaultdict(float)
        for app in tco_breakdown:
            for component, cost in app['components'].items():
                component_totals[component] += cost

        total_cost = sum(component_totals.values())

        return {
            'total_portfolio_cost': total_cost,
            'component_breakdown': dict(component_totals),
            'component_percentages': {
                k: round((v / total_cost) * 100, 1)
                for k, v in component_totals.items()
            },
            'top_cost_drivers': self._identify_cost_drivers(tco_breakdown),
            'application_count': len(tco_breakdown)
        }

    def _identify_cost_drivers(self, tco_breakdown: List[Dict]) -> List[Dict]:
        """Identify top cost-driving applications"""

        sorted_apps = sorted(tco_breakdown, key=lambda x: x['total_cost'], reverse=True)

        return [
            {
                'app_name': app['app_name'],
                'total_cost': app['total_cost'],
                'category': app['category'],
                'top_component': max(app['components'].items(), key=lambda x: x[1])[0],
                'top_component_cost': max(app['components'].values())
            }
            for app in sorted_apps[:10]
        ]

    def allocate_costs_by_department(self) -> Dict[str, Any]:
        """Allocate costs to departments (with estimation if Department column missing)"""

        # Check if Department column exists
        if 'Department' in self.df.columns and not self.df['Department'].isna().all():
            # Use actual department data
            return self._allocate_by_actual_department()
        else:
            # Estimate department allocation based on category
            return self._estimate_department_allocation()

    def _allocate_by_actual_department(self) -> Dict[str, Any]:
        """Allocate costs using actual department data"""

        dept_costs = self.df.groupby('Department').agg({
            'Cost': 'sum',
            'Application Name': 'count',
            'Tech Health': 'mean',
            'Business Value': 'mean'
        }).reset_index()

        dept_costs.columns = ['department', 'total_cost', 'app_count', 'avg_health', 'avg_value']
        dept_costs = dept_costs.sort_values('total_cost', ascending=False)

        allocations = dept_costs.to_dict('records')

        return {
            'allocation_method': 'actual',
            'departments': allocations,
            'total_departments': len(allocations),
            'highest_spend': allocations[0] if allocations else None,
            'total_cost': self.df['Cost'].sum()
        }

    def _estimate_department_allocation(self) -> Dict[str, Any]:
        """Estimate department allocation based on category"""

        # Mapping of categories to typical department owners
        CATEGORY_TO_DEPARTMENT = {
            'Finance & Accounting': 'Finance Department',
            'IT & Infrastructure': 'IT Department',
            'Citizen Services': 'Citizen Services',
            'Human Resources': 'Human Resources',
            'Public Safety': 'Police Department',
            'Operations': 'Public Works',
            'Compliance & Reporting': 'Legal Department',
            'Records Management': 'Clerk\'s Office'
        }

        # Create estimated department column
        self.df['Estimated_Department'] = self.df['Category'].map(
            lambda cat: CATEGORY_TO_DEPARTMENT.get(cat, 'General Administration')
        )

        dept_costs = self.df.groupby('Estimated_Department').agg({
            'Cost': 'sum',
            'Application Name': 'count',
            'Tech Health': 'mean',
            'Business Value': 'mean'
        }).reset_index()

        dept_costs.columns = ['department', 'total_cost', 'app_count', 'avg_health', 'avg_value']
        dept_costs = dept_costs.sort_values('total_cost', ascending=False)

        allocations = dept_costs.to_dict('records')

        return {
            'allocation_method': 'estimated',
            'departments': allocations,
            'total_departments': len(allocations),
            'highest_spend': allocations[0] if allocations else None,
            'total_cost': self.df['Cost'].sum(),
            'note': 'Department allocations are estimated based on application categories'
        }

    def identify_hidden_costs(self) -> List[Dict[str, Any]]:
        """Identify potential hidden costs and cost optimization opportunities"""

        hidden_costs = []

        # 1. Integration complexity costs
        integration_costs = self._estimate_integration_costs()
        if integration_costs:
            hidden_costs.append(integration_costs)

        # 2. Redundancy costs
        redundancy_costs = self._estimate_redundancy_costs()
        if redundancy_costs:
            hidden_costs.append(redundancy_costs)

        # 3. Technical debt costs
        tech_debt_costs = self._estimate_technical_debt_costs()
        if tech_debt_costs:
            hidden_costs.append(tech_debt_costs)

        # 4. Training and onboarding costs
        training_costs = self._estimate_training_costs()
        if training_costs:
            hidden_costs.append(training_costs)

        # 5. Opportunity costs
        opportunity_costs = self._estimate_opportunity_costs()
        if opportunity_costs:
            hidden_costs.append(opportunity_costs)

        self.hidden_costs = hidden_costs
        return hidden_costs

    def _estimate_integration_costs(self) -> Dict[str, Any]:
        """Estimate costs of maintaining integrations"""

        # Apps with low health likely have integration issues
        integration_risky = self.df[self.df['Tech Health'] <= 4]

        if integration_risky.empty:
            return None

        # Estimate 10-15% of cost goes to integration maintenance for unhealthy apps
        integration_overhead = integration_risky['Cost'].sum() * 0.12

        return {
            'category': 'Integration Complexity',
            'estimated_annual_cost': round(integration_overhead, 2),
            'affected_apps': len(integration_risky),
            'description': 'Annual cost of maintaining fragile integrations',
            'potential_savings': round(integration_overhead * 0.3, 2),  # 30% could be saved
            'recommendation': 'Modernize or consolidate apps with low health scores to reduce integration overhead'
        }

    def _estimate_redundancy_costs(self) -> Dict[str, Any]:
        """Estimate costs of redundant applications"""

        # Group by category and identify potential redundancy
        category_counts = self.df.groupby('Category').size()
        redundant_categories = category_counts[category_counts >= 3]

        if redundant_categories.empty:
            return None

        redundant_apps = self.df[self.df['Category'].isin(redundant_categories.index)]
        redundancy_cost = redundant_apps['Cost'].sum()

        # Estimate 20-30% could be saved through consolidation
        potential_savings = redundancy_cost * 0.25

        return {
            'category': 'Application Redundancy',
            'estimated_annual_cost': round(redundancy_cost, 2),
            'affected_apps': len(redundant_apps),
            'affected_categories': len(redundant_categories),
            'description': 'Cost of maintaining redundant or overlapping applications',
            'potential_savings': round(potential_savings, 2),
            'recommendation': f'Review {len(redundant_categories)} categories with 3+ apps for consolidation opportunities'
        }

    def _estimate_technical_debt_costs(self) -> Dict[str, Any]:
        """Estimate costs of technical debt"""

        # Technical debt = low health apps
        tech_debt_apps = self.df[self.df['Tech Health'] <= 5]

        if tech_debt_apps.empty:
            return None

        # Estimate 20% additional maintenance overhead for unhealthy apps
        debt_cost = tech_debt_apps['Cost'].sum() * 0.20

        return {
            'category': 'Technical Debt',
            'estimated_annual_cost': round(debt_cost, 2),
            'affected_apps': len(tech_debt_apps),
            'description': 'Additional maintenance costs due to aging technology',
            'potential_savings': round(debt_cost * 0.7, 2),  # Modernization could save 70%
            'recommendation': 'Prioritize modernization of applications with health scores ≤5'
        }

    def _estimate_training_costs(self) -> Dict[str, Any]:
        """Estimate training and support costs"""

        # Apps with low health typically require more training and support
        high_support_apps = self.df[self.df['Tech Health'] <= 6]

        if high_support_apps.empty:
            return None

        # Estimate 5-8% of cost goes to extra training/support
        training_overhead = high_support_apps['Cost'].sum() * 0.065

        return {
            'category': 'Training & Support',
            'estimated_annual_cost': round(training_overhead, 2),
            'affected_apps': len(high_support_apps),
            'description': 'Excess training costs for difficult-to-use systems',
            'potential_savings': round(training_overhead * 0.5, 2),
            'recommendation': 'Improve UX or replace apps with poor usability'
        }

    def _estimate_opportunity_costs(self) -> Dict[str, Any]:
        """Estimate opportunity costs of low-value applications"""

        # Low business value apps are opportunity costs
        low_value_apps = self.df[self.df['Business Value'] <= 4]

        if low_value_apps.empty:
            return None

        opportunity_cost = low_value_apps['Cost'].sum()

        return {
            'category': 'Opportunity Cost',
            'estimated_annual_cost': round(opportunity_cost, 2),
            'affected_apps': len(low_value_apps),
            'description': 'Budget locked in low-value applications',
            'potential_savings': round(opportunity_cost * 0.6, 2),  # Could reallocate 60%
            'recommendation': 'Retire or replace low-value apps to free budget for strategic initiatives'
        }

    def track_contract_renewals(self) -> List[Dict[str, Any]]:
        """Generate contract renewal tracking (with simulated dates)"""

        renewals = []

        # Since we don't have renewal dates, simulate based on cost and health
        today = datetime.now()

        for idx, app in self.df.iterrows():
            # Simulate renewal date (1-24 months from now)
            months_until = random.randint(1, 24)
            renewal_date = today + timedelta(days=months_until * 30)

            # Renewal risk based on health and value
            health = app['Tech Health']
            value = app['Business Value']

            if health <= 4 and value <= 4:
                risk_level = 'High - Consider retirement'
                recommendation = 'Do not renew - retire application'
            elif health <= 5 and value >= 7:
                risk_level = 'Medium - Modernization needed'
                recommendation = 'Renew short-term, plan modernization'
            elif value <= 4:
                risk_level = 'Medium - Low value'
                recommendation = 'Review business case before renewal'
            else:
                risk_level = 'Low - Good standing'
                recommendation = 'Renew as planned'

            renewals.append({
                'app_name': app['Application Name'],
                'annual_cost': app['Cost'],
                'renewal_date': renewal_date.strftime('%Y-%m-%d'),
                'months_until_renewal': months_until,
                'risk_level': risk_level,
                'tech_health': health,
                'business_value': value,
                'recommendation': recommendation,
                'category': app.get('Category', 'N/A')
            })

        # Sort by renewal date
        renewals.sort(key=lambda x: x['renewal_date'])

        return renewals

    def get_cost_optimization_summary(self) -> Dict[str, Any]:
        """Generate comprehensive cost optimization summary"""

        if not self.tco_data:
            self.calculate_tco_breakdown()

        if not self.hidden_costs:
            self.identify_hidden_costs()

        dept_allocation = self.allocate_costs_by_department()

        # Calculate total potential savings
        total_hidden_cost = sum(h['estimated_annual_cost'] for h in self.hidden_costs)
        total_potential_savings = sum(h['potential_savings'] for h in self.hidden_costs)

        # Quick wins (low effort, high savings)
        quick_wins = self._identify_quick_wins()

        return {
            'current_portfolio_cost': self.df['Cost'].sum(),
            'hidden_costs_total': total_hidden_cost,
            'potential_savings': total_potential_savings,
            'savings_percentage': round((total_potential_savings / self.df['Cost'].sum()) * 100, 1),
            'hidden_cost_categories': self.hidden_costs,
            'department_allocation': dept_allocation,
            'quick_wins': quick_wins,
            'top_opportunities': self._rank_optimization_opportunities()
        }

    def _identify_quick_wins(self) -> List[Dict[str, Any]]:
        """Identify quick win cost optimization opportunities"""

        quick_wins = []

        # 1. High cost, low value apps
        retire_candidates = self.df[
            (self.df['Cost'] > 50000) &
            (self.df['Business Value'] <= 4) &
            (self.df['Tech Health'] <= 4)
        ]

        if not retire_candidates.empty:
            quick_wins.append({
                'opportunity': 'Retire High-Cost, Low-Value Apps',
                'app_count': len(retire_candidates),
                'potential_savings': retire_candidates['Cost'].sum(),
                'effort': 'Low',
                'apps': retire_candidates['Application Name'].tolist()[:5]
            })

        # 2. Redundant low-cost apps
        low_cost_redundant = self.df[
            (self.df['Cost'] < 20000) &
            (self.df['Business Value'] <= 5)
        ]

        if len(low_cost_redundant) >= 5:
            quick_wins.append({
                'opportunity': 'Consolidate Low-Cost Redundant Apps',
                'app_count': len(low_cost_redundant),
                'potential_savings': low_cost_redundant['Cost'].sum() * 0.3,
                'effort': 'Low',
                'apps': low_cost_redundant['Application Name'].tolist()[:5]
            })

        return quick_wins

    def _rank_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """Rank all cost optimization opportunities by impact"""

        opportunities = []

        # Retirement opportunities
        retire_savings = self.df[self.df['Business Value'] <= 4]['Cost'].sum()
        opportunities.append({
            'category': 'Application Retirement',
            'potential_savings': retire_savings,
            'effort': 'Low-Medium',
            'timeframe': '3-6 months',
            'priority': 1 if retire_savings > 500000 else 2
        })

        # Consolidation opportunities
        consolidate_candidates = self.df[self.df['Tech Health'] <= 6]
        consolidate_savings = consolidate_candidates['Cost'].sum() * 0.25
        opportunities.append({
            'category': 'Application Consolidation',
            'potential_savings': consolidate_savings,
            'effort': 'Medium',
            'timeframe': '6-12 months',
            'priority': 1 if consolidate_savings > 1000000 else 2
        })

        # Modernization opportunities
        modernize_candidates = self.df[
            (self.df['Tech Health'] <= 5) & (self.df['Business Value'] >= 7)
        ]
        modernize_savings = modernize_candidates['Cost'].sum() * 0.15  # Maintenance reduction
        opportunities.append({
            'category': 'Application Modernization',
            'potential_savings': modernize_savings,
            'effort': 'High',
            'timeframe': '12-24 months',
            'priority': 1 if len(modernize_candidates) > 0 else 3
        })

        # Sort by priority then savings
        opportunities.sort(key=lambda x: (x['priority'], -x['potential_savings']))

        return opportunities
