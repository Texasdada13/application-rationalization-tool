"""
Generate realistic synthetic application portfolio data for public sector organization
Targets: 200+ applications, 100 employees, high legacy burden
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Public sector application categories
CATEGORIES = {
    'Finance & Accounting': ['Financial System', 'Budget Management', 'Procurement', 'Grant Management', 'Payroll', 'Accounts Payable', 'Revenue Collection', 'Asset Management'],
    'Human Resources': ['HR Management', 'Recruitment', 'Performance Management', 'Training', 'Time & Attendance', 'Benefits Administration', 'Employee Portal'],
    'Citizen Services': ['Permit System', 'License Management', 'Case Management', 'Public Portal', 'Service Request', '311 System', 'Complaint Tracking'],
    'Records Management': ['Document Management', 'Records Archive', 'Email Archive', 'Digital Signatures', 'Content Management'],
    'IT & Infrastructure': ['Network Monitoring', 'Help Desk', 'Asset Inventory', 'Backup System', 'Identity Management', 'VPN', 'Email System'],
    'Operations': ['Facility Management', 'Fleet Management', 'Inventory', 'Work Order', 'GIS Mapping', 'Project Management'],
    'Public Safety': ['Emergency Dispatch', 'Incident Reporting', 'Investigation Management', 'Evidence Tracking'],
    'Compliance & Reporting': ['Audit Management', 'Compliance Tracking', 'Reporting Dashboard', 'Analytics Platform', 'Data Warehouse']
}

OWNERS = [
    'IT Department', 'Finance', 'Human Resources', 'City Manager Office',
    'Public Works', 'Planning & Development', 'Police Department', 'Fire Department',
    'Parks & Recreation', 'Public Health', 'Transportation', 'Water & Utilities',
    'Legal Department', 'Communications', 'Economic Development'
]

# Application name prefixes/suffixes
PREFIXES = ['Legacy', 'Modern', 'Cloud-based', 'On-premise', 'Enterprise', 'Departmental', 'Shared']
VERSIONS = ['', ' v1', ' v2', ' (Old)', ' (New)', ' Classic', ' Pro', ' Plus', ' Enterprise']
VENDORS = ['Oracle', 'SAP', 'Microsoft', 'Tyler Technologies', 'Infor', 'Workday', 'Salesforce', 'ServiceNow', 'Custom Built', 'Open Source']

def generate_application_name(category, app_type, index):
    """Generate realistic application names"""
    base_names = [
        f"{app_type}",
        f"{app_type} System",
        f"{app_type} Platform",
        f"{app_type} Tool",
        f"Integrated {app_type}",
        f"{category.split('&')[0].strip()} {app_type}"
    ]

    name = random.choice(base_names)

    # Add version or qualifier sometimes
    if random.random() < 0.3:
        name += random.choice(VERSIONS)

    return name

def generate_realistic_portfolio(num_apps=220):
    """Generate realistic public sector portfolio data"""

    applications = []
    app_id = 1

    for category, app_types in CATEGORIES.items():
        # Determine how many apps in this category (some categories have more)
        if category in ['Finance & Accounting', 'IT & Infrastructure', 'Citizen Services']:
            num_category_apps = int(num_apps * 0.15)  # 15% each for major categories
        elif category in ['Human Resources', 'Operations', 'Records Management']:
            num_category_apps = int(num_apps * 0.12)  # 12% each
        else:
            num_category_apps = int(num_apps * 0.08)  # 8% for smaller categories

        for i in range(num_category_apps):
            app_type = random.choice(app_types)
            app_name = generate_application_name(category, app_type, app_id)

            # Ensure unique names
            while any(app['Application Name'] == app_name for app in applications):
                app_name = generate_application_name(category, app_type, app_id)

            owner = random.choice(OWNERS)

            # Generate correlated metrics for realism
            # Define app "age tier" which affects other metrics
            age_tier = random.choices(
                ['modern', 'recent', 'aging', 'legacy', 'ancient'],
                weights=[0.15, 0.20, 0.30, 0.25, 0.10]
            )[0]

            # Tech Health correlates with age
            if age_tier == 'modern':
                tech_health = np.random.randint(7, 11)
            elif age_tier == 'recent':
                tech_health = np.random.randint(6, 9)
            elif age_tier == 'aging':
                tech_health = np.random.randint(4, 7)
            elif age_tier == 'legacy':
                tech_health = np.random.randint(2, 5)
            else:  # ancient
                tech_health = np.random.randint(1, 4)

            # Business Value varies by category and criticality
            if category in ['Finance & Accounting', 'Public Safety', 'Citizen Services']:
                # Critical categories tend to have higher business value
                business_value = np.random.randint(6, 11)
            elif category in ['IT & Infrastructure', 'Human Resources']:
                business_value = np.random.randint(5, 9)
            else:
                business_value = np.random.randint(3, 8)

            # Add some variance - not all apps in critical categories are critical
            business_value = max(1, min(10, business_value + np.random.randint(-2, 3)))

            # Cost correlates with age and criticality
            base_cost = {
                'modern': np.random.uniform(15000, 80000),
                'recent': np.random.uniform(20000, 100000),
                'aging': np.random.uniform(25000, 150000),
                'legacy': np.random.uniform(30000, 250000),
                'ancient': np.random.uniform(20000, 180000)
            }[age_tier]

            # Enterprise/critical apps cost more
            if business_value >= 8:
                base_cost *= np.random.uniform(1.5, 3.0)

            # Add some small cheap apps
            if random.random() < 0.15:
                base_cost = np.random.uniform(2000, 15000)

            cost = round(base_cost, 2)

            # Usage varies - some apps are heavily used, others not
            usage_tier = random.choices(
                ['heavy', 'moderate', 'light', 'minimal'],
                weights=[0.20, 0.35, 0.30, 0.15]
            )[0]

            usage = {
                'heavy': np.random.randint(500, 1000),
                'moderate': np.random.randint(200, 500),
                'light': np.random.randint(50, 200),
                'minimal': np.random.randint(5, 50)
            }[usage_tier]

            # Security: public sector needs high security
            # Modern apps tend to be more secure
            if age_tier in ['modern', 'recent']:
                security = np.random.randint(7, 11)
            elif age_tier == 'aging':
                security = np.random.randint(5, 8)
            else:
                security = np.random.randint(3, 7)

            # Strategic Fit correlates with business value and age
            if age_tier in ['modern', 'recent'] and business_value >= 7:
                strategic_fit = np.random.randint(7, 11)
            elif age_tier in ['legacy', 'ancient'] or business_value <= 4:
                strategic_fit = np.random.randint(1, 5)
            else:
                strategic_fit = np.random.randint(4, 8)

            # Redundancy: public sector has lots of overlapping systems
            # 30% chance of redundancy
            if random.random() < 0.30:
                redundancy = np.random.randint(1, 4)
            else:
                redundancy = 0

            # Category field
            app_category = category

            # Dependencies (some apps)
            dependencies = ''
            if random.random() < 0.25 and len(applications) > 0:
                num_deps = np.random.randint(1, 3)
                dep_apps = random.sample(applications, min(num_deps, len(applications)))
                dependencies = ', '.join([app['Application Name'] for app in dep_apps])

            # Vendor
            vendor = random.choice(VENDORS)

            # Last Updated
            if age_tier == 'modern':
                months_ago = np.random.randint(1, 12)
            elif age_tier == 'recent':
                months_ago = np.random.randint(12, 36)
            elif age_tier == 'aging':
                months_ago = np.random.randint(36, 72)
            elif age_tier == 'legacy':
                months_ago = np.random.randint(72, 144)
            else:
                months_ago = np.random.randint(144, 240)

            last_updated = f"{months_ago // 12}y {months_ago % 12}m ago" if months_ago >= 12 else f"{months_ago}m ago"

            # Generate contextual comment
            comments = generate_comment(age_tier, business_value, tech_health, redundancy, category)

            app = {
                'Application Name': app_name,
                'Owner': owner,
                'Category': app_category,
                'Business Value': business_value,
                'Tech Health': tech_health,
                'Cost': cost,
                'Usage': usage,
                'Security': security,
                'Strategic Fit': strategic_fit,
                'Redundancy': redundancy,
                'Vendor': vendor,
                'Last Updated': last_updated,
                'Dependencies': dependencies,
                'Composite Score': '',  # Will be calculated
                'Action Recommendation': '',  # Will be calculated
                'Comments': comments
            }

            applications.append(app)
            app_id += 1

    return pd.DataFrame(applications)

def generate_comment(age_tier, business_value, tech_health, redundancy, category):
    """Generate realistic comments based on app characteristics"""

    comments = []

    if age_tier in ['legacy', 'ancient'] and business_value >= 7:
        comments.append("Critical legacy system requiring modernization")
    elif age_tier in ['legacy', 'ancient']:
        comments.append("Legacy application with outdated technology")

    if tech_health <= 3:
        comments.append("Significant technical debt and stability issues")
    elif tech_health >= 8:
        comments.append("Modern platform with good maintainability")

    if redundancy > 0:
        comments.append(f"Overlaps with {redundancy} other system(s)")

    if business_value <= 3:
        comments.append("Limited business value, consider retirement")
    elif business_value >= 9:
        comments.append("Mission-critical application")

    if not comments:
        comments.append(f"Standard {category.lower()} application")

    return " | ".join(comments)

if __name__ == '__main__':
    print("Generating synthetic public sector application portfolio data...")
    print("Target: 220 applications for organization with 100 employees\n")

    # Generate data
    df = generate_realistic_portfolio(220)

    # Shuffle to mix up the ordering
    df = df.sample(frac=1).reset_index(drop=True)

    # Save to CSV
    output_path = '../data/assessment_template.csv'
    df.to_csv(output_path, index=False)

    print(f"[OK] Generated {len(df)} applications")
    print(f"[OK] Saved to {output_path}\n")

    # Print summary statistics
    print("Portfolio Summary:")
    print("=" * 60)
    print(f"Total Applications: {len(df)}")
    print(f"Total Annual Cost: ${df['Cost'].sum():,.0f}")
    print(f"Average Cost per App: ${df['Cost'].mean():,.0f}")
    print(f"Average Business Value: {df['Business Value'].mean():.1f}/10")
    print(f"Average Tech Health: {df['Tech Health'].mean():.1f}/10")
    print(f"Average Security: {df['Security'].mean():.1f}/10")
    print(f"Apps with Redundancy: {len(df[df['Redundancy'] > 0])} ({len(df[df['Redundancy'] > 0])/len(df)*100:.1f}%)")
    print(f"\nTech Health Distribution:")
    print(f"  Excellent (8-10): {len(df[df['Tech Health'] >= 8])} ({len(df[df['Tech Health'] >= 8])/len(df)*100:.1f}%)")
    print(f"  Good (6-7): {len(df[(df['Tech Health'] >= 6) & (df['Tech Health'] < 8)])} ({len(df[(df['Tech Health'] >= 6) & (df['Tech Health'] < 8)])/len(df)*100:.1f}%)")
    print(f"  Fair (4-5): {len(df[(df['Tech Health'] >= 4) & (df['Tech Health'] < 6)])} ({len(df[(df['Tech Health'] >= 4) & (df['Tech Health'] < 6)])/len(df)*100:.1f}%)")
    print(f"  Poor (1-3): {len(df[df['Tech Health'] < 4])} ({len(df[df['Tech Health'] < 4])/len(df)*100:.1f}%)")
    print(f"\nCategory Distribution:")
    for cat in df['Category'].value_counts().head(5).items():
        print(f"  {cat[0]}: {cat[1]} apps")
