from __future__ import annotations

from pathlib import Path

from fishai_models import cli


def test_cli_train_invokes_rscript(monkeypatch):
    calls: list[list[str]] = []

    def fake_run(cmd, cwd, check=False):  # noqa: ARG001
        calls.append(cmd)
        return type("P", (), {"returncode": 0})()

    monkeypatch.setattr(cli.subprocess, "run", fake_run)
    rc = cli.main(["train", "--config", "configs/models/cufes_sardine.yaml"])
    assert rc == 0
    assert calls[0][0] == "Rscript"
    assert calls[0][1].endswith("train.R")
