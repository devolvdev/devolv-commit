from devolv_commit.core import generate_commit_message
from unittest.mock import patch

def test_commit_message_formatting():
    mock_diff = '''
diff --git a/core.py b/core.py
+++ b/core.py
+def alpha(): pass
+def beta(): pass
+def gamma(): pass
+def delta(): pass
+def epsilon(): pass
+def zeta(): pass
    '''
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = mock_diff
        mock_run.return_value.returncode = 0
        msg = generate_commit_message()
        assert msg.startswith("Summary of changes:") or msg.startswith("Added functions")

def test_generate_commit_message_empty_diff():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = ""
        mock_run.return_value.returncode = 0
        assert generate_commit_message() == ""

def test_generate_commit_message_unparsable_diff():
    bad_diff = '''
diff --git a/core.py b/core.py
+++ b/core.py
+"""Just comments and imports"""
+import os
+import sys
    '''
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = bad_diff
        mock_run.return_value.returncode = 0
        assert generate_commit_message() == ""

from devolv_commit.core import generate_commit_message
from unittest.mock import patch

def test_generate_commit_message_with_adds_only():
    diff = '''
diff --git a/new.py b/new.py
+++ b/new.py
+def one(): pass
+def two(): pass
    '''
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = diff
        mock_run.return_value.returncode = 0
        msg = generate_commit_message()
        assert "Added" in msg

def test_generate_commit_message_with_no_actions(monkeypatch):
    monkeypatch.setattr("subprocess.run", lambda *a, **k: type("R", (), {"stdout": "", "returncode": 0})())
    assert generate_commit_message() == ""

def test_generate_commit_message_with_multiple_actions():
    diff = '''
diff --git a/mix.py b/mix.py
+++ b/mix.py
+class One: pass
+def two(): pass
+CONSTANT_X = 123
    '''
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = diff
        mock_run.return_value.returncode = 0
        msg = generate_commit_message()
        assert "class `One`" in msg
        assert "function `two`" in msg
        assert "constant `CONSTANT_X`" in msg

def test_generate_commit_message_summary_format():
    diff = '''
diff --git a/big.py b/big.py
+++ b/big.py
+def a(): pass
+def b(): pass
+def c(): pass
+def d(): pass
    '''
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = diff
        mock_run.return_value.returncode = 0
        msg = generate_commit_message()
        assert msg == "Added functions `a`, `b`, `c`, and `d` in `big`."

def test_generate_commit_message_summary_with_4_distinct_actions():
    diff = '''
diff --git a/sample.py b/sample.py
+++ b/sample.py
+class A: pass
+class B: pass
+def x(): pass
+CONST = 1
    '''
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = diff
        mock_run.return_value.returncode = 0
        msg = generate_commit_message()
        assert "Added classes" in msg
        assert "function `x`" in msg
        assert "constant `CONST`" in msg

