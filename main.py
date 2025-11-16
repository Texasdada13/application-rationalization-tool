#!/usr/bin/env python3
"""
Application Rationalization Assessment Tool - Main Entry Point

A comprehensive Python tool for evaluating and rationalizing software application portfolios.
Analyzes applications based on multiple criteria and provides actionable recommendations.

Usage:
    python main.py                          # Run interactive assessment
    python -m src.cli assess -i data/assessment_template.csv  # CLI mode
    python -m src.cli --help                # Show all CLI options
"""

import sys
from pathlib import Path
import logging
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data_handler import DataHandler
from src.scoring_engine import ScoringEngine
from src.recommendation_engine import RecommendationEngine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """
    Main entry point for the application rationalization tool.

    Runs a complete assessment on the default template data and generates results.
    """
    print("=" * 80)
    print(" " * 20 + "APPLICATION RATIONALIZATION ASSESSMENT TOOL")
    print("=" * 80)
    print()

    try:
        # Initialize components
        logger.info("Initializing assessment components...")
        data_handler = DataHandler()
        scoring_engine = ScoringEngine()
        recommendation_engine = RecommendationEngine()

        # Default data file
        input_file = Path('data/assessment_template.csv')

        if not input_file.exists():
            print(f"Error: Input file not found: {input_file}")
            print("Please ensure data/assessment_template.csv exists.")
            return 1

        # Read input data
        print(f"Reading application data from: {input_file}")
        df = data_handler.read_csv(input_file)
        print(f"Loaded {len(df)} applications")
        print()

        # Validate data
        print("Validating application data...")
        is_valid, errors = data_handler.validate_data(df)

        if not is_valid:
            print("\nData validation warnings:")
            for error in errors:
                print(f"  - {error}")
            print()
        else:
            print("Data validation passed")
            print()

        # Calculate scores
        print("Calculating composite scores for all applications...")
        applications = df.to_dict('records')
        scored_apps = scoring_engine.batch_calculate_scores(applications)
        print(f"Calculated scores for {len(scored_apps)} applications")
        print()

        # Generate recommendations
        print("Generating rationalization recommendations...")
        final_apps = recommendation_engine.batch_generate_recommendations(scored_apps)
        print(f"Generated recommendations for {len(final_apps)} applications")
        print()

        # Convert to DataFrame
        results_df = pd.DataFrame(final_apps)

        # Display portfolio summary
        print("=" * 80)
        print(" " * 30 + "PORTFOLIO SUMMARY")
        print("=" * 80)

        stats = data_handler.get_summary_statistics(results_df)
        print(f"\nTotal Applications:        {stats['total_applications']}")
        print(f"Total Annual Cost:         ${stats['total_cost']:,.0f}")
        print(f"Average Business Value:    {stats['average_business_value']:.2f}/10")
        print(f"Average Tech Health:       {stats['average_tech_health']:.2f}/10")
        print(f"Average Security Score:    {stats['average_security']:.2f}/10")
        print(f"Redundant Applications:    {stats['redundant_applications']}")

        if 'average_composite_score' in stats:
            print(f"Average Composite Score:   {stats['average_composite_score']:.2f}/100")
            print(f"Median Composite Score:    {stats['median_composite_score']:.2f}/100")

        # Display recommendation distribution
        print("\n" + "=" * 80)
        print(" " * 25 + "RECOMMENDATION DISTRIBUTION")
        print("=" * 80)

        rec_summary = recommendation_engine.get_portfolio_summary()
        print()
        for action, count in sorted(
            rec_summary['distribution'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            if count > 0:
                percentage = rec_summary['percentages'][action]
                print(f"{action:30} {count:3d} applications ({percentage:5.1f}%)")

        # Display top priorities
        print("\n" + "=" * 80)
        print(" " * 25 + "TOP PRIORITY APPLICATIONS")
        print("=" * 80)

        # Immediate action items
        immediate = [app for app in final_apps
                    if app['Action Recommendation'] == 'Immediate Action Required']
        if immediate:
            print("\nIMMEDIATE ACTION REQUIRED:")
            for i, app in enumerate(immediate[:5], 1):
                print(f"\n{i}. {app['Application Name']}")
                print(f"   Score: {app['Composite Score']:.1f}/100")
                print(f"   Reason: {app['Comments'][:100]}...")

        # Retire candidates
        retire = sorted(
            [app for app in final_apps if app['Action Recommendation'] == 'Retire'],
            key=lambda x: x['Composite Score']
        )
        if retire:
            print("\n\nTOP RETIREMENT CANDIDATES:")
            for i, app in enumerate(retire[:5], 1):
                print(f"\n{i}. {app['Application Name']}")
                print(f"   Score: {app['Composite Score']:.1f}/100")
                print(f"   Annual Cost: ${app['Cost']:,.0f}")
                print(f"   Reason: {app['Comments'][:100]}...")

        # Investment priorities
        invest = sorted(
            [app for app in final_apps if app['Action Recommendation'] == 'Invest'],
            key=lambda x: x['Composite Score'],
            reverse=True
        )
        if invest:
            print("\n\nTOP INVESTMENT PRIORITIES:")
            for i, app in enumerate(invest[:5], 1):
                print(f"\n{i}. {app['Application Name']}")
                print(f"   Score: {app['Composite Score']:.1f}/100")
                print(f"   Business Value: {app['Business Value']}/10")
                print(f"   Reason: {app['Comments'][:100]}...")

        # Save results
        print("\n" + "=" * 80)
        print(" " * 30 + "SAVING RESULTS")
        print("=" * 80)

        output_csv = Path('output/assessment_results.csv')
        output_excel = Path('output/assessment_results.xlsx')

        # Save CSV
        csv_path = data_handler.write_csv(results_df, output_csv, include_timestamp=True)
        print(f"\nCSV results saved to:   {csv_path}")

        # Save Excel
        excel_path = data_handler.write_excel(results_df, output_excel, include_timestamp=True)
        print(f"Excel results saved to: {excel_path}")

        print("\n" + "=" * 80)
        print(" " * 25 + "ASSESSMENT COMPLETE!")
        print("=" * 80)
        print("\nFor advanced features, use the CLI:")
        print("  python -m src.cli assess -i data/assessment_template.csv")
        print("  python -m src.cli list-apps -i output/assessment_results.csv")
        print("  python -m src.cli summary -i output/assessment_results.csv")
        print("  python -m src.cli --help")
        print()

        return 0

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        print(f"\nError: {e}")
        return 1

    except Exception as e:
        logger.error(f"Assessment failed: {e}", exc_info=True)
        print(f"\nError during assessment: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
