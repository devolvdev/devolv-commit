import typer
from .core import generate_commit_message

app = typer.Typer()

@app.command()
def main():
    """
    Generate and print a smart commit message based on staged Git changes.
    """
    message = generate_commit_message()
    if message:
        print(message)
    else:
        print("No staged changes found.")

if __name__ == "__main__":
    app()
