# Advanced Reporting - Quick Start Guide

**Status**: ✅ Ready to Use
**Server**: http://localhost:5000

---

## 📊 Quick Downloads (Browser)

### From Reports Page
Navigate to: **http://localhost:5000/reports**

Click any download button:
- **CSV Export** → Raw data
- **Excel Report** → Workbook with charts
- **PDF Report** → Executive summary
- **PowerPoint** → 7-slide presentation

---

## 🚀 Direct Download Links

### Excel Report (with Charts)
```
http://localhost:5000/api/reports/export/executive_summary/excel
```
**Contains**: 7 worksheets, 3 charts, professional formatting

### PDF Report
```
http://localhost:5000/api/reports/export/executive_summary/pdf
```
**Contains**: Multi-page executive summary with charts

### PowerPoint Presentation
```
http://localhost:5000/api/reports/export/executive_summary/powerpoint
```
**Contains**: 7 professional slides with embedded charts

### JSON Export
```
http://localhost:5000/api/reports/export/executive_summary/json
```
**Contains**: Complete report data in JSON format

### CSV Summary
```
http://localhost:5000/api/reports/export/executive_summary/csv
```
**Contains**: Key metrics in CSV format

---

## 📧 Email Reports (PowerShell)

### Send PDF via Email

```powershell
$emailConfig = @{
    report_type = "executive_summary"
    recipients = @("manager@company.com")
    format = "pdf"
    smtp_host = "smtp.gmail.com"
    smtp_port = 587
    use_tls = $true
    smtp_username = "your-email@gmail.com"
    smtp_password = "your-app-password"
    from_email = "noreply@company.com"
    subject = "Application Portfolio Report - " + (Get-Date -Format "yyyy-MM-dd")
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/reports/email" `
    -Method Post `
    -ContentType "application/json" `
    -Body $emailConfig
```

### Send PowerPoint via Email

```powershell
# Same as above, just change format:
$emailConfig = @{
    # ...
    format = "powerpoint"  # Changed from "pdf"
    # ...
}
```

### Send Excel via Email

```powershell
# Same as above, just change format:
$emailConfig = @{
    # ...
    format = "excel"  # Changed from "pdf"
    # ...
}
```

---

## 📋 All Report Types

You can generate any report type in any format:

1. **executive_summary** - C-suite overview
2. **financial_analysis** - Cost analysis
3. **technical_deep_dive** - Technical details
4. **risk_compliance** - Risk & compliance
5. **roadmap_strategy** - Action plan

**Examples**:
```
/api/reports/export/financial_analysis/pdf
/api/reports/export/technical_deep_dive/excel
/api/reports/export/risk_compliance/powerpoint
```

---

## 🎨 What's in Each Format

### Excel Report (7 Worksheets)
1. **Summary** - Key metrics with formatting
2. **Category Breakdown** - With cost bar chart
3. **Health Distribution** - With pie chart
4. **Top Risks** - Top 10 risk applications
5. **Recommendations** - Strategic actions
6. **Top 10 Expensive** - With bar chart
7. **Full Portfolio** - Complete application data

### PDF Report (Multi-page)
1. **Title Page** - Report title and timestamp
2. **Executive Summary** - Key metrics table
3. **Health Distribution** - Pie chart
4. **Top Risks** - Top 5 applications table
5. **Recommendations** - Detailed actions (page 2)

### PowerPoint (7 Slides)
1. **Title Slide** - Report title and timestamp
2. **Executive Summary** - Key metrics bullets
3. **Health Distribution** - Pie chart
4. **Top Risks** - Top 5 applications
5. **Recommendations** - Strategic actions
6. **Cost Breakdown** - Bar chart
7. **Next Steps** - Action items

---

## 🔍 Check Export Capabilities

```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/reports/capabilities"
```

**Expected Response**:
```json
{
  "success": true,
  "capabilities": {
    "json": true,
    "csv": true,
    "excel": true,
    "excel_with_charts": true,
    "pdf": true,
    "powerpoint": true,
    "email": true
  }
}
```

All should be `true` if libraries are installed correctly.

---

## 📥 Download via PowerShell

### Save Excel Report
```powershell
Invoke-WebRequest `
    -Uri "http://localhost:5000/api/reports/export/executive_summary/excel" `
    -OutFile "portfolio_report.xlsx"
```

### Save PDF Report
```powershell
Invoke-WebRequest `
    -Uri "http://localhost:5000/api/reports/export/executive_summary/pdf" `
    -OutFile "portfolio_report.pdf"
```

### Save PowerPoint
```powershell
Invoke-WebRequest `
    -Uri "http://localhost:5000/api/reports/export/executive_summary/powerpoint" `
    -OutFile "portfolio_report.pptx"
```

---

## ⚙️ SMTP Configuration Examples

### Gmail (with App Password)
```powershell
smtp_host = "smtp.gmail.com"
smtp_port = 587
use_tls = $true
smtp_username = "your-email@gmail.com"
smtp_password = "your-16-char-app-password"
```

**Gmail Setup**:
1. Enable 2FA on your Google account
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use the 16-character password

### Microsoft 365
```powershell
smtp_host = "smtp.office365.com"
smtp_port = 587
use_tls = $true
smtp_username = "your-email@company.com"
smtp_password = "your-password"
```

### SendGrid
```powershell
smtp_host = "smtp.sendgrid.net"
smtp_port = 587
use_tls = $true
smtp_username = "apikey"
smtp_password = "your-sendgrid-api-key"
```

### Custom SMTP Server
```powershell
smtp_host = "mail.company.com"
smtp_port = 587
use_tls = $true
smtp_username = "alerts@company.com"
smtp_password = "your-password"
```

---

## 🚨 Troubleshooting

### "ModuleNotFoundError: No module named 'reportlab'"

**Solution**:
```bash
pip install reportlab python-pptx
```

### "SMTP Authentication Error"

**Solutions**:
- Verify username/password are correct
- Enable "Less secure app access" (Gmail)
- Use App Password instead of account password
- Check firewall allows port 587/465

### "File Download Fails"

**Solutions**:
- Check server is running: http://localhost:5000
- Check data is loaded (211 applications)
- Check browser console for errors
- Try direct download link

### "Charts Not Showing in Excel"

**Causes**:
- openpyxl not installed correctly
- Using older Excel version

**Solutions**:
```bash
pip install --upgrade openpyxl
```

---

## 💡 Tips & Best Practices

### For Presentations
- Use **PowerPoint** format for board meetings
- Use **PDF** for email distribution
- Use **Excel** for detailed analysis

### For Regular Updates
- Schedule weekly PDF emails to management
- Monthly PowerPoint for executive reviews
- Daily Excel for operations team

### For Analysis
- Download **Excel** for pivot tables and custom charts
- Export **JSON** for custom scripting
- Export **CSV** for database imports

---

## 📊 Demo Script

**Quick 3-Minute Demo**:

1. Open browser: http://localhost:5000/reports
2. Click **"Download Excel"**
3. Open Excel file, show 7 worksheets and charts
4. Go back, click **"Download PDF"**
5. Open PDF, show executive summary and charts
6. Go back, click **"Download PowerPoint"**
7. Open PowerPoint, flip through 7 slides

**Talking Points**:
- "One-click downloads for all formats"
- "Excel includes 3 embedded charts"
- "PDF is board-ready with professional layout"
- "PowerPoint auto-generates 7 slides"
- "Can also email reports automatically"

---

## 🎯 Common Use Cases

### Weekly Executive Update
```powershell
# Email PDF to executives every Friday
$emailConfig = @{
    report_type = "executive_summary"
    recipients = @("ceo@company.com", "cfo@company.com", "cto@company.com")
    format = "pdf"
    subject = "Weekly Application Portfolio Update"
    # ... SMTP config ...
}
```

### Monthly Board Presentation
```powershell
# Download PowerPoint for board meeting
Invoke-WebRequest `
    -Uri "http://localhost:5000/api/reports/export/executive_summary/powerpoint" `
    -OutFile "Board_Meeting_$(Get-Date -Format 'yyyy-MM').pptx"
```

### Quarterly Financial Review
```powershell
# Generate financial analysis Excel
Invoke-WebRequest `
    -Uri "http://localhost:5000/api/reports/export/financial_analysis/excel" `
    -OutFile "Q$(Get-Date -Format 'q')_Financial_Analysis.xlsx"
```

### Risk Assessment Report
```powershell
# Email risk report to security team
$emailConfig = @{
    report_type = "risk_compliance"
    recipients = @("security-team@company.com")
    format = "pdf"
    subject = "Application Risk Assessment - $(Get-Date -Format 'MMMM yyyy')"
    # ... SMTP config ...
}
```

---

## 📚 Related Documentation

- **Implementation Details**: [ADVANCED_REPORTING_IMPLEMENTATION.md](ADVANCED_REPORTING_IMPLEMENTATION.md)
- **API Documentation**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Feature Summary**: [FEATURE_SUMMARY.md](FEATURE_SUMMARY.md)
- **Demo Guide**: [DEMO_GUIDE.md](DEMO_GUIDE.md)

---

## ✅ Quick Verification

Test that everything works:

```powershell
# 1. Check capabilities
Invoke-RestMethod -Uri "http://localhost:5000/api/reports/capabilities"

# 2. Download Excel
Invoke-WebRequest -Uri "http://localhost:5000/api/reports/export/executive_summary/excel" -OutFile "test.xlsx"

# 3. Download PDF
Invoke-WebRequest -Uri "http://localhost:5000/api/reports/export/executive_summary/pdf" -OutFile "test.pdf"

# 4. Download PowerPoint
Invoke-WebRequest -Uri "http://localhost:5000/api/reports/export/executive_summary/powerpoint" -OutFile "test.pptx"

# 5. Open files to verify
Start-Process "test.xlsx"
Start-Process "test.pdf"
Start-Process "test.pptx"
```

If all files open correctly, **you're ready to go!**

---

**Quick Start Complete! 🎉**

For advanced usage, see [ADVANCED_REPORTING_IMPLEMENTATION.md](ADVANCED_REPORTING_IMPLEMENTATION.md)
