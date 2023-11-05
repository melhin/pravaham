import logging
import os

logging.captureWarnings(True)

bind = "0.0.0.0:6767"
workers = int(os.getenv("GUNICORN_WORKERS", 2))
worker_class = "async"
timeout = 120