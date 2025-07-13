# devolv-commit

✨ Auto-generate meaningful, smart Git commit messages based on staged code changes.

No more `git commit -m "fix stuff"` — just run `git dc`, and you're done.

---

## 🚀 Features

- 🔍 Analyzes staged diffs to understand your code changes
- 🧠 Generates human-like commit messages
- 🪝 Optional Git hook to auto-fill commit messages
- ✅ Clean, professional output — no templates or fluff
- ♻️ Follows [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) for standardization
- ⚡️ Blazing fast — not AI-powered, but built with a lean homegrown engine
- 🧪 Test suite with coverage

---

## 📦 Installation

```bash
pip install devolv-commit
```

---

## 💡 Usage

Generate a commit message and commit it:

```bash
git dc
```
---

## 📥 Manually Install Git Hook (Optional)

Automatically generate a commit message when you run `git commit`:

```bash
git dc install-hook
```

This installs a `prepare-commit-msg` hook that fills in the message field.
You can edit it before committing.

---

## 🧪 Testing

Run tests with coverage:

```bash
pytest --cov=devolv_commit --cov-report=term-missing
```

---

## ✅ Conventional Commit Support

We follow the [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) standard to enhance changelogs, release notes, and CI workflows.

Example commit messages:

- `feat: add support for multi-file diffs`
- `fix(core): handle edge case in parser`
- `refactor(utils): clean up class detection logic`

---

## 📜 License

MIT © [Devolvdev](https://github.com/devolvdev)