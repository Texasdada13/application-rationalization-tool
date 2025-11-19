# DEMO CHEAT SHEET - Quick Reference

## PRE-DEMO CHECKLIST

- [ ] Server running at http://localhost:5000
- [ ] Browser open to dashboard
- [ ] PowerShell ready (if doing command-line demo)
- [ ] This cheat sheet visible on second screen

---

## DEMO OPTION 1: AUTOMATED POWERSHELL (8 MIN)

### Run This Command:
```powershell
.\demo_presentation.ps1
```

### What Happens:
1. Auto-runs 12+ NL queries with color output
2. Shows benchmarking results
3. Checks 5 compliance frameworks
4. Creates demo snapshot
5. Opens browser automatically

**Just press Enter after each section and let it run!**

---

## DEMO OPTION 2: BROWSER WALKTHROUGH (10 MIN)

### URL: http://localhost:5000

### Page Flow:
1. **Dashboard** → Show 211 apps, $22.5M cost
2. **Smart Recommendations** → Show 2 retire, 73 modernize, 3 consolidate
3. **Prioritization Roadmap** → Show 4-phase plan
4. **Data Quality** → Show 87/100 score
5. **Compliance** → Show HIPAA 71.1%

---

## KEY NUMBERS TO MENTION

- **211 applications** in portfolio
- **$22.5M** total annual cost
- **$5.4M+** potential savings (24%)
- **60 high-risk** applications
- **71.1%** HIPAA compliance
- **87/100** data quality score
- **15 features** built
- **38+ API endpoints**

---

## NATURAL LANGUAGE QUERIES (COPY/PASTE)

### Quick Test Queries:

**Count:**
```json
{"query": "How many applications do we have?"}
```

**Retirement:**
```json
{"query": "Which applications should we retire?"}
```

**Savings:**
```json
{"query": "How much can we save?"}
```

**Health:**
```json
{"query": "Show me unhealthy applications"}
```

**Recommendations:**
```json
{"query": "What do you recommend?"}
```

---

## POWERSHELL ONE-LINERS (IF ASKED)

### Ask Questions:
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/nl-query/ask" -Method Post -ContentType "application/json" -Body '{"query": "How many applications?"}'
```

### Get Benchmark:
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/benchmark/maturity"
```

### Check HIPAA:
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/risk/compliance/HIPAA"
```

### Get Executive Summary:
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/reports/executive-summary"
```

---

## TALKING POINTS BY SECTION

### Opening (30 sec)
"Enterprise application rationalization tool with AI-powered insights, natural language interface, and compliance tracking for 5 major frameworks."

### Natural Language Processing (1 min)
"Understands 12 types of questions in plain English. No technical expertise needed. Ask questions like 'How much can we save?' and get instant, data-driven answers."

### Smart Recommendations (2 min)
"AI analyzes your portfolio across health, cost, risk, value, and dependencies. Identifies retirement candidates, modernization priorities, and consolidation opportunities automatically."

### Risk & Compliance (2 min)
"Tracks SOX, HIPAA, PCI-DSS, GDPR, and SOC2 compliance. 5-dimensional risk assessment covering technical, business, security, operational, and financial risks."

### Benchmarking (1 min)
"Compares your portfolio against industry standards. Shows maturity level, peer gaps, and provides 16 best practices for improvement."

### Financial Impact (2 min)
"Identified $5.4M in potential savings - that's 24% of the portfolio. TCO breakdown reveals hidden costs in integration complexity, redundancy, and technical debt."

---

## IF SOMETHING BREAKS

### Server Stopped:
```powershell
python web/app.py
```

### Can't Access Browser:
Try: http://127.0.0.1:5000

### PowerShell Script Blocked:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## FEATURES TO HIGHLIGHT

1. Natural Language Query (12 query types)
2. Smart Recommendations (retire/modernize/consolidate)
3. Risk Assessment (5 dimensions)
4. Compliance Tracking (5 frameworks)
5. Industry Benchmarking (maturity levels)
6. Predictive Modeling (6-12 month forecasts)
7. Automated Roadmap (117 prioritized actions)
8. Historical Tracking (snapshots & evolution)
9. Data Quality Validation (12 checks)
10. Advanced Reporting (5 types, 3 formats)

---

## ANSWER COMMON QUESTIONS

**Q: Can it handle our data size?**
A: Yes, handles 211+ apps now, scales to thousands.

**Q: Do we need IT skills?**
A: No, natural language interface for everyone.

**Q: What compliance frameworks?**
A: SOX, HIPAA, PCI-DSS, GDPR, SOC2.

**Q: Can we export reports?**
A: Yes, JSON, Excel, and CSV formats.

**Q: How accurate are recommendations?**
A: Multi-factor scoring across 5 dimensions with data validation.

**Q: Track changes over time?**
A: Yes, snapshot feature for historical comparison.

---

## DEMO TIMING

**Full Demo**: 15 minutes
- PowerShell automation: 8 min
- Browser walkthrough: 5 min
- Q&A: 2 min

**Quick Demo**: 8 minutes
- Browser only: 6 min
- Q&A: 2 min

**Deep Dive**: 20+ minutes
- All features: 15 min
- API demonstration: 5 min
- Q&A: 5+ min

---

## NEXT STEPS (CLOSING)

1. **Data Integration** - Import their real application data
2. **Customization** - Tailor frameworks and scoring
3. **User Access** - Authentication and permissions
4. **Deployment** - Production server setup
5. **Training** - Team onboarding

---

## IMPRESSIVE STATS

**Development:**
- 15 major features
- 8,000+ lines of code
- 38+ API endpoints
- 100% functional testing

**Business Value:**
- $5.4M savings identified
- 60 high-risk apps flagged
- 71.1% compliance measured
- Maturity level assessed

---

## FILES YOU MIGHT NEED

- **Main Demo Script**: `demo_presentation.ps1`
- **Data Generator**: `scripts/populate_demo_data.py`
- **Full Guide**: `DEMO_GUIDE.md`
- **API Docs**: `API_DOCUMENTATION.md`
- **Feature List**: `FEATURE_SUMMARY.md`
- **Screenshot Guide**: `docs/SCREENSHOT_GUIDE.md`

---

## EMERGENCY CONTACTS

**Documentation:**
- DEMO_GUIDE.md - Full presentation guide
- TESTING_GUIDE.md - How to test features
- API_DOCUMENTATION.md - Complete API reference

**Server URL:** http://localhost:5000

**GitHub:** https://github.com/Texasdada13/application-rationalization-tool

---

## FINAL TIPS

1. **Start with PowerShell demo** - most impressive
2. **Let the automation run** - it's designed to impress
3. **Have browser ready** - for visual exploration after
4. **Know the key numbers** - 211 apps, $5.4M savings, 71% compliance
5. **Focus on business value** - not technical details
6. **Demo flows naturally** - automation → browser → Q&A

---

**YOU'VE GOT THIS! The tool is impressive and the demo practically runs itself.**

**Good luck!**
