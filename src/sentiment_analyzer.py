"""
Sentiment Analysis Engine
Analyzes stakeholder survey comments using pattern matching and keyword analysis
"""

import re
from collections import Counter
from typing import Dict, List, Any, Union
import pandas as pd


class SentimentAnalyzer:
    """Pattern-based sentiment analyzer for stakeholder feedback"""

    def __init__(self):
        # Sentiment keyword dictionaries
        self.positive_keywords = [
            'excellent', 'great', 'good', 'love', 'amazing', 'best', 'happy',
            'satisfied', 'helpful', 'useful', 'reliable', 'efficient', 'fast',
            'easy', 'intuitive', 'powerful', 'fantastic', 'perfect', 'outstanding',
            'impressed', 'valuable', 'beneficial', 'essential', 'wonderful',
            'appreciate', 'like', 'well', 'strong', 'solid', 'quality'
        ]

        self.negative_keywords = [
            'bad', 'poor', 'terrible', 'awful', 'hate', 'worst', 'horrible',
            'frustrated', 'disappointed', 'slow', 'broken', 'buggy', 'unreliable',
            'difficult', 'confusing', 'outdated', 'useless', 'waste', 'nightmare',
            'annoying', 'complicated', 'clunky', 'inefficient', 'problematic',
            'concern', 'issue', 'problem', 'fail', 'lacks', 'missing'
        ]

        # Common themes/topics
        self.theme_keywords = {
            'performance': ['slow', 'fast', 'speed', 'performance', 'lag', 'responsive', 'quick'],
            'usability': ['easy', 'difficult', 'intuitive', 'confusing', 'user-friendly', 'complicated', 'interface'],
            'reliability': ['reliable', 'unreliable', 'stable', 'crash', 'downtime', 'broken', 'buggy'],
            'features': ['feature', 'functionality', 'capability', 'missing', 'lacks', 'needs', 'want'],
            'cost': ['expensive', 'cheap', 'costly', 'value', 'price', 'budget', 'afford'],
            'support': ['support', 'help', 'documentation', 'training', 'assistance', 'service']
        }

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of a single comment

        Args:
            text: Comment text to analyze

        Returns:
            Dictionary with sentiment analysis results
        """
        if pd.isna(text) or text == '':
            return {
                'sentiment': 'NEUTRAL',
                'score': 0,
                'confidence': 0,
                'positive_keywords': 0,
                'negative_keywords': 0
            }

        text_lower = str(text).lower()

        # Count positive and negative keywords
        positive_count = sum(1 for keyword in self.positive_keywords if keyword in text_lower)
        negative_count = sum(1 for keyword in self.negative_keywords if keyword in text_lower)

        # Calculate sentiment score (-1 to +1)
        total = positive_count + negative_count
        if total == 0:
            return {
                'sentiment': 'NEUTRAL',
                'score': 0,
                'confidence': 0,
                'positive_keywords': 0,
                'negative_keywords': 0
            }

        score = (positive_count - negative_count) / total
        confidence = min(total / 5, 1.0)  # Max confidence at 5+ keywords

        # Determine sentiment label
        if score > 0.3:
            sentiment = 'POSITIVE'
        elif score < -0.3:
            sentiment = 'NEGATIVE'
        else:
            sentiment = 'NEUTRAL'

        return {
            'sentiment': sentiment,
            'score': round(score, 2),
            'confidence': round(confidence, 2),
            'positive_keywords': positive_count,
            'negative_keywords': negative_count
        }

    def extract_themes(self, text: str) -> List[str]:
        """
        Extract main themes/topics from comment

        Args:
            text: Comment text to analyze

        Returns:
            List of identified themes
        """
        if pd.isna(text) or text == '':
            return []

        text_lower = str(text).lower()
        found_themes = []

        for theme, keywords in self.theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                found_themes.append(theme)

        return found_themes

    def analyze_survey_comments(self, comments_data: Union[pd.DataFrame, List[str]]) -> Dict[str, Any]:
        """
        Analyze all survey comments

        Args:
            comments_data: DataFrame with 'comments' column or list of comment strings

        Returns:
            Dictionary with comprehensive analysis results
        """
        if isinstance(comments_data, pd.DataFrame):
            # Assume there's a 'comments' column
            if 'comments' in comments_data.columns:
                comments_list = comments_data['comments'].dropna().tolist()
            else:
                # Try first column
                comments_list = comments_data.iloc[:, 0].dropna().tolist()
        else:
            comments_list = [c for c in comments_data if pd.notna(c) and str(c).strip() != '']

        if len(comments_list) == 0:
            return {
                'summary': {
                    'total': 0,
                    'positive': 0,
                    'negative': 0,
                    'neutral': 0,
                    'positive_pct': 0,
                    'negative_pct': 0,
                    'neutral_pct': 0
                },
                'themes': {},
                'detailed_analysis': [],
                'top_positive': [],
                'top_negative': []
            }

        # Analyze each comment
        results = []
        all_themes = []

        for comment in comments_list:
            sentiment = self.analyze_sentiment(comment)
            themes = self.extract_themes(comment)

            results.append({
                'comment': str(comment)[:100] + '...' if len(str(comment)) > 100 else str(comment),
                'full_comment': str(comment),
                'sentiment': sentiment['sentiment'],
                'score': sentiment['score'],
                'confidence': sentiment['confidence'],
                'themes': themes
            })

            all_themes.extend(themes)

        # Calculate summary statistics
        sentiment_counts = Counter([r['sentiment'] for r in results])
        theme_counts = Counter(all_themes)

        # Calculate average sentiment by theme
        theme_sentiment = {}
        for theme in theme_counts.keys():
            theme_comments = [r for r in results if theme in r['themes']]
            if theme_comments:
                avg_score = sum(c['score'] for c in theme_comments) / len(theme_comments)
                theme_sentiment[theme] = {
                    'count': theme_counts[theme],
                    'avg_sentiment': round(avg_score, 2),
                    'sentiment_label': 'POSITIVE' if avg_score > 0.3 else 'NEGATIVE' if avg_score < -0.3 else 'NEUTRAL'
                }

        total_comments = len(results)

        return {
            'summary': {
                'total': total_comments,
                'positive': sentiment_counts.get('POSITIVE', 0),
                'negative': sentiment_counts.get('NEGATIVE', 0),
                'neutral': sentiment_counts.get('NEUTRAL', 0),
                'positive_pct': round(sentiment_counts.get('POSITIVE', 0) / total_comments * 100, 1),
                'negative_pct': round(sentiment_counts.get('NEGATIVE', 0) / total_comments * 100, 1),
                'neutral_pct': round(sentiment_counts.get('NEUTRAL', 0) / total_comments * 100, 1)
            },
            'themes': theme_sentiment,
            'detailed_analysis': sorted(results, key=lambda x: abs(x['score']), reverse=True)[:20],
            'top_positive': sorted([r for r in results if r['sentiment'] == 'POSITIVE'],
                                  key=lambda x: x['score'], reverse=True)[:5],
            'top_negative': sorted([r for r in results if r['sentiment'] == 'NEGATIVE'],
                                  key=lambda x: x['score'])[:5],
            'all_comments': results
        }

    def analyze_by_application(self, survey_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Analyze sentiment grouped by application

        Args:
            survey_df: DataFrame with 'application_name' and 'comments' columns

        Returns:
            List of analysis results per application
        """
        if 'application_name' not in survey_df.columns or 'comments' not in survey_df.columns:
            return []

        app_results = []

        for app_name in survey_df['application_name'].unique():
            if pd.isna(app_name):
                continue

            app_comments = survey_df[survey_df['application_name'] == app_name]['comments'].dropna()

            if len(app_comments) > 0:
                analysis = self.analyze_survey_comments(app_comments.tolist())
                app_results.append({
                    'application': str(app_name),
                    'comment_count': len(app_comments),
                    'sentiment_summary': analysis['summary'],
                    'themes': analysis['themes']
                })

        return sorted(app_results, key=lambda x: x['comment_count'], reverse=True)
