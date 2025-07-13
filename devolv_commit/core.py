import subprocess
from .utils import parse_diff

MAX_LENGTH = 72  # for GitHub UI preview

def generate_commit_message():
    """
    Generate a professional Conventional Commit–style Git commit message from staged changes.
    """
    try:
        result = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True, check=True)
        diff = result.stdout
    except subprocess.CalledProcessError:
        return ""

    if not diff.strip():
        return ""

    actions = parse_diff(diff)
    if not actions:
        return ""

    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for typ, msg in actions:
        key = (typ, msg.rstrip("."))
        if key not in seen:
            seen.add(key)
            deduped.append(key)

    # Group by type
    grouped = {}
    for typ, msg in deduped:
        grouped.setdefault(typ, []).append(msg)

    if len(grouped) == 1:
        typ, messages = next(iter(grouped.items()))
        scope = infer_scope(messages)
        if len(messages) == 1:
            base = f"{typ}({scope}): {messages[0]}"
        elif len(messages) <= 4:
            base = f"{typ}({scope}): {', '.join(messages[:-1])}, and {messages[-1]}"
        else:
            base = f"{typ}({scope}): multiple changes\n" + "\n".join(f"- {m}." for m in messages[:5]) + "\n- ...and more"
        return truncate_line(base)

    bullets = [f"- {typ}({infer_scope([msg])}): {msg}." for typ, msg in deduped[:6]]
    if len(deduped) > 6:
        bullets.append("- ...and more")
    return "Summary of changes:\n" + "\n".join(bullets)

def infer_scope(messages):
    # Try extracting scope from file/module name in message
    for msg in messages:
        if "`" in msg:
            parts = msg.split("`")
            if len(parts) >= 2:
                return parts[1].replace(".py", "")
    return "core"

def truncate_line(text):
    if "\n" in text:
        return text
    return text if len(text) <= MAX_LENGTH else text[:MAX_LENGTH].rstrip() + "..."
