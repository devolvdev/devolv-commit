import typer
import subprocess
from .core import generate_commit_message

app = typer.Typer()

@app.command()
def main(run: bool = typer.Option(False, "--run", help="Automatically commit using the generated message")):
    """
    Generate a smart commit message based on staged Git changes.
    If --run is set, automatically runs `git commit -m "<message>"`.
    """
    message = generate_commit_message()
    if not message:
        print("No staged changes found.")
        return

    if run:
        subprocess.run(["git", "commit", "-m", message])
    else:
        print(message)

