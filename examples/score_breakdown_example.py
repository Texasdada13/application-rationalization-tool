#!/usr/bin/env python3
"""
Example: Score Breakdown Analysis

This example demonstrates how to analyze score contributions from each
criterion to understand what drives application scores.
"""

import sys
from pathlib import Path
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_handler import DataHandler
from src.scoring_engine import ScoringEngine


def analyze_application_score(app: dict, engine: ScoringEngine):
    """Analyze and display score breakdown for a single application."""

    print(f"\nApplication: {app['Application Name']}")
    print("=" * 80)

    # Display input criteria
    print("\nInput Criteria:")
    print(f"  Business Value:  {app['Business Value']}/10")
    print(f"  Tech Health:     {app['Tech Health']}/10")
    print(f"  Cost:            ${app['Cost']:,.0f}")
    print(f"  Usage:           {app['Usage']} users")
    print(f"  Security:        {app['Security']}/10")
    print(f"  Strategic Fit:   {app['Strategic Fit']}/10")
    print(f"  Redundancy:      {'Yes' if app['Redundancy'] else 'No'}")

    # Get score breakdown
    breakdown = engine.get_score_breakdown(
        business_value=app['Business Value'],
        tech_health=app['Tech Health'],
        cost=app['Cost'],
        usage=app['Usage'],
        security=app['Security'],
        strategic_fit=app['Strategic Fit'],
        redundancy=app['Redundancy']
    )

    # Display breakdown
    print("\nScore Contribution by Criterion:")
    print(f"  Business Value:  {breakdown['business_value_contribution']:5.2f} points")
    print(f"  Tech Health:     {breakdown['tech_health_contribution']:5.2f} points")
    print(f"  Cost:            {breakdown['cost_contribution']:5.2f} points")
    print(f"  Usage:           {breakdown['usage_contribution']:5.2f} points")
    print(f"  Security:        {breakdown['security_contribution']:5.2f} points")
    print(f"  Strategic Fit:   {breakdown['strategic_fit_contribution']:5.2f} points")
    print(f"  Redundancy:      {breakdown['redundancy_contribution']:5.2f} points")
    print(f"  {'-' * 40}")
    print(f"  TOTAL:           {breakdown['total']:5.2f} points")

    # Show what's driving the score
    contributions = [
        ('Business Value', breakdown['business_value_contribution']),
        ('Tech Health', breakdown['tech_health_contribution']),
        ('Cost', breakdown['cost_contribution']),
        ('Usage', breakdown['usage_contribution']),
        ('Security', breakdown['security_contribution']),
        ('Strategic Fit', breakdown['strategic_fit_contribution']),
        ('Redundancy', breakdown['redundancy_contribution'])
    ]

    sorted_contrib = sorted(contributions, key=lambda x: x[1], reverse=True)

    print("\nTop Contributors to Score:")
    for i, (criterion, value) in enumerate(sorted_contrib[:3], 1):
        pct = (value / breakdown['total']) * 100 if breakdown['total'] > 0 else 0
        print(f"  {i}. {criterion:20} {value:5.2f} points ({pct:4.1f}%)")

    print("\nLowest Contributors to Score:")
    for i, (criterion, value) in enumerate(sorted_contrib[-3:], 1):
        pct = (value / breakdown['total']) * 100 if breakdown['total'] > 0 else 0
        print(f"  {i}. {criterion:20} {value:5.2f} points ({pct:4.1f}%)")


def main():
    print("=" * 80)
    print("Score Breakdown Analysis Example")
    print("=" * 80)

    # Initialize components
    data_handler = DataHandler()
    scoring_engine = ScoringEngine()

    # Load data
    df = data_handler.read_csv('data/assessment_template.csv')
    applications = df.to_dict('records')

    # Calculate scores
    scored_apps = scoring_engine.batch_calculate_scores(applications)
    scored_apps.sort(key=lambda x: x['Composite Score'], reverse=True)

    # Analyze top 3 applications
    print("\n" + "=" * 80)
    print("TOP 3 APPLICATIONS - Score Analysis")
    print("=" * 80)

    for app in scored_apps[:3]:
        analyze_application_score(app, scoring_engine)

    # Analyze bottom 3 applications
    print("\n\n" + "=" * 80)
    print("BOTTOM 3 APPLICATIONS - Score Analysis")
    print("=" * 80)

    for app in scored_apps[-3:]:
        analyze_application_score(app, scoring_engine)

    # Find applications with specific characteristics
    print("\n\n" + "=" * 80)
    print("APPLICATIONS WITH HIGH BUSINESS VALUE BUT LOW SCORE")
    print("=" * 80)

    interesting = [
        app for app in scored_apps
        if app['Business Value'] >= 8 and app['Composite Score'] < 60
    ]

    if interesting:
        for app in interesting[:3]:
            analyze_application_score(app, scoring_engine)
    else:
        print("\nNo applications match this criteria.")

    print("\n\nAnalysis complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()
