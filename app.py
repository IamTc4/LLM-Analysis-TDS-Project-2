"""FastAPI application for LLM Analysis Quiz endpoint."""
import sys
import asyncio
import logging
from contextlib import asynccontextmanager

# Fix for Windows + Playwright: Enforce ProactorEventLoopPolicy
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, ValidationError

import config
from quiz_solver import QuizSolver

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the app."""
    # Startup
    try:
        config.validate_config()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")

# Initialize FastAPI app
app = FastAPI(
    title="LLM Analysis Quiz API",
    description="API endpoint for solving data analysis quizzes",
    version="1.0.0",
    lifespan=lifespan
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class QuizRequest(BaseModel):
    email: EmailStr
    secret: str
    url: str

# Response model
class QuizResponse(BaseModel):
    status: str
    message: str

@app.post("/quiz", response_model=QuizResponse)
async def handle_quiz(request: Request):
    """
    Handle incoming quiz requests with manual JSON parsing.
    
    Args:
        request: Raw Request object for manual JSON parsing
        
    Returns:
        QuizResponse with status and message
        
    Raises:
        HTTPException: 400 for invalid JSON, 403 for invalid credentials
    """
    # Step 1: Catch invalid JSON BEFORE validation
    try:
        data = await request.json()
    except Exception as e:
        logger.error(f"JSON parsing error: {e}")
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid JSON payload"}
        )
    
    logger.info(f"Received quiz request for URL: {data.get('url')}")
    
    # Step 2: Validate required fields manually
    email = data.get("email")
    secret = data.get("secret")
    url = data.get("url")
    
    missing_fields = []
    if not email:
        missing_fields.append("email")
    if not secret:
        missing_fields.append("secret")
    if not url:
        missing_fields.append("url")
    
    if missing_fields:
        logger.warning(f"Missing required fields: {', '.join(missing_fields)}")
        return JSONResponse(
            status_code=400,
            content={"detail": f"Missing required fields: {', '.join(missing_fields)}"}
        )
    
    # Step 3: Verify credentials
    if email != config.STUDENT_EMAIL:
        logger.warning(f"Invalid email: {email}")
        raise HTTPException(status_code=403, detail="Invalid email")
    
    if secret != config.STUDENT_SECRET:
        logger.warning("Invalid secret")
        raise HTTPException(status_code=403, detail="Invalid secret")
    
    # Step 4: Start quiz solver asynchronously (don't wait for completion)
    asyncio.create_task(solve_quiz_async(url))
    
    return QuizResponse(
        status="accepted",
        message=f"Quiz request accepted. Solving quiz at {url}"
    )

async def solve_quiz_async(quiz_url: str):
    """
    Solve the quiz asynchronously.
    
    Args:
        quiz_url: URL of the quiz to solve
    """
    solver = None
    try:
        solver = QuizSolver()
        await solver.solve_quiz_chain(quiz_url)
        logger.info(f"Successfully completed quiz chain starting from {quiz_url}")
    except Exception as e:
        logger.error(f"Error solving quiz {quiz_url}: {e}", exc_info=True)
    finally:
        if solver:
            await solver.close()

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors with 400 status."""
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": "Invalid JSON payload", "errors": exc.errors()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "LLM Analysis Quiz API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "config_valid": True,
        "email_configured": bool(config.STUDENT_EMAIL),
        "openai_configured": bool(config.OPENAI_API_KEY)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=config.HOST,
        port=config.PORT,
        reload=True
    )
