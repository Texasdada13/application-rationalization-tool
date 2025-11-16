#!/usr/bin/env python3
"""
Example: Batch Processing Multiple Portfolios

This example demonstrates how to process multiple application portfolios
and generate comparative reports.
"""

import sys
from pathlib import Path
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_handler import DataHandler
from src.scoring_engine import ScoringEngine
from src.recommendation_engine import RecommendationEngine


def process_portfolio(input_file: Path, portfolio_name: str) -> dict:
    """
    Process a single portfolio and return summary statistics.

    Args:
        input_file: Path to the portfolio CSV file
        portfolio_name: Name of the portfolio

    Returns:
        Dictionary with portfolio statistics
    """
    print(f"\nProcessing: {portfolio_name}")
    print("-" * 60)

    # Initialize components
    data_handler = DataHandler()
    scoring_engine = ScoringEngine()
    recommendation_engine = RecommendationEngine()

    try:
        # Load and process
        df = data_handler.read_csv(input_file)
        applications = df.to_dict('records')

        scored_apps = scoring_engine.batch_calculate_scores(applications)
        results = recommendation_engine.batch_generate_recommendations(scored_apps)

        # Get statistics
        results_df = pd.DataFrame(results)
        stats = data_handler.get_summary_statistics(results_df)
        rec_summary = recommendation_engine.get_portfolio_summary()

        # Save results
        output_file = Path(f'output/{portfolio_name.lower()}_results.xlsx')
        data_handler.write_excel(results_df, output_file, include_timestamp=True)

        print(f"✓ Processed {stats['total_applications']} applications")
        print(f"✓ Results saved to: {output_file}")

        # Return summary for comparison
        return {
            'portfolio': portfolio_name,
            'applications': stats['total_applications'],
            'total_cost': stats['total_cost'],
            'avg_score': stats.get('average_composite_score', 0),
            'avg_business_value': stats['average_business_value'],
            'avg_tech_health': stats['average_tech_health'],
            'avg_security': stats['average_security'],
            'redundant': stats['redundant_applications'],
            'recommendations': rec_summary['distribution']
        }

    except Exception as e:
        print(f"✗ Error processing {portfolio_name}: {e}")
        return None


def generate_comparative_report(summaries: list):
    """Generate comparative report across portfolios."""

    print("\n" + "=" * 80)
    print("COMPARATIVE PORTFOLIO ANALYSIS")
    print("=" * 80)

    # Create comparison DataFrame
    comparison_data = []
    for summary in summaries:
        if summary:
            comparison_data.append({
                'Portfolio': summary['portfolio'],
                'Apps': summary['applications'],
                'Total Cost': f"${summary['total_cost']:,.0f}",
                'Avg Score': f"{summary['avg_score']:.1f}",
                'Avg BV': f"{summary['avg_business_value']:.1f}",
                'Avg TH': f"{summary['avg_tech_health']:.1f}",
                'Avg Sec': f"{summary['avg_security']:.1f}",
                'Redundant': summary['redundant']
            })

    if comparison_data:
        df = pd.DataFrame(comparison_data)
        print("\n" + df.to_string(index=False))

    # Action recommendations summary
    print("\n\nACTION RECOMMENDATIONS BY PORTFOLIO")
    print("-" * 80)

    for summary in summaries:
        if summary:
            print(f"\n{summary['portfolio']}:")
            for action, count in sorted(summary['recommendations'].items(),
                                       key=lambda x: x[1], reverse=True):
                if count > 0:
                    print(f"  {action:30} {count:2d} apps")


def main():
    print("=" * 80)
    print("Batch Processing Example")
    print("=" * 80)

    # Define portfolios to process
    # In a real scenario, these would be different CSV files
    portfolios = [
        {
            'file': Path('data/assessment_template.csv'),
            'name': 'Primary Portfolio'
        }
        # Add more portfolios as needed:
        # {
        #     'file': Path('data/emea_portfolio.csv'),
        #     'name': 'EMEA Portfolio'
        # },
        # {
        #     'file': Path('data/apac_portfolio.csv'),
        #     'name': 'APAC Portfolio'
        # }
    ]

    # Process all portfolios
    summaries = []
    for portfolio in portfolios:
        if portfolio['file'].exists():
            summary = process_portfolio(portfolio['file'], portfolio['name'])
            if summary:
                summaries.append(summary)
        else:
            print(f"\n✗ File not found: {portfolio['file']}")

    # Generate comparative report
    if summaries:
        generate_comparative_report(summaries)

    print("\n\nBatch processing complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()
