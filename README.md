# initial-test-plan

Repositorio de demostración de un pipeline de CI/CD para Python usando
**Pytest**, **Ruff** y **Semgrep**, ejecutado en un runner self-hosted de GitHub
Actions.

## Estructura del proyecto

```
.
├── .github/
│   └── workflows/
│       └── ci.yml          # Workflow de GitHub Actions (raíz del repositorio)
├── demo-ci-pipeline/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── database.py     # Acceso a datos (contiene una vulnerabilidad intencional)
│   │   └── services.py     # Lógica de negocio (contiene un import sin usar)
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

El pipeline ejecuta dos jobs en runners self-hosted
(`runs-on: [self-hosted, Linux, ARM64]`):

- **`lint-and-test`** — ejecuta `ruff check .` y `pytest` dentro de
  `demo-ci-pipeline/`.
- **`semgrep-sast`** — ejecuta Semgrep vía Docker local con `--error`.

## Observar las comprobaciones que fallan

Este repositorio incluye problemas intencionales para que el pipeline falle:

- **Ruff (linter)** falla porque `demo-ci-pipeline/app/services.py` tiene un
  import sin usar (`import sys`).
- **Semgrep (seguridad)** falla porque `demo-ci-pipeline/app/database.py` usa un
  f-string para construir una consulta SQL, lo cual es una vulnerabilidad de
  inyección SQL.

Para ver los fallos:

1. Abre el Pull Request en GitHub.
2. Revisa la sección **Checks** al final del PR.
3. Haz clic en cada comprobación fallida (`lint-and-test` o `semgrep-sast`)
   para ver los logs.
4. Ruff reportará `F401` (import sin usar); Semgrep reportará una inyección SQL
   y terminará con un código de error.

## Cómo corregir los fallos para que pase el CI

1. **Corrige el import sin usar** en `demo-ci-pipeline/app/services.py`
   eliminando la línea `import sys`.
2. **Corrige la inyección SQL** en `demo-ci-pipeline/app/database.py` usando una
   consulta parametrizada en lugar de interpolar cadenas:

   ```python
   cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
   ```

3. Haz commit y sube los cambios. El pipeline se vuelve a ejecutar y ambos jobs
   deberían pasar.

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
