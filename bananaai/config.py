import os
from dotenv import load_dotenv
from pathlib import Path


def load_config(app):
    load_dotenv()
    
    # Basic Flask settings
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_MB', '20')) * 1024 * 1024
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    
    # File handling
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
    app.config['OUTPUT_FOLDER'] = os.getenv('OUTPUT_FOLDER', 'output')
    app.config['LOG_FOLDER'] = os.getenv('LOG_FOLDER', 'logs')
    
    # API settings (both Gemini and Banana AI use the same API)
    app.config['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY')
    app.config['LLM_MODEL'] = os.getenv('LLM_MODEL', 'gemini-2.5-flash')
    
    # Banana AI model (image generation model)
    app.config['BANANA_MODEL'] = os.getenv('BANANA_MODEL', 'gemini-2.5-flash-image-preview')
    
    # Rate limiting (per-minute limits)
    app.config['RATE_LIMIT_ASSIST'] = int(os.getenv('RATE_LIMIT_ASSIST', '10'))
    app.config['RATE_LIMIT_UPLOAD'] = int(os.getenv('RATE_LIMIT_UPLOAD', '5'))
    
    # Cache settings (TTL in seconds)
    app.config['CACHE_TTL'] = int(os.getenv('CACHE_TTL', '3600'))  # 1 hour
    app.config['CACHE_MAX_SIZE'] = int(os.getenv('CACHE_MAX_SIZE', '100'))
    
    # File cleanup (hours)
    app.config['FILE_CLEANUP_HOURS'] = int(os.getenv('FILE_CLEANUP_HOURS', '24'))
    
    # Create directories
    for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], app.config['LOG_FOLDER']]:
        Path(folder).mkdir(exist_ok=True)
    
    return app.config


def validate_config(config):
    """Validate required configuration values"""
    required_keys = ['GEMINI_API_KEY']
    missing = [key for key in required_keys if not config.get(key)]
    
    if missing:
        raise ValueError(f"Missing required configuration: {', '.join(missing)}")
    
    # Validate file size limits
    max_size = config.get('MAX_CONTENT_LENGTH', 0)
    if max_size > 100 * 1024 * 1024:  # 100MB limit
        raise ValueError("MAX_CONTENT_LENGTH cannot exceed 100MB")