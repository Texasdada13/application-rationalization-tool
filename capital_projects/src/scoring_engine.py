"""
Project Scoring Engine for Capital Projects Lifecycle Planner
Calculates composite scores for projects based on strategic value and deliverability.
"""

from typing import Dict, Optional, List
from dataclasses import dataclass
import logging
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class ProjectScoringWeights:
    """
    Configuration for project scoring weights.

    Two main dimensions:
    1. Strategic Value (benefit to the community)
    2. Deliverability (readiness to execute)
    """
    # Strategic Value weights (should sum to 1.0)
    strategic_alignment: float = 0.25  # Alignment to TIP/LRTP
    safety_benefit: float = 0.25       # Safety improvements
    congestion_relief: float = 0.20    # Traffic flow
    economic_development: float = 0.15 # Economic impact
    resilience_benefit: float = 0.15   # Stormwater/resilience

    # Deliverability weights (should sum to 1.0)
    row_readiness: float = 0.25        # Right-of-way status
    utility_readiness: float = 0.20    # Utility coordination
    permit_readiness: float = 0.20     # Permitting
    design_completeness: float = 0.20  # Design status
    funding_certainty: float = 0.15    # Funding secured

    def validate_strategic(self) -> bool:
        """Validate that strategic weights sum to 1.0."""
        total = (
            self.strategic_alignment +
            self.safety_benefit +
            self.congestion_relief +
            self.economic_development +
            self.resilience_benefit
        )
        return abs(total - 1.0) < 0.01

    def validate_deliverability(self) -> bool:
        """Validate that deliverability weights sum to 1.0."""
        total = (
            self.row_readiness +
            self.utility_readiness +
            self.permit_readiness +
            self.design_completeness +
            self.funding_certainty
        )
        return abs(total - 1.0) < 0.01


class ProjectScoringEngine:
    """
    Scoring engine for capital projects.

    Calculates:
    - Strategic Value Score (0-100): Community benefit
    - Deliverability Score (0-100): Execution readiness
    - Project Health Score (0-100): Composite overall score
    - Schedule Health (0-100): On-time performance
    - Budget Health (0-100): Financial performance
    """

    def __init__(self, weights: Optional[ProjectScoringWeights] = None):
        """Initialize with optional custom weights."""
        self.weights = weights or ProjectScoringWeights()

        if not self.weights.validate_strategic():
            logger.warning("Strategic weights do not sum to 1.0")
        if not self.weights.validate_deliverability():
            logger.warning("Deliverability weights do not sum to 1.0")

    def calculate_strategic_value_score(
        self,
        strategic_alignment: float,
        safety_benefit: float,
        congestion_relief: float,
        economic_development: float,
        resilience_benefit: float
    ) -> float:
        """
        Calculate strategic value score (0-100).

        Higher score = more valuable project to the community.

        Args:
            All inputs are 0-10 scale scores

        Returns:
            Strategic value score 0-100
        """
        score = (
            strategic_alignment * self.weights.strategic_alignment +
            safety_benefit * self.weights.safety_benefit +
            congestion_relief * self.weights.congestion_relief +
            economic_development * self.weights.economic_development +
            resilience_benefit * self.weights.resilience_benefit
        )
        return round(score * 10, 2)  # Scale to 0-100

    def calculate_deliverability_score(
        self,
        row_readiness: float,
        utility_readiness: float,
        permit_readiness: float,
        design_completeness: float,
        funding_certainty: float
    ) -> float:
        """
        Calculate deliverability score (0-100).

        Higher score = more ready to execute.

        Args:
            All inputs are 0-10 scale scores

        Returns:
            Deliverability score 0-100
        """
        score = (
            row_readiness * self.weights.row_readiness +
            utility_readiness * self.weights.utility_readiness +
            permit_readiness * self.weights.permit_readiness +
            design_completeness * self.weights.design_completeness +
            funding_certainty * self.weights.funding_certainty
        )
        return round(score * 10, 2)  # Scale to 0-100

    def calculate_schedule_health(
        self,
        percent_complete: float,
        planned_start: Optional[str],
        planned_end: Optional[str],
        actual_start: Optional[str] = None
    ) -> float:
        """
        Calculate schedule health score (0-100).

        100 = on or ahead of schedule
        <100 = behind schedule (lower = more behind)

        Args:
            percent_complete: Current completion percentage
            planned_start: Planned start date
            planned_end: Planned end date
            actual_start: Actual start date (optional)

        Returns:
            Schedule health score 0-100
        """
        from datetime import datetime, date

        try:
            if not planned_start or not planned_end:
                return 50.0  # Unknown, assume neutral

            # Parse dates
            if isinstance(planned_start, str):
                p_start = datetime.strptime(planned_start, '%Y-%m-%d').date()
            elif isinstance(planned_start, date):
                p_start = planned_start
            else:
                return 50.0

            if isinstance(planned_end, str):
                p_end = datetime.strptime(planned_end, '%Y-%m-%d').date()
            elif isinstance(planned_end, date):
                p_end = planned_end
            else:
                return 50.0

            today = date.today()

            # If project hasn't started yet
            if today < p_start:
                return 100.0

            # Calculate expected completion
            total_duration = (p_end - p_start).days
            if total_duration <= 0:
                return 50.0

            elapsed = (today - p_start).days
            expected_percent = min((elapsed / total_duration) * 100, 100)

            # Compare actual to expected
            variance = percent_complete - expected_percent

            # Convert variance to score (±20% variance = full range)
            score = 50 + (variance * 2.5)
            return round(max(0, min(100, score)), 2)

        except Exception as e:
            logger.warning(f"Error calculating schedule health: {e}")
            return 50.0

    def calculate_budget_health(
        self,
        total_budget: float,
        spent_to_date: float,
        forecast_at_completion: float,
        percent_complete: float
    ) -> float:
        """
        Calculate budget health score (0-100).

        100 = on or under budget
        <100 = over budget (lower = more over)

        Args:
            total_budget: Total project budget
            spent_to_date: Amount spent so far
            forecast_at_completion: Projected final cost
            percent_complete: Current completion percentage

        Returns:
            Budget health score 0-100
        """
        if total_budget <= 0:
            return 50.0  # Unknown

        # Calculate cost variance
        cost_variance_pct = ((total_budget - forecast_at_completion) / total_budget) * 100

        # Also check spending rate vs completion
        if percent_complete > 0:
            expected_spend = total_budget * (percent_complete / 100)
            spend_variance_pct = ((expected_spend - spent_to_date) / total_budget) * 100
        else:
            spend_variance_pct = 0

        # Weight forecast more heavily than current spend
        combined_variance = (cost_variance_pct * 0.7) + (spend_variance_pct * 0.3)

        # Convert to score (±20% variance = full range)
        score = 50 + (combined_variance * 2.5)
        return round(max(0, min(100, score)), 2)

    def calculate_risk_score(self, overall_risk_rating: float) -> float:
        """
        Convert risk rating to risk score.

        Risk rating: 1 (low) to 10 (high risk)
        Risk score: 100 (low risk) to 0 (high risk) - inverted for health

        Args:
            overall_risk_rating: Risk level 1-10

        Returns:
            Risk score 0-100 (higher = less risky)
        """
        return round((10 - overall_risk_rating) * 10, 2)

    def calculate_project_health_score(
        self,
        strategic_value: float,
        deliverability: float,
        schedule_health: float,
        budget_health: float,
        risk_score: float
    ) -> float:
        """
        Calculate overall project health score (0-100).

        Weighted composite of all health dimensions.

        Args:
            strategic_value: Strategic value score 0-100
            deliverability: Deliverability score 0-100
            schedule_health: Schedule health 0-100
            budget_health: Budget health 0-100
            risk_score: Risk score 0-100 (inverted)

        Returns:
            Overall health score 0-100
        """
        # Weights for overall health
        health_score = (
            strategic_value * 0.25 +      # Strategic importance
            deliverability * 0.25 +       # Readiness
            schedule_health * 0.20 +      # On-time
            budget_health * 0.15 +        # On-budget
            risk_score * 0.15             # Risk level
        )
        return round(health_score, 2)

    def score_project(self, project: Dict) -> Dict:
        """
        Calculate all scores for a single project.

        Args:
            project: Dictionary with project data

        Returns:
            Project dict with added score fields
        """
        result = project.copy()

        # Strategic Value Score
        strategic_value = self.calculate_strategic_value_score(
            strategic_alignment=float(project.get('Strategic Alignment', 5)),
            safety_benefit=float(project.get('Safety Benefit', 5)),
            congestion_relief=float(project.get('Congestion Relief', 5)),
            economic_development=float(project.get('Economic Development', 5)),
            resilience_benefit=float(project.get('Resilience Benefit', 5))
        )
        result['Strategic Value Score'] = strategic_value

        # Deliverability Score
        deliverability = self.calculate_deliverability_score(
            row_readiness=float(project.get('ROW Readiness', 5)),
            utility_readiness=float(project.get('Utility Readiness', 5)),
            permit_readiness=float(project.get('Permit Readiness', 5)),
            design_completeness=float(project.get('Design Completeness', 5)),
            funding_certainty=float(project.get('Funding Certainty', 5))
        )
        result['Deliverability Score'] = deliverability

        # Schedule Health
        schedule_health = self.calculate_schedule_health(
            percent_complete=float(project.get('Percent Complete', 0)),
            planned_start=project.get('Planned Start'),
            planned_end=project.get('Planned End'),
            actual_start=project.get('Actual Start')
        )
        result['Schedule Health'] = schedule_health

        # Budget Health
        budget_health = self.calculate_budget_health(
            total_budget=float(project.get('Total Budget', 0)),
            spent_to_date=float(project.get('Spent to Date', 0)),
            forecast_at_completion=float(project.get('Forecast at Completion', 0) or project.get('Total Budget', 0)),
            percent_complete=float(project.get('Percent Complete', 0))
        )
        result['Budget Health'] = budget_health

        # Risk Score (inverted from rating)
        risk_score = self.calculate_risk_score(
            float(project.get('Overall Risk Rating', 5))
        )
        result['Risk Score'] = risk_score

        # Overall Project Health
        project_health = self.calculate_project_health_score(
            strategic_value=strategic_value,
            deliverability=deliverability,
            schedule_health=schedule_health,
            budget_health=budget_health,
            risk_score=risk_score
        )
        result['Project Health Score'] = project_health

        return result

    def batch_score_projects(self, projects) -> pd.DataFrame:
        """
        Score multiple projects.

        Args:
            projects: List of dicts or DataFrame

        Returns:
            DataFrame with all scores added
        """
        if isinstance(projects, pd.DataFrame):
            projects_list = projects.to_dict('records')
        else:
            projects_list = projects

        scored = [self.score_project(p) for p in projects_list]
        return pd.DataFrame(scored)

    def get_score_breakdown(self, project: Dict) -> Dict:
        """
        Get detailed breakdown of score contributions.

        Args:
            project: Project dictionary

        Returns:
            Dictionary with score breakdown
        """
        return {
            'strategic_components': {
                'strategic_alignment': float(project.get('Strategic Alignment', 5)) * self.weights.strategic_alignment * 10,
                'safety_benefit': float(project.get('Safety Benefit', 5)) * self.weights.safety_benefit * 10,
                'congestion_relief': float(project.get('Congestion Relief', 5)) * self.weights.congestion_relief * 10,
                'economic_development': float(project.get('Economic Development', 5)) * self.weights.economic_development * 10,
                'resilience_benefit': float(project.get('Resilience Benefit', 5)) * self.weights.resilience_benefit * 10,
            },
            'deliverability_components': {
                'row_readiness': float(project.get('ROW Readiness', 5)) * self.weights.row_readiness * 10,
                'utility_readiness': float(project.get('Utility Readiness', 5)) * self.weights.utility_readiness * 10,
                'permit_readiness': float(project.get('Permit Readiness', 5)) * self.weights.permit_readiness * 10,
                'design_completeness': float(project.get('Design Completeness', 5)) * self.weights.design_completeness * 10,
                'funding_certainty': float(project.get('Funding Certainty', 5)) * self.weights.funding_certainty * 10,
            }
        }
