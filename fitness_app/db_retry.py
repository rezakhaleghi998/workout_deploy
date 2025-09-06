"""Database connection retry utility for better error handling"""

import time
import logging
from django.db import connection
from django.db.utils import OperationalError, InterfaceError
from functools import wraps

logger = logging.getLogger(__name__)

def db_retry(max_retries=5, delay=2, backoff_factor=1.5):
    """
    Decorator to retry database operations with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_factor: Factor by which delay is multiplied after each retry
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    # Close existing connection if it's stale
                    if connection.connection and attempt > 0:
                        connection.close()
                    
                    result = func(*args, **kwargs)
                    
                    # If we succeeded after retries, log it
                    if attempt > 0:
                        logger.info(f"Database operation succeeded after {attempt} retries")
                    
                    return result
                    
                except (OperationalError, InterfaceError, ConnectionError) as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logger.warning(
                            f"Database operation failed (attempt {attempt + 1}/{max_retries + 1}): {str(e)}"
                            f". Retrying in {current_delay} seconds..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        logger.error(
                            f"Database operation failed after {max_retries + 1} attempts. "
                            f"Last error: {str(e)}"
                        )
                        
                except Exception as e:
                    # For non-connection related errors, don't retry
                    logger.error(f"Non-retryable database error: {str(e)}")
                    raise e
            
            # If we've exhausted all retries, raise the last exception
            raise last_exception
        
        return wrapper
    return decorator

def test_db_connection():
    """Test database connection with retries"""
    @db_retry(max_retries=3, delay=1)
    def _test_connection():
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return cursor.fetchone()[0] == 1
    
    try:
        result = _test_connection()
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False

def ensure_db_connection():
    """Ensure database connection is alive, reconnect if necessary"""
    try:
        # Test the connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True
    except Exception as e:
        logger.warning(f"Database connection lost: {str(e)}. Attempting to reconnect...")
        try:
            connection.close()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            logger.info("Database reconnection successful")
            return True
        except Exception as reconnect_error:
            logger.error(f"Database reconnection failed: {str(reconnect_error)}")
            return False