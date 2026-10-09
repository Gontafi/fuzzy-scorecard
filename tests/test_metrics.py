import numpy as np
import pytest

from fuzzyscore.metrics import brier_score, expected_calibration_error, roc_auc


def test_auc_perfect_and_random():
    y = np.array([0, 0, 1, 1])
    assert roc_auc(y, np.array([0.1, 0.2, 0.8, 0.9])) == 1.0
    assert roc_auc(y, np.array([0.9, 0.8, 0.2, 0.1])) == 0.0
    assert roc_auc(y, np.array([0.5, 0.5, 0.5, 0.5])) == 0.5


def test_auc_matches_pairwise_definition():
    rng = np.random.default_rng(3)
    y = rng.integers(0, 2, 200)
    s = rng.normal(size=200) + y
    pos, neg = s[y == 1], s[y == 0]
    pairs = (pos[:, None] > neg[None, :]).mean() + 0.5 * (pos[:, None] == neg[None, :]).mean()
    assert roc_auc(y, s) == pytest.approx(pairs)


def test_auc_requires_both_classes():
    with pytest.raises(ValueError):
        roc_auc(np.array([1, 1]), np.array([0.2, 0.3]))


def test_brier_and_ece_on_calibrated_input():
    y = np.array([0, 1, 0, 1])
    p = np.array([0.0, 1.0, 0.0, 1.0])
    assert brier_score(y, p) == 0.0
    assert expected_calibration_error(y, p) == 0.0
    assert expected_calibration_error(y, np.full(4, 0.5)) == pytest.approx(0.0)
    assert expected_calibration_error(y, np.full(4, 0.9)) == pytest.approx(0.4)
