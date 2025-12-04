# Documentation Generation Prompt for Your Projects

Use this prompt with Claude to generate comprehensive, professional documentation for any software project. This prompt was developed based on the documentation created for the Application Rationalization Tool.

---

## The Prompt

```
I need you to create comprehensive, professional documentation for my software project. Please analyze my codebase and create the following documentation suite:

## Core Documentation to Create:

### 1. Enhanced README.md
Create a detailed, professional README that includes:
- Project overview with clear value proposition
- Live demo link (if applicable) and portfolio project context
- Table of contents with anchor links
- Feature highlights with NEW badges for recent additions
- Installation instructions (prerequisites, setup steps, virtual environment)
- Quick start guide (minimal steps to get running)
- Detailed usage section with CLI commands and examples
- Assessment/scoring criteria with tables
- Project structure diagram
- Advanced usage examples (programmatic usage, batch processing)
- Customization guide
- Troubleshooting section
- Support and contributing information
- Technology stack acknowledgments
- Version, author, and license information
- "About This Project" section highlighting demonstrated skills

### 2. FEATURE_CATALOG.md
Create a comprehensive feature inventory:
- Executive summary with platform statistics
- Organized by functional categories
- Each feature should include:
  - Feature name and description
  - What it does (clear explanation)
  - Key capabilities (bullet points)
  - Use cases (specific scenarios)
  - Technical specifications where relevant
- Use case breakdowns by user persona
- Technology stack details
- System requirements
- Data limits and capabilities
- Complete document inventory

### 3. Detailed Guides (docs/ folder)
Create individual markdown files for:
- **workflow.md**: Step-by-step process flows and procedures
- **configuration_guide.md**: How to configure and customize the system
- **[domain]_methodology.md**: Detailed methodology documentation (e.g., scoring, assessment)
- **[framework]_guide.md**: Framework implementation guides (e.g., TIME framework)
- **visualization_guide.md**: If applicable, how to use visualization features
- **integration_guide.md**: If applicable, third-party integrations

### 4. User Guides and References
- **DEMO_GUIDE.md**: How to demonstrate the system to others
- **DEMO_CHEAT_SHEET.md**: Quick reference for demos
- **TESTING_GUIDE.md**: How to test the system
- **API_DOCUMENTATION.md**: If applicable, API reference

### 5. Strategic Documents
- **PITCH_AND_VALUE_PROPOSITION.md**:
  - Why this tool exists
  - Problems it solves
  - Target audience and personas
  - Value proposition for each persona
  - Competitive advantages
  - Use case scenarios
  - ROI and business case
  - Implementation approach
  - Success metrics

- **PROJECT_PLAN_TEMPLATE.md**:
  - Project phases and timeline
  - Deliverables by phase
  - Resource requirements
  - Risk assessment
  - Success criteria
  - Communication plan

### 6. Templates and Examples (if applicable)
- Excel/CSV data input templates
- Sample data files
- Configuration examples
- Code usage examples

### 7. Project Status and Roadmap
- **PROJECT_STATUS.md**: Current state, completed features, known issues
- **FUTURE_ENHANCEMENTS.md**: Roadmap and planned features
- **SESSION_COMPLETION_SUMMARY.md**: Major milestones achieved

### 8. Supporting Documents
- **PRESENTATION_READY.md**: Slide deck outline or presentation guide
- **FEATURE_SUMMARY.md**: One-page feature overview
- **CONTRIBUTING.md**: How others can contribute

## Documentation Style Guidelines:

### Formatting
- Use clear headings (##, ###, ####)
- Include tables for structured data
- Use code blocks with language specifications
- Add bullet points and numbered lists
- Include examples and code snippets
- Use emojis sparingly for visual markers (NEW!, 🎨, 📊)

### Content Quality
- Write in professional, technical but accessible language
- Include specific use cases and scenarios
- Provide concrete examples, not just theory
- Add "Why this matters" context
- Include both basic and advanced usage
- Anticipate user questions

### Structure
- Start with executive summary or overview
- Organize by user journey or functional area
- Include navigation (TOC, links)
- End with next steps or summary
- Cross-reference related documents

### Technical Details
- Include installation/setup prerequisites
- Provide command-line examples with output
- Show both CLI and programmatic usage
- Document configuration options
- Include troubleshooting section
- Note version requirements

## Additional Outputs:

### Excel/CSV Templates (if applicable)
Create data input templates with:
- Pre-formatted columns
- Sample data
- Data validation rules
- Clear instructions

### Project Plan (Excel)
Create detailed project plan with:
- Timeline (Gantt-style)
- Milestones and deliverables
- Resource allocation
- Dependency tracking

### Word Document Versions
For key documents that need professional formatting:
- Create .docx versions of main markdown files
- Ensure proper formatting and styling
- Include table of contents
- Use consistent heading styles

## Analysis to Perform First:

1. **Codebase Analysis**
   - Identify all features and capabilities
   - Map out user personas
   - Document architecture and tech stack
   - Identify configuration options
   - Note integration points

2. **User Journey Mapping**
   - Map typical workflows
   - Identify pain points addressed
   - Document use cases by role
   - Create scenario walkthroughs

3. **Value Proposition**
   - Identify problems solved
   - Articulate unique capabilities
   - Define target audience
   - Document competitive advantages

## Quality Checklist:

Before finalizing, ensure each document:
- [ ] Has clear purpose and audience
- [ ] Includes concrete examples
- [ ] Uses consistent formatting
- [ ] Has proper navigation
- [ ] Cross-references related docs
- [ ] Includes troubleshooting/FAQs
- [ ] Has actionable next steps
- [ ] Uses professional tone
- [ ] Is technically accurate
- [ ] Provides value to multiple personas

## Deliverable Format:

1. Create all markdown files in appropriate directories
2. Use consistent naming conventions
3. Include a master documentation index
4. Create both .md and .docx versions of key documents
5. Generate any Excel templates needed
6. Ensure all cross-references work
7. Test all code examples

Please analyze my project thoroughly and create this comprehensive documentation suite. Ask me questions if you need clarification about:
- Target audience and use cases
- Key features to highlight
- Technical architecture details
- Deployment/hosting information
- Competitive landscape
```

---

## How to Use This Prompt

### Step 1: Prepare Your Project
Make sure your codebase is organized and has:
- Clear file structure
- Code comments where needed
- A basic README (can be minimal)
- Working examples or sample data

### Step 2: Start a New Claude Conversation
Open Claude Code or Claude.ai and paste the prompt above.

### Step 3: Provide Context
After pasting the prompt, provide:
```
Project Name: [Your Project Name]
Project Type: [Web App / CLI Tool / Library / API / etc.]
Primary Language: [Python / JavaScript / etc.]
Main Purpose: [Brief description of what it does]

Additional Context:
- [Any specific documentation needs]
- [Target audience details]
- [Unique features to highlight]
```

### Step 4: Answer Follow-up Questions
Claude will likely ask clarifying questions about:
- Your target users
- Key features and workflows
- Technical architecture
- Business context
- Deployment details

### Step 5: Review and Iterate
- Review generated documentation
- Request revisions or additions
- Ask for specific sections to be expanded
- Request different formats (PDF, DOCX, etc.)

### Step 6: Generate Supporting Materials
After the main documentation, ask Claude to:
```
"Now create Excel templates for data input"
"Generate a PowerPoint outline from the pitch deck"
"Create .docx versions of the main documentation files"
"Create a one-page executive summary"
```

---

## Example Follow-up Requests

Once the initial documentation is created, you can refine it:

```
"Make the README more concise for quick scanning"
"Add more code examples to the advanced usage section"
"Create a comparison table showing our advantages vs competitors"
"Generate a FAQ section based on common use cases"
"Add diagrams showing the workflow process"
"Create a quick start checklist"
"Add screenshots placeholders with descriptions"
"Make the pitch deck more compelling for C-level executives"
```

---

## Tips for Best Results

1. **Be Specific About Audience**: Tell Claude who will read each document
2. **Provide Examples**: Share similar projects or documentation you admire
3. **Iterate**: Don't expect perfection on first try - refine iteratively
4. **Test Instructions**: Actually follow the README to ensure it works
5. **Keep It Updated**: Re-run sections when features change
6. **Brand It**: Add your branding, logos, contact info after generation
7. **Use Templates**: Ask Claude to create reusable templates for future projects

---

## Documentation Maintenance

After initial creation, use this follow-up prompt periodically:

```
"I've added [new features]. Please update:
1. The README feature list
2. The FEATURE_CATALOG
3. Any relevant guides
4. The FUTURE_ENHANCEMENTS (move completed items to current)

Maintain the same style and format as existing documentation."
```

---

## Customization Options

Adjust the prompt based on project type:

### For Open Source Projects
Add: "Include CONTRIBUTING.md, CODE_OF_CONDUCT.md, and detailed issue templates"

### For Commercial Products
Add: "Include pricing tiers, ROI calculator, and sales enablement materials"

### For APIs/Libraries
Add: "Focus heavily on API documentation, code examples, and integration guides"

### For Internal Tools
Add: "Include runbooks, deployment procedures, and support escalation guides"

---

## Success Metrics

Good documentation should:
- ✅ Enable a new user to get started in < 10 minutes
- ✅ Answer 80% of common questions without support
- ✅ Clearly articulate value proposition
- ✅ Provide both beginner and advanced content
- ✅ Include working code examples
- ✅ Be scannable (headings, bullets, tables)
- ✅ Look professional and credible
- ✅ Support multiple user personas

---

## What Makes This Approach Effective

Based on the Application Rationalization Tool documentation:

1. **Comprehensive Coverage**: Every aspect documented, from installation to advanced features
2. **Multiple Formats**: Markdown, Word, Excel - whatever users need
3. **User-Centric**: Organized by persona and use case, not just features
4. **Professional Polish**: Tables, examples, proper formatting throughout
5. **Strategic Value**: Not just "how" but "why" - business case included
6. **Actionable**: Every document has clear next steps
7. **Discoverable**: Good navigation, TOC, cross-references
8. **Maintained**: Living documentation that evolves with the project

---

## Final Note

This documentation approach transforms a good project into a portfolio-ready, professional showcase. It demonstrates:
- Technical writing ability
- User empathy and UX thinking
- Business acumen (pitch, value prop)
- Attention to detail
- Professional standards

Invest the time in documentation - it's often what differentiates amateur projects from professional ones.
