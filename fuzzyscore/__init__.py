"""fuzzyscore: a small toolkit for monotone fuzzy scorecards.

The package builds Ruspini partitions over credit features, turns them into
cumulative fuzzy terms and fits a sparse logistic scorecard whose weights are
constrained to be non-negative, so that every term moves the score in the
agreed risk direction.
"""

from fuzzyscore.data import make_synthetic_loans
from fuzzyscore.metrics import brier_score, expected_calibration_error, roc_auc
from fuzzyscore.model import MonotoneFuzzyScorecard
from fuzzyscore.partitions import cumulative_terms, ruspini_partition

__all__ = [
    "MonotoneFuzzyScorecard",
    "brier_score",
    "cumulative_terms",
    "expected_calibration_error",
    "make_synthetic_loans",
    "roc_auc",
    "ruspini_partition",
]

__version__ = "0.1.0"
