#!/usr/bin/env python3
"""
Export Examples
Demonstrates how to export application rationalization data in specialized formats.

This example shows how to:
1. Create Power BI-optimized Excel exports
2. Create enhanced Excel reports with formatting and charts
3. Customize export parameters
4. Use exports for different audiences
"""

from pathlib import Path
import sys

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_handler import DataHandler
from src.scoring_engine import ScoringEngine
from src.recommendation_engine import RecommendationEngine
from src.time_framework import TIMEFramework
import pandas as pd


def example_1_powerbi_export():
    """
    Example 1: Create Power BI-optimized Excel export.

    This export creates a multi-sheet workbook designed for easy
    import into Power BI with proper table relationships.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Power BI-Optimized Export")
    print("=" * 70)

    # Load and process data
    print("\nStep 1: Processing assessment data...")
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
    print(f"✓ Processed {len(results_df)} applications")

    # Create Power BI export
    print("\nStep 2: Creating Power BI-optimized Excel export...")
    output_path = data_handler.export_for_powerbi(
        results_df,
        'output/exports/powerbi_export.xlsx',
        include_timestamp=True
    )

    print(f"\n✓ Power BI export created: {output_path}")
    print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")

    print("\nExport includes these sheets:")
    print("  1. Applications - Main fact table with all application data")
    print("  2. Dimension_Scores - Normalized scores for Power BI relationships")
    print("  3. TIME_Framework - TIME categorization data")
    print("  4. Recommendations - Action recommendations")
    print("  5. Summary_Stats - Portfolio summary statistics")
    print("  6. TIME_Distribution - TIME category breakdown")
    print("  7. Metadata - Export information")

    print("\nHow to use in Power BI:")
    print("  1. Open Power BI Desktop")
    print("  2. Get Data → Excel → Select this file")
    print("  3. Load 'Applications' as the main table")
    print("  4. Create relationships using 'Application_ID'")
    print("  5. Use 'Dimension_Scores' for detailed dimension analysis")
    print("  6. Build visualizations using the imported tables")


def example_2_enhanced_excel_export():
    """
    Example 2: Create enhanced Excel export with formatting and charts.

    This export creates a professional, presentation-ready workbook
    with conditional formatting, charts, and a summary dashboard.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Enhanced Excel Export")
    print("=" * 70)

    # Load and process data
    print("\nStep 1: Processing assessment data...")
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
    print(f"✓ Processed {len(results_df)} applications")

    # Create enhanced Excel export
    print("\nStep 2: Creating enhanced Excel export with formatting...")
    output_path = data_handler.export_enhanced_excel(
        results_df,
        'output/exports/enhanced_report.xlsx',
        include_timestamp=True,
        include_charts=True
    )

    print(f"\n✓ Enhanced Excel export created: {output_path}")
    print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")

    print("\nExport includes these worksheets:")
    print("  1. Summary_Dashboard - Executive summary with key metrics")
    print("  2. Detailed_Scores - Full application scores with conditional formatting")
    print("  3. TIME_Framework - TIME categories with color coding and pie chart")
    print("  4. Recommendations - Sorted action recommendations with bar chart")
    print("  5. Cost_Analysis - Cost breakdown with currency formatting")

    print("\nFormatting features:")
    print("  • Color-coded scores (red-yellow-green scale)")
    print("  • Conditional formatting on all score columns")
    print("  • TIME categories with color backgrounds")
    print("  • Embedded charts for visual analysis")
    print("  • Freeze panes and auto-filters on all tables")
    print("  • Professional header styling")
    print("  • Auto-adjusted column widths")

    print("\nBest for:")
    print("  • Executive presentations")
    print("  • Board reports")
    print("  • Stakeholder communications")
    print("  • Printing and PDF export")


def example_3_custom_export_without_charts():
    """
    Example 3: Create enhanced Excel export without charts.

    Sometimes you want the formatting but not the charts
    (e.g., for smaller file sizes or faster loading).
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Enhanced Excel Export (No Charts)")
    print("=" * 70)

    # Load and process data
    print("\nProcessing assessment data...")
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

    # Create export without charts
    print("\nCreating enhanced Excel export without embedded charts...")
    output_path = data_handler.export_enhanced_excel(
        results_df,
        'output/exports/enhanced_no_charts.xlsx',
        include_timestamp=True,
        include_charts=False  # Disable charts
    )

    print(f"\n✓ Export created: {output_path}")
    print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")

    print("\nBenefits of excluding charts:")
    print("  • Smaller file size")
    print("  • Faster loading in Excel")
    print("  • Easier to programmatically process")
    print("  • Still includes all formatting and conditional coloring")


def example_4_both_formats():
    """
    Example 4: Create both Power BI and Enhanced Excel exports.

    Shows how to generate both export types from the same assessment
    for different use cases.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Create Both Export Formats")
    print("=" * 70)

    # Load and process data
    print("\nStep 1: Running complete assessment...")
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
    print(f"✓ Assessed {len(results_df)} applications")

    # Create both exports
    print("\nStep 2: Creating Power BI export...")
    powerbi_path = data_handler.export_for_powerbi(
        results_df,
        'output/exports/dual_powerbi.xlsx',
        include_timestamp=False
    )
    print(f"✓ Power BI export: {powerbi_path}")

    print("\nStep 3: Creating Enhanced Excel export...")
    excel_path = data_handler.export_enhanced_excel(
        results_df,
        'output/exports/dual_enhanced.xlsx',
        include_timestamp=False,
        include_charts=True
    )
    print(f"✓ Enhanced Excel: {excel_path}")

    print("\n" + "=" * 50)
    print("Export Summary")
    print("=" * 50)
    print(f"\nPower BI Export ({powerbi_path.stat().st_size / 1024:.1f} KB):")
    print("  Use for: Interactive dashboards, drill-down analysis")
    print("  Audience: Data analysts, BI developers")
    print("  Features: Normalized tables, relationships, metadata")

    print(f"\nEnhanced Excel ({excel_path.stat().st_size / 1024:.1f} KB):")
    print("  Use for: Executive presentations, board reports")
    print("  Audience: Executives, stakeholders, decision-makers")
    print("  Features: Formatting, charts, summary dashboard")


def example_5_integration_workflow():
    """
    Example 5: Complete workflow from assessment to exports.

    Demonstrates a full end-to-end workflow that could be automated
    or run as part of a regular reporting cycle.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Complete Integration Workflow")
    print("=" * 70)

    print("\nThis example demonstrates a complete workflow:")
    print("  1. Load application data")
    print("  2. Run assessment (scoring, recommendations, TIME framework)")
    print("  3. Save intermediate CSV results")
    print("  4. Create Power BI export for analysts")
    print("  5. Create Enhanced Excel for executives")
    print("  6. Generate summary statistics")

    # Step 1: Load data
    print("\n" + "-" * 70)
    print("Step 1: Loading application data...")
    data_handler = DataHandler()
    df = data_handler.read_csv('data/assessment_template.csv')
    print(f"✓ Loaded {len(df)} applications from assessment template")

    # Step 2: Run assessment
    print("\nStep 2: Running complete assessment...")
    scoring_engine = ScoringEngine()
    rec_engine = RecommendationEngine()
    time_framework = TIMEFramework()

    applications = df.to_dict('records')

    print("  • Calculating composite scores...")
    scored_apps = scoring_engine.batch_calculate_scores(applications)

    print("  • Generating recommendations...")
    final_apps = rec_engine.batch_generate_recommendations(scored_apps)

    print("  • Applying TIME framework...")
    final_apps = time_framework.batch_categorize(final_apps)

    results_df = pd.DataFrame(final_apps)
    print(f"✓ Assessment complete for {len(results_df)} applications")

    # Step 3: Save CSV
    print("\nStep 3: Saving CSV results...")
    csv_path = data_handler.write_csv(
        results_df,
        'output/exports/workflow_results.csv',
        include_timestamp=True
    )
    print(f"✓ CSV saved: {csv_path}")

    # Step 4: Create Power BI export
    print("\nStep 4: Creating Power BI export for analysts...")
    powerbi_path = data_handler.export_for_powerbi(
        results_df,
        'output/exports/workflow_powerbi.xlsx',
        include_timestamp=True
    )
    print(f"✓ Power BI export created: {powerbi_path}")

    # Step 5: Create Enhanced Excel
    print("\nStep 5: Creating Enhanced Excel for executives...")
    excel_path = data_handler.export_enhanced_excel(
        results_df,
        'output/exports/workflow_executive_report.xlsx',
        include_timestamp=True,
        include_charts=True
    )
    print(f"✓ Executive report created: {excel_path}")

    # Step 6: Generate statistics
    print("\nStep 6: Generating summary statistics...")
    stats = data_handler.get_summary_statistics(results_df)

    print("\n" + "=" * 70)
    print("PORTFOLIO SUMMARY")
    print("=" * 70)
    print(f"Total Applications: {stats['total_applications']}")
    print(f"Total Annual Cost: ${stats['total_cost']:,.0f}")
    print(f"Average Business Value: {stats['average_business_value']:.2f}/10")
    print(f"Average Tech Health: {stats['average_tech_health']:.2f}/10")
    print(f"Average Security: {stats['average_security']:.2f}/10")
    print(f"Redundant Applications: {int(stats['redundant_applications'])}")

    if 'average_composite_score' in stats:
        print(f"Average Composite Score: {stats['average_composite_score']:.2f}/100")

    # TIME Framework summary
    time_summary = time_framework.get_category_summary()
    print("\nTIME Framework Distribution:")
    for category, count in time_summary['distribution'].items():
        percentage = time_summary['percentages'].get(category, 0)
        print(f"  • {category}: {count} ({percentage:.1f}%)")

    print("\n" + "=" * 70)
    print("WORKFLOW COMPLETE!")
    print("=" * 70)
    print("\nGenerated files:")
    print(f"  • CSV Results: {csv_path.name}")
    print(f"  • Power BI: {powerbi_path.name}")
    print(f"  • Executive Report: {excel_path.name}")
    print("\nThese files can be:")
    print("  • Distributed to stakeholders")
    print("  • Imported into Power BI dashboards")
    print("  • Used for presentations")
    print("  • Archived for historical tracking")


def main():
    """Run all export examples."""
    print("\n" + "=" * 70)
    print("APPLICATION RATIONALIZATION - EXPORT EXAMPLES")
    print("=" * 70)
    print("\nThis script demonstrates various export capabilities.")
    print("Each example creates different types of formatted exports.")
    print("\nRunning all examples...\n")

    try:
        # Create output directory
        Path('output/exports').mkdir(parents=True, exist_ok=True)

        # Run examples
        example_1_powerbi_export()
        example_2_enhanced_excel_export()
        example_3_custom_export_without_charts()
        example_4_both_formats()
        example_5_integration_workflow()

        # Summary
        print("\n" + "=" * 70)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nGenerated exports can be found in:")
        print("  • output/exports/")
        print("\nNext steps:")
        print("  1. Open the Excel files to see formatting and charts")
        print("  2. Import Power BI exports into Power BI Desktop")
        print("  3. Customize export parameters for your needs")
        print("  4. Try the CLI: python -m src.cli export -i results.csv -f powerbi")
        print()

    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
