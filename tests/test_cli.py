import json

from fuzzyscore.cli import main, run_demo


def test_run_demo_reports_metrics():
    rep = run_demo(n=3000, seed=0, l1=1e-3)
    assert 0.5 < rep["auc"] <= 1.0
    assert rep["active_terms"] == len(rep["scorecard"])


def test_cli_writes_json(tmp_path, capsys):
    out = tmp_path / "report.json"
    assert main(["demo", "--n", "2000", "--out", str(out)]) == 0
    data = json.loads(out.read_text())
    assert "auc" in data
    assert "auc" in capsys.readouterr().out
