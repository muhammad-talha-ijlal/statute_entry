# gunicorn_config.py
import os
import multiprocessing

# Worker configuration for PostgreSQL
workers = multiprocessing.cpu_count() * 2 + 1  # Optimal for PostgreSQL
worker_class = "sync"
worker_connections = 1000

# Timeout settings
timeout = 60  # Increased for database operations
keepalive = 5
graceful_timeout = 30

# Bind configuration
bind = "0.0.0.0:5000"

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "legal_text_app"

# Preload app for better performance with PostgreSQL
preload_app = True

# Worker management
max_requests = 1000
max_requests_jitter = 100

# PostgreSQL connection management
def when_ready(server):
    """Called when the server is ready to serve requests"""
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    """Called when a worker receives the INT or QUIT signal"""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called before worker processes are forked"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called after worker processes are forked"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)