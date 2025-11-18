"""
AI Chat Assistant for Natural Language Portfolio Queries
Simple pattern-matching based query handler for portfolio data
"""

import pandas as pd
from typing import Dict, List, Any


class AIChatAssistant:
    """
    Natural language chat assistant for portfolio queries.
    Uses simple pattern matching to understand user intent.
    """

    def __init__(self):
        """Initialize with query patterns for intent detection"""
        self.query_patterns = {
            'high_cost': ['expensive', 'high cost', 'costly', 'high-cost', 'spending'],
            'low_health': ['poor health', 'low health', 'unhealthy', 'failing', 'technical debt'],
            'retire': ['retire', 'eliminate', 'decommission', 'sunset', 'remove'],
            'invest': ['invest', 'strategic', 'high value', 'priority'],
            'total_cost': ['total cost', 'sum', 'all costs', 'budget', 'spending total'],
            'list_all': ['show all', 'list all', 'show me all', 'list apps'],
            'migrate': ['migrate', 'cloud', 'modernize'],
            'consolidate': ['consolidate', 'merge', 'combine'],
            'low_value': ['low value', 'poor value', 'low business value'],
            'count': ['how many', 'count', 'number of']
        }

    def parse_query(self, message: str) -> str:
        """
        Detect query intent from natural language message

        Args:
            message: User's natural language query

        Returns:
            Detected intent string
        """
        message_lower = message.lower()

        # Check each pattern
        for intent, keywords in self.query_patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent

        return 'general'

    def process_chat(self, message: str, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Main method - process user query and return response

        Args:
            message: User's natural language query
            df: Portfolio DataFrame

        Returns:
            Dictionary with response and data
        """
        if df is None or df.empty:
            return {
                'response': 'No portfolio data is currently loaded. Please upload data first.',
                'data': []
            }

        intent = self.parse_query(message)

        # Process based on intent
        if intent == 'high_cost':
            # Find high-cost applications (above average)
            avg_cost = df['Cost'].mean()
            results = df[df['Cost'] > avg_cost].sort_values('Cost', ascending=False).head(10)
            response = f"Found {len(results)} high-cost applications (above ${avg_cost:,.0f} average):"

        elif intent == 'low_health':
            # Find applications with poor technical health
            results = df[df['Tech Health'] < 50].sort_values('Tech Health').head(10)
            response = f"Found {len(results)} applications with poor technical health (<50/100):"

        elif intent == 'retire':
            # Find retirement candidates
            if 'Action Recommendation' in df.columns:
                results = df[df['Action Recommendation'].str.contains('Retire|Eliminate', case=False, na=False, regex=True)].head(10)
                response = f"Found {len(results)} retirement candidates:"
            else:
                return {
                    'response': 'Recommendation data not available.',
                    'data': []
                }

        elif intent == 'invest':
            # Find strategic investment opportunities
            if 'Action Recommendation' in df.columns:
                results = df[(df['Business Value'] > 70) &
                           (df['Action Recommendation'].str.contains('Invest', case=False, na=False))].head(10)
                response = f"Found {len(results)} strategic investment opportunities (high business value + invest recommendation):"
            else:
                results = df[df['Business Value'] > 70].head(10)
                response = f"Found {len(results)} high business value applications (>70/100):"

        elif intent == 'migrate':
            # Find migration candidates
            if 'Action Recommendation' in df.columns:
                results = df[df['Action Recommendation'].str.contains('Migrate', case=False, na=False)].head(10)
                response = f"Found {len(results)} cloud migration candidates:"
            else:
                return {
                    'response': 'Recommendation data not available.',
                    'data': []
                }

        elif intent == 'consolidate':
            # Find consolidation candidates
            if 'Action Recommendation' in df.columns:
                results = df[df['Action Recommendation'].str.contains('Consolidate', case=False, na=False)].head(10)
                response = f"Found {len(results)} consolidation candidates:"
            else:
                return {
                    'response': 'Recommendation data not available.',
                    'data': []
                }

        elif intent == 'low_value':
            # Find low business value applications
            results = df[df['Business Value'] < 40].sort_values('Business Value').head(10)
            response = f"Found {len(results)} low business value applications (<40/100):"

        elif intent == 'total_cost':
            # Calculate total portfolio cost
            total = df['Cost'].sum()
            avg = df['Cost'].mean()
            return {
                'response': f"💰 Total portfolio cost: ${total:,.0f}/year across {len(df)} applications. Average cost per app: ${avg:,.0f}/year.",
                'data': []
            }

        elif intent == 'count':
            # Count applications
            total = len(df)
            if 'Action Recommendation' in df.columns:
                breakdown = df['Action Recommendation'].value_counts().to_dict()
                breakdown_str = ', '.join([f"{count} {action}" for action, count in breakdown.items()])
                return {
                    'response': f"📊 You have {total} applications in your portfolio. Breakdown: {breakdown_str}",
                    'data': []
                }
            else:
                return {
                    'response': f"📊 You have {total} applications in your portfolio.",
                    'data': []
                }

        elif intent == 'list_all':
            # List all applications
            results = df.head(20)  # Limit to 20 for display
            response = f"Showing first {len(results)} applications (of {len(df)} total):"

        else:
            # General/unknown intent - provide help
            return {
                'response': """I can help you query your portfolio! Try asking:

• "Show me high-cost applications"
• "Which apps have poor technical health?"
• "List retirement candidates"
• "Show investment opportunities"
• "What's the total cost?"
• "How many applications do I have?"
• "Show migration candidates"
• "List consolidation opportunities"

What would you like to know?""",
                'data': []
            }

        # Prepare results data
        if len(results) > 0:
            # Select relevant columns for display
            display_cols = ['Application Name', 'Cost', 'Tech Health', 'Business Value']
            if 'Action Recommendation' in df.columns:
                display_cols.append('Action Recommendation')
            if 'Composite Score' in df.columns:
                display_cols.append('Composite Score')

            # Filter to only existing columns
            available_cols = [col for col in display_cols if col in results.columns]

            data_list = results[available_cols].to_dict('records')
        else:
            data_list = []
            response = "No applications found matching your criteria."

        return {
            'response': response,
            'data': data_list
        }
