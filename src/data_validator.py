"""
Data Quality Validator
Validates input data quality, detects anomalies, and generates data quality reports
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import re


class DataQualityValidator:
    """Comprehensive data quality validation and reporting engine"""

    # Required columns for assessment data
    REQUIRED_COLUMNS = [
        'Application Name',
        'Cost',
        'Tech Health',
        'Business Value',
        'Category'
    ]

    # Optional but recommended columns
    RECOMMENDED_COLUMNS = [
        'Comments',
        'Department',
        'Vendor',
        'Users'
    ]

    # Valid ranges for numeric fields
    FIELD_RANGES = {
        'Tech Health': (1, 10),
        'Business Value': (1, 10),
        'Cost': (0, 100000000)  # $100M max seems reasonable
    }

    def __init__(self, df: pd.DataFrame):
        """Initialize with application data"""
        self.df = df.copy()
        self.issues = defaultdict(list)
        self.warnings = defaultdict(list)
        self.stats = {}
        self.quality_score = 0
        self.confidence_level = 'Unknown'

    def validate_all(self) -> Dict[str, Any]:
        """Run all validation checks and return comprehensive report"""

        # 1. Structural validation
        self._validate_required_columns()
        self._check_recommended_columns()
        self._validate_data_types()

        # 2. Data completeness
        self._check_missing_data()
        self._check_empty_strings()

        # 3. Data quality checks
        self._detect_duplicates()
        self._validate_ranges()
        self._detect_outliers()
        self._check_suspicious_patterns()

        # 4. Business logic validation
        self._validate_business_rules()
        self._check_cost_consistency()

        # 5. Calculate overall quality score
        self._calculate_quality_score()

        # 6. Generate recommendations
        recommendations = self._generate_recommendations()

        return {
            'quality_score': self.quality_score,
            'confidence_level': self.confidence_level,
            'total_records': len(self.df),
            'issues': dict(self.issues),
            'warnings': dict(self.warnings),
            'statistics': self.stats,
            'recommendations': recommendations,
            'summary': self._generate_summary()
        }

    def _validate_required_columns(self):
        """Check if all required columns are present"""
        missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in self.df.columns]

        if missing_cols:
            self.issues['missing_columns'] = {
                'severity': 'critical',
                'count': len(missing_cols),
                'columns': missing_cols,
                'message': f'Missing required columns: {", ".join(missing_cols)}'
            }

    def _check_recommended_columns(self):
        """Check for recommended but optional columns"""
        missing_recommended = [col for col in self.RECOMMENDED_COLUMNS if col not in self.df.columns]

        if missing_recommended:
            self.warnings['missing_recommended'] = {
                'severity': 'low',
                'count': len(missing_recommended),
                'columns': missing_recommended,
                'message': f'Missing recommended columns: {", ".join(missing_recommended)}'
            }

    def _validate_data_types(self):
        """Validate data types for key columns"""
        type_issues = []

        # Check numeric columns
        numeric_cols = ['Cost', 'Tech Health', 'Business Value']
        for col in numeric_cols:
            if col in self.df.columns:
                try:
                    pd.to_numeric(self.df[col], errors='raise')
                except (ValueError, TypeError):
                    non_numeric = self.df[~pd.to_numeric(self.df[col], errors='coerce').notna()]
                    type_issues.append({
                        'column': col,
                        'expected': 'numeric',
                        'invalid_count': len(non_numeric),
                        'examples': non_numeric[col].head(3).tolist()
                    })

        if type_issues:
            self.issues['data_type_mismatch'] = {
                'severity': 'high',
                'count': len(type_issues),
                'details': type_issues,
                'message': f'Found {len(type_issues)} columns with data type issues'
            }

    def _check_missing_data(self):
        """Check for missing/null values"""
        missing_data = {}

        for col in self.df.columns:
            missing_count = self.df[col].isna().sum()
            if missing_count > 0:
                missing_pct = (missing_count / len(self.df)) * 100
                missing_data[col] = {
                    'count': int(missing_count),
                    'percentage': round(missing_pct, 1)
                }

        if missing_data:
            # Critical if required fields are missing
            critical_missing = {k: v for k, v in missing_data.items() if k in self.REQUIRED_COLUMNS}

            if critical_missing:
                self.issues['missing_required_data'] = {
                    'severity': 'high',
                    'count': len(critical_missing),
                    'details': critical_missing,
                    'message': f'Missing data in required fields'
                }

            # Warning for optional fields
            optional_missing = {k: v for k, v in missing_data.items() if k not in self.REQUIRED_COLUMNS}
            if optional_missing:
                self.warnings['missing_optional_data'] = {
                    'severity': 'medium',
                    'count': len(optional_missing),
                    'details': optional_missing,
                    'message': f'Missing data in optional fields'
                }

    def _check_empty_strings(self):
        """Check for empty string values that should be null"""
        empty_string_issues = {}

        for col in self.df.select_dtypes(include=['object']).columns:
            empty_count = (self.df[col].astype(str).str.strip() == '').sum()
            if empty_count > 0:
                empty_string_issues[col] = int(empty_count)

        if empty_string_issues:
            self.warnings['empty_strings'] = {
                'severity': 'low',
                'count': sum(empty_string_issues.values()),
                'details': empty_string_issues,
                'message': 'Found empty strings that should be null/missing'
            }

    def _detect_duplicates(self):
        """Detect duplicate application names"""
        duplicates = self.df[self.df.duplicated(subset=['Application Name'], keep=False)]

        if not duplicates.empty:
            dup_names = duplicates['Application Name'].value_counts()

            self.issues['duplicate_applications'] = {
                'severity': 'high',
                'count': len(dup_names),
                'total_duplicate_rows': len(duplicates),
                'duplicate_names': dup_names.head(10).to_dict(),
                'message': f'Found {len(dup_names)} duplicate application names'
            }

    def _validate_ranges(self):
        """Validate numeric fields are within expected ranges"""
        range_violations = []

        for field, (min_val, max_val) in self.FIELD_RANGES.items():
            if field in self.df.columns:
                out_of_range = self.df[
                    (pd.to_numeric(self.df[field], errors='coerce') < min_val) |
                    (pd.to_numeric(self.df[field], errors='coerce') > max_val)
                ]

                if not out_of_range.empty:
                    range_violations.append({
                        'field': field,
                        'expected_range': f'{min_val}-{max_val}',
                        'violation_count': len(out_of_range),
                        'examples': out_of_range[[field, 'Application Name']].head(3).to_dict('records')
                    })

        if range_violations:
            self.issues['range_violations'] = {
                'severity': 'high',
                'count': len(range_violations),
                'details': range_violations,
                'message': f'Found {len(range_violations)} fields with out-of-range values'
            }

    def _detect_outliers(self):
        """Detect statistical outliers in numeric fields"""
        outliers = {}

        numeric_cols = ['Cost', 'Tech Health', 'Business Value']

        for col in numeric_cols:
            if col in self.df.columns:
                # Use IQR method for outlier detection
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1

                lower_bound = Q1 - 3 * IQR
                upper_bound = Q3 + 3 * IQR

                outlier_rows = self.df[
                    (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
                ]

                if not outlier_rows.empty:
                    outliers[col] = {
                        'count': len(outlier_rows),
                        'lower_bound': round(lower_bound, 2),
                        'upper_bound': round(upper_bound, 2),
                        'examples': outlier_rows[[col, 'Application Name']].head(5).to_dict('records')
                    }

        if outliers:
            self.warnings['statistical_outliers'] = {
                'severity': 'medium',
                'count': len(outliers),
                'details': outliers,
                'message': 'Found statistical outliers (may be valid data)'
            }

    def _check_suspicious_patterns(self):
        """Detect suspicious data patterns"""
        suspicious = []

        # Check if all apps have same score
        for col in ['Tech Health', 'Business Value']:
            if col in self.df.columns:
                unique_vals = self.df[col].nunique()
                if unique_vals == 1:
                    suspicious.append({
                        'pattern': 'uniform_values',
                        'field': col,
                        'value': self.df[col].iloc[0],
                        'message': f'All {len(self.df)} applications have identical {col}: {self.df[col].iloc[0]}'
                    })
                elif unique_vals < 5 and len(self.df) > 50:
                    suspicious.append({
                        'pattern': 'low_variance',
                        'field': col,
                        'unique_count': unique_vals,
                        'message': f'Only {unique_vals} unique values for {col} across {len(self.df)} apps'
                    })

        # Check for sequential costs (likely placeholder data)
        if 'Cost' in self.df.columns:
            sorted_costs = sorted(self.df['Cost'].dropna())
            if len(sorted_costs) >= 10:
                diffs = np.diff(sorted_costs[:10])
                if np.all(diffs == diffs[0]):  # All differences are same
                    suspicious.append({
                        'pattern': 'sequential_costs',
                        'message': 'Costs appear to be sequential/placeholder values'
                    })

        # Check for too many perfect 5.0 scores (middle of scale)
        for col in ['Tech Health', 'Business Value']:
            if col in self.df.columns:
                middle_score_pct = (self.df[col] == 5.0).sum() / len(self.df) * 100
                if middle_score_pct > 30:
                    suspicious.append({
                        'pattern': 'excessive_middle_scores',
                        'field': col,
                        'percentage': round(middle_score_pct, 1),
                        'message': f'{middle_score_pct:.0f}% of apps have score of 5.0 (possible default/placeholder)'
                    })

        if suspicious:
            self.warnings['suspicious_patterns'] = {
                'severity': 'medium',
                'count': len(suspicious),
                'details': suspicious,
                'message': 'Detected suspicious data patterns'
            }

    def _validate_business_rules(self):
        """Validate business logic rules"""
        violations = []

        # Rule: High business value apps should have reasonable cost
        high_value_free = self.df[
            (self.df['Business Value'] >= 8) & (self.df['Cost'] == 0)
        ]
        if not high_value_free.empty:
            violations.append({
                'rule': 'high_value_zero_cost',
                'count': len(high_value_free),
                'message': f'{len(high_value_free)} high-value apps (≥8) have zero cost',
                'examples': high_value_free['Application Name'].head(5).tolist()
            })

        # Rule: Very expensive apps should have some business value
        expensive_low_value = self.df[
            (self.df['Cost'] > 100000) & (self.df['Business Value'] <= 2)
        ]
        if not expensive_low_value.empty:
            violations.append({
                'rule': 'expensive_low_value',
                'count': len(expensive_low_value),
                'message': f'{len(expensive_low_value)} expensive apps (>$100k) have very low value (≤2)',
                'examples': expensive_low_value[['Application Name', 'Cost', 'Business Value']].head(5).to_dict('records')
            })

        # Rule: Health and value both at extremes is suspicious
        extreme_both = self.df[
            ((self.df['Tech Health'] <= 1) & (self.df['Business Value'] >= 9)) |
            ((self.df['Tech Health'] >= 9) & (self.df['Business Value'] <= 1))
        ]
        if not extreme_both.empty:
            violations.append({
                'rule': 'extreme_mismatch',
                'count': len(extreme_both),
                'message': f'{len(extreme_both)} apps have extreme mismatch (health 1 + value 9, or vice versa)',
                'examples': extreme_both[['Application Name', 'Tech Health', 'Business Value']].head(5).to_dict('records')
            })

        if violations:
            self.warnings['business_rule_violations'] = {
                'severity': 'medium',
                'count': len(violations),
                'details': violations,
                'message': 'Found potential business logic inconsistencies'
            }

    def _check_cost_consistency(self):
        """Check for cost consistency and reasonableness"""
        if 'Cost' not in self.df.columns:
            return

        total_cost = self.df['Cost'].sum()
        avg_cost = self.df['Cost'].mean()
        median_cost = self.df['Cost'].median()

        self.stats['cost_analysis'] = {
            'total_cost': total_cost,
            'avg_cost': avg_cost,
            'median_cost': median_cost,
            'min_cost': self.df['Cost'].min(),
            'max_cost': self.df['Cost'].max(),
            'zero_cost_count': int((self.df['Cost'] == 0).sum()),
            'over_1m_count': int((self.df['Cost'] > 1000000).sum())
        }

        # Warning if too many zero-cost apps
        zero_pct = (self.df['Cost'] == 0).sum() / len(self.df) * 100
        if zero_pct > 20:
            self.warnings['excessive_zero_costs'] = {
                'severity': 'medium',
                'percentage': round(zero_pct, 1),
                'count': int((self.df['Cost'] == 0).sum()),
                'message': f'{zero_pct:.0f}% of applications have zero cost'
            }

    def _calculate_quality_score(self):
        """Calculate overall data quality score (0-100)"""

        score = 100.0

        # Deduct for critical issues
        if 'missing_columns' in self.issues:
            score -= 30  # Missing required columns is critical

        if 'data_type_mismatch' in self.issues:
            score -= 15

        if 'duplicate_applications' in self.issues:
            count = self.issues['duplicate_applications']['count']
            score -= min(20, count * 2)  # Up to 20 points for duplicates

        if 'range_violations' in self.issues:
            score -= 15

        if 'missing_required_data' in self.issues:
            # Deduct based on percentage of missing data
            max_missing_pct = max([v['percentage'] for v in self.issues['missing_required_data']['details'].values()])
            score -= min(20, max_missing_pct)

        # Deduct for warnings (less severe)
        warning_deductions = {
            'missing_recommended': 2,
            'missing_optional_data': 3,
            'empty_strings': 2,
            'statistical_outliers': 3,
            'suspicious_patterns': 5,
            'business_rule_violations': 5,
            'excessive_zero_costs': 3
        }

        for warning_key, deduction in warning_deductions.items():
            if warning_key in self.warnings:
                score -= deduction

        self.quality_score = max(0, min(100, round(score, 1)))

        # Determine confidence level
        if self.quality_score >= 90:
            self.confidence_level = 'Very High'
        elif self.quality_score >= 75:
            self.confidence_level = 'High'
        elif self.quality_score >= 60:
            self.confidence_level = 'Medium'
        elif self.quality_score >= 40:
            self.confidence_level = 'Low'
        else:
            self.confidence_level = 'Very Low'

    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on findings"""
        recommendations = []

        # Critical: Missing columns
        if 'missing_columns' in self.issues:
            recommendations.append({
                'priority': 'critical',
                'title': 'Add Missing Required Columns',
                'description': f'Add columns: {", ".join(self.issues["missing_columns"]["columns"])}',
                'action': 'Update your data source to include all required columns before upload'
            })

        # High: Duplicates
        if 'duplicate_applications' in self.issues:
            recommendations.append({
                'priority': 'high',
                'title': 'Remove Duplicate Applications',
                'description': f'{self.issues["duplicate_applications"]["count"]} duplicate app names found',
                'action': 'Review and merge/remove duplicate entries to ensure data accuracy'
            })

        # High: Range violations
        if 'range_violations' in self.issues:
            recommendations.append({
                'priority': 'high',
                'title': 'Fix Out-of-Range Values',
                'description': 'Some numeric fields have invalid values',
                'action': 'Review and correct values outside expected ranges (e.g., Health/Value must be 1-10)'
            })

        # Medium: Missing data
        if 'missing_required_data' in self.issues:
            recommendations.append({
                'priority': 'medium',
                'title': 'Fill in Missing Data',
                'description': 'Required fields have missing values',
                'action': 'Complete missing data for more accurate analysis'
            })

        # Medium: Suspicious patterns
        if 'suspicious_patterns' in self.warnings:
            recommendations.append({
                'priority': 'medium',
                'title': 'Review Suspicious Patterns',
                'description': 'Data shows unusual patterns that may indicate placeholder values',
                'action': 'Verify data is real assessment data, not placeholder/test values'
            })

        # Low: Add recommended columns
        if 'missing_recommended' in self.warnings:
            recommendations.append({
                'priority': 'low',
                'title': 'Add Recommended Columns',
                'description': f'Optional columns: {", ".join(self.warnings["missing_recommended"]["columns"])}',
                'action': 'Adding these columns will enable more detailed analysis'
            })

        return recommendations

    def _generate_summary(self) -> str:
        """Generate human-readable summary"""

        total_issues = len(self.issues)
        total_warnings = len(self.warnings)

        if total_issues == 0 and total_warnings == 0:
            return f"Excellent data quality! Score: {self.quality_score}/100. No issues detected."

        summary_parts = [
            f"Data quality score: {self.quality_score}/100 ({self.confidence_level} confidence)",
            f"Found {total_issues} critical issues and {total_warnings} warnings"
        ]

        if total_issues > 0:
            issue_types = ', '.join(self.issues.keys())
            summary_parts.append(f"Critical issues: {issue_types}")

        if total_warnings > 0:
            warning_types = ', '.join(list(self.warnings.keys())[:3])
            summary_parts.append(f"Warnings: {warning_types}")

        return ' | '.join(summary_parts)

    def get_clean_data_suggestions(self) -> Dict[str, Any]:
        """Generate specific data cleaning suggestions"""

        suggestions = {
            'remove_rows': [],
            'fix_values': [],
            'add_columns': [],
            'merge_duplicates': []
        }

        # Suggest removing rows with critical missing data
        if 'missing_required_data' in self.issues:
            for field, details in self.issues['missing_required_data']['details'].items():
                if details['percentage'] > 50:
                    suggestions['remove_rows'].append({
                        'reason': f'Missing {field}',
                        'percentage': details['percentage'],
                        'recommended_action': f'Remove or complete {field} data'
                    })

        # Suggest fixing range violations
        if 'range_violations' in self.issues:
            suggestions['fix_values'] = self.issues['range_violations']['details']

        # Suggest adding missing columns
        if 'missing_columns' in self.issues:
            suggestions['add_columns'] = self.issues['missing_columns']['columns']

        # Suggest merging duplicates
        if 'duplicate_applications' in self.issues:
            suggestions['merge_duplicates'] = list(self.issues['duplicate_applications']['duplicate_names'].keys())

        return suggestions
