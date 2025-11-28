# Render Deployment Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: 502 Bad Gateway / Not Found Errors

**Symptoms:**
- `curl https://your-service.onrender.com/health` returns "Not Found"
- POST requests return "502 Bad Gateway"

**Possible Causes:**

#### 1. Service is Still Building/Starting
Render deployments take 10-15 minutes for first build.

**Check:**
- Go to Render Dashboard → Your Service
- Look at "Events" tab - should show "Deploy succeeded"
- Look at "Logs" tab - should show gunicorn workers starting

**Wait for logs to show:**
```
[INFO] Starting gunicorn
[INFO] Listening at: http://0.0.0.0:8000
[INFO] Booting worker with pid: X
[INFO] Application startup complete.
```

#### 2. Port Configuration Issue
Render expects your app to bind to `0.0.0.0:$PORT` (Render sets PORT env var).

**Fix in Dockerfile:**
Make sure CMD uses port 8000 (or reads from $PORT):
```dockerfile
CMD ["gunicorn", "-c", "gunicorn_conf.py", "app:app"]
```

**Fix in gunicorn_conf.py:**
```python
import os
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
```

#### 3. Missing Environment Variables
Check all required env vars are set in Render.

**Required Variables:**
- `STUDENT_EMAIL`
- `STUDENT_SECRET`
- `OPENAI_API_KEY`
- `HOST=0.0.0.0`
- `PORT=8000` (optional, Render sets this)

**How to Check:**
1. Go to Render Dashboard → Your Service
2. Click "Environment" tab
3. Verify all variables are present

#### 4. Health Check Path Wrong
Render might be checking wrong health path.

**Fix:**
1. Go to Service Settings
2. Set "Health Check Path" to `/health` or `/`
3. Save changes

#### 5. Service on Free Tier Sleeping
Free tier services sleep after 15 minutes of inactivity.

**Symptoms:**
- First request takes 30+ seconds
- Returns 502 initially, then works

**Solution:**
- Wait 30-60 seconds and try again
- Service will wake up automatically

---

## Step-by-Step Troubleshooting

### Step 1: Check Render Dashboard

1. Go to https://dashboard.render.com
2. Click on your service: `llm-analysis-tds-project-2-2`
3. Check the status indicator (should be green "Live")

### Step 2: Check Build Logs

1. Click "Logs" tab
2. Look for errors during build
3. Common errors:
   - `playwright install` failing → Missing system dependencies
   - `pip install` failing → Check requirements.txt
   - Port binding errors → Check gunicorn config

### Step 3: Check Runtime Logs

Look for these success messages:
```
[INFO] Starting gunicorn 23.0.0
[INFO] Listening at: http://0.0.0.0:8000
[INFO] Using worker: uvicorn.workers.UvicornWorker
[INFO] Booting worker with pid: 7
[INFO] Started server process [7]
[INFO] Application startup complete.
Configuration validated successfully
```

### Step 4: Check Environment Variables

1. Click "Environment" tab
2. Verify all variables are set correctly
3. Click "Save Changes" if you made updates

### Step 5: Manual Redeploy

If service is stuck:
1. Click "Manual Deploy" → "Deploy latest commit"
2. Wait for build to complete (10-15 minutes)
3. Check logs again

---

## Testing Your Deployed Service

### Test 1: Basic Connectivity
```powershell
# Should return HTML or JSON, not "Not Found"
curl https://llm-analysis-tds-project-2-2.onrender.com/
```

### Test 2: Health Check
```powershell
# Should return: {"status":"healthy",...}
curl https://llm-analysis-tds-project-2-2.onrender.com/health
```

### Test 3: Quiz Endpoint
```powershell
$body = @{
    email = "23f2005433@ds.study.iitm.ac.in"
    secret = "iamtc"
    url = "https://example.com/quiz"
} | ConvertTo-Json

Invoke-WebRequest -Uri "https://llm-analysis-tds-project-2-2.onrender.com/quiz" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

**Expected Response:**
```json
{
  "status": "accepted",
  "message": "Quiz request accepted. Solving quiz at https://example.com/quiz"
}
```

---

## Common Render-Specific Fixes

### Fix 1: Update gunicorn_conf.py for Render

Render sets the PORT environment variable dynamically.

**Current gunicorn_conf.py:**
```python
import multiprocessing
import os

# Bind to Render's PORT or default to 8000
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# Worker configuration
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"

# Timeout settings
timeout = 300
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
```

### Fix 2: Add render.yaml (Optional)

Create `render.yaml` in your repo root:

```yaml
services:
  - type: web
    name: llm-quiz-solver
    env: docker
    region: oregon
    plan: free
    healthCheckPath: /health
    envVars:
      - key: STUDENT_EMAIL
        sync: false
      - key: STUDENT_SECRET
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: HOST
        value: 0.0.0.0
      - key: PORT
        value: 8000
```

### Fix 3: Verify Dockerfile Exposes Correct Port

Your Dockerfile should have:
```dockerfile
EXPOSE 8000
CMD ["gunicorn", "-c", "gunicorn_conf.py", "app:app"]
```

---

## If Service Won't Start

### Check Render Logs for These Errors:

**Error: "Address already in use"**
- Fix: Make sure gunicorn binds to `0.0.0.0:8000`

**Error: "playwright: command not found"**
- Fix: Ensure `playwright install` runs in Dockerfile

**Error: "ModuleNotFoundError: No module named 'email_validator'"**
- Fix: Ensure `email-validator` is in requirements.txt

**Error: "Worker timeout"**
- Fix: Increase timeout in gunicorn_conf.py

---

## Quick Diagnostic Commands

Run these in Render's Shell (if available):

```bash
# Check if gunicorn is running
ps aux | grep gunicorn

# Check port binding
netstat -tlnp | grep 8000

# Test locally within container
curl http://localhost:8000/health

# Check environment variables
env | grep STUDENT
```

---

## Still Not Working?

1. **Share Render Logs**: Copy the full logs from Render dashboard
2. **Check Service Status**: Is it showing "Live" or "Failed"?
3. **Try Local Docker**: Does `docker run` work locally?
4. **Verify GitHub Sync**: Is latest code pushed to GitHub?

---

## Alternative: Test with Local Tunnel (ngrok)

If Render isn't working, you can temporarily expose your local Docker:

```powershell
# Install ngrok
choco install ngrok

# Start your local container
docker run -d --name quiz-solver -p 8000:8000 --env-file .env llm-quiz-solver

# Expose to internet
ngrok http 8000
```

This gives you a temporary public URL like: `https://abc123.ngrok.io`
