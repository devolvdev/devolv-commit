import subprocess
from .utils import parse_diff

def generate_commit_message():
    """
    Generate a professional and structured Git commit message from staged changes.
    Deduplicates, prioritizes by type, and formats clearly.
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
    unique_actions = []
    for action in actions:
        normalized = action.rstrip(".")
        if normalized not in seen:
            seen.add(normalized)
            unique_actions.append(normalized)

    # Prioritize common verbs
    def priority(action):
        a = action.lower()
        if a.startswith("removed"): return 0
        if a.startswith("deleted"): return 1
        if a.startswith("added"): return 2
        if a.startswith("created"): return 3
        if a.startswith("defined"): return 4
        if a.startswith("updated"): return 5
        if a.startswith("refactored"): return 6
        if a.startswith("extended"): return 7
        if a.startswith("cleaned"): return 8
        return 9

    sorted_actions = sorted(unique_actions, key=priority)

    # Format output professionally
    count = len(sorted_actions)

    if count == 1:
        return sorted_actions[0] + "."
    elif count == 2:
        return f"{sorted_actions[0]} and {sorted_actions[1]}."
    elif count <= 4:
        return ", ".join(sorted_actions[:-1]) + f", and {sorted_actions[-1]}."
    else:
        bullets = [f"- {a}." for a in sorted_actions[:5]]
        bullets.append("- ...and more")
        return "Summary of changes:\n" + "\n".join(bullets)
