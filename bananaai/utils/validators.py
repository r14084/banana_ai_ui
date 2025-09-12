import os
import imghdr
from typing import Tuple


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_PROMPT_LENGTH = 2000


def validate_prompt_request(data: dict) -> Tuple[bool, str]:
    """
    Validate prompt expansion request data
    
    Args:
        data: Request data dictionary
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not data:
        return False, "Request body is required"
    
    prompt = data.get('prompt', '').strip()
    if not prompt:
        return False, "Prompt is required"
    
    if len(prompt) > MAX_PROMPT_LENGTH:
        return False, f"Prompt exceeds maximum length of {MAX_PROMPT_LENGTH} characters"
    
    aspect_ratio = data.get('aspect_ratio', '9:16')
    if aspect_ratio not in ['9:16', '16:9']:
        return False, "Invalid aspect ratio. Must be '9:16' or '16:9'"
    
    return True, ""


def validate_image_file(file) -> Tuple[bool, str]:
    """
    Validate uploaded image file
    
    Args:
        file: Flask file object
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file:
        return False, "No file provided"
    
    if not file.filename:
        return False, "No file selected"
    
    # Check file extension
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Check actual file type (more secure than extension check)
    file.seek(0)
    file_type = imghdr.what(file.stream)
    file.seek(0)  # Reset file pointer
    
    if file_type not in ALLOWED_EXTENSIONS:
        return False, "Invalid image file"
    
    return True, ""


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal attacks
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    import re
    from datetime import datetime
    
    # Remove any path components
    filename = os.path.basename(filename)
    
    # Remove non-alphanumeric characters except dots and underscores
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    # Add timestamp to make unique
    name, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    return f"{timestamp}_{name[:50]}{ext}"