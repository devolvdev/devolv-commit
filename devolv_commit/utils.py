import re
import os
from collections import defaultdict

def split_diff(diff_text):
    sections = []
    current = None
    for line in diff_text.splitlines():
        if line.startswith("diff --git"):
            if current:
                sections.append(current)
            file_path = line.split()[3][2:]
            current = {"file": file_path, "changes": []}
        elif current is not None:
            current["changes"].append(line)
    if current:
        sections.append(current)
    return sections

def is_test_file(path):
    name = os.path.basename(path).lower()
    return "test" in name or "/tests/" in path or name.startswith("test_")

def should_ignore_line(line):
    return (
        not line.strip()
        or line.strip().startswith("#")
        or re.match(r"^\s*(import|from)\s+", line)
        or '"""' in line or "'''" in line
    )

def filter_diff_lines(changes):
    plus_lines, minus_lines = [], []
    for line in changes:
        if line.startswith(("+++", "---", "index", "@@", "new file mode", "deleted file mode")):
            continue
        if line.startswith("+"):
            content = line[1:]
            if not should_ignore_line(content):
                plus_lines.append(content)
        elif line.startswith("-"):
            content = line[1:]
            if not should_ignore_line(content):
                minus_lines.append(content)
    return plus_lines, minus_lines

def plural(word, count):
    if word == "class" and count != 1:
        return "classes"
    return f"{word}s" if count != 1 else word


def format_list(items):
    if not items:
        return ""
    if len(items) == 1:
        return f"`{items[0]}`"
    return ", ".join(f"`{i}`" for i in items[:-1]) + f", and `{items[-1]}`"

def method_group(pairs):
    grouped = defaultdict(list)
    for cls, method in pairs:
        grouped[cls].append(method)
    return grouped.items()

def detect_symbols(lines):
    classes, funcs, methods = [], [], []
    constants = []
    current_class = None

    for line in lines:
        if re.match(r'^\s*[A-Z_]+\s*=\s*.+$', line):
            constants.append(line.split("=")[0].strip())
            continue

        cls_match = re.match(r'^\s*class\s+(\w+)', line)
        if cls_match:
            current_class = cls_match.group(1)
            classes.append(current_class)
            continue

        func_match = re.match(r'^(\s*)def\s+(\w+)\(', line)
        if func_match:
            indent = len(func_match.group(1))
            name = func_match.group(2)
            if indent > 0 and current_class:
                methods.append((current_class, name))
            else:
                funcs.append(name)
                current_class = None

    return classes, funcs, methods, constants

def parse_diff(diff_text):
    actions = []

    for sec in split_diff(diff_text):
        path = sec["file"]
        changes = sec["changes"]
        base = os.path.basename(path)
        module = os.path.splitext(base)[0]
        is_test = is_test_file(path)
        new_file = any("new file mode" in l for l in changes)
        del_file = any("deleted file mode" in l for l in changes)

        plus, minus = filter_diff_lines(changes)

        if is_test:
            if new_file:
                actions.append(f"Added new test file `{base}`.")
            elif plus and minus:
                actions.append(f"Updated tests in `{base}`.")
            elif plus:
                actions.append(f"Added tests in `{base}`.")
            elif minus:
                actions.append(f"Removed tests from `{base}`.")
            continue

        if new_file:
            actions.append(f"Introduced new module `{module}`.")
            continue
        if del_file:
            actions.append(f"Removed module `{module}`.")
            continue

        a_cls, a_func, a_meth, a_const = detect_symbols(plus)
        r_cls, r_func, r_meth, r_const = detect_symbols(minus)

        if a_cls:
            actions.append(f"Added {plural('class', len(a_cls))} {format_list(a_cls)} in `{module}`.")
        if r_cls:
            actions.append(f"Removed {plural('class', len(r_cls))} {format_list(r_cls)} from `{module}`.")

        if a_func:
            actions.append(f"Added {plural('function', len(a_func))} {format_list(a_func)} in `{module}`.")
        if r_func:
            actions.append(f"Removed {plural('function', len(r_func))} {format_list(r_func)} from `{module}`.")

        for cls, methods in method_group(a_meth):
            actions.append(f"Added {plural('method', len(methods))} {format_list(methods)} to class `{cls}` in `{module}`.")
        for cls, methods in method_group(r_meth):
            actions.append(f"Removed {plural('method', len(methods))} {format_list(methods)} from class `{cls}` in `{module}`.")

        if a_const:
            actions.append(f"Defined new {plural('constant', len(a_const))} {format_list(a_const)} in `{module}`.")
        if r_const:
            actions.append(f"Removed {plural('constant', len(r_const))} {format_list(r_const)} from `{module}`.")

        if not any([a_cls, r_cls, a_func, r_func, a_meth, r_meth, a_const, r_const]):
            if plus and minus:
                actions.append(f"Refactored logic in `{module}`.")
            elif plus:
                actions.append(f"Extended logic in `{module}`.")
            elif minus:
                actions.append(f"Cleaned up logic in `{module}`.")

    return actions
