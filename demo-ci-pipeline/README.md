# Demo CI Pipeline

A minimal Python project demonstrating a CI/CD pipeline with **Pytest**, **Ruff**,
and **Semgrep** running on self-hosted GitHub Actions runners.

## Project Structure

```
demo-ci-pipeline/
├── .github/workflows/ci.yml
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

## Observing Failing Checks

This repository intentionally contains issues so the pipeline fails:

- **Ruff (lint)** fails because `app/services.py` has an unused import (`import sys`).
- **Semgrep (security)** fails because `app/database.py` uses an f-string to build a
  SQL query, which is a SQL injection vulnerability.

To see the failures:

1. Open the Pull Request on GitHub.
2. Look at the **Checks** section at the bottom of the PR.
3. Click on each failed check (`lint-and-test` or `semgrep-sast`) to view the logs.
4. Ruff will report `F401` (unused import); Semgrep will report a SQL injection
   finding and exit with an error code.

## Fixing the Checks to Pass CI

1. **Fix the unused import** in `app/services.py` by removing the line `import sys`.
2. **Fix the SQL injection** in `app/database.py` by using a parameterized query
   instead of string interpolation:

   ```python
   cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
   ```

3. Commit and push the fixes. The pipeline re-runs and should pass both jobs.

## Running Locally

```sh
python -m pip install -r requirements.txt
ruff check .          # linter
pytest                # unit tests
docker run --rm -v "$PWD:/src" semgrep/semgrep semgrep scan --config=auto --error
```
