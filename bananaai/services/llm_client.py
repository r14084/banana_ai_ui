import time
import logging
import google.generativeai as genai
from typing import Optional


logger = logging.getLogger(__name__)


class LLMClient:
    """Enhanced LLM client with error handling and retry logic"""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing")
        
        self.api_key = api_key
        self.model_name = model
        genai.configure(api_key=api_key)
        self._model = None

    def _get_model(self):
        """Lazy loading of model"""
        if self._model is None:
            self._model = genai.GenerativeModel(self.model_name)
        return self._model

    def expand(self, system_prompt: str, user_prompt: str, 
               temperature: float = 0.6, max_tokens: int = 512, 
               max_retries: int = 3, reference_images: list = None) -> str:
        """
        Expand prompt with retry logic and comprehensive error handling
        """
        for attempt in range(max_retries):
            try:
                # Use system_instruction for better context
                model = genai.GenerativeModel(
                    self.model_name, 
                    system_instruction=system_prompt
                )
                
                # Prepare content - include images if provided
                content_parts = []
                
                # Add images if provided
                if reference_images:
                    import os
                    from PIL import Image
                    upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
                    
                    for img_filename in reference_images:
                        img_path = os.path.join(upload_folder, img_filename)
                        if os.path.exists(img_path):
                            try:
                                img = Image.open(img_path)
                                content_parts.append(img)
                                logger.info(f"Added reference image: {img_filename}")
                            except Exception as e:
                                logger.warning(f"Failed to load image {img_filename}: {e}")
                
                # Add the text prompt
                content_parts.append(user_prompt)
                
                response = model.generate_content(
                    content_parts,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens,
                        "top_p": 0.95,
                        "top_k": 40,
                    },
                    safety_settings=[
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                    ]
                )
                
                # Check if response has candidates and parts
                if response.candidates:
                    candidate = response.candidates[0]
                    if candidate.content and candidate.content.parts:
                        text = candidate.content.parts[0].text
                        if text:
                            logger.info(f"Successfully expanded prompt (attempt {attempt + 1})")
                            return text.strip()
                    
                    # Check finish reason
                    if hasattr(candidate, 'finish_reason'):
                        if candidate.finish_reason == 2:  # SAFETY
                            logger.warning("Response blocked by safety filters")
                            # Try with modified prompt
                            if attempt < max_retries - 1:
                                user_prompt = f"Please help me with this creative writing task: {user_prompt}"
                                continue
                            raise ValueError("Content was blocked by safety filters")
                        elif candidate.finish_reason == 3:  # MAX_TOKENS
                            logger.warning("Response hit max token limit")
                            # Still try to get partial response
                            if candidate.content and candidate.content.parts:
                                text = candidate.content.parts[0].text
                                if text:
                                    return text.strip()
                
                raise ValueError("Empty or invalid response from API")

            except genai.types.BlockedPromptException as e:
                logger.error(f"Prompt was blocked by safety filters: {e}")
                raise ValueError("Prompt contains inappropriate content")
            
            except genai.types.StopCandidateException as e:
                logger.error(f"Response generation stopped: {e}")
                raise ValueError("Could not generate appropriate response")
            
            except Exception as e:
                logger.warning(f"API call failed (attempt {attempt + 1}/{max_retries}): {e}")
                
                if attempt == max_retries - 1:
                    logger.error("All retry attempts failed")
                    raise RuntimeError(f"Failed to expand prompt after {max_retries} attempts: {str(e)}")
                
                # Exponential backoff
                time.sleep(2 ** attempt)
        
        raise RuntimeError("Unexpected error in retry loop")