import subprocess
from .utils import parse_diff

def generate_commit_message():
    """
    Run 'git diff --cached' and generate a commit message summarizing the changes.
    """
    try:
        result = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True)
    except Exception:
        # Git not available or other error
        return ""
    diff = result.stdout
    if not diff.strip():
        return ""
    actions = parse_diff(diff)
    if not actions:
        return ""
    # If only a few actions, produce a one-line summary
    if len(actions) <= 2:
        first = actions[0].rstrip('.')
        if len(actions) == 1:
            # Single action, return it as-is
            return first
        # Two actions: join with "and", lowercase second verb (imperative style)
        second = actions[1].rstrip('.')
        second = second[0].lower() + second[1:] if second else second
        return f"{first} and {second}"
    # Otherwise, format as a bullet list of key actions
    lines = []
    for action in actions[:5]:  # limit to 5 bullets
        lines.append(f"- {action}")
    return "\n".join(lines)
