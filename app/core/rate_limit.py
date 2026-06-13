import time


class RateLimiter:
    """Simple per-user rate limiting."""

    def __init__(self, max_requests: int = 3, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}

    def is_allowed(self, user_id: str) -> bool:
        """Check if user is allowed to make request.

        Args:
            user_id: unique user identifier

        Returns:
            True if request is allowed, False if rate limited
        """
        now = time.time()
        if user_id not in self.requests:
            self.requests[user_id] = []

        self.requests[user_id] = [
            ts for ts in self.requests[user_id] if now - ts < self.window_seconds
        ]

        if len(self.requests[user_id]) < self.max_requests:
            self.requests[user_id].append(now)
            return True
        return False

    def get_retry_after(self, user_id: str) -> int:
        """Get seconds until next request allowed."""
        if user_id not in self.requests or not self.requests[user_id]:
            return 0
        oldest = min(self.requests[user_id])
        retry_after = int(self.window_seconds - (time.time() - oldest)) + 1
        return max(0, retry_after)
