"""Retry handler with exponential backoff for API requests."""

import logging
import time
from typing import Callable, TypeVar

from crawler.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RetryHandler:
    """Handles retry logic with exponential backoff."""

    def __init__(
        self,
        max_retries: int = settings.max_retries,
        backoff_factor: float = settings.retry_backoff_factor,
        max_delay: int = settings.retry_max_delay,
    ):
        """
        Initialize retry handler.

        Args:
            max_retries: Maximum number of retry attempts
            backoff_factor: Multiplicative factor for exponential backoff
            max_delay: Maximum delay between retries in seconds
        """
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay

    def execute_with_retry(self, func: Callable[[], T], operation_name: str = "operation") -> T:
        """
        Execute a function with retry logic and exponential backoff.

        Args:
            func: Function to execute
            operation_name: Name of the operation for logging

        Returns:
            Result from the function

        Raises:
            Exception: If all retry attempts fail
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                result = func()
                if attempt > 0:
                    logger.info(f"{operation_name} succeeded on attempt {attempt + 1}")
                return result
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = min(self.backoff_factor**attempt, self.max_delay)
                    logger.warning(
                        f"{operation_name} failed on attempt {attempt + 1}/{self.max_retries + 1}. "
                        f"Retrying in {delay}s... Error: {str(e)}"
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        f"{operation_name} failed after {self.max_retries + 1} attempts. "
                        f"Final error: {str(e)}"
                    )

        raise last_exception  # type: ignore


# Global retry handler instance
retry_handler = RetryHandler()
