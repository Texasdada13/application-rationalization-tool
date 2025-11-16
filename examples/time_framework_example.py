#!/usr/bin/env python3
"""
Example: TIME Framework Usage

This example demonstrates how to use the TIME (Tolerate, Invest, Migrate, Eliminate)
framework for application rationalization, including custom threshold configuration
and portfolio analysis.
"""

import sys
from pathlib import Path
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_handler import DataHandler
from src.scoring_engine import ScoringEngine
from src.recommendation_engine import RecommendationEngine
from src.time_framework import TIMEFramework, TIMEThresholds


def print_section_header(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80 + "\n")


def display_time_matrix(applications):
    """Display applications in a TIME framework matrix format."""
    print("\nTIME FRAMEWORK MATRIX:")
    print("-" * 80)
    print("                    Technical Quality")
    print("                    Low         →         High")
    print("              ┌─────────────┬─────────────┐")
    print("  Business    │             │             │")
    print("  Value  High │  TOLERATE   │   INVEST    │")
    print("              │             │             │")
    print("              ├─────────────┼─────────────┤")
    print("         Low  │             │             │")
    print("              │  ELIMINATE  │   MIGRATE   │")
    print("              │             │             │")
    print("              └─────────────┴─────────────┘")
    print()

    # Count apps in each quadrant
    invest = [a for a in applications if a.get('TIME Category') == 'Invest']
    tolerate = [a for a in applications if a.get('TIME Category') == 'Tolerate']
    migrate = [a for a in applications if a.get('TIME Category') == 'Migrate']
    eliminate = [a for a in applications if a.get('TIME Category') == 'Eliminate']

    print(f"INVEST:    {len(invest):3d} applications")
    print(f"TOLERATE:  {len(tolerate):3d} applications")
    print(f"MIGRATE:   {len(migrate):3d} applications")
    print(f"ELIMINATE: {len(eliminate):3d} applications")
    print()

    return {'invest': invest, 'tolerate': tolerate, 'migrate': migrate, 'eliminate': eliminate}


def example_1_default_thresholds():
    """Example 1: Using default TIME framework thresholds."""
    print_section_header("EXAMPLE 1: Default TIME Framework")

    # Initialize components
    data_handler = DataHandler()
    scoring_engine = ScoringEngine()
    recommendation_engine = RecommendationEngine()
    time_framework = TIMEFramework()  # Uses default thresholds

    # Load and process data
    print("Processing portfolio with default TIME thresholds...")
    df = data_handler.read_csv('data/assessment_template.csv')
    applications = df.to_dict('records')

    # Calculate scores and generate recommendations
    scored_apps = scoring_engine.batch_calculate_scores(applications)
    recommended_apps = recommendation_engine.batch_generate_recommendations(scored_apps)

    # Apply TIME framework
    categorized_apps = time_framework.batch_categorize(recommended_apps)

    # Display results
    summary = time_framework.get_category_summary()
    print(f"\nTotal Applications: {summary['total']}")
    print("\nDistribution:")
    for category, count in summary['distribution'].items():
        pct = summary['percentages'][category]
        print(f"  {category:12} {count:3d} apps ({pct:5.1f}%)")

    # Display matrix
    quadrants = display_time_matrix(categorized_apps)

    # Show examples from each category
    print("\n" + "-" * 80)
    print("Sample Applications by Category:")
    print("-" * 80)

    for category_name, apps in quadrants.items():
        if apps:
            print(f"\n{category_name.upper()}:")
            for app in apps[:3]:  # Show first 3
                print(f"  • {app['Application Name']}")
                print(f"    BV: {app['TIME Business Value Score']:.1f}/10, "
                      f"TQ: {app['TIME Technical Quality Score']:.1f}/10, "
                      f"Composite: {app['Composite Score']:.1f}/100")

    return categorized_apps


def example_2_custom_thresholds():
    """Example 2: Using custom TIME framework thresholds."""
    print_section_header("EXAMPLE 2: Custom TIME Thresholds (Conservative)")

    # Create custom thresholds - more conservative (fewer investments)
    custom_thresholds = TIMEThresholds(
        business_value_threshold=7.0,      # Higher bar for high BV
        technical_quality_threshold=7.0,    # Higher bar for high TQ
        composite_score_high=70.0,
        composite_score_low=35.0,
        critical_business_value=9.0,        # Very high bar for critical
        poor_tech_health=3.0,               # Lower bar for poor
        poor_security=4.0
    )

    print("Using conservative thresholds:")
    print(f"  Business Value Threshold: {custom_thresholds.business_value_threshold}/10")
    print(f"  Technical Quality Threshold: {custom_thresholds.technical_quality_threshold}/10")
    print()

    # Initialize with custom thresholds
    data_handler = DataHandler()
    scoring_engine = ScoringEngine()
    recommendation_engine = RecommendationEngine()
    time_framework = TIMEFramework(thresholds=custom_thresholds)

    # Process
    df = data_handler.read_csv('data/assessment_template.csv')
    applications = df.to_dict('records')
    scored_apps = scoring_engine.batch_calculate_scores(applications)
    recommended_apps = recommendation_engine.batch_generate_recommendations(scored_apps)
    categorized_apps = time_framework.batch_categorize(recommended_apps)

    # Display results
    summary = time_framework.get_category_summary()
    print(f"Total Applications: {summary['total']}")
    print("\nDistribution (Conservative):")
    for category, count in summary['distribution'].items():
        pct = summary['percentages'][category]
        print(f"  {category:12} {count:3d} apps ({pct:5.1f}%)")

    display_time_matrix(categorized_apps)

    return categorized_apps


def example_3_comparison():
    """Example 3: Compare default vs. custom thresholds."""
    print_section_header("EXAMPLE 3: Threshold Comparison Analysis")

    # Run with both threshold sets
    print("Running assessments with multiple threshold configurations...\n")

    # Configuration 1: Default
    time_default = TIMEFramework()

    # Configuration 2: Aggressive (more eliminations)
    time_aggressive = TIMEFramework(TIMEThresholds(
        business_value_threshold=5.0,
        technical_quality_threshold=5.0
    ))

    # Configuration 3: Conservative (fewer investments)
    time_conservative = TIMEFramework(TIMEThresholds(
        business_value_threshold=7.0,
        technical_quality_threshold=7.0
    ))

    # Load and process
    data_handler = DataHandler()
    scoring_engine = ScoringEngine()
    recommendation_engine = RecommendationEngine()

    df = data_handler.read_csv('data/assessment_template.csv')
    applications = df.to_dict('records')
    scored_apps = scoring_engine.batch_calculate_scores(applications)
    recommended_apps = recommendation_engine.batch_generate_recommendations(scored_apps)

    # Categorize with each configuration
    default_apps = time_default.batch_categorize([app.copy() for app in recommended_apps])
    aggressive_apps = time_aggressive.batch_categorize([app.copy() for app in recommended_apps])
    conservative_apps = time_conservative.batch_categorize([app.copy() for app in recommended_apps])

    # Compare results
    print("Comparison of TIME Categorizations:")
    print("-" * 80)
    print(f"{'Category':<15} {'Default':>12} {'Aggressive':>12} {'Conservative':>12}")
    print("-" * 80)

    for category in ['Invest', 'Tolerate', 'Migrate', 'Eliminate']:
        default_count = sum(1 for a in default_apps if a.get('TIME Category') == category)
        aggressive_count = sum(1 for a in aggressive_apps if a.get('TIME Category') == category)
        conservative_count = sum(1 for a in conservative_apps if a.get('TIME Category') == category)

        print(f"{category:<15} {default_count:>12d} {aggressive_count:>12d} {conservative_count:>12d}")

    print("-" * 80)

    # Show threshold impact
    print("\nThreshold Impact Analysis:")
    print("  Default (BV≥6.0, TQ≥6.0):")
    print("    - Balanced approach")
    print("    - Suitable for most organizations")
    print()
    print("  Aggressive (BV≥5.0, TQ≥5.0):")
    print("    - More applications qualify for investment")
    print("    - Fewer candidates for elimination")
    print("    - Use when portfolio quality is generally high")
    print()
    print("  Conservative (BV≥7.0, TQ≥7.0):")
    print("    - Higher bar for investment category")
    print("    - More applications flagged for action")
    print("    - Use when focusing on portfolio cleanup")


def example_4_action_planning():
    """Example 4: Action planning based on TIME categories."""
    print_section_header("EXAMPLE 4: Action Planning by TIME Category")

    # Run assessment
    data_handler = DataHandler()
    scoring_engine = ScoringEngine()
    recommendation_engine = RecommendationEngine()
    time_framework = TIMEFramework()

    df = data_handler.read_csv('data/assessment_template.csv')
    applications = df.to_dict('records')
    scored_apps = scoring_engine.batch_calculate_scores(applications)
    recommended_apps = recommendation_engine.batch_generate_recommendations(scored_apps)
    categorized_apps = time_framework.batch_categorize(recommended_apps)

    # Group by TIME category
    by_category = {}
    for app in categorized_apps:
        category = app.get('TIME Category', 'Unknown')
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(app)

    # Action planning for each category
    print("RECOMMENDED ACTIONS BY TIME CATEGORY\n")

    # INVEST - Priority by composite score
    if 'Invest' in by_category:
        invest_apps = sorted(by_category['Invest'],
                           key=lambda x: x.get('Composite Score', 0),
                           reverse=True)
        print("INVEST CATEGORY - Continue Investment")
        print("-" * 80)
        print("Priority investment candidates (highest value first):\n")
        for i, app in enumerate(invest_apps[:5], 1):
            print(f"{i}. {app['Application Name']}")
            print(f"   Composite Score: {app['Composite Score']:.1f}/100")
            print(f"   Action: Allocate budget for enhancements and new features")
            print()

    # TOLERATE - Priority by risk
    if 'Tolerate' in by_category:
        tolerate_apps = sorted(by_category['Tolerate'],
                             key=lambda x: x.get('Tech Health', 10))
        print("\nTOLERATE CATEGORY - Plan Improvements")
        print("-" * 80)
        print("High-priority improvement candidates (worst tech health first):\n")
        for i, app in enumerate(tolerate_apps[:5], 1):
            print(f"{i}. {app['Application Name']}")
            print(f"   Tech Health: {app.get('Tech Health', 0):.1f}/10")
            print(f"   Action: Plan migration or technical debt reduction")
            print()

    # MIGRATE - Priority by effort
    if 'Migrate' in by_category:
        migrate_apps = sorted(by_category['Migrate'],
                            key=lambda x: x.get('Cost', 999999))
        print("\nMIGRATE CATEGORY - Consolidate or Modernize")
        print("-" * 80)
        print("Migration candidates (lowest cost first for quick wins):\n")
        for i, app in enumerate(migrate_apps[:5], 1):
            print(f"{i}. {app['Application Name']}")
            print(f"   Annual Cost: ${app.get('Cost', 0):,.0f}")
            print(f"   Action: Evaluate consolidation or migration options")
            print()

    # ELIMINATE - Priority by cost savings
    if 'Eliminate' in by_category:
        eliminate_apps = sorted(by_category['Eliminate'],
                              key=lambda x: x.get('Cost', 0),
                              reverse=True)
        print("\nELIMINATE CATEGORY - Retire or Decommission")
        print("-" * 80)
        print("Retirement candidates (highest cost savings first):\n")
        total_savings = 0
        for i, app in enumerate(eliminate_apps[:5], 1):
            cost = app.get('Cost', 0)
            total_savings += cost
            print(f"{i}. {app['Application Name']}")
            print(f"   Annual Cost: ${cost:,.0f}")
            print(f"   Action: Plan retirement and data archival")
            print()

        if eliminate_apps:
            print(f"Potential Annual Savings from Eliminations: ${total_savings:,.0f}")


def main():
    """Run all TIME framework examples."""
    print("=" * 80)
    print(" " * 20 + "TIME FRAMEWORK EXAMPLES")
    print("=" * 80)

    # Example 1: Default thresholds
    example_1_default_thresholds()

    # Example 2: Custom thresholds
    example_2_custom_thresholds()

    # Example 3: Threshold comparison
    example_3_comparison()

    # Example 4: Action planning
    example_4_action_planning()

    print("\n" + "=" * 80)
    print(" " * 25 + "ALL EXAMPLES COMPLETE")
    print("=" * 80)
    print("\nNext Steps:")
    print("  1. Review TIME categorizations in the output")
    print("  2. Adjust thresholds in config/time_config.yaml")
    print("  3. Run your own assessment: python main.py")
    print("  4. Filter by TIME category: python -m src.cli list-apps -i results.csv -tc Invest")
    print()


if __name__ == '__main__':
    main()
