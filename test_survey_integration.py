#!/usr/bin/env python3
"""
Survey Integration Test Script
Tests all survey integration features end-to-end.
"""

import sys
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data_handler import DataHandler
from src.scoring_engine import ScoringEngine
from src.recommendation_engine import RecommendationEngine
from src.time_framework import TIMEFramework


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def print_success(message):
    """Print a success message."""
    print(f"✓ {message}")


def print_error(message):
    """Print an error message."""
    print(f"✗ {message}")


def test_survey_import():
    """Test 1: Survey data import and validation."""
    print_header("TEST 1: Survey Data Import and Validation")

    try:
        handler = DataHandler()

        # Import survey data
        print("Importing survey data from data/sample_survey.csv...")
        survey_df = handler.read_survey_data('data/sample_survey.csv')
        print_success(f"Loaded {len(survey_df)} survey responses")

        # Validate required columns
        required_cols = handler.SURVEY_REQUIRED_COLUMNS
        missing = set(required_cols) - set(survey_df.columns)
        if missing:
            print_error(f"Missing required columns: {missing}")
            return False
        print_success(f"All required columns present: {required_cols}")

        # Validate rating columns
        rating_cols = handler.SURVEY_RATING_COLUMNS
        present_rating_cols = [col for col in rating_cols if col in survey_df.columns]
        print_success(f"Found {len(present_rating_cols)} rating columns: {present_rating_cols}")

        # Validate data
        is_valid, errors = handler.validate_survey_data(survey_df)
        if errors:
            print(f"⚠ Validation warnings: {len(errors)}")
            for error in errors:
                print(f"  - {error}")
        else:
            print_success("Survey data validation passed")

        # Check data quality
        unique_apps = survey_df['Application Name'].nunique()
        unique_stakeholders = survey_df['Stakeholder Name'].nunique()
        avg_responses = len(survey_df) / unique_apps

        print(f"\nSurvey Statistics:")
        print(f"  • Total responses: {len(survey_df)}")
        print(f"  • Unique applications: {unique_apps}")
        print(f"  • Unique stakeholders: {unique_stakeholders}")
        print(f"  • Avg responses per app: {avg_responses:.1f}")

        return True

    except Exception as e:
        print_error(f"Survey import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_response_aggregation():
    """Test 2: Response aggregation and consensus calculation."""
    print_header("TEST 2: Response Aggregation and Consensus")

    try:
        handler = DataHandler()
        survey_df = handler.read_survey_data('data/sample_survey.csv')

        # Test mean aggregation
        print("Testing mean aggregation...")
        agg_mean = handler.aggregate_survey_responses(survey_df, method='mean')
        print_success(f"Aggregated to {len(agg_mean)} applications using mean")

        # Test median aggregation
        print("Testing median aggregation...")
        agg_median = handler.aggregate_survey_responses(survey_df, method='median')
        print_success(f"Aggregated to {len(agg_median)} applications using median")

        # Check aggregation output columns
        required_agg_cols = ['Application Name', 'Survey Response Count']
        if all(col in agg_mean.columns for col in required_agg_cols):
            print_success(f"Aggregation output has required columns")
        else:
            print_error(f"Missing required aggregation columns")
            return False

        # Check consensus metrics
        if 'Overall Consensus Score' in agg_mean.columns:
            print_success("Consensus scores calculated")
            avg_consensus = agg_mean['Overall Consensus Score'].mean()
            print(f"  • Average consensus: {avg_consensus:.2f}/5")

            high_consensus = len(agg_mean[agg_mean['Overall Consensus Score'] >= 4])
            low_consensus = len(agg_mean[agg_mean['Overall Consensus Score'] < 3])
            print(f"  • High consensus apps: {high_consensus}")
            print(f"  • Low consensus apps: {low_consensus}")
        else:
            print_error("Consensus scores not calculated")
            return False

        # Verify rating columns aggregated
        for col in handler.SURVEY_RATING_COLUMNS:
            if col in agg_mean.columns:
                print_success(f"  {col} aggregated (mean: {agg_mean[col].mean():.2f})")

        return True

    except Exception as e:
        print_error(f"Response aggregation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_survey_assessment_merge():
    """Test 3: Merging survey data with assessment results."""
    print_header("TEST 3: Survey-Assessment Data Merge")

    try:
        handler = DataHandler()

        # Run quantitative assessment
        print("Running quantitative assessment...")
        assessment_df = handler.read_csv('data/assessment_template.csv')
        scoring = ScoringEngine()
        rec_engine = RecommendationEngine()
        time_framework = TIMEFramework()

        apps = assessment_df.to_dict('records')
        scored = scoring.batch_calculate_scores(apps)
        recommended = rec_engine.batch_generate_recommendations(scored)
        final = time_framework.batch_categorize(recommended)
        assessment_results = pd.DataFrame(final)
        print_success(f"Completed assessment of {len(assessment_results)} applications")

        # Load and aggregate survey
        print("Loading and aggregating survey data...")
        survey_df = handler.read_survey_data('data/sample_survey.csv')
        aggregated_survey = handler.aggregate_survey_responses(survey_df)
        print_success(f"Aggregated survey data for {len(aggregated_survey)} applications")

        # Merge with different weights
        for weight in [0.2, 0.3, 0.5]:
            print(f"\nTesting merge with {weight:.0%} survey weight...")
            merged = handler.merge_survey_with_assessment(
                assessment_results,
                aggregated_survey,
                survey_weight=weight
            )
            print_success(f"Merged {len(merged)} applications")

            # Check merged columns
            expected_cols = [
                'Business Value Original',
                'Business Value Survey Adjusted',
                'Business Value Variance',
                'Has Survey Data',
                'Survey Response Count',
                'High Variance Flag'
            ]

            present = [col for col in expected_cols if col in merged.columns]
            if len(present) == len(expected_cols):
                print_success(f"All expected columns present ({len(present)})")
            else:
                missing = set(expected_cols) - set(present)
                print_error(f"Missing columns: {missing}")
                return False

        # Verify merge results
        merged_final = handler.merge_survey_with_assessment(
            assessment_results,
            aggregated_survey,
            survey_weight=0.3
        )

        apps_with_survey = merged_final['Has Survey Data'].sum()
        print(f"\n  • Applications with survey data: {apps_with_survey}")
        print(f"  • Applications without survey: {len(merged_final) - apps_with_survey}")

        if 'High Variance Flag' in merged_final.columns:
            high_var_count = merged_final['High Variance Flag'].sum()
            print(f"  • High variance applications: {high_var_count}")

        return True

    except Exception as e:
        print_error(f"Survey-assessment merge failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_survey_impact_analysis():
    """Test 4: Survey impact analysis."""
    print_header("TEST 4: Survey Impact Analysis")

    try:
        handler = DataHandler()

        # Prepare merged data
        print("Preparing merged assessment data...")
        assessment_df = handler.read_csv('data/assessment_template.csv')
        scoring = ScoringEngine()
        rec_engine = RecommendationEngine()
        time_framework = TIMEFramework()

        apps = assessment_df.to_dict('records')
        scored = scoring.batch_calculate_scores(apps)
        recommended = rec_engine.batch_generate_recommendations(scored)
        final = time_framework.batch_categorize(recommended)
        assessment_results = pd.DataFrame(final)

        survey_df = handler.read_survey_data('data/sample_survey.csv')
        aggregated_survey = handler.aggregate_survey_responses(survey_df)
        merged = handler.merge_survey_with_assessment(
            assessment_results,
            aggregated_survey,
            survey_weight=0.3
        )
        print_success("Merged data prepared")

        # Calculate impact
        print("\nCalculating survey impact...")
        impact = handler.calculate_survey_impact(merged)
        print_success("Impact analysis complete")

        # Check impact components
        expected_components = [
            'variance_summary',
            'consensus_summary',
            'sentiment_analysis',
            'high_variance_apps',
            'needs_attention'
        ]

        present_components = [comp for comp in expected_components if comp in impact]
        print(f"\nImpact components present: {len(present_components)}/{len(expected_components)}")
        for comp in present_components:
            print_success(f"  {comp}")

        # Display impact metrics
        if 'variance_summary' in impact:
            print("\nVariance Summary:")
            for metric, stats in list(impact['variance_summary'].items())[:2]:
                print(f"  • {metric}:")
                print(f"    - Mean: {stats['mean']:.2f}")
                print(f"    - Std: {stats['std']:.2f}")

        if 'consensus_summary' in impact:
            print("\nConsensus Summary:")
            cons = impact['consensus_summary']
            print(f"  • Average consensus: {cons['average_consensus']:.2f}/5")
            print(f"  • High consensus apps: {cons['high_consensus_count']}")
            print(f"  • Low consensus apps: {cons['low_consensus_count']}")

        if 'sentiment_analysis' in impact:
            print("\nSentiment Analysis:")
            for category, count in impact['sentiment_analysis'].items():
                print(f"  • {category}: {count}")

        if 'high_variance_apps' in impact:
            print(f"\nHigh Variance Applications: {len(impact['high_variance_apps'])}")

        if 'needs_attention' in impact:
            print(f"Applications Needing Attention: {len(impact['needs_attention'])}")
            if len(impact['needs_attention']) > 0:
                print(f"  Sample: {impact['needs_attention'][0]['Application Name']}")

        return True

    except Exception as e:
        print_error(f"Impact analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_survey_report_export():
    """Test 5: Survey analysis report export."""
    print_header("TEST 5: Survey Analysis Report Export")

    try:
        handler = DataHandler()

        # Prepare merged data
        print("Preparing merged data for export...")
        assessment_df = handler.read_csv('data/assessment_template.csv')
        scoring = ScoringEngine()
        rec_engine = RecommendationEngine()
        time_framework = TIMEFramework()

        apps = assessment_df.to_dict('records')
        scored = scoring.batch_calculate_scores(apps)
        recommended = rec_engine.batch_generate_recommendations(scored)
        final = time_framework.batch_categorize(recommended)
        assessment_results = pd.DataFrame(final)

        survey_df = handler.read_survey_data('data/sample_survey.csv')
        aggregated_survey = handler.aggregate_survey_responses(survey_df)
        merged = handler.merge_survey_with_assessment(
            assessment_results,
            aggregated_survey,
            survey_weight=0.3
        )

        # Export survey analysis
        print("\nExporting survey analysis report...")
        output_path = handler.export_survey_analysis(
            merged,
            'output/test_survey_analysis.xlsx',
            include_timestamp=True
        )
        print_success(f"Report exported to: {output_path}")

        # Verify file exists and has content
        if output_path.exists():
            file_size = output_path.stat().st_size
            print_success(f"File created successfully ({file_size / 1024:.1f} KB)")

            if file_size < 5000:
                print_error("File size suspiciously small")
                return False
        else:
            print_error("Report file not created")
            return False

        # Verify Excel structure
        try:
            import openpyxl
            wb = openpyxl.load_workbook(output_path)
            sheets = wb.sheetnames
            print(f"\nExcel worksheets: {len(sheets)}")
            for sheet in sheets:
                print(f"  • {sheet}")

            expected_sheets = ['Survey_Analysis', 'Impact_Summary']
            if all(sheet in sheets for sheet in expected_sheets):
                print_success("Core worksheets present")
            else:
                print_error("Missing expected worksheets")
                return False

        except Exception as e:
            print_error(f"Could not validate Excel structure: {e}")
            return False

        return True

    except Exception as e:
        print_error(f"Report export failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_end_to_end_workflow():
    """Test 6: Complete end-to-end workflow."""
    print_header("TEST 6: End-to-End Workflow")

    try:
        handler = DataHandler()

        # Step 1: Assessment
        print("Step 1: Running quantitative assessment...")
        assessment_df = handler.read_csv('data/assessment_template.csv')
        scoring = ScoringEngine()
        rec_engine = RecommendationEngine()
        time_framework = TIMEFramework()

        apps = assessment_df.to_dict('records')
        scored = scoring.batch_calculate_scores(apps)
        recommended = rec_engine.batch_generate_recommendations(scored)
        final = time_framework.batch_categorize(recommended)
        assessment_results = pd.DataFrame(final)
        print_success(f"Assessment complete: {len(assessment_results)} apps")

        # Step 2: Survey import
        print("\nStep 2: Importing survey data...")
        survey_df = handler.read_survey_data('data/sample_survey.csv')
        print_success(f"Survey data loaded: {len(survey_df)} responses")

        # Step 3: Aggregation
        print("\nStep 3: Aggregating survey responses...")
        aggregated = handler.aggregate_survey_responses(survey_df, method='mean')
        print_success(f"Aggregated to {len(aggregated)} applications")

        # Step 4: Merge
        print("\nStep 4: Merging survey with assessment...")
        merged = handler.merge_survey_with_assessment(
            assessment_results,
            aggregated,
            survey_weight=0.3
        )
        print_success(f"Merged {len(merged)} applications")

        # Step 5: Impact analysis
        print("\nStep 5: Analyzing survey impact...")
        impact = handler.calculate_survey_impact(merged)
        print_success("Impact analysis complete")

        # Step 6: Export
        print("\nStep 6: Exporting reports...")

        # Save CSV
        csv_path = Path('output/test_merged_results.csv')
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        merged.to_csv(csv_path, index=False)
        print_success(f"CSV saved: {csv_path}")

        # Save Excel
        excel_path = handler.export_survey_analysis(
            merged,
            'output/test_complete_analysis.xlsx',
            include_timestamp=False
        )
        print_success(f"Excel report saved: {excel_path}")

        # Verify outputs
        print("\nVerifying outputs...")
        if csv_path.exists() and excel_path.exists():
            print_success("All output files created")
        else:
            print_error("Some output files missing")
            return False

        # Display summary
        print("\n" + "=" * 70)
        print("WORKFLOW SUMMARY")
        print("=" * 70)
        print(f"  ✓ Assessed {len(assessment_results)} applications")
        print(f"  ✓ Processed {len(survey_df)} survey responses")
        print(f"  ✓ {merged['Has Survey Data'].sum()} apps have survey data")

        if 'high_variance_apps' in impact:
            print(f"  ✓ {len(impact['high_variance_apps'])} high variance apps")
        if 'needs_attention' in impact:
            print(f"  ✓ {len(impact['needs_attention'])} apps need attention")

        return True

    except Exception as e:
        print_error(f"End-to-end workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("SURVEY INTEGRATION TEST SUITE")
    print("=" * 70)
    print("\nTesting stakeholder survey integration features...")

    # Create output directory
    Path('output').mkdir(exist_ok=True)

    # Run tests
    tests = [
        ("Survey Data Import", test_survey_import),
        ("Response Aggregation", test_response_aggregation),
        ("Survey-Assessment Merge", test_survey_assessment_merge),
        ("Survey Impact Analysis", test_survey_impact_analysis),
        ("Survey Report Export", test_survey_report_export),
        ("End-to-End Workflow", test_end_to_end_workflow),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Test '{name}' crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {name:30s} {status}")

    print()
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Survey integration is working correctly.")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
