# Bitácora de uso de IA — Actividad 5 (Unidad 5, CLN) · Equipo 16

**Herramienta:** Claude (Anthropic), en una sesión de trabajo con acceso a archivos y a una terminal (27/10/2026).
**Forma de uso:** el equipo entregó a la IA **un solo prompt**: el documento de instrucciones «ACTIVIDAD 5 — UNIDAD 5:
INTEGRACIÓN, PRUEBAS Y CALIDAD» (texto completo en los adjuntos de la sesión), junto con el material de la unidad y el ZIP de
Eventos Nova. No hubo otras consultas del equipo durante la sesión. Las entradas de abajo registran las **propuestas que hizo la
IA** dentro de esa sesión, cómo se contrastaron con los requisitos y con la ejecución real, y la decisión final.

**Lo que esta bitácora NO afirma:** no se usó el «prompt sugerido» de la guía del laboratorio; no hubo conversaciones adicionales;
la revisión humana del equipo sobre cada decisión queda **pendiente** y debe anotarse en la última columna antes de entregar.

Extracto del prompt real (inicio del documento de instrucciones):
> «Necesito que realices la Actividad 5 de la materia Componentes de Lógica de Negocios, correspondiente a la Unidad 5:
> Integración, Pruebas y Calidad. No quiero únicamente explicaciones… Necesito que analices los archivos adjuntos, trabajes con el
> proyecto base proporcionado por el profesor, generes los archivos necesarios, ejecutes las pruebas…»

## Registro

| # | Objetivo | Propuesta de la IA (resumen) | Revisión contra el requisito | Prueba agregada / modificada / descartada | Resultado real | Decisión final | Revisión del equipo |
|---|---|---|---|---|---|---|---|
| 1 | Identificar casos de éxito, error y límite del dominio | Casos VIP 200, regular 200, total 0 y −10, deuda, total 0.01, deuda 0 y 0.01, redondeo 99.99, prioridad total/deuda | Todos se derivan de `src/domain.py` y de los CSV del profesor; no se agregaron reglas | Agregadas 11 pruebas en `tests/test_order.py` | 16 aprobadas (E2) | Aceptada | Pendiente |
| 2 | TDD de doble confirmación | Escribir primero `test_cannot_confirm_twice` (texto de la guía), ejecutarlo, luego la guarda mínima y un refactor | Coincide con la guía; el RED debía fallar por la causa correcta | Prueba agregada antes del cambio | RED: `DID NOT RAISE ValueError`; GREEN y suite completa aprobadas (E3) | Aceptada | Pendiente |
| 3 | Probar persistencia | Fixtures con `engine.dispose()` y `filterwarnings=error::ResourceWarning`; pruebas de commit, rollback, unicidad y NOT NULL | La guía pide limpieza de recursos; la suite original dejaba conexiones SQLite abiertas (`ResourceWarning` en E1) | 6 pruebas agregadas; 2 originales adaptadas a fixtures | 8 aprobadas; se comprobó que una conexión sin cerrar ahora hace fallar la suite | Aceptada | Pendiente |
| 4 | Probar la pasarela de pago | Mock con `spec_set=["charge"]`; aprobado, rechazado (VIP 200 → 170), timeout | El código no tiene reintentos ni circuit breaker: el timeout se verifica como excepción propagada con **un** intento | 5 pruebas agregadas | Aprobadas (E5) | Aceptada sin atribuir reintentos | Pendiente |
| 5 | Documentar el riesgo de confirmar antes de pagar | Prueba `xfail(strict=True)` con la expectativa deseable en lugar de corregir el código | La guía pide anotar el riesgo como propuesta, sin ocultarlo | 1 prueba `xfail` | XFAIL (el pedido queda `CONFIRMED`) | Aceptada; la corrección queda como propuesta | Pendiente |
| 6 | **Sugerencia rechazada** | La IA escribió `test_el_servicio_no_recibe_la_deuda_del_cliente`, que confirmaba un pedido de 150 con la pasarela simulada | Al revisarla: no verificaba una regla del contrato, solo ejecutaba líneas ya cubiertas; la guía prohíbe pruebas artificiales | **Descartada** antes del commit de E5 | — | La observación (checkout no recibe la deuda) se documenta en el reporte, sin prueba | Pendiente |
| 7 | **Aserción corregida** | En PIA-13 la IA escribió `assert repo.listar_por_evento_id(...) == [] if hasattr(...) else True` | Esa expresión podía pasar sin comprobar nada (`else True`) | **Modificada** a `assert ... == []` tras confirmar que el método existe | Aprobada | Aceptada solo la versión corregida | Pendiente |
| 8 | Seleccionar reglas de Eventos Nova | Usar la lista inicial de la guía (anticipo 30 %, pago final 7 días, cargo fijo, etc.) | Contrastada con BRD, US/CA, glosario y cierre de alcance: varias diferencias (pago final = 3 días hábiles; 30 % = mínimo; cargo = tarifa vigente) | Se probaron las reglas **aprobadas**; la del «pago final 7 días» no se probó | 21 aprobadas + 1 xfail (E9) | La documentación aprobada prevalece | Pendiente |
| 9 | Hallazgo en el PIA | Esperar que, con una solicitud *No procedente*, no se consulte a proveedores (CA-083) | La IA marcó la prueba como `xfail` y **después** verificó con `--runxfail` que falla exactamente en `assert_not_called` | 1 prueba `xfail` (PIA-03b) | XFAIL: el mock se llamó 1 vez | Se reporta como hallazgo U5-H1; no se modificó el código del PIA | Pendiente |
| 10 | Límites de días naturales | Usar el 15/11 a las 23:59 como «cinco días exactos» | Los documentos no definen si se cuenta por fecha o por 24 h; el código cuenta fechas | PIA-02 prueba el comportamiento actual | Aprobada | Se registra la ambigüedad U5-O1 en lugar de suponer una regla | Pendiente |
| 11 | Calidad del CI | Corregir los 7 avisos `I001` con `ruff --fix` y añadir `pythonpath = ["."]` | Solo cambia el orden de imports y la configuración; la suite completa se volvió a ejecutar | Sin cambios de pruebas | Ruff sin errores; 13/13 aprobadas | Aceptada | Pendiente |

## Lección sobre el uso de IA

Dos propuestas de la IA (entradas 6 y 7) habrían elevado la cuenta de pruebas sin comprobar nada útil, y una tercera (entrada 8)
venía de una lista de reglas que no coincidía con los documentos aprobados. Por eso cada prueba se ejecutó y se contrastó con el
BRD, las historias de usuario y el código antes de aceptarla.
