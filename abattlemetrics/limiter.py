import time

__all__ = ('Limiter',)


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
        self._last = 0.0
        self._tokens = rate

    def get_tokens(self, current=None):
        current = time.monotonic() if current is None else current
        last = self._last or current

        tokens = self._tokens

        if current > last + self.per:
            # Passed window
            tokens = self.rate
        else:
            # Add back any tokens leaked
            elapsed = current - last
            tokens += int(elapsed // self.leak_rate)

        return tokens

    def get_retry_after(self, current=None, *, tokens=None):
        current = time.monotonic() if current is None else current
        last = self._last or current

        if tokens is None:
            tokens = self.get_tokens(current)
        if tokens:
            return 0

        elapsed = current - last
        return max(0, self.leak_rate - elapsed)

    def update_rate_limit(self, current=None):
        current = time.monotonic() if current is None else current
        if not self._last:
            self._last = current

        tokens = self.get_tokens(current)

        retry_after = 0
        if tokens:
            self._tokens = tokens - 1
        else:
            retry_after = self.get_retry_after(current, tokens=tokens)

        # Only update _last when a token is leaked
        if current - self._last > self.leak_rate:
            self._last = current

        return retry_after

    def reset(self):
        self._last = 0.0
        self._tokens = self.rate
