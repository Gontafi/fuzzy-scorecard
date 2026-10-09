"""Sparse monotone fuzzy scorecard.

The model is a logistic regression over cumulative fuzzy terms. Every term is
oriented so that a larger membership means more risk, and every weight is
constrained to be non-negative. The objective is the mean log-loss plus an L1
penalty on the weights; because the weights are non-negative the penalty is
differentiable and the problem can be solved with a bound-constrained
quasi-Newton method.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import minimize

from fuzzyscore.partitions import cumulative_terms, ruspini_partition, term_labels


def _sigmoid(z: np.ndarray) -> np.ndarray:
    return 0.5 * (1.0 + np.tanh(0.5 * z))


@dataclass
class MonotoneFuzzyScorecard:
    """Logistic scorecard on cumulative fuzzy terms with non-negative weights.

    Parameters
    ----------
    knots:
        Mapping from feature name to the increasing knots of its partition.
    directions:
        Mapping from feature name to ``+1`` (risk grows with the feature) or
        ``-1`` (risk falls with the feature).
    l1:
        Strength of the L1 penalty. Larger values give sparser scorecards.
    feature_order:
        Order of the columns of ``X``. Defaults to the order of ``knots``.
    """

    knots: dict[str, list[float]]
    directions: dict[str, int]
    l1: float = 1e-3
    feature_order: list[str] | None = None
    intercept_: float = field(default=0.0, init=False)
    coef_: np.ndarray | None = field(default=None, init=False)
    labels_: list[str] = field(default_factory=list, init=False)
    n_iter_: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        if self.feature_order is None:
            self.feature_order = list(self.knots)
        missing = [f for f in self.feature_order if f not in self.directions]
        if missing:
            raise ValueError(f"directions missing for features: {missing}")
        if self.l1 < 0:
            raise ValueError("l1 must be non-negative")
        for f in self.feature_order:
            if self.directions[f] not in (-1, 1):
                raise ValueError(f"direction of {f} must be +1 or -1")

    # ------------------------------------------------------------------ design
    def transform(self, X: np.ndarray) -> np.ndarray:
        """Return the oriented cumulative term matrix for ``X``."""
        X = np.asarray(X, dtype=float)
        if X.ndim != 2 or X.shape[1] != len(self.feature_order):
            raise ValueError(f"X must have {len(self.feature_order)} columns in order {self.feature_order}")
        blocks = []
        labels = []
        for j, f in enumerate(self.feature_order):
            col = X[:, j]
            if self.directions[f] < 0:
                col = -col
                knots = [-k for k in reversed(self.knots[f])]
            else:
                knots = list(self.knots[f])
            blocks.append(cumulative_terms(ruspini_partition(col, knots)))
            labels.extend(term_labels(f, self.knots[f], self.directions[f]))
        self.labels_ = labels
        return np.hstack(blocks)

    # --------------------------------------------------------------------- fit
    def fit(self, X: np.ndarray, y: np.ndarray) -> "MonotoneFuzzyScorecard":  # noqa: UP037
        T = self.transform(X)
        y = np.asarray(y, dtype=float)
        if y.shape != (T.shape[0],):
            raise ValueError("y must be one-dimensional and match X")
        n, p = T.shape
        base = float(np.clip(y.mean(), 1e-6, 1 - 1e-6))
        theta0 = np.concatenate([[np.log(base / (1 - base))], np.zeros(p)])

        def objective(theta: np.ndarray):
            b, w = theta[0], theta[1:]
            z = b + T @ w
            pr = _sigmoid(z)
            eps = 1e-12
            loss = -np.mean(y * np.log(pr + eps) + (1 - y) * np.log(1 - pr + eps))
            loss += self.l1 * w.sum()
            r = (pr - y) / n
            grad = np.concatenate([[r.sum()], T.T @ r + self.l1])
            return loss, grad

        bounds = [(None, None)] + [(0.0, None)] * p
        res = minimize(objective, theta0, jac=True, method="L-BFGS-B", bounds=bounds)
        self.intercept_ = float(res.x[0])
        self.coef_ = np.where(res.x[1:] < 1e-9, 0.0, res.x[1:])
        self.n_iter_ = int(res.nit)
        return self

    # ----------------------------------------------------------------- predict
    def decision_function(self, X: np.ndarray) -> np.ndarray:
        self._check_fitted()
        return self.intercept_ + self.transform(X) @ self.coef_

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return _sigmoid(self.decision_function(X))

    # ----------------------------------------------------------------- explain
    def explain(self, x: np.ndarray) -> list[tuple[str, float, float]]:
        """Return ``(term, membership, contribution)`` for the active terms of one loan."""
        self._check_fitted()
        t = self.transform(np.asarray(x, dtype=float).reshape(1, -1))[0]
        rows = []
        for label, mu, w in zip(self.labels_, t, self.coef_, strict=True):
            if mu > 0 and w > 0:
                rows.append((label, float(mu), float(mu * w)))
        return rows

    def to_table(self) -> list[tuple[str, float]]:
        """Return the non-zero terms of the scorecard with their weights."""
        self._check_fitted()
        return [(lbl, float(w)) for lbl, w in zip(self.labels_, self.coef_, strict=True) if w > 0]

    @property
    def n_active_terms_(self) -> int:
        self._check_fitted()
        return int((self.coef_ > 0).sum())

    def _check_fitted(self) -> None:
        if self.coef_ is None:
            raise RuntimeError("the scorecard has not been fitted yet")
