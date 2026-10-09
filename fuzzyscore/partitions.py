"""Fuzzy partitions of a numeric feature.

A Ruspini partition is a family of triangular membership functions whose
values sum to one at every point of the domain. Cumulative terms are the
"at least level k" aggregates of such a partition. When a scorecard is fitted
on cumulative terms with non-negative weights, its output is monotone in the
underlying feature by construction.
"""

from __future__ import annotations

import numpy as np


def ruspini_partition(x: np.ndarray, knots: np.ndarray | list[float]) -> np.ndarray:
    """Return the membership matrix of ``x`` in a triangular Ruspini partition.

    Parameters
    ----------
    x:
        One-dimensional array of feature values.
    knots:
        Strictly increasing breakpoints. Each knot is the peak of one term.
        Values below the first knot belong fully to the first term and values
        above the last knot belong fully to the last term.

    Returns
    -------
    numpy.ndarray
        Array of shape ``(len(x), len(knots))``. Every row sums to one.
    """
    x = np.asarray(x, dtype=float)
    knots = np.asarray(knots, dtype=float)
    if x.ndim != 1:
        raise ValueError("x must be one-dimensional")
    if knots.ndim != 1 or knots.size < 2:
        raise ValueError("at least two knots are required")
    if np.any(np.diff(knots) <= 0):
        raise ValueError("knots must be strictly increasing")

    xc = np.clip(x, knots[0], knots[-1])
    # Index of the right knot of the segment that contains each value.
    right = np.searchsorted(knots, xc, side="right")
    right = np.clip(right, 1, knots.size - 1)
    left = right - 1
    width = knots[right] - knots[left]
    frac = (xc - knots[left]) / width

    out = np.zeros((x.size, knots.size), dtype=float)
    rows = np.arange(x.size)
    out[rows, left] = 1.0 - frac
    out[rows, right] += frac
    return out


def cumulative_terms(memberships: np.ndarray) -> np.ndarray:
    """Turn a Ruspini membership matrix into cumulative "at least" terms.

    Column ``k`` of the result is the membership in the fuzzy set
    "level is at least k" for ``k = 1 .. m-1``. The first level is dropped
    because its cumulative membership is identically one and would duplicate
    the intercept.
    """
    m = np.asarray(memberships, dtype=float)
    if m.ndim != 2:
        raise ValueError("memberships must be a two-dimensional array")
    cum = np.cumsum(m[:, ::-1], axis=1)[:, ::-1]
    return cum[:, 1:]


def term_labels(feature: str, knots: np.ndarray | list[float], direction: int = 1) -> list[str]:
    """Human readable labels for the cumulative terms of one feature."""
    knots = list(knots)
    if direction >= 0:
        return [f"{feature} is at least {k:g}" for k in knots[1:]]
    return [f"{feature} is at most {k:g}" for k in knots[:-1][::-1]]
