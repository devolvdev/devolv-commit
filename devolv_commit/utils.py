import re
import os

def split_diff(diff_text):
    """
    Split a unified git diff into file-by-file sections.
    """
    sections = []
    current = None
    for line in diff_text.splitlines():
        if line.startswith('diff --git'):
            if current:
                sections.append(current)
            parts = line.split()
            # parts[2] = a/..., parts[3] = b/...
            file_path = parts[3][2:]  # remove the 'b/' prefix
            current = {'file': file_path, 'changes': []}
        elif current is not None:
            current['changes'].append(line)
    if current:
        sections.append(current)
    return sections

def is_test_file(path):
    """
    Determine if the given file path corresponds to a test file.
    """
    name = os.path.basename(path).lower()
    return name.startswith('test_') or '/test_' in path or '/tests/' in path

def filter_diff_lines(changes):
    """
    From a diff hunk, filter out irrelevant lines (imports, comments, docstrings).
    Return two lists of clean added and removed code lines (without '+' or '-').
    """
    plus_lines = []
    minus_lines = []
    for line in changes:
        if line.startswith('@@'):
            continue
        if line.startswith('+++') or line.startswith('---') or line.startswith('new file mode') \
           or line.startswith('deleted file mode') or line.startswith('index'):
            continue
        if line.startswith('+'):
            content = line[1:]
            if re.match(r'^\s*(import |from )', content):
                continue
            if re.match(r'^\s*#', content):
                continue
            if '"""' in content or "'''" in content:
                continue
            plus_lines.append(content)
        elif line.startswith('-'):
            content = line[1:]
            if re.match(r'^\s*(import |from )', content):
                continue
            if re.match(r'^\s*#', content):
                continue
            if '"""' in content or "'''" in content:
                continue
            minus_lines.append(content)
    return plus_lines, minus_lines

def parse_diff(diff_text):
    """
    Parse the diff text and extract a list of high-level change actions for the commit message.
    """
    sections = split_diff(diff_text)
    actions = []
    for sec in sections:
        file_path = sec['file']
        changes = sec['changes']
        new_file = any(line.startswith('new file mode') for line in changes)
        del_file = any(line.startswith('deleted file mode') for line in changes)
        test_file = is_test_file(file_path)
        base = os.path.basename(file_path)
        # Handle test files separately
        if test_file:
            if new_file:
                actions.append(f"Add new test file {base}")
                continue
            plus_lines, minus_lines = filter_diff_lines(changes)
            if plus_lines and minus_lines:
                actions.append(f"Update tests in {base}")
            elif plus_lines:
                actions.append(f"Add tests in {base}")
            elif minus_lines:
                actions.append(f"Remove tests in {base}")
            continue
        # New or deleted file (non-test)
        if new_file:
            name = os.path.splitext(base)[0]
            actions.append(f"Add new module {name}")
            continue
        if del_file:
            name = os.path.splitext(base)[0]
            actions.append(f"Remove module {name}")
            continue
        # Filtered code lines for analysis
        plus_lines, minus_lines = filter_diff_lines(changes)
        # Detect added/removed classes
        added_classes = []
        removed_classes = []
        for content in plus_lines:
            m = re.match(r'\s*class\s+(\w+)', content)
            if m:
                added_classes.append(m.group(1))
        for content in minus_lines:
            m = re.match(r'\s*class\s+(\w+)', content)
            if m:
                removed_classes.append(m.group(1))
        # Detect added/removed functions and methods
        added_funcs = []
        added_methods = []
        current_class = None
        for content in plus_lines:
            cls_match = re.match(r'\s*class\s+(\w+)', content)
            if cls_match:
                current_class = cls_match.group(1)
                continue
            func_match = re.match(r'(\s*)def\s+(\w+)\(', content)
            if func_match:
                indent = len(func_match.group(1))
                name = func_match.group(2)
                if indent > 0 and current_class:
                    added_methods.append((current_class, name))
                else:
                    added_funcs.append(name)
                    current_class = None
        removed_funcs = []
        removed_methods = []
        current_class = None
        for content in minus_lines:
            cls_match = re.match(r'\s*class\s+(\w+)', content)
            if cls_match:
                current_class = cls_match.group(1)
                continue
            func_match = re.match(r'(\s*)def\s+(\w+)\(', content)
            if func_match:
                indent = len(func_match.group(1))
                name = func_match.group(2)
                if indent > 0 and current_class:
                    removed_methods.append((current_class, name))
                else:
                    removed_funcs.append(name)
                    current_class = None
        module = os.path.splitext(base)[0]
        # Summarize detected actions
        for c in added_classes:
            actions.append(f"Add class {c} in {module}")
        for c in removed_classes:
            actions.append(f"Remove class {c} from {module}")
        for f in added_funcs:
            actions.append(f"Add function {f} in {module}")
        for f in removed_funcs:
            actions.append(f"Remove function {f} from {module}")
        for cls, m in added_methods:
            actions.append(f"Add method {m} to class {cls} in {module}")
        for cls, m in removed_methods:
            actions.append(f"Remove method {m} from class {cls} in {module}")
        # If only code changes (no named elements added/removed), give a generic summary
        if not added_classes and not removed_classes and not added_funcs \
           and not removed_funcs and not added_methods and not removed_methods:
            if plus_lines and minus_lines:
                actions.append(f"Modify code in {module}")
            elif plus_lines:
                actions.append(f"Add code in {module}")
            elif minus_lines:
                actions.append(f"Remove code in {module}")
    return actions
