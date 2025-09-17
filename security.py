from flask import g
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()


def register_security_middleware(app):
    """Register security-related middleware"""
    
    # Initialize CSRF protection
    csrf.init_app(app)
    
    # Add security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy (adjust as needed)
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:;"
        )
        response.headers['Content-Security-Policy'] = csp
        
        return response
    
    # Request ID for tracking
    @app.before_request
    def add_request_id():
        import uuid
        g.request_id = str(uuid.uuid4())
    
    # Log requests
    @app.after_request
    def log_request(response):
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        return response
