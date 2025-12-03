"""
Stakeholder Assessment Engine Module
Facilitates structured client interviews during application rationalization projects.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import json
import uuid

logger = logging.getLogger(__name__)


# ============================================================================
# Enums
# ============================================================================

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


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class Stakeholder:
    """Stakeholder profile"""
    id: str
    name: str
    email: str
    role: str
    department: str
    stakeholder_type: str  # Use string for JSON serialization
    influence_level: str
    phone: str = ""
    applications: List[str] = field(default_factory=list)
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'department': self.department,
            'stakeholder_type': self.stakeholder_type,
            'influence_level': self.influence_level,
            'phone': self.phone,
            'applications': self.applications,
            'notes': self.notes,
            'created_at': self.created_at
        }


@dataclass
class Question:
    """Assessment question"""
    id: str
    category: str
    text: str
    question_type: str
    required: bool = True
    options: List[str] = field(default_factory=list)
    weight: float = 1.0
    help_text: str = ""
    score_mapping: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'category': self.category,
            'text': self.text,
            'question_type': self.question_type,
            'required': self.required,
            'options': self.options,
            'weight': self.weight,
            'help_text': self.help_text,
            'score_mapping': self.score_mapping
        }


@dataclass
class Response:
    """Interview response"""
    question_id: str
    value: Any
    score: float = 0.0
    notes: str = ""
    verbatim_quote: str = ""
    flagged: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            'question_id': self.question_id,
            'value': self.value,
            'score': self.score,
            'notes': self.notes,
            'verbatim_quote': self.verbatim_quote,
            'flagged': self.flagged,
            'timestamp': self.timestamp
        }


@dataclass
class InterviewSession:
    """Interview session"""
    id: str
    stakeholder_id: str
    interviewer: str
    application_ids: List[str]
    status: str
    scheduled_date: str
    template_id: str = "default"
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    responses: List[Response] = field(default_factory=list)
    overall_score: float = 0.0
    category_scores: Dict[str, float] = field(default_factory=dict)
    summary: str = ""
    action_items: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'stakeholder_id': self.stakeholder_id,
            'interviewer': self.interviewer,
            'application_ids': self.application_ids,
            'status': self.status,
            'scheduled_date': self.scheduled_date,
            'template_id': self.template_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'responses': [r.to_dict() for r in self.responses],
            'overall_score': self.overall_score,
            'category_scores': self.category_scores,
            'summary': self.summary,
            'action_items': self.action_items,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


@dataclass
class AssessmentTemplate:
    """Assessment questionnaire template"""
    id: str
    name: str
    description: str
    questions: List[Question] = field(default_factory=list)
    version: str = "1.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'questions': [q.to_dict() for q in self.questions],
            'version': self.version,
            'created_at': self.created_at
        }


# ============================================================================
# Stakeholder Assessment Engine
# ============================================================================

class StakeholderAssessmentEngine:
    """
    Engine for conducting and analyzing stakeholder assessments.

    Features:
    - Stakeholder profile management
    - Interview session management
    - Customizable questionnaire templates
    - Automated scoring and analysis
    - Consensus and variance analysis
    - Integration with portfolio data
    """

    def __init__(self):
        """Initialize the assessment engine with default templates"""
        self.templates: Dict[str, AssessmentTemplate] = {}
        self.stakeholders: Dict[str, Stakeholder] = {}
        self.interviews: Dict[str, InterviewSession] = {}
        self._initialize_default_template()

    def _initialize_default_template(self):
        """Initialize the default assessment questionnaire template"""

        questions = []

        # ================================================================
        # Category 1: Business Value & Criticality
        # ================================================================
        questions.extend([
            Question(
                id="BV-001",
                category="Business Value & Criticality",
                text="How critical is this application to your daily operations?",
                question_type="Rating Scale (1-5)",
                weight=1.5,
                help_text="1 = Not critical at all, 5 = Mission critical"
            ),
            Question(
                id="BV-002",
                category="Business Value & Criticality",
                text="What percentage of your team uses this application regularly?",
                question_type="Single Choice",
                options=["0-25%", "26-50%", "51-75%", "76-100%"],
                weight=1.0,
                score_mapping={"0-25%": 0.25, "26-50%": 0.5, "51-75%": 0.75, "76-100%": 1.0}
            ),
            Question(
                id="BV-003",
                category="Business Value & Criticality",
                text="What would be the business impact if this application was unavailable for 24 hours?",
                question_type="Single Choice",
                options=["Minimal - work continues normally", "Low - minor inconvenience",
                        "Medium - significant delays", "High - major business disruption",
                        "Critical - operations halt completely"],
                weight=1.5,
                score_mapping={
                    "Minimal - work continues normally": 0.2,
                    "Low - minor inconvenience": 0.4,
                    "Medium - significant delays": 0.6,
                    "High - major business disruption": 0.8,
                    "Critical - operations halt completely": 1.0
                }
            ),
            Question(
                id="BV-004",
                category="Business Value & Criticality",
                text="Does this application generate revenue or support revenue-generating activities?",
                question_type="Yes/No",
                weight=1.0,
                score_mapping={"Yes": 1.0, "No": 0.0}
            ),
            Question(
                id="BV-005",
                category="Business Value & Criticality",
                text="How would you rate the strategic importance of this application for future business goals?",
                question_type="Rating Scale (1-5)",
                weight=1.2,
                help_text="1 = No strategic value, 5 = Core to future strategy"
            ),
        ])

        # ================================================================
        # Category 2: User Satisfaction & Experience
        # ================================================================
        questions.extend([
            Question(
                id="US-001",
                category="User Satisfaction & Experience",
                text="How satisfied are you with this application overall?",
                question_type="Rating Scale (1-5)",
                weight=1.0,
                help_text="1 = Very dissatisfied, 5 = Very satisfied"
            ),
            Question(
                id="US-002",
                category="User Satisfaction & Experience",
                text="How would you rate the ease of use of this application?",
                question_type="Rating Scale (1-5)",
                weight=1.0,
                help_text="1 = Very difficult, 5 = Very easy"
            ),
            Question(
                id="US-003",
                category="User Satisfaction & Experience",
                text="How reliable is this application (uptime, performance)?",
                question_type="Rating Scale (1-5)",
                weight=1.2,
                help_text="1 = Very unreliable, 5 = Very reliable"
            ),
            Question(
                id="US-004",
                category="User Satisfaction & Experience",
                text="How well does this application meet your current business needs?",
                question_type="Rating Scale (1-5)",
                weight=1.3,
                help_text="1 = Doesn't meet needs, 5 = Fully meets needs"
            ),
            Question(
                id="US-005",
                category="User Satisfaction & Experience",
                text="How would you rate the quality of support for this application?",
                question_type="Rating Scale (1-5)",
                weight=0.8,
                help_text="1 = Very poor support, 5 = Excellent support"
            ),
            Question(
                id="US-006",
                category="User Satisfaction & Experience",
                text="What are the top 3 pain points with this application?",
                question_type="Open Text",
                weight=1.0,
                help_text="Describe the main challenges or frustrations"
            ),
        ])

        # ================================================================
        # Category 3: Technical Health & Sustainability
        # ================================================================
        questions.extend([
            Question(
                id="TH-001",
                category="Technical Health & Sustainability",
                text="How well does this application integrate with other systems you use?",
                question_type="Rating Scale (1-5)",
                weight=1.2,
                help_text="1 = No integration, 5 = Seamless integration"
            ),
            Question(
                id="TH-002",
                category="Technical Health & Sustainability",
                text="Have you experienced data quality issues with this application?",
                question_type="Yes/No",
                weight=1.0,
                score_mapping={"Yes": 0.0, "No": 1.0}  # Inverted - No issues is good
            ),
            Question(
                id="TH-003",
                category="Technical Health & Sustainability",
                text="How would you rate the reporting/analytics capabilities?",
                question_type="Rating Scale (1-5)",
                weight=0.9,
                help_text="1 = No capabilities, 5 = Excellent capabilities"
            ),
            Question(
                id="TH-004",
                category="Technical Health & Sustainability",
                text="Is this application accessible on mobile devices when needed?",
                question_type="Single Choice",
                options=["Not needed", "Needed but not available", "Available but poor", "Available and adequate", "Excellent mobile support"],
                weight=0.7,
                score_mapping={
                    "Not needed": 0.5,
                    "Needed but not available": 0.0,
                    "Available but poor": 0.25,
                    "Available and adequate": 0.75,
                    "Excellent mobile support": 1.0
                }
            ),
            Question(
                id="TH-005",
                category="Technical Health & Sustainability",
                text="How frequently do you encounter bugs or system errors?",
                question_type="Single Choice",
                options=["Never", "Rarely (monthly)", "Sometimes (weekly)", "Often (daily)", "Constantly"],
                weight=1.1,
                score_mapping={
                    "Never": 1.0,
                    "Rarely (monthly)": 0.8,
                    "Sometimes (weekly)": 0.5,
                    "Often (daily)": 0.2,
                    "Constantly": 0.0
                }
            ),
        ])

        # ================================================================
        # Category 4: Change Readiness & Migration Potential
        # ================================================================
        questions.extend([
            Question(
                id="CR-001",
                category="Change Readiness & Migration Potential",
                text="How open would your team be to replacing this application?",
                question_type="Rating Scale (1-5)",
                weight=1.5,
                help_text="1 = Strongly opposed, 5 = Very open to change"
            ),
            Question(
                id="CR-002",
                category="Change Readiness & Migration Potential",
                text="What is the estimated effort to train users on a replacement system?",
                question_type="Single Choice",
                options=["Minimal (< 1 day)", "Low (1-3 days)", "Medium (1-2 weeks)", "High (1 month+)", "Very High (3+ months)"],
                weight=1.2,
                score_mapping={
                    "Minimal (< 1 day)": 1.0,
                    "Low (1-3 days)": 0.8,
                    "Medium (1-2 weeks)": 0.6,
                    "High (1 month+)": 0.3,
                    "Very High (3+ months)": 0.1
                }
            ),
            Question(
                id="CR-003",
                category="Change Readiness & Migration Potential",
                text="Are there critical customizations that would be difficult to replicate?",
                question_type="Yes/No",
                weight=1.3,
                score_mapping={"Yes": 0.0, "No": 1.0}
            ),
            Question(
                id="CR-004",
                category="Change Readiness & Migration Potential",
                text="How dependent are your workflows on this specific application?",
                question_type="Rating Scale (1-5)",
                weight=1.4,
                help_text="1 = Not dependent, 5 = Completely dependent (inverted for change readiness)"
            ),
            Question(
                id="CR-005",
                category="Change Readiness & Migration Potential",
                text="Have you identified potential replacement solutions?",
                question_type="Yes/No",
                weight=0.8,
                score_mapping={"Yes": 1.0, "No": 0.0}
            ),
            Question(
                id="CR-006",
                category="Change Readiness & Migration Potential",
                text="What would be required for a successful migration?",
                question_type="Open Text",
                weight=1.0,
                help_text="Key requirements, concerns, or success factors"
            ),
        ])

        # ================================================================
        # Category 5: Dependencies & Integration
        # ================================================================
        questions.extend([
            Question(
                id="DI-001",
                category="Dependencies & Integration",
                text="List all applications this system sends data to",
                question_type="Open Text",
                weight=1.5,
                help_text="Name all downstream systems"
            ),
            Question(
                id="DI-002",
                category="Dependencies & Integration",
                text="List all applications this system receives data from",
                question_type="Open Text",
                weight=1.5,
                help_text="Name all upstream systems"
            ),
            Question(
                id="DI-003",
                category="Dependencies & Integration",
                text="Are there manual processes that bridge this application to others?",
                question_type="Yes/No",
                weight=1.2,
                score_mapping={"Yes": 0.3, "No": 1.0}  # Manual processes indicate poor integration
            ),
            Question(
                id="DI-004",
                category="Dependencies & Integration",
                text="How many external partners/vendors interact with this application?",
                question_type="Single Choice",
                options=["None", "1-2", "3-5", "6-10", "More than 10"],
                weight=1.0,
                score_mapping={
                    "None": 0.2,
                    "1-2": 0.4,
                    "3-5": 0.6,
                    "6-10": 0.8,
                    "More than 10": 1.0
                }
            ),
            Question(
                id="DI-005",
                category="Dependencies & Integration",
                text="Are there regulatory requirements tied to this application's data?",
                question_type="Yes/No",
                weight=1.3,
                score_mapping={"Yes": 1.0, "No": 0.0}
            ),
        ])

        # ================================================================
        # Category 6: Cost & Resource Awareness
        # ================================================================
        questions.extend([
            Question(
                id="CA-001",
                category="Cost & Resource Awareness",
                text="Do you feel this application provides good value for its cost?",
                question_type="Rating Scale (1-5)",
                weight=1.0,
                help_text="1 = Very poor value, 5 = Excellent value"
            ),
            Question(
                id="CA-002",
                category="Cost & Resource Awareness",
                text="How much IT support time does this application require?",
                question_type="Single Choice",
                options=["Almost none", "Minimal", "Moderate", "Significant", "Excessive"],
                weight=1.1,
                score_mapping={
                    "Almost none": 1.0,
                    "Minimal": 0.8,
                    "Moderate": 0.5,
                    "Significant": 0.2,
                    "Excessive": 0.0
                }
            ),
            Question(
                id="CA-003",
                category="Cost & Resource Awareness",
                text="Are there duplicate capabilities in other applications you use?",
                question_type="Yes/No",
                weight=1.2,
                score_mapping={"Yes": 0.0, "No": 1.0}
            ),
            Question(
                id="CA-004",
                category="Cost & Resource Awareness",
                text="Would consolidating this application's functions save your team time?",
                question_type="Yes/No",
                weight=1.0,
                score_mapping={"Yes": 1.0, "No": 0.0}
            ),
        ])

        # ================================================================
        # Category 7: Future Needs & Strategic Alignment
        # ================================================================
        questions.extend([
            Question(
                id="FN-001",
                category="Future Needs & Strategic Alignment",
                text="What new capabilities do you need that this application doesn't provide?",
                question_type="Open Text",
                weight=1.2,
                help_text="Describe gaps in current functionality"
            ),
            Question(
                id="FN-002",
                category="Future Needs & Strategic Alignment",
                text="How well does this application align with company digital transformation goals?",
                question_type="Rating Scale (1-5)",
                weight=1.3,
                help_text="1 = Not aligned, 5 = Fully aligned"
            ),
            Question(
                id="FN-003",
                category="Future Needs & Strategic Alignment",
                text="What is your preferred timeline for addressing this application's future?",
                question_type="Single Choice",
                options=["Immediate (< 3 months)", "Short-term (3-6 months)", "Medium-term (6-12 months)", "Long-term (1-2 years)", "No changes needed"],
                weight=0.9,
                score_mapping={
                    "Immediate (< 3 months)": 1.0,
                    "Short-term (3-6 months)": 0.8,
                    "Medium-term (6-12 months)": 0.6,
                    "Long-term (1-2 years)": 0.4,
                    "No changes needed": 0.2
                }
            ),
            Question(
                id="FN-004",
                category="Future Needs & Strategic Alignment",
                text="Would you recommend this application to a colleague? (NPS-style)",
                question_type="Rating Scale (1-10)",
                weight=1.1,
                help_text="1 = Definitely not, 10 = Definitely yes"
            ),
        ])

        # Create the default template
        default_template = AssessmentTemplate(
            id="default",
            name="Standard Stakeholder Assessment",
            description="Comprehensive assessment covering business value, user satisfaction, technical health, change readiness, dependencies, costs, and strategic alignment.",
            questions=questions,
            version="1.0"
        )

        self.templates["default"] = default_template
        logger.info(f"Initialized default template with {len(questions)} questions")

    # ========================================================================
    # Stakeholder Management
    # ========================================================================

    def create_stakeholder(
        self,
        name: str,
        email: str,
        role: str,
        department: str,
        stakeholder_type: str,
        influence_level: str,
        phone: str = "",
        applications: List[str] = None,
        notes: str = ""
    ) -> Stakeholder:
        """Create a new stakeholder profile"""
        stakeholder = Stakeholder(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            role=role,
            department=department,
            stakeholder_type=stakeholder_type,
            influence_level=influence_level,
            phone=phone,
            applications=applications or [],
            notes=notes
        )
        self.stakeholders[stakeholder.id] = stakeholder
        logger.info(f"Created stakeholder: {name} ({stakeholder.id})")
        return stakeholder

    def get_stakeholder(self, stakeholder_id: str) -> Optional[Stakeholder]:
        """Get stakeholder by ID"""
        return self.stakeholders.get(stakeholder_id)

    def list_stakeholders(self) -> List[Dict[str, Any]]:
        """List all stakeholders"""
        return [s.to_dict() for s in self.stakeholders.values()]

    def update_stakeholder(self, stakeholder_id: str, updates: Dict[str, Any]) -> Optional[Stakeholder]:
        """Update stakeholder profile"""
        if stakeholder_id not in self.stakeholders:
            return None

        stakeholder = self.stakeholders[stakeholder_id]
        for key, value in updates.items():
            if hasattr(stakeholder, key):
                setattr(stakeholder, key, value)

        return stakeholder

    def delete_stakeholder(self, stakeholder_id: str) -> bool:
        """Delete stakeholder"""
        if stakeholder_id in self.stakeholders:
            del self.stakeholders[stakeholder_id]
            return True
        return False

    # ========================================================================
    # Interview Session Management
    # ========================================================================

    def create_interview(
        self,
        stakeholder_id: str,
        interviewer: str,
        application_ids: List[str],
        scheduled_date: str,
        template_id: str = "default"
    ) -> InterviewSession:
        """Create a new interview session"""
        interview = InterviewSession(
            id=str(uuid.uuid4()),
            stakeholder_id=stakeholder_id,
            interviewer=interviewer,
            application_ids=application_ids,
            status="Scheduled",
            scheduled_date=scheduled_date,
            template_id=template_id
        )
        self.interviews[interview.id] = interview
        logger.info(f"Created interview: {interview.id}")
        return interview

    def get_interview(self, interview_id: str) -> Optional[InterviewSession]:
        """Get interview by ID"""
        return self.interviews.get(interview_id)

    def list_interviews(self, status: str = None) -> List[Dict[str, Any]]:
        """List all interviews, optionally filtered by status"""
        interviews = self.interviews.values()
        if status:
            interviews = [i for i in interviews if i.status == status]
        return [i.to_dict() for i in interviews]

    def start_interview(self, interview_id: str) -> Optional[InterviewSession]:
        """Start an interview session"""
        interview = self.interviews.get(interview_id)
        if interview:
            interview.status = "In Progress"
            interview.start_time = datetime.now().isoformat()
            interview.updated_at = datetime.now().isoformat()
        return interview

    def complete_interview(self, interview_id: str) -> Optional[InterviewSession]:
        """Complete an interview session"""
        interview = self.interviews.get(interview_id)
        if interview:
            interview.status = "Completed"
            interview.end_time = datetime.now().isoformat()
            interview.updated_at = datetime.now().isoformat()
            # Calculate final scores
            self._calculate_interview_scores(interview)
        return interview

    def save_response(
        self,
        interview_id: str,
        question_id: str,
        value: Any,
        notes: str = "",
        verbatim_quote: str = "",
        flagged: bool = False
    ) -> Optional[Response]:
        """Save a response for an interview question"""
        interview = self.interviews.get(interview_id)
        if not interview:
            return None

        template = self.templates.get(interview.template_id)
        if not template:
            return None

        # Find the question
        question = next((q for q in template.questions if q.id == question_id), None)
        if not question:
            return None

        # Calculate score
        score = self._calculate_response_score(question, value)

        # Create response
        response = Response(
            question_id=question_id,
            value=value,
            score=score,
            notes=notes,
            verbatim_quote=verbatim_quote,
            flagged=flagged
        )

        # Update or add response
        existing_idx = next(
            (i for i, r in enumerate(interview.responses) if r.question_id == question_id),
            None
        )
        if existing_idx is not None:
            interview.responses[existing_idx] = response
        else:
            interview.responses.append(response)

        interview.updated_at = datetime.now().isoformat()
        return response

    def _calculate_response_score(self, question: Question, value: Any) -> float:
        """Calculate score for a single response"""
        if question.question_type == "Open Text":
            return 0.0  # Open text doesn't contribute to numerical score

        if question.question_type in ["Rating Scale (1-5)"]:
            try:
                return float(value) / 5.0
            except (ValueError, TypeError):
                return 0.0

        if question.question_type == "Rating Scale (1-10)":
            try:
                return float(value) / 10.0
            except (ValueError, TypeError):
                return 0.0

        if question.question_type == "Yes/No":
            if question.score_mapping:
                return question.score_mapping.get(value, 0.0)
            return 1.0 if value == "Yes" else 0.0

        if question.question_type in ["Single Choice", "Multiple Choice"]:
            if question.score_mapping:
                return question.score_mapping.get(value, 0.0)
            return 0.5  # Default for unmapped choices

        return 0.0

    def _calculate_interview_scores(self, interview: InterviewSession):
        """Calculate overall and category scores for an interview"""
        template = self.templates.get(interview.template_id)
        if not template:
            return

        # Group responses by category
        category_scores: Dict[str, List[float]] = {}
        category_weights: Dict[str, float] = {}
        total_weighted_score = 0.0
        total_weight = 0.0

        for response in interview.responses:
            question = next((q for q in template.questions if q.id == response.question_id), None)
            if not question or question.question_type == "Open Text":
                continue

            category = question.category
            if category not in category_scores:
                category_scores[category] = []
                category_weights[category] = 0.0

            weighted_score = response.score * question.weight
            category_scores[category].append(weighted_score)
            category_weights[category] += question.weight

            total_weighted_score += weighted_score
            total_weight += question.weight

        # Calculate category averages
        interview.category_scores = {}
        for category, scores in category_scores.items():
            if category_weights[category] > 0:
                interview.category_scores[category] = round(
                    (sum(scores) / category_weights[category]) * 100, 2
                )

        # Calculate overall score
        if total_weight > 0:
            interview.overall_score = round((total_weighted_score / total_weight) * 100, 2)

    # ========================================================================
    # Analysis & Reporting
    # ========================================================================

    def get_interview_analysis(self, interview_id: str) -> Dict[str, Any]:
        """Get detailed analysis for a completed interview"""
        interview = self.interviews.get(interview_id)
        if not interview:
            return {'error': 'Interview not found'}

        template = self.templates.get(interview.template_id)
        if not template:
            return {'error': 'Template not found'}

        stakeholder = self.stakeholders.get(interview.stakeholder_id)

        # Build response analysis
        response_details = []
        flagged_items = []
        open_text_responses = []

        for response in interview.responses:
            question = next((q for q in template.questions if q.id == response.question_id), None)
            if question:
                detail = {
                    'question_id': question.id,
                    'category': question.category,
                    'question_text': question.text,
                    'question_type': question.question_type,
                    'value': response.value,
                    'score': response.score,
                    'weight': question.weight,
                    'notes': response.notes,
                    'verbatim_quote': response.verbatim_quote,
                    'flagged': response.flagged
                }
                response_details.append(detail)

                if response.flagged:
                    flagged_items.append(detail)

                if question.question_type == "Open Text" and response.value:
                    open_text_responses.append({
                        'question': question.text,
                        'response': response.value,
                        'category': question.category
                    })

        return {
            'interview_id': interview.id,
            'stakeholder': stakeholder.to_dict() if stakeholder else None,
            'interviewer': interview.interviewer,
            'applications': interview.application_ids,
            'status': interview.status,
            'scheduled_date': interview.scheduled_date,
            'start_time': interview.start_time,
            'end_time': interview.end_time,
            'overall_score': interview.overall_score,
            'category_scores': interview.category_scores,
            'total_questions': len(template.questions),
            'answered_questions': len(interview.responses),
            'completion_percentage': round(len(interview.responses) / len(template.questions) * 100, 1),
            'response_details': response_details,
            'flagged_items': flagged_items,
            'open_text_responses': open_text_responses,
            'action_items': interview.action_items,
            'summary': interview.summary
        }

    def get_application_stakeholder_analysis(self, application_id: str) -> Dict[str, Any]:
        """Get aggregated stakeholder analysis for an application"""
        # Find all completed interviews for this application
        app_interviews = [
            i for i in self.interviews.values()
            if application_id in i.application_ids and i.status in ["Completed", "Reviewed"]
        ]

        if not app_interviews:
            return {
                'application_id': application_id,
                'error': 'No completed interviews found for this application'
            }

        # Aggregate scores
        overall_scores = []
        category_scores: Dict[str, List[float]] = {}
        stakeholder_assessments = []

        for interview in app_interviews:
            stakeholder = self.stakeholders.get(interview.stakeholder_id)
            overall_scores.append(interview.overall_score)

            for category, score in interview.category_scores.items():
                if category not in category_scores:
                    category_scores[category] = []
                category_scores[category].append(score)

            stakeholder_assessments.append({
                'stakeholder_name': stakeholder.name if stakeholder else 'Unknown',
                'stakeholder_type': stakeholder.stakeholder_type if stakeholder else 'Unknown',
                'influence_level': stakeholder.influence_level if stakeholder else 'Unknown',
                'overall_score': interview.overall_score,
                'category_scores': interview.category_scores,
                'interview_date': interview.end_time or interview.scheduled_date
            })

        # Calculate aggregates
        avg_overall = np.mean(overall_scores) if overall_scores else 0
        std_overall = np.std(overall_scores) if len(overall_scores) > 1 else 0

        avg_category_scores = {}
        category_variance = {}
        for category, scores in category_scores.items():
            avg_category_scores[category] = round(np.mean(scores), 2)
            category_variance[category] = round(np.std(scores), 2) if len(scores) > 1 else 0

        # Identify areas of consensus and conflict
        high_consensus = [cat for cat, var in category_variance.items() if var < 10]
        high_conflict = [cat for cat, var in category_variance.items() if var > 20]

        return {
            'application_id': application_id,
            'stakeholder_count': len(app_interviews),
            'overall_score': round(avg_overall, 2),
            'score_variance': round(std_overall, 2),
            'category_scores': avg_category_scores,
            'category_variance': category_variance,
            'high_consensus_areas': high_consensus,
            'high_conflict_areas': high_conflict,
            'stakeholder_assessments': stakeholder_assessments,
            'assessment_dates': [i.end_time or i.scheduled_date for i in app_interviews]
        }

    def get_portfolio_stakeholder_summary(self) -> Dict[str, Any]:
        """Get portfolio-wide stakeholder assessment summary"""
        # Aggregate all interviews
        completed_interviews = [
            i for i in self.interviews.values()
            if i.status in ["Completed", "Reviewed"]
        ]

        if not completed_interviews:
            return {
                'total_interviews': 0,
                'error': 'No completed interviews found'
            }

        # Get unique applications
        all_apps = set()
        for interview in completed_interviews:
            all_apps.update(interview.application_ids)

        # Calculate portfolio-wide metrics
        all_scores = [i.overall_score for i in completed_interviews]

        # Category aggregates
        category_totals: Dict[str, List[float]] = {}
        for interview in completed_interviews:
            for category, score in interview.category_scores.items():
                if category not in category_totals:
                    category_totals[category] = []
                category_totals[category].append(score)

        portfolio_category_scores = {
            cat: round(np.mean(scores), 2)
            for cat, scores in category_totals.items()
        }

        # Applications by score range
        app_analyses = {}
        for app_id in all_apps:
            analysis = self.get_application_stakeholder_analysis(app_id)
            if 'error' not in analysis:
                app_analyses[app_id] = analysis

        high_scoring = [a for a, d in app_analyses.items() if d['overall_score'] >= 70]
        medium_scoring = [a for a, d in app_analyses.items() if 40 <= d['overall_score'] < 70]
        low_scoring = [a for a, d in app_analyses.items() if d['overall_score'] < 40]

        return {
            'total_interviews': len(completed_interviews),
            'total_stakeholders': len(self.stakeholders),
            'total_applications_assessed': len(all_apps),
            'portfolio_average_score': round(np.mean(all_scores), 2),
            'score_distribution': {
                'min': round(min(all_scores), 2),
                'max': round(max(all_scores), 2),
                'std': round(np.std(all_scores), 2)
            },
            'portfolio_category_scores': portfolio_category_scores,
            'applications_by_score': {
                'high': high_scoring,
                'medium': medium_scoring,
                'low': low_scoring
            },
            'interview_status_summary': {
                'scheduled': len([i for i in self.interviews.values() if i.status == 'Scheduled']),
                'in_progress': len([i for i in self.interviews.values() if i.status == 'In Progress']),
                'completed': len([i for i in self.interviews.values() if i.status == 'Completed']),
                'reviewed': len([i for i in self.interviews.values() if i.status == 'Reviewed'])
            }
        }

    # ========================================================================
    # Template Management
    # ========================================================================

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get assessment template"""
        template = self.templates.get(template_id)
        return template.to_dict() if template else None

    def list_templates(self) -> List[Dict[str, Any]]:
        """List all available templates"""
        return [
            {
                'id': t.id,
                'name': t.name,
                'description': t.description,
                'question_count': len(t.questions),
                'version': t.version
            }
            for t in self.templates.values()
        ]

    def get_template_categories(self, template_id: str) -> List[str]:
        """Get unique categories in a template"""
        template = self.templates.get(template_id)
        if not template:
            return []

        categories = []
        seen = set()
        for q in template.questions:
            if q.category not in seen:
                categories.append(q.category)
                seen.add(q.category)
        return categories

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def get_stakeholder_types(self) -> List[str]:
        """Get list of stakeholder types"""
        return [e.value for e in StakeholderType]

    def get_influence_levels(self) -> List[str]:
        """Get list of influence levels"""
        return [e.value for e in InfluenceLevel]

    def get_interview_statuses(self) -> List[str]:
        """Get list of interview statuses"""
        return [e.value for e in InterviewStatus]

    def export_interview_data(self, interview_id: str) -> Dict[str, Any]:
        """Export interview data for reporting"""
        return self.get_interview_analysis(interview_id)

    def import_stakeholders_from_csv(self, df: pd.DataFrame) -> List[Stakeholder]:
        """Import stakeholders from a DataFrame"""
        imported = []
        for _, row in df.iterrows():
            stakeholder = self.create_stakeholder(
                name=row.get('name', row.get('Name', '')),
                email=row.get('email', row.get('Email', '')),
                role=row.get('role', row.get('Role', '')),
                department=row.get('department', row.get('Department', '')),
                stakeholder_type=row.get('stakeholder_type', row.get('Type', 'End User')),
                influence_level=row.get('influence_level', row.get('Influence', 'Contributor')),
                phone=row.get('phone', row.get('Phone', '')),
                notes=row.get('notes', row.get('Notes', ''))
            )
            imported.append(stakeholder)
        return imported
