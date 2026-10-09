"""Evaluation metrics used by the scorecard experiments."""

from __future__ import annotations

import numpy as np


def roc_auc(y_true: np.ndarray, score: np.ndarray) -> float:
    """Area under the ROC curve computed from ranks, with tie correction."""
    y = np.asarray(y_true).astype(bool)
    s = np.asarray(score, dtype=float)
    if y.shape != s.shape or y.ndim != 1:
        raise ValueError("y_true and score must be one-dimensional arrays of equal length")
    n_pos = int(y.sum())
    n_neg = int(y.size - n_pos)
    if n_pos == 0 or n_neg == 0:
        raise ValueError("both classes must be present")
    order = np.argsort(s, kind="mergesort")
    ranks = np.empty(s.size, dtype=float)
    sorted_s = s[order]
    i = 0
    while i < s.size:
        j = i
        while j + 1 < s.size and sorted_s[j + 1] == sorted_s[i]:
            j += 1
        ranks[order[i : j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    return float((ranks[y].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def brier_score(y_true: np.ndarray, prob: np.ndarray) -> float:
    """Mean squared error between outcomes and predicted probabilities."""
    y = np.asarray(y_true, dtype=float)
    p = np.asarray(prob, dtype=float)
    return float(np.mean((p - y) ** 2))


def expected_calibration_error(y_true: np.ndarray, prob: np.ndarray, n_bins: int = 10) -> float:
    """Expected calibration error with equal-width probability bins."""
    y = np.asarray(y_true, dtype=float)
    p = np.asarray(prob, dtype=float)
    if n_bins < 1:
        raise ValueError("n_bins must be positive")
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    idx = np.clip(np.digitize(p, edges[1:-1], right=True), 0, n_bins - 1)
    ece = 0.0
    for b in range(n_bins):
        mask = idx == b
        if not mask.any():
            continue
        ece += mask.mean() * abs(p[mask].mean() - y[mask].mean())
    return float(ece)
