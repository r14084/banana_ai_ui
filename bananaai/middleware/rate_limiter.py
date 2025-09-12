import time
from functools import wraps
from flask import request, jsonify, current_app
from collections import defaultdict, deque

# In-memory rate limiter (suitable for single-instance local development)
request_history = defaultdict(lambda: {'assist': deque(), 'upload': deque()})

def rate_limit(endpoint_type):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            client_ip = request.remote_addr
            now = time.time()
            
            # Get rate limit for this endpoint
            limit_key = f'RATE_LIMIT_{endpoint_type.upper()}'
            rate_limit_per_minute = current_app.config.get(limit_key, 10)
            
            # Clean old requests (older than 1 minute)
            history = request_history[client_ip][endpoint_type]
            while history and history[0] < now - 60:
                history.popleft()
            
            # Check if limit exceeded
            if len(history) >= rate_limit_per_minute:
                return jsonify({
                    "error": "Rate limit exceeded",
                    "retry_after": 60 - (now - history[0])
                }), 429
            
            # Add current request
            history.append(now)
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

def register_rate_limiter(app):
    """Register rate limiter with Flask app"""
    pass  # Rate limiting is applied via decorators