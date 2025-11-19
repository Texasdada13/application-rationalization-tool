# Screenshot Guide for PowerPoint Presentation

## Generated Data Summary

### Application Portfolio (211 apps)
- **Total Cost**: $22.6M annually
- **Average Cost**: $107K per app
- **Tech Health Distribution**:
  - Excellent (8-10): 17.5% (37 apps)
  - Good (6-7): 28.4% (60 apps)
  - Fair (4-5): 28.9% (61 apps)
  - Poor (1-3): 25.1% (53 apps)

### Stakeholder Survey (1,397 responses)
- **Sentiment Distribution**:
  - Negative: 41.9% (586 responses)
  - Positive: 29.6% (414 responses)
  - Neutral: 28.4% (397 responses)
- **Average**: 6.6 responses per application
- **Rating Distribution**:
  - 1 star: 21.3%
  - 2 stars: 20.6%
  - 3 stars: 28.4%
  - 4 stars: 14.3%
  - 5 stars: 15.3%

---

## How to Use for PowerPoint Screenshots

### Step 1: Load Survey Data into Dashboard

1. **Navigate to**: http://localhost:5000/sentiment_analysis
2. **Upload file**: `data/stakeholder_survey.csv`
3. **The page will display**:
   - Overall sentiment breakdown (pie chart)
   - Application-level sentiment scores
   - Common themes and keywords
   - Top negative and positive apps

### Step 2: Key Screenshots to Capture

#### Screenshot 1: Dashboard Overview
**URL**: http://localhost:5000/dashboard
**What to show**:
- Total Applications: 211
- Total Annual Cost: $22.6M
- Average Health Score
- Predictive Cost & Risk section (collapsed header)

**PowerPoint Talking Point**:
> "Current state: 211 applications costing $22.6M annually, with 25% in poor technical health"

---

#### Screenshot 2: Sentiment Analysis Overview
**URL**: http://localhost:5000/sentiment_analysis
**What to show**:
- Sentiment pie chart (42% negative)
- Top 10 applications with worst sentiment
- Common complaint themes

**PowerPoint Talking Point**:
> "Stakeholder feedback reveals 42% negative sentiment, concentrated in 50+ legacy applications. Common complaints: slow performance, poor usability, frequent crashes"

---

#### Screenshot 3: High-Cost, Low-Value Apps
**URL**: http://localhost:5000/dashboard (scroll to portfolio table)
**Filter by**:
- Business Value < 5
- Cost > $50,000
- Tech Health < 4

**PowerPoint Talking Point**:
> "15-20 applications consuming $2.1M annually with minimal business value and poor technical health - prime retirement candidates"

---

#### Screenshot 4: Predictive Modeling
**URL**: http://localhost:5000/dashboard
**Click**: "Predictive Cost & Risk Modeling" to expand
**What to show**:
- 3-year cost forecast chart
- High-risk applications table
- ROI analysis

**PowerPoint Talking Point**:
> "Without action, portfolio costs will grow to $25M+ by 2027. Retiring 50 applications can save $5M+ over 3 years"

---

#### Screenshot 5: Smart Recommendations
**URL**: http://localhost:5000/smart_recommendations
**What to show**:
- Retirement candidates with savings projection
- Modernization opportunities
- Consolidation potential

**PowerPoint Talking Point**:
> "Data-driven recommendations identify clear action plan: retire 50 apps, modernize 15 strategic systems, consolidate 20 redundant tools"

---

## Sample PowerPoint Slide Content

### Slide 1: Executive Summary
**Visual**: Dashboard overview screenshot

**Content**:
- 211 applications in current portfolio
- $22.6M annual operating cost
- 53 applications (25%) in critical/poor health
- 42% negative stakeholder sentiment
- **Opportunity**: $5M+ savings over 3 years

---

### Slide 2: Stakeholder Sentiment Analysis
**Visual**: Sentiment analysis screenshot

**Content**:
**Top Issues Identified:**
1. **Performance Problems** (35% of complaints)
   - "System is painfully slow and frequently times out"
   - "Takes 5+ minutes just to log in"
   - "Freezes constantly, have to restart multiple times daily"

2. **Usability Issues** (28% of complaints)
   - "Interface is confusing and not intuitive at all"
   - "Way too complicated for what it should do"
   - "User interface from the 1990s"

3. **Reliability Concerns** (22% of complaints)
   - "Crashes multiple times per week"
   - "System goes down frequently"
   - "Data integrity issues - can't trust the information"

**Impact**: $9.5M spent annually on applications with negative user sentiment

---

### Slide 3: Retirement Candidates
**Visual**: Filtered portfolio table screenshot

**Sample Apps to Highlight**:
| Application | Cost | Business Value | Tech Health | Sentiment | Action |
|-------------|------|----------------|-------------|-----------|--------|
| Legacy Billing System | $289K | 3/10 | 2/10 | 87% Negative | Retire |
| Email Archive Platform | $122K | 1/10 | 2/10 | 82% Negative | Retire |
| Document Management (Old) | $123K | 2/10 | 2/10 | 78% Negative | Retire |

**Total Savings**: $2.1M annually from top 15 retirement candidates

---

### Slide 4: 3-Year Financial Impact
**Visual**: Predictive modeling screenshot

**Scenario Comparison**:
- **Do Nothing**: Costs grow to $25.1M by 2027 (+11%)
- **Aggressive Rationalization**: Costs drop to $17.4M by 2027 (-23%)
- **Net Savings**: $7.7M over 3 years
- **ROI**: 380% on rationalization investment

---

### Slide 5: Recommended Action Plan
**Visual**: Smart recommendations screenshot

**90-Day Action Plan**:
1. **Phase 1 (Days 1-30)**: Retire 15 high-cost, low-value apps → $2.1M annual savings
2. **Phase 2 (Days 31-60)**: Begin modernization of 8 strategic apps → Improve user satisfaction 40%
3. **Phase 3 (Days 61-90)**: Consolidate 20 redundant systems → $1.8M additional savings

**Total Year 1 Impact**: $3.9M savings + 40% user satisfaction improvement

---

## Tips for Great Screenshots

1. **Maximize Browser Window**: Full screen for clean screenshots
2. **Zoom Level**: 90-100% for optimal text size
3. **Hide Browser UI**: Use F11 for fullscreen mode
4. **Capture Tables**: Show 10-15 rows maximum
5. **Highlight Key Data**: Use PowerPoint shapes/arrows to emphasize important numbers

---

## Sample Talking Points

**Opening**:
> "Our analysis of your 211-application portfolio reveals significant opportunities for cost optimization and user experience improvement. Using data-driven insights, we've identified a clear path to $5M+ in savings over the next 3 years."

**Problem Statement**:
> "42% of stakeholder feedback is negative, concentrated in legacy applications consuming $9.5M annually. These systems are slow, unreliable, and frustrating users daily - impacting productivity across 100 employees."

**Solution**:
> "Our rationalization strategy targets three areas: retire 50 end-of-life applications ($2.1M savings), modernize 15 strategic systems (40% satisfaction improvement), and consolidate 20 redundant tools ($1.8M savings)."

**Call to Action**:
> "We recommend beginning with Phase 1 immediately - retiring the 15 highest-impact applications within 30 days to demonstrate quick wins and build momentum for the broader transformation."

---

## File Locations

- **Application Data**: `data/assessment_template.csv`
- **Survey Data**: `data/stakeholder_survey.csv`
- **Dashboard**: http://localhost:5000
- **Sentiment Analysis**: http://localhost:5000/sentiment_analysis
- **Smart Recommendations**: http://localhost:5000/smart_recommendations

---

## Quick Demo Script

1. Start dashboard: Already running at http://localhost:5000
2. Show overview: "211 apps, $22.6M cost"
3. Expand Predictive Modeling: "Costs growing to $25M without action"
4. Navigate to Sentiment: "42% negative, clear problem areas"
5. Navigate to Smart Recommendations: "Data-driven action plan"
6. Show filtered table: "Here are the top retirement candidates"

**Total demo time**: 3-5 minutes
