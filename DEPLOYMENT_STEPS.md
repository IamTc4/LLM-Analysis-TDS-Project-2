# Deployment Guide - Getting Your Public API Endpoint

## Current Status
✅ Docker container working locally at `http://localhost:8000`
❌ Need public URL for quiz platform to access

## Deployment Options

### Option 1: Render.com (Recommended - Free Tier)

**Steps:**

1. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub

2. **Connect Your Repository**
   - Push your code to GitHub (if not already)
   - In Render dashboard, click "New +" → "Web Service"
   - Connect your GitHub repository

3. **Configure the Service**
   - **Name**: `llm-quiz-solver` (or any name)
   - **Environment**: Docker
   - **Region**: Choose closest to you
   - **Branch**: main
   - **Dockerfile Path**: `./Dockerfile`

4. **Add Environment Variables**
   Click "Advanced" and add:
   ```
   STUDENT_EMAIL=23f2005433@ds.study.iitm.ac.in
   STUDENT_SECRET=iamtc
   OPENAI_API_KEY=eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjIwMDU0MzNAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.AR8-lJLQwDDfk10M-yZhs6fYabhY-foJirVQE3NTpEQ
   HOST=0.0.0.0
   PORT=8000
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait 10-15 minutes for build
   - Your public URL will be: `https://your-service-name.onrender.com`

6. **Your API Endpoint**
   ```
   https://your-service-name.onrender.com/quiz
   ```

**Free Tier Limitations:**
- Service sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- 750 hours/month free

---

### Option 2: Railway.app (Easy, Paid after trial)

**Steps:**

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables (same as above)
6. Railway auto-detects Dockerfile and deploys
7. Get your URL: `https://your-app.railway.app`

**Pricing:**
- $5 credit free trial
- ~$5-10/month after

---

### Option 3: Fly.io (Good for Docker)

**Steps:**

1. Install Fly CLI:
   ```powershell
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. Login:
   ```powershell
   fly auth login
   ```

3. Launch app:
   ```powershell
   fly launch
   ```

4. Set environment variables:
   ```powershell
   fly secrets set STUDENT_EMAIL="23f2005433@ds.study.iitm.ac.in"
   fly secrets set STUDENT_SECRET="iamtc"
   fly secrets set OPENAI_API_KEY="eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjIwMDU0MzNAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.AR8-lJLQwDDfk10M-yZhs6fYabhY-foJirVQE3NTpEQ"
   ```

5. Deploy:
   ```powershell
   fly deploy
   ```

6. Your URL: `https://your-app.fly.dev`

**Free Tier:**
- 3 shared-cpu VMs
- 3GB storage

---

### Option 4: Google Cloud Run (Scalable, Pay-as-you-go)

**Steps:**

1. Install Google Cloud SDK
2. Build and push to Google Container Registry:
   ```powershell
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/llm-quiz-solver
   ```

3. Deploy:
   ```powershell
   gcloud run deploy llm-quiz-solver `
     --image gcr.io/YOUR_PROJECT_ID/llm-quiz-solver `
     --platform managed `
     --region us-central1 `
     --allow-unauthenticated `
     --set-env-vars STUDENT_EMAIL="...",STUDENT_SECRET="...",OPENAI_API_KEY="..."
   ```

4. Your URL: `https://llm-quiz-solver-xxxxx-uc.a.run.app`

**Pricing:**
- Free tier: 2 million requests/month
- Pay only for actual usage

---

## Quick Test After Deployment

Once deployed, test your public endpoint:

```powershell
# Health check
curl https://your-public-url.com/health

# Test quiz endpoint
$body = @{
    email = "23f2005433@ds.study.iitm.ac.in"
    secret = "iamtc"
    url = "https://example.com/quiz"
} | ConvertTo-Json

Invoke-WebRequest -Uri "https://your-public-url.com/quiz" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

---

## Recommended: Start with Render.com

**Why?**
- ✅ Free tier available
- ✅ Auto-deploys from GitHub
- ✅ Built-in SSL certificates
- ✅ Easy environment variable management
- ✅ Good for Docker deployments
- ✅ No credit card required for free tier

**Your Final API Endpoint will be:**
```
https://your-service-name.onrender.com/quiz
```

This is the URL you'll share with the quiz platform!
