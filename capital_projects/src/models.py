"""
Data Models for Capital Projects Lifecycle Planner
Defines the core data structures for road and transportation projects.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List, Dict
from enum import Enum


class ProjectPhase(Enum):
    """Lifecycle phases for capital projects."""
    CONCEPT = "Concept/Idea"
    FEASIBILITY = "Feasibility/Planning"
    DESIGN = "Design"
    ROW_ACQUISITION = "Right-of-Way Acquisition"
    PERMITTING = "Permitting/Utility Coordination"
    PROCUREMENT = "Procurement/Letting"
    CONSTRUCTION = "Active Construction"
    SUBSTANTIAL_COMPLETION = "Substantial Completion"
    CLOSEOUT = "Final Acceptance/Closeout"
    WARRANTY = "Post-Completion/Warranty"


class ProjectType(Enum):
    """Types of capital projects."""
    WIDENING = "Road Widening"
    RESURFACING = "Resurfacing"
    SAFETY = "Safety Improvement"
    INTERSECTION = "Intersection Improvement"
    BRIDGE = "Bridge"
    STORMWATER = "Stormwater"
    SIDEWALK = "Sidewalk/Trail"
    SIGNALS = "Traffic Signals"
    NEW_CONSTRUCTION = "New Road Construction"
    MAINTENANCE = "Major Maintenance"


class ProjectStatus(Enum):
    """Overall project status categories."""
    ADVANCE = "Advance"          # High value, ready - accelerate
    MONITOR = "Monitor"          # High value, watch closely
    RESCOPE = "Re-scope"         # High value but issues - fix it
    DEFER = "Defer"              # Lower priority or not ready
    CANCEL = "Cancel"            # Should be terminated


class FundingSource(Enum):
    """Common funding sources for county projects."""
    LOCAL_OPTION_SALES_TAX = "Local Option Sales Tax"
    GAS_TAX = "Gas Tax"
    IMPACT_FEES = "Impact Fees"
    FEDERAL_GRANT = "Federal Grant"
    STATE_GRANT = "State Grant"
    FDOT = "FDOT"
    MPO = "MPO"
    GENERAL_FUND = "General Fund"
    BONDS = "Bonds"
    OTHER = "Other"


@dataclass
class Milestone:
    """A key milestone within a project."""
    name: str
    planned_date: Optional[date] = None
    actual_date: Optional[date] = None
    is_complete: bool = False
    notes: str = ""


@dataclass
class FundingAllocation:
    """Funding allocation for a project."""
    source: FundingSource
    amount: float
    fiscal_year: int
    is_secured: bool = True
    grant_id: Optional[str] = None


@dataclass
class RiskItem:
    """A risk item associated with a project."""
    category: str  # ROW, Utility, Permitting, Contractor, Environmental, etc.
    description: str
    severity: int  # 1-10
    likelihood: int  # 1-10
    mitigation: str = ""

    @property
    def risk_score(self) -> float:
        """Calculate risk score as severity * likelihood / 10."""
        return (self.severity * self.likelihood) / 10


@dataclass
class CapitalProject:
    """
    Core data model for a capital project.

    This represents a single road/transportation project through its full lifecycle.
    """
    # Core identifiers
    project_id: str
    project_name: str

    # Location/geography
    corridor: str  # e.g., "SR 200", "NW 27th Ave"
    area: str  # e.g., "Ocala", "Silver Springs"
    commissioner_district: int

    # Classification
    project_type: ProjectType
    current_phase: ProjectPhase

    # Ownership
    project_manager: str
    department: str = "County Engineer"
    external_partners: List[str] = field(default_factory=list)  # FDOT, City, MPO

    # Schedule
    planned_start: Optional[date] = None
    planned_end: Optional[date] = None
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None
    percent_complete: float = 0.0

    # Budget
    total_budget: float = 0.0
    spent_to_date: float = 0.0
    forecast_at_completion: float = 0.0
    funding_allocations: List[FundingAllocation] = field(default_factory=list)

    # Scoring dimensions (0-10 scale)
    strategic_alignment: float = 5.0  # Alignment to TIP/LRTP
    safety_benefit: float = 5.0  # Safety improvement score
    congestion_relief: float = 5.0  # Traffic flow improvement
    economic_development: float = 5.0  # Economic impact
    resilience_benefit: float = 5.0  # Stormwater/climate resilience

    # Deliverability dimensions (0-10 scale)
    row_readiness: float = 5.0  # Right-of-way acquisition status
    utility_readiness: float = 5.0  # Utility coordination status
    permit_readiness: float = 5.0  # Permitting status
    design_completeness: float = 5.0  # Design completion %
    funding_certainty: float = 5.0  # Funding secured level

    # Risk
    risks: List[RiskItem] = field(default_factory=list)
    overall_risk_rating: float = 5.0  # 1=low risk, 10=high risk

    # Milestones
    milestones: List[Milestone] = field(default_factory=list)

    # Stakeholder/Public
    communities_affected: List[str] = field(default_factory=list)
    public_meeting_dates: List[date] = field(default_factory=list)
    public_sentiment: str = "Neutral"  # Positive, Neutral, Negative, Mixed
    notable_concerns: str = ""

    # Status
    status: ProjectStatus = ProjectStatus.MONITOR
    status_rationale: str = ""

    # Metadata
    created_date: date = field(default_factory=date.today)
    last_updated: date = field(default_factory=date.today)
    notes: str = ""

    # TIP/LRTP alignment
    tip_id: Optional[str] = None  # Transportation Improvement Program ID
    lrtp_reference: Optional[str] = None  # Long Range Transportation Plan reference

    @property
    def schedule_variance_days(self) -> Optional[int]:
        """Calculate schedule variance in days (negative = behind schedule)."""
        if self.planned_end and self.actual_end:
            return (self.planned_end - self.actual_end).days
        return None

    @property
    def cost_variance(self) -> float:
        """Calculate cost variance (negative = over budget)."""
        if self.total_budget > 0:
            return self.total_budget - self.forecast_at_completion
        return 0.0

    @property
    def cost_variance_percent(self) -> float:
        """Calculate cost variance as percentage."""
        if self.total_budget > 0:
            return ((self.total_budget - self.forecast_at_completion) / self.total_budget) * 100
        return 0.0

    @property
    def is_over_budget(self) -> bool:
        """Check if project is over budget."""
        return self.forecast_at_completion > self.total_budget

    @property
    def is_behind_schedule(self) -> bool:
        """Check if project is behind schedule based on percent complete vs time elapsed."""
        if self.planned_start and self.planned_end:
            today = date.today()
            if today > self.planned_start:
                total_duration = (self.planned_end - self.planned_start).days
                elapsed = (today - self.planned_start).days
                expected_complete = min((elapsed / total_duration) * 100, 100) if total_duration > 0 else 0
                return self.percent_complete < expected_complete - 10  # 10% tolerance
        return False

    def to_dict(self) -> Dict:
        """Convert to dictionary for DataFrame/export."""
        return {
            'Project ID': self.project_id,
            'Project Name': self.project_name,
            'Corridor': self.corridor,
            'Area': self.area,
            'District': self.commissioner_district,
            'Project Type': self.project_type.value if isinstance(self.project_type, ProjectType) else self.project_type,
            'Current Phase': self.current_phase.value if isinstance(self.current_phase, ProjectPhase) else self.current_phase,
            'Project Manager': self.project_manager,
            'Department': self.department,
            'External Partners': ', '.join(self.external_partners) if self.external_partners else '',
            'Planned Start': self.planned_start,
            'Planned End': self.planned_end,
            'Actual Start': self.actual_start,
            'Actual End': self.actual_end,
            'Percent Complete': self.percent_complete,
            'Total Budget': self.total_budget,
            'Spent to Date': self.spent_to_date,
            'Forecast at Completion': self.forecast_at_completion,
            'Strategic Alignment': self.strategic_alignment,
            'Safety Benefit': self.safety_benefit,
            'Congestion Relief': self.congestion_relief,
            'Economic Development': self.economic_development,
            'Resilience Benefit': self.resilience_benefit,
            'ROW Readiness': self.row_readiness,
            'Utility Readiness': self.utility_readiness,
            'Permit Readiness': self.permit_readiness,
            'Design Completeness': self.design_completeness,
            'Funding Certainty': self.funding_certainty,
            'Overall Risk Rating': self.overall_risk_rating,
            'Public Sentiment': self.public_sentiment,
            'Status': self.status.value if isinstance(self.status, ProjectStatus) else self.status,
            'Status Rationale': self.status_rationale,
            'TIP ID': self.tip_id,
            'LRTP Reference': self.lrtp_reference,
            'Notes': self.notes
        }
