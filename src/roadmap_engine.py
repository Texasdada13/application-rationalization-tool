"""
Automated Prioritization Roadmap Generator
AI-powered multi-phase roadmap with timeline, effort vs impact analysis, and dependency tracking
"""

import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Any, Tuple
import json


class PrioritizationRoadmapEngine:
    """AI-powered roadmap generator with phase planning and dependency tracking"""

    # Effort scoring weights
    EFFORT_WEIGHTS = {
        'cost': 0.3,          # Higher cost = higher effort
        'integrations': 0.25,  # More integrations = higher effort
        'users': 0.2,         # More users = higher effort (change management)
        'complexity': 0.15,    # Technical complexity
        'age': 0.1            # Older systems may be harder to retire
    }

    # Impact scoring weights
    IMPACT_WEIGHTS = {
        'cost_savings': 0.35,     # Annual cost savings potential
        'health_improvement': 0.25, # Technical health improvement
        'risk_reduction': 0.20,    # Risk mitigation
        'business_value': 0.20     # Business value alignment
    }

    # Phase definitions
    PHASES = {
        'quick_wins': {
            'name': 'Quick Wins',
            'duration_weeks': 12,
            'max_effort': 30,
            'icon': '🎯',
            'description': 'High impact, low effort - deliver immediate value'
        },
        'short_term': {
            'name': 'Short-term Priorities',
            'duration_weeks': 24,
            'max_effort': 50,
            'icon': '🚀',
            'description': 'Critical modernizations and strategic retirements'
        },
        'medium_term': {
            'name': 'Medium-term Initiatives',
            'duration_weeks': 36,
            'max_effort': 70,
            'icon': '🏗️',
            'description': 'Complex consolidations and platform migrations'
        },
        'long_term': {
            'name': 'Long-term Strategy',
            'duration_weeks': 52,
            'max_effort': 100,
            'icon': '🎓',
            'description': 'Strategic transformations and large-scale modernization'
        }
    }

    def __init__(self, df_applications):
        """Initialize with application portfolio data"""
        self.df = df_applications.copy()
        self.actions = []
        self.dependencies = self._extract_dependencies()
        self.roadmap = None

    def _extract_dependencies(self) -> Dict[str, List[str]]:
        """Extract application dependencies from Comments field"""
        dependencies = {}

        for idx, row in self.df.iterrows():
            app_name = row['Application Name']
            comments = str(row.get('Comments', '')).lower()

            # Look for dependency keywords
            deps = []
            if 'depends on' in comments or 'requires' in comments or 'integrates with' in comments:
                # Simple heuristic: look for other app names in comments
                for other_app in self.df['Application Name']:
                    if other_app != app_name and other_app.lower() in comments:
                        deps.append(other_app)

            if deps:
                dependencies[app_name] = deps

        return dependencies

    def calculate_effort_score(self, app_row) -> float:
        """Calculate effort score (0-100) for an action on this application"""

        # Normalize cost (0-100 scale based on portfolio)
        cost_normalized = min(100, (app_row['Cost'] / self.df['Cost'].max()) * 100)

        # Integration complexity (estimate from category and tech health)
        integration_score = 50  # Default medium
        category = str(app_row.get('Category', '')).lower()
        if 'core' in category or 'critical' in category or 'infrastructure' in category:
            integration_score = 80
        elif 'standalone' in category or 'utility' in category:
            integration_score = 20

        # User impact (estimate from business value)
        user_score = app_row['Business Value'] * 10  # Scale to 0-100

        # Complexity (inverse of tech health - poor health = complex to modernize)
        complexity_score = (10 - app_row['Tech Health']) * 10

        # Age factor (assume older = harder, use tech health as proxy)
        age_score = (10 - app_row['Tech Health']) * 10

        # Weighted effort score
        effort = (
            cost_normalized * self.EFFORT_WEIGHTS['cost'] +
            integration_score * self.EFFORT_WEIGHTS['integrations'] +
            user_score * self.EFFORT_WEIGHTS['users'] +
            complexity_score * self.EFFORT_WEIGHTS['complexity'] +
            age_score * self.EFFORT_WEIGHTS['age']
        )

        return round(effort, 1)

    def calculate_impact_score(self, app_row, action_type: str) -> float:
        """Calculate impact score (0-100) for an action"""

        # Cost savings potential
        if action_type == 'retire':
            cost_savings = 100 * (app_row['Cost'] / self.df['Cost'].max())
        elif action_type == 'consolidate':
            cost_savings = 70 * (app_row['Cost'] / self.df['Cost'].max())
        elif action_type == 'modernize':
            cost_savings = 30  # Modernization has lower direct cost savings
        else:
            cost_savings = 0

        # Health improvement potential
        if action_type == 'modernize':
            health_improvement = (10 - app_row['Tech Health']) * 10  # More room for improvement
        elif action_type == 'retire':
            health_improvement = app_row['Tech Health'] * 5  # Removing unhealthy app
        else:
            health_improvement = 50

        # Risk reduction (low health = high risk)
        risk_reduction = (10 - app_row['Tech Health']) * 10

        # Business value alignment
        if action_type == 'modernize' and app_row['Business Value'] >= 7:
            business_value = 90  # High value apps should be modernized
        elif action_type == 'retire' and app_row['Business Value'] <= 4:
            business_value = 80  # Low value apps should be retired
        else:
            business_value = app_row['Business Value'] * 10

        # Weighted impact score
        impact = (
            cost_savings * self.IMPACT_WEIGHTS['cost_savings'] +
            health_improvement * self.IMPACT_WEIGHTS['health_improvement'] +
            risk_reduction * self.IMPACT_WEIGHTS['risk_reduction'] +
            business_value * self.IMPACT_WEIGHTS['business_value']
        )

        return round(impact, 1)

    def identify_actions(self) -> List[Dict[str, Any]]:
        """Identify all recommended actions across the portfolio"""
        actions = []

        for idx, app_row in self.df.iterrows():
            app_name = app_row['Application Name']
            health = app_row['Tech Health']
            value = app_row['Business Value']
            cost = app_row['Cost']

            # Retirement candidates: Low health + Low value
            if health <= 3 and value <= 4:
                effort = self.calculate_effort_score(app_row)
                impact = self.calculate_impact_score(app_row, 'retire')

                actions.append({
                    'app_name': app_name,
                    'action_type': 'retire',
                    'effort': effort,
                    'impact': impact,
                    'priority_score': impact - (effort * 0.5),  # Prioritize high impact, low effort
                    'cost': cost,
                    'health': health,
                    'value': value,
                    'rationale': f'Low health ({health}/10) and low business value ({value}/10) - retirement candidate',
                    'estimated_savings': cost,
                    'dependencies': self.dependencies.get(app_name, [])
                })

            # Modernization candidates: High value + Low health
            elif health <= 5 and value >= 7:
                effort = self.calculate_effort_score(app_row) * 1.2  # Modernization is harder
                impact = self.calculate_impact_score(app_row, 'modernize')

                actions.append({
                    'app_name': app_name,
                    'action_type': 'modernize',
                    'effort': min(100, effort),
                    'impact': impact,
                    'priority_score': impact - (effort * 0.5),
                    'cost': cost,
                    'health': health,
                    'value': value,
                    'rationale': f'Critical application (value {value}/10) with aging technology (health {health}/10)',
                    'estimated_savings': cost * 0.2,  # Maintenance reduction
                    'dependencies': self.dependencies.get(app_name, [])
                })

            # Consolidation candidates: Redundant or overlapping functionality
            elif value <= 6 and health <= 6 and cost > 50000:
                effort = self.calculate_effort_score(app_row) * 0.9
                impact = self.calculate_impact_score(app_row, 'consolidate')

                actions.append({
                    'app_name': app_name,
                    'action_type': 'consolidate',
                    'effort': effort,
                    'impact': impact,
                    'priority_score': impact - (effort * 0.5),
                    'cost': cost,
                    'health': health,
                    'value': value,
                    'rationale': f'Moderate value and health with significant cost (${cost:,.0f}) - consolidation opportunity',
                    'estimated_savings': cost * 0.3,
                    'dependencies': self.dependencies.get(app_name, [])
                })

        # Sort by priority score
        actions.sort(key=lambda x: x['priority_score'], reverse=True)

        self.actions = actions
        return actions

    def assign_to_phases(self) -> Dict[str, List[Dict[str, Any]]]:
        """Assign actions to roadmap phases based on effort and impact"""

        if not self.actions:
            self.identify_actions()

        phases = {
            'quick_wins': [],
            'short_term': [],
            'medium_term': [],
            'long_term': []
        }

        # Track cumulative effort per phase
        phase_effort = {phase: 0 for phase in phases.keys()}

        for action in self.actions:
            effort = action['effort']

            # Check for dependency blockers
            blocked = False
            for dep in action['dependencies']:
                # If this app depends on something we're planning to retire, it's blocked
                if any(a['app_name'] == dep and a['action_type'] == 'retire' for a in self.actions):
                    blocked = True
                    action['blocked_by'] = dep
                    break

            # Assign to appropriate phase
            if effort <= 30 and not blocked:
                phases['quick_wins'].append(action)
                phase_effort['quick_wins'] += effort
            elif effort <= 50 and not blocked:
                phases['short_term'].append(action)
                phase_effort['short_term'] += effort
            elif effort <= 70:
                phases['medium_term'].append(action)
                phase_effort['medium_term'] += effort
            else:
                phases['long_term'].append(action)
                phase_effort['long_term'] += effort

        return phases

    def generate_timeline(self) -> List[Dict[str, Any]]:
        """Generate timeline with start/end dates for each phase"""

        phases_data = self.assign_to_phases()

        timeline = []
        start_date = datetime.now()

        for phase_key in ['quick_wins', 'short_term', 'medium_term', 'long_term']:
            phase_config = self.PHASES[phase_key]
            phase_actions = phases_data[phase_key]

            end_date = start_date + timedelta(weeks=phase_config['duration_weeks'])

            # Calculate phase metrics
            total_savings = sum(a['estimated_savings'] for a in phase_actions)
            total_apps = len(phase_actions)
            avg_impact = sum(a['impact'] for a in phase_actions) / total_apps if total_apps > 0 else 0

            timeline.append({
                'phase': phase_key,
                'name': phase_config['name'],
                'icon': phase_config['icon'],
                'description': phase_config['description'],
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'duration_weeks': phase_config['duration_weeks'],
                'actions': phase_actions,
                'total_actions': total_apps,
                'total_savings': total_savings,
                'avg_impact': round(avg_impact, 1),
                'milestones': self._generate_milestones(phase_actions, phase_config['name'])
            })

            # Next phase starts after current ends
            start_date = end_date + timedelta(days=1)

        return timeline

    def _generate_milestones(self, actions: List[Dict], phase_name: str) -> List[Dict]:
        """Generate milestones for a phase"""
        milestones = []

        if not actions:
            return milestones

        # Milestone: Phase kickoff
        milestones.append({
            'name': f'{phase_name} Kickoff',
            'description': 'Phase planning and resource allocation',
            'success_metric': 'Teams assigned and timeline confirmed'
        })

        # Milestone: High-impact actions completed
        high_impact_actions = [a for a in actions if a['impact'] >= 70]
        if high_impact_actions:
            milestones.append({
                'name': 'High-Impact Actions Completed',
                'description': f'{len(high_impact_actions)} critical actions delivered',
                'success_metric': f'${sum(a["estimated_savings"] for a in high_impact_actions):,.0f} in savings realized'
            })

        # Milestone: Phase completion
        total_savings = sum(a['estimated_savings'] for a in actions)
        milestones.append({
            'name': f'{phase_name} Complete',
            'description': f'All {len(actions)} actions delivered',
            'success_metric': f'${total_savings:,.0f} annual savings achieved'
        })

        return milestones

    def get_effort_impact_matrix(self) -> List[Dict[str, Any]]:
        """Get data for effort vs impact scatter plot"""

        if not self.actions:
            self.identify_actions()

        matrix_data = []

        for action in self.actions:
            matrix_data.append({
                'app_name': action['app_name'],
                'action_type': action['action_type'],
                'effort': action['effort'],
                'impact': action['impact'],
                'priority_score': action['priority_score'],
                'estimated_savings': action['estimated_savings'],
                'quadrant': self._get_quadrant(action['effort'], action['impact'])
            })

        return matrix_data

    def _get_quadrant(self, effort: float, impact: float) -> str:
        """Determine which quadrant an action falls into"""

        if impact >= 60 and effort <= 40:
            return 'Quick Wins'
        elif impact >= 60 and effort > 40:
            return 'Strategic Priorities'
        elif impact < 60 and effort <= 40:
            return 'Low Priority'
        else:
            return 'Reconsider'

    def generate_executive_summary(self) -> Dict[str, Any]:
        """Generate executive summary of the roadmap"""

        timeline = self.generate_timeline()

        # Calculate totals
        total_actions = sum(phase['total_actions'] for phase in timeline)
        total_savings = sum(phase['total_savings'] for phase in timeline)

        # Count by action type
        action_counts = defaultdict(int)
        for action in self.actions:
            action_counts[action['action_type']] += 1

        # Quick wins highlight
        quick_wins = timeline[0]['actions']
        quick_wins_savings = timeline[0]['total_savings']

        # High-risk apps (dependencies)
        blocked_actions = [a for a in self.actions if 'blocked_by' in a]

        return {
            'total_actions': total_actions,
            'total_savings': total_savings,
            'duration_months': sum(phase['duration_weeks'] for phase in timeline) / 4,
            'action_breakdown': dict(action_counts),
            'quick_wins_count': len(quick_wins),
            'quick_wins_savings': quick_wins_savings,
            'blocked_actions': len(blocked_actions),
            'avg_impact': round(sum(a['impact'] for a in self.actions) / len(self.actions), 1) if self.actions else 0,
            'phases': len(timeline),
            'timeline': timeline
        }

    def get_dependency_warnings(self) -> List[Dict[str, Any]]:
        """Get list of dependency conflicts that need attention"""

        if not self.actions:
            self.identify_actions()

        warnings = []

        for action in self.actions:
            if 'blocked_by' in action:
                warnings.append({
                    'app_name': action['app_name'],
                    'action_type': action['action_type'],
                    'blocked_by': action['blocked_by'],
                    'severity': 'high' if action['impact'] >= 70 else 'medium',
                    'recommendation': f"Review dependency on {action['blocked_by']} before proceeding"
                })

        return warnings

    def export_roadmap_json(self) -> str:
        """Export complete roadmap as JSON"""

        roadmap_data = {
            'generated_at': datetime.now().isoformat(),
            'executive_summary': self.generate_executive_summary(),
            'timeline': self.generate_timeline(),
            'effort_impact_matrix': self.get_effort_impact_matrix(),
            'dependency_warnings': self.get_dependency_warnings(),
            'all_actions': self.actions
        }

        return json.dumps(roadmap_data, indent=2)
