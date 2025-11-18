# Application Rationalization Assessment Tool – Workflow Documentation

## Overview

This tool guides organizations through a robust process to inventory, evaluate, score, and rationalize their application portfolio, supporting digital transformation initiatives.

---

## Step-by-Step Workflow

### 1. Inventory Applications
- Gather all active software applications into the `assessment_template.csv` (in /data).
- For each application, collect basic metadata:
  - Application Name
  - Owner
  - Business Unit
  - Core Functionality/Purpose
  - Technology Stack
  - Dependencies
  - Cost
  - Usage Stats
  - Security/Compliance Status

### 2. Define Assessment Criteria
- Work with stakeholders to finalize evaluation criteria (see template: Business Value, Tech Health, Cost, Usage, Security, Strategic Fit, Redundancy).
- Assign a weight to each criterion according to business priorities if desired.

### 3. Score Applications
- For each application, score on a scale of 1–5 (or as appropriate) for each assessment criterion.
- Enter rationale or comments for context where needed.

### 4. Run Assessment Tool
- Use `main.py` to ingest the assessment CSV, calculate composite scores, apply scoring logic.
- The tool will:
  - Normalize and weight scores
  - Generate a composite score for each application
  - Recommend an action (e.g., Retain, Modernize, Retire, Replace) based on scoring framework

### 5. Visualize & Export Results
- Review results and recommendations in the terminal output or exported CSV.
- Import exported results into BI tools (e.g., Power BI, Excel) for heatmaps, dashboards, and visualization.

### 6. Develop Roadmap & Take Action
- Use recommendations to create a phased action plan for rationalization.
- Track progress, update statuses as changes are made, and iterate assessment over time.

---

## Appendix

- **assessment_template.csv:** Sample spreadsheet format for portfolio input.
- **main.py:** Python script for scoring and recommendations.
- **requirements.txt:** Python dependencies for running the tool.
- **/tests:** Add any unit or functional tests as you expand the project.
