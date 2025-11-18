"""
Smart Recommendations Engine
Generates context-aware, intelligent recommendations beyond simple rules
"""

import pandas as pd
from typing import Dict, List, Any


class SmartRecommendationEngine:
    """Advanced recommendation engine with dependency analysis and context awareness"""

    def __init__(self):
        pass

    def analyze_dependencies(self, df: pd.DataFrame, app_name: str) -> Dict[str, Any]:
        """
        Check if app has critical dependencies that affect recommendation

        Args:
            df: Portfolio DataFrame
            app_name: Name of application to analyze

        Returns:
            Dictionary with dependency information
        """
        # Look for apps that depend on this one
        if 'Dependencies' not in df.columns:
            return {
                'has_dependencies': False,
                'dependent_apps': [],
                'dependency_risk': 'LOW'
            }

        dependent_apps = []
        for idx, row in df.iterrows():
            if pd.notna(row.get('Dependencies', '')):
                # Check if this app is mentioned in dependencies
                if app_name.lower() in str(row['Dependencies']).lower():
                    dependent_apps.append(row['Application Name'])

        return {
            'has_dependencies': len(dependent_apps) > 0,
            'dependent_apps': dependent_apps,
            'dependency_count': len(dependent_apps),
            'dependency_risk': 'HIGH' if len(dependent_apps) > 3 else 'MEDIUM' if len(dependent_apps) > 0 else 'LOW'
        }

    def assess_retirement_feasibility(self, app_row: pd.Series, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Assess how feasible it is to retire this app

        Args:
            app_row: Series representing the application
            df: Full portfolio DataFrame for dependency checking

        Returns:
            Dictionary with feasibility assessment
        """
        score = 100  # Start with perfect score
        reasons = []

        # Check technical health (lower is better for retirement)
        tech_health = app_row['Tech Health']
        if tech_health > 6:
            score -= 20
            reasons.append("App still has good technical health")

        # Check business value (lower is better for retirement)
        business_value = app_row['Business Value']
        if business_value > 7:
            score -= 30
            reasons.append("App has high business value")

        # Check dependencies
        deps = self.analyze_dependencies(df, app_row['Application Name'])
        if deps['has_dependencies']:
            score -= (10 * len(deps['dependent_apps']))
            reasons.append(f"{len(deps['dependent_apps'])} apps depend on this")

        # Check cost (higher cost = more savings = better candidate)
        cost = app_row['Cost']
        if cost < 30000:
            score -= 15
            reasons.append("Low cost - limited savings potential")

        return {
            'feasibility_score': max(0, score),
            'feasibility_rating': 'HIGH' if score > 70 else 'MEDIUM' if score > 40 else 'LOW',
            'blockers': reasons
        }

    def generate_modernization_path(self, app_row: pd.Series) -> Dict[str, Any]:
        """
        Suggest specific modernization approach based on app characteristics

        Args:
            app_row: Series representing the application

        Returns:
            Dictionary with modernization recommendations
        """
        tech_health = app_row['Tech Health']
        business_value = app_row['Business Value']
        cost = app_row['Cost']

        if tech_health < 4:
            if business_value > 7:
                return {
                    'approach': 'REBUILD',
                    'timeline': '12-18 months',
                    'priority': 'HIGH',
                    'estimated_cost': cost * 2,
                    'reason': 'Critical business value with poor technical health requires complete rebuild',
                    'risk_level': 'HIGH'
                }
            else:
                return {
                    'approach': 'REPLACE',
                    'timeline': '6-9 months',
                    'priority': 'MEDIUM',
                    'estimated_cost': cost * 1.5,
                    'reason': 'Low technical health - find COTS replacement',
                    'risk_level': 'MEDIUM'
                }
        elif tech_health < 7:
            return {
                'approach': 'REFACTOR',
                'timeline': '3-6 months',
                'priority': 'MEDIUM',
                'estimated_cost': cost * 0.5,
                'reason': 'Incremental improvements to extend lifespan',
                'risk_level': 'LOW'
            }
        else:
            return {
                'approach': 'ENHANCE',
                'timeline': '1-3 months',
                'priority': 'LOW',
                'estimated_cost': cost * 0.3,
                'reason': 'Add features and optimize existing system',
                'risk_level': 'LOW'
            }

    def suggest_consolidation_opportunities(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Find apps that could be consolidated based on category or function

        Args:
            df: Portfolio DataFrame

        Returns:
            List of consolidation opportunities
        """
        opportunities = []

        # Group by category if available
        if 'Category' in df.columns:
            for category in df['Category'].unique():
                if pd.isna(category):
                    continue

                category_apps = df[df['Category'] == category]
                if len(category_apps) > 2:  # Multiple apps in same category
                    total_cost = category_apps['Cost'].sum()
                    avg_health = category_apps['Tech Health'].mean()
                    avg_value = category_apps['Business Value'].mean()

                    opportunities.append({
                        'category': str(category),
                        'app_count': int(len(category_apps)),
                        'apps': category_apps['Application Name'].tolist(),
                        'total_cost': float(total_cost),
                        'avg_health': float(avg_health),
                        'avg_value': float(avg_value),
                        'potential_savings': float(total_cost * 0.3),  # Assume 30% savings
                        'priority': 'HIGH' if total_cost > 200000 else 'MEDIUM',
                        'consolidation_score': float((total_cost / 100000) * (1 / avg_health))
                    })

        return sorted(opportunities, key=lambda x: x['potential_savings'], reverse=True)[:5]

    def calculate_action_priority(self, app_row: pd.Series) -> str:
        """Calculate priority level for action"""
        tech_health = app_row['Tech Health']
        business_value = app_row['Business Value']
        cost = app_row['Cost']

        # High cost + low health = high priority
        if cost > 100000 and tech_health < 5:
            return 'CRITICAL'
        elif cost > 50000 and tech_health < 6:
            return 'HIGH'
        elif business_value > 7 and tech_health < 6:
            return 'HIGH'
        elif tech_health < 4:
            return 'MEDIUM'
        else:
            return 'LOW'

    def generate_smart_recommendations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate comprehensive smart recommendations for entire portfolio

        Args:
            df: Portfolio DataFrame

        Returns:
            Dictionary with all recommendations and analysis
        """
        recommendations = []

        for idx, app in df.iterrows():
            # Basic recommendation data
            base_rec = {
                'app_name': app['Application Name'],
                'business_value': float(app['Business Value']),
                'technical_health': float(app['Tech Health']),
                'annual_cost': float(app['Cost']),
                'current_recommendation': app.get('Action Recommendation', 'N/A')
            }

            # Calculate priority
            base_rec['priority'] = self.calculate_action_priority(app)

            # Add context-aware analysis based on current recommendation
            current_rec = str(app.get('Action Recommendation', '')).lower()

            if 'retire' in current_rec or 'eliminate' in current_rec:
                feasibility = self.assess_retirement_feasibility(app, df)
                base_rec['retirement_feasibility'] = feasibility
                base_rec['action'] = 'RETIRE' if feasibility['feasibility_score'] > 60 else 'EVALUATE'
                base_rec['confidence'] = 'HIGH' if feasibility['feasibility_score'] > 70 else 'MEDIUM' if feasibility['feasibility_score'] > 40 else 'LOW'

            elif 'invest' in current_rec or app['Business Value'] > 7:
                modernization = self.generate_modernization_path(app)
                base_rec['modernization_path'] = modernization
                base_rec['action'] = 'MODERNIZE'
                base_rec['confidence'] = 'HIGH'

            else:
                base_rec['action'] = 'MAINTAIN'
                base_rec['confidence'] = 'MEDIUM'

            # Add dependency analysis for all apps
            base_rec['dependencies'] = self.analyze_dependencies(df, app['Application Name'])

            recommendations.append(base_rec)

        # Add consolidation opportunities
        consolidation_opps = self.suggest_consolidation_opportunities(df)

        # Calculate summary statistics
        retire_candidates = [r for r in recommendations if r['action'] == 'RETIRE']
        modernize_candidates = [r for r in recommendations if r['action'] == 'MODERNIZE']
        maintain_candidates = [r for r in recommendations if r['action'] == 'MAINTAIN']

        return {
            'individual_recommendations': recommendations,
            'consolidation_opportunities': consolidation_opps,
            'summary': {
                'total_apps': len(recommendations),
                'retire_candidates': len(retire_candidates),
                'modernize_candidates': len(modernize_candidates),
                'maintain_count': len(maintain_candidates),
                'high_priority_count': len([r for r in recommendations if r['priority'] in ['CRITICAL', 'HIGH']]),
                'total_potential_savings': sum([r.get('retirement_feasibility', {}).get('feasibility_score', 0) * r['annual_cost'] / 100 for r in retire_candidates]),
                'consolidation_savings': sum([opp['potential_savings'] for opp in consolidation_opps])
            }
        }
