import time
import logging
import google.generativeai as genai
from typing import Optional


logger = logging.getLogger(__name__)


class LLMClient:
    """Enhanced LLM client with error handling and retry logic"""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
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
               max_retries: int = 3) -> str:
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
                
                response = model.generate_content(
                    user_prompt,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens,
                    },
                )
                
                if not response.text:
                    raise ValueError("Empty response from API")
                
                logger.info(f"Successfully expanded prompt (attempt {attempt + 1})")
                return response.text.strip()

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