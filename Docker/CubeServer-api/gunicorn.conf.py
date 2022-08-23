from multiprocessing import cpu_count

# gunicorn configuration

loglevel = "debug"

workers = cpu_count()

# HTTPS:
keyfile = "/etc/ssl/api_cert/key.key"
certfile = "/etc/ssl/api_cert/cert.pem"
ssl_version = "TLS"

# Bind:
bind = ['0.0.0.0:443']
