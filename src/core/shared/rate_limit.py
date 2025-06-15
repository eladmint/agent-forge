import time
from collections import defaultdict, deque
from typing import Deque, Dict

# Default production rate limits
PROD_RATE_LIMIT_MAX_CALLS = 100  # Example: 100 calls
PROD_RATE_LIMIT_PERIOD_SECONDS = 3600  # Example: per 1 hour (3600 seconds)


class RateLimiter:
    """
    A simple rate limiter that tracks requests for a single entity (e.g., a user or IP).
    """

    def __init__(self, max_calls: int, period_seconds: int):
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self.timestamps: Deque[float] = deque()

    def is_allowed(self) -> bool:
        """
        Checks if a new request is allowed based on the rate limit.
        Adds the current timestamp if allowed.
        """
        current_time = time.monotonic()

        # Remove timestamps older than the current period
        while (
            self.timestamps and self.timestamps[0] <= current_time - self.period_seconds
        ):
            self.timestamps.popleft()

        if len(self.timestamps) < self.max_calls:
            self.timestamps.append(current_time)
            return True
        return False

    def get_remaining_calls(self) -> int:
        """
        Returns the number of calls remaining in the current window.
        This is an estimate as the window slides.
        """
        current_time = time.monotonic()
        # Remove old timestamps to get an accurate count for the current window
        while (
            self.timestamps and self.timestamps[0] <= current_time - self.period_seconds
        ):
            self.timestamps.popleft()
        return max(0, self.max_calls - len(self.timestamps))

    def get_retry_after_seconds(self) -> float:
        """
        Returns the time in seconds after which the user can try again.
        Returns 0 if allowed.
        """
        current_time = time.monotonic()
        while (
            self.timestamps and self.timestamps[0] <= current_time - self.period_seconds
        ):
            self.timestamps.popleft()

        if len(self.timestamps) < self.max_calls:
            return 0.0

        # If rate limited, the retry time is when the oldest timestamp in the queue expires
        if self.timestamps:
            return (self.timestamps[0] + self.period_seconds) - current_time
        return float(
            self.period_seconds
        )  # Should not happen if timestamps is empty and limit exceeded


class UserRateLimitManager:
    """
    Manages rate limiters for multiple users.
    """

    def __init__(
        self,
        default_max_calls: int = PROD_RATE_LIMIT_MAX_CALLS,
        default_period_seconds: int = PROD_RATE_LIMIT_PERIOD_SECONDS,
    ):
        self.user_limiters: Dict[str, RateLimiter] = defaultdict(
            lambda: RateLimiter(default_max_calls, default_period_seconds)
        )
        self.default_max_calls = default_max_calls
        self.default_period_seconds = default_period_seconds

    def is_user_allowed(self, user_id: str) -> bool:
        """
        Checks if a user is allowed to make a request.
        """
        return self.user_limiters[user_id].is_allowed()

    def get_user_remaining_calls(self, user_id: str) -> int:
        """
        Gets the remaining calls for a specific user.
        """
        return self.user_limiters[user_id].get_remaining_calls()

    def get_user_retry_after_seconds(self, user_id: str) -> float:
        """
        Gets the retry_after time for a specific user.
        """
        return self.user_limiters[user_id].get_retry_after_seconds()

    def update_user_limit(self, user_id: str, max_calls: int, period_seconds: int):
        """
        Updates the rate limit settings for a specific user.
        """
        self.user_limiters[user_id] = RateLimiter(max_calls, period_seconds)


# Example usage (can be removed or kept for testing)
if __name__ == "__main__":
    # Test UserRateLimitManager
    manager = UserRateLimitManager(default_max_calls=3, default_period_seconds=10)
    user1 = "user_A"

    print(f"User {user1} attempting requests:")
    for i in range(5):
        allowed = manager.is_user_allowed(user1)
        remaining = manager.get_user_remaining_calls(user1)
        retry_after = manager.get_user_retry_after_seconds(user1)
        print(
            f"Attempt {i+1}: Allowed: {allowed}, Remaining: {remaining}, Retry After: {retry_after:.2f}s"
        )
        if not allowed:
            print(f"Rate limited. Waiting for {retry_after:.2f}s...")
            time.sleep(retry_after + 0.1)  # Sleep a bit longer
            # After waiting, the next call should be allowed
            allowed = manager.is_user_allowed(user1)
            remaining = manager.get_user_remaining_calls(user1)
            retry_after = manager.get_user_retry_after_seconds(user1)
            print(
                f"Attempt after wait: Allowed: {allowed}, Remaining: {remaining}, Retry After: {retry_after:.2f}s"
            )
        time.sleep(1)

    print("\nTesting a different user with default limits:")
    user2 = "user_B"
    for i in range(2):
        print(
            f"User {user2} - Attempt {i+1}: Allowed: {manager.is_user_allowed(user2)}"
        )

    print("\nUpdating limit for user_A to 5 calls per 5 seconds")
    manager.update_user_limit(user1, 5, 5)
    for i in range(7):
        allowed = manager.is_user_allowed(user1)
        remaining = manager.get_user_remaining_calls(user1)
        retry_after = manager.get_user_retry_after_seconds(user1)
        print(
            f"User {user1} (new limit) - Attempt {i+1}: Allowed: {allowed}, Remaining: {remaining}, Retry After: {retry_after:.2f}s"
        )
        if not allowed:
            break
        time.sleep(0.5)
