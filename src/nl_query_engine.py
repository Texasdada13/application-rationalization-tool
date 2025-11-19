"""
Natural Language Query Engine
Allow users to query portfolio data using natural language
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import re


class NaturalLanguageQueryEngine:
    """Process natural language queries about application portfolio"""

    # Query patterns and their handlers
    QUERY_PATTERNS = {
        'count': {
            'patterns': [
                r'how many (applications?|apps?)',
                r'count (of )?(applications?|apps?)',
                r'number of (applications?|apps?)',
                r'total (applications?|apps?)'
            ],
            'handler': 'handle_count_query'
        },
        'cost': {
            'patterns': [
                r'(what is|how much|show|list|tell me|get).*(total )?(cost|spend|budget|expense)',
                r'(cost|spend|budget|expense).*(total|sum|aggregate)',
                r'most expensive',
                r'highest cost'
            ],
            'handler': 'handle_cost_query'
        },
        'health': {
            'patterns': [
                r'(health|technical health|tech health)',
                r'unhealthy',
                r'(low|poor|critical|bad) health',
                r'health (score|rating)'
            ],
            'handler': 'handle_health_query'
        },
        'value': {
            'patterns': [
                r'business value',
                r'high value',
                r'low value',
                r'value score',
                r'critical (application|app)',
                r'mission.critical'
            ],
            'handler': 'handle_value_query'
        },
        'retire': {
            'patterns': [
                r'(retire|decommission|sunset|eliminate|remove)',
                r'retirement candidate',
                r'should (we )?retire',
                r'can (we )?retire'
            ],
            'handler': 'handle_retire_query'
        },
        'modernize': {
            'patterns': [
                r'(modernize|upgrade|update|refresh)',
                r'modernization',
                r'need.*(moderniz|upgrad|updat)',
                r'should (we )?modernize'
            ],
            'handler': 'handle_modernize_query'
        },
        'risk': {
            'patterns': [
                r'(risk|risky|high.risk)',
                r'risk score',
                r'at risk',
                r'dangerous'
            ],
            'handler': 'handle_risk_query'
        },
        'savings': {
            'patterns': [
                r'sav(e|ings?)',
                r'(cost )?reduction',
                r'optimize cost',
                r'cut cost',
                r'save money'
            ],
            'handler': 'handle_savings_query'
        },
        'category': {
            'patterns': [
                r'(in|by|for|from) (the )?(category|categor)',
                r'category.*?([A-Z]\w+)',
                r'type of application'
            ],
            'handler': 'handle_category_query'
        },
        'comparison': {
            'patterns': [
                r'compar(e|ison)',
                r'(vs|versus|compared to)',
                r'difference between',
                r'which is (better|worse)'
            ],
            'handler': 'handle_comparison_query'
        },
        'recommendation': {
            'patterns': [
                r'recommend',
                r'(what )?should (i|we)',
                r'suggest',
                r'advice',
                r'next step'
            ],
            'handler': 'handle_recommendation_query'
        },
        'trend': {
            'patterns': [
                r'trend',
                r'over time',
                r'history',
                r'chang(e|ing)',
                r'evolution'
            ],
            'handler': 'handle_trend_query'
        }
    }

    def __init__(self, df_applications: pd.DataFrame):
        """Initialize with application portfolio data"""
        self.df = df_applications.copy()

    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a natural language query"""

        query_lower = query.lower().strip()

        # Match query to pattern
        matched_type = None
        for query_type, config in self.QUERY_PATTERNS.items():
            for pattern in config['patterns']:
                if re.search(pattern, query_lower):
                    matched_type = query_type
                    break
            if matched_type:
                break

        if not matched_type:
            return self.handle_unknown_query(query)

        # Call appropriate handler
        handler_name = self.QUERY_PATTERNS[matched_type]['handler']
        handler = getattr(self, handler_name)
        return handler(query_lower)

    def handle_count_query(self, query: str) -> Dict[str, Any]:
        """Handle count-related queries"""

        # Check for filters
        if 'unhealthy' in query or 'poor health' in query:
            count = len(self.df[self.df['Tech Health'] <= 5])
            return {
                'query_type': 'count',
                'answer': f'{count} applications',
                'details': f'There are {count} unhealthy applications (health score ≤ 5)',
                'data': {
                    'count': count,
                    'filter': 'unhealthy'
                }
            }
        elif 'high value' in query or 'critical' in query:
            count = len(self.df[self.df['Business Value'] >= 7])
            return {
                'query_type': 'count',
                'answer': f'{count} applications',
                'details': f'There are {count} high-value applications (business value ≥ 7)',
                'data': {
                    'count': count,
                    'filter': 'high_value'
                }
            }
        else:
            count = len(self.df)
            return {
                'query_type': 'count',
                'answer': f'{count} applications',
                'details': f'The portfolio contains {count} applications in total',
                'data': {
                    'count': count,
                    'filter': 'all'
                }
            }

    def handle_cost_query(self, query: str) -> Dict[str, Any]:
        """Handle cost-related queries"""

        if 'most expensive' in query or 'highest cost' in query:
            top_5 = self.df.nlargest(5, 'Cost')[['Application Name', 'Cost']]
            return {
                'query_type': 'cost',
                'answer': f'${top_5.iloc[0]["Cost"]:,.0f} per year',
                'details': f'Most expensive: {top_5.iloc[0]["Application Name"]} at ${top_5.iloc[0]["Cost"]:,.0f}/year',
                'data': {
                    'top_expensive': top_5.to_dict('records')
                }
            }
        else:
            total = self.df['Cost'].sum()
            avg = self.df['Cost'].mean()
            return {
                'query_type': 'cost',
                'answer': f'${total:,.0f} per year',
                'details': f'Total annual cost: ${total:,.0f} (Average: ${avg:,.0f} per application)',
                'data': {
                    'total_cost': total,
                    'avg_cost': avg,
                    'app_count': len(self.df)
                }
            }

    def handle_health_query(self, query: str) -> Dict[str, Any]:
        """Handle health-related queries"""

        if 'unhealthy' in query or 'poor' in query or 'critical' in query:
            unhealthy = self.df[self.df['Tech Health'] <= 3]
            return {
                'query_type': 'health',
                'answer': f'{len(unhealthy)} critical applications',
                'details': f'{len(unhealthy)} applications have critical health (score ≤ 3)',
                'data': {
                    'critical_apps': unhealthy[['Application Name', 'Tech Health', 'Business Value', 'Cost']].to_dict('records'),
                    'count': len(unhealthy),
                    'total_cost_at_risk': unhealthy['Cost'].sum()
                }
            }
        else:
            avg_health = self.df['Tech Health'].mean()
            distribution = {
                'Excellent (10)': len(self.df[self.df['Tech Health'] == 10]),
                'Good (8-9)': len(self.df[(self.df['Tech Health'] >= 8) & (self.df['Tech Health'] < 10)]),
                'Fair (6-7)': len(self.df[(self.df['Tech Health'] >= 6) & (self.df['Tech Health'] < 8)]),
                'Poor (4-5)': len(self.df[(self.df['Tech Health'] >= 4) & (self.df['Tech Health'] < 6)]),
                'Critical (1-3)': len(self.df[self.df['Tech Health'] < 4])
            }
            return {
                'query_type': 'health',
                'answer': f'Average health: {avg_health:.1f}/10',
                'details': f'Portfolio average health score is {avg_health:.1f} out of 10',
                'data': {
                    'avg_health': avg_health,
                    'distribution': distribution
                }
            }

    def handle_value_query(self, query: str) -> Dict[str, Any]:
        """Handle business value queries"""

        if 'high value' in query or 'critical' in query or 'mission' in query:
            high_value = self.df[self.df['Business Value'] >= 8]
            return {
                'query_type': 'value',
                'answer': f'{len(high_value)} mission-critical applications',
                'details': f'{len(high_value)} applications are mission-critical (value ≥ 8)',
                'data': {
                    'critical_apps': high_value[['Application Name', 'Business Value', 'Tech Health', 'Cost']].to_dict('records'),
                    'count': len(high_value)
                }
            }
        elif 'low value' in query:
            low_value = self.df[self.df['Business Value'] <= 4]
            return {
                'query_type': 'value',
                'answer': f'{len(low_value)} low-value applications',
                'details': f'{len(low_value)} applications have low business value (≤ 4)',
                'data': {
                    'low_value_apps': low_value[['Application Name', 'Business Value', 'Tech Health', 'Cost']].to_dict('records'),
                    'count': len(low_value)
                }
            }
        else:
            avg_value = self.df['Business Value'].mean()
            return {
                'query_type': 'value',
                'answer': f'Average value: {avg_value:.1f}/10',
                'details': f'Portfolio average business value is {avg_value:.1f} out of 10',
                'data': {
                    'avg_value': avg_value
                }
            }

    def handle_retire_query(self, query: str) -> Dict[str, Any]:
        """Handle retirement candidate queries"""

        # Low health + Low value = retire
        retire_candidates = self.df[(self.df['Tech Health'] <= 3) & (self.df['Business Value'] <= 4)]

        total_savings = retire_candidates['Cost'].sum()

        return {
            'query_type': 'retire',
            'answer': f'{len(retire_candidates)} retirement candidates',
            'details': f'{len(retire_candidates)} applications are candidates for retirement (low health & low value)',
            'data': {
                'candidates': retire_candidates[['Application Name', 'Tech Health', 'Business Value', 'Cost']].to_dict('records'),
                'count': len(retire_candidates),
                'potential_savings': total_savings,
                'savings_percentage': (total_savings / self.df['Cost'].sum() * 100) if len(self.df) > 0 else 0
            }
        }

    def handle_modernize_query(self, query: str) -> Dict[str, Any]:
        """Handle modernization queries"""

        # High value + Low health = modernize
        modernize_candidates = self.df[(self.df['Business Value'] >= 7) & (self.df['Tech Health'] <= 5)]

        return {
            'query_type': 'modernize',
            'answer': f'{len(modernize_candidates)} modernization priorities',
            'details': f'{len(modernize_candidates)} high-value applications need modernization (value ≥ 7, health ≤ 5)',
            'data': {
                'candidates': modernize_candidates[['Application Name', 'Tech Health', 'Business Value', 'Cost']].to_dict('records'),
                'count': len(modernize_candidates),
                'total_cost_at_risk': modernize_candidates['Cost'].sum()
            }
        }

    def handle_risk_query(self, query: str) -> Dict[str, Any]:
        """Handle risk-related queries"""

        # High risk: Low health + High value
        high_risk = self.df[(self.df['Tech Health'] <= 5) & (self.df['Business Value'] >= 7)]

        # Calculate risk score (simple)
        def calc_risk(row):
            return ((10 - row['Tech Health']) * 0.4 + row['Business Value'] * 0.6) * 10

        high_risk = high_risk.copy()
        high_risk['risk_score'] = high_risk.apply(calc_risk, axis=1)
        high_risk = high_risk.sort_values('risk_score', ascending=False)

        return {
            'query_type': 'risk',
            'answer': f'{len(high_risk)} high-risk applications',
            'details': f'{len(high_risk)} applications are high-risk (critical but unhealthy)',
            'data': {
                'high_risk_apps': high_risk[['Application Name', 'Tech Health', 'Business Value', 'Cost', 'risk_score']].head(10).to_dict('records'),
                'count': len(high_risk),
                'total_cost': high_risk['Cost'].sum()
            }
        }

    def handle_savings_query(self, query: str) -> Dict[str, Any]:
        """Handle cost savings queries"""

        # Calculate savings opportunities
        retire_candidates = self.df[(self.df['Tech Health'] <= 3) & (self.df['Business Value'] <= 4)]
        retire_savings = retire_candidates['Cost'].sum()

        # Consolidation opportunities (apps with similar functionality)
        consolidation_savings = self.df['Cost'].sum() * 0.10  # Estimate 10% from consolidation

        # Modernization savings (maintenance reduction)
        modernize_candidates = self.df[(self.df['Business Value'] >= 7) & (self.df['Tech Health'] <= 5)]
        modernization_savings = modernize_candidates['Cost'].sum() * 0.20  # 20% maintenance reduction

        total_savings = retire_savings + consolidation_savings + modernization_savings

        return {
            'query_type': 'savings',
            'answer': f'${total_savings:,.0f} annual savings potential',
            'details': f'Total potential savings: ${total_savings:,.0f} per year across multiple initiatives',
            'data': {
                'retirement_savings': retire_savings,
                'consolidation_savings': consolidation_savings,
                'modernization_savings': modernization_savings,
                'total_savings': total_savings,
                'savings_percentage': (total_savings / self.df['Cost'].sum() * 100) if len(self.df) > 0 else 0,
                'breakdown': [
                    {'category': 'Retirement', 'amount': retire_savings, 'apps': len(retire_candidates)},
                    {'category': 'Consolidation', 'amount': consolidation_savings, 'apps': 'Various'},
                    {'category': 'Modernization', 'amount': modernization_savings, 'apps': len(modernize_candidates)}
                ]
            }
        }

    def handle_category_query(self, query: str) -> Dict[str, Any]:
        """Handle category-specific queries"""

        # Try to extract category name from query
        category = None
        categories = self.df['Category'].unique()

        for cat in categories:
            if cat.lower() in query:
                category = cat
                break

        if category:
            cat_apps = self.df[self.df['Category'] == category]
            return {
                'query_type': 'category',
                'answer': f'{len(cat_apps)} applications in {category}',
                'details': f'Category: {category} - {len(cat_apps)} applications, ${cat_apps["Cost"].sum():,.0f} annual cost',
                'data': {
                    'category': category,
                    'count': len(cat_apps),
                    'total_cost': cat_apps['Cost'].sum(),
                    'avg_health': cat_apps['Tech Health'].mean(),
                    'avg_value': cat_apps['Business Value'].mean(),
                    'applications': cat_apps[['Application Name', 'Tech Health', 'Business Value', 'Cost']].to_dict('records')
                }
            }
        else:
            # Return category summary
            cat_summary = self.df.groupby('Category').agg({
                'Application Name': 'count',
                'Cost': 'sum',
                'Tech Health': 'mean',
                'Business Value': 'mean'
            }).round(2).to_dict('index')

            return {
                'query_type': 'category',
                'answer': f'{len(categories)} categories',
                'details': f'Portfolio has {len(categories)} application categories',
                'data': {
                    'categories': cat_summary
                }
            }

    def handle_comparison_query(self, query: str) -> Dict[str, Any]:
        """Handle comparison queries"""

        # Simple comparison: best vs worst
        best_health = self.df.nlargest(5, 'Tech Health')[['Application Name', 'Tech Health', 'Business Value', 'Cost']]
        worst_health = self.df.nsmallest(5, 'Tech Health')[['Application Name', 'Tech Health', 'Business Value', 'Cost']]

        return {
            'query_type': 'comparison',
            'answer': 'Comparison available',
            'details': 'Showing best vs worst health applications',
            'data': {
                'best_health': best_health.to_dict('records'),
                'worst_health': worst_health.to_dict('records'),
                'health_gap': best_health['Tech Health'].mean() - worst_health['Tech Health'].mean()
            }
        }

    def handle_recommendation_query(self, query: str) -> Dict[str, Any]:
        """Handle recommendation requests"""

        recommendations = []

        # Retirement recommendations
        retire = self.df[(self.df['Tech Health'] <= 3) & (self.df['Business Value'] <= 4)]
        if len(retire) > 0:
            recommendations.append({
                'priority': 'High',
                'action': 'Retire',
                'count': len(retire),
                'reason': 'Low health and low business value',
                'savings': retire['Cost'].sum()
            })

        # Modernization recommendations
        modernize = self.df[(self.df['Business Value'] >= 7) & (self.df['Tech Health'] <= 5)]
        if len(modernize) > 0:
            recommendations.append({
                'priority': 'Urgent',
                'action': 'Modernize',
                'count': len(modernize),
                'reason': 'Critical applications with poor health',
                'risk_mitigation': 'Prevent business disruption'
            })

        # Investment recommendations
        invest = self.df[(self.df['Business Value'] >= 7) & (self.df['Tech Health'] >= 7)]
        if len(invest) > 0:
            recommendations.append({
                'priority': 'Medium',
                'action': 'Invest',
                'count': len(invest),
                'reason': 'High-value applications in good health',
                'opportunity': 'Continue innovation'
            })

        return {
            'query_type': 'recommendation',
            'answer': f'{len(recommendations)} recommendations',
            'details': f'Generated {len(recommendations)} portfolio recommendations based on TIME framework',
            'data': {
                'recommendations': recommendations
            }
        }

    def handle_trend_query(self, query: str) -> Dict[str, Any]:
        """Handle trend/historical queries"""

        return {
            'query_type': 'trend',
            'answer': 'Historical data available',
            'details': 'Use the History & Trends page to view portfolio evolution over time',
            'data': {
                'message': 'Historical tracking requires snapshot data. Visit /history to view trends.'
            }
        }

    def handle_unknown_query(self, query: str) -> Dict[str, Any]:
        """Handle unrecognized queries"""

        # Provide helpful suggestions
        suggestions = [
            'How many applications do we have?',
            'What is the total cost?',
            'Show unhealthy applications',
            'Which apps should we retire?',
            'What are the highest risk applications?',
            'How much can we save?',
            'Show applications by category',
            'What do you recommend?'
        ]

        return {
            'query_type': 'unknown',
            'answer': 'Query not recognized',
            'details': f'Could not understand query: "{query}"',
            'data': {
                'suggestions': suggestions,
                'query': query
            }
        }

    def get_example_queries(self) -> List[str]:
        """Get list of example queries"""

        return [
            'How many applications do we have?',
            'What is the total annual cost?',
            'Show me unhealthy applications',
            'Which applications should we retire?',
            'What apps need modernization?',
            'Show highest risk applications',
            'How much can we save?',
            'What is the average health score?',
            'Show applications in the Financial category',
            'What do you recommend?',
            'Which are the most expensive apps?',
            'Show high-value applications',
            'Compare best and worst applications'
        ]
