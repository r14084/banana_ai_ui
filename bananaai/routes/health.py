from flask import Blueprint, jsonify
import time
import os
from ..utils.file_ops import get_upload_stats

health_bp = Blueprint('health', __name__)

# Store start time when module is loaded
start_time = time.time()

@health_bp.route('/check', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "uptime": time.time() - start_time
    })

@health_bp.route('/ready', methods=['GET'])  
def readiness_check():
    """Check if all dependencies are available"""
    try:
        # Check if upload folder exists
        upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
        if not os.path.exists(upload_folder):
            return jsonify({"status": "not ready", "error": "Upload folder missing"}), 503
            
        # Check if API key is configured
        if not os.getenv('GEMINI_API_KEY'):
            return jsonify({"status": "not ready", "error": "API key missing"}), 503
            
        return jsonify({"status": "ready"})
    except Exception as e:
        return jsonify({"status": "not ready", "error": str(e)}), 503

@health_bp.route('/stats', methods=['GET'])
def stats():
    """Get application statistics"""
    upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
    upload_stats = get_upload_stats(upload_folder)
    
    return jsonify({
        "uptime": time.time() - start_time,
        "uploads": upload_stats,
        "version": "1.0.0"
    })