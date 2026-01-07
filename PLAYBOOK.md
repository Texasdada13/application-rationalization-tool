# Application Rationalization Platform - Complete Playbook

A comprehensive guide to understanding and deploying the AI-powered application portfolio rationalization platform.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Quick Start](#2-quick-start)
3. [Architecture](#3-architecture)
4. [Module Reference](#4-module-reference)
5. [AI/ML Capabilities](#5-aiml-capabilities)
6. [Scoring Methodology](#6-scoring-methodology)
7. [Data Flow](#7-data-flow)
8. [Web Application](#8-web-application)
9. [Configuration](#9-configuration)
10. [Common Workflows](#10-common-workflows)

---

## 1. System Overview

### What This System Does

This is an **AI-powered application portfolio rationalization platform** that combines multiple analysis methodologies to generate strategic recommendations for enterprise IT portfolios:

| Analysis Type | Purpose | Key Capability |
|--------------|---------|----------------|
| Composite Scoring | Multi-dimensional weighted scoring | 7 strategic dimensions, 0-100 scale |
| TIME Framework | Strategic quadrant categorization | Tolerate/Invest/Migrate/Eliminate |
| ML Clustering | Pattern recognition and grouping | K-means, anomaly detection |
| Compliance Assessment | Regulatory gap analysis | SOX, HIPAA, PCI-DSS, GDPR |
| Risk Analysis | Multi-factor risk scoring | 5 risk dimensions |
| Stakeholder Assessment | Qualitative insight capture | 30+ structured interview questions |
| Predictive Modeling | Future state forecasting | Trend analysis, scenario modeling |

### Key Capabilities

- **Portfolio Assessment** - Evaluate 200+ applications across 7 strategic dimensions
- **TIME Framework Analysis** - Categorize applications into strategic quadrants
- **Stakeholder Interviews** - 30+ structured questions across 7 categories
- **ML-Powered Insights** - Clustering, anomaly detection, predictive modeling
- **Compliance Engine** - Assessment against 4 regulatory frameworks
- **What-If Scenarios** - Model impact of different portfolio decisions
- **Smart Recommendations** - AI-generated prioritized action items
- **Executive Reporting** - PDF, PowerPoint, Excel with embedded visualizations
- **Natural Language Query** - Ask questions about your portfolio in plain English

### Tech Stack

**Backend:**
- Python 3.8+ (pandas, numpy, scipy)
- Flask 2.3+ web framework
- SQLite for persistence
- Scikit-learn 1.3+ for ML features

**Frontend:**
- HTML5 / CSS3 / Tailwind CSS
- JavaScript with Plotly.js, Chart.js, Vis.js
- Interactive dashboards and visualizations

**Export & Reporting:**
- ReportLab 4.0+ for PDF generation
- python-pptx 0.6+ for PowerPoint
- openpyxl 3.1+ / XlsxWriter 3.1+ for Excel

**Deployment:**
- Gunicorn 21.0+ WSGI server
- Docker containerization support
- Render cloud platform ready

### Platform Metrics

| Metric | Value |
|--------|-------|
| Total Features | 50+ |
| Analysis Engines | 15 |
| API Endpoints | 100+ |
| Assessment Questions | 30+ |
| Compliance Frameworks | 4 |
| Export Formats | 4 |
| Visualization Types | 20+ |

---

## 2. Quick Start

### Installation

```bash
# Clone and setup
git clone https://github.com/Texasdada13/application-rationalization-tool.git
cd application-rationalization-tool

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run Your First Assessment

**Option 1: CLI**
```bash
python main.py
# Follow the interactive prompts
```

**Option 2: Python Script**
```python
from src.scoring_engine import ScoringEngine
from src.recommendation_engine import RecommendationEngine
from src.time_framework import TIMEFramework

# Initialize engines
scoring = ScoringEngine()
recommendations = RecommendationEngine()
time_framework = TIMEFramework()

# Load and process applications
applications = load_portfolio_data('data/assessment_template.csv')
scored = scoring.batch_calculate_scores(applications)
recommended = recommendations.batch_generate_recommendations(scored)
categorized = time_framework.batch_categorize(recommended)

print(f"Assessed {len(categorized)} applications")
```

**Option 3: Web Interface**
```bash
cd web
python app.py
# Open http://localhost:5000
```

### Assess Multiple Applications

```python
from src.data_handler import DataHandler
from src.scoring_engine import ScoringEngine

data_handler = DataHandler()
scoring_engine = ScoringEngine()

# Load portfolio
df = data_handler.read_csv('data/my_portfolio.csv')
applications = df.to_dict('records')

# Score all applications
scored_apps = scoring_engine.batch_calculate_scores(applications)

# Display results
for app in sorted(scored_apps, key=lambda x: x['composite_score'], reverse=True):
    print(f"{app['name']}: {app['composite_score']:.1f} - {app['recommendation']}")
```

---

## 3. Architecture

### Directory Structure

```
application-rationalization-tool/
├── src/                           # Core analysis modules
│   ├── scoring_engine.py          # Composite score calculation
│   ├── recommendation_engine.py   # Recommendation logic
│   ├── time_framework.py          # TIME framework categorization
│   ├── compliance_engine.py       # Regulatory compliance checks
│   ├── ml_engine.py              # Machine learning clustering
│   ├── risk_assessor.py          # Risk assessment framework
│   ├── stakeholder_assessment_engine.py  # Interview management
│   ├── predictive_modeling.py    # Predictive analytics
│   ├── sentiment_analyzer.py     # Sentiment analysis
│   ├── smart_recommendations.py  # AI recommendations
│   ├── whatif_engine.py          # Scenario analysis
│   ├── cost_modeler.py           # TCO calculations
│   ├── integration_mapper.py     # Dependency mapping
│   ├── roadmap_engine.py         # Prioritization roadmap
│   ├── nl_query_engine.py        # Natural language queries
│   ├── report_generator.py       # Report generation
│   ├── data_handler.py           # CSV/Excel I/O
│   ├── data_validator.py         # Data quality checks
│   ├── visualizations.py         # Chart generation
│   ├── config_loader.py          # Configuration management
│   ├── database.py               # SQLite persistence
│   ├── scheduler.py              # Job scheduling
│   └── cli.py                    # Command-line interface
│
├── web/                          # Flask web application
│   ├── app.py                    # Main Flask app
│   ├── templates/                # HTML templates
│   └── static/                   # CSS, JS, images
│
├── data/                         # Data storage
│   └── assessment_template.csv   # Sample input data
│
├── config/                       # Configuration files
│   ├── config.yaml              # Default configuration
│   └── time_config.yaml         # TIME framework thresholds
│
├── output/                       # Generated results
│   ├── visualizations/          # Charts and graphs
│   └── exports/                 # Reports and exports
│
├── docs/                        # Documentation
├── examples/                    # Example scripts
├── main.py                      # CLI entry point
└── requirements.txt             # Python dependencies
```

### Component Relationships

```
                    ┌─────────────────────┐
                    │     Entry Points    │
                    │  main.py / web/app  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │     Data Handler    │
                    │  (Load & Validate)  │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
┌───────▼───────┐    ┌────────▼────────┐    ┌───────▼───────┐
│    Scoring    │    │   TIME Frame    │    │  Compliance   │
│    Engine     │    │    Framework    │    │    Engine     │
│  (7 dimensions)│   │  (4 quadrants)  │    │ (4 frameworks)│
└───────┬───────┘    └────────┬────────┘    └───────┬───────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼───────┐    ┌───────▼────────┐    ┌───────▼───────┐
│  ML Engine    │    │  Stakeholder   │    │     Risk      │
│ (Clustering)  │    │  Assessment    │    │   Assessor    │
└───────┬───────┘    └───────┬────────┘    └───────┬───────┘
        │                    │                     │
        └────────────────────┼─────────────────────┘
                             │
                  ┌──────────▼──────────┐
                  │  Recommendation &   │
                  │   Roadmap Engine    │
                  └──────────┬──────────┘
                             │
                  ┌──────────▼──────────┐
                  │   Report Generator  │
                  │ (PDF, PPTX, Excel)  │
                  └─────────────────────┘
```

---

## 4. Module Reference

### ScoringEngine (Main Scoring)

**Location:** `src/scoring_engine.py`

```python
from src.scoring_engine import ScoringEngine, ScoringWeights

# Basic usage
engine = ScoringEngine()
score = engine.calculate_composite_score(application)

# Custom weights
custom_weights = ScoringWeights(
    business_value=0.30,
    tech_health=0.25,
    cost=0.15,
    usage=0.10,
    security=0.10,
    strategic_fit=0.08,
    redundancy=0.02
)
engine = ScoringEngine(weights=custom_weights)
```

**Output Structure:**
```python
{
    'name': 'SAP ERP',
    'composite_score': 72.5,          # 0-100 scale
    'business_value_score': 8.5,      # 0-10 scale
    'tech_health_score': 6.0,
    'cost_score': 7.2,
    'usage_score': 8.0,
    'security_score': 7.5,
    'strategic_fit_score': 8.0,
    'redundancy_score': 9.0,
    'recommendation': 'Invest',
    'time_category': 'Invest'
}
```

### TIMEFramework (Strategic Categorization)

**Location:** `src/time_framework.py`

```python
from src.time_framework import TIMEFramework

framework = TIMEFramework()
category = framework.categorize(application)

# Categories:
# - INVEST: High business value, high tech quality
# - TOLERATE: High business value, low tech quality
# - MIGRATE: Low business value, high tech quality
# - ELIMINATE: Low business value, low tech quality
```

### ComplianceEngine (Regulatory Assessment)

**Location:** `src/compliance_engine.py`

```python
from src.compliance_engine import ComplianceEngine

engine = ComplianceEngine()

# Assess single application
sox_result = engine.assess_sox_compliance(application)
hipaa_result = engine.assess_hipaa_compliance(application)
pci_result = engine.assess_pci_compliance(application)
gdpr_result = engine.assess_gdpr_compliance(application)

# Portfolio-wide assessment
portfolio_compliance = engine.assess_portfolio(applications)
```

**Compliance Output:**
```python
{
    'framework': 'HIPAA',
    'compliance_score': 71.1,         # Percentage
    'status': 'Partial',              # Compliant/Partial/Non-Compliant
    'gaps': [
        {'control': 'Data Encryption', 'severity': 'High', 'remediation': '...'},
        {'control': 'Access Controls', 'severity': 'Medium', 'remediation': '...'}
    ],
    'risk_level': 'Medium'
}
```

### MLEngine (Machine Learning)

**Location:** `src/ml_engine.py`

```python
from src.ml_engine import MLEngine

ml = MLEngine()

# Cluster similar applications
clusters = ml.cluster_applications(applications, n_clusters=5)

# Detect anomalies
anomalies = ml.detect_anomalies(applications)

# Get cluster characteristics
characteristics = ml.get_cluster_characteristics(clusters)
```

### StakeholderAssessmentEngine (Interviews)

**Location:** `src/stakeholder_assessment_engine.py`

```python
from src.stakeholder_assessment_engine import StakeholderAssessmentEngine

engine = StakeholderAssessmentEngine()

# Get assessment questions (30+ across 7 categories)
questions = engine.get_assessment_questions()

# Score interview responses
scores = engine.score_responses(responses)

# Aggregate multiple stakeholder perspectives
aggregated = engine.aggregate_stakeholder_scores(all_responses)
```

**Assessment Categories:**
1. Business Value & Criticality (5 questions)
2. User Satisfaction & Experience (6 questions)
3. Technical Health & Sustainability (5 questions)
4. Change Readiness & Migration Potential (6 questions)
5. Dependencies & Integration (5 questions)
6. Cost & Resource Awareness (4 questions)
7. Future Needs & Strategic Alignment (4 questions)

### RoadmapEngine (Prioritization)

**Location:** `src/roadmap_engine.py`

```python
from src.roadmap_engine import RoadmapEngine

roadmap = RoadmapEngine()

# Generate prioritized roadmap
plan = roadmap.generate_roadmap(applications)

# Output includes:
# - Quick Wins (0-90 days)
# - Short-term (3-12 months)
# - Medium-term (1-2 years)
# - Long-term (2-3 years)
```

---

## 5. AI/ML Capabilities

### Machine Learning Features

| Feature | Algorithm | Purpose |
|---------|-----------|---------|
| Application Clustering | K-Means | Group similar applications for consolidation |
| Anomaly Detection | Isolation Forest | Identify outliers and data quality issues |
| Predictive Scoring | Linear Regression | Forecast future application scores |
| Sentiment Analysis | NLP Processing | Analyze stakeholder feedback sentiment |
| Smart Recommendations | Rule Engine + ML | Generate prioritized action items |

### Clustering Example

```python
from src.ml_engine import MLEngine

ml = MLEngine()

# Cluster applications into groups
clusters = ml.cluster_applications(applications, n_clusters=5)

# Each cluster represents a natural grouping:
# - Similar technical characteristics
# - Similar business value profiles
# - Potential consolidation candidates
```

### Anomaly Detection

```python
# Find applications that don't fit normal patterns
anomalies = ml.detect_anomalies(applications)

# Anomalies may indicate:
# - Data entry errors
# - Unique situations requiring attention
# - Miscategorized applications
```

### Natural Language Query

```python
from src.nl_query_engine import NLQueryEngine

query_engine = NLQueryEngine(applications)

# Ask questions in plain English
results = query_engine.query("Which applications should we retire first?")
results = query_engine.query("What's our biggest compliance risk?")
results = query_engine.query("Show me high-cost low-value applications")
```

---

## 6. Scoring Methodology

### Composite Score Calculation

```
Composite Score = (
    Business Value × 0.25 +
    Tech Health × 0.25 +
    Security × 0.15 +
    Strategic Fit × 0.15 +
    Cost Efficiency × 0.10 +
    Usage × 0.10
) × 10
```

**Scale:** 0-100 (normalized from 0-10 inputs)

### Default Weights

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Business Value | 25% | Strategic importance to organization |
| Tech Health | 25% | Technical condition and maintainability |
| Security | 15% | Security posture and compliance |
| Strategic Fit | 15% | Alignment with business strategy |
| Cost Efficiency | 10% | Value delivered per dollar spent |
| Usage | 10% | Active utilization level |

### Recommendation Thresholds

| Score Range | Recommendation | Action |
|-------------|----------------|--------|
| ≥ 70 | **Invest** | Continue investment, enhance |
| 55-69 | **Maintain** | Standard maintenance |
| 40-54 | **Tolerate** | Monitor, plan improvements |
| 25-39 | **Migrate** | Plan modernization or replacement |
| < 25 | **Retire** | Decommission candidate |

### TIME Framework Categorization

```
                Technical Quality
                Low    →    High
              ┌────────┬────────┐
Business      │TOLERATE│ INVEST │
Value    High │  Plan  │ Grow & │
              │ Modern │ Enhance│
              ├────────┼────────┤
         Low  │ELIM-   │ MIGRATE│
              │INATE   │ Consol │
              └────────┴────────┘
```

---

## 7. Data Flow

### Complete Pipeline

```
1. DATA INGESTION
   └── CSV/Excel Upload
       └── Data Validation (12 checks)
           └── Quality Score (0-100)

2. SCORING & ASSESSMENT
   ├── Composite Scoring (7 dimensions)
   ├── TIME Categorization (4 quadrants)
   ├── Compliance Assessment (4 frameworks)
   └── Risk Analysis (5 dimensions)

3. ADVANCED ANALYTICS
   ├── ML Clustering (K-means)
   ├── Anomaly Detection (Isolation Forest)
   ├── Stakeholder Aggregation
   └── Dependency Mapping

4. RECOMMENDATIONS
   ├── Smart Recommendations Engine
   ├── What-If Scenario Analysis
   └── Prioritization Roadmap

5. OUTPUT
   ├── Executive Dashboard
   ├── PDF Reports
   ├── PowerPoint Presentations
   ├── Excel Workbooks
   └── API Responses
```

### Data Quality Validation

The system performs 12 validation checks:

| Check | Description | Severity |
|-------|-------------|----------|
| Required Fields | Essential columns present | Critical |
| Score Ranges | Values within 1-10 | Critical |
| Cost Values | Non-negative numbers | Critical |
| Duplicates | No duplicate app names | Warning |
| Owner Populated | Owner field has value | Warning |
| Completeness | All optional fields | Info |

---

## 8. Web Application

### Starting the Server

```bash
cd web
python app.py
# Open http://localhost:5000
```

**Production:**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 web.app:app
```

### Key Features

- **Executive Dashboard** - KPIs, score distributions, TIME quadrants
- **Portfolio Table** - Sortable, filterable application list
- **Application Details** - Deep dive into individual apps
- **Stakeholder Assessment** - Interview management and scoring
- **Compliance Dashboard** - Regulatory status and gaps
- **Report Generator** - PDF, PPTX, Excel exports
- **AI Chat** - Natural language queries

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/applications` | GET | List all applications |
| `/api/applications/<id>` | GET | Get application details |
| `/api/assess` | POST | Run assessment |
| `/api/compliance` | GET | Compliance status |
| `/api/recommendations` | GET | Get recommendations |
| `/api/reports/generate` | POST | Generate report |
| `/api/query` | POST | Natural language query |

---

## 9. Configuration

### Configuration Files

**config/config.yaml** - Default settings
**config/config.local.yaml** - User overrides (gitignored)
**config/time_config.yaml** - TIME framework thresholds

### Scoring Weights Configuration

```yaml
# config/config.yaml
scoring_weights:
  business_value: 0.25
  tech_health: 0.25
  cost: 0.10
  usage: 0.10
  security: 0.15
  strategic_fit: 0.15
  redundancy: 0.00
```

### TIME Framework Thresholds

```yaml
# config/time_config.yaml
time_thresholds:
  business_value_threshold: 6.0      # High BV cutoff (0-10)
  technical_quality_threshold: 6.0    # High TQ cutoff (0-10)
  composite_score_high: 65.0          # High performer (0-100)
  composite_score_low: 40.0           # Low performer (0-100)
```

### Environment Variables

```bash
# .env
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///data/portfolio.db
```

---

## 10. Common Workflows

### Workflow 1: Quick Portfolio Assessment

```python
from src.data_handler import DataHandler
from src.scoring_engine import ScoringEngine
from src.time_framework import TIMEFramework

# Load data
handler = DataHandler()
df = handler.read_csv('data/portfolio.csv')

# Score and categorize
scoring = ScoringEngine()
time_fw = TIMEFramework()

apps = df.to_dict('records')
apps = scoring.batch_calculate_scores(apps)
apps = time_fw.batch_categorize(apps)

# Summary
print(f"Total Applications: {len(apps)}")
print(f"Average Score: {sum(a['composite_score'] for a in apps)/len(apps):.1f}")
```

### Workflow 2: Compliance Assessment

```python
from src.compliance_engine import ComplianceEngine

compliance = ComplianceEngine()

# Assess portfolio against all frameworks
results = compliance.assess_portfolio(applications)

print(f"SOX Compliance: {results['sox']['score']:.1f}%")
print(f"HIPAA Compliance: {results['hipaa']['score']:.1f}%")
print(f"PCI-DSS Compliance: {results['pci']['score']:.1f}%")
print(f"GDPR Compliance: {results['gdpr']['score']:.1f}%")
```

### Workflow 3: Generate Executive Report

```python
from src.report_generator import ReportGenerator

generator = ReportGenerator()

# Generate PDF executive summary
pdf_path = generator.generate_pdf_report(
    applications,
    output_path='output/executive_report.pdf',
    include_charts=True
)

# Generate PowerPoint presentation
pptx_path = generator.generate_powerpoint(
    applications,
    output_path='output/portfolio_presentation.pptx'
)
```

### Workflow 4: What-If Scenario Analysis

```python
from src.whatif_engine import WhatIfEngine

whatif = WhatIfEngine()

# Model retirement scenario
scenario = whatif.model_retirement(
    applications,
    retire_list=['Legacy CRM', 'Old Reporting Tool']
)

print(f"Cost Impact: ${scenario['cost_savings']:,.0f}")
print(f"Risk Reduction: {scenario['risk_reduction']:.1f}%")
```

### Workflow 5: Stakeholder Interview Workflow

```python
from src.stakeholder_assessment_engine import StakeholderAssessmentEngine

engine = StakeholderAssessmentEngine()

# Get questions for interview
questions = engine.get_assessment_questions()

# Score completed interview
scores = engine.score_responses(interview_responses)

# Combine with quantitative data
final_assessment = engine.combine_assessments(
    quantitative_scores,
    stakeholder_scores
)
```

---

## Appendix A: Troubleshooting

### Common Issues

**Issue: Import errors**
```bash
# Ensure you're in the project root
cd application-rationalization-tool
python -c "from src.scoring_engine import ScoringEngine"
```

**Issue: Missing dependencies**
```bash
pip install -r requirements.txt --force-reinstall
```

**Issue: Data validation failures**
```python
from src.data_validator import DataValidator
validator = DataValidator()
issues = validator.validate(df)
print(issues)  # See specific problems
```

---

## Appendix B: Key Files Reference

| File | Purpose |
|------|---------|
| `main.py` | CLI entry point |
| `src/scoring_engine.py` | Composite score calculation |
| `src/recommendation_engine.py` | Recommendation logic |
| `src/time_framework.py` | TIME categorization |
| `src/compliance_engine.py` | Regulatory assessment |
| `src/ml_engine.py` | Machine learning features |
| `src/stakeholder_assessment_engine.py` | Interview management |
| `src/report_generator.py` | PDF/PPTX/Excel generation |
| `web/app.py` | Flask web application |
| `config/config.yaml` | Configuration settings |

---

## Appendix C: Performance Benchmarks

| Operation | Portfolio Size | Time |
|-----------|---------------|------|
| Full Assessment | 200 apps | < 2 seconds |
| Compliance Check | 200 apps | < 3 seconds |
| ML Clustering | 200 apps | < 5 seconds |
| Report Generation | 200 apps | < 10 seconds |
| Data Validation | 200 apps | < 1 second |

**Tested Scale:** Up to 10,000 applications

---

*Last Updated: January 2026*
*Version: 1.0.0*
