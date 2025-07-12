import subprocess
from pathlib import Path
import typer
from .core import generate_commit_message

app = typer.Typer()

HOOK_SCRIPT = "#!/bin/sh\nexec git dc commit --print > \"$1\"\n"

@app.command()
def commit(print_only: bool = typer.Option(False, "--print", help="Only print the generated message (used by Git hook)")):
    """
    Auto-generate a smart Git commit message and optionally commit it.
    """
    message = generate_commit_message()
    if not message:
        raise typer.Exit(code=0)

    if print_only:
        print(message)
    else:
        subprocess.run(["git", "commit", "-m", message], check=False)

@app.command()
def install_hook():
    """
    Manually install the Git hook for automatic commit message generation.
    """
    result = subprocess.run(["git", "rev-parse", "--git-dir"], capture_output=True, text=True)
    if result.returncode != 0:
        typer.echo("❌ Not a Git repository.")
        raise typer.Exit(code=1)

    git_dir = Path(result.stdout.strip())
    hook_path = git_dir / "hooks" / "prepare-commit-msg"
    hook_path.write_text(HOOK_SCRIPT)
    hook_path.chmod(0o755)

    typer.echo(f"✅ Installed prepare-commit-msg hook at {hook_path}")

@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    """
    If no subcommand is provided (e.g., `git dc`), auto-commit directly.
    """
    if ctx.invoked_subcommand is None:
        # Bypass CLI parsing to force auto-commit behavior
        commit(print_only=False)


if __name__ == "__main__":
    app()
