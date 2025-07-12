from typer.testing import CliRunner
from devolv_commit.cli import app
from devolv_commit import __version__
import typer
import subprocess
import os
from io import StringIO
import sys

runner = CliRunner()

def test_commit_and_run_git(monkeypatch):
    monkeypatch.setattr("devolv_commit.core.generate_commit_message", lambda: "Some message")

    class DummyResult:
        def __init__(self):
            self.stdout = ""
            self.returncode = 0

    monkeypatch.setattr("subprocess.run", lambda *a, **k: DummyResult())
    result = runner.invoke(app, ["commit"])
    assert result.exit_code == 0


def test_commit_skips_on_empty_message(monkeypatch):
    monkeypatch.setattr("devolv_commit.core.generate_commit_message", lambda: "")
    result = runner.invoke(app, ["commit"])
    assert result.exit_code == 0
    assert result.output == ""


def test_install_hook(monkeypatch, tmp_path):
    git_dir = tmp_path / ".git"
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(parents=True)

    class DummyResult:
        def __init__(self):
            self.stdout = str(git_dir)
            self.returncode = 0

    monkeypatch.setattr("subprocess.run", lambda *a, **k: DummyResult())
    result = runner.invoke(app, ["install-hook"])
    assert result.exit_code == 0
    assert (hooks_dir / "prepare-commit-msg").exists()


def test_install_hook_fails_if_not_git(monkeypatch):
    class DummyResult:
        def __init__(self):
            self.returncode = 1

    monkeypatch.setattr("subprocess.run", lambda *a, **k: DummyResult())
    result = runner.invoke(app, ["install-hook"])
    assert result.exit_code == 1
    assert "Not a Git repository" in result.output


def test_default_behavior_triggers_commit(monkeypatch):
    monkeypatch.setattr("devolv_commit.core.generate_commit_message", lambda: "Msg")

    class DummyResult:
        def __init__(self):
            self.stdout = ""
            self.returncode = 0

    monkeypatch.setattr("subprocess.run", lambda *a, **k: DummyResult())
    result = runner.invoke(app, [])
    assert result.exit_code == 0


def test_cli_version_flag():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert f"devolv-commit version: {__version__}" in result.output
