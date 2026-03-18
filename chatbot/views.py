import os
import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.utils import timezone
import json
import logging
import hashlib
from datetime import timedelta
from .config import (
    RATE_LIMIT_ENABLED, RATE_LIMIT_REQUESTS, RATE_LIMIT_PERIOD,
    CACHE_ENABLED, CACHE_DURATION,
    MODEL_NAME, MAX_OUTPUT_TOKENS, TEMPERATURE, HISTORY_LENGTH,
    SYSTEM_PROMPT as CONFIG_SYSTEM_PROMPT
)
from .usage_stats import UsageStats

logger = logging.getLogger(__name__)

# Load all API keys from environment
API_KEYS = [
    os.environ.get("GEMINI_API_KEY"),
    os.environ.get("GEMINI_API_KEY_BACKUP"),
    os.environ.get("GEMINI_API_KEY_BACKUP_2"),
]

# Filter out None values and empty strings
API_KEYS = [key for key in API_KEYS if key and key.strip()]

# Track which API key is currently active
current_api_key_index = 0
GEMINI_AVAILABLE = len(API_KEYS) > 0

# Configure with the first available API key
if GEMINI_AVAILABLE:
    try:
        genai.configure(api_key=API_KEYS[current_api_key_index])
        logger.info(f"Configured Gemini API with key #{current_api_key_index + 1}")
    except Exception as e:
        logger.error(f"Failed to configure Gemini API: {e}")
        GEMINI_AVAILABLE = False

# Use system prompt from config
SYSTEM_PROMPT = CONFIG_SYSTEM_PROMPT


def get_cache_key(message):
    """Generate cache key from message"""
    # Normalize message for better cache hits
    normalized = message.lower().strip()
    return f"chatbot_response_{hashlib.md5(normalized.encode()).hexdigest()}"


def check_rate_limit(user_id):
    """Check if user has exceeded rate limit"""
    cache_key = f"chatbot_rate_limit_{user_id}"
    request_count = cache.get(cache_key, 0)
    
    if request_count >= RATE_LIMIT_REQUESTS:
        return False, request_count
    
    # Increment counter
    cache.set(cache_key, request_count + 1, RATE_LIMIT_PERIOD)
    return True, request_count + 1


def get_cached_response(message):
    """Get cached response if available"""
    if not CACHE_ENABLED:
        return None
    
    cache_key = get_cache_key(message)
    return cache.get(cache_key)


def cache_response(message, response):
    """Cache the response"""
    if not CACHE_ENABLED:
        return
    
    cache_key = get_cache_key(message)
    cache.set(cache_key, response, CACHE_DURATION)


def try_next_api_key():
    """Switch to the next available API key"""
    global current_api_key_index
    
    if len(API_KEYS) <= 1:
        return False
    
    # Try next API key
    current_api_key_index = (current_api_key_index + 1) % len(API_KEYS)
    
    try:
        genai.configure(api_key=API_KEYS[current_api_key_index])
        logger.info(f"Switched to backup API key #{current_api_key_index + 1}")
        return True
    except Exception as e:
        logger.error(f"Failed to configure backup API key #{current_api_key_index + 1}: {e}")
        return False


def generate_with_fallback(model_name, prompt, generation_config):
    """Try to generate content with automatic fallback to backup API keys"""
    attempts = 0
    max_attempts = len(API_KEYS)
    
    while attempts < max_attempts:
        try:
            model = genai.GenerativeModel(model_name, generation_config=generation_config)
            response = model.generate_content(prompt)
            return response, None
        except Exception as e:
            error_msg = str(e)
            logger.error(f"API key #{current_api_key_index + 1} error: {error_msg}")
            
            # Check if it's a rate limit or quota error
            is_rate_limit = any(keyword in error_msg.lower() for keyword in 
                              ["429", "quota", "exceeded", "rate limit", "resource exhausted"])
            
            if is_rate_limit and attempts < max_attempts - 1:
                # Try next API key
                if try_next_api_key():
                    attempts += 1
                    logger.info(f"Retrying with backup API key (attempt {attempts + 1}/{max_attempts})")
                    continue
                else:
                    return None, "Failed to switch to backup API key"
            else:
                # Not a rate limit error or no more keys to try
                return None, error_msg
    
    return None, "All API keys exhausted"


@csrf_exempt
@login_required
def chat(request):
    """Handle chat requests with Vex AI - requires authentication"""
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required', 'status': 'error'}, status=401)

    if not GEMINI_AVAILABLE:
        return JsonResponse({'response': "AI unavailable.", 'status': 'error'})

    try:
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()
        history = data.get("history", [])

        if not user_message:
            return JsonResponse({'error': 'Message empty'}, status=400)
        
        # Check rate limit (if enabled)
        if RATE_LIMIT_ENABLED:
            allowed, count = check_rate_limit(request.user.id)
            if not allowed:
                return JsonResponse({
                    'response': f"⏱️ You've reached the limit of {RATE_LIMIT_REQUESTS} messages per {RATE_LIMIT_PERIOD//60} minutes. Please wait a bit before sending more messages.",
                    'status': 'error'
                })
        else:
            count = 0  # No rate limiting
        
        # Check cache first
        cached_response = get_cached_response(user_message)
        if cached_response:
            logger.info(f"Cache hit for user {request.user.id}")
            UsageStats.increment_api_call(request.user.id, cached=True)
            return JsonResponse({
                "response": cached_response,
                "status": "success",
                "cached": True
            })
        
        # History formatting (configurable length)
        previous = "\n".join(
            f"{'User' if msg['role']=='user' else 'Vex AI'}: {msg['content']}"
            for msg in history[-HISTORY_LENGTH:]
        )

        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Previous conversation:\n{previous}\n\n"
            f"User: {user_message}"
            if previous else
            f"{SYSTEM_PROMPT}\n\nUser: {user_message}"
        )

        # Using configured model with automatic fallback
        generation_config = {
            "temperature": TEMPERATURE,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": MAX_OUTPUT_TOKENS
        }
        
        response, error = generate_with_fallback(MODEL_NAME, prompt, generation_config)
        
        if response:
            response_text = response.text
            
            # Cache the response
            cache_response(user_message, response_text)
            
            # Track usage
            UsageStats.increment_api_call(request.user.id, cached=False)
            
            logger.info(f"API call successful for user {request.user.id} (request #{count})")
            
            return JsonResponse({
                "response": response_text,
                "status": "success",
                "cached": False
            })
        else:
            # All API keys failed
            logger.error(f"All API keys failed: {error}")
            
            # Handle specific error types
            if any(keyword in str(error).lower() for keyword in ["429", "quota", "exceeded", "rate limit"]):
                return JsonResponse({
                    "response": "⏱️ All API keys are currently rate limited. Please try again in a few minutes!",
                    "status": "error"
                })
            else:
                return JsonResponse({
                    "response": "❌ Sorry, I encountered an error. Please try again later.",
                    "status": "error"
                })

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Unexpected error: {error_msg}")
        
        return JsonResponse({
            "response": "❌ Sorry, I encountered an unexpected error. Please try again later.",
            "status": "error"
        })
