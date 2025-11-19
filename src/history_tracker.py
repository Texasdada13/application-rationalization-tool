"""
Historical Tracking & Portfolio Evolution
Store snapshots, track changes over time, compare assessments, and measure ROI realization
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Tuple
import json
from pathlib import Path


class HistoryTracker:
    """Track portfolio changes and evolution over time"""

    def __init__(self, storage_path: str = None):
        """Initialize history tracker with storage location"""
        if storage_path is None:
            storage_path = Path(__file__).parent.parent / 'data' / 'history'

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.snapshots = []
        self.load_snapshots()

    def save_snapshot(self, df: pd.DataFrame, snapshot_name: str = None, metadata: Dict = None) -> Dict[str, Any]:
        """Save portfolio snapshot with timestamp"""

        timestamp = datetime.now().isoformat()

        if snapshot_name is None:
            snapshot_name = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Calculate summary metrics
        summary = {
            'snapshot_id': snapshot_name,
            'timestamp': timestamp,
            'total_apps': len(df),
            'total_cost': float(df['Cost'].sum()),
            'avg_health': float(df['Tech Health'].mean()),
            'avg_value': float(df['Business Value'].mean()),
            'metadata': metadata or {}
        }

        # Save dataframe as CSV
        csv_path = self.storage_path / f"{snapshot_name}.csv"
        df.to_csv(csv_path, index=False)

        # Save summary as JSON
        json_path = self.storage_path / f"{snapshot_name}_meta.json"
        with open(json_path, 'w') as f:
            json.dump(summary, f, indent=2)

        self.snapshots.append(summary)

        return summary

    def load_snapshots(self) -> List[Dict[str, Any]]:
        """Load all saved snapshots"""

        self.snapshots = []

        for json_file in self.storage_path.glob("*_meta.json"):
            try:
                with open(json_file, 'r') as f:
                    snapshot = json.load(f)
                    self.snapshots.append(snapshot)
            except Exception as e:
                print(f"Error loading {json_file}: {e}")

        # Sort by timestamp
        self.snapshots.sort(key=lambda x: x['timestamp'])

        return self.snapshots

    def get_snapshot(self, snapshot_id: str) -> pd.DataFrame:
        """Load specific snapshot data"""

        csv_path = self.storage_path / f"{snapshot_id}.csv"

        if not csv_path.exists():
            raise FileNotFoundError(f"Snapshot {snapshot_id} not found")

        return pd.read_csv(csv_path)

    def compare_snapshots(self, snapshot1_id: str, snapshot2_id: str) -> Dict[str, Any]:
        """Compare two snapshots to see what changed"""

        df1 = self.get_snapshot(snapshot1_id)
        df2 = self.get_snapshot(snapshot2_id)

        # Find metadata
        meta1 = next((s for s in self.snapshots if s['snapshot_id'] == snapshot1_id), {})
        meta2 = next((s for s in self.snapshots if s['snapshot_id'] == snapshot2_id), {})

        # Calculate changes
        apps1 = set(df1['Application Name'].tolist())
        apps2 = set(df2['Application Name'].tolist())

        added_apps = list(apps2 - apps1)
        removed_apps = list(apps1 - apps2)
        common_apps = list(apps1 & apps2)

        # Track changes in common apps
        changes = []

        for app in common_apps:
            app1_data = df1[df1['Application Name'] == app].iloc[0]
            app2_data = df2[df2['Application Name'] == app].iloc[0]

            # Check for significant changes
            cost_change = float(app2_data['Cost'] - app1_data['Cost'])
            health_change = float(app2_data['Tech Health'] - app1_data['Tech Health'])
            value_change = float(app2_data['Business Value'] - app1_data['Business Value'])

            if abs(cost_change) > 1000 or abs(health_change) > 0.5 or abs(value_change) > 0.5:
                changes.append({
                    'app_name': app,
                    'cost_change': cost_change,
                    'health_change': health_change,
                    'value_change': value_change,
                    'change_type': self._categorize_change(cost_change, health_change, value_change)
                })

        # Portfolio-level changes
        portfolio_changes = {
            'total_apps': {
                'before': meta1.get('total_apps', len(df1)),
                'after': meta2.get('total_apps', len(df2)),
                'change': len(df2) - len(df1)
            },
            'total_cost': {
                'before': meta1.get('total_cost', float(df1['Cost'].sum())),
                'after': meta2.get('total_cost', float(df2['Cost'].sum())),
                'change': float(df2['Cost'].sum() - df1['Cost'].sum())
            },
            'avg_health': {
                'before': meta1.get('avg_health', float(df1['Tech Health'].mean())),
                'after': meta2.get('avg_health', float(df2['Tech Health'].mean())),
                'change': float(df2['Tech Health'].mean() - df1['Tech Health'].mean())
            },
            'avg_value': {
                'before': meta1.get('avg_value', float(df1['Business Value'].mean())),
                'after': meta2.get('avg_value', float(df2['Business Value'].mean())),
                'change': float(df2['Business Value'].mean() - df1['Business Value'].mean())
            }
        }

        return {
            'snapshot1': meta1,
            'snapshot2': meta2,
            'added_apps': added_apps,
            'removed_apps': removed_apps,
            'modified_apps': changes,
            'portfolio_changes': portfolio_changes,
            'summary': self._generate_comparison_summary(added_apps, removed_apps, changes, portfolio_changes)
        }

    def _categorize_change(self, cost_change: float, health_change: float, value_change: float) -> str:
        """Categorize type of change"""

        if health_change > 1 and cost_change < 0:
            return 'Modernization - improved health, reduced cost'
        elif health_change > 1:
            return 'Modernization - improved health'
        elif cost_change < -10000:
            return 'Cost Reduction - significant savings'
        elif value_change > 1:
            return 'Value Enhancement - increased business value'
        elif value_change < -1 or health_change < -1:
            return 'Degradation - declining metrics'
        else:
            return 'Minor adjustment'

    def _generate_comparison_summary(self, added: List, removed: List, changes: List, portfolio: Dict) -> str:
        """Generate human-readable summary"""

        parts = []

        if removed:
            parts.append(f"Retired {len(removed)} applications")

        if added:
            parts.append(f"Added {len(added)} new applications")

        if changes:
            parts.append(f"Modified {len(changes)} applications")

        cost_change = portfolio['total_cost']['change']
        if abs(cost_change) > 10000:
            direction = "decreased" if cost_change < 0 else "increased"
            parts.append(f"Total cost {direction} by ${abs(cost_change):,.0f}")

        health_change = portfolio['avg_health']['change']
        if abs(health_change) > 0.2:
            direction = "improved" if health_change > 0 else "declined"
            parts.append(f"Average health {direction} by {abs(health_change):.1f} points")

        return " | ".join(parts) if parts else "No significant changes"

    def get_portfolio_evolution(self) -> Dict[str, Any]:
        """Get portfolio evolution over all snapshots"""

        if len(self.snapshots) < 2:
            return {
                'error': 'Need at least 2 snapshots to show evolution',
                'snapshots_count': len(self.snapshots)
            }

        timeline = []

        for snapshot in self.snapshots:
            timeline.append({
                'timestamp': snapshot['timestamp'],
                'date': snapshot['timestamp'][:10],
                'total_apps': snapshot['total_apps'],
                'total_cost': snapshot['total_cost'],
                'avg_health': snapshot['avg_health'],
                'avg_value': snapshot['avg_value']
            })

        # Calculate trends
        first = timeline[0]
        last = timeline[-1]

        trends = {
            'app_count_trend': last['total_apps'] - first['total_apps'],
            'cost_trend': last['total_cost'] - first['total_cost'],
            'health_trend': last['avg_health'] - first['avg_health'],
            'value_trend': last['avg_value'] - first['avg_value'],
            'trend_direction': self._determine_trend_direction(first, last)
        }

        return {
            'timeline': timeline,
            'trends': trends,
            'total_snapshots': len(timeline),
            'date_range': {
                'start': first['date'],
                'end': last['date']
            }
        }

    def _determine_trend_direction(self, first: Dict, last: Dict) -> str:
        """Determine overall trend direction"""

        health_improved = last['avg_health'] > first['avg_health']
        cost_reduced = last['total_cost'] < first['total_cost']
        value_improved = last['avg_value'] > first['avg_value']

        positive_trends = sum([health_improved, cost_reduced, value_improved])

        if positive_trends >= 2:
            return 'Positive - Portfolio improving'
        elif positive_trends == 1:
            return 'Mixed - Some improvements'
        else:
            return 'Negative - Portfolio declining'

    def track_roi_realization(self, decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Track ROI realization from past decisions"""

        # Decisions format: [{'app': 'X', 'action': 'retire', 'expected_savings': 100000, 'date': '2024-01-01'}]

        if len(self.snapshots) < 2:
            return {'error': 'Need snapshots before and after decisions'}

        roi_tracking = []

        for decision in decisions:
            app_name = decision.get('app')
            action = decision.get('action')
            expected_savings = decision.get('expected_savings', 0)
            decision_date = decision.get('date')

            # Find snapshots before and after decision
            before_snapshot = None
            after_snapshot = None

            for snapshot in self.snapshots:
                if snapshot['timestamp'] < decision_date:
                    before_snapshot = snapshot
                elif snapshot['timestamp'] > decision_date and after_snapshot is None:
                    after_snapshot = snapshot
                    break

            if before_snapshot and after_snapshot:
                # Check if decision was implemented
                df_before = self.get_snapshot(before_snapshot['snapshot_id'])
                df_after = self.get_snapshot(after_snapshot['snapshot_id'])

                app_in_before = app_name in df_before['Application Name'].values
                app_in_after = app_name in df_after['Application Name'].values

                if action == 'retire':
                    implemented = app_in_before and not app_in_after
                    actual_savings = expected_savings if implemented else 0

                    roi_tracking.append({
                        'app': app_name,
                        'action': action,
                        'expected_savings': expected_savings,
                        'actual_savings': actual_savings,
                        'implemented': implemented,
                        'roi_percentage': 100 if implemented else 0,
                        'status': 'Realized' if implemented else 'Not implemented'
                    })

                elif action == 'modernize' and app_in_before and app_in_after:
                    before_data = df_before[df_before['Application Name'] == app_name].iloc[0]
                    after_data = df_after[df_after['Application Name'] == app_name].iloc[0]

                    health_improvement = float(after_data['Tech Health'] - before_data['Tech Health'])

                    # Estimate realized savings based on health improvement
                    realized_pct = min(100, max(0, (health_improvement / 3) * 100))  # Assume 3-point improvement = 100%
                    actual_savings = expected_savings * (realized_pct / 100)

                    roi_tracking.append({
                        'app': app_name,
                        'action': action,
                        'expected_savings': expected_savings,
                        'actual_savings': actual_savings,
                        'health_improvement': health_improvement,
                        'roi_percentage': realized_pct,
                        'status': 'Partially realized' if realized_pct < 100 else 'Fully realized'
                    })

        # Calculate totals
        total_expected = sum(r['expected_savings'] for r in roi_tracking)
        total_actual = sum(r['actual_savings'] for r in roi_tracking)
        realization_rate = (total_actual / total_expected * 100) if total_expected > 0 else 0

        return {
            'decisions_tracked': len(roi_tracking),
            'decisions': roi_tracking,
            'total_expected_savings': total_expected,
            'total_actual_savings': total_actual,
            'realization_rate': round(realization_rate, 1),
            'summary': self._generate_roi_summary(realization_rate, total_actual)
        }

    def _generate_roi_summary(self, realization_rate: float, actual_savings: float) -> str:
        """Generate ROI summary message"""

        if realization_rate >= 90:
            return f"Excellent - {realization_rate:.0f}% ROI realization (${actual_savings:,.0f} saved)"
        elif realization_rate >= 70:
            return f"Good - {realization_rate:.0f}% ROI realization (${actual_savings:,.0f} saved)"
        elif realization_rate >= 50:
            return f"Fair - {realization_rate:.0f}% ROI realization (${actual_savings:,.0f} saved)"
        else:
            return f"Poor - Only {realization_rate:.0f}% ROI realization (${actual_savings:,.0f} saved)"

    def get_application_history(self, app_name: str) -> Dict[str, Any]:
        """Get change history for specific application"""

        history = []

        for snapshot in self.snapshots:
            df = self.get_snapshot(snapshot['snapshot_id'])

            if app_name in df['Application Name'].values:
                app_data = df[df['Application Name'] == app_name].iloc[0]

                history.append({
                    'timestamp': snapshot['timestamp'],
                    'date': snapshot['timestamp'][:10],
                    'cost': float(app_data['Cost']),
                    'health': float(app_data['Tech Health']),
                    'value': float(app_data['Business Value']),
                    'category': app_data.get('Category', 'N/A')
                })

        if not history:
            return {'error': f'Application "{app_name}" not found in any snapshot'}

        # Calculate changes over time
        if len(history) > 1:
            first = history[0]
            last = history[-1]

            changes = {
                'cost_change': last['cost'] - first['cost'],
                'health_change': last['health'] - first['health'],
                'value_change': last['value'] - first['value']
            }
        else:
            changes = None

        return {
            'app_name': app_name,
            'history': history,
            'total_snapshots': len(history),
            'changes_over_time': changes,
            'current_status': history[-1] if history else None
        }

    def list_snapshots(self) -> List[Dict[str, Any]]:
        """List all available snapshots"""

        return [
            {
                'snapshot_id': s['snapshot_id'],
                'date': s['timestamp'][:10],
                'time': s['timestamp'][11:19],
                'total_apps': s['total_apps'],
                'total_cost': s['total_cost']
            }
            for s in self.snapshots
        ]

    def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete a snapshot"""

        csv_path = self.storage_path / f"{snapshot_id}.csv"
        json_path = self.storage_path / f"{snapshot_id}_meta.json"

        deleted = False

        if csv_path.exists():
            csv_path.unlink()
            deleted = True

        if json_path.exists():
            json_path.unlink()
            deleted = True

        # Reload snapshots
        self.load_snapshots()

        return deleted
