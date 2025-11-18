"""
TIME Framework Module
Implements the TIME (Tolerate, Invest, Migrate, Eliminate) framework for application rationalization.

The TIME framework is an industry-standard approach for categorizing applications based on
their business value and technical quality. This module provides configurable thresholds
and mapping logic to assign TIME categories to applications.

TIME Categories:
    - INVEST: High value, good technical quality - invest for growth
    - TOLERATE: High value, poor technical quality - maintain but plan improvements
    - MIGRATE: Low value, poor technical quality - migrate or eliminate
    - ELIMINATE: Low value, any quality - retire or decommission

The framework uses a quadrant approach based on:
    - X-axis: Technical Quality (composite of tech health, security, strategic fit)
    - Y-axis: Business Value (composite of business value, usage, strategic fit)
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TIMECategory(Enum):
    """TIME framework categories for application rationalization."""

    INVEST = "Invest"
    TOLERATE = "Tolerate"
    MIGRATE = "Migrate"
    ELIMINATE = "Eliminate"


@dataclass
class TIMEThresholds:
    """
    Configurable thresholds for TIME framework categorization.

    These thresholds define the boundaries between TIME categories based on
    business value and technical quality scores.

    Attributes:
        business_value_threshold: Threshold above which apps are considered high business value (0-10)
        technical_quality_threshold: Threshold above which apps are considered good technical quality (0-10)
        composite_score_high: Composite score threshold for high-quality apps (0-100)
        composite_score_low: Composite score threshold for low-quality apps (0-100)
        critical_business_value: Score above which business value is critical (0-10)
        poor_tech_health: Score below which tech health is poor (0-10)
        poor_security: Score below which security is poor (0-10)
    """

    business_value_threshold: float = 6.0
    technical_quality_threshold: float = 6.0
    composite_score_high: float = 65.0
    composite_score_low: float = 40.0
    critical_business_value: float = 8.0
    poor_tech_health: float = 4.0
    poor_security: float = 5.0

    def validate(self) -> bool:
        """
        Validate threshold values are within acceptable ranges.

        Returns:
            True if all thresholds are valid, False otherwise
        """
        if not (0 <= self.business_value_threshold <= 10):
            return False
        if not (0 <= self.technical_quality_threshold <= 10):
            return False
        if not (0 <= self.composite_score_high <= 100):
            return False
        if not (0 <= self.composite_score_low <= 100):
            return False
        if self.composite_score_low >= self.composite_score_high:
            return False
        return True


class TIMEFramework:
    """
    TIME Framework implementation for application portfolio rationalization.

    This class provides methods to categorize applications using the TIME framework,
    which is based on a quadrant model of business value vs. technical quality.

    The framework helps organizations make strategic decisions about their application
    portfolio by providing clear, actionable categories.
    """

    def __init__(self, thresholds: Optional[TIMEThresholds] = None):
        """
        Initialize the TIME framework with optional custom thresholds.

        Args:
            thresholds: Custom threshold configuration. Uses defaults if not provided.

        Raises:
            ValueError: If provided thresholds are invalid
        """
        self.thresholds = thresholds or TIMEThresholds()

        if not self.thresholds.validate():
            raise ValueError("Invalid TIME framework thresholds")

        # Track categorization statistics
        self.category_counts = {cat.value: 0 for cat in TIMECategory}

    def calculate_business_value_score(
        self,
        business_value: float,
        usage: float,
        strategic_fit: float,
        max_usage: float = 1000
    ) -> float:
        """
        Calculate a composite business value score.

        This score combines multiple business-related metrics to determine
        the overall business value of an application.

        Args:
            business_value: Business value score (0-10)
            usage: Usage metric (e.g., active users)
            strategic_fit: Strategic alignment score (0-10)
            max_usage: Maximum expected usage for normalization

        Returns:
            Composite business value score (0-10)

        Formula:
            BV Score = (business_value × 0.5) + (usage_normalized × 0.2) + (strategic_fit × 0.3)

        The weights prioritize:
            - Direct business value (50%)
            - Strategic alignment (30%)
            - Actual usage (20%)
        """
        # Normalize usage to 0-10 scale
        usage_normalized = min(usage / max_usage * 10, 10)

        # Calculate weighted composite
        bv_score = (
            business_value * 0.5 +
            usage_normalized * 0.2 +
            strategic_fit * 0.3
        )

        return round(bv_score, 2)

    def calculate_technical_quality_score(
        self,
        tech_health: float,
        security: float,
        strategic_fit: float,
        cost: float,
        max_cost: float = 300000
    ) -> float:
        """
        Calculate a composite technical quality score.

        This score combines technical metrics to determine the overall
        technical quality and sustainability of an application.

        Args:
            tech_health: Technical health score (0-10)
            security: Security posture score (0-10)
            strategic_fit: Strategic technology alignment (0-10)
            cost: Annual cost
            max_cost: Maximum expected cost for normalization

        Returns:
            Composite technical quality score (0-10)

        Formula:
            TQ Score = (tech_health × 0.4) + (security × 0.3) +
                      (strategic_fit × 0.2) + (cost_efficiency × 0.1)

        The weights prioritize:
            - Technical health and maintainability (40%)
            - Security posture (30%)
            - Strategic technology fit (20%)
            - Cost efficiency (10%)
        """
        # Calculate cost efficiency (lower cost = higher score)
        cost_normalized = min(cost / max_cost, 1.0)
        cost_efficiency = 10 * (1 - cost_normalized)

        # Calculate weighted composite
        tq_score = (
            tech_health * 0.4 +
            security * 0.3 +
            strategic_fit * 0.2 +
            cost_efficiency * 0.1
        )

        return round(tq_score, 2)

    def categorize_application(
        self,
        business_value: float,
        tech_health: float,
        security: float,
        strategic_fit: float,
        usage: float,
        cost: float,
        composite_score: float,
        redundancy: int = 0
    ) -> Tuple[str, str]:
        """
        Categorize an application using the TIME framework.

        This is the core categorization logic that assigns applications to one of
        the four TIME categories based on business value and technical quality.

        Args:
            business_value: Business value score (0-10)
            tech_health: Technical health score (0-10)
            security: Security score (0-10)
            strategic_fit: Strategic fit score (0-10)
            usage: Usage metric
            cost: Annual cost
            composite_score: Overall composite score (0-100)
            redundancy: Redundancy flag (0 or 1)

        Returns:
            Tuple of (TIME_category, rationale_text)

        Decision Logic:
            1. Calculate business value score (BV)
            2. Calculate technical quality score (TQ)
            3. Apply quadrant logic:
                - High BV, High TQ → INVEST
                - High BV, Low TQ → TOLERATE (or MIGRATE if critical issues)
                - Low BV, High TQ → MIGRATE
                - Low BV, Low TQ → ELIMINATE
            4. Apply special cases (security risks, redundancy, etc.)
        """
        # Calculate composite scores for the two TIME dimensions
        bv_score = self.calculate_business_value_score(
            business_value, usage, strategic_fit
        )
        tq_score = self.calculate_technical_quality_score(
            tech_health, security, strategic_fit, cost
        )

        # Determine high/low classifications
        high_business_value = bv_score >= self.thresholds.business_value_threshold
        high_technical_quality = tq_score >= self.thresholds.technical_quality_threshold

        # Special case flags
        critical_business = business_value >= self.thresholds.critical_business_value
        poor_tech = tech_health <= self.thresholds.poor_tech_health
        poor_security_flag = security <= self.thresholds.poor_security
        is_redundant = redundancy == 1
        high_composite = composite_score >= self.thresholds.composite_score_high
        low_composite = composite_score <= self.thresholds.composite_score_low

        # Apply TIME framework logic with detailed rationale
        category, rationale = self._apply_time_logic(
            bv_score=bv_score,
            tq_score=tq_score,
            high_business_value=high_business_value,
            high_technical_quality=high_technical_quality,
            critical_business=critical_business,
            poor_tech=poor_tech,
            poor_security_flag=poor_security_flag,
            is_redundant=is_redundant,
            high_composite=high_composite,
            low_composite=low_composite,
            composite_score=composite_score,
            business_value=business_value,
            tech_health=tech_health,
            security=security
        )

        # Track statistics
        self.category_counts[category] += 1

        return category, rationale

    def _apply_time_logic(
        self,
        bv_score: float,
        tq_score: float,
        high_business_value: bool,
        high_technical_quality: bool,
        critical_business: bool,
        poor_tech: bool,
        poor_security_flag: bool,
        is_redundant: bool,
        high_composite: bool,
        low_composite: bool,
        composite_score: float,
        business_value: float,
        tech_health: float,
        security: float
    ) -> Tuple[str, str]:
        """
        Apply TIME framework categorization logic.

        This internal method contains the decision tree for TIME categorization.
        It's separated to keep the main categorize_application method clean.

        Returns:
            Tuple of (category, rationale)
        """
        # QUADRANT 1: High Business Value, High Technical Quality → INVEST
        if high_business_value and high_technical_quality:
            return (
                TIMECategory.INVEST.value,
                f"High business value (BV: {bv_score:.1f}/10) and strong technical quality "
                f"(TQ: {tq_score:.1f}/10). Continue investment to maximize returns and "
                f"maintain competitive advantage. Composite score: {composite_score:.1f}/100."
            )

        # QUADRANT 2: High Business Value, Low Technical Quality → TOLERATE or MIGRATE
        if high_business_value and not high_technical_quality:
            # Critical business with severe technical issues → MIGRATE urgently
            if critical_business and (poor_tech or poor_security_flag):
                return (
                    TIMECategory.MIGRATE.value,
                    f"Critical business value ({business_value:.1f}/10) but poor technical quality "
                    f"(TQ: {tq_score:.1f}/10). Technical debt and {'security' if poor_security_flag else 'health'} "
                    f"risks require urgent migration to modern platform."
                )
            # Otherwise, tolerate current state while planning improvements
            else:
                return (
                    TIMECategory.TOLERATE.value,
                    f"High business value (BV: {bv_score:.1f}/10) justifies retention despite "
                    f"moderate technical quality (TQ: {tq_score:.1f}/10). Maintain current operations "
                    f"while planning technical improvements. Composite score: {composite_score:.1f}/100."
                )

        # QUADRANT 3: Low Business Value, High Technical Quality → MIGRATE
        if not high_business_value and high_technical_quality:
            # Good tech but redundant → ELIMINATE
            if is_redundant:
                return (
                    TIMECategory.ELIMINATE.value,
                    f"Redundant functionality with low business value (BV: {bv_score:.1f}/10) despite "
                    f"good technical quality (TQ: {tq_score:.1f}/10). Consolidate with primary system "
                    f"to reduce complexity and costs."
                )
            # Good tech, low value → MIGRATE to better use
            else:
                return (
                    TIMECategory.MIGRATE.value,
                    f"Good technical quality (TQ: {tq_score:.1f}/10) but limited business value "
                    f"(BV: {bv_score:.1f}/10). Consider migration, consolidation, or repurposing "
                    f"to better align with business needs."
                )

        # QUADRANT 4: Low Business Value, Low Technical Quality → ELIMINATE
        if not high_business_value and not high_technical_quality:
            # Definitive elimination candidates
            if low_composite or is_redundant:
                return (
                    TIMECategory.ELIMINATE.value,
                    f"Low business value (BV: {bv_score:.1f}/10) and poor technical quality "
                    f"(TQ: {tq_score:.1f}/10) with composite score of {composite_score:.1f}/100. "
                    f"{'Redundant functionality makes this ' if is_redundant else ''}Strong candidate "
                    f"for retirement to reduce technical debt and operational costs."
                )
            # Some redeeming qualities → MIGRATE instead of eliminate
            else:
                return (
                    TIMECategory.MIGRATE.value,
                    f"Moderate scores (BV: {bv_score:.1f}/10, TQ: {tq_score:.1f}/10) suggest "
                    f"migration or modernization opportunity. Composite score: {composite_score:.1f}/100. "
                    f"Evaluate consolidation options before elimination."
                )

        # Edge case fallback (should rarely trigger)
        # This handles boundary cases where scores are exactly at thresholds
        if composite_score >= 60:
            return (
                TIMECategory.TOLERATE.value,
                f"Moderate composite score ({composite_score:.1f}/100) with balanced metrics "
                f"(BV: {bv_score:.1f}/10, TQ: {tq_score:.1f}/10). Monitor and reassess during "
                f"next planning cycle."
            )
        else:
            return (
                TIMECategory.MIGRATE.value,
                f"Below-threshold scores (BV: {bv_score:.1f}/10, TQ: {tq_score:.1f}/10) suggest "
                f"migration planning. Composite score: {composite_score:.1f}/100. "
                f"Evaluate modernization or consolidation opportunities."
            )

    def batch_categorize(self, applications: List[Dict]) -> List[Dict]:
        """
        Categorize multiple applications using the TIME framework.

        This method processes a batch of applications and adds TIME categorization
        to each one.

        Args:
            applications: List of application dictionaries with assessment data

        Returns:
            List of applications with added 'TIME Category' and 'TIME Rationale' fields

        Note:
            Applications must have already been scored (composite score calculated).
            Missing required fields will result in 'Tolerate' default categorization.
        """
        # Convert DataFrame to list of dicts if needed, but remember if it was a DataFrame
        import pandas as pd
        was_dataframe = isinstance(applications, pd.DataFrame)
        if was_dataframe:
            applications = applications.to_dict('records')

        results = []

        for app in applications:
            try:
                # Extract required fields with defaults
                category, rationale = self.categorize_application(
                    business_value=float(app.get('Business Value', 5)),
                    tech_health=float(app.get('Tech Health', 5)),
                    security=float(app.get('Security', 5)),
                    strategic_fit=float(app.get('Strategic Fit', 5)),
                    usage=float(app.get('Usage', 0)),
                    cost=float(app.get('Cost', 0)),
                    composite_score=float(app.get('Composite Score', 50)),
                    redundancy=int(app.get('Redundancy', 0))
                )

                # Add TIME categorization to application
                app_result = app.copy()
                app_result['TIME Category'] = category
                app_result['TIME Rationale'] = rationale

                # Calculate and include the dimensional scores for transparency
                bv_score = self.calculate_business_value_score(
                    float(app.get('Business Value', 5)),
                    float(app.get('Usage', 0)),
                    float(app.get('Strategic Fit', 5))
                )
                tq_score = self.calculate_technical_quality_score(
                    float(app.get('Tech Health', 5)),
                    float(app.get('Security', 5)),
                    float(app.get('Strategic Fit', 5)),
                    float(app.get('Cost', 0))
                )

                app_result['TIME Business Value Score'] = bv_score
                app_result['TIME Technical Quality Score'] = tq_score

                results.append(app_result)

            except (ValueError, KeyError) as e:
                logger.error(
                    f"Error categorizing {app.get('Application Name', 'Unknown')}: {e}"
                )
                # Default to Tolerate for error cases
                app_result = app.copy()
                app_result['TIME Category'] = TIMECategory.TOLERATE.value
                app_result['TIME Rationale'] = "Unable to categorize - data quality issues. Default to Tolerate."
                app_result['TIME Business Value Score'] = 5.0
                app_result['TIME Technical Quality Score'] = 5.0
                results.append(app_result)

        # Convert back to DataFrame if input was a DataFrame
        if was_dataframe:
            return pd.DataFrame(results)
        return results

    def get_category_summary(self) -> Dict:
        """
        Get summary statistics of TIME categorizations.

        Returns:
            Dictionary with category counts and percentages

        Example:
            {
                'total': 100,
                'distribution': {'Invest': 25, 'Tolerate': 30, 'Migrate': 20, 'Eliminate': 25},
                'percentages': {'Invest': 25.0, 'Tolerate': 30.0, 'Migrate': 20.0, 'Eliminate': 25.0}
            }
        """
        total = sum(self.category_counts.values())

        if total == 0:
            return {'total': 0, 'distribution': {}, 'percentages': {}}

        summary = {
            'total': total,
            'distribution': dict(self.category_counts),
            'percentages': {}
        }

        for category, count in self.category_counts.items():
            summary['percentages'][category] = round((count / total) * 100, 1)

        return summary

    def get_portfolio_matrix(self, applications: List[Dict]) -> Dict:
        """
        Generate a TIME framework matrix showing application distribution.

        This creates a 2x2 matrix visualization data showing how applications
        are distributed across the TIME quadrants.

        Args:
            applications: List of applications with TIME categorization

        Returns:
            Dictionary with quadrant distribution and counts

        The matrix structure:
            High BV |  TOLERATE  |  INVEST  |
                    |            |          |
            Low BV  | ELIMINATE  | MIGRATE  |
                    +------------------------
                      Low TQ      High TQ
        """
        matrix = {
            'quadrants': {
                'invest': [],      # High BV, High TQ
                'tolerate': [],    # High BV, Low TQ
                'migrate': [],     # Low BV, High TQ
                'eliminate': []    # Low BV, Low TQ
            },
            'counts': {
                'invest': 0,
                'tolerate': 0,
                'migrate': 0,
                'eliminate': 0
            }
        }

        for app in applications:
            category = app.get('TIME Category', '').lower()
            if category in matrix['quadrants']:
                matrix['quadrants'][category].append(app.get('Application Name', 'Unknown'))
                matrix['counts'][category] += 1

        return matrix

    def reset_counts(self):
        """Reset category counts for new analysis."""
        self.category_counts = {cat.value: 0 for cat in TIMECategory}
