"""
AI Assistant for Capital Projects Lifecycle Planner
Provides natural language Q&A about project portfolio with actionable insights.
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import pandas as pd


class QueryType(Enum):
    """Types of queries the assistant can handle."""
    PROJECTS_DOING_WELL = "projects_doing_well"
    PROJECTS_AT_RISK = "projects_at_risk"
    PROJECTS_OVER_BUDGET = "over_budget"
    PROJECTS_BEHIND_SCHEDULE = "behind_schedule"
    PROJECTS_BY_STATUS = "by_status"
    PROJECTS_BY_PHASE = "by_phase"
    PROJECTS_BY_DISTRICT = "by_district"
    PROJECTS_BY_TYPE = "by_type"
    PROJECT_SPECIFIC = "specific_project"
    SUMMARY = "summary"
    RECOMMENDATIONS = "recommendations"
    UNKNOWN = "unknown"


@dataclass
class ChatResponse:
    """Structured response from the AI assistant."""
    message: str
    projects: List[Dict]  # Related projects
    key_points: List[str]  # Bullet points
    follow_up_prompt: Optional[str]  # Suggested follow-up
    filter_params: Dict  # For linking to filtered view
    show_details_prompt: bool  # Whether to offer more details


class ProjectAIAssistant:
    """
    AI Assistant that answers questions about the capital projects portfolio.

    Supports natural language queries about:
    - Project health and status
    - Budget and schedule performance
    - Projects by category, phase, district
    - Recommendations and insights
    """

    def __init__(self):
        self.query_patterns = self._build_query_patterns()

    def _build_query_patterns(self) -> Dict[QueryType, List[str]]:
        """Build regex patterns for query classification."""
        return {
            QueryType.PROJECTS_DOING_WELL: [
                r'doing (well|good|great)',
                r'(good|healthy|strong) (project|health)',
                r'on track',
                r'succeeding',
                r'performing well',
                r'(best|top) (performing|project)',
                r'which.*(advance|green)',
            ],
            QueryType.PROJECTS_AT_RISK: [
                r'at risk',
                r'(problem|issue|trouble|concern)',
                r'struggling',
                r'(bad|poor|low) (health|score|performance)',
                r'need(s|ing)? attention',
                r'(worst|bottom) performing',
                r'(red|danger)',
                r'failing',
            ],
            QueryType.PROJECTS_OVER_BUDGET: [
                r'over budget',
                r'budget (issue|problem|concern|overrun)',
                r'cost (overrun|issue|problem)',
                r'spending (too much|more)',
                r'financial (issue|problem|concern)',
            ],
            QueryType.PROJECTS_BEHIND_SCHEDULE: [
                r'behind schedule',
                r'(late|delay|delayed|slipping)',
                r'schedule (issue|problem|concern|slip)',
                r'(taking|running) (too )?long',
                r'timeline (issue|problem)',
            ],
            QueryType.PROJECTS_BY_STATUS: [
                r'(advance|monitor|rescope|re-scope|defer|cancel)',
                r'status.*(advance|monitor|rescope|defer|cancel)',
            ],
            QueryType.PROJECTS_BY_PHASE: [
                r'(in |at )?(concept|feasibility|design|construction|procurement|permitting|closeout)',
                r'phase.*(concept|feasibility|design|construction|procurement|permitting)',
                r'under construction',
                r'being designed',
            ],
            QueryType.PROJECTS_BY_DISTRICT: [
                r'district\s*(\d+)',
                r'commissioner.*(district|\d)',
            ],
            QueryType.PROJECTS_BY_TYPE: [
                r'(widening|resurfacing|bridge|safety|intersection|stormwater|sidewalk|trail|signal)',
                r'type.*(widening|resurfacing|bridge|safety|intersection|stormwater)',
            ],
            QueryType.PROJECT_SPECIFIC: [
                r'(tell me about|what about|how is|status of)\s+(.+)',
                r'project.*(CP-\d+-\d+)',
                r'(SR|CR|US|NW|NE|SW|SE)\s*\d+',
            ],
            QueryType.SUMMARY: [
                r'(overview|summary|overall|total|how many)',
                r'portfolio (status|health|summary)',
                r'(all|entire) (project|portfolio)',
            ],
            QueryType.RECOMMENDATIONS: [
                r'(recommend|suggestion|advice|should|priority|prioritize)',
                r'what should (we|i) (do|focus)',
                r'action (item|needed)',
            ],
        }

    def classify_query(self, query: str) -> Tuple[QueryType, Dict]:
        """Classify the user's query and extract parameters."""
        query_lower = query.lower()
        extracted_params = {}

        # Check each query type
        for query_type, patterns in self.query_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query_lower)
                if match:
                    # Extract any captured groups
                    if match.groups():
                        extracted_params['match'] = match.groups()

                    # Special handling for district numbers
                    if query_type == QueryType.PROJECTS_BY_DISTRICT:
                        district_match = re.search(r'district\s*(\d+)', query_lower)
                        if district_match:
                            extracted_params['district'] = int(district_match.group(1))

                    return query_type, extracted_params

        return QueryType.UNKNOWN, extracted_params

    def process_query(self, query: str, df: pd.DataFrame) -> ChatResponse:
        """
        Process a natural language query and return a structured response.

        Args:
            query: User's question
            df: DataFrame with scored and categorized projects

        Returns:
            ChatResponse with message, projects, and insights
        """
        query_type, params = self.classify_query(query)

        # Route to appropriate handler
        handlers = {
            QueryType.PROJECTS_DOING_WELL: self._handle_projects_doing_well,
            QueryType.PROJECTS_AT_RISK: self._handle_projects_at_risk,
            QueryType.PROJECTS_OVER_BUDGET: self._handle_over_budget,
            QueryType.PROJECTS_BEHIND_SCHEDULE: self._handle_behind_schedule,
            QueryType.PROJECTS_BY_STATUS: self._handle_by_status,
            QueryType.PROJECTS_BY_PHASE: self._handle_by_phase,
            QueryType.PROJECTS_BY_DISTRICT: self._handle_by_district,
            QueryType.PROJECTS_BY_TYPE: self._handle_by_type,
            QueryType.SUMMARY: self._handle_summary,
            QueryType.RECOMMENDATIONS: self._handle_recommendations,
            QueryType.UNKNOWN: self._handle_unknown,
        }

        handler = handlers.get(query_type, self._handle_unknown)
        return handler(query, df, params)

    def _handle_projects_doing_well(self, query: str, df: pd.DataFrame, params: Dict) -> ChatResponse:
        """Handle queries about projects performing well."""
        # Filter for healthy projects
        good_projects = df[df['Project Health Score'] >= 70].copy()
        good_projects = good_projects.sort_values('Project Health Score', ascending=False)

        if len(good_projects) == 0:
            return ChatResponse(
                message="Currently, no projects are scoring above 70 in overall health. However, let me show you the top performers.",
                projects=df.nlargest(5, 'Project Health Score').to_dict('records'),
                key_points=[
                    f"Highest health score is {df['Project Health Score'].max():.0f}",
                    "Consider reviewing scoring thresholds"
                ],
                follow_up_prompt="Would you like to see projects that need attention instead?",
                filter_params={'min_health': 60},
                show_details_prompt=True
            )

        top_projects = good_projects.head(5)
        key_points = []

        for _, proj in top_projects.iterrows():
            reasons = []
            if proj.get('Strategic Value Score', 0) >= 70:
                reasons.append("high strategic value")
            if proj.get('Deliverability Score', 0) >= 70:
                reasons.append("strong deliverability")
            if proj.get('Schedule Health', 50) >= 60:
                reasons.append("on schedule")
            if proj.get('Budget Health', 50) >= 60:
                reasons.append("on budget")

            reason_text = ", ".join(reasons) if reasons else "balanced metrics"
            key_points.append(f"**{proj['Project Name']}** (Health: {proj['Project Health Score']:.0f}) - {reason_text}")

        return ChatResponse(
            message=f"Great news! I found **{len(good_projects)} projects** performing well with health scores above 70.",
            projects=top_projects.to_dict('records'),
            key_points=key_points,
            follow_up_prompt="Would you like details on what's making these projects successful?",
            filter_params={'status': 'Advance', 'min_health': 70},
            show_details_prompt=True
        )

    def _handle_projects_at_risk(self, query: str, df: pd.DataFrame, params: Dict) -> ChatResponse:
        """Handle queries about projects at risk."""
        # Filter for at-risk projects
        at_risk = df[df['Project Health Score'] < 50].copy()
        at_risk = at_risk.sort_values('Project Health Score', ascending=True)

        if len(at_risk) == 0:
            return ChatResponse(
                message="Good news! No projects are currently in critical health (below 50). However, here are projects to watch:",
                projects=df.nsmallest(5, 'Project Health Score').to_dict('records'),
                key_points=["All projects are maintaining acceptable health scores"],
                follow_up_prompt="Would you like to see the projects doing well instead?",
                filter_params={'max_health': 60},
                show_details_prompt=False
            )

        key_points = []
        for _, proj in at_risk.head(5).iterrows():
            issues = []
            if proj.get('Schedule Health', 50) < 50:
                issues.append("schedule delays")
            if proj.get('Budget Health', 50) < 50:
                issues.append("budget overrun")
            if proj.get('Deliverability Score', 50) < 50:
                issues.append("deliverability concerns (ROW/utilities/permits)")
            if proj.get('Risk Score', 50) < 40:
                issues.append("high risk level")

            issue_text = ", ".join(issues) if issues else "multiple contributing factors"
            key_points.append(f"**{proj['Project Name']}** (Health: {proj['Project Health Score']:.0f}) - Issues: {issue_text}")

        return ChatResponse(
            message=f"I found **{len(at_risk)} projects** that need attention with health scores below 50.",
            projects=at_risk.head(5).to_dict('records'),
            key_points=key_points,
            follow_up_prompt="Would you like more details on any of these projects, or recommendations for addressing these issues?",
            filter_params={'status': ['Re-scope', 'Defer', 'Cancel'], 'max_health': 50},
            show_details_prompt=True
        )

    def _handle_over_budget(self, query: str, df: pd.DataFrame, params: Dict) -> ChatResponse:
        """Handle queries about budget issues."""
        # Calculate budget variance
        df_copy = df.copy()
        df_copy['Budget Variance'] = df_copy['Total Budget'] - df_copy['Forecast at Completion'].fillna(df_copy['Total Budget'])
        df_copy['Budget Variance %'] = (df_copy['Budget Variance'] / df_copy['Total Budget'] * 100).round(1)

        over_budget = df_copy[df_copy['Budget Variance'] < 0].sort_values('Budget Variance')

        if len(over_budget) == 0:
            return ChatResponse(
                message="Excellent! All projects are currently on or under budget.",
                projects=[],
                key_points=[
                    f"Total portfolio budget: ${df['Total Budget'].sum()/1e6:.1f}M",
                    f"No projects exceeding budget forecasts"
                ],
                follow_up_prompt="Would you like to see projects with schedule concerns instead?",
                filter_params={},
                show_details_prompt=False
            )

        key_points = []
        total_overrun = abs(over_budget['Budget Variance'].sum())

        for _, proj in over_budget.head(5).iterrows():
            overrun = abs(proj['Budget Variance'])
            pct = abs(proj['Budget Variance %'])
            key_points.append(
                f"**{proj['Project Name']}** - ${overrun/1e6:.2f}M over budget ({pct:.1f}% variance)"
            )

        return ChatResponse(
            message=f"I found **{len(over_budget)} projects** with budget concerns, totaling **${total_overrun/1e6:.2f}M** in overruns.",
            projects=over_budget.head(5).to_dict('records'),
            key_points=key_points,
            follow_up_prompt="Would you like recommendations on addressing these budget issues?",
            filter_params={'budget_issue': True},
            show_details_prompt=True
        )

    def _handle_behind_schedule(self, query: str, df: pd.DataFrame, params: Dict) -> ChatResponse:
        """Handle queries about schedule issues."""
        behind_schedule = df[df['Schedule Health'] < 50].sort_values('Schedule Health')

        if len(behind_schedule) == 0:
            return ChatResponse(
                message="Good news! All projects are currently on or ahead of schedule.",
                projects=[],
                key_points=["No significant schedule delays detected"],
                follow_up_prompt="Would you like to see projects with budget concerns instead?",
                filter_params={},
                show_details_prompt=False
            )

        key_points = []
        for _, proj in behind_schedule.head(5).iterrows():
            pct_complete = proj.get('Percent Complete', 0)
            phase = proj.get('Current Phase', 'Unknown')
            key_points.append(
                f"**{proj['Project Name']}** - {pct_complete:.0f}% complete, currently in {phase}"
            )

        return ChatResponse(
            message=f"I found **{len(behind_schedule)} projects** experiencing schedule delays.",
            projects=behind_schedule.head(5).to_dict('records'),
            key_points=key_points,
            follow_up_prompt="Would you like to understand the root causes of these delays?",
            filter_params={'schedule_issue': True},
            show_details_prompt=True
        )

    def _handle_by_status(self, query: str, df: pd.DataFrame, params: Dict) -> ChatResponse:
        """Handle queries filtered by status."""
        query_lower = query.lower()

        # Determine which status
        status_map = {
            'advance': 'Advance',
            'monitor': 'Monitor',
            'rescope': 'Re-scope',
            're-scope': 'Re-scope',
            'defer': 'Defer',
            'cancel': 'Cancel'
        }

        status = None
        for key, value in status_map.items():
            if key in query_lower:
                status = value
                break

        if status:
            filtered = df[df['Status'] == status]
            return ChatResponse(
                message=f"There are **{len(filtered)} projects** with '{status}' status.",
                projects=filtered.to_dict('records'),
                key_points=[f"{proj['Project Name']} - {proj['Current Phase']}" for _, proj in filtered.head(5).iterrows()],
                follow_up_prompt=f"Would you like details on why these projects are categorized as '{status}'?",
                filter_params={'status': status},
                show_details_prompt=True
            )

        return self._handle_summary(query, df, params)

    def _handle_by_phase(self, query: str, df: pd.DataFrame, params: Dict) -> ChatResponse:
        """Handle queries filtered by phase."""
        query_lower = query.lower()

        phase_map = {
            'concept': 'Concept/Idea',
            'feasibility': 'Feasibility/Planning',
            'design': 'Design',
            'construction': 'Active Construction',
            'procurement': 'Procurement/Letting',
            'permitting': 'Permitting/Utility Coordination',
            'closeout': 'Final Acceptance/Closeout',
            'right-of-way': 'Right-of-Way Acquisition',
            'row': 'Right-of-Way Acquisition',
        }

        phase = None
        for key, value in phase_map.items():
            if key in query_lower:
                phase = value
                break

        if phase:
            filtered = df[df['Current Phase'] == phase]
            total_budget = filtered['Total Budget'].sum()
            return ChatResponse(
                message=f"There are **{len(filtered)} projects** in the '{phase}' phase with a combined budget of **${total_budget/1e6:.1f}M**.",
                projects=filtered.to_dict('records'),
                key_points=[f"{proj['Project Name']} - ${proj['Total Budget']/1e6:.1f}M" for _, proj in filtered.head(5).iterrows()],
                follow_up_prompt="Would you like to see the health scores for these projects?",
                filter_params={'phase': phase},
                show_details_prompt=True
            )

        return self._handle_summary(query, df, params)

    def _handle_by_district(self, query: str, df: pd.DataFrame, params: Dict) -> ChatResponse:
        """Handle queries filtered by district."""
        district = params.get('district')

        if district:
            filtered = df[df['District'] == district]
            if len(filtered) == 0:
                return ChatResponse(
                    message=f"No projects found in District {district}.",
                    projects=[],
                    key_points=[],
                    follow_up_prompt="Would you like to see projects in a different district?",
                    filter_params={},
                    show_details_prompt=False
                )

            total_budget = filtered['Total Budget'].sum()
            avg_health = filtered['Project Health Score'].mean()

            return ChatResponse(
                message=f"District {district} has **{len(filtered)} projects** with a combined budget of **${total_budget/1e6:.1f}M** and average health score of **{avg_health:.0f}**.",
                projects=filtered.to_dict('records'),
                key_points=[f"{proj['Project Name']} - Health: {proj['Project Health Score']:.0f}" for _, proj in filtered.iterrows()],
                follow_up_prompt=f"Would you like to know which District {district} projects need attention?",
                filter_params={'district': district},
                show_details_prompt=True
            )

        return self._handle_summary(query, df, params)

    def _handle_by_type(self, query: str, df: pd.DataFrame, params: Dict) -> ChatResponse:
        """Handle queries filtered by project type."""
        query_lower = query.lower()

        type_map = {
            'widening': 'Road Widening',
            'resurfacing': 'Resurfacing',
            'bridge': 'Bridge',
            'safety': 'Safety Improvement',
            'intersection': 'Intersection Improvement',
            'stormwater': 'Stormwater',
            'sidewalk': 'Sidewalk/Trail',
            'trail': 'Sidewalk/Trail',
            'signal': 'Traffic Signals',
        }

        proj_type = None
        for key, value in type_map.items():
            if key in query_lower:
                proj_type = value
                break

        if proj_type:
            filtered = df[df['Project Type'] == proj_type]
            total_budget = filtered['Total Budget'].sum()

            return ChatResponse(
                message=f"There are **{len(filtered)} {proj_type}** projects with a combined budget of **${total_budget/1e6:.1f}M**.",
                projects=filtered.to_dict('records'),
                key_points=[f"{proj['Project Name']} - {proj['Current Phase']}" for _, proj in filtered.head(5).iterrows()],
                follow_up_prompt=f"Would you like to see which {proj_type} projects are performing best?",
                filter_params={'type': proj_type},
                show_details_prompt=True
            )

        return self._handle_summary(query, df, params)

    def _handle_summary(self, query: str, df: pd.DataFrame, params: Dict) -> ChatResponse:
        """Handle general summary queries."""
        total_projects = len(df)
        total_budget = df['Total Budget'].sum()
        avg_health = df['Project Health Score'].mean()

        status_counts = df['Status'].value_counts().to_dict()
        phase_counts = df['Current Phase'].value_counts()

        key_points = [
            f"**{total_projects}** total projects in the portfolio",
            f"**${total_budget/1e6:.1f}M** total program value",
            f"**{avg_health:.0f}** average health score",
            f"**{status_counts.get('Advance', 0)}** projects ready to advance",
            f"**{status_counts.get('Re-scope', 0) + status_counts.get('Defer', 0)}** projects needing attention",
        ]

        return ChatResponse(
            message="Here's an overview of your capital projects portfolio:",
            projects=df.nlargest(5, 'Total Budget').to_dict('records'),
            key_points=key_points,
            follow_up_prompt="What would you like to know more about? (e.g., projects at risk, budget status, specific districts)",
            filter_params={},
            show_details_prompt=True
        )

    def _handle_recommendations(self, query: str, df: pd.DataFrame, params: Dict) -> ChatResponse:
        """Handle requests for recommendations."""
        recommendations = []
        priority_projects = []

        # Find projects needing immediate attention
        critical = df[df['Project Health Score'] < 40]
        if len(critical) > 0:
            recommendations.append(f"**Immediate Action**: {len(critical)} project(s) have critical health scores below 40")
            priority_projects.extend(critical.to_dict('records'))

        # Budget issues
        df_copy = df.copy()
        df_copy['Budget Variance'] = df_copy['Total Budget'] - df_copy['Forecast at Completion'].fillna(df_copy['Total Budget'])
        over_budget = df_copy[df_copy['Budget Variance'] < -100000]  # Over by >$100k
        if len(over_budget) > 0:
            total_overrun = abs(over_budget['Budget Variance'].sum())
            recommendations.append(f"**Budget Review**: {len(over_budget)} project(s) are over budget by ${total_overrun/1e6:.2f}M total")

        # Schedule issues
        behind = df[df['Schedule Health'] < 40]
        if len(behind) > 0:
            recommendations.append(f"**Schedule Recovery**: {len(behind)} project(s) have significant schedule delays")

        # Projects ready to advance
        ready = df[(df['Status'] == 'Advance') | (df['Project Health Score'] >= 75)]
        if len(ready) > 0:
            recommendations.append(f"**Accelerate**: {len(ready)} project(s) are healthy and ready for acceleration")

        # Re-scope candidates
        rescope = df[df['Status'] == 'Re-scope']
        if len(rescope) > 0:
            recommendations.append(f"**Re-scope**: {len(rescope)} project(s) need scope or approach adjustments")

        if not recommendations:
            recommendations.append("Portfolio is generally healthy - continue monitoring")

        return ChatResponse(
            message="Based on my analysis, here are my recommendations:",
            projects=priority_projects[:5] if priority_projects else df.nsmallest(3, 'Project Health Score').to_dict('records'),
            key_points=recommendations,
            follow_up_prompt="Would you like details on any of these recommendations?",
            filter_params={'needs_attention': True},
            show_details_prompt=True
        )

    def _handle_unknown(self, query: str, df: pd.DataFrame, params: Dict) -> ChatResponse:
        """Handle unrecognized queries."""
        return ChatResponse(
            message="I'm not sure I understood that question. Here are some things you can ask me:",
            projects=[],
            key_points=[
                "**\"Which projects are doing well?\"** - See healthy projects",
                "**\"What projects are at risk?\"** - Find projects needing attention",
                "**\"Show me projects over budget\"** - Budget analysis",
                "**\"What's behind schedule?\"** - Schedule analysis",
                "**\"Projects in District 3\"** - Filter by commissioner district",
                "**\"Show construction projects\"** - Filter by phase",
                "**\"Give me recommendations\"** - Get actionable insights",
            ],
            follow_up_prompt=None,
            filter_params={},
            show_details_prompt=False
        )


def format_response_as_html(response: ChatResponse) -> str:
    """Format ChatResponse as HTML for display."""
    html = f'<div class="chat-response">'
    html += f'<p class="message">{response.message}</p>'

    if response.key_points:
        html += '<ul class="key-points">'
        for point in response.key_points:
            html += f'<li>{point}</li>'
        html += '</ul>'

    if response.follow_up_prompt:
        html += f'<p class="follow-up">{response.follow_up_prompt}</p>'

    html += '</div>'
    return html
