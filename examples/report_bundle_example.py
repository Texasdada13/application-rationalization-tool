#!/usr/bin/env python3
"""
Complete Report Bundle Generation Example
Demonstrates how to generate comprehensive report packages with all export formats.

This example shows how to:
1. Generate complete report bundles programmatically
2. Create Tableau-optimized exports
3. Generate automated reports for multiple audiences
4. Create time-series report packages
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


def example_1_basic_report_bundle():
    """
    Example 1: Generate a basic complete report bundle.

    Creates all export formats (CSV, Power BI, Excel, Tableau) in one command.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Complete Report Bundle")
    print("=" * 70)

    # Load and process data
    print("\nStep 1: Running assessment...")
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

    # Generate complete report bundle
    print("\nStep 2: Generating complete report bundle...")
    bundle_files = data_handler.generate_complete_report_bundle(
        results_df,
        output_dir='output/reports/example1_basic',
        report_name='Q1_2025_Assessment',
        include_visualizations=True
    )

    print(f"\n✓ Report bundle created with {len(bundle_files)} files:")
    for file_type, file_path in bundle_files.items():
        file_size = file_path.stat().st_size / 1024
        print(f"  • {file_type}: {file_path.name} ({file_size:.1f} KB)")

    print("\nWhat was generated:")
    print("  • CSV data export - for general analysis")
    print("  • Power BI Excel - for interactive dashboards")
    print("  • Enhanced Excel - for executive presentations")
    print("  • Tableau CSV - for Tableau visualizations")
    print("  • Visualizations - PNG charts and dashboards")
    print("  • README.md - usage instructions")
    print("  • Summary statistics - text file with key metrics")


def example_2_tableau_export():
    """
    Example 2: Create Tableau-specific export.

    Demonstrates Tableau-optimized CSV with calculated fields.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Tableau-Optimized Export")
    print("=" * 70)

    # Load assessment data
    print("\nLoading assessment data...")
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

    # Create Tableau export
    print("\nCreating Tableau-optimized export...")
    tableau_path = data_handler.export_for_tableau(
        results_df,
        'output/reports/example2_tableau/assessment_data.csv',
        include_timestamp=False
    )

    print(f"\n✓ Tableau export created: {tableau_path}")
    print(f"  File size: {tableau_path.stat().st_size / 1024:.1f} KB")

    # Show what was added
    tableau_df = pd.read_csv(tableau_path)
    print(f"  Rows: {len(tableau_df)}")
    print(f"  Columns: {len(tableau_df.columns)}")

    print("\nCalculated fields added for Tableau:")
    calc_fields = [col for col in tableau_df.columns if col not in results_df.columns]
    for field in calc_fields:
        print(f"  • {field}")

    print("\nRecommended Tableau visualizations:")
    print("  1. Scatter Plot: Business_Value (X) vs Tech_Health (Y)")
    print("     - Color by TIME_Category")
    print("     - Size by Cost")
    print("  2. Bar Chart: Application_Name vs Composite_Score")
    print("     - Color by Score_Category")
    print("  3. Treemap: Applications sized by Cost")
    print("     - Color by Performance_Tier")
    print("  4. Heatmap: Application_Name vs Score dimensions")


def example_3_multi_audience_reports():
    """
    Example 3: Generate reports for different audiences.

    Creates separate report packages for executives, analysts, and technical teams.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Multi-Audience Report Generation")
    print("=" * 70)

    # Load and process data
    print("\nPreparing assessment data...")
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

    # 1. Executive Package (Excel only, with visualizations)
    print("\n1. Creating Executive Package...")
    exec_path = data_handler.export_enhanced_excel(
        results_df,
        'output/reports/example3_audiences/executive/Executive_Summary.xlsx',
        include_timestamp=False,
        include_charts=True
    )
    print(f"   ✓ Executive report: {exec_path.name}")

    # Also create visualizations for executives
    from src.visualizations import VisualizationEngine

    viz_engine = VisualizationEngine(
        output_dir=Path('output/reports/example3_audiences/executive/charts'),
        style='presentation'  # Bold style for presentations
    )

    dashboard_path = viz_engine.create_comprehensive_dashboard(
        results_df,
        output_file='executive_dashboard.png',
        title='Portfolio Assessment - Executive Dashboard'
    )
    print(f"   ✓ Dashboard: {dashboard_path.name}")

    # 2. Analyst Package (Power BI)
    print("\n2. Creating Analyst Package...")
    powerbi_path = data_handler.export_for_powerbi(
        results_df,
        'output/reports/example3_audiences/analysts/PowerBI_Data.xlsx',
        include_timestamp=False
    )
    print(f"   ✓ Power BI export: {powerbi_path.name}")

    # 3. Technical Team Package (CSV and Tableau)
    print("\n3. Creating Technical Team Package...")
    csv_path = data_handler.write_csv(
        results_df,
        'output/reports/example3_audiences/technical/detailed_data.csv',
        include_timestamp=False
    )

    tableau_path = data_handler.export_for_tableau(
        results_df,
        'output/reports/example3_audiences/technical/tableau_data.csv',
        include_timestamp=False
    )
    print(f"   ✓ CSV export: {csv_path.name}")
    print(f"   ✓ Tableau export: {tableau_path.name}")

    print("\nAudience-specific packages created:")
    print("  • Executives: Enhanced Excel + Presentation-style dashboard")
    print("  • Analysts: Power BI workbook for drill-down analysis")
    print("  • Technical: CSV + Tableau for detailed data exploration")


def example_4_automated_monthly_report():
    """
    Example 4: Automated monthly report generation.

    Demonstrates how to create timestamped monthly reports automatically.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Automated Monthly Report")
    print("=" * 70)

    from datetime import datetime

    # Get current month
    month_str = datetime.now().strftime('%Y-%m')
    month_name = datetime.now().strftime('%B_%Y')

    print(f"\nGenerating report for: {month_name}")

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

    # Generate monthly report bundle
    print(f"\nCreating monthly report bundle...")
    bundle_files = data_handler.generate_complete_report_bundle(
        results_df,
        output_dir=f'output/reports/monthly/{month_str}',
        report_name=f'Assessment_{month_name}',
        include_visualizations=True
    )

    print(f"\n✓ Monthly report for {month_name} created!")
    print(f"  Location: output/reports/monthly/{month_str}/")
    print(f"  Files: {len(bundle_files)}")

    print("\nAutomation tip:")
    print("  Schedule this script to run monthly via cron:")
    print("  0 0 1 * * cd /path/to/tool && python examples/report_bundle_example.py")


def example_5_complete_workflow():
    """
    Example 5: Complete workflow from assessment to report distribution.

    End-to-end example including all steps.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Complete Assessment-to-Report Workflow")
    print("=" * 70)

    # Step 1: Data Collection
    print("\n" + "-" * 70)
    print("STEP 1: Data Collection")
    print("-" * 70)
    data_handler = DataHandler()
    df = data_handler.read_csv('data/assessment_template.csv')
    print(f"✓ Loaded {len(df)} applications from assessment template")

    # Step 2: Run Assessment
    print("\n" + "-" * 70)
    print("STEP 2: Run Assessment")
    print("-" * 70)

    scoring_engine = ScoringEngine()
    rec_engine = RecommendationEngine()
    time_framework = TIMEFramework()

    print("  • Calculating scores...")
    applications = df.to_dict('records')
    scored_apps = scoring_engine.batch_calculate_scores(applications)

    print("  • Generating recommendations...")
    final_apps = rec_engine.batch_generate_recommendations(scored_apps)

    print("  • Applying TIME framework...")
    final_apps = time_framework.batch_categorize(final_apps)

    results_df = pd.DataFrame(final_apps)
    print(f"✓ Assessment complete for {len(results_df)} applications")

    # Step 3: Generate Reports
    print("\n" + "-" * 70)
    print("STEP 3: Generate Report Bundle")
    print("-" * 70)

    bundle_files = data_handler.generate_complete_report_bundle(
        results_df,
        output_dir='output/reports/example5_complete',
        report_name='Complete_Assessment',
        include_visualizations=True
    )
    print(f"✓ Generated {len(bundle_files)} files")

    # Step 4: Display Summary
    print("\n" + "-" * 70)
    print("STEP 4: Portfolio Summary")
    print("-" * 70)

    stats = data_handler.get_summary_statistics(results_df)
    print(f"\nPortfolio Metrics:")
    print(f"  • Total Applications: {stats['total_applications']}")
    print(f"  • Total Annual Cost: ${stats['total_cost']:,.0f}")
    print(f"  • Average Business Value: {stats['average_business_value']:.2f}/10")
    print(f"  • Average Tech Health: {stats['average_tech_health']:.2f}/10")
    print(f"  • Average Security: {stats['average_security']:.2f}/10")
    print(f"  • Average Composite Score: {stats.get('average_composite_score', 0):.2f}/100")

    # Step 5: Distribution Plan
    print("\n" + "-" * 70)
    print("STEP 5: Distribution Plan")
    print("-" * 70)

    print("\nRecommended distribution:")
    print("  • Board Meeting: Executive Excel + Dashboard PNG")
    print("  • BI Team: Power BI workbook")
    print("  • Analysts: Tableau CSV")
    print("  • Stakeholders: README.md + Summary stats")
    print("  • Archive: Complete bundle + CSV")

    print("\n" + "=" * 70)
    print("WORKFLOW COMPLETE!")
    print("=" * 70)
    print(f"\nAll reports available in: output/reports/example5_complete/")


def main():
    """Run all report bundle examples."""
    print("\n" + "=" * 70)
    print("COMPLETE REPORT BUNDLE EXAMPLES")
    print("=" * 70)
    print("\nThese examples demonstrate automated report generation")
    print("for different audiences and use cases.")
    print("\nRunning all examples...\n")

    try:
        example_1_basic_report_bundle()
        example_2_tableau_export()
        example_3_multi_audience_reports()
        example_4_automated_monthly_report()
        example_5_complete_workflow()

        # Summary
        print("\n" + "=" * 70)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nGenerated reports can be found in:")
        print("  • output/reports/example1_basic/")
        print("  • output/reports/example2_tableau/")
        print("  • output/reports/example3_audiences/")
        print("  • output/reports/monthly/")
        print("  • output/reports/example5_complete/")
        print("\nNext steps:")
        print("  1. Review the generated README.md files in each directory")
        print("  2. Open Excel reports for executive insights")
        print("  3. Import Power BI/Tableau files into respective tools")
        print("  4. Try the CLI: python -m src.cli generate-report -i results.csv")
        print()

    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
