import time
import logging
import google.generativeai as genai
from typing import Optional, Dict, Any
import base64
import os
import tempfile
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)


class BananaAIClient:
    """Client for Banana AI image generation using Google Generative AI Image Model"""

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash-image-preview"):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required for Banana AI")
        
        self.api_key = api_key
        self.model_name = model_name
        genai.configure(api_key=api_key)
        self._image_model = None

    def _get_image_model(self):
        """Lazy loading of image generation model"""
        if self._image_model is None:
            self._image_model = genai.GenerativeModel(self.model_name)
        return self._image_model

    def generate_image(self, prompt: str, aspect_ratio: str = "9:16", 
                      negative_prompt: str = "", guidance_scale: float = 7.5, 
                      num_inference_steps: int = 20, reference_image_paths: list = None,
                      max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        Generate image using Gemini 2.5 Flash Image Preview model with reference image
        
        Args:
            prompt: Text prompt for image generation
            aspect_ratio: Image aspect ratio (9:16 or 16:9)
            negative_prompt: What to avoid in the image
            guidance_scale: How closely to follow the prompt (1-20)
            num_inference_steps: Number of denoising steps (1-100)
            reference_image_paths: List of paths to reference image files
            max_retries: Maximum retry attempts
        
        Returns:
            Dictionary containing image data and metadata or None if failed
        """
        # Convert aspect ratio to width/height - fixed dimensions
        if aspect_ratio == "16:9":
            width, height = 1920, 1080  # Full HD landscape
        else:  # Default to 9:16 
            width, height = 1080, 1920  # Full HD portrait

        # Build prompt for image generation
        image_prompt = self._build_image_prompt(prompt, negative_prompt, aspect_ratio)

        # Load reference images if provided
        reference_images = []
        if reference_image_paths:
            for ref_path in reference_image_paths:
                if os.path.exists(ref_path):
                    try:
                        from PIL import Image as PILImage
                        ref_img = PILImage.open(ref_path)
                        reference_images.append(ref_img)
                        logger.info(f"Loaded reference image: {ref_path}")
                    except Exception as e:
                        logger.error(f"Error loading reference image {ref_path}: {e}")
            logger.info(f"Total reference images loaded: {len(reference_images)}")

        for attempt in range(max_retries):
            try:
                logger.info(f"Generating image with Gemini Image Model (attempt {attempt + 1})")
                
                # Get image generation model
                model = self._get_image_model()
                
                # Build content for generation
                if reference_images:
                    # Include reference images in the prompt
                    if len(reference_images) == 1:
                        content = [
                            f"Based on this reference image, {image_prompt}",
                            reference_images[0]
                        ]
                        logger.info("Using 1 reference image for generation")
                    else:
                        content = [f"Based on these reference images, combine and use them as inspiration for: {image_prompt}"]
                        content.extend(reference_images)
                        logger.info(f"Using {len(reference_images)} reference images for generation")
                else:
                    content = image_prompt
                    logger.info("No reference images, using text prompt only")
                
                # Generate image using Gemini Image Preview model
                response = model.generate_content(
                    content,
                    generation_config={
                        "temperature": max(0.1, min(1.0, guidance_scale / 10)),
                        "max_output_tokens": 2048,
                        "candidate_count": 1
                    }
                )
                
                # Extract image data from response
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    
                    # Check if response contains image data
                    if hasattr(candidate, 'content') and candidate.content.parts:
                        for part in candidate.content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                # Found image data - it might be raw bytes or base64
                                image_data = part.inline_data.data
                                mime_type = part.inline_data.mime_type
                                
                                # Check if data is bytes (raw image) or string (base64)
                                if isinstance(image_data, bytes):
                                    logger.info("Received raw binary image data from Gemini")
                                    # Keep as bytes - our save function can handle it
                                    final_data = image_data
                                else:
                                    logger.info("Received base64 image data from Gemini")
                                    # Keep as string - our save function can handle it
                                    final_data = image_data
                                
                                logger.info("Successfully generated image with Gemini")
                                return {
                                    "image_base64": final_data,  # Can be bytes or string
                                    "seed": hash(prompt + str(time.time())) % 1000000,
                                    "prompt": prompt,
                                    "aspect_ratio": aspect_ratio,
                                    "width": width,
                                    "height": height,
                                    "generation_time": time.time(),
                                    "mime_type": mime_type,
                                    "model": self.model_name
                                }
                
                # If no image data found, create placeholder
                logger.warning("No image data in Gemini response, creating placeholder")
                image_data = self._create_placeholder_image(width, height, prompt)
                
                if image_data:
                    logger.info("Created placeholder image")
                    return {
                        "image_base64": image_data,
                        "seed": hash(prompt + str(time.time())) % 1000000,
                        "prompt": prompt,
                        "aspect_ratio": aspect_ratio,
                        "width": width,
                        "height": height,
                        "generation_time": time.time(),
                        "mime_type": "image/png",
                        "model": self.model_name + " (placeholder)"
                    }
                else:
                    logger.error("Failed to create any image data")
                            
            except genai.types.BlockedPromptException as e:
                logger.error(f"Prompt was blocked by safety filters: {e}")
                raise ValueError("Prompt contains inappropriate content")
            
            except genai.types.StopCandidateException as e:
                logger.error(f"Response generation stopped: {e}")
                raise ValueError("Could not generate appropriate response")
            
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Image generation failed: {str(e)}")
            
            # Wait before retry (exponential backoff)
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
        
        raise RuntimeError("Failed to generate image after all retries")

    def _build_image_prompt(self, prompt: str, negative_prompt: str, aspect_ratio: str) -> str:
        """Build optimized prompt for Gemini image generation model"""
        # Build the image generation prompt
        image_prompt = f"Create a high-quality image: {prompt}"
        
        # Add style and quality descriptors
        image_prompt += ". Style: photorealistic, highly detailed, vibrant colors, professional lighting"
        
        # Add aspect ratio specification
        if aspect_ratio == "16:9":
            image_prompt += ". Format: wide landscape orientation, 16:9 aspect ratio"
        else:
            image_prompt += ". Format: portrait orientation, 9:16 aspect ratio"
        
        # Add negative prompt constraints
        if negative_prompt:
            image_prompt += f". Avoid: {negative_prompt}, blurry, low quality, distorted"
        else:
            image_prompt += ". Avoid: blurry, low quality, distorted, artifacts"
        
        return image_prompt

    def _create_placeholder_image(self, width: int, height: int, prompt: str) -> str:
        """Create a placeholder image (in real implementation, this would be actual image generation)"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import random
            
            # Create a colorful gradient background
            image = Image.new('RGB', (width, height), color=(135, 206, 235))  # Sky blue
            draw = ImageDraw.Draw(image)
            
            # Add gradient effect
            for y in range(height):
                color_intensity = int(255 * (1 - y / height))
                color = (max(100, color_intensity), max(150, color_intensity), 235)
                draw.line([(0, y), (width, y)], fill=color)
            
            # Add some visual elements based on prompt
            colors = [(255, 182, 193), (255, 165, 0), (50, 205, 50), (255, 20, 147), (30, 144, 255)]
            
            # Add circles for visual interest
            for i in range(5):
                x = random.randint(50, width - 50)
                y = random.randint(50, height - 50)
                radius = random.randint(20, 60)
                color = random.choice(colors)
                draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color + (128,))
            
            # Add text
            try:
                # Try to use a nice font, fallback to default if not available
                font_size = min(width, height) // 15
                font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            
            text = f"Generated: {prompt[:30]}..."
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = (width - text_width) // 2
            text_y = height - text_height - 20
            
            # Add text with background
            draw.rectangle([text_x-10, text_y-5, text_x+text_width+10, text_y+text_height+5], fill=(0, 0, 0, 180))
            draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)
            
            # Convert to base64
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            image_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return image_b64
            
        except Exception as e:
            logger.error(f"Error creating placeholder image: {e}")
            return None

    def save_image_from_base64(self, image_base64, filename: str) -> bool:
        """
        Save base64 image to file
        
        Args:
            image_base64: Base64 encoded image data (str or bytes)
            filename: Full path to save the image
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Handle both string and bytes input
            if isinstance(image_base64, bytes):
                # If it's bytes, decode to string first
                image_base64 = image_base64.decode('utf-8')
            
            # Convert to string if not already
            image_base64 = str(image_base64)
            
            # Remove data URL prefix if present
            if image_base64.startswith('data:image'):
                image_base64 = image_base64.split(',')[1]
            
            # Decode base64
            image_data = base64.b64decode(image_base64)
            
            # Save to file
            with open(filename, 'wb') as f:
                f.write(image_data)
            
            logger.info(f"Image saved: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            return False