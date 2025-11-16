#!/usr/bin/env python3
"""
Example: Customizable Scoring Weights Configuration

This example demonstrates how to customize scoring weights using the configuration
system, showing different organizational priorities and their impact on results.
"""

import sys
from pathlib import Path
import yaml

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_handler import DataHandler
from src.scoring_engine import ScoringEngine, ScoringWeights
from src.recommendation_engine import RecommendationEngine
from src.time_framework import TIMEFramework
from src.config_loader import ConfigLoader


def print_section_header(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80 + "\n")


def run_assessment_with_config(config: ConfigLoader, scenario_name: str):
    """Run assessment with a specific configuration."""
    print(f"Running assessment: {scenario_name}")
    print("-" * 80)

    # Get configuration
    scoring_weights = config.get_scoring_weights()
    time_thresholds = config.get_time_thresholds()

    # Display weights
    print("\nScoring Weights:")
    print(f"  Business Value:  {scoring_weights.business_value:5.1%}")
    print(f"  Tech Health:     {scoring_weights.tech_health:5.1%}")
    print(f"  Cost:            {scoring_weights.cost:5.1%}")
    print(f"  Usage:           {scoring_weights.usage:5.1%}")
    print(f"  Security:        {scoring_weights.security:5.1%}")
    print(f"  Strategic Fit:   {scoring_weights.strategic_fit:5.1%}")
    print(f"  Redundancy:      {scoring_weights.redundancy:5.1%}")

    # Initialize components
    data_handler = DataHandler()
    scoring_engine = ScoringEngine(weights=scoring_weights)
    recommendation_engine = RecommendationEngine()
    time_framework = TIMEFramework(thresholds=time_thresholds)

    # Load and process data
    df = data_handler.read_csv('data/assessment_template.csv')
    applications = df.to_dict('records')

    # Calculate scores and generate recommendations
    scored_apps = scoring_engine.batch_calculate_scores(applications)
    recommended_apps = recommendation_engine.batch_generate_recommendations(scored_apps)
    categorized_apps = time_framework.batch_categorize(recommended_apps)

    # Display results
    import pandas as pd
    results_df = pd.DataFrame(categorized_apps)

    print("\nResults Summary:")
    print(f"  Average Composite Score: {results_df['Composite Score'].mean():.1f}/100")
    print(f"  Median Composite Score:  {results_df['Composite Score'].median():.1f}/100")
    print(f"  Min Score:               {results_df['Composite Score'].min():.1f}/100")
    print(f"  Max Score:               {results_df['Composite Score'].max():.1f}/100")

    # TIME distribution
    time_summary = time_framework.get_category_summary()
    print("\nTIME Distribution:")
    for category, count in time_summary['distribution'].items():
        pct = time_summary['percentages'][category]
        print(f"  {category:12} {count:2d} apps ({pct:5.1f}%)")

    # Save results
    output_file = f"output/config_example_{scenario_name.lower().replace(' ', '_')}.csv"
    data_handler.write_csv(results_df, Path(output_file), include_timestamp=False)
    print(f"\nResults saved to: {output_file}")

    return results_df


def example_1_default_config():
    """Example 1: Using default balanced configuration."""
    print_section_header("EXAMPLE 1: Default Balanced Configuration")

    # Load default configuration
    config = ConfigLoader()

    # Display configuration
    print(config.display_current_config())

    # Run assessment
    results = run_assessment_with_config(config, "Default_Balanced")

    return results


def example_2_security_first():
    """Example 2: Security-first configuration."""
    print_section_header("EXAMPLE 2: Security-First Organization")

    # Create config with security-first weights
    config = ConfigLoader()
    config.set_config_value('scoring_weights.business_value', 0.20)
    config.set_config_value('scoring_weights.tech_health', 0.20)
    config.set_config_value('scoring_weights.cost', 0.10)
    config.set_config_value('scoring_weights.usage', 0.10)
    config.set_config_value('scoring_weights.security', 0.25)  # Increased
    config.set_config_value('scoring_weights.strategic_fit', 0.10)
    config.set_config_value('scoring_weights.redundancy', 0.05)

    # Also adjust TIME thresholds for stricter security
    config.set_config_value('time_thresholds.poor_security', 6.0)  # Stricter

    print("Configuration Approach: Prioritize security and technical health")
    print("Use Case: Organizations in regulated industries (healthcare, finance)")

    # Run assessment
    results = run_assessment_with_config(config, "Security_First")

    return results


def example_3_cost_reduction():
    """Example 3: Cost reduction focus configuration."""
    print_section_header("EXAMPLE 3: Cost Reduction Initiative")

    # Create config with cost-focused weights
    config = ConfigLoader()
    config.set_config_value('scoring_weights.business_value', 0.20)
    config.set_config_value('scoring_weights.tech_health', 0.15)
    config.set_config_value('scoring_weights.cost', 0.30)  # Increased
    config.set_config_value('scoring_weights.usage', 0.15)
    config.set_config_value('scoring_weights.security', 0.08)
    config.set_config_value('scoring_weights.strategic_fit', 0.07)
    config.set_config_value('scoring_weights.redundancy', 0.05)

    print("Configuration Approach: Maximize cost optimization")
    print("Use Case: Budget reduction initiatives, cost containment programs")

    # Run assessment
    results = run_assessment_with_config(config, "Cost_Reduction")

    return results


def example_4_digital_transformation():
    """Example 4: Digital transformation configuration."""
    print_section_header("EXAMPLE 4: Digital Transformation Focus")

    # Create config for transformation
    config = ConfigLoader()
    config.set_config_value('scoring_weights.business_value', 0.20)
    config.set_config_value('scoring_weights.tech_health', 0.25)  # Increased
    config.set_config_value('scoring_weights.cost', 0.10)
    config.set_config_value('scoring_weights.usage', 0.10)
    config.set_config_value('scoring_weights.security', 0.10)
    config.set_config_value('scoring_weights.strategic_fit', 0.20)  # Increased
    config.set_config_value('scoring_weights.redundancy', 0.05)

    print("Configuration Approach: Emphasize strategic fit and technical modernization")
    print("Use Case: Digital transformation programs, cloud migration initiatives")

    # Run assessment
    results = run_assessment_with_config(config, "Digital_Transformation")

    return results


def example_5_business_value_driven():
    """Example 5: Business value driven configuration."""
    print_section_header("EXAMPLE 5: Business Value Driven")

    # Create config emphasizing business value and usage
    config = ConfigLoader()
    config.set_config_value('scoring_weights.business_value', 0.35)  # Increased
    config.set_config_value('scoring_weights.tech_health', 0.15)
    config.set_config_value('scoring_weights.cost', 0.10)
    config.set_config_value('scoring_weights.usage', 0.20)  # Increased
    config.set_config_value('scoring_weights.security', 0.08)
    config.set_config_value('scoring_weights.strategic_fit', 0.07)
    config.set_config_value('scoring_weights.redundancy', 0.05)

    print("Configuration Approach: Maximize focus on business value and user adoption")
    print("Use Case: Product-centric organizations, customer-focused strategies")

    # Run assessment
    results = run_assessment_with_config(config, "Business_Value")

    return results


def example_6_save_custom_config():
    """Example 6: Saving custom configuration to file."""
    print_section_header("EXAMPLE 6: Saving Custom Configuration")

    # Create custom configuration
    config = ConfigLoader()

    # Customize settings
    config.set_config_value('scoring_weights.business_value', 0.30)
    config.set_config_value('scoring_weights.tech_health', 0.20)
    config.set_config_value('scoring_weights.cost', 0.15)
    config.set_config_value('scoring_weights.usage', 0.15)
    config.set_config_value('scoring_weights.security', 0.10)
    config.set_config_value('scoring_weights.strategic_fit', 0.05)
    config.set_config_value('scoring_weights.redundancy', 0.05)

    # Set organization info
    config.set_config_value('organization.name', 'Acme Corporation')
    config.set_config_value('organization.cycle', 'Q1 2025')
    config.set_config_value('organization.owner', 'Enterprise Architecture Team')

    print("Custom Configuration Created")
    print(config.display_current_config())

    # Save to local config file
    output_path = Path('config/config.local.example.yaml')
    config.save_config(output_path)

    print(f"\nConfiguration saved to: {output_path}")
    print("\nTo use this configuration:")
    print("  1. Copy config.local.example.yaml to config.local.yaml")
    print("  2. Edit config.local.yaml as needed")
    print("  3. Run assessments - config.local.yaml will be loaded automatically")


def example_7_compare_configurations():
    """Example 7: Compare impact of different configurations."""
    print_section_header("EXAMPLE 7: Configuration Impact Comparison")

    print("Running assessments with different configurations...\n")

    # Run with different configs
    scenarios = []

    # Default
    config_default = ConfigLoader()
    results_default = run_assessment_with_config(config_default, "Comparison_Default")
    scenarios.append(('Default', results_default))

    # Security-first
    config_security = ConfigLoader()
    config_security.set_config_value('scoring_weights.security', 0.25)
    config_security.set_config_value('scoring_weights.business_value', 0.20)
    config_security.set_config_value('scoring_weights.tech_health', 0.20)
    results_security = run_assessment_with_config(config_security, "Comparison_Security")
    scenarios.append(('Security-First', results_security))

    # Cost-focused
    config_cost = ConfigLoader()
    config_cost.set_config_value('scoring_weights.cost', 0.30)
    config_cost.set_config_value('scoring_weights.business_value', 0.20)
    results_cost = run_assessment_with_config(config_cost, "Comparison_Cost")
    scenarios.append(('Cost-Focused', results_cost))

    # Compare results
    print("\n" + "=" * 80)
    print("CONFIGURATION COMPARISON")
    print("=" * 80)

    print(f"\n{'Metric':<30} {'Default':>15} {'Security':>15} {'Cost':>15}")
    print("-" * 80)

    for metric in ['Composite Score', 'Business Value', 'Tech Health', 'Security', 'Cost']:
        if metric in scenarios[0][1].columns:
            default_val = scenarios[0][1][metric].mean()
            security_val = scenarios[1][1][metric].mean()
            cost_val = scenarios[2][1][metric].mean()
            print(f"Avg {metric:<24} {default_val:>15.1f} {security_val:>15.1f} {cost_val:>15.1f}")

    print("\nKey Insights:")
    print("  - Different weights emphasize different strengths")
    print("  - Security-first config rewards high-security apps")
    print("  - Cost-focused config penalizes expensive apps more heavily")
    print("  - Choose weights that align with organizational priorities")


def main():
    """Run all configuration examples."""
    print("=" * 80)
    print(" " * 15 + "CUSTOMIZABLE SCORING WEIGHTS EXAMPLES")
    print("=" * 80)

    # Example 1: Default configuration
    example_1_default_config()

    # Example 2: Security-first
    example_2_security_first()

    # Example 3: Cost reduction
    example_3_cost_reduction()

    # Example 4: Digital transformation
    example_4_digital_transformation()

    # Example 5: Business value driven
    example_5_business_value_driven()

    # Example 6: Save custom config
    example_6_save_custom_config()

    # Example 7: Compare configurations
    example_7_compare_configurations()

    print("\n" + "=" * 80)
    print(" " * 25 + "ALL EXAMPLES COMPLETE")
    print("=" * 80)

    print("\nNext Steps:")
    print("  1. Review the generated output files in output/")
    print("  2. Edit config/config.yaml to customize default weights")
    print("  3. Create config/config.local.yaml for user-specific settings")
    print("  4. Run: python main.py (uses configuration automatically)")
    print("  5. View current config: python -c \"from src.config_loader import load_config; print(load_config().display_current_config())\"")
    print()


if __name__ == '__main__':
    main()
