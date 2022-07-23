from multiprocessing import cpu_count

# gunicorn configuration

loglevel = "info"

workers = cpu_count()

# HTTPS:
keyfile = "/etc/ssl/key.key"
certfile = "/etc/ssl/cert.pem"
ssl_version = "TLS"

# Bind:
bind = ['0.0.0.0:80']
