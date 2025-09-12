from flask import Flask
from bananaai.config import load_config, validate_config
from bananaai.routes.ui import ui_bp
from bananaai.routes.api import api_bp
from bananaai.routes.health import health_bp
from bananaai.middleware.error_handler import register_error_handlers
from bananaai.middleware.security import register_security_middleware
from bananaai.middleware.rate_limiter import register_rate_limiter
from bananaai.utils.logger import setup_logging


def create_app():
    app = Flask(__name__)
    
    # Load and validate configuration
    cfg = load_config(app)
    validate_config(cfg)
    
    # Setup logging
    setup_logging(app)
    
    # Register middleware
    register_security_middleware(app)
    register_rate_limiter(app)
    register_error_handlers(app)

    # Register blueprints
    app.register_blueprint(ui_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(health_bp, url_prefix='/health')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='127.0.0.1', port=8000, debug=True)