"""
Integration & Dependency Mapper
Visual dependency graph, hub identification, blast radius calculation, critical path analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Set
from collections import defaultdict, deque
import re


class IntegrationMapper:
    """Map application dependencies and integration relationships"""

    def __init__(self, df_applications: pd.DataFrame):
        """Initialize with application portfolio data"""
        self.df = df_applications.copy()
        self.dependency_graph = defaultdict(list)  # app -> [dependencies]
        self.reverse_graph = defaultdict(list)     # app -> [dependents]
        self.integration_map = {}
        self.hub_apps = []
        self.critical_path = []

    @staticmethod
    def _to_native_types(value):
        """Convert numpy/pandas types to native Python types"""
        if hasattr(value, 'item'):
            return value.item()
        return value

    def extract_dependencies(self) -> Dict[str, List[str]]:
        """Extract dependencies from Comments and Dependencies columns"""

        all_apps = set(self.df['Application Name'].tolist())

        for idx, app_row in self.df.iterrows():
            app_name = app_row['Application Name']
            dependencies = []

            # Check Dependencies column if exists
            if 'Dependencies' in self.df.columns and pd.notna(app_row.get('Dependencies')):
                deps_text = str(app_row['Dependencies']).lower()

                # Look for other app names
                for other_app in all_apps:
                    if other_app != app_name and other_app.lower() in deps_text:
                        dependencies.append(other_app)

            # Also check Comments field
            if 'Comments' in self.df.columns and pd.notna(app_row.get('Comments')):
                comments = str(app_row['Comments']).lower()

                # Look for dependency keywords
                if any(keyword in comments for keyword in ['depends on', 'requires', 'integrates with', 'uses']):
                    for other_app in all_apps:
                        if other_app != app_name and other_app.lower() in comments:
                            if other_app not in dependencies:
                                dependencies.append(other_app)

            if dependencies:
                self.dependency_graph[app_name] = dependencies

                # Build reverse graph
                for dep in dependencies:
                    self.reverse_graph[dep].append(app_name)

        return dict(self.dependency_graph)

    def identify_hub_applications(self) -> List[Dict[str, Any]]:
        """Identify hub applications with many connections"""

        if not self.dependency_graph:
            self.extract_dependencies()

        hub_scores = {}

        for app in self.df['Application Name']:
            # Count incoming connections (how many apps depend on this)
            incoming = len(self.reverse_graph.get(app, []))

            # Count outgoing connections (how many apps this depends on)
            outgoing = len(self.dependency_graph.get(app, []))

            # Total connections
            total_connections = incoming + outgoing

            if total_connections > 0:
                app_data = self.df[self.df['Application Name'] == app].iloc[0]

                hub_scores[app] = {
                    'app_name': app,
                    'total_connections': total_connections,
                    'incoming': incoming,
                    'outgoing': outgoing,
                    'hub_score': total_connections,
                    'health': self._to_native_types(app_data['Tech Health']),
                    'value': self._to_native_types(app_data['Business Value']),
                    'cost': self._to_native_types(app_data['Cost']),
                    'risk_level': self._calculate_hub_risk(incoming, outgoing, app_data['Tech Health'])
                }

        # Sort by hub score
        sorted_hubs = sorted(hub_scores.values(), key=lambda x: x['hub_score'], reverse=True)

        # Top 10 hubs
        self.hub_apps = sorted_hubs[:10]

        return self.hub_apps

    def _calculate_hub_risk(self, incoming: int, outgoing: int, health: float) -> str:
        """Calculate risk level for hub applications"""

        # High incoming + low health = critical risk
        if incoming >= 5 and health <= 4:
            return 'Critical - Many dependents with poor health'
        elif incoming >= 3 and health <= 5:
            return 'High - Multiple dependents with aging tech'
        elif incoming >= 5:
            return 'Medium - Many dependents but healthy'
        elif outgoing >= 5 and health <= 5:
            return 'Medium - Highly dependent with aging tech'
        else:
            return 'Low - Limited dependencies'

    def calculate_blast_radius(self, app_name: str) -> Dict[str, Any]:
        """Calculate blast radius if this app is retired or fails"""

        if not self.dependency_graph:
            self.extract_dependencies()

        if app_name not in self.df['Application Name'].values:
            return {'error': 'Application not found'}

        # Find all apps that depend on this one (directly or indirectly)
        affected_apps = self._find_all_dependents(app_name)

        # Calculate impact metrics
        affected_data = self.df[self.df['Application Name'].isin(affected_apps)]

        total_cost = affected_data['Cost'].sum()
        total_apps = len(affected_apps)
        avg_health = affected_data['Tech Health'].mean() if total_apps > 0 else 0
        avg_value = affected_data['Business Value'].mean() if total_apps > 0 else 0

        # Get app info
        app_data = self.df[self.df['Application Name'] == app_name].iloc[0]

        return {
            'app_name': app_name,
            'app_health': app_data['Tech Health'],
            'app_value': app_data['Business Value'],
            'app_cost': app_data['Cost'],
            'directly_affected': len(self.reverse_graph.get(app_name, [])),
            'total_affected': total_apps,
            'affected_apps': affected_apps,
            'total_cost_at_risk': total_cost,
            'avg_affected_health': round(avg_health, 1),
            'avg_affected_value': round(avg_value, 1),
            'risk_category': self._categorize_blast_radius(total_apps, total_cost, avg_value)
        }

    def _find_all_dependents(self, app_name: str, visited: Set[str] = None) -> List[str]:
        """Recursively find all apps that depend on this one"""

        if visited is None:
            visited = set()

        if app_name in visited:
            return []

        visited.add(app_name)
        dependents = []

        # Get direct dependents
        direct = self.reverse_graph.get(app_name, [])

        for dep in direct:
            if dep not in visited:
                dependents.append(dep)
                # Recursively get their dependents
                indirect = self._find_all_dependents(dep, visited)
                dependents.extend([d for d in indirect if d not in dependents])

        return dependents

    def _categorize_blast_radius(self, affected_count: int, total_cost: float, avg_value: float) -> str:
        """Categorize blast radius severity"""

        if affected_count >= 10 or total_cost > 2000000 or avg_value >= 8:
            return 'Critical - Wide-reaching impact'
        elif affected_count >= 5 or total_cost > 1000000 or avg_value >= 7:
            return 'High - Significant impact'
        elif affected_count >= 2 or total_cost > 500000:
            return 'Medium - Moderate impact'
        else:
            return 'Low - Limited impact'

    def find_critical_path(self) -> List[Dict[str, Any]]:
        """Identify critical path - longest dependency chain"""

        if not self.dependency_graph:
            self.extract_dependencies()

        # Find longest path using DFS
        longest_path = []
        max_length = 0

        all_apps = set(self.df['Application Name'].tolist())

        for app in all_apps:
            path = self._dfs_longest_path(app, set())
            if len(path) > max_length:
                max_length = len(path)
                longest_path = path

        # Enhance with app data
        critical_path_data = []
        for app_name in longest_path:
            app_data = self.df[self.df['Application Name'] == app_name].iloc[0]

            critical_path_data.append({
                'app_name': app_name,
                'health': app_data['Tech Health'],
                'value': app_data['Business Value'],
                'cost': app_data['Cost'],
                'dependencies': self.dependency_graph.get(app_name, []),
                'dependents': self.reverse_graph.get(app_name, [])
            })

        self.critical_path = critical_path_data

        return {
            'path_length': len(critical_path_data),
            'total_cost': sum(app['cost'] for app in critical_path_data),
            'avg_health': round(sum(app['health'] for app in critical_path_data) / len(critical_path_data), 1) if critical_path_data else 0,
            'weakest_link': min(critical_path_data, key=lambda x: x['health']) if critical_path_data else None,
            'path': critical_path_data
        }

    def _dfs_longest_path(self, start: str, visited: Set[str]) -> List[str]:
        """DFS to find longest dependency path"""

        visited.add(start)
        longest = [start]

        for dep in self.dependency_graph.get(start, []):
            if dep not in visited:
                path = self._dfs_longest_path(dep, visited.copy())
                candidate = [start] + path
                if len(candidate) > len(longest):
                    longest = candidate

        return longest

    def detect_circular_dependencies(self) -> List[Dict[str, Any]]:
        """Detect circular dependency loops"""

        if not self.dependency_graph:
            self.extract_dependencies()

        cycles = []
        visited = set()
        rec_stack = set()

        def dfs_cycle(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.dependency_graph.get(node, []):
                if neighbor not in visited:
                    dfs_cycle(neighbor, path.copy())
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]

                    # Get cycle details
                    cycle_apps = []
                    for app in cycle:
                        app_data = self.df[self.df['Application Name'] == app].iloc[0]
                        cycle_apps.append({
                            'app_name': app,
                            'health': app_data['Tech Health'],
                            'value': app_data['Business Value']
                        })

                    cycles.append({
                        'cycle_length': len(cycle) - 1,
                        'apps_in_cycle': cycle_apps,
                        'severity': 'High' if len(cycle) > 3 else 'Medium'
                    })

            rec_stack.remove(node)

        for app in self.df['Application Name']:
            if app not in visited:
                dfs_cycle(app, [])

        return cycles

    def get_integration_complexity_score(self) -> Dict[str, Any]:
        """Calculate overall portfolio integration complexity"""

        if not self.dependency_graph:
            self.extract_dependencies()

        total_apps = len(self.df)
        total_dependencies = sum(len(deps) for deps in self.dependency_graph.values())
        avg_dependencies = total_dependencies / total_apps if total_apps > 0 else 0

        # Calculate density (actual connections / possible connections)
        max_possible = total_apps * (total_apps - 1)
        density = (total_dependencies / max_possible) * 100 if max_possible > 0 else 0

        # Identify isolated apps (no connections)
        connected_apps = set(self.dependency_graph.keys()) | set(self.reverse_graph.keys())
        isolated_apps = total_apps - len(connected_apps)

        return {
            'total_applications': total_apps,
            'total_dependencies': total_dependencies,
            'avg_dependencies_per_app': round(avg_dependencies, 2),
            'network_density': round(density, 2),
            'isolated_applications': isolated_apps,
            'hub_applications': len([h for h in self.hub_apps if h['hub_score'] >= 5]) if self.hub_apps else 0,
            'complexity_rating': self._rate_complexity(avg_dependencies, density)
        }

    def _rate_complexity(self, avg_deps: float, density: float) -> str:
        """Rate overall complexity"""

        if avg_deps > 3 or density > 5:
            return 'Very High - Highly interconnected portfolio'
        elif avg_deps > 2 or density > 3:
            return 'High - Significant integration complexity'
        elif avg_deps > 1 or density > 1:
            return 'Medium - Moderate integration'
        else:
            return 'Low - Loosely coupled portfolio'

    def generate_graph_data(self) -> Dict[str, Any]:
        """Generate graph data for visualization (nodes + edges)"""

        if not self.dependency_graph:
            self.extract_dependencies()

        nodes = []
        edges = []

        # Create nodes
        for idx, app_row in self.df.iterrows():
            app_name = app_row['Application Name']

            # Calculate node size based on connections
            connections = len(self.dependency_graph.get(app_name, [])) + len(self.reverse_graph.get(app_name, []))

            nodes.append({
                'id': app_name,
                'label': app_name,
                'health': app_row['Tech Health'],
                'value': app_row['Business Value'],
                'cost': app_row['Cost'],
                'category': app_row.get('Category', 'Other'),
                'connections': connections,
                'size': 10 + (connections * 5),  # Bigger nodes for hubs
                'color': self._get_node_color(app_row['Tech Health'], app_row['Business Value'])
            })

        # Create edges
        edge_id = 0
        for source, targets in self.dependency_graph.items():
            for target in targets:
                edges.append({
                    'id': f'edge_{edge_id}',
                    'source': source,
                    'target': target,
                    'label': 'depends on'
                })
                edge_id += 1

        return {
            'nodes': nodes,
            'edges': edges,
            'stats': {
                'total_nodes': len(nodes),
                'total_edges': len(edges),
                'avg_connections': sum(n['connections'] for n in nodes) / len(nodes) if nodes else 0
            }
        }

    def _get_node_color(self, health: float, value: float) -> str:
        """Determine node color based on health and value"""

        if health <= 4 and value <= 4:
            return '#EF4444'  # Red - retire candidate
        elif health <= 5 and value >= 7:
            return '#8B5CF6'  # Purple - modernize candidate
        elif health >= 7 and value >= 7:
            return '#10B981'  # Green - healthy
        elif value <= 4:
            return '#F59E0B'  # Orange - low value
        else:
            return '#6B7280'  # Gray - neutral

    def get_integration_report(self) -> Dict[str, Any]:
        """Generate comprehensive integration analysis report"""

        self.extract_dependencies()
        hubs = self.identify_hub_applications()
        critical_path = self.find_critical_path()
        cycles = self.detect_circular_dependencies()
        complexity = self.get_integration_complexity_score()

        # Calculate risk summary
        high_risk_hubs = [h for h in hubs if 'Critical' in h['risk_level'] or 'High' in h['risk_level']]

        return {
            'complexity_score': complexity,
            'hub_applications': hubs,
            'high_risk_hubs': high_risk_hubs,
            'critical_path': critical_path,
            'circular_dependencies': cycles,
            'recommendations': self._generate_integration_recommendations(complexity, hubs, cycles),
            'graph_data': self.generate_graph_data()
        }

    def _generate_integration_recommendations(self, complexity: Dict, hubs: List, cycles: List) -> List[str]:
        """Generate actionable recommendations"""

        recommendations = []

        if complexity['complexity_rating'].startswith('Very High') or complexity['complexity_rating'].startswith('High'):
            recommendations.append('Portfolio has high integration complexity - consider consolidation to reduce interdependencies')

        high_risk = [h for h in hubs if 'Critical' in h['risk_level']]
        if high_risk:
            recommendations.append(f'Prioritize modernization of {len(high_risk)} critical hub applications with poor health')

        if len(cycles) > 0:
            recommendations.append(f'Resolve {len(cycles)} circular dependency loops to improve maintainability')

        if complexity['isolated_applications'] > 10:
            recommendations.append(f'{complexity["isolated_applications"]} isolated apps identified - potential consolidation candidates')

        if not recommendations:
            recommendations.append('Integration architecture is well-structured - maintain current practices')

        return recommendations
