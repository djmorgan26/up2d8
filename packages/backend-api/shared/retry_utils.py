"""
Retry utilities with exponential backoff for external API calls.

Provides decorators and functions for retrying operations that may fail
due to transient errors (network issues, rate limits, temporary service unavailability).
"""

import time
import logging
from functools import wraps
from typing import Callable, TypeVar, Any
import random

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryExhaustedError(Exception):
    """Raised when all retry attempts have been exhausted."""
    pass


def exponential_backoff_with_jitter(
    attempt: int,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True
) -> float:
    """
    Calculate exponential backoff delay with optional jitter.

    Args:
        attempt: The current attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        jitter: Whether to add random jitter to prevent thundering herd

    Returns:
        Delay in seconds before next retry
    """
    delay = min(base_delay * (2 ** attempt), max_delay)

    if jitter:
        # Add jitter: random value between 0 and delay
        delay = delay * (0.5 + random.random() * 0.5)

    return delay


def should_retry_exception(exception: Exception, retryable_exceptions: tuple = None) -> bool:
    """
    Determine if an exception should trigger a retry.

    Args:
        exception: The exception that was raised
        retryable_exceptions: Tuple of exception types that are retryable

    Returns:
        True if the exception is retryable, False otherwise
    """
    if retryable_exceptions is None:
        # Default retryable exceptions
        retryable_exceptions = (
            ConnectionError,
            TimeoutError,
            IOError,
        )

    # Check if it's a retryable exception type
    if isinstance(exception, retryable_exceptions):
        return True

    # Check for specific error messages that indicate retryable errors
    error_msg = str(exception).lower()
    retryable_messages = [
        'rate limit',
        'too many requests',
        'timeout',
        'connection',
        'temporarily unavailable',
        'service unavailable',
        '429',
        '503',
        '504',
    ]

    return any(msg in error_msg for msg in retryable_messages)


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retryable_exceptions: tuple = None,
    on_retry: Callable[[Exception, int, float], None] = None
):
    """
    Decorator for retrying a function with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts (including first attempt)
        base_delay: Base delay in seconds between retries
        max_delay: Maximum delay in seconds
        retryable_exceptions: Tuple of exception types that should trigger retry
        on_retry: Optional callback function called before each retry

    Example:
        @retry_with_backoff(max_attempts=3, base_delay=2.0)
        def call_external_api():
            response = requests.get("https://api.example.com")
            return response.json()
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # Check if we should retry
                    if attempt < max_attempts - 1 and should_retry_exception(e, retryable_exceptions):
                        delay = exponential_backoff_with_jitter(attempt, base_delay, max_delay)

                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {delay:.2f}s..."
                        )

                        # Call retry callback if provided
                        if on_retry:
                            on_retry(e, attempt + 1, delay)

                        time.sleep(delay)
                    else:
                        # Non-retryable error or last attempt
                        break

            # All retries exhausted
            logger.error(
                f"All {max_attempts} attempts failed for {func.__name__}. Last error: {str(last_exception)}"
            )
            raise last_exception

        return wrapper
    return decorator


async def retry_async_with_backoff(
    func: Callable[..., Any],
    *args,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retryable_exceptions: tuple = None,
    **kwargs
) -> Any:
    """
    Async version of retry with exponential backoff.

    Args:
        func: Async function to retry
        *args: Positional arguments for func
        max_attempts: Maximum number of attempts
        base_delay: Base delay in seconds between retries
        max_delay: Maximum delay in seconds
        retryable_exceptions: Tuple of exception types that should trigger retry
        **kwargs: Keyword arguments for func

    Returns:
        Result of the function call

    Example:
        result = await retry_async_with_backoff(
            async_api_call,
            param1="value",
            max_attempts=3
        )
    """
    import asyncio

    last_exception = None

    for attempt in range(max_attempts):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e

            # Check if we should retry
            if attempt < max_attempts - 1 and should_retry_exception(e, retryable_exceptions):
                delay = exponential_backoff_with_jitter(attempt, base_delay, max_delay)

                logger.warning(
                    f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {str(e)}. "
                    f"Retrying in {delay:.2f}s..."
                )

                await asyncio.sleep(delay)
            else:
                # Non-retryable error or last attempt
                break

    # All retries exhausted
    logger.error(
        f"All {max_attempts} attempts failed for {func.__name__}. Last error: {str(last_exception)}"
    )
    raise last_exception


# Convenience function for DB operations
def retry_db_operation(
    operation: Callable[..., T],
    *args,
    max_attempts: int = 3,
    **kwargs
) -> T:
    """
    Retry a database operation with sensible defaults for DB errors.

    Args:
        operation: Database operation function to retry
        *args: Positional arguments for operation
        max_attempts: Maximum number of attempts (default: 3)
        **kwargs: Keyword arguments for operation

    Returns:
        Result of the operation

    Example:
        result = retry_db_operation(
            collection.find_one,
            {"_id": doc_id},
            max_attempts=3
        )
    """
    db_exceptions = (
        ConnectionError,
        TimeoutError,
        IOError,
    )

    @retry_with_backoff(
        max_attempts=max_attempts,
        base_delay=0.5,  # Shorter delay for DB ops
        max_delay=10.0,   # Max 10s for DB
        retryable_exceptions=db_exceptions
    )
    def _wrapped_operation():
        return operation(*args, **kwargs)

    return _wrapped_operation()
