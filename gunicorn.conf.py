# gunicorn.conf.py

import multiprocessing

# Configuración básica
bind = "unix:/var/www/carta_virtual_cuba/gunicorn.sock"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "/var/www/carta_virtual_cuba/logs/gunicorn_access.log"
errorlog = "/var/www/carta_virtual_cuba/logs/gunicorn_error.log"
loglevel = "warning"
capture_output = True

# Seguridad
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Performance
max_requests = 1000
max_requests_jitter = 50
