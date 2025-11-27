# Test Script for Windows PowerShell
# This script tests your LLM Analysis Quiz API endpoint

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Testing LLM Analysis Quiz API" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Read environment variables from .env file
Write-Host "Reading .env file..." -ForegroundColor Yellow
$envFile = Get-Content .env
$email = ($envFile | Select-String "STUDENT_EMAIL=").ToString().Split("=")[1]
$secret = ($envFile | Select-String "STUDENT_SECRET=").ToString().Split("=")[1]

Write-Host "Email: $email" -ForegroundColor Green
Write-Host "Secret: $secret" -ForegroundColor Green
Write-Host ""

# Test 1: Health Check
Write-Host "Test 1: Health Check" -ForegroundColor Yellow
Write-Host "GET http://127.0.0.1:8000/health" -ForegroundColor Gray
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -Method GET
    Write-Host "Success: Health check passed!" -ForegroundColor Green
    Write-Host $response.Content -ForegroundColor White
} catch {
    Write-Host "Failed: Health check failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
Write-Host ""

# Test 2: Quiz Endpoint with Demo
Write-Host "Test 2: Quiz Endpoint (Demo)" -ForegroundColor Yellow
Write-Host "POST http://127.0.0.1:8000/quiz" -ForegroundColor Gray

$body = @{
    email = $email
    secret = $secret
    url = "https://tds-llm-analysis.s-anand.net/demo"
} | ConvertTo-Json

Write-Host "Request body:" -ForegroundColor Gray
Write-Host $body -ForegroundColor White
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/quiz" -Method POST -ContentType "application/json" -Body $body
    
    Write-Host "Success: Quiz request accepted!" -ForegroundColor Green
    Write-Host $response.Content -ForegroundColor White
    Write-Host ""
    Write-Host "Watch the server logs to see the quiz being solved..." -ForegroundColor Cyan
} catch {
    Write-Host "Failed: Quiz request failed!" -ForegroundColor Red
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "All tests passed!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
