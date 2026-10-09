# Contributing

Create a virtual environment and install the package in editable mode with the
development extras:

    python -m venv .venv
    . .venv/bin/activate
    pip install -e ".[dev]"

Before opening a pull request run the same checks that the CI pipeline runs:

    ruff check .
    ruff format --check .
    pytest

Work happens on short-lived branches named `feature/<topic>` or `fix/<topic>`.
Every pull request targets `main`, needs a green CI run and a short description
of what changed and why. Releases are made by tagging `main` with `vX.Y.Z`;
the release workflow runs the tests, builds the wheel and attaches it to the
GitHub release.
