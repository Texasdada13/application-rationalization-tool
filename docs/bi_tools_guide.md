# BI Tools Import Guide

## Table of Contents

1. [Overview](#overview)
2. [Power BI](#power-bi)
3. [Tableau](#tableau)
4. [Other BI Tools](#other-bi-tools)
5. [Best Practices](#best-practices)
6. [Sample Dashboards](#sample-dashboards)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The Application Rationalization Tool provides optimized exports for multiple BI platforms. This guide covers how to import and visualize your assessment data in popular business intelligence tools.

### Available Export Formats

| Format | Best For | Tools |
|--------|----------|-------|
| **Power BI Excel** | Interactive dashboards, drill-down | Power BI Desktop, Power BI Service |
| **Tableau CSV** | Advanced visualizations, Calculated fields | Tableau Desktop, Tableau Server |
| **Enhanced Excel** | Quick insights, Presentations | Excel, Google Sheets |
| **CSV** | General purpose, Custom tools | Any BI tool |

---

## Power BI

### 1. Exporting for Power BI

#### Using CLI:
```bash
python -m src.cli export -i results.csv -f powerbi -o powerbi_export.xlsx
```

#### Using Python:
```python
from src.data_handler import DataHandler

data_handler = DataHandler()
path = data_handler.export_for_powerbi(
    df,
    'powerbi_export.xlsx'
)
```

### 2. Importing into Power BI Desktop

**Step-by-Step Instructions:**

1. **Open Power BI Desktop**
   - Launch Power BI Desktop application

2. **Get Data**
   - Click "Get Data" →  "Excel" → "Connect"
   - Navigate to your Power BI export file
   - Select all tables

3. **Select Tables**
   Load these tables:
   - ✅ `Applications` - Main fact table
   - ✅ `Dimension_Scores` - Detailed dimension analysis
   - ✅ `TIME_Framework` - TIME categorization
   - ✅ `Recommendations` - Action recommendations
   - ✅ `Summary_Stats` - Portfolio metrics
   - ✅ `TIME_Distribution` - Category breakdown
   - ℹ️ `Metadata` - Optional, for documentation

4. **Load Data**
   - Click "Load" (not "Transform Data" for first load)

### 3. Creating Relationships

Power BI should auto-detect relationships, but verify/create these:

**Navigate to:** Model view (left sidebar)

**Create these relationships:**

| From Table | From Column | To Table | To Column | Cardinality |
|------------|-------------|----------|-----------|-------------|
| Applications | Application_ID | Dimension_Scores | Application_ID | One to Many |
| Applications | Application_ID | TIME_Framework | Application_ID | One to Many |
| Applications | Application_ID | Recommendations | Application_ID | One to One |

**How to create:**
1. Drag `Application_ID` from Applications table
2. Drop onto `Application_ID` in target table
3. Verify cardinality is correct
4. Click "OK"

### 4. Recommended Visualizations

#### Dashboard 1: Executive Overview

**Components:**

1. **KPI Cards** (Top row)
   - Total Applications (from Summary_Stats)
   - Total Annual Cost (from Summary_Stats)
   - Average Composite Score (from Summary_Stats)
   - Redundant Apps (from Summary_Stats)

2. **TIME Framework Pie Chart**
   - Values: Count of Application_ID
   - Legend: TIME Category
   - Colors: Custom (Green=Invest, Orange=Tolerate, Blue=Migrate, Red=Eliminate)

3. **Score Distribution Bar Chart**
   - Axis: Application Name (top 20)
   - Values: Composite Score
   - Sort: Descending by Composite Score

4. **Cost Analysis Treemap**
   - Group: Application Name
   - Values: Cost
   - Color saturation: Business Value

#### Dashboard 2: Detailed Analysis

**Components:**

1. **Scatter Plot: Business Value vs Technical Quality**
   - X-Axis: TIME Technical Quality Score
   - Y-Axis: TIME Business Value Score
   - Legend: TIME Category
   - Size: Cost
   - Add quadrant lines at (6, 6)

2. **Dimension Heatmap**
   - Rows: Application Name
   - Columns: Dimension
   - Values: Score
   - Color scale: Red-Yellow-Green (0-10)

3. **Action Recommendations Table**
   - Columns: Application Name, Action Recommendation, Composite Score
   - Sort: By Composite Score (ascending for priority)
   - Conditional formatting on score

4. **Timeline Slicer**
   - If you have historical data, add date slicer for trend analysis

### 5. DAX Measures

Add these calculated measures for enhanced analytics:

```dax
// Total Applications
Total Apps = COUNTROWS(Applications)

// Average Score
Avg Composite Score = AVERAGE(Applications[Composite Score])

// High Risk Count
High Risk Apps =
CALCULATE(
    COUNTROWS(Applications),
    Applications[Security] < 5,
    Applications[Business Value] > 7
)

// Investment Needed
Total Investment =
CALCULATE(
    SUM(Applications[Cost]),
    Applications[Action Recommendation] IN {"Invest", "Migrate"}
)

// Retirement Savings
Retirement Savings =
CALCULATE(
    SUM(Applications[Cost]),
    Applications[Action Recommendation] = "Retire"
)

// Portfolio Health Score
Portfolio Health =
AVERAGEX(
    Applications,
    [Composite Score]
) / 100

// Time-based measures (if you have historical data)
MoM Change =
VAR CurrentScore = [Avg Composite Score]
VAR PreviousScore =
CALCULATE(
    [Avg Composite Score],
    DATEADD('Date'[Date], -1, MONTH)
)
RETURN
CurrentScore - PreviousScore
```

### 6. Publishing to Power BI Service

1. **Sign in** to Power BI Service account
2. **Click** "Publish" in Power BI Desktop
3. **Select** destination workspace
4. **Share** dashboard with stakeholders

---

## Tableau

### 1. Exporting for Tableau

#### Using CLI:
```bash
python -m src.cli export -i results.csv -f tableau -o tableau_data.csv
```

Or generate complete bundle:
```bash
python -m src.cli generate-report -i results.csv -o reports/
```

#### Using Python:
```python
from src.data_handler import DataHandler

data_handler = DataHandler()
path = data_handler.export_for_tableau(
    df,
    'tableau_data.csv'
)
```

### 2. Importing into Tableau

**Step-by-Step Instructions:**

1. **Open Tableau Desktop**

2. **Connect to Data**
   - Click "Connect" → "Text file"
   - Navigate to your Tableau CSV export
   - Click "Open"

3. **Data Source Setup**
   - Verify data types are correct:
     - `Assessment_Date`: Date
     - Numeric scores: Number (decimal)
     - Categories: String
     - `High_Risk_Flag`: Number (whole)
   - Click "Update Now" to load preview

4. **Create Sheet**
   - Click "Sheet 1" tab at bottom

### 3. Calculated Fields

The Tableau export includes pre-calculated fields, but you can add more:

#### Custom Calculations:

**Investment Priority Score:**
```
([Business_Value] * 2 + [Tech_Health] - [Cost] / 10000) / 3
```

**Risk Level:**
```
IF [High_Risk_Flag] = 1 THEN "High Risk"
ELSEIF [Security] < 5 THEN "Medium Risk"
ELSE "Low Risk"
END
```

**Modernization Urgency:**
```
IF [TIME_Category] = "Eliminate" AND [Business_Value] > 5 THEN "Urgent"
ELSEIF [TIME_Category] IN ("Migrate", "Tolerate") THEN "Plan"
ELSE "Monitor"
END
```

**ROI Potential:**
```
IF [Value_per_Dollar] > MEDIAN([Value_per_Dollar])
AND [Tech_Health] < 6
THEN "High ROI Opportunity"
ELSE "Standard"
END
```

### 4. Recommended Worksheets

#### Worksheet 1: TIME Framework Quadrant

**Visual:** Scatter Plot

- **Columns:** `Business_Value`
- **Rows:** `Tech_Health`
- **Color:** `TIME_Category`
- **Size:** `Cost`
- **Label:** `Application_Name` (for selected points)

**Formatting:**
- Add reference lines at Business_Value = 6 and Tech_Health = 6
- Use custom colors: Green (Invest), Orange (Tolerate), Blue (Migrate), Red (Eliminate)
- Add annotations for quadrant labels

#### Worksheet 2: Score Heatmap

**Visual:** Heatmap

- **Columns:** Dimension scores (Business_Value, Tech_Health, etc.)
- **Rows:** `Application_Name`
- **Color:** `Score` (use Red-Yellow-Green diverging palette)
- **Text:** `Score` value

**Formatting:**
- Sort applications by Composite_Score descending
- Limit to top 30 applications for readability

#### Worksheet 3: Portfolio Overview

**Visual:** Dashboard with multiple charts

Components:
1. **KPI Summary**
   - Big numbers for key metrics
   - Use `Total Applications`, `AVG(Composite_Score)`, `SUM(Cost)`

2. **TIME Distribution**
   - Pie or donut chart
   - Dimension: `TIME_Category`
   - Measure: `COUNT(Application_Name)`

3. **Top/Bottom Performers**
   - Bar chart (horizontal)
   - Top 10 and Bottom 10 by Composite_Score

4. **Cost Analysis**
   - Treemap
   - Size: `Cost`
   - Color: `Score_Category`

#### Worksheet 4: Trend Analysis (if historical data available)

**Visual:** Line Chart

- **Columns:** `Assessment_Date`
- **Rows:** `AVG(Composite_Score)`, `AVG(Business_Value)`, `AVG(Tech_Health)`
- **Color:** Metric name
- **Filters:** Time period selector

### 5. Creating an Interactive Dashboard

**Dashboard Layout:**

```
┌─────────────────────────────────────────────────┐
│  Portfolio Health Dashboard                     │
├──────────────┬──────────────┬────────────────  │
│   KPI 1      │   KPI 2      │   KPI 3          │
│   Total Apps │   Avg Score  │   Total Cost     │
├──────────────┴──────────────┴──────────────────┤
│  TIME Framework Quadrant     │  TIME Pie Chart │
│  (Scatter)                   │                  │
│                              │                  │
├──────────────────────────────┼──────────────────┤
│  Application Heatmap         │  Action Items   │
│  (Top 20)                    │  (Table)        │
│                              │                  │
└──────────────────────────────┴──────────────────┘
```

**Add Interactivity:**
1. Add filter for `TIME_Category`
2. Add filter for `Score_Category`
3. Add parameter for minimum `Composite_Score`
4. Enable "Use as Filter" on scatter plot

### 6. Publishing to Tableau Server

1. **Sign in** to Tableau Server
2. **Server** → "Publish Workbook"
3. **Select** destination project
4. **Configure** permissions
5. **Publish**

---

## Other BI Tools

### Google Data Studio (Looker Studio)

**Import Method:** Upload CSV

**Steps:**
1. Upload the CSV export to Google Sheets
2. In Data Studio, Add Data → Google Sheets
3. Select your uploaded sheet
4. Build visualizations similar to Power BI approach

**Best Practices:**
- Use calculated fields for complex metrics
- Create separate pages for executive vs. detailed views
- Enable date range controls if tracking over time

### QlikView / Qlik Sense

**Import Method:** Load CSV via Data Load Editor

**Steps:**
1. Data Load Editor → Add Data → Files
2. Select CSV export
3. Write load script:
```qlik
LOAD
    Application_Name,
    Business_Value,
    Tech_Health,
    Composite_Score,
    TIME_Category
FROM [tableau_data.csv]
(txt, utf8, embedded labels, delimiter is ',');
```

**Recommended Visualizations:**
- Scatter plot for TIME quadrant
- KPI objects for summary metrics
- Filter pane for TIME categories

### Apache Superset

**Import Method:** Connect to database or upload CSV

**Steps:**
1. Upload CSV to SQL database
2. Add Database connection in Superset
3. Create Dataset from table
4. Build charts using intuitive interface

### Excel Pivot Tables

Use the **Enhanced Excel** export which includes:
- Pre-formatted data
- Conditional formatting
- Embedded charts

**Additional Pivot Tables:**
1. Applications by TIME Category
2. Cost by Owner
3. Avg Score by Action Recommendation

---

## Best Practices

### 1. Data Refresh Strategy

**For Regular Assessments:**

1. **Monthly Updates:**
   - Run assessment on same date each month
   - Use consistent naming: `Assessment_2025_01.xlsx`
   - Append to historical table in BI tool

2. **Incremental Refresh:**
```python
# Example: Append monthly data
import pandas as pd

# Load historical data
historical = pd.read_csv('historical_assessments.csv')

# Load new assessment
new_data = pd.read_csv('current_assessment.csv')
new_data['Assessment_Date'] = '2025-01-01'

# Combine
combined = pd.concat([historical, new_data], ignore_index=True)
combined.to_csv('historical_assessments.csv', index=False)
```

3. **Version Control:**
   - Keep each export in dated folders
   - Archive old reports
   - Document methodology changes

### 2. Performance Optimization

**For Large Datasets (>1000 apps):**

- **Power BI:**
  - Use Import mode for <100MB data
  - Use DirectQuery for larger datasets
  - Create aggregations for summary views

- **Tableau:**
  - Extract data to `.hyper` format
  - Filter data at source
  - Use context filters for hierarchy

### 3. Security and Access Control

**Sensitivity Levels:**

| Audience | Access Level | Recommended Export |
|----------|--------------|-------------------|
| Board | Summary only | Enhanced Excel (Summary sheet only) |
| Executives | High-level + trends | Power BI (filtered dashboards) |
| Portfolio Managers | Full access | Power BI / Tableau (all data) |
| Application Owners | Own apps only | Filtered CSV |

**Implementation:**
- Use Row-Level Security (RLS) in Power BI
- Set up user filters in Tableau
- Distribute separate exports per audience

### 4. Color Coding Standards

**Consistency Across Tools:**

```
TIME Framework Colors:
- Invest: #2E7D32 (Dark Green)
- Tolerate: #FFA726 (Orange)
- Migrate: #1976D2 (Blue)
- Eliminate: #C62828 (Dark Red)

Score Colors:
- Excellent (8-10): #4CAF50 (Green)
- Good (6-7.9): #8BC34A (Light Green)
- Fair (4-5.9): #FFC107 (Yellow/Orange)
- Poor (0-3.9): #F44336 (Red)
```

---

## Sample Dashboards

### Power BI Sample Dashboard

**Download:** [PowerBI_Sample.pbix](link-to-sample)

**Features:**
- Executive summary page
- Detailed analysis page
- Time-based trending (if historical data)
- Drill-through capabilities
- Custom tooltips
- Mobile-optimized layout

### Tableau Sample Workbook

**Download:** [Tableau_Sample.twbx](link-to-sample)

**Features:**
- Interactive TIME quadrant
- Application deep-dive sheets
- Action priority matrix
- Cost optimization opportunities
- Custom dashboard actions

---

## Troubleshooting

### Common Issues

#### Power BI

**Issue:** Relationships not auto-detected

**Solution:**
1. Go to Model view
2. Manually create relationships as documented above
3. Ensure `Application_ID` fields are same data type

**Issue:** Circular dependency error

**Solution:**
- Remove auto-generated relationships
- Keep only: Applications → Dimension_Scores, Applications → TIME_Framework

**Issue:** Slow performance

**Solution:**
- Reduce data volume with filters
- Use Import mode instead of DirectQuery
- Optimize DAX measures (avoid calculated columns where possible)

#### Tableau

**Issue:** Date field not recognized

**Solution:**
1. Data Source tab
2. Click data type icon next to `Assessment_Date`
3. Change to "Date"

**Issue:** Measures showing as dimensions

**Solution:**
- Drag field to "Measures" pane
- Or right-click → "Convert to Measure"

**Issue:** Colors not matching TIME categories

**Solution:**
1. Right-click color legend
2. Edit Colors
3. Assign: Invest=Green, Tolerate=Orange, Migrate=Blue, Eliminate=Red

#### General CSV Import Issues

**Issue:** Special characters garbled

**Solution:**
- Ensure file is UTF-8 encoded
- Use Tableau CSV export (not basic CSV)

**Issue:** Numbers imported as text

**Solution:**
- Check delimiter is comma
- Remove any currency symbols
- Verify decimal separator (. not ,)

---

## Additional Resources

### Documentation Links

- [Power BI Documentation](https://docs.microsoft.com/en-us/power-bi/)
- [Tableau Help](https://help.tableau.com/)
- [Google Data Studio Help](https://support.google.com/datastudio)

### Video Tutorials

- **Power BI Basics:** Create your first dashboard
- **Tableau Fundamentals:** Data connection and visualization
- **Advanced Analytics:** DAX and calculated fields

### Community Forums

- Power BI Community: community.powerbi.com
- Tableau Community: community.tableau.com
- Stack Overflow: Tagged questions for specific tools

---

## Next Steps

1. **Export your data** using preferred format
2. **Import to BI tool** following guides above
3. **Create initial dashboard** using recommended visualizations
4. **Customize** for your organization's needs
5. **Share** with stakeholders
6. **Iterate** based on feedback
7. **Automate** monthly refresh process

---

*Last Updated: 2025*
*For tool-specific questions, consult the visualization guide or contact support*
