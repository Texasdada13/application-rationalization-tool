"""
What-If Scenario Analysis Engine
Interactive simulation of portfolio rationalization scenarios
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any
from datetime import datetime


class WhatIfScenarioEngine:
    """
    Interactive scenario simulator for portfolio rationalization
    Allows users to test "what if we retire/modernize these apps?" questions
    """

    def __init__(self, df_applications):
        """Initialize with application portfolio data"""
        self.df = df_applications.copy()
        self.baseline = self._calculate_baseline_metrics()

    def _calculate_baseline_metrics(self):
        """Calculate current state metrics as baseline"""
        return {
            'total_apps': len(self.df),
            'total_cost': float(self.df['Cost'].sum()),
            'avg_health': float(self.df['Tech Health'].mean()),
            'avg_value': float(self.df['Business Value'].mean()),
            'avg_security': float(self.df['Security'].mean()) if 'Security' in self.df.columns else 0,
            'total_redundancy_count': int(self.df['Redundancy'].sum()) if 'Redundancy' in self.df.columns else 0,
            'risk_score': self._calculate_portfolio_risk(self.df)
        }

    def _calculate_portfolio_risk(self, df):
        """Calculate overall portfolio risk score (0-100, lower is better)"""
        if df.empty:
            return 0

        # Risk factors
        health_risk = (10 - df['Tech Health'].mean()) * 10  # Low health = high risk
        security_risk = (10 - df['Security'].mean()) * 10 if 'Security' in df.columns else 0
        redundancy_risk = (df['Redundancy'].sum() / len(df)) * 20 if 'Redundancy' in df.columns else 0

        # Weighted risk score
        total_risk = (health_risk * 0.5) + (security_risk * 0.3) + (redundancy_risk * 0.2)

        return round(min(100, max(0, total_risk)), 1)

    def simulate_retirement(self, app_names: List[str]):
        """
        Simulate retiring a list of applications
        Returns impact analysis
        """
        if not app_names:
            return self._create_scenario_result('retirement', [], self.baseline, self.baseline)

        # Filter out apps to be retired
        retired_apps = self.df[self.df['Application Name'].isin(app_names)]
        remaining_apps = self.df[~self.df['Application Name'].isin(app_names)]

        # Calculate new metrics
        new_metrics = {
            'total_apps': len(remaining_apps),
            'total_cost': float(remaining_apps['Cost'].sum()),
            'avg_health': float(remaining_apps['Tech Health'].mean()) if len(remaining_apps) > 0 else 0,
            'avg_value': float(remaining_apps['Business Value'].mean()) if len(remaining_apps) > 0 else 0,
            'avg_security': float(remaining_apps['Security'].mean()) if 'Security' in remaining_apps.columns and len(remaining_apps) > 0 else 0,
            'total_redundancy_count': int(remaining_apps['Redundancy'].sum()) if 'Redundancy' in remaining_apps.columns else 0,
            'risk_score': self._calculate_portfolio_risk(remaining_apps)
        }

        # Calculate impact
        impact = self._calculate_impact(self.baseline, new_metrics)

        # Calculate retirement details
        retirement_details = {
            'apps_retired': len(retired_apps),
            'cost_savings': float(retired_apps['Cost'].sum()),
            'avg_retired_health': float(retired_apps['Tech Health'].mean()),
            'avg_retired_value': float(retired_apps['Business Value'].mean()),
            'retired_apps': retired_apps[['Application Name', 'Cost', 'Tech Health', 'Business Value']].to_dict('records')
        }

        return self._create_scenario_result('retirement', app_names, new_metrics, impact, retirement_details)

    def simulate_modernization(self, app_names: List[str], health_improvement: float = 3.0):
        """
        Simulate modernizing applications (improving tech health)
        Returns impact analysis
        """
        if not app_names:
            return self._create_scenario_result('modernization', [], self.baseline, self.baseline)

        # Copy dataframe and improve health for selected apps
        modernized_df = self.df.copy()
        mask = modernized_df['Application Name'].isin(app_names)

        # Store original values
        original_health = modernized_df.loc[mask, 'Tech Health'].copy()

        # Improve tech health (cap at 10)
        modernized_df.loc[mask, 'Tech Health'] = modernized_df.loc[mask, 'Tech Health'].apply(
            lambda x: min(10, x + health_improvement)
        )

        # Improve security score as well (40% of health improvement)
        if 'Security' in modernized_df.columns:
            modernized_df.loc[mask, 'Security'] = modernized_df.loc[mask, 'Security'].apply(
                lambda x: min(10, x + (health_improvement * 0.4))
            )

        # Calculate modernization cost (estimate: 15% of annual cost per health point improvement)
        modernized_apps = self.df[mask]
        modernization_cost = sum(
            modernized_apps['Cost'] * 0.15 * health_improvement
        )

        # Calculate new metrics
        new_metrics = {
            'total_apps': len(modernized_df),
            'total_cost': float(modernized_df['Cost'].sum()),  # Ongoing cost stays same
            'avg_health': float(modernized_df['Tech Health'].mean()),
            'avg_value': float(modernized_df['Business Value'].mean()),
            'avg_security': float(modernized_df['Security'].mean()) if 'Security' in modernized_df.columns else 0,
            'total_redundancy_count': int(modernized_df['Redundancy'].sum()) if 'Redundancy' in modernized_df.columns else 0,
            'risk_score': self._calculate_portfolio_risk(modernized_df)
        }

        # Calculate impact
        impact = self._calculate_impact(self.baseline, new_metrics)

        # Modernization details
        modernization_details = {
            'apps_modernized': len(modernized_apps),
            'one_time_cost': round(modernization_cost, 2),
            'health_improvement': health_improvement,
            'avg_original_health': float(original_health.mean()),
            'avg_new_health': float(modernized_df.loc[mask, 'Tech Health'].mean()),
            'modernized_apps': modernized_apps[['Application Name', 'Cost', 'Tech Health', 'Business Value']].to_dict('records')
        }

        return self._create_scenario_result('modernization', app_names, new_metrics, impact, modernization_details)

    def simulate_consolidation(self, app_groups: List[List[str]], consolidation_cost_reduction: float = 0.30):
        """
        Simulate consolidating redundant applications
        app_groups: List of lists, where each inner list is apps to consolidate into one
        consolidation_cost_reduction: % cost reduction from consolidation (default 30%)
        """
        if not app_groups:
            return self._create_scenario_result('consolidation', [], self.baseline, self.baseline)

        consolidated_df = self.df.copy()
        total_cost_saved = 0
        apps_eliminated = []
        consolidation_cost = 0

        for group in app_groups:
            if len(group) <= 1:
                continue

            # Get apps in this consolidation group
            group_apps = self.df[self.df['Application Name'].isin(group)]

            # Total cost of group
            group_cost = group_apps['Cost'].sum()

            # After consolidation: keep highest value app, retire others
            # New cost = best app cost + (30% reduction from consolidation)
            best_app = group_apps.loc[group_apps['Business Value'].idxmax()]
            new_cost = best_app['Cost'] * (1 - consolidation_cost_reduction)

            cost_saved = group_cost - new_cost
            total_cost_saved += cost_saved

            # One-time consolidation cost (estimate: 50% of first-year savings)
            consolidation_cost += cost_saved * 0.5

            # Remove consolidated apps (except the primary one)
            apps_to_remove = [app for app in group if app != best_app['Application Name']]
            apps_eliminated.extend(apps_to_remove)
            consolidated_df = consolidated_df[~consolidated_df['Application Name'].isin(apps_to_remove)]

            # Update cost for the remaining app
            consolidated_df.loc[consolidated_df['Application Name'] == best_app['Application Name'], 'Cost'] = new_cost

        # Calculate new metrics
        new_metrics = {
            'total_apps': len(consolidated_df),
            'total_cost': float(consolidated_df['Cost'].sum()),
            'avg_health': float(consolidated_df['Tech Health'].mean()),
            'avg_value': float(consolidated_df['Business Value'].mean()),
            'avg_security': float(consolidated_df['Security'].mean()) if 'Security' in consolidated_df.columns else 0,
            'total_redundancy_count': int(consolidated_df['Redundancy'].sum()) if 'Redundancy' in consolidated_df.columns else 0,
            'risk_score': self._calculate_portfolio_risk(consolidated_df)
        }

        # Calculate impact
        impact = self._calculate_impact(self.baseline, new_metrics)

        # Consolidation details
        consolidation_details = {
            'groups_consolidated': len([g for g in app_groups if len(g) > 1]),
            'apps_eliminated': len(apps_eliminated),
            'annual_savings': round(total_cost_saved, 2),
            'one_time_cost': round(consolidation_cost, 2),
            'eliminated_apps': apps_eliminated
        }

        all_consolidated_apps = [app for group in app_groups for app in group]

        return self._create_scenario_result('consolidation', all_consolidated_apps, new_metrics, impact, consolidation_details)

    def simulate_combined_scenario(self, scenarios: List[Dict[str, Any]]):
        """
        Simulate a combined scenario with multiple actions
        scenarios: List of scenario dicts with 'type' and 'apps' keys
        Example: [
            {'type': 'retire', 'apps': ['App1', 'App2']},
            {'type': 'modernize', 'apps': ['App3'], 'health_improvement': 4},
            {'type': 'consolidate', 'app_groups': [['App4', 'App5']]},
        ]
        """
        if not scenarios:
            return self._create_scenario_result('combined', [], self.baseline, self.baseline)

        working_df = self.df.copy()
        total_cost_saved = 0
        total_one_time_cost = 0
        actions_summary = []

        for scenario in scenarios:
            scenario_type = scenario.get('type')

            if scenario_type == 'retire':
                apps = scenario.get('apps', [])
                if apps:
                    retired = working_df[working_df['Application Name'].isin(apps)]
                    total_cost_saved += retired['Cost'].sum()
                    working_df = working_df[~working_df['Application Name'].isin(apps)]
                    actions_summary.append(f"Retired {len(apps)} applications")

            elif scenario_type == 'modernize':
                apps = scenario.get('apps', [])
                health_improvement = scenario.get('health_improvement', 3.0)
                if apps:
                    mask = working_df['Application Name'].isin(apps)
                    modernized_apps = working_df[mask]
                    modernization_cost = sum(modernized_apps['Cost'] * 0.15 * health_improvement)
                    total_one_time_cost += modernization_cost

                    working_df.loc[mask, 'Tech Health'] = working_df.loc[mask, 'Tech Health'].apply(
                        lambda x: min(10, x + health_improvement)
                    )
                    if 'Security' in working_df.columns:
                        working_df.loc[mask, 'Security'] = working_df.loc[mask, 'Security'].apply(
                            lambda x: min(10, x + (health_improvement * 0.4))
                        )
                    actions_summary.append(f"Modernized {len(apps)} applications (+{health_improvement} health)")

            elif scenario_type == 'consolidate':
                app_groups = scenario.get('app_groups', [])
                consolidation_cost_reduction = scenario.get('cost_reduction', 0.30)

                for group in app_groups:
                    if len(group) <= 1:
                        continue

                    group_apps = working_df[working_df['Application Name'].isin(group)]
                    group_cost = group_apps['Cost'].sum()
                    best_app = group_apps.loc[group_apps['Business Value'].idxmax()]
                    new_cost = best_app['Cost'] * (1 - consolidation_cost_reduction)

                    cost_saved = group_cost - new_cost
                    total_cost_saved += cost_saved
                    total_one_time_cost += cost_saved * 0.5

                    apps_to_remove = [app for app in group if app != best_app['Application Name']]
                    working_df = working_df[~working_df['Application Name'].isin(apps_to_remove)]
                    working_df.loc[working_df['Application Name'] == best_app['Application Name'], 'Cost'] = new_cost

                actions_summary.append(f"Consolidated {len(app_groups)} groups")

        # Calculate new metrics
        new_metrics = {
            'total_apps': len(working_df),
            'total_cost': float(working_df['Cost'].sum()),
            'avg_health': float(working_df['Tech Health'].mean()) if len(working_df) > 0 else 0,
            'avg_value': float(working_df['Business Value'].mean()) if len(working_df) > 0 else 0,
            'avg_security': float(working_df['Security'].mean()) if 'Security' in working_df.columns and len(working_df) > 0 else 0,
            'total_redundancy_count': int(working_df['Redundancy'].sum()) if 'Redundancy' in working_df.columns else 0,
            'risk_score': self._calculate_portfolio_risk(working_df)
        }

        # Calculate impact
        impact = self._calculate_impact(self.baseline, new_metrics)

        # Combined scenario details
        combined_details = {
            'actions_performed': len(scenarios),
            'actions_summary': actions_summary,
            'total_annual_savings': round(total_cost_saved, 2),
            'total_one_time_cost': round(total_one_time_cost, 2),
            'net_first_year_impact': round(total_cost_saved - total_one_time_cost, 2),
            'roi_percentage': round((total_cost_saved / total_one_time_cost * 100), 1) if total_one_time_cost > 0 else 0
        }

        return self._create_scenario_result('combined', [], new_metrics, impact, combined_details)

    def _calculate_impact(self, baseline, new_metrics):
        """Calculate the delta/impact between baseline and new metrics"""
        return {
            'apps_change': new_metrics['total_apps'] - baseline['total_apps'],
            'apps_change_pct': round(((new_metrics['total_apps'] - baseline['total_apps']) / baseline['total_apps'] * 100), 1) if baseline['total_apps'] > 0 else 0,

            'cost_change': new_metrics['total_cost'] - baseline['total_cost'],
            'cost_change_pct': round(((new_metrics['total_cost'] - baseline['total_cost']) / baseline['total_cost'] * 100), 1) if baseline['total_cost'] > 0 else 0,

            'health_change': round(new_metrics['avg_health'] - baseline['avg_health'], 2),
            'health_change_pct': round(((new_metrics['avg_health'] - baseline['avg_health']) / baseline['avg_health'] * 100), 1) if baseline['avg_health'] > 0 else 0,

            'value_change': round(new_metrics['avg_value'] - baseline['avg_value'], 2),
            'value_change_pct': round(((new_metrics['avg_value'] - baseline['avg_value']) / baseline['avg_value'] * 100), 1) if baseline['avg_value'] > 0 else 0,

            'security_change': round(new_metrics['avg_security'] - baseline['avg_security'], 2),
            'security_change_pct': round(((new_metrics['avg_security'] - baseline['avg_security']) / baseline['avg_security'] * 100), 1) if baseline['avg_security'] > 0 else 0,

            'risk_change': round(new_metrics['risk_score'] - baseline['risk_score'], 2),
            'risk_change_pct': round(((new_metrics['risk_score'] - baseline['risk_score']) / baseline['risk_score'] * 100), 1) if baseline['risk_score'] > 0 else 0,
        }

    def _create_scenario_result(self, scenario_type, app_names, new_metrics, impact, details=None):
        """Create standardized scenario result object"""
        return {
            'scenario_type': scenario_type,
            'timestamp': datetime.now().isoformat(),
            'apps_affected': app_names,
            'baseline': self.baseline,
            'new_state': new_metrics,
            'impact': impact,
            'details': details or {}
        }

    def get_recommended_scenarios(self):
        """Generate 3-5 recommended scenarios based on portfolio analysis"""
        recommendations = []

        # Scenario 1: Retire low-value, low-health apps
        retire_candidates = self.df[
            (self.df['Tech Health'] <= 3) &
            (self.df['Business Value'] <= 4)
        ]

        if len(retire_candidates) > 0:
            recommendations.append({
                'name': 'Aggressive Retirement',
                'description': f'Retire {len(retire_candidates)} low-value, poor-health applications',
                'apps': retire_candidates['Application Name'].tolist(),
                'type': 'retire',
                'estimated_savings': round(retire_candidates['Cost'].sum(), 2)
            })

        # Scenario 2: Modernize critical apps with poor health
        modernize_candidates = self.df[
            (self.df['Tech Health'] <= 5) &
            (self.df['Business Value'] >= 7)
        ]

        if len(modernize_candidates) > 0:
            recommendations.append({
                'name': 'Critical Modernization',
                'description': f'Modernize {len(modernize_candidates)} critical applications with aging tech',
                'apps': modernize_candidates['Application Name'].tolist(),
                'type': 'modernize',
                'estimated_cost': round(sum(modernize_candidates['Cost'] * 0.15 * 3), 2)
            })

        # Scenario 3: Consolidate redundant apps
        if 'Redundancy' in self.df.columns:
            redundant_apps = self.df[self.df['Redundancy'] > 0]
            if len(redundant_apps) >= 4:
                # Group by category for consolidation
                consolidation_groups = []
                for category in redundant_apps['Category'].unique() if 'Category' in redundant_apps.columns else []:
                    category_apps = redundant_apps[redundant_apps['Category'] == category]['Application Name'].tolist()
                    if len(category_apps) >= 2:
                        consolidation_groups.append(category_apps[:4])  # Max 4 per group

                if consolidation_groups:
                    recommendations.append({
                        'name': 'Redundancy Consolidation',
                        'description': f'Consolidate {len(consolidation_groups)} groups of redundant applications',
                        'app_groups': consolidation_groups,
                        'type': 'consolidate'
                    })

        # Scenario 4: Balanced approach (retire some + modernize some)
        retire_some = retire_candidates.nsmallest(10, 'Business Value')['Application Name'].tolist() if len(retire_candidates) >= 10 else []
        modernize_some = modernize_candidates.nlargest(5, 'Business Value')['Application Name'].tolist() if len(modernize_candidates) >= 5 else []

        if retire_some and modernize_some:
            recommendations.append({
                'name': 'Balanced Optimization',
                'description': f'Retire {len(retire_some)} apps + Modernize {len(modernize_some)} critical apps',
                'scenarios': [
                    {'type': 'retire', 'apps': retire_some},
                    {'type': 'modernize', 'apps': modernize_some, 'health_improvement': 3}
                ],
                'type': 'combined'
            })

        return recommendations
