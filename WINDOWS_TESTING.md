# Windows PowerShell Commands for Testing

## The Problem

On Windows PowerShell, `curl` is an alias for `Invoke-WebRequest`, which has different syntax than the Linux/Mac `curl` command.

---

## Solution 1: Use PowerShell Test Script (EASIEST)

I've created a test script for you: `test_local.ps1`

### Run it:

```powershell
.\test_local.ps1
```

This will:
- ✓ Read your `.env` file automatically
- ✓ Test the health endpoint
- ✓ Test the quiz endpoint with demo
- ✓ Show colored output

---

## Solution 2: Manual PowerShell Commands

If you want to test manually, use these PowerShell commands:

### Test Health Endpoint:

```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -Method GET
```

### Test Quiz Endpoint:

**First, set your credentials** (replace with your actual values):

```powershell
$email = "your.email@example.com"
$secret = "your_secret_here"
```

**Then test the quiz**:

```powershell
$body = @{
    email = $email
    secret = $secret
    url = "https://tds-llm-analysis.s-anand.net/demo"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://127.0.0.1:8000/quiz" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

---

## Solution 3: Install Real Curl (Optional)

If you want to use the Linux-style `curl` commands:

### Install curl:

```powershell
# Using winget
winget install curl.curl

# Or using Chocolatey
choco install curl
```

Then restart PowerShell and the `curl` commands from the guide will work.

---

## Expected Responses

### Health Check Response:

```json
{
  "status": "healthy",
  "config_valid": true,
  "email_configured": true,
  "openai_configured": true
}
```

### Quiz Request Response:

```json
{
  "status": "accepted",
  "message": "Quiz request accepted. Solving quiz at https://tds-llm-analysis.s-anand.net/demo"
}
```

---

## Quick Start

**Easiest way to test**:

```powershell
# 1. Make sure server is running in another terminal
uvicorn app:app --reload

# 2. Run the test script
.\test_local.ps1
```

Done! ✅
