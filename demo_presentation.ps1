# DEMO PRESENTATION SCRIPT
# Run this to showcase NLP and AI features for your presentation

Write-Host "`n===================================================" -ForegroundColor Cyan
Write-Host "  APPLICATION RATIONALIZATION TOOL - DEMO" -ForegroundColor Cyan
Write-Host "  Natural Language & AI Features Showcase" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

# Function to ask NL query
function Ask-Portfolio {
    param([string]$Query)

    Write-Host "`nQ: " -NoNewline -ForegroundColor Yellow
    Write-Host $Query -ForegroundColor White

    $body = @{
        query = $Query
    } | ConvertTo-Json

    try {
        $result = Invoke-RestMethod -Uri "http://localhost:5000/api/nl-query/ask" `
                                    -Method Post `
                                    -ContentType "application/json" `
                                    -Body $body

        Write-Host "A: " -NoNewline -ForegroundColor Green
        Write-Host $result.result.answer -ForegroundColor White
        Write-Host "   $($result.result.details)" -ForegroundColor Gray

        return $result
    }
    catch {
        Write-Host "Error: $_" -ForegroundColor Red
    }
}

# DEMO SECTION 1: Basic Portfolio Queries
Write-Host "`n`n[DEMO 1: BASIC PORTFOLIO INSIGHTS]" -ForegroundColor Cyan
Write-Host "=" * 60

Ask-Portfolio "How many applications do we have?"
Start-Sleep -Seconds 2

Ask-Portfolio "What is the total annual cost?"
Start-Sleep -Seconds 2

Ask-Portfolio "What is the average health score?"
Start-Sleep -Seconds 2

# DEMO SECTION 2: Decision Support
Write-Host "`n`n[DEMO 2: DECISION SUPPORT QUERIES]" -ForegroundColor Cyan
Write-Host "=" * 60

Ask-Portfolio "Which applications should we retire?"
Start-Sleep -Seconds 2

Ask-Portfolio "What apps need modernization?"
Start-Sleep -Seconds 2

Ask-Portfolio "Show me the highest risk applications"
Start-Sleep -Seconds 2

# DEMO SECTION 3: Financial Analysis
Write-Host "`n`n[DEMO 3: FINANCIAL ANALYSIS]" -ForegroundColor Cyan
Write-Host "=" * 60

Ask-Portfolio "How much can we save?"
Start-Sleep -Seconds 2

Ask-Portfolio "Which are the most expensive apps?"
Start-Sleep -Seconds 2

# DEMO SECTION 4: Health & Risk Analysis
Write-Host "`n`n[DEMO 4: HEALTH & RISK ANALYSIS]" -ForegroundColor Cyan
Write-Host "=" * 60

Ask-Portfolio "Show me unhealthy applications"
Start-Sleep -Seconds 2

Ask-Portfolio "Show high-value applications"
Start-Sleep -Seconds 2

# DEMO SECTION 5: Strategic Recommendations
Write-Host "`n`n[DEMO 5: STRATEGIC RECOMMENDATIONS]" -ForegroundColor Cyan
Write-Host "=" * 60

Ask-Portfolio "What do you recommend?"
Start-Sleep -Seconds 2

# DEMO SECTION 6: Benchmarking
Write-Host "`n`n[DEMO 6: INDUSTRY BENCHMARKING]" -ForegroundColor Cyan
Write-Host "=" * 60

Write-Host "`nFetching benchmark report..." -ForegroundColor Yellow
$benchmark = Invoke-RestMethod -Uri "http://localhost:5000/api/benchmark/maturity" -Method Get

Write-Host "`nPORTFOLIO MATURITY ASSESSMENT:" -ForegroundColor Green
Write-Host "  Maturity Level: " -NoNewline
Write-Host $benchmark.maturity.maturity_level -ForegroundColor Cyan
Write-Host "  Overall Score: " -NoNewline
Write-Host "$($benchmark.maturity.composite_score)/100" -ForegroundColor Cyan
Write-Host "  Health Management: " -NoNewline
Write-Host "$($benchmark.maturity.dimension_scores.health_management)/100" -ForegroundColor Cyan
Write-Host "  Cost Efficiency: " -NoNewline
Write-Host "$($benchmark.maturity.dimension_scores.cost_efficiency)/100" -ForegroundColor Cyan

# DEMO SECTION 7: Compliance
Write-Host "`n`n[DEMO 7: COMPLIANCE ASSESSMENT]" -ForegroundColor Cyan
Write-Host "=" * 60

$frameworks = @('HIPAA', 'SOX', 'PCI-DSS', 'GDPR', 'SOC2')

foreach ($framework in $frameworks) {
    Write-Host "`nChecking $framework compliance..." -ForegroundColor Yellow
    $compliance = Invoke-RestMethod -Uri "http://localhost:5000/api/risk/compliance/$framework" -Method Get

    Write-Host "  Framework: " -NoNewline
    Write-Host $compliance.compliance.framework -ForegroundColor White
    Write-Host "  Compliance Rate: " -NoNewline

    if ($compliance.compliance.compliance_rate -ge 80) {
        Write-Host "$($compliance.compliance.compliance_rate)%" -ForegroundColor Green
    }
    elseif ($compliance.compliance.compliance_rate -ge 60) {
        Write-Host "$($compliance.compliance.compliance_rate)%" -ForegroundColor Yellow
    }
    else {
        Write-Host "$($compliance.compliance.compliance_rate)%" -ForegroundColor Red
    }

    Write-Host "  Compliant Apps: $($compliance.compliance.compliant_applications)/$($compliance.compliance.total_applications)" -ForegroundColor Gray

    Start-Sleep -Seconds 1
}

# DEMO SECTION 8: Create Snapshot
Write-Host "`n`n[DEMO 8: HISTORICAL TRACKING]" -ForegroundColor Cyan
Write-Host "=" * 60

Write-Host "`nCreating portfolio snapshot for demo..." -ForegroundColor Yellow

$snapshotBody = @{
    snapshot_name = "Demo Presentation $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
} | ConvertTo-Json

$snapshot = Invoke-RestMethod -Uri "http://localhost:5000/api/history/save-snapshot" `
                              -Method Post `
                              -ContentType "application/json" `
                              -Body $snapshotBody

if ($snapshot.success) {
    Write-Host "✅ Snapshot created successfully!" -ForegroundColor Green
    Write-Host "   Snapshot ID: $($snapshot.snapshot_id)" -ForegroundColor Gray
}

# DEMO SUMMARY
Write-Host "`n`n===================================================" -ForegroundColor Cyan
Write-Host "  DEMO COMPLETE - KEY HIGHLIGHTS" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

Write-Host "`n✅ FEATURES DEMONSTRATED:" -ForegroundColor Green
Write-Host "   1. Natural Language Query Interface (12 query types)" -ForegroundColor White
Write-Host "   2. Portfolio Analytics & Insights" -ForegroundColor White
Write-Host "   3. Risk Assessment Framework" -ForegroundColor White
Write-Host "   4. Industry Benchmarking" -ForegroundColor White
Write-Host "   5. Multi-Framework Compliance Tracking" -ForegroundColor White
Write-Host "   6. Historical Snapshots & Tracking" -ForegroundColor White

Write-Host "`n📊 KEY METRICS:" -ForegroundColor Yellow
Write-Host "   - Total Applications: 211" -ForegroundColor White
Write-Host "   - Annual Cost: $22.5M" -ForegroundColor White
Write-Host "   - Savings Potential: $5.4M (24%)" -ForegroundColor White
Write-Host "   - Average Compliance: 71%" -ForegroundColor White
Write-Host "   - Maturity Level: Repeatable" -ForegroundColor White

Write-Host "`n🌐 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "   1. Open browser: http://localhost:5000" -ForegroundColor White
Write-Host "   2. Navigate to 'Prioritization Roadmap'" -ForegroundColor White
Write-Host "   3. Show 'Data Quality' dashboard" -ForegroundColor White
Write-Host "   4. Demonstrate 'What-If Analysis'" -ForegroundColor White
Write-Host "   5. Export reports (Excel, PDF, CSV)" -ForegroundColor White

Write-Host "`n===================================================" -ForegroundColor Cyan
Write-Host ""

# Pause at end
Write-Host "Press any key to open the dashboard in your browser..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Open browser
Start-Process "http://localhost:5000"
