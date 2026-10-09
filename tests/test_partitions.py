import numpy as np
import pytest

from fuzzyscore.partitions import cumulative_terms, ruspini_partition, term_labels


def test_memberships_sum_to_one():
    x = np.linspace(-10, 110, 500)
    m = ruspini_partition(x, [0, 25, 50, 75, 100])
    assert m.shape == (500, 5)
    assert np.allclose(m.sum(axis=1), 1.0)
    assert np.all(m >= 0)


def test_peaks_and_clipping():
    m = ruspini_partition(np.array([-5.0, 0.0, 12.5, 25.0, 200.0]), [0, 25, 50])
    assert np.allclose(m[0], [1, 0, 0])
    assert np.allclose(m[1], [1, 0, 0])
    assert np.allclose(m[2], [0.5, 0.5, 0])
    assert np.allclose(m[3], [0, 1, 0])
    assert np.allclose(m[4], [0, 0, 1])


def test_cumulative_terms_are_monotone_in_x():
    x = np.sort(np.random.default_rng(1).uniform(0, 100, 300))
    c = cumulative_terms(ruspini_partition(x, [0, 30, 60, 100]))
    assert c.shape == (300, 3)
    assert np.all(np.diff(c, axis=0) >= -1e-12)
    assert np.all((c >= 0) & (c <= 1))


@pytest.mark.parametrize("bad", [[1.0], [3, 2, 1], [1, 1, 2]])
def test_invalid_knots_raise(bad):
    with pytest.raises(ValueError):
        ruspini_partition(np.array([0.0, 1.0]), bad)


def test_two_dimensional_x_rejected():
    with pytest.raises(ValueError):
        ruspini_partition(np.zeros((3, 2)), [0, 1])


def test_labels_follow_direction():
    assert term_labels("ltv", [50, 80, 97], 1) == ["ltv is at least 80", "ltv is at least 97"]
    assert term_labels("fico", [600, 700, 800], -1) == ["fico is at most 700", "fico is at most 600"]
