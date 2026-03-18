"""
Chatbot Configuration
Adjust these settings to control API usage and performance
"""

# ============================================
# RATE LIMITING SETTINGS
# ============================================
# Rate limiting is DISABLED - users can send unlimited messages

# Enable/disable rate limiting
RATE_LIMIT_ENABLED = False

# Maximum messages per user in the time period (only if enabled)
RATE_LIMIT_REQUESTS = 5

# Time period in seconds (300 = 5 minutes) (only if enabled)
RATE_LIMIT_PERIOD = 300

# ============================================
# CACHING SETTINGS
# ============================================
# Reduces API calls by caching common responses

# Enable/disable response caching
CACHE_ENABLED = True

# How long to cache responses (in seconds)
# 3600 = 1 hour, 7200 = 2 hours, 86400 = 24 hours
CACHE_DURATION = 3600

# ============================================
# AI MODEL SETTINGS
# ============================================

# Model to use (gemini-2.5-flash is fastest and cheapest)
MODEL_NAME = "gemini-2.5-flash"

# Maximum tokens in response (lower = less quota usage)
# 300 = short responses, 500 = medium, 1000 = long
MAX_OUTPUT_TOKENS = 300

# Temperature (0.0-1.0, higher = more creative but less consistent)
TEMPERATURE = 0.7

# Number of previous messages to include in context
# Lower = less quota usage, but less context
HISTORY_LENGTH = 4

# ============================================
# SYSTEM PROMPT
# ============================================
SYSTEM_PROMPT = """You are Vex AI, a PC customization expert. Keep responses concise and helpful.
Expertise: PC components, custom builds, bottleneck analysis, compatibility checks."""

# ============================================
# QUOTA MANAGEMENT
# ============================================

# Log API usage statistics
LOG_API_USAGE = True

# Warn when approaching quota limit
QUOTA_WARNING_THRESHOLD = 0.8  # 80%

# ============================================
# OPTIMIZATION TIPS
# ============================================
"""
To reduce API usage:

1. ENABLE RATE_LIMIT (set RATE_LIMIT_ENABLED = True)
2. INCREASE CACHE_DURATION (e.g., 7200 = 2 hours)
3. DECREASE MAX_OUTPUT_TOKENS (e.g., 200 for shorter responses)
4. DECREASE HISTORY_LENGTH (e.g., 2 for less context)

Current settings provide:
- NO rate limiting (unlimited messages per user)
- 1 hour response caching
- 300 token responses
- 4 message history

Estimated capacity with 3 API keys (60 requests/day):
- Without caching: ~60 unique conversations
- With caching (50% hit rate): ~120 conversations
- Without rate limiting: Users can send unlimited messages

⚠️ WARNING: Without rate limiting, a single user could exhaust your quota.
Consider enabling it if you notice quota running out too fast.
"""
