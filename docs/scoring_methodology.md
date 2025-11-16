# Scoring Methodology

This document provides detailed information about the scoring methodology used in the Application Rationalization Assessment Tool.

## Overview

The tool uses a weighted multi-criteria decision analysis (MCDA) approach to evaluate applications. Each application receives a composite score from 0-100 based on seven key criteria.

## Scoring Criteria

### 1. Business Value (Weight: 25%)

**Definition:** The value an application delivers to the business.

**Scale:** 0-10

**Scoring Guidelines:**

| Score | Description | Characteristics |
|-------|-------------|-----------------|
| 9-10 | Critical | Mission-critical, revenue-generating, strategic advantage |
| 7-8 | High | Important business function, significant impact |
| 5-6 | Medium | Useful but not essential, moderate impact |
| 3-4 | Low | Minimal business impact, convenience only |
| 0-2 | Negligible | Little to no business value, unused |

**Evaluation Factors:**
- Revenue impact (direct or indirect)
- Customer satisfaction impact
- Operational efficiency gains
- Regulatory/compliance requirements
- Number of business processes supported
- Strategic importance

### 2. Technical Health (Weight: 20%)

**Definition:** The technical condition and maintainability of the application.

**Scale:** 0-10

**Scoring Guidelines:**

| Score | Description | Characteristics |
|-------|-------------|-----------------|
| 9-10 | Excellent | Modern architecture, clean code, well-maintained |
| 7-8 | Good | Solid architecture, manageable technical debt |
| 5-6 | Fair | Aging but functional, some technical debt |
| 3-4 | Poor | Significant technical debt, difficult to maintain |
| 0-2 | Critical | Obsolete technology, unmaintainable |

**Evaluation Factors:**
- Code quality and maintainability
- Architecture soundness
- Technology stack currency
- Performance and scalability
- Availability and reliability
- Documentation quality
- Ease of updates/changes

### 3. Cost (Weight: 15%)

**Definition:** Annual total cost of ownership.

**Input:** Dollar amount (e.g., $50,000)

**Normalization:**
- Costs are normalized to a 0-10 scale
- Lower cost = higher score
- Default max cost for normalization: $300,000

**Formula:**
```
Cost Score = 10 × (1 - min(cost / max_cost, 1.0))
```

**Components to Include:**
- Software licensing fees
- Infrastructure costs (servers, storage, network)
- Support and maintenance contracts
- Personnel costs (dedicated staff)
- Integration and interface costs
- Training costs
- Hidden costs (e.g., workarounds, manual processes)

### 4. Usage (Weight: 15%)

**Definition:** Level of actual usage of the application.

**Input:** Numeric metric (e.g., daily active users, transactions)

**Normalization:**
- Usage is normalized to a 0-10 scale
- Higher usage = higher score
- Default max usage for normalization: 1,000

**Formula:**
```
Usage Score = 10 × min(usage / max_usage, 1.0)
```

**Suggested Metrics:**
- Daily or monthly active users
- Transaction volume
- API call volume
- Session count
- Business transactions processed

### 5. Security (Weight: 10%)

**Definition:** Security posture and compliance status.

**Scale:** 0-10

**Scoring Guidelines:**

| Score | Description | Characteristics |
|-------|-------------|-----------------|
| 9-10 | Excellent | No vulnerabilities, full compliance, best practices |
| 7-8 | Good | Minor issues only, generally compliant |
| 5-6 | Fair | Some vulnerabilities, compliance gaps |
| 3-4 | Poor | Significant vulnerabilities, compliance issues |
| 0-2 | Critical | Critical vulnerabilities, major compliance failures |

**Evaluation Factors:**
- Known vulnerabilities (CVEs)
- Security testing results
- Authentication/authorization strength
- Data encryption (at rest and in transit)
- Compliance with regulations (GDPR, HIPAA, etc.)
- Security incident history
- Patch currency
- Access controls

### 6. Strategic Fit (Weight: 10%)

**Definition:** Alignment with organizational strategy and future direction.

**Scale:** 0-10

**Scoring Guidelines:**

| Score | Description | Characteristics |
|-------|-------------|-----------------|
| 9-10 | Strategic | Core to future strategy, competitive advantage |
| 7-8 | High | Supports strategic objectives, future-ready |
| 5-6 | Medium | Aligned but not strategic, adequate fit |
| 3-4 | Low | Misaligned with strategy, declining relevance |
| 0-2 | None | Counter to strategy, legacy burden |

**Evaluation Factors:**
- Alignment with business strategy
- Support for future business models
- Innovation enablement
- Market differentiation
- Digital transformation readiness
- Cloud/modern architecture alignment

### 7. Redundancy (Weight: 5%)

**Definition:** Whether application functionality is duplicated elsewhere.

**Scale:** Binary (0 or 1)
- 0 = Unique functionality
- 1 = Redundant/duplicate functionality

**Conversion to Score:**
```
Redundancy Score = 10 × (1 - redundancy)
```
- Unique (0) → Score of 10
- Redundant (1) → Score of 0

**Evaluation:**
- Does another application provide the same capabilities?
- Could this application's functions be consolidated?
- Are there overlapping features with other applications?
- Is there a primary system that should be used instead?

## Composite Score Calculation

### Formula

```
Composite Score = (
    Business_Value × 0.25 +
    Tech_Health × 0.20 +
    Cost_Score × 0.15 +
    Usage_Score × 0.15 +
    Security × 0.10 +
    Strategic_Fit × 0.10 +
    Redundancy_Score × 0.05
) × 10
```

### Example Calculation

**Application: Customer Portal**

| Criterion | Input | Normalized Score | Weight | Contribution |
|-----------|-------|------------------|--------|--------------|
| Business Value | 9 | 9.0 | 0.25 | 2.25 |
| Tech Health | 7 | 7.0 | 0.20 | 1.40 |
| Cost | $50,000 | 8.33 | 0.15 | 1.25 |
| Usage | 850 users | 8.50 | 0.15 | 1.28 |
| Security | 8 | 8.0 | 0.10 | 0.80 |
| Strategic Fit | 9 | 9.0 | 0.10 | 0.90 |
| Redundancy | 0 | 10.0 | 0.05 | 0.50 |
| **TOTAL** | | | | **8.38** |

**Composite Score = 8.38 × 10 = 83.8 / 100**

This score of 83.8 indicates a high-performing application that should be retained and potentially invested in.

## Retention Score

In addition to the composite score, the tool calculates a **Retention Score** that emphasizes critical factors:

### Formula

```
Retention Score = (
    Composite_Score × 0.5 +
    ((Business_Value + Tech_Health + Security) / 3) × 10 × 0.5
)
```

### Purpose

The retention score helps identify applications that should be kept regardless of cost considerations, by placing extra emphasis on:
- Business criticality
- Technical viability
- Security requirements

## Customizing Weights

Organizations can customize weights to match their priorities:

### Example: Security-First Organization

```python
weights = ScoringWeights(
    business_value=0.20,
    tech_health=0.15,
    cost=0.15,
    usage=0.10,
    security=0.25,      # Increased from 0.10
    strategic_fit=0.10,
    redundancy=0.05
)
```

### Example: Cost-Reduction Initiative

```python
weights = ScoringWeights(
    business_value=0.20,
    tech_health=0.15,
    cost=0.25,          # Increased from 0.15
    usage=0.15,
    security=0.10,
    strategic_fit=0.10,
    redundancy=0.05
)
```

### Example: Digital Transformation

```python
weights = ScoringWeights(
    business_value=0.20,
    tech_health=0.25,   # Increased from 0.20
    cost=0.10,
    usage=0.10,
    security=0.10,
    strategic_fit=0.20, # Increased from 0.10
    redundancy=0.05
)
```

## Score Interpretation

### Score Ranges

| Range | Interpretation | Typical Action |
|-------|----------------|----------------|
| 80-100 | Excellent | Retain, Invest |
| 70-79 | Good | Retain, Maintain |
| 50-69 | Fair | Maintain, Tolerate, Migrate |
| 30-49 | Poor | Migrate, Consolidate, Retire |
| 0-29 | Critical | Retire, Immediate Action |

### Caveats

Scores should not be used in isolation:

1. **Context Matters**: A critical application with a low score may need immediate investment, not retirement
2. **Trending**: Score changes over time are as important as absolute scores
3. **Outliers**: Extreme values in any criterion warrant investigation
4. **Stakeholder Input**: Scores inform decisions but don't replace judgment

## Quality Assurance

### Data Validation

The tool automatically validates:
- Score ranges (0-10 for subjective criteria)
- Positive values (cost, usage)
- Binary values (redundancy)
- Required fields

### Calibration Sessions

**Recommended practice:**

1. Score a sample of applications with stakeholders
2. Review and discuss scores
3. Adjust criteria definitions as needed
4. Establish organizational benchmarks
5. Document scoring decisions for consistency

### Sensitivity Analysis

Test how weight changes affect results:

```python
# Original weights
original_score = calculate_score(app, original_weights)

# Adjusted weights
adjusted_score = calculate_score(app, adjusted_weights)

# Compare
difference = adjusted_score - original_score
```

## Limitations and Considerations

### Subjectivity

Some criteria involve subjective judgment:
- Business value assessments vary by stakeholder
- Technical health depends on evaluator expertise
- Strategic fit requires organizational context

**Mitigation:**
- Use multiple evaluators
- Provide clear scoring guidelines
- Calibrate with examples
- Document rationale

### Data Availability

Some data may be difficult to obtain:
- Accurate usage metrics
- True total cost of ownership
- Complete security assessments

**Mitigation:**
- Use best available estimates
- Document assumptions
- Improve data over time
- Focus on relative rankings

### Temporal Validity

Scores can become outdated:
- Business priorities change
- Technology evolves
- Costs fluctuate
- Usage patterns shift

**Mitigation:**
- Regular reassessment (quarterly/annually)
- Update criteria as needed
- Track trends over time
- Version assessment data

## Best Practices

1. **Consistent Application**: Use the same criteria and weights across all applications in a portfolio

2. **Documentation**: Record the rationale for scores, especially for outliers

3. **Validation**: Have application owners review and confirm scores

4. **Iteration**: Refine scores based on stakeholder feedback

5. **Transparency**: Share methodology and results openly

6. **Action-Oriented**: Use scores to drive decisions, not just documentation

7. **Continuous Improvement**: Learn from each assessment cycle and refine the approach

---

**Document Version:** 1.0
**Last Updated:** November 2025
**Owner:** Application Rationalization Team
