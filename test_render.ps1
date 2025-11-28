# Quick Render Deployment Diagnostics
# Run this to check your Render service status

Write-Host "`n=== Render Deployment Diagnostics ===" -ForegroundColor Cyan
Write-Host "Service: llm-analysis-tds-project-2-2.onrender.com`n" -ForegroundColor Yellow

$baseUrl = "https://llm-analysis-tds-project-2-2.onrender.com"

# Test 1: Root endpoint
Write-Host "[Test 1] Checking root endpoint..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri $baseUrl -TimeoutSec 60 -ErrorAction Stop
    Write-Host "✅ SUCCESS - Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content.Substring(0, [Math]::Min(200, $response.Content.Length)))" -ForegroundColor Gray
} catch {
    Write-Host "❌ FAILED - Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    }
}

Start-Sleep -Seconds 2

# Test 2: Health endpoint
Write-Host "`n[Test 2] Checking /health endpoint..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/health" -TimeoutSec 60 -ErrorAction Stop
    Write-Host "✅ SUCCESS - Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor Gray
} catch {
    Write-Host "❌ FAILED - Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    }
}

Start-Sleep -Seconds 2

# Test 3: Quiz endpoint (POST)
Write-Host "`n[Test 3] Testing /quiz endpoint..." -ForegroundColor Green
try {
    $body = @{
        email = "23f2005433@ds.study.iitm.ac.in"
        secret = "iamtc"
        url = "https://example.com/test-quiz"
    } | ConvertTo-Json

    $response = Invoke-WebRequest `
        -Uri "$baseUrl/quiz" `
        -Method POST `
        -Body $body `
        -ContentType "application/json" `
        -TimeoutSec 60 `
        -ErrorAction Stop
    
    Write-Host "✅ SUCCESS - Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor Gray
} catch {
    Write-Host "❌ FAILED - Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    }
}

# Summary
Write-Host "`n=== Diagnostic Summary ===" -ForegroundColor Cyan
Write-Host "If all tests passed: ✅ Your service is working!" -ForegroundColor Green
Write-Host "If tests failed with 502/503: ⏳ Service might be starting (wait 30-60s)" -ForegroundColor Yellow
Write-Host "If tests failed with 404: ❌ Check Render dashboard logs" -ForegroundColor Red
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Check Render Dashboard: https://dashboard.render.com" -ForegroundColor White
Write-Host "2. View logs for your service" -ForegroundColor White
Write-Host "3. Verify environment variables are set" -ForegroundColor White
Write-Host "4. See RENDER_TROUBLESHOOTING.md for detailed help`n" -ForegroundColor White
