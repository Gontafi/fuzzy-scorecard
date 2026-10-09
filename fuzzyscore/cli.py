"""Command line entry point: ``fuzzyscore demo``."""

from __future__ import annotations

import argparse
import json
import sys

from fuzzyscore import __version__
from fuzzyscore.data import DEFAULT_DIRECTIONS, DEFAULT_KNOTS, make_synthetic_loans
from fuzzyscore.metrics import brier_score, expected_calibration_error, roc_auc
from fuzzyscore.model import MonotoneFuzzyScorecard


def run_demo(n: int, seed: int, l1: float) -> dict:
    """Fit the scorecard on synthetic loans and evaluate on a held-out sample."""
    X_tr, y_tr = make_synthetic_loans(n, seed=seed)
    X_te, y_te = make_synthetic_loans(n, seed=seed + 1)
    model = MonotoneFuzzyScorecard(DEFAULT_KNOTS, DEFAULT_DIRECTIONS, l1=l1).fit(X_tr, y_tr)
    p = model.predict_proba(X_te)
    return {
        "version": __version__,
        "n_train": int(len(y_tr)),
        "n_test": int(len(y_te)),
        "default_rate": float(y_te.mean()),
        "auc": roc_auc(y_te, p),
        "brier": brier_score(y_te, p),
        "ece": expected_calibration_error(y_te, p),
        "active_terms": model.n_active_terms_,
        "scorecard": [{"term": t, "weight": round(w, 4)} for t, w in model.to_table()],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fuzzyscore", description="Monotone fuzzy scorecard toolkit")
    parser.add_argument("--version", action="version", version=f"fuzzyscore {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo", help="fit and evaluate a scorecard on synthetic loans")
    demo.add_argument("--n", type=int, default=20_000, help="loans per split")
    demo.add_argument("--seed", type=int, default=0)
    demo.add_argument("--l1", type=float, default=1e-3)
    demo.add_argument("--out", type=str, default=None, help="write the JSON report to this file")
    args = parser.parse_args(argv)

    if args.command == "demo":
        report = run_demo(args.n, args.seed, args.l1)
        text = json.dumps(report, indent=2)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as fh:
                fh.write(text + "\n")
        print(text)
        return 0
    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
