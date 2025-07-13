import subprocess
from .utils import parse_diff

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

    # Group by type for Conventional Commit style
    grouped = {}
    for typ, msg in deduped:
        grouped.setdefault(typ, []).append(msg)

    # If only one type, use it in subject
    if len(grouped) == 1:
        (typ, messages) = list(grouped.items())[0]
        if len(messages) == 1:
            return f"{typ}: {messages[0].rstrip('.')}."
        elif len(messages) == 2:
            return f"{typ}: {messages[0]} and {messages[1]}."
        elif len(messages) <= 4:
            return f"{typ}: {', '.join(messages[:-1])}, and {messages[-1]}."
        else:
            return f"{typ}: multiple changes.\n" + "\n".join(f"- {m}." for m in messages[:5]) + "\n- ...and more"

    # Multiple types → show bullet points
    bullets = [f"- {typ}: {msg}." for typ, msg in deduped[:6]]
    if len(deduped) > 6:
        bullets.append("- ...and more")
    return "Summary of changes:\n" + "\n".join(bullets)
