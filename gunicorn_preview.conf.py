"""Free-preview settings; application access logs are disabled."""
import os
bind = '0.0.0.0:' + os.environ.get('PORT', '8003')
workers = 2
worker_class = 'sync'
threads = 1
timeout = 30
graceful_timeout = 30
max_requests = 200
max_requests_jitter = 20
limit_request_line = 2048
limit_request_fields = 50
limit_request_field_size = 4096
accesslog = None
errorlog = '-'
capture_output = False
loglevel = 'warning'
