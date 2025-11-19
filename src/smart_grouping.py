"""
Smart Application Grouping with AI-Powered Explanations
Auto-categorizes applications into business domains with contextual reasoning
"""

import pandas as pd
from collections import defaultdict
import re


class SmartGroupingEngine:
    """AI-powered application grouping and explanation generator"""

    # Business domain patterns with keywords
    DOMAIN_PATTERNS = {
        'Financial Operations': {
            'keywords': ['budget', 'financial', 'finance', 'accounting', 'billing', 'payment',
                        'invoice', 'revenue', 'payroll', 'procurement', 'grant', 'accounts',
                        'asset', 'treasury', 'cost', 'expense'],
            'categories': ['Finance & Accounting'],
            'icon': '💰',
            'strategic_importance': 'Critical - Financial data and compliance'
        },

        'Human Capital Management': {
            'keywords': ['hr', 'human resources', 'recruitment', 'hiring', 'employee',
                        'performance', 'training', 'talent', 'attendance', 'benefits',
                        'onboarding', 'workforce', 'personnel'],
            'categories': ['Human Resources'],
            'icon': '👥',
            'strategic_importance': 'High - Workforce enablement and compliance'
        },

        'Citizen Engagement': {
            'keywords': ['citizen', 'permit', 'license', 'public', 'service request',
                        '311', 'complaint', 'case management', 'portal', 'community',
                        'resident', 'feedback', 'survey'],
            'categories': ['Citizen Services'],
            'icon': '🏛️',
            'strategic_importance': 'Critical - Public-facing services'
        },

        'Information Management': {
            'keywords': ['document', 'records', 'archive', 'content', 'digital', 'signature',
                        'knowledge', 'repository', 'file', 'storage', 'data warehouse',
                        'report', 'analytics', 'business intelligence'],
            'categories': ['Records Management', 'Compliance & Reporting'],
            'icon': '📄',
            'strategic_importance': 'High - Data governance and compliance'
        },

        'IT Infrastructure & Operations': {
            'keywords': ['network', 'infrastructure', 'monitoring', 'help desk', 'it support',
                        'backup', 'security', 'identity', 'vpn', 'email', 'server',
                        'database', 'cloud', 'hosting', 'system'],
            'categories': ['IT & Infrastructure'],
            'icon': '💻',
            'strategic_importance': 'Critical - Technology backbone'
        },

        'Asset & Resource Management': {
            'keywords': ['facility', 'fleet', 'inventory', 'work order', 'maintenance',
                        'asset', 'gis', 'mapping', 'project', 'resource', 'equipment',
                        'vehicle', 'building'],
            'categories': ['Operations'],
            'icon': '🏗️',
            'strategic_importance': 'Medium - Operational efficiency'
        },

        'Public Safety & Emergency Services': {
            'keywords': ['emergency', 'dispatch', 'incident', 'police', 'fire', 'investigation',
                        'evidence', 'safety', 'security', '911', 'crime', 'enforcement',
                        'patrol', 'response'],
            'categories': ['Public Safety'],
            'icon': '🚨',
            'strategic_importance': 'Critical - Public safety mission'
        },

        'Governance & Compliance': {
            'keywords': ['audit', 'compliance', 'regulation', 'policy', 'governance',
                        'legal', 'risk', 'internal control', 'oversight', 'transparency',
                        'accountability', 'ethics'],
            'categories': ['Compliance & Reporting'],
            'icon': '⚖️',
            'strategic_importance': 'High - Regulatory compliance'
        }
    }

    def __init__(self, df_applications):
        """Initialize with application portfolio data"""
        self.df = df_applications
        self.groupings = None

    def classify_application(self, app_row):
        """Classify a single application into business domain"""
        app_name = app_row['Application Name'].lower()
        category = app_row.get('Category', '').lower()
        comments = str(app_row.get('Comments', '')).lower()

        # Combined text for matching
        text = f"{app_name} {category} {comments}"

        scores = {}

        # Score each domain based on keyword matches
        for domain, config in self.DOMAIN_PATTERNS.items():
            score = 0
            matched_keywords = []

            # Check keywords
            for keyword in config['keywords']:
                if keyword in text:
                    score += 1
                    matched_keywords.append(keyword)

            # Bonus for category match
            if category and any(cat.lower() in category for cat in config['categories']):
                score += 5

            if score > 0:
                scores[domain] = {
                    'score': score,
                    'matched_keywords': matched_keywords
                }

        # Return best match
        if scores:
            best_domain = max(scores.items(), key=lambda x: x[1]['score'])
            return best_domain[0], scores[best_domain[0]]['matched_keywords']

        # Fallback to category-based classification
        return self._fallback_classification(category)

    def _fallback_classification(self, category):
        """Fallback classification based on category"""
        category_lower = category.lower()

        for domain, config in self.DOMAIN_PATTERNS.items():
            for cat in config['categories']:
                if cat.lower() in category_lower:
                    return domain, ['category match']

        return 'Uncategorized Applications', []

    def generate_groupings(self):
        """Generate smart groupings for all applications"""
        groupings = defaultdict(lambda: {
            'applications': [],
            'total_cost': 0,
            'avg_health': 0,
            'avg_value': 0,
            'count': 0,
            'icon': '📦',
            'strategic_importance': 'Medium',
            'retirement_candidates': 0,
            'modernization_candidates': 0,
            'health_scores': [],
            'business_values': []
        })

        # Classify each application
        for idx, app_row in self.df.iterrows():
            domain, matched_keywords = self.classify_application(app_row)

            # Add to grouping
            groupings[domain]['applications'].append({
                'name': app_row['Application Name'],
                'cost': app_row['Cost'],
                'health': app_row['Tech Health'],
                'value': app_row['Business Value'],
                'category': app_row.get('Category', 'N/A'),
                'matched_keywords': matched_keywords
            })

            groupings[domain]['total_cost'] += app_row['Cost']
            groupings[domain]['health_scores'].append(app_row['Tech Health'])
            groupings[domain]['business_values'].append(app_row['Business Value'])
            groupings[domain]['count'] += 1

            # Identify candidates
            if app_row['Tech Health'] <= 3 and app_row['Business Value'] <= 4:
                groupings[domain]['retirement_candidates'] += 1
            elif app_row['Tech Health'] <= 5 and app_row['Business Value'] >= 7:
                groupings[domain]['modernization_candidates'] += 1

            # Copy domain metadata
            if domain in self.DOMAIN_PATTERNS:
                groupings[domain]['icon'] = self.DOMAIN_PATTERNS[domain]['icon']
                groupings[domain]['strategic_importance'] = self.DOMAIN_PATTERNS[domain]['strategic_importance']

        # Calculate averages
        for domain in groupings:
            if groupings[domain]['health_scores']:
                groupings[domain]['avg_health'] = round(
                    sum(groupings[domain]['health_scores']) / len(groupings[domain]['health_scores']), 1
                )
            if groupings[domain]['business_values']:
                groupings[domain]['avg_value'] = round(
                    sum(groupings[domain]['business_values']) / len(groupings[domain]['business_values']), 1
                )

        self.groupings = dict(groupings)
        return self.groupings

    def generate_ai_explanation(self, domain, grouping_data):
        """Generate AI-powered explanation for WHY this grouping exists"""

        count = grouping_data['count']
        total_cost = grouping_data['total_cost']
        avg_health = grouping_data['avg_health']
        avg_value = grouping_data['avg_value']
        retire_count = grouping_data['retirement_candidates']
        modernize_count = grouping_data['modernization_candidates']

        # Build contextual explanation
        explanation_parts = []

        # 1. Domain purpose
        if domain in self.DOMAIN_PATTERNS:
            importance = self.DOMAIN_PATTERNS[domain]['strategic_importance']
            explanation_parts.append(f"Purpose: {importance}")

        # 2. Portfolio composition
        explanation_parts.append(
            f"Portfolio: {count} applications consuming ${total_cost:,.0f} annually "
            f"(${total_cost/count:,.0f} per app)"
        )

        # 3. Health assessment
        health_status = self._assess_health(avg_health)
        value_status = self._assess_value(avg_value)

        explanation_parts.append(
            f"Health Status: {health_status} (avg: {avg_health}/10) | "
            f"Business Value: {value_status} (avg: {avg_value}/10)"
        )

        # 4. Actionable insights
        insights = []

        if retire_count > 0:
            insights.append(f"🔴 {retire_count} retirement candidates identified (low health + low value)")

        if modernize_count > 0:
            insights.append(f"🟡 {modernize_count} modernization opportunities (critical apps with aging tech)")

        if avg_health < 5:
            insights.append(f"⚠️ Domain health below acceptable threshold - modernization priority")

        if total_cost > 2000000 and avg_value < 6:
            insights.append(f"💰 High spend domain with moderate value - rationalization opportunity")

        if avg_health >= 7 and avg_value >= 7:
            insights.append(f"✅ Well-maintained domain with strong business value")

        if insights:
            explanation_parts.append("Insights: " + " | ".join(insights))

        # 5. Recommendation
        recommendation = self._generate_recommendation(
            avg_health, avg_value, retire_count, modernize_count, total_cost
        )
        explanation_parts.append(f"Recommendation: {recommendation}")

        return "\n\n".join(explanation_parts)

    def _assess_health(self, score):
        """Assess technical health status"""
        if score >= 8:
            return "Excellent ✅"
        elif score >= 6:
            return "Good 🟢"
        elif score >= 4:
            return "Fair 🟡"
        else:
            return "Poor 🔴"

    def _assess_value(self, score):
        """Assess business value status"""
        if score >= 8:
            return "Critical ⭐"
        elif score >= 6:
            return "High 🟢"
        elif score >= 4:
            return "Moderate 🟡"
        else:
            return "Low 🔴"

    def _generate_recommendation(self, avg_health, avg_value, retire_count, modernize_count, total_cost):
        """Generate actionable recommendation"""

        if retire_count >= 3:
            return f"Start with retirement of {retire_count} low-value applications to reduce costs and complexity"

        if modernize_count >= 2 and avg_value >= 7:
            return f"Prioritize modernization of {modernize_count} critical applications to reduce technical risk"

        if avg_health < 5 and avg_value >= 6:
            return "Domain requires urgent modernization investment to protect business value"

        if avg_health >= 7 and avg_value >= 7:
            return "Continue current maintenance strategy - portfolio is well-optimized"

        if total_cost > 2000000 and avg_value < 5:
            return "High-spend, low-value domain - conduct detailed rationalization review"

        if avg_health >= 6 and avg_value < 5:
            return "Consider consolidation or retirement to free up resources for higher-value domains"

        return "Monitor portfolio and reassess quarterly"

    def get_groupings_summary(self):
        """Get summary of all groupings with AI explanations"""
        if not self.groupings:
            self.generate_groupings()

        summary = []

        # Sort by total cost (descending)
        sorted_domains = sorted(
            self.groupings.items(),
            key=lambda x: x[1]['total_cost'],
            reverse=True
        )

        for domain, data in sorted_domains:
            summary.append({
                'domain': domain,
                'icon': data['icon'],
                'count': data['count'],
                'total_cost': data['total_cost'],
                'avg_health': data['avg_health'],
                'avg_value': data['avg_value'],
                'retirement_candidates': data['retirement_candidates'],
                'modernization_candidates': data['modernization_candidates'],
                'strategic_importance': data['strategic_importance'],
                'ai_explanation': self.generate_ai_explanation(domain, data),
                'applications': data['applications']
            })

        return summary

    def get_domain_details(self, domain_name):
        """Get detailed breakdown for specific domain"""
        if not self.groupings:
            self.generate_groupings()

        if domain_name not in self.groupings:
            return None

        data = self.groupings[domain_name]

        return {
            'domain': domain_name,
            'icon': data['icon'],
            'count': data['count'],
            'total_cost': data['total_cost'],
            'avg_health': data['avg_health'],
            'avg_value': data['avg_value'],
            'retirement_candidates': data['retirement_candidates'],
            'modernization_candidates': data['modernization_candidates'],
            'strategic_importance': data['strategic_importance'],
            'ai_explanation': self.generate_ai_explanation(domain_name, data),
            'applications': sorted(
                data['applications'],
                key=lambda x: x['cost'],
                reverse=True
            )
        }
