# waitress.conf.py
import os
from decouple import config

# Waitress configuration for Windows Production
host = config('WAITRESS_HOST', default='0.0.0.0')
port = config('WAITRESS_PORT', default='8000', cast=int)
threads = config('WAITRESS_THREADS', default='8', cast=int)

# Production optimizations
channel_timeout = 300
connection_limit = 1000
asyncore_use_poll = True
max_request_body_size = 1073741824  # 1GB

print(f"🚀 Waitress Production Server")
print(f"📍 Host: {host}:{port}")
print(f"🧵 Threads: {threads}")
print(f"⏱️  Channel Timeout: {channel_timeout}s")
print(f"📊 Connection Limit: {connection_limit}")