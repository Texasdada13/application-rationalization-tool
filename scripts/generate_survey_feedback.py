"""
Generate realistic stakeholder survey feedback for sentiment analysis
Creates survey responses with varied sentiment for 211 applications
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Read the current application portfolio
df_apps = pd.read_csv('../data/assessment_template.csv')

# Sentiment patterns based on app characteristics
POSITIVE_FEEDBACK = [
    "This application works great and has everything we need",
    "Very reliable and easy to use - saves us a lot of time",
    "Love this system! It's intuitive and fast",
    "Excellent tool that has significantly improved our workflow",
    "Works perfectly, no complaints whatsoever",
    "Great application - modern interface and reliable performance",
    "Really helpful tool, very user-friendly",
    "Fantastic system, makes my job much easier",
    "Impressed with the functionality and ease of use",
    "Best application we have - couldn't do without it",
    "Very efficient and well-designed",
    "Outstanding tool that delivers real value",
    "Clean interface and powerful features",
    "Solid application that just works",
    "Appreciate how reliable and fast this is"
]

NEUTRAL_FEEDBACK = [
    "It works fine, does what it needs to do",
    "Gets the job done, nothing special",
    "Adequate for our needs but could be better",
    "Functional but a bit outdated",
    "Works okay most of the time",
    "Not great but not terrible either",
    "Does the basic functions we need",
    "It's fine, no major issues",
    "Average tool, meets minimum requirements",
    "Could use some improvements but manageable",
    "Basic functionality works, missing some features",
    "Acceptable for now, considering alternatives",
    "It works but feels dated",
    "Serviceable but not ideal",
    "Middle of the road - neither good nor bad"
]

NEGATIVE_PERFORMANCE = [
    "Extremely slow - takes forever to load anything",
    "System is painfully slow and frequently times out",
    "Performance is terrible, constantly laggy",
    "Takes 5+ minutes just to log in, completely unacceptable",
    "So slow it's almost unusable during peak hours",
    "Freezes constantly, have to restart multiple times daily",
    "Loading times are ridiculous, kills productivity"
]

NEGATIVE_USABILITY = [
    "Interface is confusing and not intuitive at all",
    "Way too complicated for what it should do",
    "Very difficult to navigate, poor user experience",
    "Clunky interface makes simple tasks take forever",
    "Unnecessarily complex, needs complete redesign",
    "User interface from the 1990s - desperately needs update",
    "Confusing workflow that makes no sense"
]

NEGATIVE_RELIABILITY = [
    "Crashes multiple times per week, very unreliable",
    "System goes down frequently, can't count on it",
    "Constantly broken, always reporting issues",
    "Data integrity issues - can't trust the information",
    "Frequent errors and unexpected behavior",
    "Too many bugs, feels like it's never been tested",
    "Downtime is unacceptable for a critical system"
]

NEGATIVE_FEATURES = [
    "Missing basic features we desperately need",
    "Lacks essential functionality for our work",
    "Outdated - doesn't integrate with anything modern",
    "Can't do half of what we need, very limited",
    "Missing critical features that competitors have",
    "Functionality is bare-bones and inadequate",
    "Needs major feature updates to be useful"
]

NEGATIVE_GENERAL = [
    "Terrible application, looking for replacement ASAP",
    "Waste of money - should retire this immediately",
    "Nightmare to use, causes daily frustration",
    "Absolutely hate this system, it's awful",
    "Worst application in our portfolio",
    "Horrible experience every time I have to use it",
    "Complete disaster - retire it now"
]

NEGATIVE_COST = [
    "Way too expensive for what little value it provides",
    "Not worth the cost - should find cheaper alternative",
    "Overpriced and underperforming",
    "Costs too much for how rarely we use it",
    "Budget drain with minimal return on investment"
]

# Stakeholder roles
ROLES = [
    'End User', 'Department Manager', 'IT Staff', 'Executive',
    'Business Analyst', 'Administrator', 'Support Staff',
    'Team Lead', 'Director', 'Supervisor'
]

def generate_feedback_for_app(app_row):
    """Generate realistic feedback based on app characteristics"""

    app_name = app_row['Application Name']
    tech_health = app_row['Tech Health']
    business_value = app_row['Business Value']
    cost = app_row['Cost']

    # Determine sentiment based on app characteristics
    # Tech health heavily influences sentiment
    if tech_health >= 8:
        # High tech health = mostly positive
        sentiment_weights = [0.70, 0.20, 0.10]  # [positive, neutral, negative]
    elif tech_health >= 6:
        # Good tech health = mixed but positive-leaning
        sentiment_weights = [0.45, 0.40, 0.15]
    elif tech_health >= 4:
        # Fair tech health = mostly neutral/negative
        sentiment_weights = [0.15, 0.35, 0.50]
    else:
        # Poor tech health = mostly negative
        sentiment_weights = [0.05, 0.15, 0.80]

    # Adjust based on business value
    if business_value >= 8:
        # High value apps get more feedback (people care)
        num_responses = np.random.randint(8, 15)
    elif business_value >= 5:
        num_responses = np.random.randint(4, 8)
    else:
        num_responses = np.random.randint(1, 4)

    feedback_list = []

    for _ in range(num_responses):
        # Determine sentiment for this response
        sentiment = np.random.choice(['positive', 'neutral', 'negative'], p=sentiment_weights)

        # Generate feedback text based on sentiment
        if sentiment == 'positive':
            comment = random.choice(POSITIVE_FEEDBACK)

        elif sentiment == 'neutral':
            comment = random.choice(NEUTRAL_FEEDBACK)

        else:  # negative
            # Choose type of negative feedback based on app issues
            negative_types = []

            if tech_health <= 3:
                negative_types.extend(NEGATIVE_PERFORMANCE * 2)  # Weight performance complaints
                negative_types.extend(NEGATIVE_RELIABILITY * 2)

            if tech_health <= 5:
                negative_types.extend(NEGATIVE_USABILITY)
                negative_types.extend(NEGATIVE_FEATURES)

            # High cost apps get cost complaints
            if cost > 100000:
                negative_types.extend(NEGATIVE_COST)

            # Always include general negative
            negative_types.extend(NEGATIVE_GENERAL)

            comment = random.choice(negative_types)

        # Generate response metadata
        role = random.choice(ROLES)

        # Date within last 6 months
        days_ago = np.random.randint(1, 180)
        response_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')

        # Rating (1-5 scale correlates with sentiment)
        if sentiment == 'positive':
            rating = np.random.randint(4, 6)  # 4 or 5
        elif sentiment == 'neutral':
            rating = 3
        else:
            rating = np.random.randint(1, 3)  # 1 or 2

        feedback_list.append({
            'Application Name': app_name,
            'Respondent Role': role,
            'Rating': rating,
            'Comment': comment,
            'Date': response_date,
            'Sentiment': sentiment.capitalize()
        })

    return feedback_list

def generate_survey_data():
    """Generate complete survey dataset"""

    all_feedback = []

    print("Generating stakeholder survey feedback...")
    print(f"Processing {len(df_apps)} applications\n")

    for idx, app_row in df_apps.iterrows():
        feedback = generate_feedback_for_app(app_row)
        all_feedback.extend(feedback)

        if (idx + 1) % 50 == 0:
            print(f"  Processed {idx + 1}/{len(df_apps)} applications...")

    df_feedback = pd.DataFrame(all_feedback)

    # Shuffle
    df_feedback = df_feedback.sample(frac=1).reset_index(drop=True)

    return df_feedback

if __name__ == '__main__':
    print("=" * 70)
    print("Stakeholder Survey Feedback Generator")
    print("Public Sector Application Portfolio")
    print("=" * 70)
    print()

    # Generate feedback
    df_survey = generate_survey_data()

    # Save to CSV
    output_path = '../data/stakeholder_survey.csv'
    df_survey.to_csv(output_path, index=False)

    print()
    print("[OK] Generated survey feedback")
    print(f"[OK] Saved to {output_path}\n")

    # Print summary statistics
    print("Survey Summary:")
    print("=" * 70)
    print(f"Total Responses: {len(df_survey)}")
    print(f"Applications Covered: {df_survey['Application Name'].nunique()}")
    print(f"Average Responses per App: {len(df_survey) / df_survey['Application Name'].nunique():.1f}")
    print()

    print("Sentiment Distribution:")
    sentiment_counts = df_survey['Sentiment'].value_counts()
    for sentiment, count in sentiment_counts.items():
        pct = (count / len(df_survey)) * 100
        print(f"  {sentiment}: {count} ({pct:.1f}%)")
    print()

    print("Rating Distribution:")
    rating_counts = df_survey['Rating'].value_counts().sort_index()
    for rating, count in rating_counts.items():
        pct = (count / len(df_survey)) * 100
        stars = '*' * rating + '-' * (5 - rating)
        print(f"  {rating} [{stars}]: {count} ({pct:.1f}%)")
    print()

    print("Top Respondent Roles:")
    role_counts = df_survey['Respondent Role'].value_counts().head(5)
    for role, count in role_counts.items():
        print(f"  {role}: {count} responses")
    print()

    # Sample feedback
    print("Sample Feedback:")
    print("-" * 70)
    sample = df_survey.sample(5)
    for idx, row in sample.iterrows():
        sentiment_label = {'Positive': '[+]', 'Neutral': '[=]', 'Negative': '[-]'}[row['Sentiment']]
        print(f"{sentiment_label} [{row['Application Name']}] - {row['Respondent Role']}")
        print(f"   Rating: {row['Rating']}/5")
        print(f"   \"{row['Comment']}\"")
        print()
