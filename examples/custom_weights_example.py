#!/usr/bin/env python3
"""
Example: Using Custom Scoring Weights

This example demonstrates how to customize scoring weights to match
your organization's specific priorities.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_handler import DataHandler
from src.scoring_engine import ScoringEngine, ScoringWeights
from src.recommendation_engine import RecommendationEngine


def main():
    print("=" * 80)
    print("Custom Scoring Weights Example")
    print("=" * 80)
    print()

    # Scenario 1: Security-First Organization
    print("Scenario 1: Security-First Organization")
    print("-" * 80)

    security_weights = ScoringWeights(
        business_value=0.20,
        tech_health=0.15,
        cost=0.15,
        usage=0.10,
        security=0.25,      # Increased emphasis on security
        strategic_fit=0.10,
        redundancy=0.05
    )

    run_assessment_with_weights(security_weights, "Security-First")

    # Scenario 2: Cost Reduction Initiative
    print("\n\nScenario 2: Cost Reduction Initiative")
    print("-" * 80)

    cost_weights = ScoringWeights(
        business_value=0.20,
        tech_health=0.15,
        cost=0.25,          # Increased emphasis on cost
        usage=0.15,
        security=0.10,
        strategic_fit=0.10,
        redundancy=0.05
    )

    run_assessment_with_weights(cost_weights, "Cost-Reduction")

    # Scenario 3: Digital Transformation
    print("\n\nScenario 3: Digital Transformation")
    print("-" * 80)

    transformation_weights = ScoringWeights(
        business_value=0.20,
        tech_health=0.25,   # Increased emphasis on tech health
        cost=0.10,
        usage=0.10,
        security=0.10,
        strategic_fit=0.20, # Increased emphasis on strategic fit
        redundancy=0.05
    )

    run_assessment_with_weights(transformation_weights, "Transformation")


def run_assessment_with_weights(weights: ScoringWeights, scenario_name: str):
    """Run assessment with custom weights."""

    # Initialize components
    data_handler = DataHandler()
    scoring_engine = ScoringEngine(weights=weights)
    recommendation_engine = RecommendationEngine()

    # Load data
    df = data_handler.read_csv('data/assessment_template.csv')
    applications = df.to_dict('records')

    # Calculate scores
    scored_apps = scoring_engine.batch_calculate_scores(applications)
    results = recommendation_engine.batch_generate_recommendations(scored_apps)

    # Get summary
    rec_summary = recommendation_engine.get_portfolio_summary()

    # Display results
    print(f"\nWeight Configuration:")
    print(f"  Business Value: {weights.business_value:.0%}")
    print(f"  Tech Health:    {weights.tech_health:.0%}")
    print(f"  Cost:           {weights.cost:.0%}")
    print(f"  Usage:          {weights.usage:.0%}")
    print(f"  Security:       {weights.security:.0%}")
    print(f"  Strategic Fit:  {weights.strategic_fit:.0%}")
    print(f"  Redundancy:     {weights.redundancy:.0%}")

    print(f"\nRecommendation Distribution:")
    for action, count in sorted(rec_summary['distribution'].items(),
                                 key=lambda x: x[1], reverse=True):
        if count > 0:
            pct = rec_summary['percentages'][action]
            print(f"  {action:30} {count:2d} apps ({pct:5.1f}%)")

    # Save results
    output_path = Path(f'output/custom_weights_{scenario_name.lower()}.csv')
    import pandas as pd
    results_df = pd.DataFrame(results)
    data_handler.write_csv(results_df, output_path, include_timestamp=False)
    print(f"\nResults saved to: {output_path}")


if __name__ == '__main__':
    main()
