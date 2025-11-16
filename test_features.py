#!/usr/bin/env python3
"""
Quick test script to verify visualization and export features work correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data_handler import DataHandler
from src.scoring_engine import ScoringEngine
from src.recommendation_engine import RecommendationEngine
from src.time_framework import TIMEFramework
from src.visualizations import VisualizationEngine
import pandas as pd

def test_features():
    print("=" * 70)
    print("TESTING VISUALIZATION AND EXPORT FEATURES")
    print("=" * 70)
    print()

    try:
        # Step 1: Load and process data
        print("Step 1: Loading and processing assessment data...")
        data_handler = DataHandler()
        df = data_handler.read_csv('data/assessment_template.csv')
        print(f"✓ Loaded {len(df)} applications")

        # Step 2: Run assessment
        print("\nStep 2: Running assessment...")
        scoring_engine = ScoringEngine()
        rec_engine = RecommendationEngine()
        time_framework = TIMEFramework()

        applications = df.to_dict('records')
        scored_apps = scoring_engine.batch_calculate_scores(applications)
        final_apps = rec_engine.batch_generate_recommendations(scored_apps)
        final_apps = time_framework.batch_categorize(final_apps)

        results_df = pd.DataFrame(final_apps)
        print(f"✓ Assessment complete for {len(results_df)} applications")

        # Step 3: Save CSV
        print("\nStep 3: Saving CSV results...")
        csv_path = data_handler.write_csv(
            results_df,
            'output/test_results.csv',
            include_timestamp=False
        )
        print(f"✓ CSV saved: {csv_path}")

        # Step 4: Create one visualization (heatmap)
        print("\nStep 4: Creating sample visualization (heatmap)...")
        viz_engine = VisualizationEngine(
            output_dir=Path('output/visualizations'),
            style='professional'
        )

        heatmap_path = viz_engine.create_score_heatmap(
            results_df,
            output_file='test_heatmap.png',
            max_apps=15,
            title='Application Portfolio Score Heatmap - Test'
        )
        print(f"✓ Heatmap created: {heatmap_path}")

        # Step 5: Create Power BI export
        print("\nStep 5: Creating Power BI export...")
        powerbi_path = data_handler.export_for_powerbi(
            results_df,
            'output/test_powerbi_export.xlsx',
            include_timestamp=False
        )
        print(f"✓ Power BI export created: {powerbi_path}")
        print(f"  File size: {powerbi_path.stat().st_size / 1024:.1f} KB")

        # Step 6: Create Enhanced Excel export
        print("\nStep 6: Creating Enhanced Excel export...")
        excel_path = data_handler.export_enhanced_excel(
            results_df,
            'output/test_enhanced_excel.xlsx',
            include_timestamp=False,
            include_charts=True
        )
        print(f"✓ Enhanced Excel created: {excel_path}")
        print(f"  File size: {excel_path.stat().st_size / 1024:.1f} KB")

        # Summary
        print("\n" + "=" * 70)
        print("ALL TESTS PASSED SUCCESSFULLY!")
        print("=" * 70)
        print("\nGenerated files:")
        print(f"  • CSV: output/test_results.csv")
        print(f"  • Heatmap: output/visualizations/test_heatmap.png")
        print(f"  • Power BI: output/test_powerbi_export.xlsx")
        print(f"  • Enhanced Excel: output/test_enhanced_excel.xlsx")
        print("\nFeatures verified:")
        print("  ✓ Assessment pipeline")
        print("  ✓ Visualization generation")
        print("  ✓ Power BI export")
        print("  ✓ Enhanced Excel export")
        print()

        return 0

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(test_features())
