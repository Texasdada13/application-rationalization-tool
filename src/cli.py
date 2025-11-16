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
from .config_loader import load_config
from .visualizations import VisualizationEngine, quick_visualize

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
        # Load configuration
        config = load_config()
        scoring_weights = config.get_scoring_weights()
        time_thresholds = config.get_time_thresholds()

        click.echo("Using configured scoring weights:")
        click.echo(f"  Business Value: {scoring_weights.business_value:.0%}, "
                  f"Tech Health: {scoring_weights.tech_health:.0%}, "
                  f"Cost: {scoring_weights.cost:.0%}")
        click.echo()

        # Initialize components with configuration
        data_handler = DataHandler()
        scoring_engine = ScoringEngine(weights=scoring_weights)
        recommendation_engine = RecommendationEngine()
        time_framework = TIMEFramework(thresholds=time_thresholds)

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


@cli.command()
@click.option(
    '--input', '-i',
    type=click.Path(exists=True),
    required=True,
    help='Input CSV or Excel file with assessment results'
)
@click.option(
    '--output-dir', '-o',
    type=click.Path(),
    default='output/visualizations',
    help='Output directory for visualization files'
)
@click.option(
    '--type', '-t',
    'viz_type',
    type=click.Choice([
        'heatmap', 'time-quadrant', 'priority-matrix',
        'distributions', 'time-summary', 'dashboard', 'all'
    ], case_sensitive=False),
    default='all',
    help='Type of visualization to create'
)
@click.option(
    '--style',
    type=click.Choice(['professional', 'presentation', 'technical'], case_sensitive=False),
    default='professional',
    help='Visualization style'
)
def visualize(input: str, output_dir: str, viz_type: str, style: str):
    """
    Create visualizations from assessment results.

    Generates professional visualizations including heatmaps, TIME quadrants,
    priority matrices, and comprehensive dashboards.
    """
    click.echo("=" * 70)
    click.echo("Application Rationalization - Visualization Generator")
    click.echo("=" * 70)
    click.echo()

    try:
        # Load data
        click.echo(f"Loading data from: {input}")
        input_path = Path(input)

        if input_path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(input_path, engine='openpyxl')
        else:
            df = pd.read_csv(input_path)

        click.echo(f"Loaded {len(df)} applications")
        click.echo()

        # Initialize visualization engine
        viz_engine = VisualizationEngine(output_dir=Path(output_dir), style=style)

        # Determine which visualizations to create
        if viz_type == 'all':
            viz_types = ['heatmap', 'time-quadrant', 'priority-matrix',
                        'distributions', 'time-summary', 'dashboard']
        else:
            viz_types = [viz_type]

        click.echo(f"Creating {len(viz_types)} visualization(s)...")
        click.echo()

        created_files = {}

        # Create visualizations
        for vtype in viz_types:
            try:
                if vtype == 'heatmap':
                    click.echo("Creating score heatmap...")
                    path = viz_engine.create_score_heatmap(df)
                    created_files['Score Heatmap'] = path
                    click.echo(f"  ✓ Saved to: {path}")

                elif vtype == 'time-quadrant':
                    click.echo("Creating TIME framework quadrant...")
                    path = viz_engine.create_time_quadrant_heatmap(df)
                    created_files['TIME Quadrant'] = path
                    click.echo(f"  ✓ Saved to: {path}")

                elif vtype == 'priority-matrix':
                    click.echo("Creating priority matrix...")
                    path = viz_engine.create_priority_matrix(df)
                    created_files['Priority Matrix'] = path
                    click.echo(f"  ✓ Saved to: {path}")

                elif vtype == 'distributions':
                    click.echo("Creating distribution plots...")
                    path = viz_engine.create_distribution_plots(df)
                    created_files['Distributions'] = path
                    click.echo(f"  ✓ Saved to: {path}")

                elif vtype == 'time-summary':
                    click.echo("Creating TIME category summary...")
                    path = viz_engine.create_time_category_summary(df)
                    created_files['TIME Summary'] = path
                    click.echo(f"  ✓ Saved to: {path}")

                elif vtype == 'dashboard':
                    click.echo("Creating comprehensive dashboard...")
                    path = viz_engine.create_comprehensive_dashboard(df)
                    created_files['Dashboard'] = path
                    click.echo(f"  ✓ Saved to: {path}")

            except Exception as e:
                click.echo(f"  ✗ Failed to create {vtype}: {e}", err=True)
                logger.error(f"Visualization creation failed for {vtype}: {e}", exc_info=True)

        click.echo()
        click.echo("=" * 70)
        click.echo("VISUALIZATION SUMMARY")
        click.echo("=" * 70)
        click.echo(f"Created {len(created_files)} visualization(s)")
        click.echo(f"Output directory: {output_dir}")
        click.echo()

        if created_files:
            for viz_name, viz_path in created_files.items():
                click.echo(f"  • {viz_name}: {viz_path.name}")

        click.echo()
        click.echo("Visualization complete!")

    except Exception as e:
        logger.error(f"Visualization command failed: {e}", exc_info=True)
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
    '--output', '-o',
    type=click.Path(),
    default='output/export.xlsx',
    help='Output file path'
)
@click.option(
    '--format', '-f',
    'export_format',
    type=click.Choice(['powerbi', 'excel-enhanced', 'both'], case_sensitive=False),
    default='excel-enhanced',
    help='Export format type'
)
@click.option(
    '--timestamp/--no-timestamp',
    default=True,
    help='Include timestamp in output filename'
)
@click.option(
    '--charts/--no-charts',
    default=True,
    help='Include charts in Excel export (only for excel-enhanced format)'
)
def export(input: str, output: str, export_format: str, timestamp: bool, charts: bool):
    """
    Export assessment results in specialized formats.

    Supports Power BI-optimized exports and enhanced Excel reports with
    formatting, charts, and professional styling.
    """
    click.echo("=" * 70)
    click.echo("Application Rationalization - Data Export")
    click.echo("=" * 70)
    click.echo()

    try:
        # Load data
        click.echo(f"Loading data from: {input}")
        input_path = Path(input)

        if input_path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(input_path, engine='openpyxl')
        else:
            df = pd.read_csv(input_path)

        click.echo(f"Loaded {len(df)} applications")
        click.echo()

        # Initialize data handler
        data_handler = DataHandler()

        output_path = Path(output)
        created_files = []

        # Create exports based on format
        if export_format in ['powerbi', 'both']:
            click.echo("Creating Power BI-optimized Excel export...")
            if export_format == 'both':
                powerbi_output = output_path.parent / f"{output_path.stem}_powerbi{output_path.suffix}"
            else:
                powerbi_output = output_path

            path = data_handler.export_for_powerbi(df, powerbi_output, include_timestamp=timestamp)
            created_files.append(('Power BI Export', path))
            click.echo(f"  ✓ Power BI export saved to: {path}")
            click.echo()

        if export_format in ['excel-enhanced', 'both']:
            click.echo("Creating enhanced Excel export...")
            if export_format == 'both':
                excel_output = output_path.parent / f"{output_path.stem}_enhanced{output_path.suffix}"
            else:
                excel_output = output_path

            path = data_handler.export_enhanced_excel(
                df,
                excel_output,
                include_timestamp=timestamp,
                include_charts=charts
            )
            created_files.append(('Enhanced Excel Export', path))
            click.echo(f"  ✓ Enhanced Excel export saved to: {path}")
            click.echo()

        # Display summary
        click.echo("=" * 70)
        click.echo("EXPORT SUMMARY")
        click.echo("=" * 70)
        click.echo()

        for export_name, export_path in created_files:
            file_size = export_path.stat().st_size / 1024  # KB
            click.echo(f"  • {export_name}")
            click.echo(f"    Path: {export_path}")
            click.echo(f"    Size: {file_size:.1f} KB")
            click.echo()

        click.echo("Export complete!")

        # Display format-specific tips
        if 'powerbi' in export_format.lower():
            click.echo()
            click.echo("Power BI Import Tips:")
            click.echo("  1. Open Power BI Desktop")
            click.echo("  2. Get Data → Excel → Select the exported file")
            click.echo("  3. Choose 'Applications' table as the main fact table")
            click.echo("  4. Create relationships using 'Application_ID' field")
            click.echo("  5. Use 'Dimension_Scores' for detailed analysis")

    except Exception as e:
        logger.error(f"Export command failed: {e}", exc_info=True)
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
    '--output-dir', '-o',
    type=click.Path(),
    default='output/reports',
    help='Output directory for report bundle'
)
@click.option(
    '--name', '-n',
    default='assessment_report',
    help='Base name for report files'
)
@click.option(
    '--visualizations/--no-visualizations',
    default=True,
    help='Include visualizations in the bundle'
)
def generate_report(input: str, output_dir: str, name: str, visualizations: bool):
    """
    Generate a complete report bundle with all formats.

    Creates a comprehensive package including CSV, Power BI, Enhanced Excel,
    Tableau exports, visualizations, and documentation.
    """
    click.echo("=" * 70)
    click.echo("Application Rationalization - Complete Report Generator")
    click.echo("=" * 70)
    click.echo()

    try:
        # Load data
        click.echo(f"Loading data from: {input}")
        input_path = Path(input)

        if input_path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(input_path, engine='openpyxl')
        else:
            df = pd.read_csv(input_path)

        click.echo(f"Loaded {len(df)} applications")
        click.echo()

        # Initialize data handler
        data_handler = DataHandler()

        # Generate complete report bundle
        click.echo(f"Generating complete report bundle in: {output_dir}")
        click.echo(f"Report name: {name}")
        click.echo(f"Include visualizations: {'Yes' if visualizations else 'No'}")
        click.echo()

        click.echo("Creating exports...")
        bundle_files = data_handler.generate_complete_report_bundle(
            df,
            output_dir=output_dir,
            report_name=name,
            include_visualizations=visualizations
        )

        # Display results
        click.echo()
        click.echo("=" * 70)
        click.echo("REPORT BUNDLE GENERATED SUCCESSFULLY!")
        click.echo("=" * 70)
        click.echo()

        click.echo(f"Output directory: {output_dir}")
        click.echo(f"Total files created: {len(bundle_files)}")
        click.echo()

        click.echo("Generated files:")
        for file_type, file_path in bundle_files.items():
            file_size = file_path.stat().st_size / 1024  # KB
            click.echo(f"  • {file_type:20s} → {file_path.name:40s} ({file_size:7.1f} KB)")

        click.echo()
        click.echo("=" * 70)
        click.echo("NEXT STEPS")
        click.echo("=" * 70)
        click.echo()
        click.echo("1. Review README.md in the output directory for detailed instructions")
        click.echo("2. Open the executive Excel report for high-level insights")
        click.echo("3. Import Power BI or Tableau files for interactive dashboards")
        click.echo("4. Share appropriate formats with different stakeholders")
        click.echo()

        # Display summary statistics
        stats = data_handler.get_summary_statistics(df)
        click.echo("Portfolio Summary:")
        click.echo(f"  • Total Applications: {stats['total_applications']}")
        click.echo(f"  • Total Annual Cost: ${stats['total_cost']:,.0f}")
        click.echo(f"  • Average Composite Score: {stats.get('average_composite_score', 0):.1f}/100")
        click.echo()

    except Exception as e:
        logger.error(f"Report generation failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option(
    '--input', '-i',
    type=click.Path(exists=True),
    required=True,
    help='Input survey CSV file'
)
@click.option(
    '--output', '-o',
    type=click.Path(),
    default='output/survey_aggregated.csv',
    help='Output file for aggregated survey data'
)
@click.option(
    '--method', '-m',
    type=click.Choice(['mean', 'median', 'weighted'], case_sensitive=False),
    default='mean',
    help='Aggregation method for multiple responses'
)
def import_survey(input: str, output: str, method: str):
    """
    Import and aggregate stakeholder survey data.

    Reads survey responses, validates data, aggregates multiple stakeholder
    responses per application, and calculates consensus metrics.
    """
    click.echo("=" * 70)
    click.echo("Application Rationalization - Survey Import")
    click.echo("=" * 70)
    click.echo()

    try:
        # Initialize data handler
        data_handler = DataHandler()

        # Load survey data
        click.echo(f"Loading survey data from: {input}")
        survey_df = data_handler.read_survey_data(input)
        click.echo(f"Loaded {len(survey_df)} survey responses")
        click.echo()

        # Validate survey data
        click.echo("Validating survey data...")
        is_valid, errors = data_handler.validate_survey_data(survey_df)

        if not is_valid:
            click.echo("Survey data validation warnings:", err=True)
            for error in errors:
                click.echo(f"  - {error}", err=True)
            click.echo()

        # Show survey statistics
        unique_apps = survey_df['Application Name'].nunique()
        unique_stakeholders = survey_df['Stakeholder Name'].nunique()
        avg_responses_per_app = len(survey_df) / unique_apps

        click.echo("=" * 70)
        click.echo("SURVEY DATA SUMMARY")
        click.echo("=" * 70)
        click.echo(f"Total Responses: {len(survey_df)}")
        click.echo(f"Unique Applications: {unique_apps}")
        click.echo(f"Unique Stakeholders: {unique_stakeholders}")
        click.echo(f"Average Responses per App: {avg_responses_per_app:.1f}")
        click.echo()

        # Aggregate responses
        click.echo(f"Aggregating responses using {method} method...")
        aggregated_df = data_handler.aggregate_survey_responses(survey_df, method)
        click.echo(f"Aggregated {len(survey_df)} responses into {len(aggregated_df)} applications")
        click.echo()

        # Show top apps by consensus
        if 'Overall Consensus Score' in aggregated_df.columns:
            click.echo("Applications with highest stakeholder consensus:")
            top_consensus = aggregated_df.nlargest(5, 'Overall Consensus Score')[
                ['Application Name', 'Overall Consensus Score', 'Survey Response Count']
            ]
            click.echo(tabulate(
                top_consensus,
                headers='keys',
                tablefmt='grid',
                showindex=False
            ))
            click.echo()

        # Save aggregated data
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        aggregated_df.to_csv(output_path, index=False)

        click.echo(f"Aggregated survey data saved to: {output_path}")
        click.echo()
        click.echo("Survey import complete!")
        click.echo()
        click.echo("Next steps:")
        click.echo("  1. Use 'merge-survey-data' command to merge with assessment data")
        click.echo("  2. Review aggregated scores and consensus metrics")

    except Exception as e:
        logger.error(f"Survey import failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option(
    '--assessment', '-a',
    type=click.Path(exists=True),
    required=True,
    help='Input CSV/Excel file with assessment results'
)
@click.option(
    '--survey', '-s',
    type=click.Path(exists=True),
    required=True,
    help='Input CSV file with aggregated survey data'
)
@click.option(
    '--output', '-o',
    type=click.Path(),
    default='output/merged_assessment.csv',
    help='Output file for merged data'
)
@click.option(
    '--survey-weight', '-w',
    type=float,
    default=0.3,
    help='Weight for survey data (0-1), default 0.3 (30%)'
)
def merge_survey_data(assessment: str, survey: str, output: str, survey_weight: float):
    """
    Merge stakeholder survey data with quantitative assessment scores.

    Combines survey feedback with existing assessment data, creating
    survey-adjusted scores and variance analysis.
    """
    click.echo("=" * 70)
    click.echo("Application Rationalization - Survey Data Merge")
    click.echo("=" * 70)
    click.echo()

    try:
        # Initialize data handler
        data_handler = DataHandler()

        # Load assessment data
        click.echo(f"Loading assessment data from: {assessment}")
        assessment_path = Path(assessment)
        if assessment_path.suffix.lower() in ['.xlsx', '.xls']:
            assessment_df = pd.read_excel(assessment_path, engine='openpyxl')
        else:
            assessment_df = pd.read_csv(assessment_path)
        click.echo(f"Loaded {len(assessment_df)} applications")

        # Load survey data
        click.echo(f"Loading survey data from: {survey}")
        survey_df = pd.read_csv(survey)
        click.echo(f"Loaded {len(survey_df)} survey aggregations")
        click.echo()

        # Merge data
        click.echo(f"Merging data with survey weight: {survey_weight:.0%}")
        merged_df = data_handler.merge_survey_with_assessment(
            assessment_df,
            survey_df,
            survey_weight=survey_weight
        )
        click.echo(f"Merged {len(merged_df)} applications")
        click.echo()

        # Calculate survey impact
        click.echo("Analyzing survey impact...")
        impact = data_handler.calculate_survey_impact(merged_df)
        click.echo()

        # Display impact summary
        click.echo("=" * 70)
        click.echo("SURVEY IMPACT SUMMARY")
        click.echo("=" * 70)

        if 'consensus_summary' in impact:
            cons = impact['consensus_summary']
            click.echo(f"\nConsensus Metrics:")
            click.echo(f"  • Average Consensus Score: {cons['average_consensus']:.2f}/5")
            click.echo(f"  • High Consensus Apps: {cons['high_consensus_count']}")
            click.echo(f"  • Low Consensus Apps: {cons['low_consensus_count']}")

        if 'sentiment_analysis' in impact:
            click.echo(f"\nStakeholder Sentiment Distribution:")
            for category, count in impact['sentiment_analysis'].items():
                click.echo(f"  • {category}: {count}")

        if 'high_variance_apps' in impact and len(impact['high_variance_apps']) > 0:
            click.echo(f"\nApplications with High Variance (qualitative vs quantitative):")
            click.echo(f"  Found {len(impact['high_variance_apps'])} apps with significant differences")

        if 'needs_attention' in impact and len(impact['needs_attention']) > 0:
            click.echo(f"\nApplications Needing Attention:")
            click.echo(f"  {len(impact['needs_attention'])} apps are critical but have low satisfaction")

        click.echo()

        # Save merged data
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        merged_df.to_csv(output_path, index=False)

        click.echo(f"Merged data saved to: {output_path}")
        click.echo()
        click.echo("Survey merge complete!")
        click.echo()
        click.echo("Next steps:")
        click.echo("  1. Use 'generate-survey-report' for detailed Excel analysis")
        click.echo("  2. Review variance analysis to identify discrepancies")
        click.echo("  3. Investigate high variance applications")

    except Exception as e:
        logger.error(f"Survey merge failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option(
    '--input', '-i',
    type=click.Path(exists=True),
    required=True,
    help='Input CSV file with merged assessment and survey data'
)
@click.option(
    '--output', '-o',
    type=click.Path(),
    default='output/survey_analysis.xlsx',
    help='Output Excel file for survey analysis report'
)
@click.option(
    '--timestamp/--no-timestamp',
    default=True,
    help='Include timestamp in output filename'
)
def generate_survey_report(input: str, output: str, timestamp: bool):
    """
    Generate comprehensive survey analysis report.

    Creates a multi-sheet Excel workbook with survey analysis, variance
    analysis, consensus metrics, and qualitative feedback summary.
    """
    click.echo("=" * 70)
    click.echo("Application Rationalization - Survey Analysis Report")
    click.echo("=" * 70)
    click.echo()

    try:
        # Initialize data handler
        data_handler = DataHandler()

        # Load merged data
        click.echo(f"Loading merged data from: {input}")
        merged_df = pd.read_csv(input)
        click.echo(f"Loaded {len(merged_df)} applications")
        click.echo()

        # Generate survey analysis report
        click.echo("Generating comprehensive survey analysis report...")
        output_path = data_handler.export_survey_analysis(
            merged_df,
            output,
            include_timestamp=timestamp
        )

        click.echo()
        click.echo("=" * 70)
        click.echo("SURVEY ANALYSIS REPORT GENERATED!")
        click.echo("=" * 70)
        click.echo()

        file_size = output_path.stat().st_size / 1024
        click.echo(f"Report saved to: {output_path}")
        click.echo(f"File size: {file_size:.1f} KB")
        click.echo()

        click.echo("Report includes:")
        click.echo("  • Survey Analysis - Merged scores with survey adjustments")
        click.echo("  • High Variance - Apps with significant score differences")
        click.echo("  • Impact Summary - Statistical analysis of survey impact")
        click.echo("  • Needs Attention - Critical apps with low satisfaction")
        click.echo("  • Qualitative Feedback - Stakeholder comments by app")
        click.echo()

        # Calculate and display key metrics
        impact = data_handler.calculate_survey_impact(merged_df)

        apps_with_survey = merged_df['Has Survey Data'].sum()
        click.echo("Key Findings:")
        click.echo(f"  • {apps_with_survey} applications have survey data")

        if 'consensus_summary' in impact:
            avg_consensus = impact['consensus_summary']['average_consensus']
            click.echo(f"  • Average stakeholder consensus: {avg_consensus:.2f}/5")

        if 'high_variance_apps' in impact:
            high_var_count = len(impact['high_variance_apps'])
            click.echo(f"  • {high_var_count} apps show high variance between scores")

        if 'needs_attention' in impact:
            needs_attn_count = len(impact['needs_attention'])
            click.echo(f"  • {needs_attn_count} critical apps need attention")

        click.echo()
        click.echo("Survey analysis complete!")

    except Exception as e:
        logger.error(f"Survey report generation failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    cli()
