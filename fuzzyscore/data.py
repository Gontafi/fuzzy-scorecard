"""Synthetic loan generator used for tests, examples and the CI demo.

The generator imitates the shape of public mortgage data: a credit score,
a loan-to-value ratio, a debt-to-income ratio and a binary default flag whose
probability rises with LTV and DTI and falls with the credit score.
"""

from __future__ import annotations

import numpy as np

FEATURES = ("fico", "ltv", "dti")


def make_synthetic_loans(n: int = 10_000, seed: int = 0, base_rate: float = 0.04):
    """Return ``(X, y)`` where ``X`` has columns FICO, LTV, DTI."""
    if n < 1:
        raise ValueError("n must be positive")
    rng = np.random.default_rng(seed)
    fico = np.clip(rng.normal(740, 50, n), 580, 850)
    ltv = np.clip(rng.normal(78, 14, n), 20, 100)
    dti = np.clip(rng.normal(35, 9, n), 5, 60)

    logit = (
        -3.9
        - 0.018 * (fico - 740)
        + 0.045 * (ltv - 78)
        + 0.035 * (dti - 35)
        + 0.6 * ((ltv > 90) & (fico < 680))
    )
    logit += np.log(base_rate / 0.04)
    prob = 1.0 / (1.0 + np.exp(-logit))
    y = (rng.uniform(size=n) < prob).astype(int)
    X = np.column_stack([fico, ltv, dti])
    return X, y


DEFAULT_KNOTS = {
    "fico": [600, 640, 680, 720, 760, 800],
    "ltv": [50, 70, 80, 90, 97],
    "dti": [15, 25, 36, 43, 50],
}

DEFAULT_DIRECTIONS = {"fico": -1, "ltv": 1, "dti": 1}
