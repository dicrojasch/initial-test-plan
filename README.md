# initial-test-plan

Repositorio de demostración de un pipeline de CI/CD para Python usando
**Pytest**, **Ruff** y **Semgrep**, ejecutado en un runner self-hosted de GitHub
Actions.

## Estructura del proyecto

```
.
├── .github/
│   ├── scripts/
│   │   └── ai_reviewer.py  # Agente de revisión de código con Gemini
│   └── workflows/
│       └── ci.yml          # Workflow de GitHub Actions (raíz del repositorio)
├── demo-ci-pipeline/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── database.py     # Acceso a datos (consultas parametrizadas)
│   │   └── services.py     # Lógica de negocio
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_services.py
│   ├── requirements.txt
│   └── README.md
└── README.md
```

> **Importante:** GitHub Actions solo lee workflows ubicados en
> `.github/workflows/` en la **raíz** del repositorio. Por eso el archivo
> `ci.yml` vive en la raíz y apunta al código dentro de `demo-ci-pipeline/`.

## Cómo disparar el pipeline

1. Crea una rama desde `main`, por ejemplo `git checkout -b mi-cambio`.
2. Haz tus cambios y sube la rama:

   ```sh
   git push -u origin mi-cambio
   ```

3. Abre un **Pull Request** hacia `main`. El workflow `CI` se ejecuta
   automáticamente porque está configurado con `on: pull_request` hacia `main`.

El pipeline ejecuta tres jobs en runners self-hosted
(`runs-on: [self-hosted, Linux, ARM64]`):

- **`lint-and-test`** — ejecuta `ruff check .` y `pytest` dentro de
  `demo-ci-pipeline/`.
- **`semgrep-sast`** — ejecuta Semgrep vía Docker local con `--error`.
- **`ai-review`** — revisa el diff del PR con Gemini y publica el comentario
  automáticamente.

## Qué valida el pipeline

- **Ruff** revisa la calidad del código (`ruff check .`) y falla ante problemas
  como imports sin usar (`F401`).
- **Pytest** ejecuta las pruebas unitarias de `tests/`.
- **Semgrep** (`semgrep scan --config=auto --error`) detecta vulnerabilidades de
  seguridad, como inyecciones SQL, y falla si encuentra hallazgos bloqueantes.

Este repositorio nació con fallos intencionales (un `import sys` sin usar y una
consulta SQL construida con f-strings) para demostrar cómo los detecta el
pipeline. Ya están corregidos:

- `app/services.py`: se eliminó el import sin usar.
- `app/database.py`: la consulta ahora usa parámetros:

  ```python
  cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
  ```

Con esto, ambos jobs del pipeline pasan.

## Revisión de código con IA (Gemini)

El job **`ai-review`** analiza los cambios del Pull Request con el modelo
`gemini-2.5-flash` (SDK oficial `google-genai`) y publica la evaluación como
comentario en el PR. Se ejecuta siempre (`if: always()`), sin importar si los
jobs anteriores pasaron o fallaron.

### Configurar el secreto de la API

1. Obtén una API key en [Google AI Studio](https://aistudio.google.com/).
2. En GitHub, ve a **Settings → Secrets and variables → Actions**.
3. Pulsa **New repository secret** y crea:
   - **`GEMINI_API_KEY`** — tu clave de Google AI Studio.
   - **`GITHUB_TOKEN`** — GitHub lo provee automáticamente; no es necesario
     crearlo, pero el workflow lo lee vía `${{ secrets.GITHUB_TOKEN }}`.

> El job usa `permissions: pull-requests: write` para poder publicar el
> comentario en el PR.

### Cómo funciona

En cada Pull Request:

1. El job descarga el historial completo (`fetch-depth: 0`).
2. Genera el diff con `git diff origin/main...HEAD > pr_diff.patch`.
3. `ai_reviewer.py` envía el diff a Gemini con un prompt de *Senior Code
   Reviewer* (diseño, mantenibilidad y mejoras accionables).
4. Publica el resultado en el PR mediante la API REST de GitHub.

## Ejecutar localmente

```sh
cd demo-ci-pipeline
python -m pip install -r requirements.txt
ruff check .          # linter
pytest                # pruebas unitarias
docker run --rm -v "$PWD:/src" semgrep/semgrep semgrep scan --config=auto --error
```

## Requisitos del runner self-hosted

- Etiquetas del runner: `self-hosted`, `Linux`, `ARM64`.
- Python 3 y `venv` instalados en el runner (`sudo apt install python3 python3-venv python3-pip`).
- Docker instalado y la imagen `semgrep/semgrep` ya descargada.
