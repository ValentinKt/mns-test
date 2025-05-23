import time
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# In-memory cache
_cache = {}

def get_cached_data(key):
    """
    Get data from cache if it exists and is not expired.
    
    Args:
        key (str): Cache key
        
    Returns:
        dict or None: Cached data or None if not found or expired
    """
    if key in _cache:
        entry = _cache[key]
        if entry['expires'] > time.time():
            return entry['data']
        else:
            # Remove expired entry
            del _cache[key]
    return None

def cache_data(key, data, ttl=3600):
    """
    Store data in cache with expiration time.
    
    Args:
        key (str): Cache key
        data (dict): Data to cache
        ttl (int): Time to live in seconds (default: 1 hour)
    """
    _cache[key] = {
        'data': data,
        'expires': time.time() + ttl
    }
    logger.debug(f"Cached data with key {key}, expires in {ttl} seconds")

@lru_cache(maxsize=512)
def memoized_fetch(func, *args, **kwargs):
    """
    Memoize function results for expensive operations.
    
    Args:
        func: Function to memoize
        *args, **kwargs: Function arguments
        
    Returns:
        Result of the function call
    """
    return func(*args, **kwargs)