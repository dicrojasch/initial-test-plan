# Demo CI Pipeline

A minimal Python project demonstrating a CI/CD pipeline with **Pytest**, **Ruff**,
and **Semgrep** running on self-hosted GitHub Actions runners.

## Project Structure

```
demo-ci-pipeline/
├── app/
│   ├── __init__.py
│   ├── database.py
│   └── services.py
├── tests/
│   ├── __init__.py
│   └── test_services.py
├── requirements.txt
└── README.md
```

## Triggering the Pipeline

1. Create a branch off `main`, e.g. `git checkout -b my-change`.
2. Make your changes and push the branch:

   ```sh
   git push -u origin my-change
   ```

3. Open a **Pull Request** targeting the `main` branch. The `CI` workflow runs
   automatically because it is configured with `on: pull_request` against `main`.

The pipeline runs two jobs on self-hosted runners
(`runs-on: [self-hosted, Linux, ARM64]`):

- **`lint-and-test`** — runs `ruff check .` and `pytest`.
- **`semgrep-sast`** — runs Semgrep via Docker with `--error`.

## What the Pipeline Validates

- **Ruff** checks code quality (`ruff check .`) and fails on issues like unused
  imports (`F401`).
- **Pytest** runs the unit tests in `tests/`.
- **Semgrep** (`semgrep scan --config=auto --error`) detects security
  vulnerabilities such as SQL injection and fails on blocking findings.

This repository originally shipped with intentional flaws (an unused `import sys`
and an f-string built SQL query) to demonstrate how the pipeline catches them.
They have been fixed:

- `app/services.py`: unused import removed.
- `app/database.py`: the query now uses parameters:

  ```python
  cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
  ```

Both pipeline jobs now pass.

## Running Locally

```sh
python -m pip install -r requirements.txt
ruff check .          # linter
pytest                # unit tests
docker run --rm -v "$PWD:/src" semgrep/semgrep semgrep scan --config=auto --error
```
