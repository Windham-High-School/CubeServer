from multiprocessing import cpu_count

# gunicorn configuration

loglevel = "info"

workers = cpu_count()

# HTTPS:
keyfile = "/etc/ssl/api_cert/api.key"
certfile = "/etc/ssl/api_cert/api.pem"
ssl_version = "TLS"

# Bind:
bind = ['0.0.0.0:443']
