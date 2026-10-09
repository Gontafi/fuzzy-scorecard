import numpy as np
import pytest

from fuzzyscore import MonotoneFuzzyScorecard, make_synthetic_loans, roc_auc
from fuzzyscore.data import DEFAULT_DIRECTIONS, DEFAULT_KNOTS


@pytest.fixture(scope="module")
def fitted():
    X, y = make_synthetic_loans(8000, seed=11)
    model = MonotoneFuzzyScorecard(DEFAULT_KNOTS, DEFAULT_DIRECTIONS, l1=1e-3).fit(X, y)
    return model, X, y


def test_weights_are_non_negative(fitted):
    model, _, _ = fitted
    assert np.all(model.coef_ >= 0)
    assert model.n_active_terms_ > 0


def test_out_of_sample_auc_is_reasonable(fitted):
    model, _, _ = fitted
    X_te, y_te = make_synthetic_loans(8000, seed=12)
    assert roc_auc(y_te, model.predict_proba(X_te)) > 0.72


@pytest.mark.parametrize("col,direction", [(0, -1), (1, 1), (2, 1)])
def test_score_is_monotone_in_each_feature(fitted, col, direction):
    model, X, _ = fitted
    base = X[:200].copy()
    grid = np.linspace(X[:, col].min(), X[:, col].max(), 25)
    prev = None
    for g in grid:
        cur = base.copy()
        cur[:, col] = g
        s = model.decision_function(cur)
        if prev is not None:
            assert np.all(direction * (s - prev) >= -1e-9)
        prev = s


def test_explanation_sums_to_logit(fitted):
    model, X, _ = fitted
    for i in range(5):
        rows = model.explain(X[i])
        total = model.intercept_ + sum(c for _, _, c in rows)
        assert total == pytest.approx(model.decision_function(X[i : i + 1])[0])
        assert all(0 < mu <= 1 for _, mu, _ in rows)


def test_larger_l1_gives_sparser_scorecard():
    X, y = make_synthetic_loans(6000, seed=5)
    light = MonotoneFuzzyScorecard(DEFAULT_KNOTS, DEFAULT_DIRECTIONS, l1=1e-4).fit(X, y)
    heavy = MonotoneFuzzyScorecard(DEFAULT_KNOTS, DEFAULT_DIRECTIONS, l1=5e-2).fit(X, y)
    assert heavy.n_active_terms_ <= light.n_active_terms_


def test_validation_errors():
    with pytest.raises(ValueError):
        MonotoneFuzzyScorecard({"a": [0, 1]}, {})
    with pytest.raises(ValueError):
        MonotoneFuzzyScorecard({"a": [0, 1]}, {"a": 2})
    with pytest.raises(ValueError):
        MonotoneFuzzyScorecard({"a": [0, 1]}, {"a": 1}, l1=-1)
    model = MonotoneFuzzyScorecard({"a": [0, 1]}, {"a": 1})
    with pytest.raises(RuntimeError):
        model.predict_proba(np.zeros((2, 1)))
    with pytest.raises(ValueError):
        model.fit(np.zeros((3, 2)), np.zeros(3))
