#!/usr/bin/env python3
"""
Visualization Examples
Demonstrates how to create various visualizations for application rationalization assessments.

This example shows how to:
1. Create individual visualizations (heatmaps, TIME quadrants, etc.)
2. Create comprehensive dashboards
3. Customize visualization styles and parameters
4. Use the quick visualization helper function
"""

from pathlib import Path
import sys

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.visualizations import VisualizationEngine, quick_visualize
from src.data_handler import DataHandler
from src.scoring_engine import ScoringEngine
from src.recommendation_engine import RecommendationEngine
from src.time_framework import TIMEFramework
import pandas as pd


def example_1_basic_heatmap():
    """
    Example 1: Create a basic application score heatmap.

    This visualization shows all applications and their scores across
    different dimensions, making it easy to spot patterns and outliers.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Score Heatmap")
    print("=" * 70)

    # Load sample data
    data_handler = DataHandler()
    df = data_handler.read_csv('data/assessment_template.csv')

    # Calculate scores
    scoring_engine = ScoringEngine()
    rec_engine = RecommendationEngine()
    time_framework = TIMEFramework()

    applications = df.to_dict('records')
    scored_apps = scoring_engine.batch_calculate_scores(applications)
    final_apps = rec_engine.batch_generate_recommendations(scored_apps)
    final_apps = time_framework.batch_categorize(final_apps)

    results_df = pd.DataFrame(final_apps)

    # Create visualization engine
    viz_engine = VisualizationEngine(
        output_dir=Path('output/visualizations/examples'),
        style='professional'
    )

    # Create score heatmap
    print("\nCreating score heatmap...")
    heatmap_path = viz_engine.create_score_heatmap(
        results_df,
        output_file='example_1_score_heatmap.png',
        max_apps=20,  # Limit to top 20 for readability
        title='Application Portfolio Score Analysis - Top 20 Applications'
    )

    print(f"✓ Heatmap saved to: {heatmap_path}")
    print("\nThis heatmap helps you:")
    print("  • Identify high and low performers across dimensions")
    print("  • Spot applications with unbalanced scores")
    print("  • Quickly compare relative strengths and weaknesses")


def example_2_time_quadrant():
    """
    Example 2: Create TIME framework quadrant visualization.

    This scatter plot shows where each application falls in the TIME
    framework, making strategic recommendations clearer.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: TIME Framework Quadrant")
    print("=" * 70)

    # Load and process data
    data_handler = DataHandler()
    df = data_handler.read_csv('data/assessment_template.csv')

    scoring_engine = ScoringEngine()
    rec_engine = RecommendationEngine()
    time_framework = TIMEFramework()

    applications = df.to_dict('records')
    scored_apps = scoring_engine.batch_calculate_scores(applications)
    final_apps = rec_engine.batch_generate_recommendations(scored_apps)
    final_apps = time_framework.batch_categorize(final_apps)

    results_df = pd.DataFrame(final_apps)

    # Create visualization
    viz_engine = VisualizationEngine(output_dir=Path('output/visualizations/examples'))

    print("\nCreating TIME quadrant visualization...")
    quadrant_path = viz_engine.create_time_quadrant_heatmap(
        results_df,
        output_file='example_2_time_quadrant.png',
        show_labels=True,  # Show application names
        title='TIME Framework: Strategic Application Positioning'
    )

    print(f"✓ TIME quadrant saved to: {quadrant_path}")
    print("\nThis visualization helps you:")
    print("  • See strategic positioning of all applications")
    print("  • Identify INVEST candidates (top-right quadrant)")
    print("  • Spot ELIMINATE candidates (bottom-left quadrant)")
    print("  • Understand technical debt vs. business value trade-offs")


def example_3_priority_matrix():
    """
    Example 3: Create priority matrix with custom metrics.

    This bubble chart allows you to visualize up to 4 dimensions
    simultaneously using position, size, and color.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Priority Matrix Bubble Chart")
    print("=" * 70)

    # Load and process data
    data_handler = DataHandler()
    df = data_handler.read_csv('data/assessment_template.csv')

    scoring_engine = ScoringEngine()
    rec_engine = RecommendationEngine()
    time_framework = TIMEFramework()

    applications = df.to_dict('records')
    scored_apps = scoring_engine.batch_calculate_scores(applications)
    final_apps = rec_engine.batch_generate_recommendations(scored_apps)
    final_apps = time_framework.batch_categorize(final_apps)

    results_df = pd.DataFrame(final_apps)

    viz_engine = VisualizationEngine(output_dir=Path('output/visualizations/examples'))

    print("\nCreating priority matrix...")
    matrix_path = viz_engine.create_priority_matrix(
        results_df,
        output_file='example_3_priority_matrix.png',
        x_metric='Composite Score',     # X-axis: Overall score
        y_metric='Business Value',      # Y-axis: Business value
        size_metric='Cost',              # Bubble size: Annual cost
        color_metric='Tech Health',     # Bubble color: Technical health
        title='Application Priority Matrix\n(Size = Cost, Color = Tech Health)'
    )

    print(f"✓ Priority matrix saved to: {matrix_path}")
    print("\nThis visualization helps you:")
    print("  • Identify high-value applications needing attention")
    print("  • See cost distribution across the portfolio")
    print("  • Spot technical debt in high-value applications")
    print("  • Prioritize modernization investments")


def example_4_distribution_analysis():
    """
    Example 4: Create score distribution plots.

    These histograms show the distribution of scores across the portfolio,
    helping identify overall health and trends.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Score Distribution Analysis")
    print("=" * 70)

    # Load and process data
    data_handler = DataHandler()
    df = data_handler.read_csv('data/assessment_template.csv')

    scoring_engine = ScoringEngine()
    rec_engine = RecommendationEngine()

    applications = df.to_dict('records')
    scored_apps = scoring_engine.batch_calculate_scores(applications)
    final_apps = rec_engine.batch_generate_recommendations(scored_apps)

    results_df = pd.DataFrame(final_apps)

    viz_engine = VisualizationEngine(output_dir=Path('output/visualizations/examples'))

    print("\nCreating distribution plots...")
    dist_path = viz_engine.create_distribution_plots(
        results_df,
        output_file='example_4_distributions.png',
        metrics=['Business Value', 'Tech Health', 'Security',
                'Strategic Fit', 'Composite Score'],
        title='Application Portfolio Score Distributions'
    )

    print(f"✓ Distribution plots saved to: {dist_path}")
    print("\nThis visualization helps you:")
    print("  • Understand overall portfolio health")
    print("  • Identify common score ranges")
    print("  • Spot outliers (very high or low scores)")
    print("  • See if scores are normally distributed or skewed")


def example_5_time_category_summary():
    """
    Example 5: Create TIME category summary charts.

    These pie and bar charts show the distribution of applications
    across TIME framework categories.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 5: TIME Category Summary")
    print("=" * 70)

    # Load and process data
    data_handler = DataHandler()
    df = data_handler.read_csv('data/assessment_template.csv')

    scoring_engine = ScoringEngine()
    rec_engine = RecommendationEngine()
    time_framework = TIMEFramework()

    applications = df.to_dict('records')
    scored_apps = scoring_engine.batch_calculate_scores(applications)
    final_apps = rec_engine.batch_generate_recommendations(scored_apps)
    final_apps = time_framework.batch_categorize(final_apps)

    results_df = pd.DataFrame(final_apps)

    viz_engine = VisualizationEngine(output_dir=Path('output/visualizations/examples'))

    print("\nCreating TIME category summary...")
    summary_path = viz_engine.create_time_category_summary(
        results_df,
        output_file='example_5_time_summary.png',
        title='TIME Framework Category Distribution'
    )

    print(f"✓ TIME summary saved to: {summary_path}")
    print("\nThis visualization helps you:")
    print("  • See percentage breakdown of TIME categories")
    print("  • Understand portfolio composition at a glance")
    print("  • Communicate strategy to stakeholders")
    print("  • Track changes over time (run periodically)")


def example_6_comprehensive_dashboard():
    """
    Example 6: Create comprehensive dashboard with multiple views.

    This all-in-one visualization combines several charts into a single
    dashboard suitable for executive presentations.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Comprehensive Dashboard")
    print("=" * 70)

    # Load and process data
    data_handler = DataHandler()
    df = data_handler.read_csv('data/assessment_template.csv')

    scoring_engine = ScoringEngine()
    rec_engine = RecommendationEngine()
    time_framework = TIMEFramework()

    applications = df.to_dict('records')
    scored_apps = scoring_engine.batch_calculate_scores(applications)
    final_apps = rec_engine.batch_generate_recommendations(scored_apps)
    final_apps = time_framework.batch_categorize(final_apps)

    results_df = pd.DataFrame(final_apps)

    viz_engine = VisualizationEngine(output_dir=Path('output/visualizations/examples'))

    print("\nCreating comprehensive dashboard...")
    dashboard_path = viz_engine.create_comprehensive_dashboard(
        results_df,
        output_file='example_6_dashboard.png',
        title='Application Rationalization Executive Dashboard - Q4 2025'
    )

    print(f"✓ Dashboard saved to: {dashboard_path}")
    print("\nThis dashboard includes:")
    print("  • TIME framework quadrant positioning")
    print("  • TIME category distribution (pie chart)")
    print("  • Top 5 applications by score")
    print("  • Score distribution histogram")
    print("  • Key portfolio metrics")
    print("  • Top action recommendations")
    print("\nPerfect for executive presentations and strategic planning!")


def example_7_quick_visualize():
    """
    Example 7: Use the quick_visualize helper function.

    This convenience function creates all standard visualizations
    in a single call - perfect for quick analysis.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Quick Visualize Helper Function")
    print("=" * 70)

    # First, create an assessment results file
    print("\nStep 1: Running full assessment...")
    data_handler = DataHandler()
    df = data_handler.read_csv('data/assessment_template.csv')

    scoring_engine = ScoringEngine()
    rec_engine = RecommendationEngine()
    time_framework = TIMEFramework()

    applications = df.to_dict('records')
    scored_apps = scoring_engine.batch_calculate_scores(applications)
    final_apps = rec_engine.batch_generate_recommendations(scored_apps)
    final_apps = time_framework.batch_categorize(final_apps)

    results_df = pd.DataFrame(final_apps)

    # Save results
    results_file = 'output/quick_viz_results.csv'
    data_handler.write_csv(results_df, results_file, include_timestamp=False)
    print(f"✓ Results saved to: {results_file}")

    # Now use quick_visualize
    print("\nStep 2: Creating all visualizations with quick_visualize()...")
    viz_paths = quick_visualize(
        input_file=results_file,
        output_dir='output/visualizations/quick',
        viz_types=['time_quadrant', 'time_summary', 'dashboard']  # Subset for demo
    )

    print(f"\n✓ Created {len(viz_paths)} visualizations:")
    for viz_type, path in viz_paths.items():
        print(f"  • {viz_type}: {path}")

    print("\nQuick visualize is perfect for:")
    print("  • Rapid analysis of assessment results")
    print("  • Automated reporting workflows")
    print("  • Batch processing multiple assessments")
    print("  • Integration with CI/CD pipelines")


def example_8_custom_styling():
    """
    Example 8: Customize visualization styles.

    Shows how to use different visualization styles for different
    audiences (professional, presentation, technical).
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Custom Visualization Styling")
    print("=" * 70)

    # Load and process data
    data_handler = DataHandler()
    df = data_handler.read_csv('data/assessment_template.csv')

    scoring_engine = ScoringEngine()
    rec_engine = RecommendationEngine()
    time_framework = TIMEFramework()

    applications = df.to_dict('records')
    scored_apps = scoring_engine.batch_calculate_scores(applications)
    final_apps = rec_engine.batch_generate_recommendations(scored_apps)
    final_apps = time_framework.batch_categorize(final_apps)

    results_df = pd.DataFrame(final_apps)

    # Create visualizations with different styles
    styles = ['professional', 'presentation', 'technical']

    for style in styles:
        print(f"\nCreating visualizations with '{style}' style...")
        viz_engine = VisualizationEngine(
            output_dir=Path(f'output/visualizations/styles/{style}'),
            style=style
        )

        heatmap_path = viz_engine.create_score_heatmap(
            results_df,
            output_file=f'heatmap_{style}.png',
            max_apps=15,
            title=f'Score Heatmap - {style.title()} Style'
        )

        print(f"  ✓ {style.title()} style heatmap: {heatmap_path}")

    print("\nStyle comparison:")
    print("  • Professional: Clean, business-focused, suitable for reports")
    print("  • Presentation: Bold colors, high contrast, great for slides")
    print("  • Technical: Detailed grid, precise data, for deep analysis")


def main():
    """Run all visualization examples."""
    print("\n" + "=" * 70)
    print("APPLICATION RATIONALIZATION - VISUALIZATION EXAMPLES")
    print("=" * 70)
    print("\nThis script demonstrates various visualization capabilities.")
    print("Each example creates different types of charts and dashboards.")
    print("\nRunning all examples...\n")

    try:
        # Run examples
        example_1_basic_heatmap()
        example_2_time_quadrant()
        example_3_priority_matrix()
        example_4_distribution_analysis()
        example_5_time_category_summary()
        example_6_comprehensive_dashboard()
        example_7_quick_visualize()
        example_8_custom_styling()

        # Summary
        print("\n" + "=" * 70)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nGenerated visualizations can be found in:")
        print("  • output/visualizations/examples/")
        print("  • output/visualizations/quick/")
        print("  • output/visualizations/styles/")
        print("\nNext steps:")
        print("  1. Review the generated visualizations")
        print("  2. Customize parameters for your specific needs")
        print("  3. Integrate into your reporting workflows")
        print("  4. Try the CLI: python -m src.cli visualize -i results.csv")
        print()

    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
