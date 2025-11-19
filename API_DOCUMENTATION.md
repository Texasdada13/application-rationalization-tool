# API Documentation

## Application Rationalization Tool - Complete API Reference

**Base URL**: `http://localhost:5000`

**Server Status**: Running ✅

---

## Table of Contents

1. [Historical Tracking APIs](#historical-tracking-apis)
2. [Risk Assessment APIs](#risk-assessment-apis)
3. [Advanced Reporting APIs](#advanced-reporting-apis)
4. [Benchmark Engine APIs](#benchmark-engine-apis)
5. [Natural Language Query APIs](#natural-language-query-apis)
6. [Roadmap & Planning APIs](#roadmap--planning-apis)
7. [What-If Scenario APIs](#what-if-scenario-apis)
8. [Data Quality APIs](#data-quality-apis)
9. [Cost Modeling APIs](#cost-modeling-apis)
10. [Dependency Mapping APIs](#dependency-mapping-apis)

---

## Historical Tracking APIs

### Save Portfolio Snapshot
```http
POST /api/history/save-snapshot
Content-Type: application/json

{
  "snapshot_name": "Q4 2024 Baseline"
}
```

**Response**:
```json
{
  "success": true,
  "snapshot_id": "Q4 2024 Baseline",
  "message": "Snapshot saved successfully"
}
```

### List All Snapshots
```http
GET /api/history/list-snapshots
```

**Response**:
```json
{
  "success": true,
  "snapshots": [
    {
      "snapshot_id": "Q4 2024 Baseline",
      "date": "2025-11-19",
      "time": "11:16:36",
      "total_apps": 211,
      "total_cost": 22563270.28
    }
  ]
}
```

### Compare Two Snapshots
```http
POST /api/history/compare
Content-Type: application/json

{
  "snapshot1_id": "Q4 2024 Baseline",
  "snapshot2_id": "Q1 2025 Review"
}
```

### Get Portfolio Evolution
```http
GET /api/history/evolution
```

### Track ROI Realization
```http
POST /api/history/roi-tracking
Content-Type: application/json

{
  "decisions": [
    {
      "app_name": "Legacy HR System",
      "action": "retire",
      "expected_savings": 150000,
      "actual_savings": 135000
    }
  ]
}
```

### Get Application History
```http
GET /api/history/app-history/<app_name>
```

---

## Risk Assessment APIs

### Assess Entire Portfolio
```http
GET /api/risk/assess-portfolio
```

**Response**:
```json
{
  "success": true,
  "assessment": {
    "assessments": [...],
    "portfolio_metrics": {
      "total_applications": 211,
      "avg_risk_score": 65.3,
      "max_risk_score": 87.2,
      "min_risk_score": 12.5
    },
    "risk_distribution": {
      "critical": 15,
      "high": 45,
      "medium": 98,
      "low": 42,
      "minimal": 11
    },
    "high_risk_apps": [...],
    "urgent_apps": [...]
  }
}
```

### Assess Single Application
```http
GET /api/risk/assess-app/<app_name>
```

### Check Compliance
```http
GET /api/risk/compliance/<framework>
```

**Supported Frameworks**: SOX, HIPAA, PCI-DSS, GDPR, SOC2

**Response**:
```json
{
  "success": true,
  "compliance": {
    "framework": "HIPAA",
    "compliance_rate": 71.1,
    "total_applications": 211,
    "compliant_applications": 150,
    "non_compliant_applications": 61,
    "compliance_issues": [...],
    "critical_issues": [...],
    "recommendation": "Moderate compliance - urgent action needed on 61 issues"
  }
}
```

### Get Risk Mitigation Plan
```http
GET /api/risk/mitigation-plan/<app_name>
```

### Get Risk Heatmap Data
```http
GET /api/risk/heatmap
```

---

## Advanced Reporting APIs

### Get Available Reports
```http
GET /api/reports/available
```

**Response**:
```json
{
  "success": true,
  "reports": {
    "executive_summary": {
      "name": "Executive Summary Report",
      "description": "High-level overview for C-suite",
      "sections": ["portfolio_overview", "key_metrics", "top_risks", "recommendations"]
    },
    "technical_deep_dive": {...},
    "financial_analysis": {...},
    "risk_compliance": {...},
    "roadmap_strategy": {...}
  }
}
```

### Generate Report
```http
GET /api/reports/generate/<report_type>
```

**Report Types**: `executive_summary`, `technical_deep_dive`, `financial_analysis`, `risk_compliance`, `roadmap_strategy`

### Export Report
```http
GET /api/reports/export/<report_type>/<format>
```

**Formats**: `json`, `excel`, `csv`

**Example**:
```bash
curl "http://localhost:5000/api/reports/export/executive_summary/excel" -o report.xlsx
```

### Get Executive Summary (Quick Access)
```http
GET /api/reports/executive-summary
```

### Get Portfolio Overview
```http
GET /api/reports/portfolio-overview
```

---

## Benchmark Engine APIs

### Get Comprehensive Benchmark Report
```http
GET /api/benchmark/report
```

**Response**:
```json
{
  "success": true,
  "benchmark": {
    "portfolio_profile": {
      "size_category": "large",
      "total_applications": 211,
      "total_annual_cost": 22563270.28,
      "avg_cost_per_app": 106902.71
    },
    "health_benchmark": {
      "actual_distribution": {...},
      "benchmark_category": "industry_average",
      "health_score": 72.5,
      "gaps": {...},
      "recommendation": "..."
    },
    "maturity_assessment": {
      "maturity_level": "Managed",
      "composite_score": 73.2,
      "dimension_scores": {...}
    },
    "peer_gaps": [...],
    "best_practices": [...]
  }
}
```

### Benchmark Health Distribution
```http
GET /api/benchmark/health
```

### Benchmark Cost Efficiency
```http
GET /api/benchmark/cost-efficiency
```

### Assess Portfolio Maturity
```http
GET /api/benchmark/maturity
```

**Maturity Levels**:
- **Initial**: Basic inventory and tracking
- **Repeatable**: Defined processes
- **Defined**: Risk-based decision making
- **Managed**: Automation and optimization
- **Optimized**: Industry leadership

### Identify Peer Gaps
```http
GET /api/benchmark/gaps
```

### Get Best Practices
```http
GET /api/benchmark/best-practices?category=<category>
```

**Categories**: `portfolio_optimization`, `cost_management`, `risk_management`, `modernization`

---

## Natural Language Query APIs

### Ask a Question
```http
POST /api/nl-query/ask
Content-Type: application/json

{
  "query": "How many applications should we retire?"
}
```

**Response**:
```json
{
  "success": true,
  "result": {
    "query_type": "retire",
    "answer": "15 retirement candidates",
    "details": "15 applications are candidates for retirement (low health & low value)",
    "data": {
      "candidates": [...],
      "count": 15,
      "potential_savings": 2456000,
      "savings_percentage": 10.9
    }
  }
}
```

### Get Example Queries
```http
GET /api/nl-query/examples
```

**Supported Query Types**:
- Count: "How many applications do we have?"
- Cost: "What is the total annual cost?"
- Health: "Show me unhealthy applications"
- Value: "Show high-value applications"
- Retire: "Which applications should we retire?"
- Modernize: "What apps need modernization?"
- Risk: "Show highest risk applications"
- Savings: "How much can we save?"
- Category: "Show applications in Finance"
- Comparison: "Compare best and worst"
- Recommendation: "What do you recommend?"
- Trend: "Show portfolio evolution"

---

## Roadmap & Planning APIs

### Generate Roadmap
```http
GET /api/roadmap/generate
```

**Response**:
```json
{
  "success": true,
  "roadmap": {
    "total_actions": 117,
    "total_savings": 2456789,
    "duration_months": 31,
    "phases": [...],
    "timeline": [...]
  }
}
```

### Get Effort vs Impact Matrix
```http
GET /api/roadmap/effort-impact
```

### Get Dependency Warnings
```http
GET /api/roadmap/dependencies
```

---

## What-If Scenario APIs

### Get Baseline Metrics
```http
GET /api/whatif/baseline
```

### Simulate Retirement
```http
POST /api/whatif/retire
Content-Type: application/json

{
  "apps": ["Legacy System A", "Old CRM"]
}
```

### Simulate Modernization
```http
POST /api/whatif/modernize
Content-Type: application/json

{
  "apps": ["Critical App 1"],
  "health_improvement": 3.0
}
```

### Simulate Consolidation
```http
POST /api/whatif/consolidate
Content-Type: application/json

{
  "app_groups": [
    ["App A", "App B", "App C"]
  ],
  "cost_reduction": 0.30
}
```

### Get Recommendations
```http
GET /api/whatif/recommendations
```

---

## Data Quality APIs

### Validate Data Quality
```http
POST /api/data-quality/validate
Content-Type: multipart/form-data

file: <CSV file>
```

### Get Current Quality Status
```http
GET /api/data-quality/current
```

**Response**:
```json
{
  "success": true,
  "quality_report": {
    "overall_score": 87,
    "issues": [],
    "warnings": [...]
  }
}
```

### Get Quality Improvement Suggestions
```http
GET /api/data-quality/suggestions
```

---

## Cost Modeling APIs

### Get TCO Breakdown
```http
GET /api/cost-modeling/tco
```

### Get Department Costs
```http
GET /api/cost-modeling/departments
```

### Identify Hidden Costs
```http
GET /api/cost-modeling/hidden-costs
```

### Get Cost Summary
```http
GET /api/cost-modeling/summary
```

---

## Dependency Mapping APIs

### Get Dependency Report
```http
GET /api/dependencies/report
```

**Response**:
```json
{
  "success": true,
  "dependency_report": {
    "total_dependencies": 45,
    "hub_applications": [...],
    "critical_paths": [...],
    "network_density": 0.15,
    "circular_dependencies": [...]
  }
}
```

### Get Blast Radius
```http
GET /api/dependencies/blast-radius/<app_name>
```

---

## Error Responses

All endpoints follow consistent error response format:

```json
{
  "error": "Description of error",
  "success": false
}
```

**Common HTTP Status Codes**:
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `404`: Not Found
- `500`: Internal Server Error

---

## Rate Limiting

Currently no rate limiting implemented (development server).

---

## Authentication

Currently no authentication required (development server).

**Production Recommendation**: Implement OAuth 2.0 or API keys for production deployment.

---

## Response Formats

All APIs return JSON responses with consistent structure:

**Success Response**:
```json
{
  "success": true,
  "result": {...}
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Error message"
}
```

---

## Data Formats

### Dates
ISO 8601 format: `2025-11-19T11:16:36.131011`

### Currency
USD with 2 decimal places: `22563270.28`

### Percentages
Decimal format (0-1): `0.711` = 71.1%

---

## Complete Feature Summary

**Total API Endpoints**: 38+

**Categories**:
1. Historical Tracking: 6 endpoints
2. Risk Assessment: 5 endpoints
3. Advanced Reporting: 5 endpoints
4. Benchmark Engine: 6 endpoints
5. Natural Language Query: 2 endpoints
6. Roadmap Planning: 3 endpoints
7. What-If Scenarios: 5 endpoints
8. Data Quality: 3 endpoints
9. Cost Modeling: 4 endpoints
10. Dependencies: 2 endpoints

---

## Testing Examples

### Using cURL

```bash
# Get portfolio overview
curl "http://localhost:5000/api/reports/portfolio-overview"

# Ask a question
curl -X POST "http://localhost:5000/api/nl-query/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "How many applications should we retire?"}'

# Check HIPAA compliance
curl "http://localhost:5000/api/risk/compliance/HIPAA"

# Download Excel report
curl "http://localhost:5000/api/reports/export/executive_summary/excel" -o report.xlsx
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:5000"

# Ask a natural language question
response = requests.post(
    f"{BASE_URL}/api/nl-query/ask",
    json={"query": "What is the total cost?"}
)
result = response.json()
print(result['result']['answer'])

# Get benchmark report
response = requests.get(f"{BASE_URL}/api/benchmark/report")
benchmark = response.json()
print(f"Maturity Level: {benchmark['benchmark']['maturity_assessment']['maturity_level']}")
```

### Using JavaScript (Fetch API)

```javascript
// Ask a question
fetch('http://localhost:5000/api/nl-query/ask', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({query: 'Show unhealthy applications'})
})
.then(r => r.json())
.then(data => console.log(data.result.answer));

// Get risk assessment
fetch('http://localhost:5000/api/risk/assess-portfolio')
  .then(r => r.json())
  .then(data => console.log(data.assessment.portfolio_metrics));
```

---

## Support

For issues or questions:
- GitHub: https://github.com/Texasdada13/application-rationalization-tool
- Documentation: See TESTING_GUIDE.md for more examples

---

**Last Updated**: 2025-11-19
**API Version**: 2.0
**Server**: Flask Development Server
