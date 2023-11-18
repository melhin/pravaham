import logging
import os

logging.captureWarnings(True)

bind = "0.0.0.0:8001"
workers = int(os.getenv("GUNICORN_WORKERS", 2))
worker_class = "sync"
timeout = 120