import multiprocessing
import os

# Bind to 0.0.0.0:8000
bind = "0.0.0.0:8000"

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
