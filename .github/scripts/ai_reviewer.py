#!/usr/bin/env python3
"""AI Code Reviewer.

Reads the PR diff, asks Gemini to review it as a Senior Code Reviewer, and
posts the resulting markdown as a comment on the pull request via the GitHub
REST API.

Environment variables (required):
    GEMINI_API_KEY     Google AI Studio API key
    GITHUB_TOKEN       GitHub token with permission to comment on PRs
    PR_NUMBER          Pull request number
    GITHUB_REPOSITORY  Repository in the form "owner/name"
    DIFF_FILE          Path to the diff file (default: pr_diff.patch)
"""

import os
import sys

import requests
from google import genai

DIFF_FILE = os.environ.get("DIFF_FILE", "pr_diff.patch")
MODEL = "gemini-2.5-flash"

REVIEWER_PROMPT = """Eres un revisor de código senior. Revisa el diff y responde en español,
de forma breve y directa. Máximo 15 líneas.

Estructura:
- **Diseño**: 1-2 frases sobre arquitectura/cohesión.
- **Mantenibilidad**: 1-2 frases sobre legibilidad, nombres o duplicación.
- **Mejoras**: lista corta y priorizada de acciones concretas (con snippet solo si aporta).

Sé específico con archivos y líneas. No repitas el diff. Si no hay problemas, dilo.

Reglas anti falsos positivos:
- Solo reporta problemas reales del código del diff. No inventes.
- Verifica la API real de las librerías usadas antes de sugerir cambios.
- No sugieras cambiar algo que ya es correcto. Si dudas, omítelo.

Devuelve solo la revisión en Markdown, sin introducción ni despedida.

--- BEGIN GIT DIFF ---
{diff}
--- END GIT DIFF ---
"""


def load_diff(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Diff file not found: {path}")
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def review_with_gemini(api_key: str, diff: str) -> str:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL,
        contents=REVIEWER_PROMPT.format(diff=diff),
    )
    return response.text


def post_comment(token: str, repo: str, pr_number: str, body: str) -> None:
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {"body": body}
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    if resp.status_code >= 400:
        raise RuntimeError(
            f"Failed to post comment ({resp.status_code}): {resp.text}"
        )


def main() -> int:
    api_key = os.environ.get("GEMINI_API_KEY")
    token = os.environ.get("GITHUB_TOKEN")
    pr_number = os.environ.get("PR_NUMBER")
    repo = os.environ.get("GITHUB_REPOSITORY")

    missing = [
        name
        for name, value in (
            ("GEMINI_API_KEY", api_key),
            ("GITHUB_TOKEN", token),
            ("PR_NUMBER", pr_number),
            ("GITHUB_REPOSITORY", repo),
        )
        if not value
    ]
    if missing:
        print(f"Missing required environment variables: {', '.join(missing)}")
        return 1

    diff = load_diff(DIFF_FILE)
    if not diff.strip():
        print("Diff is empty; nothing to review.")
        return 0

    print(f"Requesting review from {MODEL} ...")
    review = review_with_gemini(api_key, diff)
    print("Posting review comment to PR ...")
    post_comment(token, repo, pr_number, review)
    print("Review posted successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
