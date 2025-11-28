# Test All Quiz URLs with Deployed API
# This script tests your Render deployment with real quiz URLs

Write-Host "`n=== Testing All Quiz URLs ===" -ForegroundColor Cyan
Write-Host "API Endpoint: https://llm-analysis-tds-project-2-2.onrender.com/solve" -ForegroundColor Yellow
Write-Host ""

$apiUrl = "https://llm-analysis-tds-project-2-2.onrender.com/solve"
$email = "23f2005433@ds.study.iitm.ac.in"
$secret = "iamtc"

# Quiz URLs to test
$quizUrls = @(
    "https://p2testingone.vercel.app/q1.html",
    "https://tds-llm-analysis.s-anand.net/demo",
    "https://tds-llm-analysis.s-anand.net/demo2",
    "https://tdsbasictest.vercel.app/quiz/1"
)

$successCount = 0
$failCount = 0
$results = @()

# First, wake up the service with a health check
Write-Host "[Warming up] Waking up the service..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri "https://llm-analysis-tds-project-2-2.onrender.com/health" -TimeoutSec 60 | Out-Null
    Write-Host "  Service is awake" -ForegroundColor Green
    Write-Host ""
    Start-Sleep -Seconds 2
} catch {
    Write-Host "  Service might be sleeping, continuing anyway..." -ForegroundColor Yellow
    Write-Host ""
}

foreach ($quizUrl in $quizUrls) {
    Write-Host "[Testing] $quizUrl" -ForegroundColor Green
    
    try {
        $body = @{
            email = $email
            secret = $secret
            url = $quizUrl
        } | ConvertTo-Json

        # Increased timeout to 60 seconds for sleeping service
        $response = Invoke-WebRequest -Uri $apiUrl -Method POST -Body $body -ContentType "application/json" -TimeoutSec 60 -ErrorAction Stop
        
        Write-Host "  SUCCESS - Status: $($response.StatusCode)" -ForegroundColor Green
        $content = $response.Content | ConvertFrom-Json
        Write-Host "  Response: $($content.message)" -ForegroundColor Gray
        Write-Host ""
        $successCount++
        
        $results += [PSCustomObject]@{
            URL = $quizUrl
            Status = "PASSED"
            Message = $content.message
        }
        
        # Wait a bit between requests
        Start-Sleep -Seconds 2
        
    } catch {
        Write-Host "  FAILED - Error: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            Write-Host "  Status Code: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
        }
        Write-Host ""
        $failCount++
        
        $results += [PSCustomObject]@{
            URL = $quizUrl
            Status = "FAILED"
            Message = $_.Exception.Message
        }
    }
}

# Summary
Write-Host ""
Write-Host "=== Test Summary ===" -ForegroundColor Cyan
Write-Host "Total Tests: $($quizUrls.Count)" -ForegroundColor White
Write-Host "Passed: $successCount" -ForegroundColor Green
Write-Host "Failed: $failCount" -ForegroundColor Red
Write-Host ""

Write-Host "=== Detailed Results ===" -ForegroundColor Cyan
$results | Format-Table -AutoSize -Wrap

if ($successCount -eq $quizUrls.Count) {
    Write-Host ""
    Write-Host "ALL TESTS PASSED! Your API is working perfectly!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your API endpoint is ready to use:" -ForegroundColor Green
    Write-Host "https://llm-analysis-tds-project-2-2.onrender.com/quiz" -ForegroundColor Yellow
} elseif ($successCount -gt 0) {
    Write-Host ""
    Write-Host "Some tests passed, some failed." -ForegroundColor Yellow
    Write-Host "This might be due to:" -ForegroundColor Yellow
    Write-Host "  - Service was sleeping (free tier sleeps after 15 min)" -ForegroundColor Gray
    Write-Host "  - Network timeout" -ForegroundColor Gray
    Write-Host "  - Quiz URL might be invalid or unreachable" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Try running the script again - service should be awake now." -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "ALL TESTS FAILED. Check your API endpoint and credentials." -ForegroundColor Red
}

Write-Host ""
Write-Host "Important Notes:" -ForegroundColor Cyan
Write-Host "  - Quiz solving happens asynchronously in the background" -ForegroundColor White
Write-Host "  - 200 status means request was accepted, not that quiz is solved" -ForegroundColor White
Write-Host "  - Check Render logs to see actual quiz solving progress" -ForegroundColor White
Write-Host "  - Free tier sleeps after 15 min - first request takes ~30 sec" -ForegroundColor White
Write-Host ""
