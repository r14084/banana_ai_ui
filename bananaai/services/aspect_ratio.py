"""Aspect ratio configurations for image generation"""

AR_MAP = {
    "9:16": {
        "aspect_ratio": "9:16",
        "width": 1024,
        "height": 1820,
        "composition_hint": "Vertical composition ideal for portraits and mobile content",
        "suggested_subjects": ["portraits", "full-body shots", "vertical scenes"],
        "frame_type": "portrait"
    },
    "16:9": {
        "aspect_ratio": "16:9",
        "width": 1820,
        "height": 1024,
        "composition_hint": "Horizontal composition ideal for landscapes and cinematic shots",
        "suggested_subjects": ["landscapes", "group photos", "wide scenes"],
        "frame_type": "landscape"
    }
}

def get_aspect_ratio_config(ar: str) -> dict:
    """
    Get aspect ratio configuration
    
    Args:
        ar: Aspect ratio string (9:16 or 16:9)
    
    Returns:
        Configuration dictionary for the aspect ratio
    """
    return AR_MAP.get(ar, AR_MAP['9:16'])