"""Configuration file for gunicorn"""

import os
from multiprocessing import cpu_count

# gunicorn configuration

workers = cpu_count()

if os.path.exists("/etc/ssl/api_cert/server.key") and os.path.exists("/etc/ssl/api_cert/server.pem"):
    # HTTPS:
    keyfile = "/etc/ssl/api_cert/server.key"
    certfile = "/etc/ssl/api_cert/server.pem"
    ssl_version = "TLS"
    # Bind:
    bind = [f'0.0.0.0:{os.environ.get("PORT", 443)}']
else:
    # Bind:
    bind = [f'0.0.0.0:{os.environ.get("PORT", 80)}']

# Logging:
accesslog = '-'  # Access log to stdout

# Reduce crashing on lower-power servers:
preload_app = True
timeout = 120
graceful_timeout = 90
