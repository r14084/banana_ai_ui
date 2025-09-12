from .aspect_ratio import AR_MAP

SYSTEM_GUIDE = (
    "You are a prompt expander for Banana AI image generation. "
    "Expand user intent into a precise, visual, and non-ambiguous instruction. "
    "Keep photography-aware details (lighting, lens, perspective), subject placement, style, and constraints. "
    "Avoid copyrighted names unless provided. Output plain text."
)

BASE_STYLE = (
    "Use concise sentences; prefer concrete visual terms; maintain consistent lighting with the source image; "
    "respect human diversity; avoid unsafe or explicit content."
)

def expand_prompt(user_text: str, ar: str = '9:16') -> str:
    """
    Expand user prompt with aspect ratio considerations
    
    Args:
        user_text: The user's original prompt
        ar: Aspect ratio (9:16 or 16:9)
    
    Returns:
        Expanded prompt with visual details and technical specifications
    """
    ar_conf = AR_MAP.get(ar, AR_MAP['9:16'])
    hints = [
        f"Aspect ratio {ar_conf['aspect_ratio']} ({ar_conf['width']}x{ar_conf['height']})",
        ar_conf['composition_hint'],
        "match perspective and shadows with the original photo if provided",
        "clean background continuity; avoid artifacts or extra limbs",
        "subtle, natural color grading; avoid oversaturation",
    ]

    expanded = (
        f"{user_text.strip()}\n"
        f"\nScene & Subject: clarify age range, pose, and facial expression; wardrobe details with textures.\n"
        f"Lighting: soft daylight or match source; realistic shadows and reflections.\n"
        f"Composition: rule of thirds; foreground/background separation. {ar_conf['composition_hint']}.\n"
        f"Technical: {hints[0]}; maintain detail; photorealistic skin; no watermark.\n"
        f"Context: {hints[2]}. {hints[3]}. {hints[4]}\n"
    )
    return expanded