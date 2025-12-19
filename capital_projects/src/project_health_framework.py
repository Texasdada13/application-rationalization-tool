"""
Project Health Framework for Capital Projects Lifecycle Planner
Replaces the TIME framework with project-specific categorization.

Categories:
- ADVANCE: High strategic value + high deliverability - accelerate execution
- MONITOR: High strategic value + good deliverability - watch closely
- RESCOPE: High strategic value + low deliverability - fix issues first
- DEFER: Lower strategic value or not ready - push to future
- CANCEL: Low value and/or major issues - terminate
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class ProjectCategory(Enum):
    """Project health categories."""
    ADVANCE = "Advance"      # Green light - accelerate
    MONITOR = "Monitor"      # Yellow - proceed with caution
    RESCOPE = "Re-scope"     # Orange - needs adjustment
    DEFER = "Defer"          # Gray - push back
    CANCEL = "Cancel"        # Red - terminate


@dataclass
class HealthThresholds:
    """
    Configurable thresholds for project categorization.

    All scores are 0-100 scale.
    """
    # Strategic value thresholds
    high_strategic_value: float = 65.0   # Above = high value project
    low_strategic_value: float = 40.0    # Below = low value project

    # Deliverability thresholds
    high_deliverability: float = 65.0    # Above = ready to execute
    low_deliverability: float = 40.0     # Below = not ready

    # Health thresholds
    healthy_project: float = 60.0        # Above = healthy
    at_risk_project: float = 40.0        # Below = at risk

    # Schedule/Budget thresholds
    schedule_concern: float = 40.0       # Below = schedule issues
    budget_concern: float = 40.0         # Below = budget issues

    # Risk threshold
    high_risk: float = 30.0              # Risk score below = high risk (inverted)

    def validate(self) -> bool:
        """Validate thresholds are sensible."""
        return (
            0 <= self.high_strategic_value <= 100 and
            0 <= self.low_strategic_value <= 100 and
            self.low_strategic_value < self.high_strategic_value and
            0 <= self.high_deliverability <= 100 and
            0 <= self.low_deliverability <= 100 and
            self.low_deliverability < self.high_deliverability
        )


class ProjectHealthFramework:
    """
    Framework for categorizing capital projects by health status.

    Uses a 2D quadrant model:
    - X-axis: Deliverability (readiness to execute)
    - Y-axis: Strategic Value (benefit to community)

    Quadrants:
                    HIGH STRATEGIC VALUE
                           │
         RE-SCOPE          │         ADVANCE
    (High value but        │    (High value, ready
     not ready - fix it)   │     to execute)
                           │
    ───────────────────────┼───────────────────────
                           │
         CANCEL/DEFER      │         DEFER/MONITOR
    (Low value,            │    (Lower value but
     not ready)            │     ready - deprioritize)
                           │
                    LOW STRATEGIC VALUE
        LOW DELIVERABILITY          HIGH DELIVERABILITY
    """

    def __init__(self, thresholds: Optional[HealthThresholds] = None):
        """Initialize with optional custom thresholds."""
        self.thresholds = thresholds or HealthThresholds()

        if not self.thresholds.validate():
            raise ValueError("Invalid health framework thresholds")

        self.category_counts = {cat.value: 0 for cat in ProjectCategory}

    def categorize_project(
        self,
        strategic_value: float,
        deliverability: float,
        schedule_health: float,
        budget_health: float,
        risk_score: float,
        project_health: float,
        current_phase: str = "",
        percent_complete: float = 0
    ) -> Tuple[str, str]:
        """
        Categorize a project using the health framework.

        Args:
            strategic_value: Strategic value score 0-100
            deliverability: Deliverability score 0-100
            schedule_health: Schedule health 0-100
            budget_health: Budget health 0-100
            risk_score: Risk score 0-100 (higher = less risky)
            project_health: Overall health score 0-100
            current_phase: Current project phase
            percent_complete: Completion percentage

        Returns:
            Tuple of (category, rationale)
        """
        # Determine quadrant position
        high_value = strategic_value >= self.thresholds.high_strategic_value
        low_value = strategic_value < self.thresholds.low_strategic_value
        high_deliverability = deliverability >= self.thresholds.high_deliverability
        low_deliverability = deliverability < self.thresholds.low_deliverability

        # Check for critical issues
        schedule_issue = schedule_health < self.thresholds.schedule_concern
        budget_issue = budget_health < self.thresholds.budget_concern
        high_risk = risk_score < self.thresholds.high_risk
        critical_issues = schedule_issue or budget_issue or high_risk

        # Projects in construction with >50% complete get special handling
        in_active_construction = (
            'construction' in current_phase.lower() and
            percent_complete > 50
        )

        # Apply categorization logic
        category, rationale = self._apply_categorization_logic(
            strategic_value=strategic_value,
            deliverability=deliverability,
            high_value=high_value,
            low_value=low_value,
            high_deliverability=high_deliverability,
            low_deliverability=low_deliverability,
            schedule_health=schedule_health,
            budget_health=budget_health,
            risk_score=risk_score,
            project_health=project_health,
            critical_issues=critical_issues,
            schedule_issue=schedule_issue,
            budget_issue=budget_issue,
            high_risk=high_risk,
            in_active_construction=in_active_construction
        )

        self.category_counts[category] += 1
        return category, rationale

    def _apply_categorization_logic(
        self,
        strategic_value: float,
        deliverability: float,
        high_value: bool,
        low_value: bool,
        high_deliverability: bool,
        low_deliverability: bool,
        schedule_health: float,
        budget_health: float,
        risk_score: float,
        project_health: float,
        critical_issues: bool,
        schedule_issue: bool,
        budget_issue: bool,
        high_risk: bool,
        in_active_construction: bool
    ) -> Tuple[str, str]:
        """Apply the categorization decision logic."""

        # QUADRANT 1: High Value + High Deliverability = ADVANCE
        if high_value and high_deliverability:
            if critical_issues:
                # High value, ready, but has issues - still advance but monitor
                issues = []
                if schedule_issue:
                    issues.append("schedule")
                if budget_issue:
                    issues.append("budget")
                if high_risk:
                    issues.append("risk")
                return (
                    ProjectCategory.MONITOR.value,
                    f"High strategic value ({strategic_value:.0f}) and deliverability ({deliverability:.0f}), "
                    f"but {', '.join(issues)} concerns require close monitoring. "
                    f"Project health: {project_health:.0f}/100."
                )
            else:
                return (
                    ProjectCategory.ADVANCE.value,
                    f"Strong strategic value ({strategic_value:.0f}) and high deliverability ({deliverability:.0f}). "
                    f"Project is ready for accelerated execution. Health score: {project_health:.0f}/100."
                )

        # QUADRANT 2: High Value + Low Deliverability = RESCOPE
        if high_value and low_deliverability:
            # Identify what's blocking deliverability
            return (
                ProjectCategory.RESCOPE.value,
                f"High strategic value ({strategic_value:.0f}) but deliverability concerns ({deliverability:.0f}). "
                f"Address blocking issues (ROW, utilities, permits, design, or funding) before proceeding. "
                f"Health score: {project_health:.0f}/100."
            )

        # QUADRANT 3: Low Value + High Deliverability = DEFER (or MONITOR if moderate value)
        if not high_value and high_deliverability:
            if low_value:
                return (
                    ProjectCategory.DEFER.value,
                    f"Lower strategic priority ({strategic_value:.0f}) despite being ready to execute ({deliverability:.0f}). "
                    f"Consider deferring to prioritize higher-value projects. Health: {project_health:.0f}/100."
                )
            else:
                # Moderate value - MONITOR
                return (
                    ProjectCategory.MONITOR.value,
                    f"Moderate strategic value ({strategic_value:.0f}) with good deliverability ({deliverability:.0f}). "
                    f"Proceed with normal oversight. Health score: {project_health:.0f}/100."
                )

        # QUADRANT 4: Low Value + Low Deliverability = DEFER or CANCEL
        if low_value and low_deliverability:
            if critical_issues or project_health < 30:
                return (
                    ProjectCategory.CANCEL.value,
                    f"Low strategic value ({strategic_value:.0f}) and poor deliverability ({deliverability:.0f}) "
                    f"with critical issues. Strong candidate for cancellation. Health: {project_health:.0f}/100."
                )
            else:
                return (
                    ProjectCategory.DEFER.value,
                    f"Limited strategic value ({strategic_value:.0f}) and deliverability ({deliverability:.0f}). "
                    f"Defer until conditions improve or priorities change. Health: {project_health:.0f}/100."
                )

        # Projects in active construction with >50% complete - don't cancel
        if in_active_construction:
            if critical_issues:
                return (
                    ProjectCategory.MONITOR.value,
                    f"Project is >50% complete in construction phase. Despite issues "
                    f"(health: {project_health:.0f}), continue with close monitoring rather than stopping."
                )
            else:
                return (
                    ProjectCategory.ADVANCE.value,
                    f"Active construction project progressing well. Continue execution. "
                    f"Health score: {project_health:.0f}/100."
                )

        # Edge cases / moderate scores
        if project_health >= 60:
            return (
                ProjectCategory.MONITOR.value,
                f"Moderate scores (value: {strategic_value:.0f}, deliverability: {deliverability:.0f}) "
                f"with acceptable health ({project_health:.0f}). Proceed with standard oversight."
            )
        elif project_health >= 40:
            return (
                ProjectCategory.RESCOPE.value,
                f"Below-threshold scores suggest rescoping opportunity. "
                f"Value: {strategic_value:.0f}, Deliverability: {deliverability:.0f}, Health: {project_health:.0f}."
            )
        else:
            return (
                ProjectCategory.DEFER.value,
                f"Low overall health ({project_health:.0f}) suggests deferral. "
                f"Reassess during next planning cycle."
            )

    def batch_categorize(self, projects) -> pd.DataFrame:
        """
        Categorize multiple projects.

        Args:
            projects: DataFrame or list of project dicts with scores

        Returns:
            DataFrame with category and rationale added
        """
        if isinstance(projects, pd.DataFrame):
            projects_list = projects.to_dict('records')
        else:
            projects_list = projects

        results = []
        for project in projects_list:
            try:
                category, rationale = self.categorize_project(
                    strategic_value=float(project.get('Strategic Value Score', 50)),
                    deliverability=float(project.get('Deliverability Score', 50)),
                    schedule_health=float(project.get('Schedule Health', 50)),
                    budget_health=float(project.get('Budget Health', 50)),
                    risk_score=float(project.get('Risk Score', 50)),
                    project_health=float(project.get('Project Health Score', 50)),
                    current_phase=str(project.get('Current Phase', '')),
                    percent_complete=float(project.get('Percent Complete', 0))
                )

                result = project.copy()
                result['Status'] = category
                result['Status Rationale'] = rationale
                results.append(result)

            except Exception as e:
                logger.error(f"Error categorizing project {project.get('Project Name', 'Unknown')}: {e}")
                result = project.copy()
                result['Status'] = ProjectCategory.MONITOR.value
                result['Status Rationale'] = "Unable to categorize - data quality issues."
                results.append(result)

        return pd.DataFrame(results)

    def get_category_summary(self) -> Dict:
        """Get summary of categorizations."""
        total = sum(self.category_counts.values())
        if total == 0:
            return {'total': 0, 'distribution': {}, 'percentages': {}}

        return {
            'total': total,
            'distribution': dict(self.category_counts),
            'percentages': {
                cat: round((count / total) * 100, 1)
                for cat, count in self.category_counts.items()
            }
        }

    def get_portfolio_matrix(self, projects: List[Dict]) -> Dict:
        """
        Generate portfolio matrix data for visualization.

        Returns structure suitable for quadrant chart.
        """
        matrix = {
            'quadrants': {
                'advance': [],
                'monitor': [],
                'rescope': [],
                'defer': [],
                'cancel': []
            },
            'counts': {
                'advance': 0,
                'monitor': 0,
                'rescope': 0,
                'defer': 0,
                'cancel': 0
            }
        }

        for project in projects:
            status = project.get('Status', '').lower().replace('-', '')
            if status in matrix['quadrants']:
                matrix['quadrants'][status].append(project.get('Project Name', 'Unknown'))
                matrix['counts'][status] += 1

        return matrix

    def reset_counts(self):
        """Reset category counts for new analysis."""
        self.category_counts = {cat.value: 0 for cat in ProjectCategory}
