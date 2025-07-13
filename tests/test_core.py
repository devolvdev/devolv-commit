import pytest
from devolv_commit import core

def test_truncate_line():
    assert core.truncate_line("short") == "short"
    long = "x" * 100
    assert core.truncate_line(long).endswith("...")

def test_infer_scope():
    msgs = ["add function `utils.py`"]
    assert core.infer_scope(msgs) == "utils"
    assert core.infer_scope(["random message"]) == "core"

def test_generate_commit_message_empty(monkeypatch):
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: type("obj", (), {"stdout": "", "returncode": 0}))
    assert core.generate_commit_message() == ""

def test_generate_commit_message_valid(monkeypatch):
    diff = (
        "diff --git a/sample.py b/sample.py\n"
        "+++ b/sample.py\n"
        "+def new_function():\n"
    )
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: type("obj", (), {"stdout": diff, "returncode": 0}))
    msg = core.generate_commit_message()
    assert msg.startswith("feat")

def test_generate_commit_message_empty_diff(monkeypatch):
    class FakeResult:
        returncode = 0
        stdout = "   \n   "

    monkeypatch.setattr("subprocess.run", lambda *a, **k: FakeResult())
    assert core.generate_commit_message() == ""

def test_generate_commit_message_no_actions(monkeypatch):
    monkeypatch.setattr("subprocess.run", lambda *a, **k: type("obj", (), {"stdout": "diff --git a/a.py b/a.py\n", "returncode": 0}))
    monkeypatch.setattr("devolv_commit.core.parse_diff", lambda diff: [])
    assert core.generate_commit_message() == ""

def test_generate_commit_message_long_group(monkeypatch):
    # Simulate multiple types so it enters "Summary of changes" path
    actions = [
        ("feat", "add A"),
        ("fix", "fix B"),
        ("chore", "clean C"),
        ("refactor", "refactor D"),
        ("test", "add test E"),
        ("feat", "extend F"),
        ("fix", "resolve G"),
    ]

    monkeypatch.setattr("subprocess.run", lambda *a, **k: type("obj", (), {"stdout": "non-empty", "returncode": 0}))
    monkeypatch.setattr("devolv_commit.core.parse_diff", lambda _: actions)

    result = core.generate_commit_message()
    assert "Summary of changes:" in result
    assert "- feat(" in result or "- fix(" in result  # bullet style

def test_generate_commit_message_only_one_type(monkeypatch):
    # Single type but many messages should use multiline, not "Summary of changes"
    actions = [("feat", f"feature {i}") for i in range(6)]
    monkeypatch.setattr("subprocess.run", lambda *a, **k: type("obj", (), {"stdout": "some-diff", "returncode": 0}))
    monkeypatch.setattr("devolv_commit.core.parse_diff", lambda _: actions)
    result = core.generate_commit_message()
    assert result.startswith("feat(core): multiple changes")
    assert "- feature 0." in result
    assert "- ...and more" in result

def test_generate_commit_message_blank_diff(monkeypatch):
    class FakeResult:
        returncode = 0
        stdout = "   \n   "  # whitespace-only diff

    monkeypatch.setattr("subprocess.run", lambda *a, **k: FakeResult())
    result = core.generate_commit_message()
    assert result == ""

def test_generate_commit_message_single_message(monkeypatch):
    actions = [("feat", "add helper to `my_module.py`")]
    monkeypatch.setattr("subprocess.run", lambda *a, **k: type("obj", (), {"stdout": "mock-diff", "returncode": 0}))
    monkeypatch.setattr("devolv_commit.core.parse_diff", lambda _: actions)

    result = core.generate_commit_message()
    assert result.startswith("feat(my_module): add helper to")

def test_generate_commit_message_blank_input(monkeypatch):
    class BlankDiff:
        returncode = 0
        stdout = "   \n\n"  # whitespace-only

    monkeypatch.setattr("subprocess.run", lambda *a, **k: BlankDiff())
    assert core.generate_commit_message() == ""

def test_generate_commit_message_single_scope(monkeypatch):
    actions = [("fix", "patch bug in `xyz.py`")]
    monkeypatch.setattr("subprocess.run", lambda *a, **k: type("obj", (), {"stdout": "data", "returncode": 0}))
    monkeypatch.setattr("devolv_commit.core.parse_diff", lambda _: actions)
    result = core.generate_commit_message()
    assert result.startswith("fix(xyz): patch bug")
