#!/usr/bin/env python3
"""
Survey Integration Examples
Demonstrates how to integrate stakeholder survey data with quantitative assessments.

This example shows how to:
1. Import and validate survey data
2. Aggregate multiple stakeholder responses per application
3. Merge survey data with assessment scores
4. Analyze survey impact on recommendations
5. Generate comprehensive survey analysis reports
6. Interpret variance between qualitative and quantitative scores
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


def example_1_import_survey_data():
    """
    Example 1: Import and validate stakeholder survey data.

    Demonstrates how to load survey data from CSV, validate it,
    and understand survey response patterns.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Import and Validate Survey Data")
    print("=" * 70)

    print("\nStep 1: Loading survey data from CSV...")
    data_handler = DataHandler()

    survey_df = data_handler.read_survey_data('data/sample_survey.csv')
    print(f"✓ Loaded {len(survey_df)} survey responses")

    # Validate survey data
    print("\nStep 2: Validating survey data...")
    is_valid, errors = data_handler.validate_survey_data(survey_df)

    if is_valid:
        print("✓ Survey data is valid")
    else:
        print("⚠ Survey data has warnings:")
        for error in errors:
            print(f"  - {error}")

    # Display survey statistics
    print("\nStep 3: Survey data statistics:")
    print(f"  • Total responses: {len(survey_df)}")
    print(f"  • Unique applications: {survey_df['Application Name'].nunique()}")
    print(f"  • Unique stakeholders: {survey_df['Stakeholder Name'].nunique()}")
    print(f"  • Average responses per app: {len(survey_df) / survey_df['Application Name'].nunique():.1f}")

    # Show response distribution by role
    print("\nResponse distribution by stakeholder role:")
    role_dist = survey_df['Stakeholder Role'].value_counts().head(10)
    for role, count in role_dist.items():
        print(f"  • {role}: {count}")

    # Show sample responses
    print("\nSample survey responses:")
    sample = survey_df[['Application Name', 'Stakeholder Name', 'Critical to Business',
                       'User Satisfaction', 'Qualitative Feedback']].head(3)
    print(sample.to_string(index=False))


def example_2_aggregate_responses():
    """
    Example 2: Aggregate multiple stakeholder responses.

    Shows how to combine responses from multiple stakeholders into
    single scores per application with consensus metrics.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Aggregate Survey Responses")
    print("=" * 70)

    # Load survey data
    print("\nStep 1: Loading survey data...")
    data_handler = DataHandler()
    survey_df = data_handler.read_survey_data('data/sample_survey.csv')
    print(f"✓ Loaded {len(survey_df)} responses")

    # Aggregate using mean method
    print("\nStep 2: Aggregating responses using mean method...")
    aggregated_df = data_handler.aggregate_survey_responses(survey_df, method='mean')
    print(f"✓ Aggregated {len(survey_df)} responses into {len(aggregated_df)} applications")

    # Display aggregation results
    print("\nAggregation results (top 5 by response count):")
    top_apps = aggregated_df.nlargest(5, 'Survey Response Count')[[
        'Application Name',
        'Survey Response Count',
        'Critical to Business',
        'User Satisfaction',
        'Overall Consensus Score'
    ]]
    print(top_apps.to_string(index=False))

    # Show consensus analysis
    print("\nConsensus analysis:")
    avg_consensus = aggregated_df['Overall Consensus Score'].mean()
    high_consensus = len(aggregated_df[aggregated_df['Overall Consensus Score'] >= 4])
    low_consensus = len(aggregated_df[aggregated_df['Overall Consensus Score'] < 3])

    print(f"  • Average consensus score: {avg_consensus:.2f}/5")
    print(f"  • Apps with high consensus (≥4): {high_consensus}")
    print(f"  • Apps with low consensus (<3): {low_consensus}")

    # Identify apps with divergent stakeholder opinions
    print("\nApplications with divergent stakeholder opinions (low consensus):")
    divergent = aggregated_df.nsmallest(3, 'Overall Consensus Score')[[
        'Application Name',
        'Survey Response Count',
        'Overall Consensus Score'
    ]]
    print(divergent.to_string(index=False))

    print("\nNote: Low consensus may indicate:")
    print("  • Different stakeholder perspectives (users vs. IT)")
    print("  • Varying experiences across departments")
    print("  • Need for further investigation")


def example_3_merge_survey_with_assessment():
    """
    Example 3: Merge survey data with quantitative assessment.

    Demonstrates how to combine stakeholder feedback with technical
    assessments to create survey-adjusted scores.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Merge Survey with Assessment Data")
    print("=" * 70)

    # Step 1: Run quantitative assessment
    print("\nStep 1: Running quantitative assessment...")
    data_handler = DataHandler()
    assessment_df = data_handler.read_csv('data/assessment_template.csv')

    scoring_engine = ScoringEngine()
    rec_engine = RecommendationEngine()
    time_framework = TIMEFramework()

    applications = assessment_df.to_dict('records')
    scored_apps = scoring_engine.batch_calculate_scores(applications)
    final_apps = rec_engine.batch_generate_recommendations(scored_apps)
    final_apps = time_framework.batch_categorize(final_apps)

    assessment_results = pd.DataFrame(final_apps)
    print(f"✓ Completed assessment of {len(assessment_results)} applications")

    # Step 2: Load and aggregate survey data
    print("\nStep 2: Loading and aggregating survey data...")
    survey_df = data_handler.read_survey_data('data/sample_survey.csv')
    aggregated_survey = data_handler.aggregate_survey_responses(survey_df)
    print(f"✓ Aggregated {len(survey_df)} responses")

    # Step 3: Merge data with 30% survey weight
    print("\nStep 3: Merging assessment and survey data (30% survey weight)...")
    merged_df = data_handler.merge_survey_with_assessment(
        assessment_results,
        aggregated_survey,
        survey_weight=0.3
    )
    print(f"✓ Merged {len(merged_df)} applications")
    print(f"  • {merged_df['Has Survey Data'].sum()} apps have survey data")

    # Step 4: Show survey-adjusted scores
    print("\nSample applications with survey-adjusted scores:")
    sample_cols = [
        'Application Name',
        'Business Value Original',
        'Business Value Survey Adjusted',
        'Business Value Variance',
        'User Satisfaction'
    ]
    sample = merged_df[merged_df['Has Survey Data'] == True][sample_cols].head(5)
    print(sample.to_string(index=False))

    print("\nInterpretation:")
    print("  • Original = Quantitative technical score")
    print("  • Survey Adjusted = Blended score (70% quantitative + 30% survey)")
    print("  • Variance = Difference (positive means survey rated higher)")


def example_4_analyze_survey_impact():
    """
    Example 4: Analyze survey impact on assessment scores.

    Shows how to identify applications where stakeholder feedback
    significantly differs from quantitative metrics.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Analyze Survey Impact")
    print("=" * 70)

    # Prepare merged data
    print("\nPreparing assessment and survey data...")
    data_handler = DataHandler()

    # Run assessment
    assessment_df = data_handler.read_csv('data/assessment_template.csv')
    scoring_engine = ScoringEngine()
    rec_engine = RecommendationEngine()
    time_framework = TIMEFramework()

    applications = assessment_df.to_dict('records')
    scored_apps = scoring_engine.batch_calculate_scores(applications)
    final_apps = rec_engine.batch_generate_recommendations(scored_apps)
    final_apps = time_framework.batch_categorize(final_apps)
    assessment_results = pd.DataFrame(final_apps)

    # Load survey
    survey_df = data_handler.read_survey_data('data/sample_survey.csv')
    aggregated_survey = data_handler.aggregate_survey_responses(survey_df)

    # Merge
    merged_df = data_handler.merge_survey_with_assessment(
        assessment_results,
        aggregated_survey,
        survey_weight=0.3
    )

    # Calculate survey impact
    print("\nCalculating survey impact...")
    impact = data_handler.calculate_survey_impact(merged_df)

    # Display variance summary
    if 'variance_summary' in impact:
        print("\n" + "=" * 70)
        print("VARIANCE SUMMARY (Qualitative vs. Quantitative)")
        print("=" * 70)

        for metric, stats in impact['variance_summary'].items():
            print(f"\n{metric}:")
            print(f"  • Mean variance: {stats['mean']:.2f}")
            print(f"  • Max positive (survey higher): {stats['max_positive']:.2f}")
            print(f"  • Max negative (quant higher): {stats['max_negative']:.2f}")

    # Display consensus summary
    if 'consensus_summary' in impact:
        print("\n" + "=" * 70)
        print("CONSENSUS SUMMARY")
        print("=" * 70)
        cons = impact['consensus_summary']
        print(f"  • Average consensus: {cons['average_consensus']:.2f}/5")
        print(f"  • High consensus apps: {cons['high_consensus_count']}")
        print(f"  • Low consensus apps: {cons['low_consensus_count']}")

    # Display sentiment analysis
    if 'sentiment_analysis' in impact:
        print("\n" + "=" * 70)
        print("STAKEHOLDER SENTIMENT ANALYSIS")
        print("=" * 70)
        for category, count in impact['sentiment_analysis'].items():
            print(f"  • {category}: {count}")

    # Display high variance applications
    if 'high_variance_apps' in impact and len(impact['high_variance_apps']) > 0:
        print("\n" + "=" * 70)
        print("HIGH VARIANCE APPLICATIONS")
        print("=" * 70)
        print(f"Found {len(impact['high_variance_apps'])} apps with significant differences:")
        for app in impact['high_variance_apps'][:5]:
            print(f"\n  • {app['Application Name']}")
            print(f"    Responses: {app['Survey Response Count']}")
            for key, value in app.items():
                if 'Variance' in key and 'Flag' not in key:
                    print(f"    {key}: {value:.2f}")

    # Display apps needing attention
    if 'needs_attention' in impact and len(impact['needs_attention']) > 0:
        print("\n" + "=" * 70)
        print("APPLICATIONS NEEDING ATTENTION")
        print("=" * 70)
        print(f"Critical apps with low user satisfaction: {len(impact['needs_attention'])}")
        for app in impact['needs_attention'][:3]:
            print(f"\n  • {app['Application Name']}")
            print(f"    Critical to Business: {app['Critical to Business']:.1f}/5")
            print(f"    User Satisfaction: {app['User Satisfaction']:.1f}/5")
            if 'Qualitative Feedback' in app and pd.notna(app['Qualitative Feedback']):
                feedback_preview = str(app['Qualitative Feedback'])[:100]
                print(f"    Feedback: {feedback_preview}...")


def example_5_export_survey_analysis():
    """
    Example 5: Generate comprehensive survey analysis report.

    Creates a multi-sheet Excel report with survey analysis,
    variance metrics, and qualitative feedback.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Generate Survey Analysis Report")
    print("=" * 70)

    # Prepare merged data
    print("\nStep 1: Preparing assessment and survey data...")
    data_handler = DataHandler()

    # Run assessment
    assessment_df = data_handler.read_csv('data/assessment_template.csv')
    scoring_engine = ScoringEngine()
    rec_engine = RecommendationEngine()
    time_framework = TIMEFramework()

    applications = assessment_df.to_dict('records')
    scored_apps = scoring_engine.batch_calculate_scores(applications)
    final_apps = rec_engine.batch_generate_recommendations(scored_apps)
    final_apps = time_framework.batch_categorize(final_apps)
    assessment_results = pd.DataFrame(final_apps)

    # Load survey
    survey_df = data_handler.read_survey_data('data/sample_survey.csv')
    aggregated_survey = data_handler.aggregate_survey_responses(survey_df)

    # Merge
    merged_df = data_handler.merge_survey_with_assessment(
        assessment_results,
        aggregated_survey,
        survey_weight=0.3
    )
    print(f"✓ Prepared {len(merged_df)} applications")

    # Generate survey analysis report
    print("\nStep 2: Generating comprehensive survey analysis Excel report...")
    output_path = data_handler.export_survey_analysis(
        merged_df,
        'output/examples/survey_analysis_report.xlsx',
        include_timestamp=True
    )

    print(f"\n✓ Survey analysis report created: {output_path}")
    print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")

    print("\nReport includes:")
    print("  1. Survey Analysis - Merged scores with survey adjustments")
    print("  2. High Variance - Apps where stakeholders disagree with metrics")
    print("  3. Impact Summary - Statistical analysis of survey impact")
    print("  4. Needs Attention - Critical apps with low satisfaction")
    print("  5. Qualitative Feedback - All stakeholder comments by app")

    print("\nHow to use this report:")
    print("  • Review High Variance sheet to find discrepancies")
    print("  • Check Needs Attention for priority interventions")
    print("  • Read Qualitative Feedback for stakeholder perspectives")
    print("  • Use Impact Summary to understand overall patterns")


def example_6_complete_workflow():
    """
    Example 6: Complete end-to-end survey integration workflow.

    Demonstrates the full workflow from raw data to final reports,
    showing how survey integration affects recommendations.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Complete Survey Integration Workflow")
    print("=" * 70)

    print("\nThis example demonstrates a complete workflow:")
    print("  1. Run quantitative assessment")
    print("  2. Import and aggregate survey data")
    print("  3. Merge survey with assessment")
    print("  4. Compare recommendations before/after survey")
    print("  5. Export comprehensive analysis")

    data_handler = DataHandler()

    # Step 1: Quantitative assessment
    print("\n" + "-" * 70)
    print("Step 1: Running quantitative assessment...")
    assessment_df = data_handler.read_csv('data/assessment_template.csv')

    scoring_engine = ScoringEngine()
    rec_engine = RecommendationEngine()
    time_framework = TIMEFramework()

    applications = assessment_df.to_dict('records')
    scored_apps = scoring_engine.batch_calculate_scores(applications)
    final_apps = rec_engine.batch_generate_recommendations(scored_apps)
    final_apps = time_framework.batch_categorize(final_apps)

    assessment_results = pd.DataFrame(final_apps)
    print(f"✓ Assessed {len(assessment_results)} applications")

    # Save quantitative-only results
    quant_only_path = Path('output/examples/assessment_quantitative_only.csv')
    quant_only_path.parent.mkdir(parents=True, exist_ok=True)
    assessment_results.to_csv(quant_only_path, index=False)
    print(f"  Saved quantitative results to: {quant_only_path}")

    # Step 2: Import survey data
    print("\nStep 2: Importing and aggregating survey data...")
    survey_df = data_handler.read_survey_data('data/sample_survey.csv')
    aggregated_survey = data_handler.aggregate_survey_responses(survey_df, method='mean')
    print(f"✓ Aggregated {len(survey_df)} responses from {survey_df['Stakeholder Name'].nunique()} stakeholders")

    # Save aggregated survey
    survey_path = Path('output/examples/survey_aggregated.csv')
    aggregated_survey.to_csv(survey_path, index=False)
    print(f"  Saved aggregated survey to: {survey_path}")

    # Step 3: Merge data
    print("\nStep 3: Merging survey with assessment...")
    merged_df = data_handler.merge_survey_with_assessment(
        assessment_results,
        aggregated_survey,
        survey_weight=0.3
    )
    print(f"✓ Merged data for {len(merged_df)} applications")
    print(f"  • {merged_df['Has Survey Data'].sum()} apps have survey feedback")

    # Save merged results
    merged_path = Path('output/examples/assessment_with_survey.csv')
    merged_df.to_csv(merged_path, index=False)
    print(f"  Saved merged results to: {merged_path}")

    # Step 4: Compare before/after
    print("\nStep 4: Analyzing survey impact on recommendations...")
    impact = data_handler.calculate_survey_impact(merged_df)

    print("\n" + "=" * 70)
    print("IMPACT ANALYSIS")
    print("=" * 70)

    if 'variance_summary' in impact:
        print("\nScore Variance:")
        for metric, stats in impact['variance_summary'].items():
            if 'Business Value' in metric:
                print(f"  • {metric}: Mean = {stats['mean']:.2f}, Std = {stats['std']:.2f}")

    if 'sentiment_analysis' in impact:
        print("\nStakeholder Sentiment:")
        for category, count in impact['sentiment_analysis'].items():
            pct = (count / merged_df['Has Survey Data'].sum()) * 100
            print(f"  • {category}: {count} ({pct:.1f}%)")

    if 'needs_attention' in impact:
        print(f"\nApplications Needing Attention: {len(impact['needs_attention'])}")
        if len(impact['needs_attention']) > 0:
            print("  Top 3 priority applications:")
            for i, app in enumerate(impact['needs_attention'][:3], 1):
                print(f"    {i}. {app['Application Name']}")

    # Step 5: Export comprehensive reports
    print("\nStep 5: Exporting comprehensive analysis...")

    # Survey analysis report
    survey_report_path = data_handler.export_survey_analysis(
        merged_df,
        'output/examples/complete_survey_analysis.xlsx',
        include_timestamp=True
    )
    print(f"✓ Survey analysis report: {survey_report_path.name}")

    print("\n" + "=" * 70)
    print("WORKFLOW COMPLETE!")
    print("=" * 70)
    print("\nGenerated files in output/examples/:")
    print("  • assessment_quantitative_only.csv - Baseline assessment")
    print("  • survey_aggregated.csv - Aggregated stakeholder feedback")
    print("  • assessment_with_survey.csv - Merged assessment + survey")
    print("  • complete_survey_analysis.xlsx - Detailed Excel analysis")

    print("\nKey insights from survey integration:")
    if 'high_variance_apps' in impact:
        print(f"  • {len(impact['high_variance_apps'])} apps show significant variance")
    if 'needs_attention' in impact:
        print(f"  • {len(impact['needs_attention'])} critical apps need attention")
    if 'consensus_summary' in impact:
        avg_cons = impact['consensus_summary']['average_consensus']
        print(f"  • Average stakeholder consensus: {avg_cons:.2f}/5")

    print("\nNext steps:")
    print("  1. Review high variance applications for potential score adjustments")
    print("  2. Investigate 'needs attention' apps as priority interventions")
    print("  3. Use qualitative feedback to inform action plans")
    print("  4. Re-run assessments with updated data as needed")


def main():
    """Run all survey integration examples."""
    print("\n" + "=" * 70)
    print("SURVEY INTEGRATION EXAMPLES")
    print("=" * 70)
    print("\nThese examples demonstrate stakeholder survey integration.")
    print("Survey data adds qualitative feedback to quantitative assessments.\n")

    try:
        # Create output directory
        Path('output/examples').mkdir(parents=True, exist_ok=True)

        # Run examples
        example_1_import_survey_data()
        example_2_aggregate_responses()
        example_3_merge_survey_with_assessment()
        example_4_analyze_survey_impact()
        example_5_export_survey_analysis()
        example_6_complete_workflow()

        # Summary
        print("\n" + "=" * 70)
        print("ALL SURVEY INTEGRATION EXAMPLES COMPLETED!")
        print("=" * 70)
        print("\nKey capabilities demonstrated:")
        print("  ✓ Survey data import and validation")
        print("  ✓ Multi-stakeholder response aggregation")
        print("  ✓ Survey-assessment data merging")
        print("  ✓ Variance and consensus analysis")
        print("  ✓ Impact assessment on recommendations")
        print("  ✓ Comprehensive Excel reporting")

        print("\nGenerated files can be found in:")
        print("  • output/examples/")

        print("\nCLI Usage:")
        print("  # Import survey data")
        print("  python -m src.cli import-survey -i data/sample_survey.csv -o survey.csv")
        print()
        print("  # Merge with assessment")
        print("  python -m src.cli merge-survey-data -a results.csv -s survey.csv -w 0.3")
        print()
        print("  # Generate report")
        print("  python -m src.cli generate-survey-report -i merged.csv -o report.xlsx")
        print()

    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
