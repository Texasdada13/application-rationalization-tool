# Visualization and Export Guide

## Table of Contents

1. [Overview](#overview)
2. [Visualization Types](#visualization-types)
3. [CLI Usage](#cli-usage)
4. [Programmatic Usage](#programmatic-usage)
5. [Export Formats](#export-formats)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Examples](#advanced-examples)

---

## Overview

The Application Rationalization Tool provides comprehensive visualization and export capabilities to help you analyze, communicate, and act on application portfolio insights. This guide covers:

- **6 Visualization Types**: Heatmaps, TIME quadrants, priority matrices, distributions, summaries, and dashboards
- **3 Export Formats**: CSV, Power BI-optimized Excel, and Enhanced Excel with formatting
- **3 Usage Methods**: CLI commands, Python API, and quick helper functions
- **3 Visualization Styles**: Professional, Presentation, and Technical

### Key Features

- 🎨 **Professional Visualizations**: High-DPI charts ready for presentations
- 📊 **Interactive Dashboards**: Comprehensive multi-panel views
- 📈 **Executive Reports**: Formatted Excel with charts and conditional formatting
- 🔄 **Power BI Integration**: Optimized exports with proper table relationships
- ⚡ **Quick Analysis**: Helper functions for rapid insights
- 🎯 **Customizable**: Flexible parameters and styling options

---

## Visualization Types

### 1. Score Heatmap

**Purpose**: Visual overview of application scores across all dimensions

**Use Cases**:
- Portfolio health assessment
- Identifying strengths and weaknesses
- Comparing applications side-by-side
- Spotting outliers and patterns

**Key Parameters**:
- `max_apps`: Limit display to top N applications (default: 30)
- `dimensions`: List of scoring dimensions to include
- `show_values`: Display numeric values on cells (default: True)

**CLI Example**:
```bash
python -m src.cli visualize -i results.csv -t heatmap -o output/visualizations/
```

**Python Example**:
```python
from src.visualizations import VisualizationEngine
import pandas as pd

viz = VisualizationEngine()
df = pd.read_csv('results.csv')
path = viz.create_score_heatmap(
    df,
    max_apps=20,
    dimensions=['Business Value', 'Tech Health', 'Security'],
    title='Application Portfolio Score Analysis'
)
```

**Interpretation Guide**:
- 🟢 **Green cells**: High scores (7-10) - Strong performance
- 🟡 **Yellow cells**: Medium scores (4-6) - Needs attention
- 🔴 **Red cells**: Low scores (0-3) - Critical issues

### 2. TIME Framework Quadrant

**Purpose**: Strategic positioning of applications in the TIME framework

**Use Cases**:
- Strategic planning sessions
- Portfolio rationalization decisions
- Investment prioritization
- Executive communications

**The Four Quadrants**:
```
High BV │  TOLERATE  │  INVEST   │
        │  (Orange)  │  (Green)  │
────────┼────────────┼───────────┤
Low BV  │ ELIMINATE  │  MIGRATE  │
        │   (Red)    │  (Blue)   │
        └────────────┴───────────┘
          Low TQ       High TQ
```

**CLI Example**:
```bash
python -m src.cli visualize -i results.csv -t time-quadrant
```

**Python Example**:
```python
path = viz.create_time_quadrant_heatmap(
    df,
    show_labels=True,  # Display application names
    title='Strategic Application Portfolio Analysis'
)
```

**Decision Matrix**:
- **INVEST (Top-Right)**: Continue investing, maximize value
- **TOLERATE (Top-Left)**: Maintain but plan improvements
- **MIGRATE (Bottom-Right)**: Consolidate or modernize
- **ELIMINATE (Bottom-Left)**: Retire or decommission

### 3. Priority Matrix

**Purpose**: Multi-dimensional bubble chart for prioritization

**Use Cases**:
- Budget allocation decisions
- Identifying high-value opportunities
- Understanding cost-value relationships
- Technical debt prioritization

**Visualization Dimensions**:
- **X-Axis**: Composite Score (overall health)
- **Y-Axis**: Business Value (strategic importance)
- **Bubble Size**: Cost (investment level)
- **Bubble Color**: Tech Health (technical quality)

**CLI Example**:
```bash
python -m src.cli visualize -i results.csv -t priority-matrix
```

**Python Example**:
```python
path = viz.create_priority_matrix(
    df,
    x_metric='Composite Score',
    y_metric='Business Value',
    size_metric='Cost',
    color_metric='Tech Health',
    title='Application Investment Priority Matrix'
)
```

**Reading the Chart**:
- **Large red bubbles in top-left**: High-cost, high-value apps with tech debt → Priority for modernization
- **Small green bubbles in top-right**: Low-cost, high-value apps in good shape → Maintain
- **Large bubbles in bottom half**: High-cost, low-value apps → Candidates for elimination

### 4. Distribution Plots

**Purpose**: Statistical overview of score distributions

**Use Cases**:
- Portfolio health trends
- Identifying score clustering
- Benchmarking against targets
- Tracking improvements over time

**Metrics Displayed**:
- Business Value distribution
- Tech Health distribution
- Security distribution
- Strategic Fit distribution
- Composite Score distribution

**CLI Example**:
```bash
python -m src.cli visualize -i results.csv -t distributions
```

**Python Example**:
```python
path = viz.create_distribution_plots(
    df,
    metrics=['Business Value', 'Tech Health', 'Composite Score'],
    title='Portfolio Score Distributions'
)
```

**Interpretation**:
- **Normal distribution**: Healthy portfolio with expected variation
- **Left-skewed**: Most apps scoring low (portfolio at risk)
- **Right-skewed**: Most apps scoring high (healthy portfolio)
- **Bimodal**: Two distinct groups (e.g., legacy vs. modern)

### 5. TIME Category Summary

**Purpose**: Visual breakdown of TIME framework categorization

**Use Cases**:
- Executive summaries
- Portfolio composition overview
- Tracking category shifts over time
- Board presentations

**Chart Types**:
- Pie chart showing percentage distribution
- Bar chart showing application counts

**CLI Example**:
```bash
python -m src.cli visualize -i results.csv -t time-summary
```

**Python Example**:
```python
path = viz.create_time_category_summary(
    df,
    title='TIME Framework Portfolio Distribution'
)
```

**Healthy Portfolio Benchmarks**:
- **Invest**: 20-30% (growth focus)
- **Tolerate**: 30-40% (stable operations)
- **Migrate**: 20-30% (modernization pipeline)
- **Eliminate**: 10-20% (technical debt reduction)

### 6. Comprehensive Dashboard

**Purpose**: All-in-one executive dashboard

**Use Cases**:
- Executive presentations
- Board meetings
- Quarterly business reviews
- Strategic planning sessions

**Dashboard Components**:
1. **TIME Quadrant**: Strategic positioning
2. **TIME Distribution**: Category breakdown
3. **Top Applications**: Highest scorers
4. **Score Distribution**: Portfolio health
5. **Key Metrics**: Summary statistics
6. **Recommendations**: Top actions

**CLI Example**:
```bash
python -m src.cli visualize -i results.csv -t dashboard
```

**Python Example**:
```python
path = viz.create_comprehensive_dashboard(
    df,
    title='Application Rationalization Executive Dashboard - Q4 2025'
)
```

---

## CLI Usage

### Basic Commands

#### Visualize Command

```bash
# Create all visualizations
python -m src.cli visualize -i results.csv

# Create specific visualization type
python -m src.cli visualize -i results.csv -t heatmap

# Specify output directory
python -m src.cli visualize -i results.csv -o output/my_visuals/

# Use different style
python -m src.cli visualize -i results.csv --style presentation
```

**Available Visualization Types**:
- `heatmap` - Application score heatmap
- `time-quadrant` - TIME framework quadrant
- `priority-matrix` - Priority bubble chart
- `distributions` - Score distribution plots
- `time-summary` - TIME category summary
- `dashboard` - Comprehensive dashboard
- `all` - Create all visualizations (default)

**Available Styles**:
- `professional` - Clean, business-focused (default)
- `presentation` - Bold, high contrast
- `technical` - Detailed, precise

#### Export Command

```bash
# Enhanced Excel export (default)
python -m src.cli export -i results.csv -o output/report.xlsx

# Power BI export
python -m src.cli export -i results.csv -f powerbi -o output/powerbi.xlsx

# Create both formats
python -m src.cli export -i results.csv -f both -o output/export.xlsx

# Without charts (smaller file)
python -m src.cli export -i results.csv --no-charts

# Without timestamp
python -m src.cli export -i results.csv --no-timestamp
```

**Export Format Options**:
- `excel-enhanced` - Enhanced Excel with formatting and charts (default)
- `powerbi` - Power BI-optimized Excel
- `both` - Create both formats

### Complete Workflow Example

```bash
# Step 1: Run assessment
python -m src.cli assess -i data/assessment_template.csv -o output/results.csv

# Step 2: Create visualizations
python -m src.cli visualize -i output/results.csv -t all

# Step 3: Create exports
python -m src.cli export -i output/results.csv -f both -o output/final_report.xlsx
```

---

## Programmatic Usage

### Basic Setup

```python
from src.visualizations import VisualizationEngine, quick_visualize
from src.data_handler import DataHandler
import pandas as pd
from pathlib import Path

# Initialize components
data_handler = DataHandler()
viz_engine = VisualizationEngine(
    output_dir=Path('output/visualizations'),
    style='professional'
)

# Load results
df = pd.read_csv('output/assessment_results.csv')
```

### Creating Individual Visualizations

```python
# Score heatmap
heatmap_path = viz_engine.create_score_heatmap(
    df,
    max_apps=25,
    output_file='portfolio_heatmap.png',
    title='Application Portfolio Analysis'
)

# TIME quadrant
quadrant_path = viz_engine.create_time_quadrant_heatmap(
    df,
    show_labels=True,
    output_file='time_framework.png'
)

# Priority matrix
matrix_path = viz_engine.create_priority_matrix(
    df,
    x_metric='Composite Score',
    y_metric='Business Value',
    size_metric='Cost',
    color_metric='Tech Health'
)

# Distributions
dist_path = viz_engine.create_distribution_plots(
    df,
    metrics=['Business Value', 'Tech Health', 'Security']
)

# TIME summary
summary_path = viz_engine.create_time_category_summary(df)

# Dashboard
dashboard_path = viz_engine.create_comprehensive_dashboard(df)
```

### Using Quick Visualize Helper

```python
# Create all visualizations at once
results = quick_visualize(
    input_file='output/results.csv',
    output_dir='output/visualizations',
    viz_types=['time_quadrant', 'dashboard', 'time_summary']
)

# Access created files
for viz_type, path in results.items():
    print(f"{viz_type}: {path}")
```

### Creating Exports Programmatically

```python
from src.data_handler import DataHandler

data_handler = DataHandler()
df = pd.read_csv('results.csv')

# Power BI export
powerbi_path = data_handler.export_for_powerbi(
    df,
    output_path='output/powerbi_export.xlsx',
    include_timestamp=True
)

# Enhanced Excel export
excel_path = data_handler.export_enhanced_excel(
    df,
    output_path='output/executive_report.xlsx',
    include_timestamp=True,
    include_charts=True
)
```

### Custom Styling

```python
# Create visualizations with different styles
styles = ['professional', 'presentation', 'technical']

for style in styles:
    viz = VisualizationEngine(
        output_dir=Path(f'output/{style}'),
        style=style
    )

    viz.create_score_heatmap(df, output_file=f'heatmap_{style}.png')
```

---

## Export Formats

### 1. CSV Export (Basic)

**Purpose**: Simple, portable data format

**Use Cases**:
- Data archival
- Import into other tools
- Version control
- Programmatic processing

**Features**:
- All assessment data in single file
- Easy to parse and process
- Timestamps optional
- Lightweight

**Create**:
```python
data_handler.write_csv(df, 'output/results.csv', include_timestamp=True)
```

### 2. Power BI-Optimized Excel Export

**Purpose**: Multi-sheet workbook optimized for Power BI import

**Use Cases**:
- Interactive dashboards
- Drill-down analysis
- Self-service BI
- Data relationships

**Sheet Structure**:

| Sheet | Purpose | Key Columns |
|-------|---------|-------------|
| **Applications** | Main fact table | Application_ID, all assessment data |
| **Dimension_Scores** | Normalized scores | Application_ID, Dimension, Score |
| **TIME_Framework** | TIME categorization | Application_ID, TIME Category, Scores |
| **Recommendations** | Actions | Application_ID, Action, Comments |
| **Summary_Stats** | Portfolio metrics | Metric, Value |
| **TIME_Distribution** | Category breakdown | TIME_Category, Count, Percentage |
| **Metadata** | Export info | Property, Value |

**Features**:
- Properly formatted Excel tables
- Application_ID for relationships
- Normalized dimension table
- Ready for Power BI import
- Metadata for tracking

**Power BI Import Steps**:

1. **Open Power BI Desktop**
2. **Get Data** → **Excel**
3. **Select** the Power BI export file
4. **Load** these tables:
   - Applications (main fact table)
   - Dimension_Scores (for detailed analysis)
   - TIME_Framework (for categorization)
5. **Create Relationships**:
   - Applications[Application_ID] ↔ Dimension_Scores[Application_ID]
   - Applications[Application_ID] ↔ TIME_Framework[Application_ID]
6. **Build Visualizations**:
   - Cards for summary metrics
   - Bar charts for top applications
   - Scatter plot for TIME quadrant
   - Slicers for filtering by TIME category

**Create**:
```python
data_handler.export_for_powerbi(
    df,
    'output/powerbi_export.xlsx',
    include_timestamp=True
)
```

### 3. Enhanced Excel Export

**Purpose**: Presentation-ready Excel with formatting and charts

**Use Cases**:
- Executive presentations
- Board reports
- Stakeholder communications
- Printable reports

**Sheet Structure**:

| Sheet | Features |
|-------|----------|
| **Summary_Dashboard** | Executive summary with key metrics |
| **Detailed_Scores** | All applications with conditional formatting |
| **TIME_Framework** | TIME categories with color coding + pie chart |
| **Recommendations** | Sorted recommendations + bar chart |
| **Cost_Analysis** | Cost breakdown with currency formatting |

**Formatting Features**:

1. **Conditional Formatting**:
   - Score columns: Red-Yellow-Green color scale
   - Cost column: Green-Yellow-Red (lower is better)
   - TIME categories: Color-coded backgrounds

2. **Charts**:
   - Pie chart: TIME category distribution
   - Bar chart: Top recommendations
   - Embedded in relevant sheets

3. **Professional Styling**:
   - Header row: Bold white text on blue background
   - Freeze panes on all sheets
   - Auto-filters enabled
   - Auto-adjusted column widths
   - Currency formatting for costs

4. **User Experience**:
   - Easy navigation between sheets
   - Clear section headers
   - Consistent formatting
   - Print-ready layouts

**Create**:
```python
data_handler.export_enhanced_excel(
    df,
    'output/executive_report.xlsx',
    include_timestamp=True,
    include_charts=True
)
```

**Create Without Charts** (smaller file):
```python
data_handler.export_enhanced_excel(
    df,
    'output/report_no_charts.xlsx',
    include_timestamp=True,
    include_charts=False
)
```

---

## Best Practices

### Visualization Best Practices

#### 1. Choose the Right Visualization

| Goal | Recommended Visualization |
|------|--------------------------|
| Portfolio overview | Dashboard or Score Heatmap |
| Strategic planning | TIME Quadrant |
| Budget allocation | Priority Matrix |
| Performance trends | Distribution Plots |
| Executive summary | TIME Category Summary |
| Comprehensive analysis | Dashboard |

#### 2. Optimize for Audience

| Audience | Style | Focus | Export Format |
|----------|-------|-------|---------------|
| Executives | Presentation | Dashboard, TIME Summary | Enhanced Excel |
| Technical Teams | Technical | Heatmap, Distributions | CSV, Enhanced Excel |
| Analysts | Professional | All visualizations | Power BI Export |
| Stakeholders | Presentation | TIME Quadrant, Summary | Enhanced Excel |

#### 3. Visualization Quality

- **Use appropriate DPI**: All visualizations are 300 DPI for print quality
- **Limit displayed items**: Show top 20-30 applications for readability
- **Add context**: Include titles that explain what the visualization shows
- **Use consistent colors**: TIME framework colors are standardized
- **Label clearly**: All axes, legends, and data points should be clear

#### 4. File Organization

```
output/
├── visualizations/
│   ├── executive/          # For board presentations
│   ├── technical/          # For detailed analysis
│   └── monthly/            # Regular reporting
├── exports/
│   ├── powerbi/           # Power BI exports
│   └── reports/           # Enhanced Excel reports
└── archive/               # Historical versions
```

### Export Best Practices

#### 1. Naming Conventions

Use descriptive, timestamped filenames:

```
Good:
- assessment_results_20250315_144523.csv
- powerbi_export_Q1_2025_20250331.xlsx
- executive_report_march_2025.xlsx

Avoid:
- results.csv
- export.xlsx
- file1.xlsx
```

#### 2. Regular Cadence

Establish a regular reporting schedule:

- **Weekly**: CSV exports for tracking
- **Monthly**: Enhanced Excel for stakeholder updates
- **Quarterly**: Full package (all visualizations + both export formats)
- **Annual**: Comprehensive review with trend analysis

#### 3. Version Control

- Enable timestamps for all exports
- Archive previous versions before generating new ones
- Track changes in assessment data
- Document methodology changes

#### 4. Data Quality

Before exporting:

1. **Validate Data**:
   ```python
   is_valid, errors = data_handler.validate_data(df)
   if not is_valid:
       print("Errors:", errors)
   ```

2. **Check Completeness**:
   - All applications have scores
   - TIME categorization is complete
   - No missing critical fields

3. **Review Statistics**:
   ```python
   stats = data_handler.get_summary_statistics(df)
   print(stats)
   ```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: "Missing required columns" error

**Cause**: DataFrame doesn't have all required columns for visualization

**Solution**:
```python
# Check required columns
required = ['Business Value', 'Tech Health', 'Composite Score']
missing = [col for col in required if col not in df.columns]
if missing:
    print(f"Missing: {missing}")

# Run full assessment to generate all columns
from src.scoring_engine import ScoringEngine
from src.time_framework import TIMEFramework

scoring_engine = ScoringEngine()
time_framework = TIMEFramework()

apps = df.to_dict('records')
scored = scoring_engine.batch_calculate_scores(apps)
categorized = time_framework.batch_categorize(scored)
df = pd.DataFrame(categorized)
```

#### Issue: Visualizations look blurry or low quality

**Cause**: Display scaling or export settings

**Solution**:
- Visualizations are created at 300 DPI by default
- Ensure you're viewing the PNG files at 100% zoom
- For presentations, import PNGs directly (don't screenshot)

#### Issue: Power BI can't find relationships

**Cause**: Application_ID field not properly imported

**Solution**:
1. In Power BI, go to Model view
2. Manually create relationships:
   - Drag `Applications[Application_ID]` to `Dimension_Scores[Application_ID]`
   - Drag `Applications[Application_ID]` to `TIME_Framework[Application_ID]`
3. Set relationship cardinality to One-to-Many

#### Issue: Excel file is too large

**Causes**: Too many applications or charts included

**Solutions**:
```python
# Option 1: Disable charts
data_handler.export_enhanced_excel(
    df,
    'output/report.xlsx',
    include_charts=False
)

# Option 2: Filter to top applications
top_apps = df.nlargest(50, 'Composite Score')
data_handler.export_enhanced_excel(top_apps, 'output/report.xlsx')

# Option 3: Use CSV instead
data_handler.write_csv(df, 'output/results.csv')
```

#### Issue: Charts not showing in Excel

**Cause**: OpenPyXL chart compatibility or Excel version

**Solution**:
- Use Excel 2016 or later
- Save and reopen the file
- Check that `include_charts=True` is set
- Verify openpyxl version: `pip install --upgrade openpyxl`

#### Issue: Colors not displaying correctly

**Cause**: Monitor color profile or export settings

**Solution**:
- Check visualization style setting
- Ensure matplotlib backend is configured correctly
- Update matplotlib: `pip install --upgrade matplotlib`

---

## Advanced Examples

### Example 1: Automated Monthly Reporting

Create a script that runs automatically each month:

```python
#!/usr/bin/env python3
"""
Monthly Application Rationalization Report Generator
Runs automatically via cron/scheduler
"""

from datetime import datetime
from pathlib import Path
from src.data_handler import DataHandler
from src.scoring_engine import ScoringEngine
from src.recommendation_engine import RecommendationEngine
from src.time_framework import TIMEFramework
from src.visualizations import quick_visualize
import pandas as pd

def monthly_report():
    # Configuration
    month = datetime.now().strftime('%Y-%m')
    output_base = Path(f'output/monthly/{month}')
    output_base.mkdir(parents=True, exist_ok=True)

    # Load data
    data_handler = DataHandler()
    df = data_handler.read_csv('data/current_assessment.csv')

    # Run assessment
    scoring = ScoringEngine()
    recommendations = RecommendationEngine()
    time_fw = TIMEFramework()

    apps = df.to_dict('records')
    apps = scoring.batch_calculate_scores(apps)
    apps = recommendations.batch_generate_recommendations(apps)
    apps = time_fw.batch_categorize(apps)

    results_df = pd.DataFrame(apps)

    # Save CSV
    csv_path = output_base / f'assessment_{month}.csv'
    data_handler.write_csv(results_df, csv_path, include_timestamp=False)

    # Create visualizations
    viz_paths = quick_visualize(
        csv_path,
        output_dir=output_base / 'visualizations',
        viz_types=['time_quadrant', 'dashboard', 'time_summary']
    )

    # Create exports
    data_handler.export_for_powerbi(
        results_df,
        output_base / f'powerbi_{month}.xlsx',
        include_timestamp=False
    )

    data_handler.export_enhanced_excel(
        results_df,
        output_base / f'executive_report_{month}.xlsx',
        include_timestamp=False,
        include_charts=True
    )

    print(f"Monthly report generated for {month}")
    print(f"Location: {output_base}")

if __name__ == '__main__':
    monthly_report()
```

### Example 2: Trend Analysis Over Time

Compare assessments across multiple time periods:

```python
def trend_analysis():
    """Compare assessments over time."""
    import matplotlib.pyplot as plt

    # Load multiple assessments
    periods = ['2025-01', '2025-02', '2025-03']
    trends = []

    for period in periods:
        df = pd.read_csv(f'output/monthly/{period}/assessment_{period}.csv')

        avg_scores = {
            'period': period,
            'business_value': df['Business Value'].mean(),
            'tech_health': df['Tech Health'].mean(),
            'security': df['Security'].mean(),
            'composite': df['Composite Score'].mean()
        }

        trends.append(avg_scores)

    trend_df = pd.DataFrame(trends)

    # Plot trends
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(trend_df['period'], trend_df['business_value'], marker='o', label='Business Value')
    ax.plot(trend_df['period'], trend_df['tech_health'], marker='s', label='Tech Health')
    ax.plot(trend_df['period'], trend_df['security'], marker='^', label='Security')

    ax.set_xlabel('Period')
    ax.set_ylabel('Average Score')
    ax.set_title('Application Portfolio Trends')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('output/trends.png', dpi=300)

    print("Trend analysis complete")
```

### Example 3: Custom Multi-Organization Dashboard

Create dashboards for multiple business units:

```python
def multi_org_dashboard(df, org_column='Owner'):
    """Create separate dashboards for each organization."""
    from src.visualizations import VisualizationEngine

    organizations = df[org_column].unique()

    for org in organizations:
        # Filter data for this organization
        org_df = df[df[org_column] == org]

        # Create organization-specific output directory
        output_dir = Path(f'output/organizations/{org}')

        # Initialize viz engine
        viz = VisualizationEngine(output_dir=output_dir)

        # Create all visualizations
        viz.create_score_heatmap(
            org_df,
            title=f'{org} - Application Scores'
        )

        viz.create_time_quadrant_heatmap(
            org_df,
            title=f'{org} - TIME Framework Analysis'
        )

        viz.create_comprehensive_dashboard(
            org_df,
            title=f'{org} - Portfolio Dashboard'
        )

        print(f"Dashboard created for {org}")
```

### Example 4: Integration with Jira/ServiceNow

Export recommendations as tickets:

```python
def export_to_tickets(df):
    """Generate ticket data from recommendations."""

    # Filter high-priority actions
    urgent = df[
        (df['Composite Score'] < 40) |
        (df['Action Recommendation'] == 'Immediate Action Required')
    ].copy()

    # Create ticket data
    tickets = []
    for _, app in urgent.iterrows():
        ticket = {
            'summary': f"Address {app['Application Name']} - {app['Action Recommendation']}",
            'description': f"""
Application: {app['Application Name']}
Owner: {app.get('Owner', 'Unknown')}
Composite Score: {app['Composite Score']:.1f}/100
TIME Category: {app.get('TIME Category', 'N/A')}

Recommended Action: {app['Action Recommendation']}

Rationale: {app.get('TIME Rationale', 'See assessment for details')}

Scores:
- Business Value: {app['Business Value']}/10
- Tech Health: {app['Tech Health']}/10
- Security: {app['Security']}/10
            """,
            'priority': 'High' if app['Composite Score'] < 30 else 'Medium',
            'labels': ['application-rationalization', app.get('TIME Category', '').lower()]
        }
        tickets.append(ticket)

    # Save as CSV for import
    tickets_df = pd.DataFrame(tickets)
    tickets_df.to_csv('output/tickets_import.csv', index=False)

    print(f"Generated {len(tickets)} tickets for import")
```

---

## Additional Resources

### Related Documentation
- [Workflow Guide](workflow.md) - Complete assessment workflow
- [TIME Framework Guide](time_framework.md) - TIME framework details
- [Configuration Guide](configuration.md) - Customizing scoring weights

### External Resources
- [Matplotlib Documentation](https://matplotlib.org/stable/contents.html)
- [Seaborn Gallery](https://seaborn.pydata.org/examples/index.html)
- [Power BI Documentation](https://docs.microsoft.com/en-us/power-bi/)
- [OpenPyXL Documentation](https://openpyxl.readthedocs.io/)

### Support
- GitHub Issues: https://github.com/yourusername/application-rationalization-tool/issues
- Documentation: https://github.com/yourusername/application-rationalization-tool/docs

---

*Last Updated: 2025*
