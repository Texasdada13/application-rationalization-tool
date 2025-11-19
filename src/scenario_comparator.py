"""
Scenario Comparator
Side-by-side comparison of multiple what-if scenarios with decision matrix scoring
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from src.whatif_engine import WhatIfScenarioEngine


class ScenarioComparator:
    """Compare multiple what-if scenarios side-by-side with decision matrix"""

    # Decision criteria weights (customizable)
    DEFAULT_WEIGHTS = {
        'cost_savings': 0.30,
        'risk_reduction': 0.25,
        'effort': 0.20,
        'impact': 0.15,
        'timeline': 0.10
    }

    def __init__(self, df_applications: pd.DataFrame):
        """Initialize with application portfolio data"""
        self.df = df_applications.copy()
        self.whatif_engine = WhatIfScenarioEngine(df_applications)
        self.scenarios = {}
        self.comparison_data = None

    def add_scenario(self, scenario_name: str, scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """Add a scenario for comparison"""

        scenario_type = scenario_config.get('type')
        result = None

        if scenario_type == 'retire':
            apps = scenario_config.get('apps', [])
            result = self.whatif_engine.simulate_retirement(apps)

        elif scenario_type == 'modernize':
            apps = scenario_config.get('apps', [])
            health_improvement = scenario_config.get('health_improvement', 3.0)
            result = self.whatif_engine.simulate_modernization(apps, health_improvement)

        elif scenario_type == 'consolidate':
            app_groups = scenario_config.get('app_groups', [])
            cost_reduction = scenario_config.get('cost_reduction', 0.30)
            result = self.whatif_engine.simulate_consolidation(app_groups, cost_reduction)

        elif scenario_type == 'combined':
            scenarios = scenario_config.get('scenarios', [])
            result = self.whatif_engine.simulate_combined_scenario(scenarios)

        if result:
            # Enhance with comparison metrics
            result['comparison_metrics'] = self._calculate_comparison_metrics(result)
            self.scenarios[scenario_name] = result

        return result

    def _calculate_comparison_metrics(self, scenario_result: Dict) -> Dict[str, Any]:
        """Calculate standardized metrics for comparison"""

        impact = scenario_result.get('impact', {})
        new_metrics = scenario_result.get('new_metrics', {})
        details = scenario_result.get('details', {})

        # Calculate normalized scores (0-100)
        cost_savings_score = min(100, abs(impact.get('cost_change', 0)) / 10000)  # Per $10k saved
        risk_score = (new_metrics.get('avg_health', 0) / 10) * 100

        # Effort score (inverse - lower is better)
        app_count = len(details.get('affected_apps', []))
        effort_score = max(0, 100 - (app_count * 5))  # Deduct 5 points per app

        # Impact score (health improvement)
        impact_score = (impact.get('health_change', 0) / 10) * 100 if impact.get('health_change', 0) > 0 else 0

        # Timeline score (based on complexity)
        if app_count <= 5:
            timeline_score = 90  # Quick
        elif app_count <= 15:
            timeline_score = 70  # Medium
        elif app_count <= 30:
            timeline_score = 50  # Long
        else:
            timeline_score = 30  # Very long

        return {
            'cost_savings_score': round(cost_savings_score, 1),
            'risk_reduction_score': round(risk_score, 1),
            'effort_score': round(effort_score, 1),
            'impact_score': round(impact_score, 1),
            'timeline_score': round(timeline_score, 1)
        }

    def compare_all(self, weights: Dict[str, float] = None) -> Dict[str, Any]:
        """Compare all scenarios side-by-side with weighted scoring"""

        if not self.scenarios:
            return {'error': 'No scenarios to compare'}

        if weights is None:
            weights = self.DEFAULT_WEIGHTS

        comparison_matrix = []

        for name, scenario in self.scenarios.items():
            metrics = scenario.get('comparison_metrics', {})
            impact = scenario.get('impact', {})
            new_metrics = scenario.get('new_metrics', {})

            # Calculate weighted score
            weighted_score = (
                metrics.get('cost_savings_score', 0) * weights.get('cost_savings', 0) +
                metrics.get('risk_reduction_score', 0) * weights.get('risk_reduction', 0) +
                metrics.get('effort_score', 0) * weights.get('effort', 0) +
                metrics.get('impact_score', 0) * weights.get('impact', 0) +
                metrics.get('timeline_score', 0) * weights.get('timeline', 0)
            )

            comparison_matrix.append({
                'scenario_name': name,
                'scenario_type': scenario.get('type'),
                'weighted_score': round(weighted_score, 1),
                'cost_change': impact.get('cost_change', 0),
                'health_change': impact.get('health_change', 0),
                'app_count_change': impact.get('app_count_change', 0),
                'new_total_cost': new_metrics.get('total_cost', 0),
                'new_app_count': new_metrics.get('app_count', 0),
                'new_avg_health': new_metrics.get('avg_health', 0),
                'metrics': metrics,
                'roi': scenario.get('details', {}).get('roi_analysis', {})
            })

        # Sort by weighted score
        comparison_matrix.sort(key=lambda x: x['weighted_score'], reverse=True)

        # Generate recommendations
        best_scenario = comparison_matrix[0] if comparison_matrix else None

        self.comparison_data = {
            'scenarios': comparison_matrix,
            'weights_used': weights,
            'baseline': self.whatif_engine.baseline,
            'best_scenario': best_scenario,
            'recommendation': self._generate_recommendation(comparison_matrix),
            'total_scenarios': len(comparison_matrix)
        }

        return self.comparison_data

    def _generate_recommendation(self, comparison_matrix: List[Dict]) -> str:
        """Generate recommendation based on comparison"""

        if not comparison_matrix:
            return "No scenarios available for comparison"

        best = comparison_matrix[0]

        # Check if best scenario is significantly better
        if len(comparison_matrix) > 1:
            second_best = comparison_matrix[1]
            score_diff = best['weighted_score'] - second_best['weighted_score']

            if score_diff > 20:
                return f"Strong recommendation: {best['scenario_name']} - significantly outperforms alternatives"
            elif score_diff > 10:
                return f"Recommended: {best['scenario_name']} - better overall value than alternatives"
            else:
                return f"Marginal preference: {best['scenario_name']} - consider trade-offs with {second_best['scenario_name']}"
        else:
            return f"Proceed with: {best['scenario_name']}"

    def get_pareto_frontier(self) -> List[Dict[str, Any]]:
        """Identify Pareto-optimal scenarios (best trade-offs)"""

        if not self.scenarios:
            return []

        # Use cost savings vs risk reduction for Pareto analysis
        scenarios_list = []

        for name, scenario in self.scenarios.items():
            metrics = scenario.get('comparison_metrics', {})
            impact = scenario.get('impact', {})

            scenarios_list.append({
                'name': name,
                'cost_savings': abs(impact.get('cost_change', 0)),
                'risk_reduction': metrics.get('risk_reduction_score', 0),
                'effort': 100 - metrics.get('effort_score', 0)  # Invert so higher = more effort
            })

        # Find Pareto frontier
        pareto_optimal = []

        for i, scenario_a in enumerate(scenarios_list):
            is_dominated = False

            for j, scenario_b in enumerate(scenarios_list):
                if i == j:
                    continue

                # Check if scenario_b dominates scenario_a
                if (scenario_b['cost_savings'] >= scenario_a['cost_savings'] and
                    scenario_b['risk_reduction'] >= scenario_a['risk_reduction'] and
                    scenario_b['effort'] <= scenario_a['effort'] and
                    (scenario_b['cost_savings'] > scenario_a['cost_savings'] or
                     scenario_b['risk_reduction'] > scenario_a['risk_reduction'] or
                     scenario_b['effort'] < scenario_a['effort'])):
                    is_dominated = True
                    break

            if not is_dominated:
                pareto_optimal.append(scenario_a)

        return pareto_optimal

    def sensitivity_analysis(self, parameter: str, variation: float = 0.2) -> Dict[str, Any]:
        """Perform sensitivity analysis by varying a parameter"""

        if not self.comparison_data:
            self.compare_all()

        # Vary parameter by +/- variation (e.g., 20%)
        variations = {
            'cost_pessimistic': {'cost_savings': -variation},
            'cost_optimistic': {'cost_savings': variation},
            'timeline_pessimistic': {'timeline': -variation},
            'timeline_optimistic': {'timeline': variation}
        }

        sensitivity_results = {}

        for variation_name, weight_adjustments in variations.items():
            # Adjust weights
            adjusted_weights = self.DEFAULT_WEIGHTS.copy()

            for param, adjustment in weight_adjustments.items():
                if param in adjusted_weights:
                    adjusted_weights[param] = max(0, adjusted_weights[param] + adjustment)

            # Renormalize weights
            total_weight = sum(adjusted_weights.values())
            adjusted_weights = {k: v / total_weight for k, v in adjusted_weights.items()}

            # Re-run comparison
            result = self.compare_all(weights=adjusted_weights)
            sensitivity_results[variation_name] = {
                'best_scenario': result['best_scenario']['scenario_name'],
                'best_score': result['best_scenario']['weighted_score'],
                'weights': adjusted_weights
            }

        return {
            'base_case': self.comparison_data['best_scenario']['scenario_name'],
            'variations': sensitivity_results,
            'recommendation': self._interpret_sensitivity(sensitivity_results)
        }

    def _interpret_sensitivity(self, sensitivity_results: Dict) -> str:
        """Interpret sensitivity analysis results"""

        best_scenarios = [v['best_scenario'] for v in sensitivity_results.values()]
        unique_scenarios = set(best_scenarios)

        if len(unique_scenarios) == 1:
            return f"Robust choice: {list(unique_scenarios)[0]} is best across all variations"
        else:
            return f"Sensitive to assumptions: {len(unique_scenarios)} different scenarios recommended depending on priorities"

    def monte_carlo_simulation(self, iterations: int = 1000) -> Dict[str, Any]:
        """Run Monte Carlo simulation with cost uncertainty"""

        if not self.scenarios:
            return {'error': 'No scenarios to simulate'}

        results = {name: [] for name in self.scenarios.keys()}

        for _ in range(iterations):
            # Vary costs randomly (±15%)
            for name, scenario in self.scenarios.items():
                impact = scenario.get('impact', {})
                cost_change = impact.get('cost_change', 0)

                # Add random variation
                variation = np.random.normal(0, abs(cost_change) * 0.15)
                simulated_cost_change = cost_change + variation

                results[name].append(simulated_cost_change)

        # Calculate statistics
        monte_carlo_results = {}

        for name, values in results.items():
            monte_carlo_results[name] = {
                'mean_savings': np.mean(values),
                'median_savings': np.median(values),
                'std_dev': np.std(values),
                'min_savings': np.min(values),
                'max_savings': np.max(values),
                'percentile_10': np.percentile(values, 10),
                'percentile_90': np.percentile(values, 90)
            }

        return {
            'iterations': iterations,
            'scenarios': monte_carlo_results,
            'interpretation': self._interpret_monte_carlo(monte_carlo_results)
        }

    def _interpret_monte_carlo(self, results: Dict) -> str:
        """Interpret Monte Carlo results"""

        # Find most reliable scenario (lowest std dev relative to mean)
        reliability_scores = {}

        for name, stats in results.items():
            mean = abs(stats['mean_savings'])
            std_dev = stats['std_dev']

            if mean > 0:
                coefficient_of_variation = std_dev / mean
                reliability_scores[name] = coefficient_of_variation

        if reliability_scores:
            most_reliable = min(reliability_scores.items(), key=lambda x: x[1])
            return f"Most reliable scenario: {most_reliable[0]} (lowest variance)"
        else:
            return "Insufficient data for reliability assessment"

    def export_comparison_report(self) -> Dict[str, Any]:
        """Export comprehensive comparison report"""

        if not self.comparison_data:
            self.compare_all()

        pareto_frontier = self.get_pareto_frontier()
        sensitivity = self.sensitivity_analysis('cost_savings')
        monte_carlo = self.monte_carlo_simulation(iterations=500)

        return {
            'executive_summary': {
                'total_scenarios_compared': len(self.scenarios),
                'recommended_scenario': self.comparison_data['best_scenario']['scenario_name'],
                'expected_savings': self.comparison_data['best_scenario']['cost_change'],
                'confidence_level': 'High' if len(pareto_frontier) == 1 else 'Medium'
            },
            'comparison_matrix': self.comparison_data,
            'pareto_optimal_scenarios': pareto_frontier,
            'sensitivity_analysis': sensitivity,
            'monte_carlo_simulation': monte_carlo,
            'decision_recommendation': self._generate_final_recommendation(
                self.comparison_data, pareto_frontier, sensitivity
            )
        }

    def _generate_final_recommendation(self, comparison: Dict, pareto: List, sensitivity: Dict) -> str:
        """Generate final recommendation with confidence level"""

        best_scenario = comparison['best_scenario']['scenario_name']

        # Check robustness
        is_pareto_optimal = any(p['name'] == best_scenario for p in pareto)
        is_robust = 'Robust choice' in sensitivity.get('recommendation', '')

        if is_pareto_optimal and is_robust:
            confidence = "Very High"
            recommendation = f"Strongly recommend: {best_scenario}"
        elif is_pareto_optimal or is_robust:
            confidence = "High"
            recommendation = f"Recommend: {best_scenario}"
        else:
            confidence = "Medium"
            recommendation = f"Consider: {best_scenario} (review assumptions)"

        return f"{recommendation} (Confidence: {confidence})"
