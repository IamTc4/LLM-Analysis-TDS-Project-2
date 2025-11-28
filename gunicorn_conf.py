import multiprocessing
import os

# Debug: Log PORT value for troubleshooting
port = os.getenv('PORT', '8000')
print(f"🔍 DEBUG: PORT environment variable = '{port}'")
print(f"🔍 DEBUG: Binding to 0.0.0.0:{port}")

# Bind to Render's PORT or default to 8000
bind = f"0.0.0.0:{port}"

# Worker configuration
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"

# Timeout settings (important for long-running quiz solving)
timeout = 300
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Development mode
reload = os.getenv("FLASK_ENV") == "development"
