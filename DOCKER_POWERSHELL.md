# Docker Commands for PowerShell (Windows)

## Important: PowerShell vs Bash

PowerShell does **NOT** support backslash `\` for line continuation. Use these single-line commands instead.

## Build the Docker Image

```powershell
docker build -t llm-quiz-solver .
```

## Run the Container

### Option 1: With .env file (Recommended)

```powershell
docker run -d --name quiz-solver -p 8000:8000 --env-file .env llm-quiz-solver
```

### Option 2: With individual environment variables

```powershell
docker run -d --name quiz-solver -p 8000:8000 -e STUDENT_EMAIL="your-email@example.com" -e STUDENT_SECRET="your-secret" -e OPENAI_API_KEY="your-key" llm-quiz-solver
```

### Option 3: Interactive mode (for debugging)

```powershell
docker run -it --name quiz-solver -p 8000:8000 --env-file .env llm-quiz-solver
```

## Multi-line Commands (PowerShell Style)

If you prefer multi-line commands in PowerShell, use backtick `` ` `` (not backslash):

```powershell
docker run -d `
  --name quiz-solver `
  -p 8000:8000 `
  --env-file .env `
  llm-quiz-solver
```

## Common Commands

```powershell
# Check running containers
docker ps

# Check all containers (including stopped)
docker ps -a

# View logs
docker logs quiz-solver

# Follow logs in real-time
docker logs -f quiz-solver

# Stop container
docker stop quiz-solver

# Start container
docker start quiz-solver

# Restart container
docker restart quiz-solver

# Remove container
docker rm quiz-solver

# Remove container (force)
docker rm -f quiz-solver

# Remove image
docker rmi llm-quiz-solver

# Execute bash inside container
docker exec -it quiz-solver bash

# Check container stats
docker stats quiz-solver
```

## Test the API

```powershell
# Health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/

# Or use Invoke-WebRequest (PowerShell native)
Invoke-WebRequest -Uri http://localhost:8000/health
Invoke-WebRequest -Uri http://localhost:8000/
```

## Troubleshooting

### Container exits immediately

```powershell
# Check logs for errors
docker logs quiz-solver

# Check if container exists
docker ps -a
```

### Port already in use

```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Use a different port (map host 8080 to container 8000)
docker run -d --name quiz-solver -p 8080:8000 --env-file .env llm-quiz-solver
```

### Rebuild without cache

```powershell
docker build --no-cache -t llm-quiz-solver .
```

### Clean up everything

```powershell
# Stop and remove container
docker stop quiz-solver
docker rm quiz-solver

# Remove image
docker rmi llm-quiz-solver

# Remove all stopped containers
docker container prune

# Remove all unused images
docker image prune -a
```

## Quick Start (Complete Workflow)

```powershell
# 1. Build the image
docker build -t llm-quiz-solver .

# 2. Run the container
docker run -d --name quiz-solver -p 8000:8000 --env-file .env llm-quiz-solver

# 3. Check if it's running
docker ps

# 4. View logs
docker logs quiz-solver

# 5. Test the API
curl http://localhost:8000/health
```

## Environment Variables Required

Make sure your `.env` file contains:

```
STUDENT_EMAIL=your-email@example.com
STUDENT_SECRET=your-secret
OPENAI_API_KEY=your-openai-api-key
HOST=0.0.0.0
PORT=8000
```
