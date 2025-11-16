"""
Command Line Interface Module
Provides interactive CLI for the application rationalization tool.
"""

import click
from pathlib import Path
from typing import Optional
import logging
from tabulate import tabulate
import pandas as pd

from .data_handler import DataHandler
from .scoring_engine import ScoringEngine, ScoringWeights
from .recommendation_engine import RecommendationEngine
from .time_framework import TIMEFramework

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    Application Rationalization Assessment Tool

    A comprehensive tool for evaluating and rationalizing software application portfolios.
    """
    pass


@cli.command()
@click.option(
    '--input', '-i',
    type=click.Path(exists=True),
    required=True,
    help='Input CSV or Excel file with application data'
)
@click.option(
    '--output', '-o',
    type=click.Path(),
    default='output/assessment_results.csv',
    help='Output file path for results'
)
@click.option(
    '--format', '-f',
    type=click.Choice(['csv', 'excel'], case_sensitive=False),
    default='csv',
    help='Output format'
)
@click.option(
    '--timestamp/--no-timestamp',
    default=True,
    help='Include timestamp in output filename'
)
def assess(input: str, output: str, format: str, timestamp: bool):
    """
    Run complete assessment on application portfolio.

    Reads application data, calculates scores, generates recommendations,
    and writes results to output file.
    """
    click.echo("=" * 70)
    click.echo("Application Rationalization Assessment Tool")
    click.echo("=" * 70)
    click.echo()

    try:
        # Initialize components
        data_handler = DataHandler()
        scoring_engine = ScoringEngine()
        recommendation_engine = RecommendationEngine()

        # Read input data
        click.echo(f"Reading data from: {input}")
        input_path = Path(input)

        if input_path.suffix.lower() in ['.xlsx', '.xls']:
            df = data_handler.read_excel(input_path)
        else:
            df = data_handler.read_csv(input_path)

        click.echo(f"Loaded {len(df)} applications")
        click.echo()

        # Validate data
        click.echo("Validating data...")
        is_valid, errors = data_handler.validate_data(df)

        if not is_valid:
            click.echo("Data validation warnings:", err=True)
            for error in errors:
                click.echo(f"  - {error}", err=True)
            click.echo()

        # Calculate scores
        click.echo("Calculating composite scores...")
        applications = df.to_dict('records')
        scored_apps = scoring_engine.batch_calculate_scores(applications)
        click.echo("Scores calculated successfully")
        click.echo()

        # Generate recommendations
        click.echo("Generating rationalization recommendations...")
        final_apps = recommendation_engine.batch_generate_recommendations(scored_apps)
        click.echo("Recommendations generated successfully")
        click.echo()

        # Apply TIME framework categorization
        click.echo("Applying TIME framework categorization...")
        time_framework = TIMEFramework()
        final_apps = time_framework.batch_categorize(final_apps)
        click.echo("TIME categories assigned successfully")
        click.echo()

        # Convert back to DataFrame
        results_df = pd.DataFrame(final_apps)

        # Display summary
        click.echo("=" * 70)
        click.echo("PORTFOLIO SUMMARY")
        click.echo("=" * 70)

        stats = data_handler.get_summary_statistics(results_df)
        click.echo(f"Total Applications: {stats['total_applications']}")
        click.echo(f"Total Annual Cost: ${stats['total_cost']:,.0f}")
        click.echo(f"Average Business Value: {stats['average_business_value']:.1f}/10")
        click.echo(f"Average Tech Health: {stats['average_tech_health']:.1f}/10")
        click.echo(f"Average Security: {stats['average_security']:.1f}/10")
        click.echo(f"Redundant Applications: {stats['redundant_applications']}")

        if 'average_composite_score' in stats:
            click.echo(f"Average Composite Score: {stats['average_composite_score']:.1f}/100")

        click.echo()

        # Display recommendation distribution
        rec_summary = recommendation_engine.get_portfolio_summary()
        click.echo("=" * 70)
        click.echo("RECOMMENDATION DISTRIBUTION")
        click.echo("=" * 70)

        table_data = [
            [action, count, f"{rec_summary['percentages'].get(action, 0):.1f}%"]
            for action, count in rec_summary['distribution'].items()
            if count > 0
        ]
        click.echo(tabulate(
            table_data,
            headers=['Action', 'Count', 'Percentage'],
            tablefmt='grid'
        ))
        click.echo()

        # Display TIME framework distribution
        time_summary = time_framework.get_category_summary()
        click.echo("=" * 70)
        click.echo("TIME FRAMEWORK DISTRIBUTION")
        click.echo("=" * 70)

        time_table_data = [
            [category, count, f"{time_summary['percentages'].get(category, 0):.1f}%"]
            for category, count in time_summary['distribution'].items()
            if count > 0
        ]
        click.echo(tabulate(
            time_table_data,
            headers=['TIME Category', 'Count', 'Percentage'],
            tablefmt='grid'
        ))
        click.echo()

        # Write output
        output_path = Path(output)
        click.echo(f"Writing results to: {output}")

        if format.lower() == 'excel':
            if not output_path.suffix:
                output_path = output_path.with_suffix('.xlsx')
            final_path = data_handler.write_excel(results_df, output_path, include_timestamp=timestamp)
        else:
            if not output_path.suffix:
                output_path = output_path.with_suffix('.csv')
            final_path = data_handler.write_csv(results_df, output_path, include_timestamp=timestamp)

        click.echo(f"Results written to: {final_path}")
        click.echo()
        click.echo("Assessment complete!")

    except Exception as e:
        logger.error(f"Assessment failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option(
    '--input', '-i',
    type=click.Path(exists=True),
    required=True,
    help='Input CSV or Excel file with assessment results'
)
@click.option(
    '--action', '-a',
    type=click.Choice([
        'Retain', 'Invest', 'Maintain', 'Tolerate',
        'Migrate', 'Consolidate', 'Retire', 'Immediate Action Required'
    ]),
    help='Filter by action recommendation'
)
@click.option(
    '--time-category', '-tc',
    type=click.Choice(['Invest', 'Tolerate', 'Migrate', 'Eliminate']),
    help='Filter by TIME framework category'
)
@click.option(
    '--min-score',
    type=float,
    help='Minimum composite score'
)
@click.option(
    '--max-score',
    type=float,
    help='Maximum composite score'
)
@click.option(
    '--top', '-t',
    type=int,
    default=10,
    help='Number of results to display'
)
def list_apps(input: str, action: Optional[str], time_category: Optional[str],
              min_score: Optional[float], max_score: Optional[float], top: int):
    """
    List applications with optional filtering.
    """
    try:
        data_handler = DataHandler()

        # Read data
        input_path = Path(input)
        if input_path.suffix.lower() in ['.xlsx', '.xls']:
            df = data_handler.read_excel(input_path)
        else:
            df = data_handler.read_csv(input_path)

        # Apply filters
        filtered_df = data_handler.filter_applications(
            df,
            min_score=min_score,
            max_score=max_score,
            action=action
        )

        # Apply TIME category filter if specified
        if time_category and 'TIME Category' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['TIME Category'] == time_category]

        # Limit results
        display_df = filtered_df.head(top)

        # Display
        if len(display_df) == 0:
            click.echo("No applications match the specified criteria.")
            return

        click.echo(f"\nShowing {len(display_df)} of {len(filtered_df)} applications:\n")

        # Select columns to display
        display_columns = [
            'Application Name', 'Owner', 'Business Value',
            'Tech Health', 'Composite Score', 'Action Recommendation', 'TIME Category'
        ]
        display_columns = [col for col in display_columns if col in display_df.columns]

        click.echo(tabulate(
            display_df[display_columns],
            headers='keys',
            tablefmt='grid',
            showindex=False
        ))

    except Exception as e:
        logger.error(f"List command failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option(
    '--input', '-i',
    type=click.Path(exists=True),
    required=True,
    help='Input CSV or Excel file with assessment results'
)
def summary(input: str):
    """
    Display summary statistics for the portfolio.
    """
    try:
        data_handler = DataHandler()

        # Read data
        input_path = Path(input)
        if input_path.suffix.lower() in ['.xlsx', '.xls']:
            df = data_handler.read_excel(input_path)
        else:
            df = data_handler.read_csv(input_path)

        # Get statistics
        stats = data_handler.get_summary_statistics(df)

        click.echo("\n" + "=" * 70)
        click.echo("PORTFOLIO SUMMARY STATISTICS")
        click.echo("=" * 70 + "\n")

        click.echo(f"Total Applications: {stats['total_applications']}")
        click.echo(f"Total Annual Cost: ${stats['total_cost']:,.0f}")
        click.echo(f"Average Business Value: {stats['average_business_value']:.2f}/10")
        click.echo(f"Average Tech Health: {stats['average_tech_health']:.2f}/10")
        click.echo(f"Average Security: {stats['average_security']:.2f}/10")
        click.echo(f"Redundant Applications: {stats['redundant_applications']}")

        if 'average_composite_score' in stats:
            click.echo(f"\nAverage Composite Score: {stats['average_composite_score']:.2f}/100")
            click.echo(f"Median Composite Score: {stats['median_composite_score']:.2f}/100")

        if 'action_distribution' in stats:
            click.echo("\n" + "=" * 70)
            click.echo("ACTION DISTRIBUTION")
            click.echo("=" * 70 + "\n")

            table_data = [
                [action, count]
                for action, count in stats['action_distribution'].items()
            ]
            click.echo(tabulate(
                table_data,
                headers=['Action', 'Count'],
                tablefmt='grid'
            ))

    except Exception as e:
        logger.error(f"Summary command failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    cli()
