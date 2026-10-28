# Bitácora de uso de IA — Actividad 5 (Unidad 5, CLN) · Equipo 16

Versión en texto de `docs/BITACORA_IA_ACTIVIDAD5.docx` (28/10/2026). **Estado: borrador para revisión del equipo.**
Ninguna validación humana está marcada como completada.

## 1. Herramienta y alcance

- **Herramienta:** Claude (Anthropic), en una sesión con acceso a archivos y a una terminal Linux (Python 3.13.18; PostgreSQL 16 local y efímero).
- **Sesión 1 (27/10/2026):** desarrollo de la actividad a partir del documento «ACTIVIDAD 5 — UNIDAD 5: INTEGRACIÓN, PRUEBAS Y CALIDAD».
- **Sesión 2 (28/10/2026):** revisión correctiva a partir del documento «REVISIÓN CORRECTIVA FINAL — ACTIVIDAD 5, EQUIPO 16».
- No hubo otras consultas. La IA no accedió a GitHub, no ejecutó el pipeline real y trabajó sobre una **copia** del repositorio del PIA.

## 2. Método de revisión

1. **Requisito:** la regla existe en el código del laboratorio o en un documento aprobado de Eventos Nova.
2. **Aserción:** la prueba comprueba un resultado útil y no solo ejecuta líneas.
3. **Ejecución:** la prueba se ejecutó; si es nueva, se comprobó que falla cuando la regla no se cumple.
4. **Equipo:** cada integrante puede explicar la decisión y la aprueba (pendiente).

## 3. Sesión 1 (27/10/2026) — reconstrucción a partir de los registros

No es una transcripción literal: se reconstruye con el historial de la conversación de trabajo, el historial de Git y `evidencias/`.

| Hora | Objetivo | Propuesta de la IA | Evidencia | Resultado real | Decisión |
|---|---|---|---|---|---|
| 21:14 | Diagnóstico inicial | Ejecutar suite, cobertura y Ruff antes de cambiar nada | E1_01–E1_04 | 13/13; 98 %; 7 avisos de Ruff; `pytest` directo sin `src` | Corregir configuración (`e77bcc2`) |
| 21:18 | Pruebas de dominio | VIP 200, regular 200, total 0 y −10, deuda, límites | E2_01 | 16/16 | Aceptada |
| 21:18 | TDD | Escribir primero `test_cannot_confirm_twice` | E3_01, E3_03 | RED por `DID NOT RAISE` | Aceptada |
| 21:19 | Persistencia | Fixtures con `dispose()`; commit, rollback, unicidad, NOT NULL | E4_01 | 8/8 | Aceptada |
| 21:19 | Pasarela | Mock con `spec_set`; timeout sin suponer reintentos; riesgo con `xfail` | E5_01 | 7 + 1 xfail | Aceptada; una prueba artificial descartada |
| 21:19 | Autorización | Matriz de 10 casos con fechas fijas | E6_01 | 20/20 | Aceptada |
| 21:20 | Datos del profesor | CP01–CP15 con `csv.DictReader` | E2_02 | 15/15 | Aceptada |
| 21:22–21:32 | PIA Eventos Nova | Pruebas sobre el código real (R1–R4, PostgreSQL, mocks) | E9_01–E9_06 | 21 + 1 xfail (U5-H1) | Aceptada; aserción de PIA-13 corregida |

Propuestas corregidas o rechazadas: **S1-1** prueba sin regla (`test_el_servicio_no_recibe_la_deuda_del_cliente`) → rechazada;
**S1-2** aserción `... == [] if hasattr(...) else True` → corregida a `assert ... == []`; **S1-3** reglas de la guía no aprobadas
(pago final 7 días, cargo fijo) → rechazadas; **S1-4** `xfail` de PIA-03b → verificado con `--runxfail`.

## 4. Sesión 2 (28/10/2026) — iteraciones ejecutadas

| # | Objetivo | Problema | Propuesta de la IA | Archivos | Prueba ejecutada | Resultado real | Decisión | Validación del equipo |
|---|---|---|---|---|---|---|---|---|
| 1 | Diagnóstico | `ModuleNotFoundError: domain` en 5 archivos | Comparar SHA-256, respaldar y reproducir en copia limpia | ZIP v1, `conftest.py` | E9_09, E9_10 | El ZIP v1 no traía el código del PIA (`pia_eventos_nova/src` no existía) | Integrar el código real | Pendiente |
| 2 | Corrección | Falta de código; hallazgo U5-H1 | Copia del repo con `tests_u5/`, `pytest.ini`, `conftest.py` con mensaje claro; `motivo_rechazo_registro_disponibilidad()` | `conftest.py`, `pytest.ini`, `solicitudes.py`, `servicios.py` | `test_trazabilidad_api`, suite del equipo | **Propuesta corregida:** un comentario con «CA-083» alteró la trazabilidad generada; se retiró y la prueba pasó. Suite: 1 306, 1 fallo de entorno (E9_13) | Corrección solo en la copia; parche para el equipo | Pendiente |
| 3 | Depuración | PIA-03b era `xfail` | RED sin `xfail`, GREEN, comprobar mensaje, probar sin código | `test_u5_r1_servicio_adicional_plazo.py` | E9_11, E9_12, E9_15, E9_18 | RED 1 fallo → GREEN; 22/22; sin código: mensaje de uso (código 4); con solo pytest+SQLAlchemy: 19 + 3 omitidas | PIA-03b queda como prueba normal | Pendiente |
| 4 | Reglas de Eventos Nova | — | Mantener R1–R4 con éxito, error y límite | `matriz_pruebas_PIA.csv` | `pytest tests_u5`, `ruff check tests_u5` | 22 aprobadas; Ruff sin errores | Sin cambios de reglas | Pendiente |
| 5 | Matrices y evidencias | Riesgo sumado a errores en el reporte v1; categoría «Error → Éxito» | «Riesgo documentado» separado; columna de fecha; demostrar causa del xfail y detección de conexiones abiertas | `generar_matrices.py`, CSV, `evidencias/` | E1_06, E7_07–E7_10, E5_02, E4_02 | 69 + 1 xfail; 100 % líneas y ramas; base 8/11/7 + 1 riesgo; PIA 7/9/6, 22 aprobadas | Matrices regeneradas; registros del 27/10 sin cambios | Pendiente |
| 6 | Entrega | Afirmaciones del reporte v1 desactualizadas | Documentos con la plantilla del reporte; ZIP v2 verificado en carpeta limpia | `docs/`, README, ZIP v2 | Extracción limpia y ejecución | Ver la guía de pendientes, sección 6 | v2 preparada; v1 conservada | Pendiente |

## 5. Decisiones que requieren aprobación del equipo

| ID | Decisión | Situación | Aprobación |
|---|---|---|---|
| D-1 | Aplicar la corrección U5-H1 en el repositorio real del PIA | Aplicada solo en la copia | Pendiente |
| D-2 | Agregar `tests_u5/` y `pytest.ini` al repositorio del PIA (y un paso de CI) | Preparado | Pendiente |
| D-3 | Conteo de días naturales (U5-O1): por fecha o por 24 h | Se prueba el comportamiento actual (fecha) | Pendiente |
| D-4 | Riesgo de pago del laboratorio: mantener `xfail` o implementar la propuesta | Documentado | Pendiente |
| D-5 | `test_openapi_exportada` (versión de Pydantic) | Sin confirmar en el entorno del equipo | Pendiente |

## 6. Revisión individual

| Elemento | Lesly Adamaris Cotlame Nieto | Christopher Bethancourt Contreras | Francisco Mora Ruiz |
|---|---|---|---|
| Doble confirmación (LAB-12) | Pendiente | Pendiente | Pendiente |
| Pago rechazado (LAB-27) | Pendiente | Pendiente | Pendiente |
| Corrección de importaciones (tests_u5) | Pendiente | Pendiente | Pendiente |
| Limpieza de conexiones SQLite | Pendiente | Pendiente | Pendiente |
| Aserción débil corregida (PIA-13) | Pendiente | Pendiente | Pendiente |
| Laboratorio frente a Eventos Nova | Pendiente | Pendiente | Pendiente |
| Consulta a proveedores (PIA-03b) | Pendiente | Pendiente | Pendiente |
| D-1 a D-5 | Pendiente | Pendiente | Pendiente |

Las fichas de revisión (problema, por qué se aceptó o rechazó, regla protegida, qué demuestra la aserción, resultado, qué hacer si
falla y conclusión) y las nueve preguntas de verificación están en el DOCX, secciones 8 y 9.

## 7. Reflexión

La IA cometió errores que solo aparecieron al ejecutar y revisar: una prueba que no verificaba nada, una aserción que no podía
fallar, un comentario que alteró la trazabilidad del equipo y un paquete v1 sin el código que sus pruebas importaban. La
documentación aprobada decide las reglas, la ejecución decide si una prueba sirve y la revisión del equipo decide la entrega.
