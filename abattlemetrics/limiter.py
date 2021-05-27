import asyncio
import math
import time


class Limiter:
    """An implementation of the leaky bucket algorithm.

    Args:
        rate (int): The max number of tokens available.
        per (float): How fast the tokens are restored in seconds.

    """
    __slots__ = ('rate', 'per', 'leak_rate', '_last', '_tokens')

    def __init__(self, rate, per):
        self.rate = int(rate)
        self.per = float(per)
        self.leak_rate = self.per / self.rate
        self._last = time.monotonic()
        self._tokens = rate

    def get_tokens(self, current=None):
        current = time.monotonic() if current is None else current

        tokens = self._tokens

        if current > self._last + self.per:
            # Passed window
            tokens = self.rate
        else:
            # Add back any tokens leaked
            elapsed = current - self._last
            tokens += int(elapsed // self.leak_rate)

        return tokens

    def get_retry_after(self, current=None, *, _tokens=None):
        current = time.monotonic() if current is None else current

        tokens = self.get_tokens(current) if _tokens is None else _tokens
        if tokens:
            return 0

        elapsed = current - self._last
        return max(0, self.leak_rate - elapsed)

    def update_rate_limit(self, current=None):
        current = time.monotonic() if current is None else current

        tokens = self.get_tokens(current)

        retry_after = 0
        if tokens:
            self._tokens = tokens - 1
        else:
            retry_after = self.get_retry_after(current, _tokens=tokens)

        # Only update _last when a token is leaked
        if current - self._last > self.leak_rate:
            self._last = current

        return retry_after

    def reset(self):
        self._last = time.monotonic()
        self._tokens = self.rate


# class LimitedLock(Limiter):
#     """A Limiter with an integrated asyncio.Lock.
# 
#     This provides methods from both the Limiter and the asyncio.Lock,
#     and also supports the async context manager.
#     The internal lock can be accessed via the `lock` attribute.
# 
#     The unlock can also be delayed using the defer() method if you
#     need to enforce a custom retry after time.
# 
#     """
#     __slots__ = ('lock',)
# 
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
# 
#         lock = asyncio.Lock()
#         self.lock = lock
#         self.acquire = lock.acquire
#         self.release = lock.release
#         self.locked = lock.locked
#         self._unlock = True
# 
#     async def __aenter__(self):
#         await self.lock.acquire()
#         self._unlock = True
#         self.update_rate_limit()
# 
#     def defer(
#             self, unlock_after: float, *, check_limiter=True
#         ) -> asyncio.TimerHandle:
#         """Defer the asyncio.Lock's unlock.
# 
#         Args:
#             unlock_after (float):
#                 The number of seconds to sleep before unlocking.
#             check_limiter (bool):
#                 If True, takes into consideration both the limiter's
#                 current rate limit and `unlock_after`, and defers
#                 the lock by the larger of the two.
#                 This should only be disabled if unlock_after
#                 was calculated from get_retry_after().
# 
#         Returns:
#             asyncio.TimerHandle
# 
#         """
#         if not self._unlock:
#             return
#         self._unlock = False
# 
#         if check_limiter:
#             unlock_after = max(unlock_after, self.get_retry_after())
# 
#         loop = asyncio.get_running_loop()
#         return loop.call_later(unlock_after, self.lock.release)
# 
#     async def __aexit__(self, exc_type, exc_val, tb):
#         retry_after = self.get_retry_after()
#         if retry_after:
#             self.defer(retry_after, check_limiter=False)
#         else:
#             self.lock.release()
# 
#     @classmethod
#     def from_limiter(cls, rate, per):
#         return cls(Limiter(rate, per))
# 
# 
# class MockLimitedLock(LimitedLock):
#     """A mock limited lock with an infinite number of tokens."""
#     def __init__(self, limiter=None):
#         super().__init__(Limiter(math.inf, 0))
# 
#     def get_tokens(self, current=None):
#         return math.inf
# 
#     def get_retry_after(self, current=None, *, _tokens=None):
#         return 0
# 
#     def update_rate_limit(self, current=None):
#         return 0
