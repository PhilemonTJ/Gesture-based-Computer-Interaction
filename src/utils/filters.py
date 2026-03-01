"""
OneEuroFilter – adaptive low-pass filter for real-time signal smoothing.

Reduces jitter at low speeds while keeping responsiveness at high speeds.
Reference: Casiez et al., "1€ Filter: A Simple Speed-based Low-pass Filter
for Noisy Input in Interactive Systems", CHI 2012.
"""

import math


class OneEuroFilter:
    """
    A simple speed-adaptive low-pass filter.

    Parameters
    ----------
    min_cutoff : float
        Minimum cutoff frequency (Hz). Lower = more smoothing at low speeds.
    beta : float
        Speed coefficient. Higher = less smoothing (more responsiveness) at
        high speeds.
    d_cutoff : float
        Cutoff frequency for the derivative (Hz).  Usually left at 1.0.
    """

    def __init__(self, min_cutoff: float = 1.0, beta: float = 0.007,
                 d_cutoff: float = 1.0):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff

        # Internal state
        self._x_prev: float | None = None
        self._dx_prev: float = 0.0
        self._t_prev: float | None = None

    # ------------------------------------------------------------------
    @staticmethod
    def _smoothing_factor(t_e: float, cutoff: float) -> float:
        """Compute the exponential smoothing factor alpha."""
        r = 2.0 * math.pi * cutoff * t_e
        return r / (r + 1.0)

    @staticmethod
    def _exponential_smoothing(alpha: float, x: float, x_prev: float) -> float:
        return alpha * x + (1.0 - alpha) * x_prev

    # ------------------------------------------------------------------
    def __call__(self, t: float, x: float) -> float:
        """
        Filter a new sample.

        Parameters
        ----------
        t : float
            Timestamp in seconds (e.g. ``time.time()``).
        x : float
            Raw (unfiltered) value.

        Returns
        -------
        float
            Filtered value.
        """
        if self._t_prev is None:
            # First sample – nothing to filter yet.
            self._x_prev = x
            self._dx_prev = 0.0
            self._t_prev = t
            return x

        t_e = t - self._t_prev  # elapsed time since last sample
        if t_e <= 0:
            t_e = 1e-6  # guard against zero / negative dt

        # --- filtered derivative (speed estimate) ---
        a_d = self._smoothing_factor(t_e, self.d_cutoff)
        dx = (x - self._x_prev) / t_e
        dx_hat = self._exponential_smoothing(a_d, dx, self._dx_prev)

        # --- adaptive cutoff ---
        cutoff = self.min_cutoff + self.beta * abs(dx_hat)

        # --- filtered signal ---
        a = self._smoothing_factor(t_e, cutoff)
        x_hat = self._exponential_smoothing(a, x, self._x_prev)

        # --- store state ---
        self._x_prev = x_hat
        self._dx_prev = dx_hat
        self._t_prev = t

        return x_hat

    def reset(self) -> None:
        """Clear internal state so the next call acts as a first sample."""
        self._x_prev = None
        self._dx_prev = 0.0
        self._t_prev = None
