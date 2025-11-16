# TIME Framework Integration Guide

This document provides comprehensive guidance on using the TIME framework for application rationalization.

## Table of Contents

1. [What is the TIME Framework?](#what-is-the-time-framework)
2. [TIME Categories](#time-categories)
3. [How TIME Categorization Works](#how-time-categorization-works)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)
6. [Integration with Recommendations](#integration-with-recommendations)
7. [Customization Guide](#customization-guide)
8. [Best Practices](#best-practices)

## What is the TIME Framework?

The TIME framework is an industry-standard approach for application portfolio rationalization. It categorizes applications into four quadrants based on two key dimensions:

- **Business Value**: The importance and contribution of the application to business objectives
- **Technical Quality**: The technical health, security, and strategic fit of the application

### The Four TIME Categories

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

## TIME Categories

### INVEST (High Business Value, High Technical Quality)

**Definition:** Applications that are strategically valuable and technically sound.

**Characteristics:**
- High business value score (typically ≥6.0/10)
- High technical quality score (typically ≥6.0/10)
- Strong user adoption
- Modern technology stack
- Good security posture
- Aligned with business strategy

**Recommended Actions:**
- Continue investment and enhancement
- Maximize returns through feature development
- Maintain and improve existing capabilities
- Use as reference architecture for other systems

**Examples:**
- Modern CRM platforms
- Cloud-native customer portals
- Strategic analytics platforms
- Recently modernized core systems

**Typical Outcomes:**
- Increased budget allocation
- Feature roadmap development
- Enhanced support and maintenance
- Integration with strategic initiatives

---

### TOLERATE (High Business Value, Low Technical Quality)

**Definition:** Business-critical applications with technical limitations or debt.

**Characteristics:**
- High business value score (typically ≥6.0/10)
- Low technical quality score (typically <6.0/10)
- Aging technology stack
- Significant technical debt
- Difficult to maintain or enhance
- May have security concerns

**Recommended Actions:**
- Maintain current operations
- Plan technical improvements or migration
- Minimize new development
- Document exit strategy
- Budget for eventual replacement

**Examples:**
- Legacy ERP systems
- Aging core banking platforms
- Custom-built business applications
- End-of-life vendor software still in use

**Typical Outcomes:**
- Stabilization efforts
- Security patches only
- Migration/modernization planning
- Risk mitigation measures
- Cost containment focus

---

### MIGRATE (Low Business Value, Good Technical Quality OR Misaligned Apps)

**Definition:** Applications with limited business value that should be reconsidered.

**Characteristics:**
- Low business value score (typically <6.0/10)
- May have good or poor technical quality
- Underutilized capabilities
- Misaligned with current strategy
- Consolidation opportunities exist
- Over-engineered for actual needs

**Recommended Actions:**
- Evaluate consolidation opportunities
- Consider migration to shared services
- Repurpose for different use cases
- Plan phased retirement
- Transfer users to alternative solutions

**Examples:**
- Over-engineered internal tools
- Niche applications with few users
- Redundant functionality
- Shadow IT applications
- Department-specific tools with enterprise alternatives

**Typical Outcomes:**
- Consolidation projects
- Migration to standard platforms
- User transition planning
- Functionality rationalization
- Cost reduction through elimination

---

### ELIMINATE (Low Business Value, Low Technical Quality)

**Definition:** Applications that should be retired or decommissioned.

**Characteristics:**
- Low business value score (typically <6.0/10)
- Low technical quality score (typically <6.0/10)
- Minimal or no usage
- High technical debt
- Security vulnerabilities
- Often redundant

**Recommended Actions:**
- Plan immediate retirement
- Archive historical data
- Decommission infrastructure
- Cancel licenses and support contracts
- Document replacement solution
- Notify users and stakeholders

**Examples:**
- Unused legacy applications
- Duplicate systems
- End-of-life software
- Abandoned projects
- Obsolete reporting tools

**Typical Outcomes:**
- Application retirement
- Cost savings from license cancellation
- Infrastructure decommissioning
- Data archival
- Technical debt reduction

---

## How TIME Categorization Works

### Two-Dimensional Scoring

The TIME framework calculates two composite scores for each application:

#### 1. Business Value Score (0-10 scale)

**Formula:**
```
BV Score = (Business Value × 0.5) + (Usage Normalized × 0.2) + (Strategic Fit × 0.3)
```

**Components:**
- **Business Value** (50% weight): Direct assessment of business impact
- **Usage** (20% weight): Actual adoption and utilization
- **Strategic Fit** (30% weight): Alignment with business strategy

**Example:**
```
Application: Customer Portal
- Business Value: 9/10
- Usage: 850 users → 8.5/10 (normalized to max 1000)
- Strategic Fit: 9/10

BV Score = (9 × 0.5) + (8.5 × 0.2) + (9 × 0.3)
         = 4.5 + 1.7 + 2.7
         = 8.9/10
```

#### 2. Technical Quality Score (0-10 scale)

**Formula:**
```
TQ Score = (Tech Health × 0.4) + (Security × 0.3) +
           (Strategic Fit × 0.2) + (Cost Efficiency × 0.1)
```

**Components:**
- **Tech Health** (40% weight): Maintainability, architecture, performance
- **Security** (30% weight): Security posture and compliance
- **Strategic Fit** (20% weight): Technology strategy alignment
- **Cost Efficiency** (10% weight): Cost-effectiveness

**Example:**
```
Application: Customer Portal
- Tech Health: 7/10
- Security: 8/10
- Strategic Fit: 9/10
- Cost: $50,000 → 8.33/10 efficiency (normalized to max $300k)

TQ Score = (7 × 0.4) + (8 × 0.3) + (9 × 0.2) + (8.33 × 0.1)
         = 2.8 + 2.4 + 1.8 + 0.83
         = 7.83/10
```

### Categorization Logic

```python
# Simplified decision logic
if BV_Score >= 6.0 and TQ_Score >= 6.0:
    category = "INVEST"
elif BV_Score >= 6.0 and TQ_Score < 6.0:
    category = "TOLERATE"
elif BV_Score < 6.0 and TQ_Score >= 6.0:
    category = "MIGRATE"
else:  # BV_Score < 6.0 and TQ_Score < 6.0
    category = "ELIMINATE"
```

The actual implementation includes additional logic for edge cases, such as:
- Critical business applications with severe technical issues → MIGRATE (not TOLERATE)
- Redundant applications regardless of quality → ELIMINATE or CONSOLIDATE
- Applications at threshold boundaries → Context-based decisions

---

## Configuration

### Default Thresholds

Located in `config/time_config.yaml`:

```yaml
time_thresholds:
  business_value_threshold: 6.0      # High BV cutoff
  technical_quality_threshold: 6.0    # High TQ cutoff
  composite_score_high: 65.0          # High performer
  composite_score_low: 40.0           # Low performer
  critical_business_value: 8.0        # Mission-critical
  poor_tech_health: 4.0               # Technically troubled
  poor_security: 5.0                  # Security risk
```

### Customizing Thresholds

Edit `config/time_config.yaml` to adjust for your organization:

#### Conservative Approach (Fewer Investments)
```yaml
time_thresholds:
  business_value_threshold: 7.0      # Higher bar for high BV
  technical_quality_threshold: 7.0    # Higher bar for high TQ
```

#### Aggressive Rationalization (More Eliminations)
```yaml
time_thresholds:
  business_value_threshold: 5.0      # Lower bar for high BV
  technical_quality_threshold: 5.0    # Lower bar for high TQ
```

#### Security-Focused
```yaml
time_thresholds:
  poor_security: 6.0                  # Stricter security threshold
dimension_weights:
  technical_quality:
    security: 0.4                      # Increased from 0.3
```

---

## Usage Examples

### Basic Usage (Python Script)

```python
from src.time_framework import TIMEFramework
from src.data_handler import DataHandler

# Initialize
time_framework = TIMEFramework()
data_handler = DataHandler()

# Load applications with scores
df = data_handler.read_csv('output/results.csv')
applications = df.to_dict('records')

# Categorize applications
categorized = time_framework.batch_categorize(applications)

# Get summary
summary = time_framework.get_category_summary()
print(f"Invest: {summary['distribution']['Invest']}")
print(f"Tolerate: {summary['distribution']['Tolerate']}")
print(f"Migrate: {summary['distribution']['Migrate']}")
print(f"Eliminate: {summary['distribution']['Eliminate']}")
```

### Using Main Script

```bash
# Run assessment with TIME framework (automatic)
python main.py
```

Output includes:
```
TIME FRAMEWORK DISTRIBUTION
================================================================================

Invest                          14 applications ( 46.7%)
Tolerate                         8 applications ( 26.7%)
Migrate                          5 applications ( 16.7%)
Eliminate                        3 applications ( 10.0%)
```

### Using CLI

```bash
# Run assessment with TIME categorization
python -m src.cli assess -i data/portfolio.csv -o output/results.csv

# Filter by TIME category
python -m src.cli list-apps -i output/results.csv -tc Eliminate

# Show applications in Invest category
python -m src.cli list-apps -i output/results.csv -tc Invest -t 20
```

### Custom Thresholds

```python
from src.time_framework import TIMEFramework, TIMEThresholds

# Create custom thresholds
custom_thresholds = TIMEThresholds(
    business_value_threshold=7.0,
    technical_quality_threshold=7.0,
    composite_score_high=70.0,
    composite_score_low=35.0
)

# Use custom thresholds
time_framework = TIMEFramework(thresholds=custom_thresholds)
```

---

## Integration with Recommendations

The TIME framework works alongside the detailed recommendation engine:

| TIME Category | Typical Recommendations |
|---------------|------------------------|
| **INVEST** | Retain, Invest |
| **TOLERATE** | Tolerate, Maintain, Migrate (if critical issues) |
| **MIGRATE** | Migrate, Consolidate |
| **ELIMINATE** | Retire, Eliminate, Immediate Action Required |

### Output Columns

Complete assessment output includes:

- **Composite Score**: Overall score (0-100)
- **Action Recommendation**: Specific action (Retain, Invest, Migrate, etc.)
- **Comments**: Detailed rationale
- **TIME Category**: TIME framework category
- **TIME Rationale**: TIME-specific reasoning
- **TIME Business Value Score**: BV dimension score (0-10)
- **TIME Technical Quality Score**: TQ dimension score (0-10)

### Example Output

```csv
Application Name,Composite Score,Action Recommendation,TIME Category,TIME BV Score,TIME TQ Score
Customer Portal,83.8,Invest,Invest,8.9,7.8
Legacy Billing,48.2,Migrate,Tolerate,7.2,4.1
Old FTP Server,21.5,Retire,Eliminate,2.1,3.2
```

---

## Customization Guide

### Extending TIME Logic

To modify categorization logic, edit `src/time_framework.py`:

```python
def _apply_time_logic(self, ...):
    """Custom TIME categorization logic."""

    # Your custom rules here
    if your_condition:
        return ("INVEST", "Your custom rationale")

    # Fall back to standard logic
    ...
```

### Adding New Criteria

1. Update dimension calculations in `calculate_business_value_score()` or `calculate_technical_quality_score()`
2. Adjust weights in `config/time_config.yaml`
3. Update documentation

### Creating Custom Categories

Extend the `TIMECategory` enum:

```python
class TIMECategory(Enum):
    INVEST = "Invest"
    TOLERATE = "Tolerate"
    MIGRATE = "Migrate"
    ELIMINATE = "Eliminate"
    TRANSFORM = "Transform"  # New custom category
```

---

## Best Practices

### 1. Threshold Calibration

Start with defaults and adjust based on results:

```python
# Run with defaults first
results1 = assess_with_defaults()

# Review distribution
analyze_distribution(results1)

# Adjust and rerun
results2 = assess_with_adjusted_thresholds()
```

### 2. Stakeholder Alignment

- Present the TIME matrix to stakeholders
- Get consensus on threshold values
- Document decisions and rationale
- Review quarterly or annually

### 3. Portfolio Balancing

Aim for a balanced portfolio:

- **INVEST**: 20-30% (strategic growth)
- **TOLERATE**: 20-30% (managed risk)
- **MIGRATE**: 20-30% (optimization)
- **ELIMINATE**: 10-20% (cleanup)

### 4. Action Planning

Prioritize within each category:

**INVEST:**
- Rank by strategic value
- Focus on highest ROI enhancements

**TOLERATE:**
- Prioritize by risk level
- Plan migrations for highest-risk first

**MIGRATE:**
- Start with easiest consolidations
- Build momentum with quick wins

**ELIMINATE:**
- Begin with zero-usage applications
- Progress to low-usage, redundant apps

### 5. Regular Reassessment

- **Quarterly**: Review high-risk TOLERATE apps
- **Biannually**: Update all scores and categories
- **Annually**: Recalibrate thresholds and weights

### 6. Documentation

Document all decisions:

```csv
Application,TIME Category,Date,Decision,Rationale,Owner
Legacy CRM,TOLERATE → MIGRATE,2025-Q2,Plan migration,Security risks increasing,IT Architecture
```

### 7. Communication

Create visualizations:

```python
# Generate TIME matrix chart
matrix = time_framework.get_portfolio_matrix(applications)

# Display distribution
print_matrix_visualization(matrix)
```

---

## Troubleshooting

### Issue: Too Many INVEST Applications

**Problem:** 60%+ applications categorized as INVEST

**Solution:**
- Increase `business_value_threshold` to 7.0
- Increase `technical_quality_threshold` to 7.0
- Review scoring criteria for inflation

### Issue: Too Many ELIMINATE Applications

**Problem:** 40%+ applications categorized as ELIMINATE

**Solution:**
- Decrease thresholds to 5.0-5.5
- Review if scores are too harsh
- Validate data quality

### Issue: Disagreement with Results

**Problem:** Stakeholders disagree with categorization

**Solution:**
- Review individual dimension scores
- Examine rationale text
- Adjust dimension weights
- Recalibrate with sample applications

---

## Additional Resources

- **Scoring Methodology**: See `docs/scoring_methodology.md`
- **Workflow Guide**: See `docs/workflow.md`
- **Configuration Examples**: See `config/time_config.yaml`
- **Code Implementation**: See `src/time_framework.py`

---

**Document Version:** 1.0
**Last Updated:** November 2025
**Owner:** Application Rationalization Team
