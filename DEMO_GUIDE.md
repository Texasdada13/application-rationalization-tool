# DEMO GUIDE - Application Rationalization Tool

## Quick Start for Your Presentation

**Server Status**: Running at http://localhost:5000

**Demo Duration**: 10-15 minutes

---

## Option 1: Live PowerShell Demo (Recommended)

This gives a dramatic, automated demonstration of the NLP and AI features.

### Steps:

1. Open PowerShell in the project directory:
   ```powershell
   cd C:\Users\dada_\OneDrive\Documents\application-rationalization-tool
   ```

2. Run the demo script:
   ```powershell
   .\demo_presentation.ps1
   ```

3. Watch as it automatically:
   - Asks 12+ natural language questions
   - Shows AI-powered answers with color coding
   - Demonstrates industry benchmarking
   - Checks compliance for 5 frameworks (SOX, HIPAA, PCI-DSS, GDPR, SOC2)
   - Creates a demo snapshot
   - Opens the web dashboard automatically

### What You'll See:

**Section 1: Basic Portfolio Insights**
- Q: "How many applications do we have?"
- A: 211 applications

**Section 2: Decision Support**
- Q: "Which applications should we retire?"
- A: Shows retirement candidates with savings

**Section 3: Financial Analysis**
- Q: "How much can we save?"
- A: $5.4M+ potential savings

**Section 4: Compliance Assessment**
- Shows compliance rates for all 5 frameworks
- Color-coded results (Green = Good, Yellow = Warning, Red = Critical)

---

## Option 2: Browser Walkthrough (Interactive)

Best for showing the visual interface and exploring features interactively.

### Open the Dashboard:
http://localhost:5000

### Demo Flow (10 minutes):

**1. Dashboard Overview (2 min)**
- Show portfolio summary: 211 applications, $22.5M cost
- Point out key metrics: Health score, Business value
- Show the Predictive Modeling section with cost/risk predictions

**2. Smart Recommendations (2 min)**
- Navigate to "Smart Recommendations" page
- Show:
  - 2 retirement candidates
  - 73 modernization priorities
  - 3 consolidation opportunities (Citizen Services, Finance, IT Infrastructure)

**3. Prioritization Roadmap (2 min)**
- Navigate to "Prioritization Roadmap"
- Show the multi-phase plan:
  - Quick Wins
  - Short-term actions
  - Medium-term strategies
  - Long-term initiatives
- Highlight effort vs impact matrix

**4. Data Quality Dashboard (2 min)**
- Navigate to "Data Quality"
- Show quality score: 87/100
- Demonstrate the 12 validation checks
- Show recommendations for improvement

**5. Compliance Tracking (2 min)**
- Navigate to "Compliance" page
- Show framework tracking
- Demonstrate compliance assessment for HIPAA (71.1%)
- Show non-compliant applications

---

## Option 3: Natural Language Query Demo

Best for showcasing the AI/NLP capabilities in real-time.

### Using PowerShell (Quick Commands):

Open PowerShell and try these one at a time:

```powershell
# Ask about the portfolio
Invoke-RestMethod -Uri "http://localhost:5000/api/nl-query/ask" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"query": "How many applications do we have?"}'
```

```powershell
# Ask about retirement
Invoke-RestMethod -Uri "http://localhost:5000/api/nl-query/ask" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"query": "Which applications should we retire?"}'
```

```powershell
# Ask about savings
Invoke-RestMethod -Uri "http://localhost:5000/api/nl-query/ask" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"query": "How much can we save?"}'
```

```powershell
# Ask about health
Invoke-RestMethod -Uri "http://localhost:5000/api/nl-query/ask" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"query": "Show me unhealthy applications"}'
```

---

## Key Talking Points for Your Demo

### 1. Natural Language Processing
- "The tool understands natural language queries - you don't need to learn complex commands"
- "It can answer 12 different types of questions about your portfolio"
- "The AI contextualizes answers based on your actual data"

### 2. AI-Powered Recommendations
- "The Smart Recommendations engine analyzes applications across multiple dimensions"
- "It identifies retirement candidates, modernization priorities, and consolidation opportunities"
- "All recommendations are backed by data-driven scoring"

### 3. Risk & Compliance
- "We track compliance against 5 major frameworks: SOX, HIPAA, PCI-DSS, GDPR, SOC2"
- "The risk assessment uses 5 dimensions: Technical, Business, Security, Operational, Financial"
- "Currently showing 71.1% HIPAA compliance with 150 out of 211 apps compliant"

### 4. Industry Benchmarking
- "The tool compares your portfolio against industry standards"
- "Maturity assessment shows you're at 'Repeatable' level with room to grow"
- "We provide 16 best practices across 4 categories"

### 5. Financial Analysis
- "Total portfolio cost: $22.5M annually"
- "Identified $5.4M+ in potential savings (24% of portfolio)"
- "TCO breakdown shows hidden costs in integration complexity, redundancy, and tech debt"

### 6. Historical Tracking
- "You can create snapshots to track portfolio evolution over time"
- "Compare before/after to measure ROI realization"
- "Track which decisions led to actual savings"

---

## Demo Data Available

The tool currently has:
- 211 applications loaded
- $22.56M total annual cost
- 60 high-risk applications identified
- 8-15 retirement candidates (depending on criteria)
- 73 modernization priorities
- 3 consolidation groups
- 1 saved snapshot: "Test Snapshot 1"

---

## Features to Highlight

### What Makes This Tool Special:

1. **Natural Language Interface** - Non-technical users can ask questions in plain English

2. **AI-Powered Insights** - Machine learning analyzes patterns and makes recommendations

3. **Multi-Framework Compliance** - Track 5 major compliance frameworks simultaneously

4. **Industry Benchmarking** - See how you compare to peers

5. **Predictive Modeling** - Forecast costs and risks 6-12 months ahead

6. **Automated Roadmap** - Multi-phase action plan with 117 prioritized actions

7. **Data Quality Validation** - 12 automated checks ensure data integrity

8. **What-If Analysis** - Test scenarios before making decisions

9. **Historical Tracking** - Measure progress over time

10. **Comprehensive Reporting** - 5 report types, 3 export formats (JSON, Excel, CSV)

---

## Common Questions & Answers

**Q: Can it handle our data?**
A: Yes, it currently handles 211+ applications and can scale to thousands.

**Q: Do we need technical expertise to use it?**
A: No, the natural language interface allows anyone to ask questions in plain English.

**Q: What frameworks do you support for compliance?**
A: SOX, HIPAA, PCI-DSS, GDPR, and SOC2 with automated checking.

**Q: Can we export reports?**
A: Yes, all reports can be exported as JSON, Excel, or CSV.

**Q: How accurate are the recommendations?**
A: Recommendations use multi-factor scoring across health, cost, risk, value, and dependencies.

**Q: Can we track changes over time?**
A: Yes, the historical tracking feature lets you create snapshots and compare portfolio evolution.

---

## If Something Goes Wrong

### Server Not Running:
```powershell
cd C:\Users\dada_\OneDrive\Documents\application-rationalization-tool
python web/app.py
```

### Can't Access Browser:
Make sure you're going to: http://localhost:5000

### PowerShell Script Won't Run:
You might need to enable script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## After the Demo

**Next Steps to Discuss:**

1. **Data Integration** - How to import their actual application data
2. **Customization** - Tailoring compliance frameworks and scoring
3. **User Access** - Setting up authentication and permissions
4. **Deployment** - Moving from localhost to production server
5. **Training** - Onboarding their team to use the tool

---

## Quick Reference: All Natural Language Queries

The system understands these types of questions:

1. "How many applications do we have?"
2. "What is the total annual cost?"
3. "What is the average health score?"
4. "Which applications should we retire?"
5. "What apps need modernization?"
6. "Show me the highest risk applications"
7. "How much can we save?"
8. "Which are the most expensive apps?"
9. "Show me unhealthy applications"
10. "Show high-value applications"
11. "What do you recommend?"
12. "Show applications in [category]"

---

## Estimated Demo Timeline

**Full Demo (15 minutes)**:
- Run PowerShell demo script: 8 minutes
- Browse web interface: 5 minutes
- Q&A: 2 minutes

**Quick Demo (8 minutes)**:
- Browser walkthrough only: 6 minutes
- Q&A: 2 minutes

**Technical Deep Dive (20+ minutes)**:
- PowerShell demo: 8 minutes
- Browser features: 7 minutes
- API demonstration: 5 minutes
- Q&A: 5+ minutes

---

## Success Metrics to Mention

**Development**:
- 15 major features built
- 38+ API endpoints
- 8,000+ lines of code
- 100% functional testing complete

**Business Value**:
- $5.4M+ savings identified (24% of portfolio)
- 60 high-risk applications flagged
- 71.1% compliance rate measured
- Portfolio maturity assessed

---

**Good luck with your presentation!**

For any issues, refer to:
- [TESTING_GUIDE.md](TESTING_GUIDE.md)
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- [FEATURE_SUMMARY.md](FEATURE_SUMMARY.md)
