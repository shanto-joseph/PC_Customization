"""
API Usage Statistics Tracker
Monitor and log chatbot API usage
"""

from django.core.cache import cache
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class UsageStats:
    """Track API usage statistics"""
    
    STATS_KEY = "chatbot_usage_stats"
    DAILY_RESET_HOUR = 0  # Midnight UTC
    
    @staticmethod
    def increment_api_call(user_id, cached=False):
        """Increment API call counter"""
        stats = cache.get(UsageStats.STATS_KEY, {
            'total_requests': 0,
            'cached_requests': 0,
            'api_calls': 0,
            'users': set(),
            'last_reset': datetime.now().isoformat()
        })
        
        stats['total_requests'] += 1
        if cached:
            stats['cached_requests'] += 1
        else:
            stats['api_calls'] += 1
        
        stats['users'].add(user_id)
        
        cache.set(UsageStats.STATS_KEY, stats, 86400)  # 24 hours
        
        # Log every 10 requests
        if stats['total_requests'] % 10 == 0:
            UsageStats.log_stats(stats)
    
    @staticmethod
    def log_stats(stats=None):
        """Log current usage statistics"""
        if stats is None:
            stats = cache.get(UsageStats.STATS_KEY, {})
        
        if not stats:
            return
        
        total = stats.get('total_requests', 0)
        cached = stats.get('cached_requests', 0)
        api_calls = stats.get('api_calls', 0)
        users = len(stats.get('users', set()))
        
        cache_hit_rate = (cached / total * 100) if total > 0 else 0
        
        logger.info(
            f"📊 Chatbot Usage Stats: "
            f"Total: {total} | API Calls: {api_calls} | "
            f"Cached: {cached} ({cache_hit_rate:.1f}%) | "
            f"Users: {users}"
        )
    
    @staticmethod
    def get_stats():
        """Get current statistics"""
        stats = cache.get(UsageStats.STATS_KEY, {})
        
        total = stats.get('total_requests', 0)
        cached = stats.get('cached_requests', 0)
        api_calls = stats.get('api_calls', 0)
        users = len(stats.get('users', set()))
        
        cache_hit_rate = (cached / total * 100) if total > 0 else 0
        
        return {
            'total_requests': total,
            'api_calls': api_calls,
            'cached_requests': cached,
            'cache_hit_rate': cache_hit_rate,
            'unique_users': users,
            'last_reset': stats.get('last_reset', 'N/A')
        }
    
    @staticmethod
    def reset_stats():
        """Reset statistics"""
        cache.delete(UsageStats.STATS_KEY)
        logger.info("📊 Usage statistics reset")
    
    @staticmethod
    def estimate_remaining_capacity(api_keys_count=3):
        """Estimate remaining capacity for today"""
        stats = UsageStats.get_stats()
        api_calls = stats['api_calls']
        
        # Each API key gets 20 requests per day
        total_capacity = api_keys_count * 20
        remaining = total_capacity - api_calls
        percentage = (remaining / total_capacity * 100) if total_capacity > 0 else 0
        
        return {
            'total_capacity': total_capacity,
            'used': api_calls,
            'remaining': remaining,
            'percentage_remaining': percentage
        }
