import logging
import os

logging.captureWarnings(True)

bind = "0.0.0.0:8002"
workers = int(os.getenv("GUNICORN_WORKERS", 2))
worker_class = "async"
timeout = 120