"""
Claude LLM-powered AI Assistant for Capital Projects Lifecycle Planner
Uses Anthropic's Claude API for sophisticated natural language responses.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import pandas as pd

logger = logging.getLogger(__name__)

# Try to import anthropic
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("anthropic package not installed. Run: pip install anthropic")


@dataclass
class ClaudeResponse:
    """Structured response from Claude assistant."""
    message: str
    projects: List[Dict]
    key_points: List[str]
    follow_up_prompt: Optional[str]
    filter_params: Dict
    show_details_prompt: bool


class ClaudeProjectAssistant:
    """
    Claude-powered AI Assistant for capital projects portfolio analysis.

    Uses Claude to provide intelligent, contextual responses about projects.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Claude assistant.

        Args:
            api_key: Anthropic API key. If not provided, looks for ANTHROPIC_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        self.client = None
        self.model = "claude-sonnet-4-20250514"  # Use Claude 3.5 Sonnet for speed/cost balance

        if ANTHROPIC_AVAILABLE and self.api_key:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.info("Claude assistant initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Claude client: {e}")
        else:
            if not ANTHROPIC_AVAILABLE:
                logger.warning("Anthropic package not available")
            if not self.api_key:
                logger.warning("No API key provided for Claude")

    def is_available(self) -> bool:
        """Check if Claude is available and configured."""
        return self.client is not None

    def _build_system_prompt(self) -> str:
        """Build the system prompt for Claude."""
        return """You are an AI assistant for a County Engineer's Office Capital Projects Lifecycle Planner.
You help county staff understand the status, health, and priorities of their road and transportation capital improvement projects.

Your role is to:
1. Answer questions about project portfolio status clearly and concisely
2. Identify projects that are doing well and explain WHY (good scores, on schedule, on budget)
3. Identify projects at risk and explain the specific issues (schedule delays, budget overruns, deliverability concerns)
4. Provide actionable recommendations when asked
5. Help users understand the data with plain language explanations

When discussing projects:
- Always mention specific project names when relevant
- Explain scores in context (e.g., "Health score of 45 is below the 60 threshold, indicating concerns")
- Be specific about issues (e.g., "behind schedule due to ROW acquisition delays" not just "has issues")
- Suggest follow-up questions the user might want to ask

Keep responses conversational but professional - this is for county government staff.
Use bullet points for lists of projects or key findings.
Be concise but thorough."""

    def _build_data_context(self, df: pd.DataFrame) -> str:
        """Build context about the portfolio data for Claude."""
        # Portfolio summary
        total_projects = len(df)
        total_budget = df['Total Budget'].sum()
        avg_health = df['Project Health Score'].mean() if 'Project Health Score' in df.columns else 0

        # Status distribution
        status_counts = df['Status'].value_counts().to_dict() if 'Status' in df.columns else {}

        # Phase distribution
        phase_counts = df['Current Phase'].value_counts().to_dict() if 'Current Phase' in df.columns else {}

        # At-risk projects
        at_risk = df[df['Project Health Score'] < 50] if 'Project Health Score' in df.columns else pd.DataFrame()

        # Top projects by budget
        top_budget = df.nlargest(5, 'Total Budget')[['Project Name', 'Total Budget', 'Project Health Score', 'Status', 'Current Phase']].to_dict('records')

        # Projects with issues
        schedule_issues = df[df['Schedule Health'] < 50] if 'Schedule Health' in df.columns else pd.DataFrame()
        budget_issues = df[df['Budget Health'] < 50] if 'Budget Health' in df.columns else pd.DataFrame()

        context = f"""
PORTFOLIO SUMMARY:
- Total Projects: {total_projects}
- Total Program Value: ${total_budget:,.0f}
- Average Health Score: {avg_health:.1f}/100 (60+ is healthy, <50 is at risk)

STATUS DISTRIBUTION:
{json.dumps(status_counts, indent=2)}

Status definitions:
- Advance: High value + ready to execute - accelerate these
- Monitor: Proceed with oversight
- Re-scope: High value but issues - needs adjustment before proceeding
- Defer: Lower priority or not ready - push to future
- Cancel: Should be terminated

PHASE DISTRIBUTION:
{json.dumps(phase_counts, indent=2)}

TOP 5 PROJECTS BY BUDGET:
{json.dumps(top_budget, indent=2)}

PROJECTS AT RISK (Health < 50): {len(at_risk)}
"""

        if len(at_risk) > 0:
            at_risk_summary = at_risk[['Project Name', 'Project Health Score', 'Schedule Health', 'Budget Health', 'Status']].head(5).to_dict('records')
            context += f"At-risk project details:\n{json.dumps(at_risk_summary, indent=2)}\n"

        context += f"""
SCHEDULE ISSUES (Schedule Health < 50): {len(schedule_issues)} projects
BUDGET ISSUES (Budget Health < 50): {len(budget_issues)} projects

FULL PROJECT LIST (abbreviated):
"""
        # Add abbreviated project list
        project_summary = df[['Project Name', 'Project ID', 'Status', 'Current Phase',
                             'Project Health Score', 'Total Budget', 'Percent Complete']].head(20).to_dict('records')
        context += json.dumps(project_summary, indent=2)

        return context

    def _extract_relevant_projects(self, df: pd.DataFrame, query: str, response_text: str) -> List[Dict]:
        """Extract projects relevant to the query and response."""
        query_lower = query.lower()

        # Determine filter based on query
        if 'risk' in query_lower or 'concern' in query_lower or 'issue' in query_lower or 'problem' in query_lower:
            filtered = df[df['Project Health Score'] < 50].nsmallest(5, 'Project Health Score')
        elif 'well' in query_lower or 'good' in query_lower or 'healthy' in query_lower or 'best' in query_lower:
            filtered = df[df['Project Health Score'] >= 60].nlargest(5, 'Project Health Score')
        elif 'budget' in query_lower and ('over' in query_lower or 'issue' in query_lower):
            filtered = df[df['Budget Health'] < 50].nsmallest(5, 'Budget Health')
        elif 'schedule' in query_lower or 'delay' in query_lower or 'late' in query_lower:
            filtered = df[df['Schedule Health'] < 50].nsmallest(5, 'Schedule Health')
        elif 'advance' in query_lower:
            filtered = df[df['Status'] == 'Advance']
        elif 'monitor' in query_lower:
            filtered = df[df['Status'] == 'Monitor']
        elif 'rescope' in query_lower or 're-scope' in query_lower:
            filtered = df[df['Status'] == 'Re-scope']
        elif 'defer' in query_lower:
            filtered = df[df['Status'] == 'Defer']
        elif 'district' in query_lower:
            # Try to extract district number
            import re
            match = re.search(r'district\s*(\d+)', query_lower)
            if match:
                district = int(match.group(1))
                filtered = df[df['District'] == district]
            else:
                filtered = df.head(5)
        elif 'construction' in query_lower:
            filtered = df[df['Current Phase'] == 'Active Construction']
        elif 'design' in query_lower:
            filtered = df[df['Current Phase'] == 'Design']
        else:
            # Default to top projects by budget
            filtered = df.nlargest(5, 'Total Budget')

        return filtered.head(10).to_dict('records')

    def _determine_filter_params(self, query: str) -> Dict:
        """Determine filter parameters based on the query."""
        query_lower = query.lower()
        params = {}

        if 'risk' in query_lower or 'concern' in query_lower:
            params['max_health'] = 50
        elif 'well' in query_lower or 'good' in query_lower or 'healthy' in query_lower:
            params['min_health'] = 60
        elif 'advance' in query_lower:
            params['status'] = 'Advance'
        elif 'monitor' in query_lower:
            params['status'] = 'Monitor'
        elif 'rescope' in query_lower or 're-scope' in query_lower:
            params['status'] = 'Re-scope'
        elif 'defer' in query_lower:
            params['status'] = 'Defer'

        # District filter
        import re
        match = re.search(r'district\s*(\d+)', query_lower)
        if match:
            params['district'] = match.group(1)

        return params

    def process_query(self, query: str, df: pd.DataFrame) -> ClaudeResponse:
        """
        Process a natural language query using Claude.

        Args:
            query: User's question
            df: DataFrame with scored and categorized projects

        Returns:
            ClaudeResponse with message, projects, and insights
        """
        if not self.is_available():
            # Fallback response if Claude is not available
            return ClaudeResponse(
                message="Claude AI is not configured. Please set your ANTHROPIC_API_KEY environment variable or check your API key.",
                projects=[],
                key_points=["Claude integration requires an Anthropic API key"],
                follow_up_prompt=None,
                filter_params={},
                show_details_prompt=False
            )

        try:
            # Build context
            data_context = self._build_data_context(df)

            # Create the message for Claude
            user_message = f"""Based on the following capital projects portfolio data, please answer this question:

QUESTION: {query}

{data_context}

Please provide a helpful, specific answer. If discussing specific projects, mention them by name.
Include 2-4 key bullet points summarizing your findings.
End with a suggested follow-up question the user might want to ask."""

            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=self._build_system_prompt(),
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            # Extract response text
            response_text = response.content[0].text

            # Parse the response to extract key points
            key_points = self._extract_key_points(response_text)

            # Extract follow-up prompt if present
            follow_up = self._extract_follow_up(response_text)

            # Get relevant projects
            projects = self._extract_relevant_projects(df, query, response_text)

            # Determine filter params
            filter_params = self._determine_filter_params(query)

            return ClaudeResponse(
                message=response_text,
                projects=projects,
                key_points=key_points,
                follow_up_prompt=follow_up,
                filter_params=filter_params,
                show_details_prompt=len(projects) > 0
            )

        except anthropic.APIConnectionError as e:
            logger.error(f"Claude API connection error: {e}")
            return ClaudeResponse(
                message="I'm having trouble connecting to the AI service. Please check your internet connection and try again.",
                projects=[],
                key_points=[],
                follow_up_prompt=None,
                filter_params={},
                show_details_prompt=False
            )
        except anthropic.RateLimitError as e:
            logger.error(f"Claude API rate limit: {e}")
            return ClaudeResponse(
                message="The AI service is currently busy. Please wait a moment and try again.",
                projects=[],
                key_points=[],
                follow_up_prompt=None,
                filter_params={},
                show_details_prompt=False
            )
        except anthropic.APIStatusError as e:
            logger.error(f"Claude API error: {e}")
            return ClaudeResponse(
                message=f"There was an error with the AI service: {str(e)}",
                projects=[],
                key_points=[],
                follow_up_prompt=None,
                filter_params={},
                show_details_prompt=False
            )
        except Exception as e:
            logger.error(f"Unexpected error in Claude assistant: {e}")
            import traceback
            traceback.print_exc()
            return ClaudeResponse(
                message=f"I encountered an unexpected error: {str(e)}. Please try rephrasing your question.",
                projects=[],
                key_points=[],
                follow_up_prompt=None,
                filter_params={},
                show_details_prompt=False
            )

    def _extract_key_points(self, text: str) -> List[str]:
        """Extract bullet points from the response."""
        import re

        # Look for lines starting with - or * or •
        bullet_pattern = r'^[\-\*•]\s*(.+)$'
        bullets = re.findall(bullet_pattern, text, re.MULTILINE)

        # Also look for numbered points
        numbered_pattern = r'^\d+[\.\)]\s*(.+)$'
        numbered = re.findall(numbered_pattern, text, re.MULTILINE)

        all_points = bullets + numbered

        # If no bullets found, try to extract key sentences
        if not all_points:
            sentences = text.split('.')
            # Get first few meaningful sentences
            all_points = [s.strip() for s in sentences[:3] if len(s.strip()) > 20]

        return all_points[:5]  # Limit to 5 points

    def _extract_follow_up(self, text: str) -> Optional[str]:
        """Extract suggested follow-up question from the response."""
        import re

        # Look for common follow-up patterns
        patterns = [
            r'(?:you might|you may|you could|consider asking|follow-up)[:\s]+["\']?([^"\'\.]+\?)["\']?',
            r'(?:would you like|do you want|shall I)[^?]*\?',
            r'([^.]*\?)\s*$'  # Last question in text
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip() if match.lastindex else match.group(0).strip()

        return "Would you like more details on any specific project?"
