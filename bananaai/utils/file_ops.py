import os
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


def save_uploaded_file(file, upload_folder: str) -> Optional[str]:
    """
    Save uploaded file to the upload folder
    
    Args:
        file: Flask file object
        upload_folder: Directory to save files
    
    Returns:
        Saved filename or None if error
    """
    from .validators import sanitize_filename
    
    try:
        filename = sanitize_filename(file.filename)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        logger.info(f"File saved: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return None


def cleanup_old_files(upload_folder: str, hours: int = 24):
    """
    Remove files older than specified hours
    
    Args:
        upload_folder: Directory containing uploaded files
        hours: Age threshold in hours
    """
    try:
        cutoff_time = time.time() - (hours * 3600)
        
        for file_path in Path(upload_folder).glob('*'):
            if file_path.is_file():
                file_age = file_path.stat().st_mtime
                if file_age < cutoff_time:
                    file_path.unlink()
                    logger.info(f"Deleted old file: {file_path.name}")
    except Exception as e:
        logger.error(f"Error during file cleanup: {e}")


def get_file_url(filename: str, base_url: str = '') -> str:
    """
    Generate URL for uploaded file
    
    Args:
        filename: Name of the file
        base_url: Base URL of the application
    
    Returns:
        Full URL to the file
    """
    if base_url:
        return f"{base_url}/uploads/{filename}"
    return f"/uploads/{filename}"


def generate_output_filename(prompt: str, aspect_ratio: str = "9:16") -> str:
    """
    Generate filename for generated image
    
    Args:
        prompt: Original prompt text
        aspect_ratio: Image aspect ratio
    
    Returns:
        Generated filename
    """
    import re
    from datetime import datetime
    
    # Clean prompt for filename
    clean_prompt = re.sub(r'[^a-zA-Z0-9\s]', '', prompt)
    clean_prompt = re.sub(r'\s+', '_', clean_prompt.strip())
    clean_prompt = clean_prompt[:30]  # Limit length
    
    # Add timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    ar_suffix = aspect_ratio.replace(':', 'x')
    
    return f"{timestamp}_{clean_prompt}_{ar_suffix}.png"


def save_generated_image(image_data, output_folder: str, filename: str) -> Optional[str]:
    """
    Save generated image from base64 or binary data
    
    Args:
        image_data: Base64 encoded image (str) or raw binary image data (bytes)
        output_folder: Output directory
        filename: Filename to save as
    
    Returns:
        Full filepath if successful, None otherwise
    """
    import base64
    from pathlib import Path
    
    try:
        # Ensure output folder exists
        Path(output_folder).mkdir(exist_ok=True)
        
        # Handle different input types
        if isinstance(image_data, bytes):
            # Check if it's raw image data (starts with image magic numbers)
            # PNG: 0x89 0x50 0x4E 0x47 (‰PNG)
            # JPEG: 0xFF 0xD8 0xFF
            # GIF: 0x47 0x49 0x46 (GIF)
            if (image_data[:4] == b'\x89PNG' or 
                image_data[:3] == b'\xff\xd8\xff' or 
                image_data[:3] == b'GIF'):
                # It's already raw image binary data
                final_image_data = image_data
            else:
                # It's base64 encoded bytes - decode it
                try:
                    final_image_data = base64.b64decode(image_data)
                except:
                    # Try decoding as UTF-8 first then base64
                    image_str = image_data.decode('utf-8')
                    final_image_data = base64.b64decode(image_str)
        elif isinstance(image_data, str):
            # String input - handle data URL or plain base64
            if image_data.startswith('data:image'):
                # Remove data URL prefix
                image_data = image_data.split(',')[1]
            
            # Decode base64 string
            final_image_data = base64.b64decode(image_data)
        else:
            raise ValueError(f"Unsupported image data type: {type(image_data)}")
        
        # Full file path
        filepath = os.path.join(output_folder, filename)
        
        # Save to file
        with open(filepath, 'wb') as f:
            f.write(final_image_data)
        
        logger.info(f"Generated image saved: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error saving generated image: {e}")
        return None


def get_upload_stats(upload_folder: str) -> dict:
    """
    Get statistics about uploaded files
    
    Args:
        upload_folder: Directory containing uploaded files
    
    Returns:
        Dictionary with upload statistics
    """
    try:
        files = list(Path(upload_folder).glob('*'))
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        
        return {
            'file_count': len(files),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'oldest_file': min((f.stat().st_mtime for f in files if f.is_file()), default=None),
            'newest_file': max((f.stat().st_mtime for f in files if f.is_file()), default=None)
        }
    except Exception as e:
        logger.error(f"Error getting upload stats: {e}")
        return {
            'file_count': 0,
            'total_size_mb': 0,
            'oldest_file': None,
            'newest_file': None
        }