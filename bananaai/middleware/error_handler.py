import logging
from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Register global error handlers for the application"""
    
    @app.errorhandler(400)
    def bad_request(e):
        logger.warning(f"Bad request: {e}")
        return jsonify({"error": "Bad request"}), 400
    
    @app.errorhandler(404)
    def not_found(e):
        logger.warning(f"Not found: {e}")
        return jsonify({"error": "Resource not found"}), 404
    
    @app.errorhandler(413)
    def request_entity_too_large(e):
        logger.warning(f"Request entity too large: {e}")
        return jsonify({"error": "File too large"}), 413
    
    @app.errorhandler(429)
    def too_many_requests(e):
        logger.warning(f"Too many requests: {e}")
        return jsonify({"error": "Too many requests"}), 429
    
    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error(f"Internal server error: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        logger.warning(f"HTTP exception: {e}")
        return jsonify({"error": e.description}), e.code
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred"}), 500