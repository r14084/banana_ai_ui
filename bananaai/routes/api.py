from flask import Blueprint, request, jsonify, current_app
from ..services.llm_client import LLMClient
from ..services.banana_client import BananaAIClient
from ..services.prompt_builder import expand_prompt, SYSTEM_GUIDE
from ..services.cache_service import CacheService
from ..middleware.rate_limiter import rate_limit
from ..utils.validators import validate_prompt_request, validate_image_file
from ..utils.file_ops import save_uploaded_file, get_file_url, generate_output_filename, save_generated_image
import logging
import os

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__)
cache = CacheService()

@api_bp.route('/assist', methods=['POST'])
@rate_limit('assist')
def assist():
    """AI-powered prompt expansion endpoint"""
    try:
        data = request.get_json(force=True, silent=True) or {}
        
        # Validate input
        is_valid, error_msg = validate_prompt_request(data)
        if not is_valid:
            return jsonify({"error": error_msg}), 400

        user_text = data.get('prompt').strip()
        ar = data.get('aspect_ratio', '9:16').strip()
        
        # Check cache first
        cache_key = f"{user_text}:{ar}"
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info("Returning cached prompt expansion")
            return jsonify({"expanded": cached_result, "cached": True})

        # 1) rule-based expansion ภายใน
        expanded_local = expand_prompt(user_text, ar)

        # 2) ส่งเข้า Gemini 2.5 Flash เพื่อขยาย/ขัดเกลา
        cfg = current_app.config
        client = LLMClient(api_key=cfg.get('GEMINI_API_KEY'), model=cfg.get('LLM_MODEL'))
        result = client.expand(SYSTEM_GUIDE, expanded_local)
        
        # Cache the result
        cache.set(cache_key, result, ttl=cfg.get('CACHE_TTL', 3600))
        
        logger.info("Successfully generated prompt expansion")
        return jsonify({"expanded": result, "cached": False})
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        logger.error(f"API error: {e}")
        return jsonify({"error": "Service temporarily unavailable"}), 503
    except Exception as e:
        logger.error(f"Unexpected error in /assist: {e}")
        return jsonify({"error": "Internal server error"}), 500


@api_bp.route('/upload', methods=['POST'])
@rate_limit('upload')
def upload():
    """File upload endpoint"""
    try:
        if 'image_file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['image_file']
        
        # Validate file
        is_valid, error_msg = validate_image_file(file)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        # Save file
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        filename = save_uploaded_file(file, upload_folder)
        
        if not filename:
            return jsonify({"error": "Failed to save file"}), 500
        
        # Return file info
        file_url = get_file_url(filename)
        logger.info(f"File uploaded successfully: {filename}")
        
        return jsonify({
            "filename": filename,
            "url": file_url,
            "message": "File uploaded successfully"
        })
        
    except Exception as e:
        logger.error(f"Error in /upload: {e}")
        return jsonify({"error": "Failed to upload file"}), 500


@api_bp.route('/generate', methods=['POST'])
@rate_limit('assist')  # Use same rate limit as assist
def generate():
    """Generate image using Banana AI"""
    try:
        data = request.get_json(force=True, silent=True) or {}
        
        # Validate input
        is_valid, error_msg = validate_prompt_request(data)
        if not is_valid:
            return jsonify({"error": error_msg}), 400

        prompt = data.get('prompt').strip()
        aspect_ratio = data.get('aspect_ratio', '9:16').strip()
        
        # Optional parameters
        negative_prompt = data.get('negative_prompt', '').strip()
        guidance_scale = float(data.get('guidance_scale', 7.5))
        num_inference_steps = int(data.get('num_inference_steps', 20))
        reference_images = data.get('reference_images', [])  # list of uploaded image filenames
        
        # Validate optional parameters
        if guidance_scale < 1 or guidance_scale > 20:
            return jsonify({"error": "guidance_scale must be between 1 and 20"}), 400
        
        if num_inference_steps < 1 or num_inference_steps > 100:
            return jsonify({"error": "num_inference_steps must be between 1 and 100"}), 400

        # Get configuration
        cfg = current_app.config
        api_key = cfg.get('GEMINI_API_KEY')
        banana_model = cfg.get('BANANA_MODEL', 'gemini-2.5-flash-image-preview')
        
        if not api_key:
            return jsonify({"error": "GEMINI_API_KEY not configured"}), 503

        # Initialize Banana AI client (uses Gemini Image model)
        banana_client = BananaAIClient(api_key, banana_model)
        
        # Build reference image paths if provided
        reference_image_paths = []
        if reference_images:
            upload_folder = cfg.get('UPLOAD_FOLDER', 'uploads')
            for ref_image in reference_images:
                ref_path = os.path.join(upload_folder, ref_image)
                if os.path.exists(ref_path):
                    reference_image_paths.append(ref_path)
                    logger.info(f"Using reference image: {ref_image}")
                else:
                    logger.warning(f"Reference image not found: {ref_path}")
            logger.info(f"Total reference images found: {len(reference_image_paths)}")
        
        # Generate image
        logger.info(f"Generating image with prompt: {prompt[:50]}...")
        result = banana_client.generate_image(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            negative_prompt=negative_prompt,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            reference_image_paths=reference_image_paths
        )
        
        if not result:
            return jsonify({"error": "Failed to generate image"}), 500
        
        # Save generated image
        output_folder = cfg.get('OUTPUT_FOLDER', 'output')
        filename = generate_output_filename(prompt, aspect_ratio)
        
        filepath = save_generated_image(
            result['image_base64'], 
            output_folder, 
            filename
        )
        
        if not filepath:
            return jsonify({"error": "Failed to save generated image"}), 500
        
        # Return result
        logger.info("Image generation completed successfully")
        return jsonify({
            "success": True,
            "filename": filename,
            "url": f"/output/{filename}",
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "seed": result.get('seed'),
            "width": result.get('width'),
            "height": result.get('height'),
            "generation_time": result.get('generation_time'),
            "message": "Image generated successfully"
        })
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        logger.error(f"Generation error: {e}")
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        logger.error(f"Unexpected error in /generate: {e}")
        return jsonify({"error": "Internal server error"}), 500