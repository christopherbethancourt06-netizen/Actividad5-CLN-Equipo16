# Adaptación U5 al PIA — Eventos Nova

Pruebas pytest de la Unidad 5 escritas sobre el **código real** de Eventos Nova (repositorio del equipo incluido en
`Eventosnova.zip`, último commit `6b501af` del 22/10/2026 **más los cambios locales sin confirmar** que contenía la copia
entregada: 24 archivos modificados y 93 archivos nuevos sin confirmar en `src/` y `tests/`). Se probó ese estado tal como se entregó.

No se modificó ningún archivo de `src/` del PIA ni de su suite existente. Lo nuevo es la carpeta `tests_u5/`.

## 1. Reglas seleccionadas (documentación aprobada)

| Regla | Fuentes | Casos |
|---|---|---|
| **R1** Servicio adicional: mínimo cinco días naturales y orden de verificación (evento → plazo → saldo) | BN-004, SE-004, GL-015; US-025, CA-073, CA-075, CA-083 | PIA-01 a PIA-04 (+ PIA-03b) |
| **R2** Anticipo: al menos 30 % en tres días hábiles desde la firma; contacto y 24 horas naturales | BN-009, SE-010, GL-060; US-009/US-010, CA-019 a CA-021; decisión B del cierre de alcance | PIA-05 a PIA-09 |
| **R3** Cambio tardío: con menos de siete días naturales, cargo por la tarifa vigente separado del costo del proveedor; sin cambios tras el inicio | BN-003, SE-003, SE-005, GL-020, GL-025; US-024, CA-039, CA-061 a CA-063 | PIA-10 a PIA-13 |
| **R4** Pago de servicio adicional: 24 horas naturales desde la solicitud de pago; cierre por falta de pago | BN-004, GL-045, GL-060; US-025, CA-080, CA-082 | PIA-14 a PIA-16 |
| Integración: persistencia en PostgreSQL y dobles de prueba de los puertos externos | ADR-004; puertos `IVerificadorPagos`, `IConsultaDisponibilidadProveedor` | PIA-17 a PIA-21 |

La matriz completa con trazabilidad está en `../matriz_pruebas_PIA.csv` (22 casos).

## 2. Cómo integrarlas en el repositorio del PIA

1. Copiar la carpeta `tests_u5/` a la raíz del repositorio `Eventosnova/` (al lado de `src/` y `tests/`).
2. Instalar las dependencias del equipo y pytest:
   ```bash
   python -m pip install -r requirements-dev.txt
   python -m pip install "pytest>=8,<10" "pytest-cov>=5,<8"
   ```
3. Ejecutar:
   ```bash
   python -m ruff check tests_u5
   python -m pytest tests_u5 -v -rxX
   python -m pytest tests_u5 --cov=src --cov-branch --cov-report=term --cov-report=html:htmlcov_u5
   ```
4. Las pruebas PIA-17 a PIA-19 usan la base **de pruebas** de PostgreSQL (`TEST_DATABASE_URL`, nombre terminado en `_test`),
   igual que `tests/apoyo_bd.py`. Sin base se **omiten**; con `EVENTOSNOVA_REQUIERE_BD=1` **fallan**. El resto no necesita base.

Paso de CI **propuesto** (no aplicado al `ci.yml` del equipo), después de la suite con `unittest`:
```yaml
      - name: Pruebas U5 (pytest)
        run: |
          python -m pip install "pytest>=8,<10" "pytest-cov>=5,<8"
          python -m pytest tests_u5 -v -rxX
```

## 3. Resultados de la verificación local (27/10/2026)

| Ejecución | Resultado |
|---|---|
| `pytest tests_u5` (PostgreSQL 16 local, `EVENTOSNOVA_REQUIERE_BD=1`) | **21 aprobadas, 1 xfail** (hallazgo U5-H1) |
| `ruff check tests_u5` | Sin errores |
| Cobertura de `src/` solo con `tests_u5` | 50.4 % (líneas + ramas). Se esperaba: son 22 pruebas enfocadas en 4 reglas |
| Suite existente del equipo (`unittest`, 1 306 pruebas) + `tests_u5` | Sentencias **98.82 %**, ramas 95.85 % (mínimo 80 %: cumple) |
| Suite existente del equipo sola | 1 306 pruebas, **1 fallo** (`test_openapi_exportada`), ver incidencia I-PIA-1 |

Registros en `../evidencias/E9/`. Reportes HTML: `htmlcov_u5/` (solo U5) y `htmlcov_pia_completo/` (suite del equipo + U5).

## 4. Hallazgos y observaciones

- **U5-H1 (hallazgo, prueba `xfail` PIA-03b).** `GestionServiciosAdicionalesService.evaluar_disponibilidad_servicio_adicional()`
  consulta al puerto de proveedores **antes** de que el dominio rechace el cambio de estado de una solicitud que ya es
  *No procedente*. El estado final es correcto (el dominio rechaza), pero se hace una consulta externa que CA-083 dice no
  realizar. Corrección **propuesta, no aplicada**: comprobar que la solicitud está en un estado que admite la búsqueda antes de
  llamar a `_buscar_proveedor_servicio_adicional()`.
- **U5-O1 (ambigüedad).** Los documentos no precisan si los «días naturales» se cuentan por fecha de calendario o por periodos de
  24 horas. El código cuenta fechas de calendario: una solicitud del 15/11 a las 23:59 tiene «cinco días» para un evento del 20/11 a
  las 18:00 aunque falten 4 días 18 horas (PIA-02). Se registra para que el equipo lo confirme; no se cambió.
- **U5-O2 (análisis).** Con el saldo exigible tres días hábiles antes del evento (BN-005) y el mínimo de cinco días naturales para un
  servicio adicional (SE-004), cuando el saldo ya está vencido nunca quedan cinco días naturales (como máximo cuatro). En una
  solicitud **nueva** de servicio adicional el motivo de plazo siempre se informa antes que el de saldo vencido. Es consecuencia del
  orden aprobado, no un defecto.
- **I-PIA-1 (incidencia de entorno).** `tests/test_openapi_exportada.py` falla en este entorno: con Pydantic 2.13.5 el esquema
  generado añade un `pattern` a 8 campos decimales que el archivo `docs/api/openapi.json` del equipo (exportado con Pydantic
  2.14.1, la versión de su entorno) no tiene. No es un cambio del código. Debe confirmarse en el entorno del equipo.

## 5. Diferencias entre la guía de la actividad y la documentación aprobada

Se siguieron los documentos aprobados (BRD corregido, US/CA, glosario y `Cierre_Alcance_Eventos_Nova_FINAL_APROBADO_20261023.md`).

| Punto de la guía | Documento aprobado | Decisión |
|---|---|---|
| Anticipo del 30 % | «Como mínimo» el 30 % (BN-009, CA-019, decisión B) | Se prueba como mínimo (PIA-06, PIA-07) |
| Pago final siete días antes del evento | Saldo **tres días hábiles** antes (BN-005) | No se prueba la regla de la guía |
| Cambio con < 7 días: «cargo fijo» | Cargo por cambio tardío según la **tarifa vigente** al registrar, solo si el cambio es viable, aceptado y realizado (SE-003, SE-005, GL-025) | La tarifa es un dato de entrada; 500.00 es un ejemplo |
| Autorización de Administración «cuando corresponda» en servicios adicionales | Autorización **obligatoria** después de la aprobación del Cliente (BN-004) | Se sigue el BRD |
| Saldo vencido «antes de procesar» un servicio adicional | Se verifica **al final**: evento → plazo → saldo (SE-004, GL-015) | Se prueba el orden aprobado (PIA-04) |
| «No reembolso» | Política de no reembolso incluida y comunicada (BN-009); además existen dos devoluciones aprobadas (SE-012 y decisión A) | No se prueban devoluciones en U5 |

## 6. Pendiente

- Copiar `tests_u5/` al repositorio real del equipo, hacer commit y, si el equipo lo decide, añadir el paso de CI propuesto.
- Ejecutar la suite en el entorno del equipo (Windows, Python 3.13, PostgreSQL 18 de Docker) y en GitHub Actions; aquí se usó
  PostgreSQL 16 local.
- Decidir sobre U5-H1 y U5-O1.
