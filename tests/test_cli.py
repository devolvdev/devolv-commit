import pytest
from typer.testing import CliRunner
from devolv_commit.cli import app
import typer 
runner = CliRunner()

from typer.testing import CliRunner
from devolv_commit.cli import app

runner = CliRunner()

def test_commit_no_message(monkeypatch):
    monkeypatch.setattr("devolv_commit.core.generate_commit_message", lambda: "")
    result = runner.invoke(app, ["commit"])
    assert result.exit_code == 0

def test_install_hook(monkeypatch, tmp_path):
    fake_git_dir = tmp_path / ".git"
    hooks_dir = fake_git_dir / "hooks"
    hooks_dir.mkdir(parents=True)

    monkeypatch.setattr("subprocess.run", lambda *a, **k: type("obj", (), {
        "returncode": 0,
        "stdout": str(fake_git_dir)
    }))

    result = runner.invoke(app, ["install-hook"])
    hook_file = hooks_dir / "prepare-commit-msg"
    assert result.exit_code == 0
    assert hook_file.exists()
    assert hook_file.read_text().startswith("#!/bin/sh")


def test_version_callback(monkeypatch):
    monkeypatch.setattr("devolv_commit.__version__", "1.2.3")
    result = runner.invoke(app, ["--version"])
    assert "0.1.0" in result.output

def test_default_callback_prints_version(monkeypatch):
    # Patch the __version__ inside the cli module (NOT devolv_commit.__version__)
    import devolv_commit.cli
    monkeypatch.setattr(devolv_commit.cli, "__version__", "9.9.9")

    result = runner.invoke(app, ["--version"])
    assert "9.9.9" in result.output


def test_default_callback_auto_commit(monkeypatch):
    monkeypatch.setattr("devolv_commit.core.generate_commit_message", lambda: "feat: auto commit")
    result = runner.invoke(app, [])
    assert result.exit_code == 0

def test_cli_fallback_to_commit(monkeypatch):
    monkeypatch.setattr("devolv_commit.core.generate_commit_message", lambda: "feat: auto commit")
    result = runner.invoke(app, [])
    assert result.exit_code == 0

def test_cli_callback_no_version(monkeypatch):
    # simulate no subcommand, no --version
    monkeypatch.setattr("devolv_commit.core.generate_commit_message", lambda: "feat: default commit")
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "feat: default commit" not in result.output  # not printed, just committed

