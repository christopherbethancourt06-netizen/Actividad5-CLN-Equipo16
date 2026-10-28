#!/usr/bin/env bash
# Reproduce LOCALMENTE, en el mismo orden, las etapas de .github/workflows/ci.yml (Ruff → pytest con cobertura ≥ 80 % →
# compilación de src/). Sirve para comprobar un cambio antes de hacer push; NO sustituye la ejecución real en GitHub Actions.
# Uso (desde la raíz del proyecto, con el entorno virtual activo):  bash herramientas/ci_local.sh
set -u
paso() { echo; echo "==> $1"; }
paso "Ruff"
python -m ruff check src tests || { echo "PIPELINE LOCAL: FALLÓ (Ruff)"; exit 1; }
paso "Pytest con cobertura mínima del 80 %"
python -m pytest -q --cov=src --cov-report=term-missing --cov-fail-under=80 || { echo "PIPELINE LOCAL: FALLÓ (pytest)"; exit 1; }
paso "Compilar src/"
python -m compileall -q src || { echo "PIPELINE LOCAL: FALLÓ (compileall)"; exit 1; }
echo; echo "PIPELINE LOCAL: TODAS LAS ETAPAS APROBADAS"
