"""
Compliance Engine Module - Security & Compliance Assessment
Supports SOX, PCI-DSS, HIPAA, GDPR compliance frameworks
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class ComplianceRequirement:
    """Individual compliance requirement"""
    id: str
    name: str
    description: str
    framework: str  # SOX, PCI-DSS, HIPAA, GDPR
    category: str  # e.g., "Data Security", "Access Control", "Audit Trail"
    severity: str  # Critical, High, Medium, Low
    weight: float = 1.0


@dataclass
class ComplianceFramework:
    """Compliance framework definition"""
    name: str
    description: str
    requirements: List[ComplianceRequirement] = field(default_factory=list)

    def add_requirement(self, requirement: ComplianceRequirement):
        """Add a requirement to the framework"""
        self.requirements.append(requirement)

    def get_requirements_by_category(self, category: str) -> List[ComplianceRequirement]:
        """Get all requirements for a specific category"""
        return [r for r in self.requirements if r.category == category]


class ComplianceEngine:
    """
    Assesses applications against compliance frameworks.

    Features:
    - Multi-framework support (SOX, PCI-DSS, HIPAA, GDPR)
    - Automated compliance scoring
    - Gap analysis and remediation recommendations
    - Control effectiveness measurement
    - Audit trail tracking
    """

    def __init__(self):
        """Initialize compliance engine with standard frameworks"""
        self.frameworks = {}
        self._initialize_frameworks()

    def _initialize_frameworks(self):
        """Initialize standard compliance frameworks"""

        # SOX (Sarbanes-Oxley) - Financial Controls
        sox = ComplianceFramework(
            name="SOX",
            description="Sarbanes-Oxley Act - Financial Reporting Controls"
        )
        sox.add_requirement(ComplianceRequirement(
            id="SOX-001", name="Data Integrity",
            description="Ensure accuracy and completeness of financial data",
            framework="SOX", category="Data Security", severity="Critical", weight=1.5
        ))
        sox.add_requirement(ComplianceRequirement(
            id="SOX-002", name="Access Controls",
            description="Implement role-based access controls for financial systems",
            framework="SOX", category="Access Control", severity="Critical", weight=1.5
        ))
        sox.add_requirement(ComplianceRequirement(
            id="SOX-003", name="Audit Trail",
            description="Maintain comprehensive audit logs for all financial transactions",
            framework="SOX", category="Audit Trail", severity="Critical", weight=1.5
        ))
        sox.add_requirement(ComplianceRequirement(
            id="SOX-004", name="Change Management",
            description="Document and approve all system changes",
            framework="SOX", category="Change Management", severity="High", weight=1.2
        ))
        sox.add_requirement(ComplianceRequirement(
            id="SOX-005", name="Segregation of Duties",
            description="Separate responsibilities to prevent fraud",
            framework="SOX", category="Access Control", severity="Critical", weight=1.5
        ))
        self.frameworks["SOX"] = sox

        # PCI-DSS (Payment Card Industry Data Security Standard)
        pci = ComplianceFramework(
            name="PCI-DSS",
            description="Payment Card Industry Data Security Standard"
        )
        pci.add_requirement(ComplianceRequirement(
            id="PCI-001", name="Encryption at Rest",
            description="Encrypt stored cardholder data",
            framework="PCI-DSS", category="Data Security", severity="Critical", weight=2.0
        ))
        pci.add_requirement(ComplianceRequirement(
            id="PCI-002", name="Encryption in Transit",
            description="Encrypt transmission of cardholder data across networks",
            framework="PCI-DSS", category="Data Security", severity="Critical", weight=2.0
        ))
        pci.add_requirement(ComplianceRequirement(
            id="PCI-003", name="Firewall Configuration",
            description="Install and maintain firewall to protect cardholder data",
            framework="PCI-DSS", category="Network Security", severity="Critical", weight=1.8
        ))
        pci.add_requirement(ComplianceRequirement(
            id="PCI-004", name="Vulnerability Management",
            description="Regular security scanning and patching",
            framework="PCI-DSS", category="Security Maintenance", severity="High", weight=1.5
        ))
        pci.add_requirement(ComplianceRequirement(
            id="PCI-005", name="Multi-Factor Authentication",
            description="Implement MFA for system access",
            framework="PCI-DSS", category="Access Control", severity="Critical", weight=1.8
        ))
        pci.add_requirement(ComplianceRequirement(
            id="PCI-006", name="Security Monitoring",
            description="Track and monitor all access to network resources",
            framework="PCI-DSS", category="Monitoring", severity="High", weight=1.5
        ))
        self.frameworks["PCI-DSS"] = pci

        # HIPAA (Health Insurance Portability and Accountability Act)
        hipaa = ComplianceFramework(
            name="HIPAA",
            description="Health Insurance Portability and Accountability Act"
        )
        hipaa.add_requirement(ComplianceRequirement(
            id="HIPAA-001", name="PHI Encryption",
            description="Encrypt Protected Health Information at rest and in transit",
            framework="HIPAA", category="Data Security", severity="Critical", weight=2.0
        ))
        hipaa.add_requirement(ComplianceRequirement(
            id="HIPAA-002", name="Access Controls",
            description="Implement unique user identification and authentication",
            framework="HIPAA", category="Access Control", severity="Critical", weight=1.8
        ))
        hipaa.add_requirement(ComplianceRequirement(
            id="HIPAA-003", name="Audit Controls",
            description="Implement mechanisms to record and examine activity",
            framework="HIPAA", category="Audit Trail", severity="Critical", weight=1.7
        ))
        hipaa.add_requirement(ComplianceRequirement(
            id="HIPAA-004", name="Data Backup",
            description="Establish and implement procedures for data backup",
            framework="HIPAA", category="Business Continuity", severity="High", weight=1.5
        ))
        hipaa.add_requirement(ComplianceRequirement(
            id="HIPAA-005", name="Breach Notification",
            description="Procedures for breach detection and notification",
            framework="HIPAA", category="Incident Response", severity="Critical", weight=1.8
        ))
        hipaa.add_requirement(ComplianceRequirement(
            id="HIPAA-006", name="Minimum Necessary",
            description="Limit PHI access to minimum necessary",
            framework="HIPAA", category="Access Control", severity="High", weight=1.4
        ))
        self.frameworks["HIPAA"] = hipaa

        # GDPR (General Data Protection Regulation)
        gdpr = ComplianceFramework(
            name="GDPR",
            description="General Data Protection Regulation (EU)"
        )
        gdpr.add_requirement(ComplianceRequirement(
            id="GDPR-001", name="Data Encryption",
            description="Pseudonymization and encryption of personal data",
            framework="GDPR", category="Data Security", severity="Critical", weight=1.8
        ))
        gdpr.add_requirement(ComplianceRequirement(
            id="GDPR-002", name="Right to Erasure",
            description="Capability to delete personal data upon request",
            framework="GDPR", category="Data Rights", severity="Critical", weight=1.7
        ))
        gdpr.add_requirement(ComplianceRequirement(
            id="GDPR-003", name="Data Portability",
            description="Ability to export data in machine-readable format",
            framework="GDPR", category="Data Rights", severity="High", weight=1.4
        ))
        gdpr.add_requirement(ComplianceRequirement(
            id="GDPR-004", name="Breach Notification",
            description="72-hour breach notification requirement",
            framework="GDPR", category="Incident Response", severity="Critical", weight=1.9
        ))
        gdpr.add_requirement(ComplianceRequirement(
            id="GDPR-005", name="Data Processing Records",
            description="Maintain records of processing activities",
            framework="GDPR", category="Audit Trail", severity="High", weight=1.5
        ))
        gdpr.add_requirement(ComplianceRequirement(
            id="GDPR-006", name="Privacy by Design",
            description="Data protection integrated into system design",
            framework="GDPR", category="System Design", severity="High", weight=1.6
        ))
        gdpr.add_requirement(ComplianceRequirement(
            id="GDPR-007", name="Consent Management",
            description="Obtain and manage user consent for data processing",
            framework="GDPR", category="Data Rights", severity="Critical", weight=1.7
        ))
        self.frameworks["GDPR"] = gdpr

        logger.info(f"Initialized {len(self.frameworks)} compliance frameworks")

    def assess_application_compliance(
        self,
        app_name: str,
        framework_name: str,
        compliance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess a single application against a compliance framework.

        Args:
            app_name: Application name
            framework_name: Framework to assess against (SOX, PCI-DSS, HIPAA, GDPR)
            compliance_data: Dictionary with compliance status for each requirement
                            Format: {requirement_id: {'status': 'compliant|non_compliant|partial',
                                                      'notes': 'optional notes'}}

        Returns:
            Compliance assessment results
        """
        if framework_name not in self.frameworks:
            return {'error': f'Framework {framework_name} not found'}

        framework = self.frameworks[framework_name]

        # Calculate compliance for each requirement
        requirement_results = []
        total_weight = 0
        weighted_score = 0

        for req in framework.requirements:
            req_data = compliance_data.get(req.id, {'status': 'non_compliant'})
            status = req_data.get('status', 'non_compliant')

            # Score: compliant=1.0, partial=0.5, non_compliant=0.0
            if status == 'compliant':
                score = 1.0
            elif status == 'partial':
                score = 0.5
            else:
                score = 0.0

            weighted_score += score * req.weight
            total_weight += req.weight

            requirement_results.append({
                'requirement_id': req.id,
                'requirement_name': req.name,
                'category': req.category,
                'severity': req.severity,
                'status': status,
                'score': score,
                'weight': req.weight,
                'notes': req_data.get('notes', '')
            })

        # Calculate overall compliance percentage
        compliance_percentage = (weighted_score / total_weight * 100) if total_weight > 0 else 0

        # Determine compliance level
        if compliance_percentage >= 95:
            compliance_level = 'Fully Compliant'
            risk_level = 'Low'
        elif compliance_percentage >= 80:
            compliance_level = 'Substantially Compliant'
            risk_level = 'Medium'
        elif compliance_percentage >= 60:
            compliance_level = 'Partially Compliant'
            risk_level = 'High'
        else:
            compliance_level = 'Non-Compliant'
            risk_level = 'Critical'

        # Identify gaps (non-compliant or partial requirements)
        gaps = [r for r in requirement_results if r['status'] != 'compliant']
        critical_gaps = [r for r in gaps if r['severity'] == 'Critical']

        return {
            'application_name': app_name,
            'framework': framework_name,
            'assessment_date': datetime.now().isoformat(),
            'compliance_percentage': round(compliance_percentage, 2),
            'compliance_level': compliance_level,
            'risk_level': risk_level,
            'total_requirements': len(framework.requirements),
            'compliant_requirements': len([r for r in requirement_results if r['status'] == 'compliant']),
            'partial_requirements': len([r for r in requirement_results if r['status'] == 'partial']),
            'non_compliant_requirements': len([r for r in requirement_results if r['status'] == 'non_compliant']),
            'critical_gaps_count': len(critical_gaps),
            'requirement_results': requirement_results,
            'gaps': gaps,
            'critical_gaps': critical_gaps
        }

    def batch_assess_compliance(
        self,
        df: pd.DataFrame,
        framework_name: str,
        compliance_mapping: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> pd.DataFrame:
        """
        Assess multiple applications against a framework.

        Args:
            df: DataFrame with application data
            framework_name: Framework to assess
            compliance_mapping: Optional mapping of app names to compliance data

        Returns:
            DataFrame with compliance scores added
        """
        if framework_name not in self.frameworks:
            logger.error(f"Framework {framework_name} not found")
            return df

        # If no mapping provided, use heuristics based on Security and Tech Health scores
        if compliance_mapping is None:
            compliance_mapping = self._generate_compliance_heuristics(df, framework_name)

        compliance_scores = []
        compliance_levels = []
        risk_levels = []
        gap_counts = []

        for _, row in df.iterrows():
            app_name = row['Application Name']
            comp_data = compliance_mapping.get(app_name, {})

            assessment = self.assess_application_compliance(
                app_name=app_name,
                framework_name=framework_name,
                compliance_data=comp_data
            )

            compliance_scores.append(assessment['compliance_percentage'])
            compliance_levels.append(assessment['compliance_level'])
            risk_levels.append(assessment['risk_level'])
            gap_counts.append(len(assessment['gaps']))

        # Add compliance data to DataFrame
        df_result = df.copy()
        df_result[f'{framework_name}_Compliance_Score'] = compliance_scores
        df_result[f'{framework_name}_Compliance_Level'] = compliance_levels
        df_result[f'{framework_name}_Risk_Level'] = risk_levels
        df_result[f'{framework_name}_Gap_Count'] = gap_counts

        return df_result

    def _generate_compliance_heuristics(
        self,
        df: pd.DataFrame,
        framework_name: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generate compliance estimates based on app characteristics.
        Uses Security score and Tech Health as proxies for compliance.
        """
        framework = self.frameworks[framework_name]
        compliance_mapping = {}

        for _, row in df.iterrows():
            app_name = row['Application Name']

            # Use Security score (0-10) and Tech Health (0-10) as compliance indicators
            security_score = row.get('Security', 5) / 10  # Normalize to 0-1
            tech_health = row.get('Tech Health', 5) / 10

            # Average as base compliance probability
            base_compliance = (security_score + tech_health) / 2

            # Generate status for each requirement
            req_statuses = {}
            for req in framework.requirements:
                # Add some randomness but weighted by base compliance
                random_factor = np.random.random()

                # Higher severity requirements are harder to meet
                severity_modifier = {
                    'Critical': -0.15,
                    'High': -0.10,
                    'Medium': -0.05,
                    'Low': 0
                }.get(req.severity, 0)

                probability = base_compliance + severity_modifier

                if random_factor < probability:
                    status = 'compliant'
                elif random_factor < probability + 0.2:
                    status = 'partial'
                else:
                    status = 'non_compliant'

                req_statuses[req.id] = {'status': status}

            compliance_mapping[app_name] = req_statuses

        return compliance_mapping

    def generate_gap_analysis_report(
        self,
        df: pd.DataFrame,
        framework_name: str,
        compliance_mapping: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive gap analysis report.

        Returns:
            Gap analysis with remediation priorities
        """
        if framework_name not in self.frameworks:
            return {'error': f'Framework {framework_name} not found'}

        framework = self.frameworks[framework_name]

        # Assess all applications
        if compliance_mapping is None:
            compliance_mapping = self._generate_compliance_heuristics(df, framework_name)

        all_assessments = []
        for _, row in df.iterrows():
            app_name = row['Application Name']
            comp_data = compliance_mapping.get(app_name, {})
            assessment = self.assess_application_compliance(app_name, framework_name, comp_data)
            all_assessments.append(assessment)

        # Aggregate gap analysis
        requirement_gap_summary = {}
        for req in framework.requirements:
            gap_summary = {
                'requirement_id': req.id,
                'requirement_name': req.name,
                'category': req.category,
                'severity': req.severity,
                'compliant_apps': 0,
                'partial_apps': 0,
                'non_compliant_apps': 0,
                'affected_applications': []
            }

            for assessment in all_assessments:
                req_result = next(
                    (r for r in assessment['requirement_results'] if r['requirement_id'] == req.id),
                    None
                )
                if req_result:
                    if req_result['status'] == 'compliant':
                        gap_summary['compliant_apps'] += 1
                    elif req_result['status'] == 'partial':
                        gap_summary['partial_apps'] += 1
                        gap_summary['affected_applications'].append(assessment['application_name'])
                    else:
                        gap_summary['non_compliant_apps'] += 1
                        gap_summary['affected_applications'].append(assessment['application_name'])

            # Calculate compliance rate
            total_apps = len(all_assessments)
            gap_summary['compliance_rate'] = (
                gap_summary['compliant_apps'] / total_apps * 100
            ) if total_apps > 0 else 0

            requirement_gap_summary[req.id] = gap_summary

        # Identify top gaps (lowest compliance rates for critical/high severity)
        critical_gaps = [
            gap for gap in requirement_gap_summary.values()
            if gap['severity'] in ['Critical', 'High'] and gap['compliance_rate'] < 80
        ]
        critical_gaps.sort(key=lambda x: (
            -({'Critical': 3, 'High': 2, 'Medium': 1, 'Low': 0}[x['severity']]),
            x['compliance_rate']
        ))

        # Portfolio-wide statistics
        avg_compliance = np.mean([a['compliance_percentage'] for a in all_assessments])

        return {
            'framework': framework_name,
            'report_date': datetime.now().isoformat(),
            'portfolio_summary': {
                'total_applications': len(all_assessments),
                'avg_compliance_percentage': round(avg_compliance, 2),
                'fully_compliant_apps': len([a for a in all_assessments if a['compliance_level'] == 'Fully Compliant']),
                'non_compliant_apps': len([a for a in all_assessments if a['compliance_level'] == 'Non-Compliant']),
                'critical_risk_apps': len([a for a in all_assessments if a['risk_level'] == 'Critical'])
            },
            'requirement_gaps': list(requirement_gap_summary.values()),
            'critical_gaps': critical_gaps[:10],  # Top 10 critical gaps
            'application_assessments': all_assessments,
            'remediation_priorities': self._generate_remediation_priorities(critical_gaps, all_assessments)
        }

    def _generate_remediation_priorities(
        self,
        critical_gaps: List[Dict[str, Any]],
        assessments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate prioritized remediation recommendations"""
        priorities = []

        for gap in critical_gaps[:5]:  # Top 5 priorities
            priority = {
                'priority_rank': len(priorities) + 1,
                'requirement_id': gap['requirement_id'],
                'requirement_name': gap['requirement_name'],
                'severity': gap['severity'],
                'affected_apps_count': len(gap['affected_applications']),
                'affected_applications': gap['affected_applications'][:10],  # Top 10
                'current_compliance_rate': round(gap['compliance_rate'], 1),
                'estimated_effort': self._estimate_remediation_effort(gap),
                'business_impact': self._estimate_business_impact(gap, assessments),
                'recommended_action': self._get_remediation_action(gap)
            }
            priorities.append(priority)

        return priorities

    def _estimate_remediation_effort(self, gap: Dict[str, Any]) -> str:
        """Estimate effort required for remediation"""
        affected_count = len(gap['affected_applications'])

        if gap['severity'] == 'Critical' and affected_count > 10:
            return 'High (3-6 months)'
        elif gap['severity'] in ['Critical', 'High'] and affected_count > 5:
            return 'Medium (1-3 months)'
        else:
            return 'Low (< 1 month)'

    def _estimate_business_impact(
        self,
        gap: Dict[str, Any],
        assessments: List[Dict[str, Any]]
    ) -> str:
        """Estimate business impact of the gap"""
        if gap['severity'] == 'Critical':
            return 'Critical - Potential regulatory penalties and data breach risk'
        elif gap['severity'] == 'High':
            return 'High - Increased security and compliance risk'
        else:
            return 'Medium - Moderate compliance risk'

    def _get_remediation_action(self, gap: Dict[str, Any]) -> str:
        """Get recommended remediation action"""
        actions = {
            'Data Security': 'Implement encryption and data protection controls',
            'Access Control': 'Deploy identity and access management solution',
            'Audit Trail': 'Enable comprehensive logging and monitoring',
            'Network Security': 'Update firewall rules and network segmentation',
            'Monitoring': 'Deploy SIEM and security monitoring tools',
            'Business Continuity': 'Implement backup and disaster recovery procedures',
            'Incident Response': 'Develop and test incident response procedures',
            'Data Rights': 'Implement data subject rights management system',
            'System Design': 'Redesign system with privacy by design principles',
            'Change Management': 'Establish formal change management process',
            'Security Maintenance': 'Implement patch management and vulnerability scanning'
        }

        return actions.get(gap['category'], 'Review and implement appropriate controls')

    def get_framework_summary(self, framework_name: str) -> Dict[str, Any]:
        """Get summary of a compliance framework"""
        if framework_name not in self.frameworks:
            return {'error': f'Framework {framework_name} not found'}

        framework = self.frameworks[framework_name]

        categories = {}
        for req in framework.requirements:
            if req.category not in categories:
                categories[req.category] = []
            categories[req.category].append({
                'id': req.id,
                'name': req.name,
                'severity': req.severity
            })

        return {
            'name': framework.name,
            'description': framework.description,
            'total_requirements': len(framework.requirements),
            'categories': categories,
            'severity_breakdown': {
                'Critical': len([r for r in framework.requirements if r.severity == 'Critical']),
                'High': len([r for r in framework.requirements if r.severity == 'High']),
                'Medium': len([r for r in framework.requirements if r.severity == 'Medium']),
                'Low': len([r for r in framework.requirements if r.severity == 'Low'])
            }
        }

    def list_frameworks(self) -> List[str]:
        """List all available frameworks"""
        return list(self.frameworks.keys())
