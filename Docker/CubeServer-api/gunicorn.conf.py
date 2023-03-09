from multiprocessing import cpu_count

# gunicorn configuration

workers = cpu_count()

# HTTPS:
keyfile = "/etc/ssl/api_cert/server.key"
certfile = "/etc/ssl/api_cert/server.pem"
ssl_version = "TLS"

# Bind:
bind = ['0.0.0.0:443']

# Logging:
accesslog = '-'  # Access log to stdout

# Reduce crashing on lower-power servers:
#preload_app = True
#timeout = 120
#graceful_timeout = 90
