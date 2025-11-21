# Stakeholder Assessment Tool

## Overview

The Stakeholder Assessment Tool is a comprehensive feature designed to facilitate structured client interviews during application rationalization projects. It enables consultants to capture, analyze, and score stakeholder perspectives on applications within a portfolio, providing valuable qualitative insights that complement quantitative data analysis.

## Purpose & Business Value

### Primary Objectives
- **Standardize Interview Process**: Provide consistent, repeatable interview frameworks for stakeholder engagement
- **Capture Qualitative Insights**: Gather subjective assessments that quantitative data alone cannot provide
- **Identify Hidden Dependencies**: Uncover relationships and dependencies not documented in technical systems
- **Assess Change Readiness**: Evaluate stakeholder willingness and capability to adopt changes
- **Document Institutional Knowledge**: Preserve critical business context that exists only in stakeholder minds

### Key Benefits
- Reduced interview preparation time
- Consistent data collection across multiple stakeholders
- Automated scoring and analysis of responses
- Easy identification of consensus and conflict areas
- Historical tracking of stakeholder sentiment over time

---

## Feature Components

### 1. Interview Session Management
- Create and manage interview sessions
- Associate interviews with specific applications or portfolio-wide assessments
- Track interview status (Scheduled, In Progress, Completed, Reviewed)
- Link multiple stakeholders to single applications

### 2. Stakeholder Profiles
- Capture stakeholder information (name, role, department, contact)
- Define stakeholder types (Executive Sponsor, Business Owner, Power User, IT Support, etc.)
- Track influence level and decision-making authority
- Record relationship to specific applications

### 3. Questionnaire Framework
- Pre-built question templates for different assessment types
- Customizable questions and scoring criteria
- Multiple question types (rating scales, multiple choice, open text)
- Conditional logic for follow-up questions

### 4. Response Capture & Scoring
- Real-time response entry during interviews
- Automatic scoring based on response values
- Support for notes and verbatim quotes
- Flag important insights or concerns

### 5. Analysis & Reporting
- Individual stakeholder assessment reports
- Aggregated views across multiple stakeholders
- Consensus analysis and conflict identification
- Integration with portfolio rationalization scores
- Export capabilities (PDF, Excel, PowerPoint)

---

## Technical Architecture

### File Structure

```
/src/stakeholder_assessment_engine.py    # Core assessment logic
/web/templates/stakeholder_assessment.html  # Main UI template
/web/app.py                                  # Flask routes (additions)
/data/stakeholder_assessments.db            # SQLite database (or use existing)
```

### Data Models

```python
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class StakeholderType(Enum):
    EXECUTIVE_SPONSOR = "Executive Sponsor"
    BUSINESS_OWNER = "Business Owner"
    PRODUCT_MANAGER = "Product Manager"
    POWER_USER = "Power User"
    END_USER = "End User"
    IT_SUPPORT = "IT Support"
    DEVELOPER = "Developer"
    ARCHITECT = "Architect"
    SECURITY_OFFICER = "Security Officer"
    COMPLIANCE_OFFICER = "Compliance Officer"

class InfluenceLevel(Enum):
    DECISION_MAKER = "Decision Maker"
    KEY_INFLUENCER = "Key Influencer"
    CONTRIBUTOR = "Contributor"
    INFORMED = "Informed Only"

class InterviewStatus(Enum):
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    REVIEWED = "Reviewed"
    CANCELLED = "Cancelled"

class QuestionType(Enum):
    RATING_SCALE = "Rating Scale (1-5)"
    RATING_SCALE_10 = "Rating Scale (1-10)"
    MULTIPLE_CHOICE = "Multiple Choice"
    SINGLE_CHOICE = "Single Choice"
    OPEN_TEXT = "Open Text"
    YES_NO = "Yes/No"
    DATE = "Date"

@dataclass
class Stakeholder:
    id: str
    name: str
    email: str
    role: str
    department: str
    stakeholder_type: StakeholderType
    influence_level: InfluenceLevel
    phone: Optional[str] = None
    applications: List[str] = field(default_factory=list)
    notes: str = ""

@dataclass
class Question:
    id: str
    category: str
    text: str
    question_type: QuestionType
    required: bool = True
    options: List[str] = field(default_factory=list)
    weight: float = 1.0
    help_text: str = ""
    follow_up_condition: Optional[Dict] = None

@dataclass
class Response:
    question_id: str
    value: any
    score: float
    notes: str = ""
    verbatim_quote: str = ""
    flagged: bool = False
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class InterviewSession:
    id: str
    stakeholder_id: str
    interviewer: str
    application_ids: List[str]
    status: InterviewStatus
    scheduled_date: datetime
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    responses: List[Response] = field(default_factory=list)
    overall_score: float = 0.0
    summary: str = ""
    action_items: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class AssessmentTemplate:
    id: str
    name: str
    description: str
    questions: List[Question]
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)
```

---

## Interview Questionnaire Structure

### Assessment Categories

The questionnaire is organized into key assessment categories, each targeting specific aspects of stakeholder knowledge and perspective:

#### 1. Business Value & Criticality
*Understand the business importance and impact of the application*

| Question | Type | Weight |
|----------|------|--------|
| How critical is this application to your daily operations? | Rating (1-5) | 1.5 |
| What percentage of your team uses this application regularly? | Multiple Choice | 1.0 |
| What would be the business impact if this application was unavailable for 24 hours? | Single Choice | 1.5 |
| Does this application generate revenue or support revenue-generating activities? | Yes/No | 1.0 |
| How would you rate the strategic importance of this application for future business goals? | Rating (1-5) | 1.2 |

#### 2. User Satisfaction & Experience
*Evaluate user sentiment and experience with the application*

| Question | Type | Weight |
|----------|------|--------|
| How satisfied are you with this application overall? | Rating (1-5) | 1.0 |
| How would you rate the ease of use of this application? | Rating (1-5) | 1.0 |
| How reliable is this application (uptime, performance)? | Rating (1-5) | 1.2 |
| How well does this application meet your current business needs? | Rating (1-5) | 1.3 |
| How would you rate the quality of support for this application? | Rating (1-5) | 0.8 |
| What are the top 3 pain points with this application? | Open Text | 1.0 |

#### 3. Technical Health & Sustainability
*Assess technical aspects from the stakeholder perspective*

| Question | Type | Weight |
|----------|------|--------|
| How well does this application integrate with other systems you use? | Rating (1-5) | 1.2 |
| Have you experienced data quality issues with this application? | Yes/No | 1.0 |
| How would you rate the reporting/analytics capabilities? | Rating (1-5) | 0.9 |
| Is this application accessible on mobile devices when needed? | Yes/No | 0.7 |
| How frequently do you encounter bugs or system errors? | Single Choice | 1.1 |

#### 4. Change Readiness & Migration Potential
*Evaluate willingness and capability to change*

| Question | Type | Weight |
|----------|------|--------|
| How open would your team be to replacing this application? | Rating (1-5) | 1.5 |
| What is the estimated effort to train users on a replacement system? | Single Choice | 1.2 |
| Are there critical customizations that would be difficult to replicate? | Yes/No | 1.3 |
| How dependent are your workflows on this specific application? | Rating (1-5) | 1.4 |
| Have you identified potential replacement solutions? | Yes/No | 0.8 |
| What would be required for a successful migration? | Open Text | 1.0 |

#### 5. Dependencies & Integration
*Identify relationships and dependencies*

| Question | Type | Weight |
|----------|------|--------|
| List all applications this system sends data to | Open Text | 1.5 |
| List all applications this system receives data from | Open Text | 1.5 |
| Are there manual processes that bridge this application to others? | Yes/No | 1.2 |
| How many external partners/vendors interact with this application? | Single Choice | 1.0 |
| Are there regulatory requirements tied to this application's data? | Yes/No | 1.3 |

#### 6. Cost & Resource Awareness
*Understand perceived value and resource utilization*

| Question | Type | Weight |
|----------|------|--------|
| Do you feel this application provides good value for its cost? | Rating (1-5) | 1.0 |
| How much IT support time does this application require? | Single Choice | 1.1 |
| Are there duplicate capabilities in other applications you use? | Yes/No | 1.2 |
| Would consolidating this application's functions save your team time? | Yes/No | 1.0 |

#### 7. Future Needs & Strategic Alignment
*Capture forward-looking requirements*

| Question | Type | Weight |
|----------|------|--------|
| What new capabilities do you need that this application doesn't provide? | Open Text | 1.2 |
| How well does this application align with company digital transformation goals? | Rating (1-5) | 1.3 |
| What is your preferred timeline for addressing this application's future? | Single Choice | 0.9 |
| Would you recommend this application to a colleague? (NPS-style) | Rating (1-10) | 1.1 |

---

## Scoring Methodology

### Response Scoring

#### Rating Scale (1-5)
- 5 = Excellent (1.0)
- 4 = Good (0.8)
- 3 = Adequate (0.6)
- 2 = Poor (0.4)
- 1 = Very Poor (0.2)

#### Rating Scale (1-10)
- Score = Value / 10

#### Yes/No Questions
- Positive responses (context-dependent) = 1.0
- Negative responses = 0.0
- Some questions may have inverted scoring

#### Multiple Choice
- Pre-defined scores for each option based on context

### Weighted Score Calculation

```python
def calculate_interview_score(responses: List[Response], questions: Dict[str, Question]) -> float:
    total_weighted_score = 0.0
    total_weight = 0.0

    for response in responses:
        question = questions[response.question_id]
        if question.question_type != QuestionType.OPEN_TEXT:
            weighted_score = response.score * question.weight
            total_weighted_score += weighted_score
            total_weight += question.weight

    return (total_weighted_score / total_weight) * 100 if total_weight > 0 else 0.0
```

### Category Scores

Calculate separate scores for each category to identify specific areas of concern:
- Business Value Score
- User Satisfaction Score
- Technical Health Score
- Change Readiness Score
- Dependency Complexity Score
- Cost Efficiency Score
- Strategic Alignment Score

### Aggregate Analysis

When multiple stakeholders assess the same application:
- **Consensus Score**: Average across all stakeholders
- **Variance Analysis**: Identify questions with high variance (conflicting views)
- **Weighted by Influence**: Give more weight to decision-makers
- **Stakeholder Type Analysis**: Compare views across different stakeholder types

---

## User Interface Design

### Main Dashboard View

```
+----------------------------------------------------------+
|  Stakeholder Assessment Tool                              |
+----------------------------------------------------------+
|                                                           |
|  Quick Stats                                              |
|  +--------+  +--------+  +--------+  +--------+          |
|  |   12   |  |   8    |  |   3    |  |   1    |          |
|  |Scheduled|  |Complete|  |In Prog |  |Pending |          |
|  +--------+  +--------+  +--------+  +--------+          |
|                                                           |
|  Actions                                                  |
|  [+ New Interview]  [+ Add Stakeholder]  [Templates]      |
|                                                           |
|  Recent Interviews                          Filter: [All] |
|  +------------------------------------------------------+|
|  | Stakeholder    | Application | Status    | Score | Date|
|  |----------------|-------------|-----------|-------|-----|
|  | John Smith     | SAP ERP     | Completed | 72%   | 3/1 |
|  | Jane Doe       | Salesforce  | In Prog   | --    | 3/2 |
|  | Bob Johnson    | Legacy CRM  | Scheduled | --    | 3/5 |
|  +------------------------------------------------------+|
|                                                           |
|  Assessment Coverage                                      |
|  [Heatmap showing applications vs stakeholders assessed]  |
|                                                           |
+----------------------------------------------------------+
```

### Interview Conduct View

```
+----------------------------------------------------------+
|  Interview: John Smith - SAP ERP                          |
|  Status: In Progress  |  Progress: 15/25 questions        |
+----------------------------------------------------------+
|                                                           |
|  Category: User Satisfaction & Experience         [3/6]   |
|  --------------------------------------------------------|
|                                                           |
|  Q: How satisfied are you with this application overall?  |
|                                                           |
|     1 [  ]  2 [  ]  3 [X]  4 [  ]  5 [  ]                |
|     Very Poor              Adequate              Excellent |
|                                                           |
|  Notes: ____________________________________________      |
|         ____________________________________________      |
|                                                           |
|  [ ] Flag this response                                   |
|                                                           |
|  Verbatim Quote (optional): ________________________      |
|                             ________________________      |
|                                                           |
|  [< Previous]                              [Next >]       |
|                                                           |
|  Progress: [==============          ] 60%                 |
|                                                           |
|  Quick Actions: [Save Draft] [Skip Category] [End Early]  |
+----------------------------------------------------------+
```

### Analysis View

```
+----------------------------------------------------------+
|  Assessment Analysis: SAP ERP                             |
+----------------------------------------------------------+
|                                                           |
|  Overall Score: 68/100        Stakeholders Assessed: 5    |
|                                                           |
|  Category Breakdown                                       |
|  +----------------------------------------------------+  |
|  | Business Value      [================    ] 82%      |  |
|  | User Satisfaction   [==============      ] 71%      |  |
|  | Technical Health    [============        ] 58%      |  |
|  | Change Readiness    [==========          ] 52%      |  |
|  | Dependencies        [===============     ] 75%      |  |
|  | Cost Efficiency     [==============      ] 68%      |  |
|  | Strategic Alignment [===========         ] 55%      |  |
|  +----------------------------------------------------+  |
|                                                           |
|  Stakeholder Comparison                                   |
|  [Radar chart comparing scores by stakeholder]            |
|                                                           |
|  Key Findings                                             |
|  - High business value but low change readiness           |
|  - Technical concerns around integration                  |
|  - Conflicting views on replacement timeline              |
|                                                           |
|  [View Details] [Export Report] [Compare Applications]    |
+----------------------------------------------------------+
```

---

## API Endpoints

### Stakeholder Management
- `GET /api/stakeholders` - List all stakeholders
- `POST /api/stakeholders` - Create new stakeholder
- `GET /api/stakeholders/<id>` - Get stakeholder details
- `PUT /api/stakeholders/<id>` - Update stakeholder
- `DELETE /api/stakeholders/<id>` - Delete stakeholder

### Interview Sessions
- `GET /api/interviews` - List all interviews
- `POST /api/interviews` - Create new interview session
- `GET /api/interviews/<id>` - Get interview details
- `PUT /api/interviews/<id>` - Update interview
- `DELETE /api/interviews/<id>` - Delete interview
- `POST /api/interviews/<id>/start` - Start interview
- `POST /api/interviews/<id>/complete` - Complete interview
- `POST /api/interviews/<id>/responses` - Save responses

### Assessment Templates
- `GET /api/assessment-templates` - List all templates
- `GET /api/assessment-templates/<id>` - Get template details
- `POST /api/assessment-templates` - Create custom template
- `PUT /api/assessment-templates/<id>` - Update template

### Analysis & Reporting
- `GET /api/stakeholder-analysis/<app_id>` - Get aggregated analysis for application
- `GET /api/stakeholder-analysis/portfolio` - Portfolio-wide analysis
- `GET /api/stakeholder-consensus/<app_id>` - Consensus and variance analysis
- `POST /api/stakeholder-reports/export` - Export reports (PDF/Excel/PPT)

---

## Implementation Plan

### Phase 1: Core Infrastructure (Foundation)
1. Create `stakeholder_assessment_engine.py` with data models
2. Set up database tables for stakeholders, interviews, responses
3. Implement basic CRUD operations for stakeholders
4. Add navigation link to base.html

### Phase 2: Interview Management
1. Create interview session management
2. Implement questionnaire framework with default template
3. Build interview conduct UI with response capture
4. Add real-time scoring calculations

### Phase 3: Analysis & Visualization
1. Implement category-based scoring
2. Create aggregated analysis views
3. Build comparison visualizations (radar charts, heatmaps)
4. Add consensus/variance analysis

### Phase 4: Reporting & Integration
1. Export capabilities (PDF, Excel, PowerPoint)
2. Integration with existing portfolio scores
3. Historical tracking and trend analysis
4. Executive summary generation

### Phase 5: Advanced Features
1. Custom template builder
2. Conditional question logic
3. AI-powered insight generation
4. Email scheduling and reminders

---

## Integration Points

### With Existing Features

1. **Portfolio Dashboard**: Display stakeholder sentiment scores alongside technical scores
2. **TIME Framework**: Incorporate stakeholder readiness into categorization
3. **Smart Recommendations**: Factor in stakeholder insights for recommendations
4. **Risk Assessment**: Add stakeholder-identified risks to risk analysis
5. **Compliance**: Link stakeholder interviews to compliance requirements
6. **Reports**: Include stakeholder analysis in generated reports

### Data Flow

```
Stakeholder Interviews
         |
         v
  Assessment Scores -----> Portfolio Integration
         |                         |
         v                         v
  Qualitative Insights      Combined Analysis
         |                         |
         v                         v
  Action Items            Rationalization Decisions
```

---

## Success Metrics

- **Interview Completion Rate**: % of scheduled interviews completed
- **Coverage Rate**: % of applications with stakeholder assessments
- **Score Accuracy**: Correlation between stakeholder scores and actual outcomes
- **Time Savings**: Reduction in interview preparation and analysis time
- **Insight Quality**: Number of actionable insights generated per assessment

---

## Security & Privacy Considerations

- Stakeholder PII should be protected and access-controlled
- Interview responses may contain sensitive business information
- Export files should be marked as confidential
- Audit trail for all data access and modifications
- Option to anonymize stakeholder identities in reports

---

## Future Enhancements

1. **AI Interview Assistant**: Suggest follow-up questions based on responses
2. **Sentiment Analysis**: Analyze open-text responses for sentiment
3. **Predictive Scoring**: ML model to predict rationalization success based on stakeholder scores
4. **External Surveys**: Send questionnaires directly to stakeholders via email
5. **Mobile Interview App**: Tablet-optimized interface for in-person interviews
6. **Voice Recording**: Transcribe and analyze recorded interview sessions
7. **Benchmarking**: Compare stakeholder scores against industry benchmarks
