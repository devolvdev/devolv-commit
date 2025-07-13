import pytest
from devolv_commit import utils

def test_split_diff():
    diff = "diff --git a/a.py b/a.py\n+print('hi')\n"
    result = utils.split_diff(diff)
    assert result[0]["file"] == "a.py"

def test_is_test_file():
    assert utils.is_test_file("tests/test_utils.py")
    assert not utils.is_test_file("main/app.py")

def test_should_ignore_line():
    assert utils.should_ignore_line("")
    assert utils.should_ignore_line("# comment")
    assert utils.should_ignore_line("import os")
    assert utils.should_ignore_line('""" doc """')
    assert not utils.should_ignore_line("print('hi')")

def test_filter_diff_lines():
    changes = ["+print('hi')", "-import os", "+# comment", " print('ignore')"]
    plus, minus = utils.filter_diff_lines(changes)
    assert "print('hi')" in plus
    assert not minus  # `import os` and comment ignored

def test_plural():
    assert utils.plural("class", 2) == "classes"
    assert utils.plural("function", 1) == "function"
    assert utils.plural("function", 3) == "functions"

def test_format_list():
    assert utils.format_list(["a"]) == "`a`"
    assert utils.format_list(["a", "b", "c"]) == "`a`, `b`, and `c`"

def test_method_group():
    methods = [("A", "m1"), ("A", "m2"), ("B", "m")]
    grouped = dict(utils.method_group(methods))
    assert grouped["A"] == ["m1", "m2"]
    assert grouped["B"] == ["m"]

def test_detect_symbols():
    lines = [
        "CONSTANT = 1",
        "class MyClass:",
        "    def method(self): pass",
        "def function(): pass"
    ]
    classes, funcs, methods, consts = utils.detect_symbols(lines)
    assert "MyClass" in classes
    assert "function" in funcs
    assert ("MyClass", "method") in methods
    assert "CONSTANT" in consts

def test_parse_diff_add_new_file():
    diff = (
        "diff --git a/a.py b/a.py\n"
        "new file mode 100644\n"
        "+++ b/a.py\n"
        "+def test_func():\n"
    )
    actions = utils.parse_diff(diff)
    assert actions[0][0] == "feat"

def test_parse_diff_removal_only():
    diff = (
        "diff --git a/x.py b/x.py\n"
        "deleted file mode 100644\n"
        "--- a/x.py\n"
        "-def old_func(): pass\n"
    )
    acts = utils.parse_diff(diff)
    assert acts[0][0] == "refactor"

def test_parse_diff_plus_only_ignored_lines():
    diff = (
        "diff --git a/a.py b/a.py\n"
        "+++ b/a.py\n"
        "+import os\n"
        "+# comment\n"
    )
    acts = utils.parse_diff(diff)
    assert acts == []  # no real code to act on


def test_detect_symbols_edge_case():
    lines = [
        "class Empty:",
        "    def __init__(self): pass",
        "SOME_CONST = 42",
    ]
    cls, fn, methods, consts = utils.detect_symbols(lines)
    assert "Empty" in cls
    assert ("Empty", "__init__") in methods
    assert "SOME_CONST" in consts

def test_detect_symbols_deep_cases():
    lines = [
        "# comment line",
        "'''docstring'''",
        "CONSTANT_NAME = 123",
        "class DeepClass:",
        "    def nested(self): pass",
        "def top_level(): pass",
        "class Another:",
        "    # comment",
        "    def inside(self): pass"
    ]
    c, f, m, k = utils.detect_symbols(lines)
    assert "DeepClass" in c
    assert "top_level" in f
    assert ("DeepClass", "nested") in m
    assert "CONSTANT_NAME" in k

def test_parse_diff_removes_all_types():
    diff = (
        "diff --git a/sample.py b/sample.py\n"
        "deleted file mode 100644\n"
        "--- a/sample.py\n"
        "-CONSTANT = 1\n"
        "-def my_func(): pass\n"
        "-class Bye: pass\n"
        "-    def meth(self): pass\n"
    )
    actions = utils.parse_diff(diff)
    types = [a[0] for a in actions]
    assert "refactor" in types

def test_detect_symbols_top_level_resets_class():
    lines = [
        "class ResetClass:",
        "    def method_one(self): pass",
        "def outside(): pass",  # should reset class context
        "def another(): pass",
        "CONSTANT_THING = 42"
    ]
    c, f, m, const = utils.detect_symbols(lines)
    assert "ResetClass" in c
    assert "outside" in f
    assert "another" in f
    assert "CONSTANT_THING" in const
    assert ("ResetClass", "method_one") in m

def test_method_group_multiple_classes():
    pairs = [("Alpha", "x"), ("Beta", "y"), ("Alpha", "z")]
    grouped = dict(utils.method_group(pairs))
    assert grouped["Alpha"] == ["x", "z"]
    assert grouped["Beta"] == ["y"]

def test_parse_diff_refactor_logic_no_symbols():
    diff = (
        "diff --git a/file.py b/file.py\n"
        "--- a/file.py\n"
        "+++ b/file.py\n"
        "-x = 1\n"
        "+x = 2\n"
    )
    actions = utils.parse_diff(diff)
    assert ("refactor", "refactor logic in `file`") in actions

def test_parse_diff_extend_and_cleanup_logic():
    # Extend
    diff_plus = (
        "diff --git a/foo.py b/foo.py\n"
        "+++ b/foo.py\n"
        "+x = 1\n"
    )
    assert ("feat", "extend logic in `foo`") in utils.parse_diff(diff_plus)

    # Cleanup
    diff_minus = (
        "diff --git a/bar.py b/bar.py\n"
        "--- a/bar.py\n"
        "-x = 1\n"
    )
    assert ("chore", "clean up logic in `bar`") in utils.parse_diff(diff_minus)

def test_detect_symbols_no_match_lines():
    lines = ["", "# comment", "'''doc", "import os"]
    c, f, m, const = utils.detect_symbols(lines)
    assert not any([c, f, m, const])

def test_detect_symbols_multiline_indented_funcs():
    lines = [
        "class One:",
        "    def m1(self): pass",
        "    def m2(self): pass",
        "def outside(): pass",
        "OTHER = 10"
    ]
    c, f, m, const = utils.detect_symbols(lines)
    assert "One" in c
    assert "outside" in f
    assert ("One", "m1") in m
    assert ("One", "m2") in m
    assert "OTHER" in const

def test_format_list_edge_cases():
    assert utils.format_list([]) == ""
    assert utils.format_list(["one"]) == "`one`"
    assert utils.format_list(["a", "b", "c"]) == "`a`, `b`, and `c`"

def test_split_diff_no_git_diff():
    diff = "index 1234567..89abcde 100644\n+print('hello')\n"
    result = utils.split_diff(diff)
    assert result == []

def test_detect_symbols_stray_def_outside_class():
    lines = [
        "class MyClass:",
        "    def method(self): pass",
        "def reset(): pass",  # resets current_class
        "def top(): pass"
    ]
    c, f, m, const = utils.detect_symbols(lines)
    assert "MyClass" in c
    assert ("MyClass", "method") in m
    assert "reset" in f
    assert "top" in f

def test_method_group_items_type():
    grouped = utils.method_group([("A", "m1"), ("A", "m2")])
    assert isinstance(list(grouped), list)

def test_parse_diff_logic_fallbacks():
    # Refactor fallback (plus + minus, no symbols)
    refactor = (
        "diff --git a/file.py b/file.py\n"
        "--- a/file.py\n"
        "+++ b/file.py\n"
        "-x = 1\n"
        "+x = 2\n"
    )
    assert ("refactor", "refactor logic in `file`") in utils.parse_diff(refactor)

    # Extend fallback (plus only)
    extend = (
        "diff --git a/extend.py b/extend.py\n"
        "+++ b/extend.py\n"
        "+x = 10\n"
    )
    assert ("feat", "extend logic in `extend`") in utils.parse_diff(extend)

    # Chore fallback (minus only)
    cleanup = (
        "diff --git a/clean.py b/clean.py\n"
        "--- a/clean.py\n"
        "-x = 10\n"
    )
    assert ("chore", "clean up logic in `clean`") in utils.parse_diff(cleanup)

def test_split_diff_single_block_only():
    diff = (
        "diff --git a/sample.py b/sample.py\n"
        "index 123..456\n"
        "--- a/sample.py\n"
        "+++ b/sample.py\n"
        "+print('hello')\n"
    )
    sections = utils.split_diff(diff)
    assert len(sections) == 1
    assert sections[0]["file"] == "sample.py"

def test_split_diff_single_block_only():
    diff = (
        "diff --git a/sample.py b/sample.py\n"
        "index 123..456\n"
        "--- a/sample.py\n"
        "+++ b/sample.py\n"
        "+print('hello')\n"
    )
    sections = utils.split_diff(diff)
    assert len(sections) == 1
    assert sections[0]["file"] == "sample.py"

def test_method_group_multiple_methods():
    pairs = [("A", "m1"), ("A", "m2"), ("B", "m3")]
    grouped = list(utils.method_group(pairs))
    assert ("A", ["m1", "m2"]) in grouped
    assert ("B", ["m3"]) in grouped

def test_parse_diff_logic_fallback_paths():
    # Fallback for refactor
    fallback_refactor = (
        "diff --git a/x.py b/x.py\n"
        "--- a/x.py\n"
        "+++ b/x.py\n"
        "-x = 1\n"
        "+x = 2\n"
    )
    assert ("refactor", "refactor logic in `x`") in utils.parse_diff(fallback_refactor)

    # Fallback for feat
    fallback_feat = (
        "diff --git a/y.py b/y.py\n"
        "+++ b/y.py\n"
        "+y = 10\n"
    )
    assert ("feat", "extend logic in `y`") in utils.parse_diff(fallback_feat)

    # Fallback for chore
    fallback_chore = (
        "diff --git a/z.py b/z.py\n"
        "--- a/z.py\n"
        "-z = 9\n"
    )
    assert ("chore", "clean up logic in `z`") in utils.parse_diff(fallback_chore)

