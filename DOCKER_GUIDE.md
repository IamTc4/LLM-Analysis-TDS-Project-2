# Docker Build and Run Guide

## Fixed Issues

The following issues in the original Dockerfile have been fixed:

1. ✅ **Playwright Installation Order**: Moved Playwright installation BEFORE switching to non-root user (requires root privileges)
2. ✅ **Python Version Consistency**: Unified to Python 3.11 (removed multi-stage build with conflicting versions)
3. ✅ **System Dependencies**: Added all required X11 libraries for headless Chromium rendering
4. ✅ **Gunicorn Installation**: Added gunicorn to pip install command
5. ✅ **Gunicorn Configuration**: Fixed worker class to use `uvicorn.workers.UvicornWorker` for FastAPI

## Prerequisites

- Docker installed and running
- `.env` file configured with required environment variables

## Build the Docker Image

```bash
docker build -t llm-quiz-solver .
```

This will:
- Install all system dependencies for Playwright/Chromium
- Install Python dependencies including gunicorn
- Install Chromium browser with Playwright
- Copy your application code
- Set up a non-root user for security

## Run the Docker Container

### Option 1: Run with environment file

```bash
docker run -d \
  --name quiz-solver \
  -p 8000:8000 \
  --env-file .env \
  llm-quiz-solver
```

### Option 2: Run with individual environment variables

```bash
docker run -d \
  --name quiz-solver \
  -p 8000:8000 \
  -e STUDENT_EMAIL="your-email@example.com" \
  -e STUDENT_SECRET="your-secret" \
  -e OPENAI_API_KEY="your-openai-key" \
  llm-quiz-solver
```

### Option 3: Run interactively (for debugging)

```bash
docker run -it \
  --name quiz-solver \
  -p 8000:8000 \
  --env-file .env \
  llm-quiz-solver
```

## Verify the Container is Running

```bash
# Check container status
docker ps

# Check logs
docker logs quiz-solver

# Follow logs in real-time
docker logs -f quiz-solver
```

## Test the API

```bash
# Health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/
```

## Common Commands

```bash
# Stop the container
docker stop quiz-solver

# Start the container
docker start quiz-solver

# Restart the container
docker restart quiz-solver

# Remove the container
docker rm quiz-solver

# Remove the image
docker rmi llm-quiz-solver

# View container logs
docker logs quiz-solver

# Execute commands inside the container
docker exec -it quiz-solver bash
```

## Troubleshooting

### Container exits immediately

Check logs:
```bash
docker logs quiz-solver
```

Common issues:
- Missing environment variables
- Port 8000 already in use
- Insufficient memory

### Playwright/Chromium issues

If you see errors related to browser rendering:
```bash
# Rebuild with --no-cache to ensure fresh Playwright installation
docker build --no-cache -t llm-quiz-solver .
```

### Port already in use

```bash
# Find what's using port 8000
netstat -ano | findstr :8000

# Use a different port
docker run -d --name quiz-solver -p 8080:8000 --env-file .env llm-quiz-solver
```

### Check Chromium installation inside container

```bash
docker exec -it quiz-solver bash
playwright --version
chromium --version
```

## Production Deployment

For production, consider:

1. **Use Docker Compose** for easier management
2. **Add health checks** to the Dockerfile
3. **Use secrets management** instead of .env files
4. **Set resource limits** (CPU/memory)
5. **Enable logging to external service**

Example with resource limits:
```bash
docker run -d \
  --name quiz-solver \
  -p 8000:8000 \
  --env-file .env \
  --memory="2g" \
  --cpus="2" \
  llm-quiz-solver
```

## Environment Variables Required

- `STUDENT_EMAIL`: Your student email
- `STUDENT_SECRET`: Your secret key
- `OPENAI_API_KEY`: Your OpenAI API key
- `HOST`: (Optional) Default: 0.0.0.0
- `PORT`: (Optional) Default: 8000
