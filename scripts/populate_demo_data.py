"""
Populate Demo Data for NLP and AI Chat Features
Creates realistic demo scenarios for presentation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")

def test_nl_query(query):
    """Test natural language query"""
    response = requests.post(
        f"{BASE_URL}/api/nl-query/ask",
        json={"query": query}
    )
    result = response.json()['result']
    print(f"Q: {query}")
    print(f"A: {result['answer']}")
    print(f"   {result['details']}\n")
    return result

def save_snapshot(name):
    """Save a portfolio snapshot"""
    response = requests.post(
        f"{BASE_URL}/api/history/save-snapshot",
        json={"snapshot_name": name}
    )
    return response.json()

def ask_ai_chat(question):
    """Ask AI chat a question"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat/ask",
            json={"question": question}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"Q: {question}")
            print(f"A: {data.get('answer', 'Response received')}\n")
            return data
    except Exception as e:
        print(f"AI Chat: {e}")
        return None

def main():
    print_section("DEMO DATA POPULATION SCRIPT")
    print("This script will create demo scenarios for your presentation.\n")

    # Test 1: Natural Language Queries
    print_section("1. NATURAL LANGUAGE QUERY DEMOS")

    demo_queries = [
        "How many applications do we have?",
        "What is the total annual cost?",
        "Show me unhealthy applications",
        "Which applications should we retire?",
        "What apps need modernization?",
        "Show highest risk applications",
        "How much can we save?",
        "What do you recommend?",
        "Show applications in Citizen Services",
        "Which are the most expensive apps?"
    ]

    results = []
    for query in demo_queries:
        result = test_nl_query(query)
        results.append({"query": query, "result": result})
        time.sleep(0.5)

    # Save results for demo
    with open('data/nl_query_demo_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("✅ NL Query demo data saved to: data/nl_query_demo_results.json\n")

    # Test 2: Create Historical Snapshots
    print_section("2. CREATING HISTORICAL SNAPSHOTS")

    snapshots = [
        "Q4 2024 Baseline",
        "January 2025 Review",
        "Post-Rationalization"
    ]

    for snapshot_name in snapshots:
        result = save_snapshot(snapshot_name)
        if result.get('success'):
            print(f"✅ Created snapshot: {snapshot_name}")
        time.sleep(1)

    # Test 3: AI Chat Demos
    print_section("3. AI CHAT CONVERSATION DEMOS")

    chat_questions = [
        "What is the overall health of our portfolio?",
        "Which department has the highest costs?",
        "What are the biggest risks in our portfolio?",
        "Give me a summary of retirement candidates",
        "How does our portfolio compare to industry standards?"
    ]

    for question in chat_questions:
        ask_ai_chat(question)
        time.sleep(0.5)

    # Test 4: Generate Reports
    print_section("4. GENERATING DEMO REPORTS")

    print("Generating Executive Summary...")
    response = requests.get(f"{BASE_URL}/api/reports/executive-summary")
    if response.status_code == 200:
        print("✅ Executive Summary generated")

    print("Generating Benchmark Report...")
    response = requests.get(f"{BASE_URL}/api/benchmark/report")
    if response.status_code == 200:
        data = response.json()
        benchmark = data['benchmark']
        print(f"✅ Benchmark Report generated")
        print(f"   Maturity Level: {benchmark['maturity_assessment']['maturity_level']}")
        print(f"   Overall Score: {benchmark['executive_summary']['overall_score']}/100")

    print("\nGenerating Risk Assessment...")
    response = requests.get(f"{BASE_URL}/api/risk/assess-portfolio")
    if response.status_code == 200:
        data = response.json()
        metrics = data['assessment']['portfolio_metrics']
        print(f"✅ Risk Assessment generated")
        print(f"   Total Apps: {metrics['total_applications']}")
        print(f"   Avg Risk: {metrics['avg_risk_score']}/100")
        print(f"   High Risk Apps: {len(data['assessment']['high_risk_apps'])}")

    # Test 5: Compliance Checks
    print_section("5. COMPLIANCE ASSESSMENTS")

    frameworks = ['SOX', 'HIPAA', 'PCI-DSS', 'GDPR', 'SOC2']

    for framework in frameworks:
        response = requests.get(f"{BASE_URL}/api/risk/compliance/{framework}")
        if response.status_code == 200:
            data = response.json()
            comp = data['compliance']
            print(f"{framework}:")
            print(f"   Compliance Rate: {comp['compliance_rate']}%")
            print(f"   Status: {comp['recommendation']}\n")

    # Summary
    print_section("DEMO DATA READY!")

    print("✅ All demo scenarios created successfully!\n")
    print("PRESENTATION TALKING POINTS:\n")
    print("1. Natural Language Queries:")
    print("   - Show how users can ask questions in plain English")
    print("   - Demo 10 different query types")
    print("   - Instant answers with detailed explanations\n")

    print("2. Historical Tracking:")
    print("   - 3 snapshots created showing portfolio evolution")
    print("   - Compare before/after scenarios")
    print("   - Track ROI realization over time\n")

    print("3. AI Chat:")
    print("   - Conversational interface for insights")
    print("   - Context-aware responses")
    print("   - Natural interaction\n")

    print("4. Risk Assessment:")
    print("   - Multi-dimensional risk scoring")
    print("   - Compliance tracking across 5 frameworks")
    print("   - Mitigation recommendations\n")

    print("5. Benchmarking:")
    print("   - Industry comparison")
    print("   - Maturity assessment")
    print("   - Best practices guidance\n")

    print("=" * 60)
    print("Demo data location: data/nl_query_demo_results.json")
    print("View in browser: http://localhost:5000")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo data population cancelled by user.")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        print("Make sure the server is running on http://localhost:5000")
