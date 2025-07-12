from devolv_commit.utils import parse_diff

def test_added_function():
    diff = '''
diff --git a/utils.py b/utils.py
new file mode 100644
+++ b/utils.py
+def my_func():
+    pass
    '''
    result = parse_diff(diff)
    assert "Introduced new module `utils`." in result

def test_removed_class():
    diff = '''
diff --git a/core.py b/core.py
index 123..456 100644
--- a/core.py
+++ b/core.py
-class RemovedClass:
-    pass
    '''
    result = parse_diff(diff)
    assert "Removed class `RemovedClass` from `core`." in result

def test_test_file_handling():
    diff = '''
diff --git a/tests/test_logic.py b/tests/test_logic.py
+++ b/tests/test_logic.py
+def test_basic():
+    assert True
    '''
    result = parse_diff(diff)
    assert "Added tests in `test_logic.py`." in result

def test_extended_and_refactored_logic_detection():
    diff = '''
diff --git a/logic.py b/logic.py
+++ b/logic.py
+print("Hello")
-print("Hi")
    '''
    result = parse_diff(diff)
    assert any("Refactored logic" in r or "Extended logic" in r for r in result)

def test_constant_and_ignore_line_detection():
    diff = '''
diff --git a/config.py b/config.py
+++ b/config.py
+MAX_RETRY = 5
+"""This is a comment"""
+import os
    '''
    result = parse_diff(diff)
    assert any("constant" in r.lower() for r in result)

from devolv_commit.utils import (
    should_ignore_line, filter_diff_lines, detect_symbols, parse_diff
)

def test_should_ignore_line_variants():
    assert should_ignore_line("")
    assert should_ignore_line("# this is comment")
    assert should_ignore_line("import os")
    assert should_ignore_line("from sys import path")
    assert should_ignore_line('""" doc """')
    assert not should_ignore_line("print('hello')")

def test_filter_diff_lines_edge_cases():
    changes = [
        "+++ b/sample.py",
        "--- a/sample.py",
        "@@ def test @@",
        "+import os",
        "-# remove me",
        "+print('add')",
        "-print('remove')"
    ]
    plus, minus = filter_diff_lines(changes)
    assert "print('add')" in plus
    assert "print('remove')" in minus
    assert "import os" not in plus

def test_detect_symbols_weird_constants():
    lines = [
        "MAX_RETRIES = 5",
        "class MyClass: pass",
        "    def method(self): pass",
        "def outer(): pass",
    ]
    classes, funcs, methods, constants = detect_symbols(lines)
    assert "MyClass" in classes
    assert "outer" in funcs
    assert ("MyClass", "method") in methods
    assert "MAX_RETRIES" in constants

def test_parse_diff_with_no_changes():
    diff = '''
diff --git a/test.py b/test.py
+++ b/test.py
    '''
    result = parse_diff(diff)
    assert result == []

def test_parse_diff_with_unstructured_changes():
    diff = '''
diff --git a/misc.py b/misc.py
+++ b/misc.py
+print("one")
+print("two")
+print("three")
    '''
    result = parse_diff(diff)
    assert "Extended logic in `misc`." in result

def test_parse_diff_cleanup_logic_only():
    diff = '''
diff --git a/sample.py b/sample.py
+++ b/sample.py
+print("new line")
-print("old line")
    '''
    result = parse_diff(diff)
    assert "Refactored logic in `sample`." in result

def test_detect_removed_symbols_and_methods():
    diff = '''
diff --git a/app.py b/app.py
+++ b/app.py
-class DeletedClass:
-    def gone(self): pass
-def vanished(): pass
-CONST = 42
    '''
    result = parse_diff(diff)
    assert "Removed class `DeletedClass` from `app`." in result
    assert "Removed function `vanished` from `app`." in result
    assert "Removed constant `CONST` from `app`." in result
    assert "Removed method `gone` from class `DeletedClass` in `app`." in result


def test_parse_diff_extended_and_cleaned_logic():
    extended = '''
diff --git a/logic.py b/logic.py
+++ b/logic.py
+print("new logic")
    '''
    cleaned = '''
diff --git a/logic.py b/logic.py
+++ b/logic.py
-print("old logic")
    '''
    assert "Extended logic" in parse_diff(extended)[0]
    assert "Cleaned up logic" in parse_diff(cleaned)[0]

