"""Configuration file for gunicorn"""

from multiprocessing import cpu_count

# gunicorn configuration

workers = cpu_count()
threads = 2

# TODO: Add TLS configurability to maybe use certbot?
# Need to secure the webapp with TLS...
#keyfile = "/etc/ssl/key.key"
#certfile = "/etc/ssl/cert.pem"
#ssl_version = "TLS"

# Bind:
bind = ['0.0.0.0:80']

# Logging:
accesslog = '-'  # Access log to stdout

# Reduce crashing on lower-power servers:
preload_app = True
timeout = 120
graceful_timeout = 90
