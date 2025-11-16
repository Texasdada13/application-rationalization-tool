# Application Rationalization Assessment Tool

A comprehensive Python-based tool for evaluating and rationalizing software application portfolios. This tool helps organizations make data-driven decisions about their application landscape by calculating composite scores and generating actionable recommendations.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Assessment Criteria](#assessment-criteria)
- [Recommendation Actions](#recommendation-actions)
- [Project Structure](#project-structure)
- [Advanced Usage](#advanced-usage)
- [Customization](#customization)
- [Contributing](#contributing)
- [License](#license)

## Overview

Managing a large application portfolio is challenging. This tool automates the assessment process by:

1. **Evaluating applications** across multiple dimensions (business value, technical health, cost, etc.)
2. **Calculating composite scores** using weighted criteria
3. **Generating recommendations** (Retain, Invest, Migrate, Retire, etc.)
4. **Providing actionable insights** for portfolio optimization

The tool is designed for IT leaders, enterprise architects, and portfolio managers who need to make informed decisions about application rationalization.

## Features

### Core Assessment
- **Multi-Criteria Scoring**: Evaluates applications across 7 key dimensions
- **TIME Framework Integration**: Industry-standard Tolerate/Invest/Migrate/Eliminate categorization
- **Flexible Weighting**: Customize scoring weights to match organizational priorities
- **Smart Recommendations**: AI-driven recommendation engine with detailed rationale
- **Data Validation**: Built-in validation to ensure data quality
- **Summary Statistics**: Portfolio-level insights and trends

### Visualization & Reporting (NEW! 🎨)
- **Professional Heatmaps**: Application score matrices across all dimensions
- **TIME Quadrant Charts**: Strategic positioning visualizations
- **Priority Matrices**: Multi-dimensional bubble charts for prioritization
- **Distribution Analysis**: Score distribution plots and trends
- **Executive Dashboards**: Comprehensive multi-panel visualizations
- **Multiple Styles**: Professional, Presentation, and Technical themes

### Export Formats (NEW! 📊)
- **Power BI-Optimized Excel**: Multi-sheet workbooks with proper table relationships
- **Enhanced Excel Reports**: Formatted reports with charts and conditional formatting
- **CSV Export**: Simple, portable data format
- **Executive Summaries**: Dashboard sheets with key metrics

### Tools & Integration
- **CLI Interface**: Command-line tools for batch processing and automation
- **Python API**: Programmatic access for custom workflows
- **Quick Helpers**: One-line functions for rapid analysis
- **Extensible Architecture**: Modular design for easy customization
- **Configurable Thresholds**: Customize TIME framework thresholds for your organization

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository:**

```bash
git clone https://github.com/Texasdada13/application-rationalization-tool.git
cd application-rationalization-tool
```

2. **Create a virtual environment (recommended):**

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

## Quick Start

1. **Prepare your data:**

   Edit `data/assessment_template.csv` with your application portfolio data. The template includes sample data to get you started.

2. **Run the assessment:**

```bash
python main.py
```

3. **Review results:**

   Results are saved to:
   - `output/assessment_results_TIMESTAMP.csv`
   - `output/assessment_results_TIMESTAMP.xlsx`

That's it! The tool will calculate scores, generate recommendations, and provide a detailed summary.

## Configuration

The tool uses a flexible configuration system that allows you to customize scoring weights, TIME framework thresholds, and other settings.

### Configuration Files

**config/config.yaml** - Global default configuration
**config/config.local.yaml** - User-specific overrides (gitignored)

Configuration is loaded in cascading order:
1. Built-in defaults
2. `config/config.yaml` (if exists)
3. `config/config.local.yaml` (if exists)
4. Runtime parameters

### Customizing Scoring Weights

Edit `config/config.yaml` to customize how criteria are weighted:

```yaml
scoring_weights:
  business_value: 0.25    # 25% - Business impact
  tech_health: 0.20       # 20% - Technical health
  cost: 0.15              # 15% - Annual cost (lower is better)
  usage: 0.15             # 15% - Active usage
  security: 0.10          # 10% - Security posture
  strategic_fit: 0.10     # 10% - Strategic alignment
  redundancy: 0.05        # 5% - Redundancy penalty
```

**All weights must sum to 1.0 (100%)**

### Example Configurations

**Security-First Organization:**
```yaml
scoring_weights:
  security: 0.25          # Increased from 0.10
  business_value: 0.20
  tech_health: 0.20
  # ... adjust others to sum to 1.0
```

**Cost Reduction Initiative:**
```yaml
scoring_weights:
  cost: 0.30              # Increased from 0.15
  business_value: 0.20
  tech_health: 0.15
  # ... adjust others to sum to 1.0
```

### Creating Custom Configuration

```bash
# Copy example to create your config
cp config/config.example.yaml config/config.yaml

# Or create user-specific config (gitignored)
cp config/config.example.yaml config/config.local.yaml
```

### Viewing Current Configuration

```bash
# Display current configuration
python -c "from src.config_loader import load_config; print(load_config().display_current_config())"
```

**See `docs/configuration_guide.md` for complete configuration documentation.**

## Usage

### Basic Usage

Run the main script to process the default template:

```bash
python main.py
```

### Command-Line Interface (CLI)

The tool includes a powerful CLI for advanced operations:

#### Run Assessment

```bash
# Assess a CSV file
python -m src.cli assess -i data/assessment_template.csv -o output/results.csv

# Assess and output to Excel
python -m src.cli assess -i data/mydata.csv -o output/results.xlsx -f excel

# Without timestamp in filename
python -m src.cli assess -i data/mydata.csv --no-timestamp
```

#### List Applications

```bash
# List all applications
python -m src.cli list-apps -i output/results.csv

# Filter by action recommendation
python -m src.cli list-apps -i output/results.csv -a Retire

# Filter by score range
python -m src.cli list-apps -i output/results.csv --min-score 60 --max-score 80

# Show top 5 applications
python -m src.cli list-apps -i output/results.csv -t 5
```

#### Portfolio Summary

```bash
# Display summary statistics
python -m src.cli summary -i output/results.csv
```

#### Create Visualizations (NEW!)

```bash
# Create all visualizations
python -m src.cli visualize -i output/results.csv

# Create specific visualization type
python -m src.cli visualize -i output/results.csv -t heatmap
python -m src.cli visualize -i output/results.csv -t time-quadrant
python -m src.cli visualize -i output/results.csv -t dashboard

# Specify output directory
python -m src.cli visualize -i output/results.csv -o output/my_visuals/

# Use different style
python -m src.cli visualize -i output/results.csv --style presentation
```

**Available visualization types:**
- `heatmap` - Application score heatmap
- `time-quadrant` - TIME framework quadrant chart
- `priority-matrix` - Priority bubble chart
- `distributions` - Score distribution plots
- `time-summary` - TIME category summary
- `dashboard` - Comprehensive dashboard
- `all` - All visualizations (default)

**Available styles:**
- `professional` - Clean, business-focused (default)
- `presentation` - Bold, high contrast for slides
- `technical` - Detailed, precise for analysis

#### Export Data (NEW!)

```bash
# Enhanced Excel export (with formatting and charts)
python -m src.cli export -i output/results.csv -o output/report.xlsx

# Power BI-optimized export
python -m src.cli export -i output/results.csv -f powerbi -o output/powerbi.xlsx

# Create both formats
python -m src.cli export -i output/results.csv -f both

# Without charts (smaller file size)
python -m src.cli export -i output/results.csv --no-charts

# Without timestamp
python -m src.cli export -i output/results.csv --no-timestamp
```

**Export format options:**
- `excel-enhanced` - Professional Excel with formatting and charts (default)
- `powerbi` - Power BI-optimized with normalized tables
- `both` - Create both formats

#### Help

```bash
# Show all available commands
python -m src.cli --help

# Help for specific command
python -m src.cli assess --help
python -m src.cli visualize --help
python -m src.cli export --help
```

## Assessment Criteria

The tool evaluates applications across 7 key criteria:

| Criterion | Scale | Weight | Description |
|-----------|-------|--------|-------------|
| **Business Value** | 0-10 | 25% | Value delivered to the business |
| **Tech Health** | 0-10 | 20% | Technical condition and maintainability |
| **Cost** | Dollars | 15% | Annual operating cost (normalized) |
| **Usage** | Count | 15% | Active users or usage metrics |
| **Security** | 0-10 | 10% | Security posture and compliance |
| **Strategic Fit** | 0-10 | 10% | Alignment with strategy |
| **Redundancy** | 0 or 1 | 5% | Whether functionality is duplicated |

### Composite Score Calculation

The composite score (0-100) is calculated as:

```
Composite Score = (
    Business Value × 0.25 +
    Tech Health × 0.20 +
    Cost Score × 0.15 +
    Usage Score × 0.15 +
    Security × 0.10 +
    Strategic Fit × 0.10 +
    Redundancy Score × 0.05
) × 10
```

## Recommendation Actions

The recommendation engine generates one of 8 possible actions:

### Retain
**High-performing applications that should continue as-is**
- Composite Score: ≥70
- Strong balanced metrics
- Action: Continue current operations

### Invest
**Strategic applications requiring additional investment**
- High strategic fit and business value
- Opportunity for enhancement
- Action: Increase funding/resources

### Maintain
**Stable applications requiring routine maintenance**
- Composite Score: 50-70
- Good technical health
- Action: Standard maintenance and updates

### Tolerate
**Acceptable applications with limitations**
- Moderate scores
- Critical business function or acceptable for now
- Action: Monitor and reassess

### Migrate
**Applications requiring modernization**
- Critical business value but poor technical health
- High strategic value but low composite score
- Action: Plan migration to modern platform

### Consolidate
**Redundant applications that should be merged**
- Redundancy flag = 1
- Duplicate functionality exists
- Action: Merge with primary system

### Retire
**Applications that should be decommissioned**
- Composite Score: <30
- Low business value
- Poor technical health
- Action: Plan retirement

### Immediate Action Required
**Critical risk applications**
- Poor security with high business value
- Urgent remediation needed
- Action: Immediate intervention

## TIME Framework

The tool integrates the industry-standard **TIME Framework** (Tolerate, Invest, Migrate, Eliminate) for portfolio categorization.

### TIME Categories

```
                    Technical Quality
                    Low    →    High
                  ┌────────┬────────┐
    Business      │TOLERATE│ INVEST │
    Value    High │        │        │
                  ├────────┼────────┤
             Low  │ELIM-   │ MIGRATE│
                  │INATE   │        │
                  └────────┴────────┘
```

**INVEST** - High business value, high technical quality
- Continue investment for growth
- Strategic applications with good health
- Maximize returns through enhancement

**TOLERATE** - High business value, low technical quality
- Maintain while planning improvements
- Business-critical but aging
- Manage technical debt and risk

**MIGRATE** - Low business value OR misaligned
- Plan consolidation or modernization
- Good tech but limited business value
- Evaluate repurposing opportunities

**ELIMINATE** - Low business value, low technical quality
- Retire or decommission
- Minimal business impact
- Reduce technical debt and costs

### Using TIME Framework

The TIME framework is automatically applied during assessment:

```bash
# Run assessment (TIME categories included automatically)
python main.py

# Filter by TIME category
python -m src.cli list-apps -i output/results.csv -tc Invest
python -m src.cli list-apps -i output/results.csv -tc Eliminate
```

### TIME Configuration

Customize thresholds in `config/time_config.yaml`:

```yaml
time_thresholds:
  business_value_threshold: 6.0      # High BV cutoff (0-10)
  technical_quality_threshold: 6.0    # High TQ cutoff (0-10)
  composite_score_high: 65.0          # High performer (0-100)
  composite_score_low: 40.0           # Low performer (0-100)
```

**See `docs/time_framework.md` for complete TIME framework documentation.**

## Project Structure

```
application-rationalization-tool/
├── data/
│   └── assessment_template.csv    # Sample input data with 30 applications
├── src/
│   ├── __init__.py               # Package initialization
│   ├── scoring_engine.py         # Composite score calculation
│   ├── data_handler.py           # CSV/Excel I/O and advanced exports
│   ├── recommendation_engine.py  # Recommendation logic
│   ├── time_framework.py         # TIME framework categorization
│   ├── config_loader.py          # Configuration management
│   ├── visualizations.py         # Visualization engine (NEW!)
│   └── cli.py                    # Command-line interface
├── docs/
│   ├── workflow.md               # Detailed workflow documentation
│   ├── scoring_methodology.md    # Scoring approach details
│   ├── time_framework.md         # TIME framework guide
│   ├── configuration.md          # Configuration guide
│   └── visualization_guide.md    # Visualization & export guide (NEW!)
├── examples/
│   ├── basic_example.py          # Basic usage example
│   ├── visualization_example.py  # Visualization examples (NEW!)
│   └── export_example.py         # Export examples (NEW!)
├── output/                       # Generated assessment results
│   ├── visualizations/           # Generated charts and graphs (NEW!)
│   └── exports/                  # Enhanced Excel and Power BI exports (NEW!)
├── config/                       # Configuration files
│   ├── config.example.yaml       # Example configuration
│   └── time_config.yaml          # TIME framework thresholds
├── tests/                        # Unit tests (future)
├── main.py                       # Main entry point
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Advanced Usage

### Custom Scoring Weights

Modify scoring weights to match your organization's priorities:

```python
from src.scoring_engine import ScoringEngine, ScoringWeights

# Create custom weights
custom_weights = ScoringWeights(
    business_value=0.30,    # Increase business value importance
    tech_health=0.25,       # Increase tech health importance
    cost=0.15,
    usage=0.10,
    security=0.10,
    strategic_fit=0.08,
    redundancy=0.02
)

# Use custom weights
engine = ScoringEngine(weights=custom_weights)
```

### Programmatic Usage

Use the tool as a library in your own scripts:

```python
from pathlib import Path
from src.data_handler import DataHandler
from src.scoring_engine import ScoringEngine
from src.recommendation_engine import RecommendationEngine

# Initialize
data_handler = DataHandler()
scoring_engine = ScoringEngine()
recommendation_engine = RecommendationEngine()

# Load data
df = data_handler.read_csv('data/myapps.csv')

# Process
applications = df.to_dict('records')
scored = scoring_engine.batch_calculate_scores(applications)
results = recommendation_engine.batch_generate_recommendations(scored)

# Save
data_handler.write_excel(results, 'output/custom_results.xlsx')
```

### Batch Processing

Process multiple portfolios:

```bash
for file in data/*.csv; do
    python -m src.cli assess -i "$file" -o "output/$(basename $file)"
done
```

### Visualization and Export Usage (NEW!)

#### Creating Visualizations Programmatically

```python
from src.visualizations import VisualizationEngine, quick_visualize
from pathlib import Path
import pandas as pd

# Method 1: Using VisualizationEngine for full control
viz_engine = VisualizationEngine(
    output_dir=Path('output/visualizations'),
    style='professional'  # or 'presentation' or 'technical'
)

df = pd.read_csv('output/results.csv')

# Create individual visualizations
heatmap = viz_engine.create_score_heatmap(df, max_apps=20)
quadrant = viz_engine.create_time_quadrant_heatmap(df, show_labels=True)
matrix = viz_engine.create_priority_matrix(df)
dashboard = viz_engine.create_comprehensive_dashboard(df)

# Method 2: Quick visualization (all at once)
viz_paths = quick_visualize(
    input_file='output/results.csv',
    output_dir='output/visualizations',
    viz_types=['time_quadrant', 'dashboard', 'time_summary']
)
```

#### Creating Exports Programmatically

```python
from src.data_handler import DataHandler
import pandas as pd

data_handler = DataHandler()
df = pd.read_csv('output/results.csv')

# Power BI-optimized export
powerbi_path = data_handler.export_for_powerbi(
    df,
    output_path='output/powerbi_export.xlsx',
    include_timestamp=True
)

# Enhanced Excel with formatting and charts
excel_path = data_handler.export_enhanced_excel(
    df,
    output_path='output/executive_report.xlsx',
    include_timestamp=True,
    include_charts=True  # Set to False for smaller files
)
```

#### Complete Workflow Example

```python
from pathlib import Path
from src.data_handler import DataHandler
from src.scoring_engine import ScoringEngine
from src.recommendation_engine import RecommendationEngine
from src.time_framework import TIMEFramework
from src.visualizations import quick_visualize

# 1. Load and process data
data_handler = DataHandler()
df = data_handler.read_csv('data/assessment_template.csv')

# 2. Run assessment
scoring = ScoringEngine()
recommendations = RecommendationEngine()
time_framework = TIMEFramework()

apps = df.to_dict('records')
apps = scoring.batch_calculate_scores(apps)
apps = recommendations.batch_generate_recommendations(apps)
apps = time_framework.batch_categorize(apps)

results_df = pd.DataFrame(apps)

# 3. Save CSV results
csv_path = data_handler.write_csv(results_df, 'output/results.csv')

# 4. Create all visualizations
viz_paths = quick_visualize(csv_path, output_dir='output/visualizations')

# 5. Create Power BI export for analysts
powerbi_path = data_handler.export_for_powerbi(
    results_df,
    'output/powerbi_export.xlsx'
)

# 6. Create executive report
excel_path = data_handler.export_enhanced_excel(
    results_df,
    'output/executive_report.xlsx',
    include_charts=True
)

print(f"Assessment complete!")
print(f"  CSV: {csv_path}")
print(f"  Visualizations: {len(viz_paths)} charts created")
print(f"  Power BI: {powerbi_path}")
print(f"  Executive Report: {excel_path}")
```

#### Visualization Examples

See `examples/visualization_example.py` for 8 detailed examples including:
- Basic score heatmaps
- TIME framework quadrants
- Priority matrices
- Distribution analysis
- TIME category summaries
- Comprehensive dashboards
- Quick visualization helper
- Custom styling

Run the examples:
```bash
python examples/visualization_example.py
python examples/export_example.py
```

**For complete visualization and export documentation, see `docs/visualization_guide.md`**

## Customization

### Adding New Criteria

1. Update `REQUIRED_COLUMNS` in `src/data_handler.py`
2. Add weight in `src/scoring_engine.py`
3. Update calculation in `calculate_composite_score()`
4. Adjust recommendation logic in `src/recommendation_engine.py`

### Custom Recommendation Logic

Modify `_apply_decision_logic()` in `src/recommendation_engine.py` to implement custom business rules.

### Output Formatting

Customize output formatting in `src/data_handler.py`:
- Add conditional formatting for Excel
- Include charts and visualizations
- Generate PDF reports

## Next Steps

Planned enhancements:

- **Web Dashboard**: Interactive web UI for portfolio visualization
- **REST API**: API endpoints for integration with other tools
- **Machine Learning**: Predictive analytics for portfolio trends
- **Advanced Analytics**: TCO analysis, ROI projections
- **Integration**: Connectors for ServiceNow, JIRA, etc.
- **Reporting**: Automated PDF/PowerPoint report generation
- **Version Control**: Track portfolio changes over time

## Data Privacy

This tool processes data locally. No data is sent to external services. All assessment data remains within your environment.

## Troubleshooting

### Import Errors

If you encounter import errors:

```bash
# Ensure you're in the project root directory
cd application-rationalization-tool

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Missing Data File

Ensure `data/assessment_template.csv` exists:

```bash
ls -la data/assessment_template.csv
```

### Permission Errors

Ensure the `output/` directory is writable:

```bash
chmod 755 output/
```

## Support

For issues, questions, or contributions:

- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions
- **Email**: Contact the development team

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Acknowledgments

Built with:
- **pandas** - Data manipulation and analysis
- **openpyxl** - Excel file handling with advanced formatting
- **click** - CLI framework
- **tabulate** - Table formatting
- **matplotlib** - Professional chart generation
- **seaborn** - Statistical visualizations
- **numpy** - Numerical computing

---

**Version**: 1.0.0
**Last Updated**: November 2025
**Author**: Application Rationalization Team
