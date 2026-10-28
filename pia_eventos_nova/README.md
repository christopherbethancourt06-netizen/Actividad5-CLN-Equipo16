# Adaptación U5 al PIA — Eventos Nova (versión 2, 28/10/2026)

Esta carpeta contiene **el código real de Eventos Nova** y las pruebas de la Unidad 5 integradas en él:

| Ruta | Contenido |
|---|---|
| `Eventosnova/` | Copia del repositorio del equipo tomada de `Eventosnova.zip` (último commit `6b501af` del 22/10/2026 más los cambios locales sin confirmar que traía). Sin `.git`, `.venv`, `.env`, cachés ni reportes generados. |
| `Eventosnova/tests_u5/` | 22 pruebas pytest de la Unidad 5 sobre ese código |
| `Eventosnova/pytest.ini` | **Nuevo.** Hace que `pytest` recoja solo `tests_u5/` y fija la raíz de pytest en este repositorio |
| `PARCHE_U5H1_consulta_proveedores.patch` | Diferencia exacta de la corrección U5-H1 respecto al código original |
| `htmlcov_u5/`, `htmlcov_pia_completo/` | Reportes HTML de cobertura del 28/10/2026 |

## 1. Por qué fallaba la versión 1

En el ZIP v1 se entregó solo `pia_eventos_nova/tests_u5/`, **sin el código del PIA**. `tests_u5/conftest.py` agregaba a
`sys.path` las carpetas `../src` y `../tests` relativas a sí mismo, que en ese ZIP no existían. Por eso los cinco archivos de
prueba fallaban al recopilarse con `ModuleNotFoundError: No module named 'domain'` (registros `E9_09` y `E9_10`).

Corrección:
1. Las pruebas viven ahora dentro de la copia del repositorio real (`Eventosnova/tests_u5/`).
2. `conftest.py` comprueba que existan `src/domain`, `src/application`, `src/infrastructure` y `tests/apoyo_flujo.py`. Si faltan,
   detiene la ejecución con un mensaje que explica qué falta y cómo resolverlo (registro `E9_18`). La variable
   `EVENTOSNOVA_RAIZ` permite apuntar a otro repositorio.

## 2. Cómo ejecutar

Desde `pia_eventos_nova/Eventosnova/`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1                      # Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pip install "pytest>=8,<10" "pytest-cov>=5,<8" "ruff>=0.6"
python -m ruff check tests_u5
python -m pytest -v -rxX                           # recoge solo tests_u5 (pytest.ini)
python -m pytest --cov=src --cov-branch --cov-report=term --cov-report=html:htmlcov_u5
python -m unittest discover -s tests              # suite propia del equipo (1 306 pruebas)
```

**Dependencias.** Con solo `pytest` y `SQLAlchemy` instalados, 19 pruebas se ejecutan y las 3 de PostgreSQL (PIA-17 a PIA-19) se
**omiten**. Para ejecutarlas hacen falta `requirements-dev.txt`, un PostgreSQL de pruebas y `TEST_DATABASE_URL` con una base cuyo
nombre termine en `_test` (vea `.env.example`). Con `EVENTOSNOVA_REQUIERE_BD=1` la falta de base es un fallo, no una omisión.

## 3. Corrección U5-H1 (aplicada en esta copia)

`evaluar_disponibilidad_servicio_adicional()` consultaba al puerto de proveedores antes de que el dominio rechazara una solicitud
que ya era *No procedente* (CA-083 indica no continuar con la búsqueda). Se añadió
`SolicitudServicioAdicional.motivo_rechazo_registro_disponibilidad()`, que usa la misma máquina de estados y el mismo mensaje, y el
servicio rechaza antes de la consulta externa. No cambia ninguna regla de negocio ni ningún mensaje.

Verificación del 28/10/2026: RED sin `xfail` (`E9_11`), GREEN (`E9_12`), `tests_u5` 22/22 (`E9_15`), suite del equipo con 1 306
pruebas y el mismo único fallo de entorno que antes (`E9_13`). Un primer comentario del cambio citaba «CA-083» y alteraba el
documento de trazabilidad que genera el equipo (`test_trazabilidad_api` falló); se retiró la cita del comentario y la prueba volvió
a pasar.

**Pendiente del equipo:** revisar el parche y, si lo aprueban, aplicarlo y hacer commit en su repositorio real. El archivo
`MANIFIESTO_SHA256.txt` de la copia no se actualizó y no coincidirá en `servicios.py` y `solicitudes.py`.

## 4. Resultados (28/10/2026, PostgreSQL 16 local, `EVENTOSNOVA_REQUIERE_BD=1`)

| Ejecución | Resultado |
|---|---|
| `pytest tests_u5` | **22 aprobadas** |
| `ruff check tests_u5` | Sin errores |
| Cobertura de `src/` solo con `tests_u5` | 50.4 % (líneas + ramas) |
| Suite del equipo + `tests_u5` | Sentencias **98.83 %**, ramas 95.86 % |
| Suite del equipo (`unittest`) | 1 306 pruebas, 1 fallo de entorno (`test_openapi_exportada`, versión de Pydantic) |

## 5. Reglas, observaciones y diferencias con la guía

Reglas R1 a R4 y su trazabilidad: `../matriz_pruebas_PIA.csv`. La ambigüedad U5-O1 (días naturales por fecha o por 24 h), la
observación U5-O2 y la tabla de diferencias entre la guía y los documentos aprobados se mantienen como en el reporte.
