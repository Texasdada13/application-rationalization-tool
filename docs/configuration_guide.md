# Configuration Guide

This guide explains how to customize the Application Rationalization Assessment Tool through configuration files.

## Table of Contents

1. [Overview](#overview)
2. [Configuration Files](#configuration-files)
3. [Scoring Weights Configuration](#scoring-weights-configuration)
4. [TIME Framework Configuration](#time-framework-configuration)
5. [Configuration Loading](#configuration-loading)
6. [Programmatic Configuration](#programmatic-configuration)
7. [Examples](#examples)
8. [Best Practices](#best-practices)

## Overview

The tool supports flexible configuration through YAML files, allowing you to customize:

- **Scoring weights** for composite score calculation
- **TIME framework thresholds** for categorization
- **Normalization parameters** for cost and usage
- **Output settings** for reports and files
- **Organization information** for branding

### Configuration Hierarchy

Configuration is loaded in cascading order (later overrides earlier):

```
1. Built-in defaults (hardcoded)
     ↓
2. config/config.yaml (global configuration)
     ↓
3. config/config.local.yaml (user-specific, gitignored)
     ↓
4. Runtime parameters (command-line arguments)
```

##Configuration Files

### config/config.yaml

**Purpose:** Global default configuration for the entire project.

**Location:** `config/config.yaml`

**Version Control:** Committed to git, shared across all users

**Use When:**
- Setting organization-wide defaults
- Defining standard weights for all assessments
- Establishing baseline configurations

**Example:**
```yaml
scoring_weights:
  business_value: 0.25
  tech_health: 0.20
  cost: 0.15
  usage: 0.15
  security: 0.10
  strategic_fit: 0.10
  redundancy: 0.05
```

### config/config.local.yaml

**Purpose:** User-specific or environment-specific overrides.

**Location:** `config/config.local.yaml`

**Version Control:** Gitignored, not shared

**Use When:**
- Testing different configurations
- User-specific customizations
- Temporary experimental settings
- Sensitive configuration values

**Example:**
```yaml
# Override just the weights you want to change
scoring_weights:
  security: 0.25  # Increase security weight
  business_value: 0.20  # Decrease business value
```

### Creating Configuration Files

```bash
# Copy example to create global config
cp config/config.example.yaml config/config.yaml

# Create user-specific config
cp config/config.example.yaml config/config.local.yaml
# Edit config.local.yaml as needed
```

## Scoring Weights Configuration

Scoring weights determine how different criteria contribute to the composite score.

### Weight Requirements

1. **Must sum to 1.0** (100%)
2. **Range: 0.0 to 1.0** for each weight
3. **Higher weight = more importance** in final score

### Available Weights

| Weight | Default | Description | Impact of Increase |
|--------|---------|-------------|-------------------|
| `business_value` | 25% | Business value and impact | Rewards high-value applications |
| `tech_health` | 20% | Technical health | Rewards well-maintained apps |
| `cost` | 15% | Annual cost (inverted) | Rewards low-cost applications |
| `usage` | 15% | Active usage | Rewards highly-used applications |
| `security` | 10% | Security posture | Rewards secure applications |
| `strategic_fit` | 10% | Strategic alignment | Rewards strategically aligned apps |
| `redundancy` | 5% | Redundancy (inverted) | Penalizes redundant applications |

### Configuration Examples

#### Example 1: Security-First Organization

```yaml
scoring_weights:
  business_value: 0.20
  tech_health: 0.20
  cost: 0.10
  usage: 0.10
  security: 0.25      # Increased from 0.10
  strategic_fit: 0.10
  redundancy: 0.05
```

**Use Case:** Healthcare, financial services, government sectors

**Impact:**
- Applications with high security scores rank higher
- Security vulnerabilities more heavily penalized
- Encourages investment in secure applications

#### Example 2: Cost Reduction Initiative

```yaml
scoring_weights:
  business_value: 0.20
  tech_health: 0.15
  cost: 0.30          # Increased from 0.15
  usage: 0.15
  security: 0.08
  strategic_fit: 0.07
  redundancy: 0.05
```

**Use Case:** Budget constraints, cost optimization programs

**Impact:**
- Expensive applications ranked lower
- Strong incentive for cost reduction
- Retirement of high-cost, low-value apps

#### Example 3: Digital Transformation

```yaml
scoring_weights:
  business_value: 0.20
  tech_health: 0.25    # Increased from 0.20
  cost: 0.10
  usage: 0.10
  security: 0.10
  strategic_fit: 0.20  # Increased from 0.10
  redundancy: 0.05
```

**Use Case:** Cloud migration, modernization initiatives

**Impact:**
- Modern, well-architected apps rank higher
- Strategic alignment more important
- Legacy apps with poor tech health rank lower

#### Example 4: Business Value Driven

```yaml
scoring_weights:
  business_value: 0.35  # Increased from 0.25
  tech_health: 0.15
  cost: 0.10
  usage: 0.20          # Increased from 0.15
  security: 0.08
  strategic_fit: 0.07
  redundancy: 0.05
```

**Use Case:** Product companies, customer-focused organizations

**Impact:**
- High business value apps strongly preferred
- User adoption highly valued
- Technical debt tolerated if business value high

#### Example 5: Balanced Approach

```yaml
scoring_weights:
  business_value: 0.20
  tech_health: 0.20
  cost: 0.15
  usage: 0.15
  security: 0.15
  strategic_fit: 0.10
  redundancy: 0.05
```

**Use Case:** Mature portfolio management, no specific crisis

**Impact:**
- Equal consideration across criteria
- Well-rounded assessment
- No single factor dominates

## TIME Framework Configuration

Configure thresholds for TIME categorization.

### Available Thresholds

```yaml
time_thresholds:
  # High business value cutoff (0-10 scale)
  business_value_threshold: 6.0

  # High technical quality cutoff (0-10 scale)
  technical_quality_threshold: 6.0

  # Composite score thresholds (0-100 scale)
  composite_score_high: 65.0
  composite_score_low: 40.0

  # Critical values (0-10 scale)
  critical_business_value: 8.0
  poor_tech_health: 4.0
  poor_security: 5.0
```

### Threshold Adjustment Guidelines

#### Conservative (Fewer Investments)

```yaml
time_thresholds:
  business_value_threshold: 7.0      # Higher bar
  technical_quality_threshold: 7.0    # Higher bar
  composite_score_high: 70.0         # Higher bar
```

**Effect:** More applications in Tolerate/Migrate/Eliminate categories

#### Aggressive (More Investments)

```yaml
time_thresholds:
  business_value_threshold: 5.0      # Lower bar
  technical_quality_threshold: 5.0    # Lower bar
  composite_score_high: 60.0         # Lower bar
```

**Effect:** More applications in Invest category

## Configuration Loading

### Automatic Loading

Configuration is loaded automatically by the tool:

```python
# In your code
from src.config_loader import load_config

# Load configuration (automatic cascading)
config = load_config()

# Get configured weights
weights = config.get_scoring_weights()

# Get TIME thresholds
thresholds = config.get_time_thresholds()
```

### Manual Loading

```python
from pathlib import Path
from src.config_loader import ConfigLoader

# Load from specific directory
config = ConfigLoader(config_dir=Path('/path/to/config'))

# Access configuration values
max_cost = config.get_config_value('normalization.max_cost')
org_name = config.get_config_value('organization.name')
```

### Viewing Current Configuration

```bash
# View current configuration from command line
python -c "from src.config_loader import load_config; print(load_config().display_current_config())"
```

Output:
```
Current Configuration:
============================================================

Scoring Weights:
  business_value       0.25 (25%)
  tech_health          0.20 (20%)
  cost                 0.15 (15%)
  usage                0.15 (15%)
  security             0.10 (10%)
  strategic_fit        0.10 (10%)
  redundancy           0.05 (5%)
  TOTAL                1.00 (100%)

TIME Framework Thresholds:
  business_value_threshold       6.0
  technical_quality_threshold    6.0
  ...
```

## Programmatic Configuration

### Setting Values at Runtime

```python
from src.config_loader import ConfigLoader

# Load configuration
config = ConfigLoader()

# Modify weights
config.set_config_value('scoring_weights.security', 0.30)
config.set_config_value('scoring_weights.business_value', 0.20)

# Get updated weights
weights = config.get_scoring_weights()
```

### Saving Configuration

```python
# Save modified configuration
config.save_config(Path('config/my_custom.yaml'))

# Or save to local config (default)
config.save_config()  # Saves to config.local.yaml
```

### Validation

```python
# Weights are automatically validated
try:
    weights = config.get_scoring_weights()
    print("Weights valid!")
except ValueError as e:
    print(f"Invalid weights: {e}")
```

## Examples

### Example 1: Quick Configuration Change

```bash
# Edit config file
vi config/config.local.yaml

# Add your changes:
scoring_weights:
  security: 0.25

# Run assessment (uses new config automatically)
python main.py
```

### Example 2: Test Multiple Configurations

```python
# test_configs.py
from src.config_loader import ConfigLoader
from src.scoring_engine import ScoringEngine

configs = [
    {'name': 'default', 'security': 0.10},
    {'name': 'high_security', 'security': 0.25},
    {'name': 'balanced', 'security': 0.15}
]

for cfg in configs:
    config = ConfigLoader()
    config.set_config_value('scoring_weights.security', cfg['security'])
    config.set_config_value('scoring_weights.business_value', 0.25 - (cfg['security'] - 0.10))

    weights = config.get_scoring_weights()
    engine = ScoringEngine(weights=weights)

    # Run assessment with this configuration
    print(f"Testing {cfg['name']} configuration...")
    # ... assessment code ...
```

### Example 3: Organization-Specific Config

```yaml
# config/config.yaml
scoring_weights:
  business_value: 0.30  # Acme Corp prioritizes business value
  tech_health: 0.20
  cost: 0.15
  usage: 0.15
  security: 0.10
  strategic_fit: 0.05
  redundancy: 0.05

organization:
  name: "Acme Corporation"
  cycle: "FY2025 Q1"
  owner: "Enterprise Architecture Team"
  contact: "ea-team@acme.com"

normalization:
  max_cost: 500000     # Acme has higher cost apps
  max_usage: 2000      # Acme has high-usage apps
```

## Best Practices

### 1. Document Your Decisions

```yaml
# config/config.yaml
# Decision: 2025-01-15 by Architecture Team
# Rationale: Emphasize security due to recent audit findings
scoring_weights:
  security: 0.25  # Increased from 0.10 per security review
  business_value: 0.20  # Reduced to accommodate security increase
```

### 2. Version Control Global Config

- ✅ Commit `config/config.yaml`
- ✅ Commit `config/config.example.yaml`
- ❌ Don't commit `config/config.local.yaml`
- ✅ Document changes in commit messages

### 3. Test Before Applying

```bash
# Test configuration with sample data
python -m src.cli assess -i data/sample.csv -o output/test.csv

# Review results before production use
```

### 4. Validate Weights Sum to 1.0

```python
# Tool validates automatically, but double-check:
weights = {
    'business_value': 0.25,
    'tech_health': 0.20,
    'cost': 0.15,
    'usage': 0.15,
    'security': 0.10,
    'strategic_fit': 0.10,
    'redundancy': 0.05
}

assert sum(weights.values()) == 1.0, "Weights must sum to 1.0"
```

### 5. Start Conservative

When uncertain:
1. Start with default balanced weights
2. Run initial assessment
3. Review results with stakeholders
4. Adjust weights incrementally
5. Rerun and compare

### 6. Use Meaningful Names

```yaml
# Good: Descriptive organization info
organization:
  name: "Global Retail Corp - NA Region"
  cycle: "2025 Portfolio Optimization Initiative"
  owner: "Application Portfolio Management Office"

# Avoid: Generic info
organization:
  name: "My Org"
  cycle: "Q1"
```

### 7. Regular Reviews

- Review weights quarterly
- Adjust based on changing priorities
- Document all changes
- Keep history of configurations

## Troubleshooting

### Issue: Weights Don't Sum to 1.0

**Error:**
```
WARNING - Scoring weights do not sum to 1.0. Sum: 0.95
```

**Solution:**
```yaml
# Check all weights add up
scoring_weights:
  business_value: 0.25
  tech_health: 0.20
  cost: 0.15
  usage: 0.15
  security: 0.10
  strategic_fit: 0.10
  redundancy: 0.05
  # Total: 1.00 ✓
```

### Issue: Configuration Not Loading

**Problem:** Changes to config file not reflected

**Solutions:**
1. Check file location: `config/config.yaml` or `config/config.local.yaml`
2. Verify YAML syntax (use YAML linter)
3. Clear Python cache: `find . -type d -name __pycache__ -exec rm -rf {} +`
4. Restart Python process

### Issue: Invalid YAML Syntax

**Error:**
```
Error parsing YAML config file: ...
```

**Solution:**
- Use online YAML validator
- Check indentation (spaces, not tabs)
- Ensure colons have spaces after them
- Quote strings with special characters

## Advanced Usage

### Environment-Specific Configs

```bash
# Development
export CONFIG_ENV=dev
# Use config/config.dev.yaml

# Production
export CONFIG_ENV=prod
# Use config/config.prod.yaml
```

### Dynamic Weight Calculation

```python
# Calculate weights based on portfolio characteristics
def calculate_dynamic_weights(portfolio_stats):
    if portfolio_stats['avg_security'] < 5:
        return {'security': 0.25, 'business_value': 0.20, ...}
    else:
        return {'security': 0.10, 'business_value': 0.30, ...}
```

---

**Document Version:** 1.0
**Last Updated:** January 2025
**Owner:** Application Rationalization Team
