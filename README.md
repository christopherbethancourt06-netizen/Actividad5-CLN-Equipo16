# Actividad 5 · Unidad 5 — Integración, Pruebas y Calidad

**Componentes de Lógica de Negocios · FIME UANL · Equipo 16**
Profesor: Miguel Ángel Gómez Marroquín.
Integrantes: Lesly Adamaris Cotlame Nieto (2226958), Christopher Bethancourt Contreras (2226948), Francisco Mora Ruiz (2226912).

Este repositorio contiene dos alcances separados:

| Alcance | Dónde | Qué es |
|---|---|---|
| **Laboratorio base U5** | `src/`, `tests/`, `datos_prueba/`, `.github/workflows/ci.yml` | Proyecto didáctico de **pedidos** entregado por el profesor (descuento VIP, deuda, pagos simulados, cancelación). No es el PIA. |
| **Adaptación al PIA: Eventos Nova** | `pia_eventos_nova/` | Pruebas pytest escritas sobre el **código real** de Eventos Nova (repositorio del equipo), con sus propias reglas aprobadas (BRD, US/CA, glosario). |

Las reglas de pedidos (VIP, deuda, `SHIPPED`, etc.) **no** se usan en Eventos Nova, y las de Eventos Nova no se mezclan con el laboratorio.

---

## 1. Requisitos y versiones

| Herramienta | Versión requerida | Versión usada en la verificación local |
|---|---|---|
| Python | 3.11 o superior | 3.13.18 |
| pytest | `>=8,<10` | 9.1.1 |
| pytest-cov | `>=5,<8` | 6.3.0 (coverage 7.10.7) |
| SQLAlchemy | `>=2,<3` | 2.0.44 |
| Ruff | `>=0.6` | 0.16.9 |

El workflow de GitHub Actions ejecuta la suite con **Python 3.11 y 3.13**.

## 2. Instalación

**Windows PowerShell**
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## 3. Comandos

```bash
python -m ruff check src tests
python -m pytest -v
python -m pytest -v --cov=src --cov-report=term-missing --cov-report=html --cov-fail-under=80
python -m compileall -q src
bash herramientas/ci_local.sh        # las mismas etapas del workflow, en local (no sustituye a GitHub Actions)
```

El reporte HTML queda en `htmlcov/index.html` (se regenera en cada ejecución y está excluido de Git).

## 4. Arquitectura del laboratorio

```
Prueba / llamador → OrderService (application.py) → Order (domain.py)
                         │ puerto implícito `gateway.charge(importe)`
                         ▼
               Pasarela de pago (en pruebas: unittest.mock.Mock)
SqlOrderRepository (repository.py) → SQLAlchemy → SQLite EN MEMORIA (solo pruebas)
can_cancel (security.py) → política de cancelación (rol, propietario, estado, antigüedad)
```

- `src/domain.py` — `Order.confirm()`: rechaza pedidos ya confirmados (regla añadida con TDD), totales ≤ 0 y clientes con deuda; aplica 15 % de descuento VIP y deja el estado `CONFIRMED`.
- `src/application.py` — `OrderService.checkout()`: confirma y cobra; si la pasarela responde `False` lanza `RuntimeError("payment rejected")`.
- `src/repository.py` — tabla `orders` y `SqlOrderRepository.save()`; la sesión de SQLAlchemy es el límite transaccional.
- `src/security.py` — `can_cancel()`: `SHIPPED` nunca se cancela; el administrador cancela los demás estados; el propietario solo durante las primeras 24 horas (a las 24 h exactas ya no).

## 5. Pruebas

| Archivo | Tipo | Qué verifica |
|---|---|---|
| `tests/test_order.py` | Unitaria (dominio) | VIP 200 → 170, regular 200 → 200, total 0 y negativo, deuda, límites (0.01, deuda 0 / 0.01, redondeo 99.99) y TDD de doble confirmación |
| `tests/test_repository.py` | Integración (SQLAlchemy + SQLite en memoria) | Guardado, commit, lectura en sesión nueva, rollback, unicidad de `id` y `total` no nulo; limpieza de recursos |
| `tests/test_service.py` | Unitaria con mock | Pago aprobado, rechazado (VIP 200 → intento de 170), timeout, sin cobro si el dominio rechaza; riesgo documentado con `xfail` |
| `tests/test_security.py` | Unitaria (autorización) | Matriz de 10 casos con fechas fijas (`now` explícito) |
| `tests/test_casos_csv.py` | Parametrizada con datos | Casos CP01–CP15 del profesor leídos con `csv.DictReader` desde `datos_prueba/` |

Los CSV de `datos_prueba/` son datos **didácticos y ficticios** y se leen expresamente en `test_casos_csv.py`; no se cargan solos.
La base `pedidos_prueba.sqlite3` del profesor **no** se usa: las pruebas de repositorio crean una base SQLite en memoria por prueba.

**Riesgo conocido (no corregido):** `checkout()` confirma el pedido antes de conocer el resultado del pago; si el pago se rechaza el pedido queda `CONFIRMED`. Está documentado con una prueba `xfail(strict=True)`. La mejora propuesta se describe en el reporte; **no** se implementó.

## 6. Cobertura

`pyproject.toml` mide `src/` completo (no se excluye ningún archivo). La cobertura de líneas indica qué sentencias se ejecutaron; no demuestra que el programa esté libre de defectos (el riesgo del punto anterior existe con 100 % de líneas cubiertas).

## 7. Integración continua (GitHub Actions)

`.github/workflows/ci.yml` se ejecuta en cada push, pull request o manualmente: checkout → Python (3.11 y 3.13) → dependencias → Ruff → pytest con `--cov-fail-under=80` y reporte HTML (artefacto) → `compileall`.

**Evidencia E8 (pendiente de ejecutar en GitHub con la cuenta del equipo):**
```bash
git remote add origin https://github.com/<usuario>/<repositorio>.git
git push -u origin main                      # 1) ejecución verde
# 2) fallo controlado: cambiar en tests/test_service.py  `assert cobrado == 170`  por  `assert cobrado == 171`
git commit -am "E8: fallo controlado temporal" && git push      # ejecución roja
git revert --no-edit HEAD && git push                            # 3) ejecución verde de nuevo
```
Capturar las tres ejecuciones en la pestaña *Actions* y anotar la URL del repositorio. La protección de la rama (*branch protection / rulesets*) se configura aparte en GitHub; tener el YAML no la activa.

## 8. Historial de Git

El historial muestra el trabajo por pasos, incluido el ciclo TDD: `TDD RED` (prueba que falla) → `TDD GREEN` (implementación mínima) → `TDD REFACTOR`.

## 9. Adaptación al PIA (Eventos Nova)

Ver `pia_eventos_nova/README.md`. Resumen: 22 pruebas pytest (4 reglas aprobadas, 21 aprobadas y 1 `xfail` que documenta un hallazgo) sobre el código real, incluidas pruebas con PostgreSQL y con dobles de prueba de los puertos externos.
