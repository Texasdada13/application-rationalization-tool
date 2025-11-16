# Stakeholder Survey Integration Guide

## Overview

The Stakeholder Survey Integration feature allows you to incorporate qualitative stakeholder feedback into your application rationalization assessments. By combining stakeholder surveys with quantitative metrics, you can:

- **Capture stakeholder sentiment** and opinions about applications
- **Merge qualitative and quantitative data** to create more holistic assessments
- **Identify discrepancies** between technical metrics and user perceptions
- **Measure stakeholder consensus** on application value and quality
- **Make data-driven decisions** that balance technical and business perspectives

## Table of Contents

1. [Survey Data Format](#survey-data-format)
2. [Workflow Overview](#workflow-overview)
3. [Data Import and Validation](#data-import-and-validation)
4. [Response Aggregation](#response-aggregation)
5. [Merging Survey with Assessment](#merging-survey-with-assessment)
6. [Survey Impact Analysis](#survey-impact-analysis)
7. [Reporting and Visualization](#reporting-and-visualization)
8. [Best Practices](#best-practices)
9. [CLI Command Reference](#cli-command-reference)
10. [Python API Reference](#python-api-reference)

---

## Survey Data Format

### Required Columns

Your survey CSV file must include these columns:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| Application Name | String | Name of the application (must match assessment data) | "Customer Portal" |
| Stakeholder Name | String | Name of the survey respondent | "John Smith" |
| Stakeholder Role | String | Job title or role of respondent | "VP Sales" |
| Survey Date | Date | Date survey was completed | "2025-01-10" |

### Rating Columns (Optional but Recommended)

All ratings use a **1-5 scale** where:
- 1 = Strongly Disagree / Very Low
- 5 = Strongly Agree / Very High

| Column | Description | Survey Question |
|--------|-------------|----------------|
| Critical to Business | How critical is this application to business operations? | "This application is critical to business operations" |
| Easy to Replace | How easy would it be to replace this application? | "This application could be easily replaced" |
| User Satisfaction | How satisfied are users with this application? | "Users are satisfied with this application" |
| Performance Rating | How would you rate the application's performance? | "This application performs well" |
| Strategic Importance | How strategically important is this application? | "This application aligns with our strategic goals" |

### Qualitative Feedback (Optional)

| Column | Type | Description |
|--------|------|-------------|
| Qualitative Feedback | Text | Open-ended stakeholder comments and observations |

### Example Survey Data

```csv
Application Name,Stakeholder Name,Stakeholder Role,Survey Date,Critical to Business,Easy to Replace,User Satisfaction,Performance Rating,Strategic Importance,Qualitative Feedback
Customer Portal,John Smith,VP Sales,2025-01-10,5,2,5,4,5,"Essential for customer engagement. Performance could be better during peak hours."
Customer Portal,Sarah Johnson,Customer Service Manager,2025-01-10,5,1,4,4,5,"Critical for our daily operations. Users love the self-service features."
Legacy Billing System,Robert Davis,CFO,2025-01-10,5,1,2,2,3,"Absolutely critical but outdated. Replacement is urgent priority."
```

### Creating Your Survey Template

Use the provided template:
```bash
cp data/sample_survey.csv data/my_survey.csv
# Edit my_survey.csv with your survey data
```

---

## Workflow Overview

The survey integration workflow consists of five main steps:

```
1. COLLECT SURVEYS           2. IMPORT & VALIDATE      3. AGGREGATE RESPONSES
   ┌─────────────┐              ┌─────────────┐           ┌─────────────┐
   │  Survey     │              │   Validate  │           │  Multiple   │
   │  Responses  │──────────────│   Data      │───────────│  Responses  │
   │  (CSV)      │              │   Format    │           │  Per App    │
   └─────────────┘              └─────────────┘           └─────────────┘
                                                                 │
4. MERGE WITH ASSESSMENT     5. GENERATE REPORTS                │
   ┌─────────────┐              ┌─────────────┐                 │
   │  Combine    │◄─────────────│   Survey    │                 │
   │  Quant &    │              │  Analysis   │                 │
   │  Qual Data  │              │   Report    │                 │
   └─────────────┘              └─────────────┘                 │
         │                            │                          │
         └────────────────────────────┴──────────────────────────┘
                           INSIGHTS & DECISIONS
```

### Step-by-Step Process

1. **Collect Surveys**: Distribute surveys to stakeholders and collect responses in CSV format
2. **Import & Validate**: Load survey data and validate for completeness
3. **Aggregate Responses**: Combine multiple stakeholder responses per application
4. **Merge with Assessment**: Combine survey data with quantitative assessment scores
5. **Generate Reports**: Create comprehensive analysis reports with insights

---

## Data Import and Validation

### Importing Survey Data

**Using Python API:**

```python
from src.data_handler import DataHandler

handler = DataHandler()

# Import survey data
survey_df = handler.read_survey_data('data/my_survey.csv')
print(f"Loaded {len(survey_df)} survey responses")

# Validate survey data
is_valid, errors = handler.validate_survey_data(survey_df)
if not is_valid:
    for error in errors:
        print(f"Warning: {error}")
```

**Using CLI:**

```bash
# The import-survey command automatically validates
python -m src.cli import-survey \
    --input data/my_survey.csv \
    --output output/survey_aggregated.csv
```

### Validation Checks

The validation process checks for:

- ✅ Required columns present (Application Name, Stakeholder Name, Role, Date)
- ✅ No empty application names or stakeholder names
- ✅ Rating values within valid range (1-5)
- ✅ Valid survey dates
- ⚠️ Warnings for missing or incomplete data (doesn't block import)

---

## Response Aggregation

When multiple stakeholders provide feedback for the same application, responses must be aggregated into single scores.

### Aggregation Methods

**1. Mean (Default)**
- Calculates the average of all stakeholder ratings
- Best for: Most use cases, balanced approach
```python
aggregated = handler.aggregate_survey_responses(survey_df, method='mean')
```

**2. Median**
- Uses the middle value when ratings are sorted
- Best for: Reducing impact of outliers
```python
aggregated = handler.aggregate_survey_responses(survey_df, method='median')
```

**3. Weighted** (Future Enhancement)
- Weights responses by stakeholder seniority or importance
- Best for: When some stakeholders' opinions should carry more weight

### Consensus Metrics

The aggregation process calculates **consensus metrics** to measure stakeholder agreement:

- **Overall Consensus Score** (1-5): High score = high agreement among stakeholders
  - Score ≥ 4: Strong consensus
  - Score 3-4: Moderate consensus
  - Score < 3: Divergent opinions

- **Individual Metric Consensus**: Standard deviation for each rating dimension

### Example

```python
# Aggregate with mean method
aggregated_df = handler.aggregate_survey_responses(survey_df, method='mean')

# View results
print(aggregated_df[['Application Name', 'Survey Response Count',
                     'Critical to Business', 'Overall Consensus Score']])
```

**Output:**
```
Application Name           Survey Response Count  Critical to Business  Overall Consensus Score
Customer Portal            3                      4.67                  4.2
Legacy Billing System      3                      5.00                  4.5
CRM System                 3                      5.00                  4.8
```

**Interpretation:**
- Customer Portal: 3 responses, average criticality 4.67/5, high consensus (4.2/5)
- CRM System: Perfect consensus (4.8/5) - all stakeholders agree

---

## Merging Survey with Assessment

### Survey Weighting

When merging, you specify a **survey weight** (0-1) that determines how much influence survey data has on final scores:

- **0.3 (30%)** - Recommended default: Balanced approach
- **0.5 (50%)** - Equal weight to quantitative and qualitative
- **0.2 (20%)** - More trust in quantitative metrics
- **0.4 (40%)** - More trust in stakeholder feedback

### Score Adjustment Formula

For each metric, the survey-adjusted score is calculated as:

```
Adjusted Score = (Quantitative Score × (1 - Weight)) + (Survey Score × Weight)
```

Example with 30% weight:
```
Original Business Value: 7.0
Survey Critical Rating:  5.0 → Scaled to 10.0 (1-5 scale → 0-10 scale)

Survey Adjusted = (7.0 × 0.7) + (10.0 × 0.3)
                = 4.9 + 3.0
                = 7.9
```

### Metric Mapping

Survey ratings map to assessment dimensions:

| Survey Metric | Assessment Dimension | Scale Conversion |
|---------------|---------------------|------------------|
| Critical to Business | Business Value | (Rating - 1) × 2.5 |
| User Satisfaction | Usage | (Rating - 1) × 2.5 |
| Performance Rating | Tech Health | (Rating - 1) × 2.5 |
| Strategic Importance | Strategic Fit | (Rating - 1) × 2.5 |

### Variance Analysis

The merge process calculates **variance** for each dimension:

```
Variance = Survey Score (scaled) - Quantitative Score
```

- **Positive variance**: Stakeholders rate higher than metrics suggest
- **Negative variance**: Metrics rate higher than stakeholders perceive
- **High variance (|variance| > 2)**: Significant discrepancy requiring investigation

### Python Example

```python
# Merge with 30% survey weight
merged_df = handler.merge_survey_with_assessment(
    assessment_df=assessment_results,
    survey_df=aggregated_survey,
    survey_weight=0.3
)

# View merged results
cols = ['Application Name', 'Business Value Original',
        'Business Value Survey Adjusted', 'Business Value Variance']
print(merged_df[cols])
```

### CLI Example

```bash
python -m src.cli merge-survey-data \
    --assessment output/assessment_results.csv \
    --survey output/survey_aggregated.csv \
    --output output/merged_results.csv \
    --survey-weight 0.3
```

---

## Survey Impact Analysis

### Impact Metrics

The impact analysis provides insights into how survey data affects assessments:

#### 1. Variance Summary
Statistical summary of differences between quantitative and qualitative scores:
- Mean variance per dimension
- Maximum positive/negative variance
- Standard deviation of variance

#### 2. Consensus Summary
Stakeholder agreement metrics:
- Average consensus score across all applications
- Count of high consensus applications (score ≥ 4)
- Count of low consensus applications (score < 3)

#### 3. Sentiment Analysis
Categorizes applications by stakeholder sentiment:
- **High Value & Satisfaction**: Keep and invest
- **High Value but Poor Satisfaction**: Critical but needs improvement
- **Low Value but High Satisfaction**: Good UX but questionable ROI
- **Low Value & Satisfaction**: Candidates for elimination

#### 4. High Variance Applications
Applications where survey ratings significantly differ from quantitative scores (|variance| > 2):
- Indicates discrepancy between metrics and stakeholder perception
- Requires investigation and potential score adjustment

#### 5. Needs Attention
Applications that are:
- Critical to business (rating ≥ 4)
- Low user satisfaction (rating < 3)

These are priority candidates for improvement investments.

### Python Example

```python
impact = handler.calculate_survey_impact(merged_df)

# View variance summary
if 'variance_summary' in impact:
    for metric, stats in impact['variance_summary'].items():
        print(f"{metric}: mean={stats['mean']:.2f}, std={stats['std']:.2f}")

# View sentiment distribution
if 'sentiment_analysis' in impact:
    for category, count in impact['sentiment_analysis'].items():
        print(f"{category}: {count} apps")

# View apps needing attention
if 'needs_attention' in impact:
    print(f"Priority interventions: {len(impact['needs_attention'])} apps")
```

---

## Reporting and Visualization

### Survey Analysis Excel Report

The comprehensive Excel report includes multiple worksheets:

#### Sheet 1: Survey Analysis
- Application name
- Original quantitative scores
- Survey-adjusted scores
- Variance metrics
- Survey ratings
- Consensus scores
- Qualitative feedback

#### Sheet 2: High Variance
- Applications with significant discrepancies
- Variance by dimension
- Response count

#### Sheet 3: Impact Summary
- Variance statistics
- Consensus metrics
- Sentiment distribution

#### Sheet 4: Needs Attention
- Critical apps with low satisfaction
- Stakeholder feedback
- Recommended actions

#### Sheet 5: Qualitative Feedback
- All stakeholder comments by application
- Response counts
- Searchable and filterable

### Generating Reports

**Using Python:**

```python
report_path = handler.export_survey_analysis(
    merged_df,
    output_path='output/survey_analysis.xlsx',
    include_timestamp=True
)
print(f"Report saved to: {report_path}")
```

**Using CLI:**

```bash
python -m src.cli generate-survey-report \
    --input output/merged_results.csv \
    --output output/survey_analysis.xlsx
```

### Report Features

- ✅ Professional formatting with color-coded headers
- ✅ Auto-adjusted column widths
- ✅ Multiple worksheets for different analyses
- ✅ Sortable and filterable data
- ✅ Timestamp in filename for version control

---

## Best Practices

### Survey Design

1. **Keep it Short**: 5-10 questions maximum to ensure completion
2. **Use Consistent Scales**: Stick to 1-5 scale for all rating questions
3. **Include Open-Ended**: Always have a qualitative feedback field
4. **Target the Right People**: Survey both users and IT stakeholders

### Data Collection

1. **Multiple Stakeholders per App**: Aim for 3-5 responses per application
2. **Diverse Perspectives**: Include different roles (users, IT, management)
3. **Recent Data**: Surveys should be conducted within 3-6 months of assessment
4. **Standardized Questions**: Use the same questions for all applications

### Analysis and Interpretation

1. **Check Consensus First**: Low consensus indicates need for deeper investigation
2. **Investigate High Variance**: Apps with |variance| > 2 warrant review
3. **Prioritize Needs Attention**: Critical apps with low satisfaction are high priority
4. **Read Qualitative Feedback**: Numbers don't tell the whole story
5. **Iterate**: Use findings to refine future assessments

### Survey Weighting

**Recommended Weights by Scenario:**

| Scenario | Recommended Weight | Rationale |
|----------|-------------------|-----------|
| First-time survey | 20-30% | Conservative approach, validate survey quality |
| Established survey process | 30-40% | Balanced quantitative/qualitative |
| User-facing applications | 35-45% | User satisfaction matters more |
| Infrastructure apps | 20-30% | Technical metrics more reliable |
| Regulatory/compliance apps | 25-35% | Balance risk metrics with user input |

### Handling Discrepancies

When survey data significantly differs from quantitative scores:

1. **Investigate Root Cause**: Why do stakeholders perceive differently?
2. **Validate Metrics**: Are quantitative scores accurate and current?
3. **Gather Context**: Interview stakeholders for deeper understanding
4. **Adjust Weights**: Consider different weights for different app types
5. **Update Scores**: Use insights to refine quantitative assessments

---

## CLI Command Reference

### import-survey

Import and aggregate stakeholder survey data.

```bash
python -m src.cli import-survey [OPTIONS]
```

**Options:**
- `--input, -i`: Input survey CSV file (required)
- `--output, -o`: Output file for aggregated data (default: `output/survey_aggregated.csv`)
- `--method, -m`: Aggregation method: `mean`, `median`, or `weighted` (default: `mean`)

**Example:**
```bash
python -m src.cli import-survey \
    -i data/stakeholder_survey.csv \
    -o output/survey_agg.csv \
    -m mean
```

### merge-survey-data

Merge stakeholder survey data with quantitative assessment scores.

```bash
python -m src.cli merge-survey-data [OPTIONS]
```

**Options:**
- `--assessment, -a`: Assessment results CSV/Excel file (required)
- `--survey, -s`: Aggregated survey data CSV file (required)
- `--output, -o`: Output file for merged data (default: `output/merged_assessment.csv`)
- `--survey-weight, -w`: Survey weight 0-1 (default: 0.3)

**Example:**
```bash
python -m src.cli merge-survey-data \
    -a output/assessment_results.csv \
    -s output/survey_agg.csv \
    -o output/merged.csv \
    -w 0.3
```

### generate-survey-report

Generate comprehensive survey analysis Excel report.

```bash
python -m src.cli generate-survey-report [OPTIONS]
```

**Options:**
- `--input, -i`: Merged assessment CSV file (required)
- `--output, -o`: Output Excel file (default: `output/survey_analysis.xlsx`)
- `--timestamp/--no-timestamp`: Include timestamp in filename (default: yes)

**Example:**
```bash
python -m src.cli generate-survey-report \
    -i output/merged.csv \
    -o reports/survey_analysis.xlsx
```

---

## Python API Reference

### DataHandler.read_survey_data()

```python
def read_survey_data(file_path: Union[str, Path]) -> pd.DataFrame
```

Read stakeholder survey data from CSV file.

**Parameters:**
- `file_path`: Path to survey CSV file

**Returns:**
- DataFrame containing survey data

**Raises:**
- `FileNotFoundError`: If file doesn't exist
- `ValueError`: If required columns missing

### DataHandler.validate_survey_data()

```python
def validate_survey_data(survey_df: pd.DataFrame) -> tuple[bool, List[str]]
```

Validate survey data for completeness and correctness.

**Parameters:**
- `survey_df`: DataFrame containing survey data

**Returns:**
- Tuple of (is_valid, list_of_errors)

### DataHandler.aggregate_survey_responses()

```python
def aggregate_survey_responses(
    survey_df: pd.DataFrame,
    aggregation_method: str = 'mean'
) -> pd.DataFrame
```

Aggregate multiple stakeholder responses per application.

**Parameters:**
- `survey_df`: Raw survey data DataFrame
- `aggregation_method`: 'mean', 'median', or 'weighted'

**Returns:**
- DataFrame with one row per application

### DataHandler.merge_survey_with_assessment()

```python
def merge_survey_with_assessment(
    assessment_df: pd.DataFrame,
    survey_df: pd.DataFrame,
    survey_weight: float = 0.3
) -> pd.DataFrame
```

Merge survey data with quantitative assessment scores.

**Parameters:**
- `assessment_df`: Assessment results DataFrame
- `survey_df`: Aggregated survey DataFrame
- `survey_weight`: Weight for survey data (0-1)

**Returns:**
- DataFrame with merged data and adjusted scores

### DataHandler.calculate_survey_impact()

```python
def calculate_survey_impact(merged_df: pd.DataFrame) -> Dict
```

Analyze impact of survey data on assessment scores.

**Parameters:**
- `merged_df`: Merged assessment + survey DataFrame

**Returns:**
- Dictionary containing:
  - `variance_summary`: Statistics on score variances
  - `high_variance_apps`: Apps with significant differences
  - `consensus_summary`: Stakeholder agreement metrics
  - `sentiment_analysis`: Sentiment distribution
  - `needs_attention`: Critical apps with low satisfaction

### DataHandler.export_survey_analysis()

```python
def export_survey_analysis(
    merged_df: pd.DataFrame,
    output_path: Union[str, Path],
    include_timestamp: bool = True
) -> Path
```

Export survey analysis to multi-sheet Excel workbook.

**Parameters:**
- `merged_df`: Merged assessment + survey DataFrame
- `output_path`: Path for output Excel file
- `include_timestamp`: Whether to include timestamp in filename

**Returns:**
- Path to exported Excel file

---

## Complete Example Workflow

Here's a complete end-to-end example:

```python
from src.data_handler import DataHandler
from src.scoring_engine import ScoringEngine
from src.recommendation_engine import RecommendationEngine
from src.time_framework import TIMEFramework
import pandas as pd

# Initialize
handler = DataHandler()

# Step 1: Run quantitative assessment
print("Running assessment...")
assessment_df = handler.read_csv('data/applications.csv')
scoring = ScoringEngine()
recommendations = RecommendationEngine()
time_framework = TIMEFramework()

apps = assessment_df.to_dict('records')
scored = scoring.batch_calculate_scores(apps)
recommended = recommendations.batch_generate_recommendations(scored)
final = time_framework.batch_categorize(recommended)
assessment_results = pd.DataFrame(final)

# Step 2: Import and aggregate survey
print("Importing survey data...")
survey_df = handler.read_survey_data('data/stakeholder_survey.csv')
is_valid, errors = handler.validate_survey_data(survey_df)
aggregated_survey = handler.aggregate_survey_responses(survey_df, method='mean')

# Step 3: Merge data
print("Merging survey with assessment...")
merged_df = handler.merge_survey_with_assessment(
    assessment_results,
    aggregated_survey,
    survey_weight=0.3
)

# Step 4: Analyze impact
print("Analyzing survey impact...")
impact = handler.calculate_survey_impact(merged_df)

print(f"\nResults:")
print(f"  • {merged_df['Has Survey Data'].sum()} apps have survey data")
print(f"  • {len(impact.get('high_variance_apps', []))} high variance apps")
print(f"  • {len(impact.get('needs_attention', []))} apps need attention")

# Step 5: Export reports
print("\nGenerating reports...")
merged_df.to_csv('output/merged_assessment.csv', index=False)
report_path = handler.export_survey_analysis(
    merged_df,
    'output/survey_analysis.xlsx'
)
print(f"Survey analysis report: {report_path}")
```

---

## Troubleshooting

### Common Issues

**Issue: "Missing required survey columns"**
- **Solution**: Ensure CSV has: Application Name, Stakeholder Name, Stakeholder Role, Survey Date

**Issue: "No matching applications found"**
- **Solution**: Application names in survey must exactly match assessment data (case-sensitive)

**Issue: "Low consensus scores across all apps"**
- **Solution**: This may indicate:
  - Need for clearer survey questions
  - Genuinely divergent stakeholder opinions
  - Different stakeholder groups with different perspectives

**Issue: "All apps show high variance"**
- **Solution**: May indicate:
  - Quantitative metrics need updating
  - Survey scale interpretation issues
  - Need to adjust survey weight

### Getting Help

- Review example scripts in `examples/survey_integration_example.py`
- Check sample data format in `data/sample_survey.csv`
- See test script in root directory for validation

---

## Version History

- **v1.0** (2025-01): Initial release
  - Survey data import and validation
  - Response aggregation with consensus metrics
  - Survey-assessment merging with adjustable weights
  - Impact analysis and reporting
  - CLI commands and Python API
