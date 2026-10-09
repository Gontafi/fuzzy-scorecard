# fuzzy-scorecard

[![CI](https://github.com/Gontafi/fuzzy-scorecard/actions/workflows/ci.yml/badge.svg)](https://github.com/Gontafi/fuzzy-scorecard/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)

`fuzzyscore` is a small Python toolkit for building credit scorecards from fuzzy
terms whose weights are constrained to be monotone. It is a reusable extract of the
model code written for a Master's thesis on explainable mortgage credit risk at
Astana IT University (thesis title: Fuzzy Rules-Based Mortgage Loan Valuation Model).

## What it does

1. Builds a Ruspini partition (triangular membership functions that sum to one) on
   every numeric feature from a list of knots that an analyst chooses, for example
   the usual underwriting thresholds of FICO, LTV and DTI.
2. Converts the partition into cumulative "at least" terms, oriented so that a
   larger membership always means more risk.
3. Fits a logistic scorecard with an L1 penalty and non-negative weights. Because
   the weights cannot be negative, the score is monotone in every feature by
   construction, and the L1 penalty keeps the scorecard short.
4. Explains any single score as a list of activated terms and their contributions,
   and reports ROC AUC, Brier score and expected calibration error.

## Installation

    pip install git+https://github.com/Gontafi/fuzzy-scorecard.git

or, for development,

    git clone https://github.com/Gontafi/fuzzy-scorecard.git
    cd fuzzy-scorecard
    pip install -e ".[dev]"

## Quick start

```python
from fuzzyscore import MonotoneFuzzyScorecard, make_synthetic_loans, roc_auc

knots = {"fico": [600, 640, 680, 720, 760, 800], "ltv": [50, 70, 80, 90, 97], "dti": [15, 25, 36, 43, 50]}
directions = {"fico": -1, "ltv": 1, "dti": 1}

X, y = make_synthetic_loans(20_000, seed=0)
model = MonotoneFuzzyScorecard(knots, directions, l1=1e-3).fit(X, y)

X_test, y_test = make_synthetic_loans(20_000, seed=1)
print("AUC:", roc_auc(y_test, model.predict_proba(X_test)))
for term, weight in model.to_table():
    print(f"{term:30s} {weight:+.3f}")
print(model.explain(X_test[0]))
```

The same experiment is available from the command line and is what the CI
pipeline runs as a smoke test:

    fuzzyscore demo --n 20000 --out report.json

## Project layout

    fuzzyscore/partitions.py   Ruspini partitions, cumulative terms, term labels
    fuzzyscore/model.py        MonotoneFuzzyScorecard (fit, predict_proba, explain, to_table)
    fuzzyscore/metrics.py      roc_auc, brier_score, expected_calibration_error
    fuzzyscore/data.py         synthetic loan generator and default knots
    fuzzyscore/cli.py          the `fuzzyscore demo` command
    tests/                     pytest suite (coverage gate at 90 percent)
    .github/workflows/ci.yml   lint, test matrix, build
    .github/workflows/release.yml  tagged releases

## Continuous integration

Every push and pull request to `main` runs three stages on GitHub Actions: `ruff`
lint and format check, the test suite on Python 3.10, 3.11 and 3.12 with a coverage
gate, followed by a build of the source and wheel distributions. Pushing a tag of
the form `v*` runs the tests again and attaches the built package to a GitHub release.
Dependabot opens monthly pull requests for outdated actions and Python packages.

## Why these technologies

The reasoning behind the choice of Python, NumPy and SciPy, pytest, ruff, GitHub
and GitHub Actions is written up in the Assignment 3 report (`docs/`). In short,
the stack matches the existing thesis code, has no compiled dependencies, installs
in under a minute in CI and is familiar to anyone who would audit the model.

## License

MIT. See `LICENSE`.
