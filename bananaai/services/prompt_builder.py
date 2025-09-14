from .aspect_ratio import AR_MAP

SYSTEM_GUIDE = (
    "You are a style expander for image generation. "
    "DO NOT add new objects or subjects. Keep the user's original subject/object exactly as they wrote it. "
    "ONLY expand on visual style, mood, lighting, color grading, camera techniques, and artistic qualities. "
    "Focus on: photography style, lighting quality, color tone, atmosphere, texture, composition style, camera angle. "
    "Never add people, objects, or scenes that the user didn't mention. Output plain text."
)

BASE_STYLE = (
    "Use concise sentences; prefer concrete visual terms; maintain consistent lighting with the source image; "
    "respect human diversity; avoid unsafe or explicit content."
)

def expand_prompt(user_text: str, ar: str = '9:16') -> str:
    """
    Expand user prompt focusing ONLY on style, not adding new objects
    
    Args:
        user_text: The user's original prompt (e.g., "cinematic food photography")
        ar: Aspect ratio (9:16 or 16:9)
    
    Returns:
        Expanded prompt with style and technical details ONLY
    """
    ar_conf = AR_MAP.get(ar, AR_MAP['9:16'])
    
    # Build style-focused expansion
    expanded = (
        f"{user_text.strip()}\n"
        f"\nStyle Enhancement:\n"
        f"- Lighting: professional studio lighting, soft shadows, highlight details\n"
        f"- Color Grading: cinematic color palette, balanced tones, rich contrast\n"
        f"- Composition: {ar_conf['composition_hint']}, {ar_conf['aspect_ratio']} format\n"
        f"- Technical Quality: ultra sharp focus, high detail, professional grade\n"
        f"- Atmosphere: mood and tone matching the style requested\n"
        f"- Camera: professional photography techniques, depth of field control\n"
    )
    return expanded