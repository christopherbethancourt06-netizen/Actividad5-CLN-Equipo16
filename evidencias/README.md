# Evidencias E1–E9

Cada carpeta contiene los **registros reales** de las ejecuciones (`*.log`, `*.diff`, `*.txt`, `*.xml`) y su representación en
imagen (`*.png`). Los registros empiezan con una cabecera con fecha y hora (CST), directorio, versión de Python y el comando
exacto, y terminan con el código de salida. Las imágenes se generaron con `herramientas/renderizar_registros.py` a partir de
esos mismos archivos, sin modificar el texto; cuando una imagen muestra solo un tramo, su título indica las líneas incluidas.
Las capturas `E7_05`, `E7_06`, `E9_07` y `E9_08` son capturas del navegador (Chromium) de los reportes HTML de cobertura.

Entorno: contenedor Linux, Python 3.13.18. Para Eventos Nova se usó una base PostgreSQL 16 local y efímera (CI del equipo: 18).

| ID | Objetivo | Archivos principales | Resultado observado | Requisito | Estado |
|---|---|---|---|---|---|
| E1 | Instalación y prueba inicial | `E1_01` pytest inicial, `E1_02` cobertura inicial, `E1_03` Ruff inicial, `E1_04` `pytest` sin `python -m`, `E1_05` tras la configuración | 13/13 aprobadas, cobertura 98 %; Ruff: 7 errores I001; `pytest` directo: `ModuleNotFoundError: src`; corregido: 13/13 | 5.1, 4 | Completa (local) |
| E2 | Pruebas unitarias VIP/regular, errores y límites; casos CSV | `E2_01`, `E2_02` | 16/16 en `test_order.py`; 15/15 CP01–CP15 | 5.2 | Completa |
| E3 | TDD Red–Green–Refactor | `E3_01_RED`, `E3_02` diff, `E3_03_GREEN`, `E3_04` suite, `E3_05` diff refactor, `E3_06` suite, `E3_07` historial Git | RED: `DID NOT RAISE ValueError`; GREEN: aprobada; suite completa aprobada | 5.3 | Completa |
| E4 | Persistencia, commit, rollback y restricciones | `E4_01` | 8/8 aprobadas | 5.4 | Completa |
| E5 | Pasarela simulada | `E5_01` | 7 aprobadas, 1 xfail (riesgo documentado) | 5.5 | Completa |
| E6 | Autorización | `E6_01` | 20/20 aprobadas (matriz SEG-01 a SEG-10) | 5.6 | Completa |
| E7 | Ruff, cobertura y reporte HTML | `E7_01` Ruff, `E7_02` pytest + cobertura + HTML, `E7_03` ramas, `E7_04` compileall, `E7_05`/`E7_06` HTML, `junit_lab.xml` | Ruff sin errores; 69 aprobadas + 1 xfail; líneas 100 %, ramas 100 % | 5.7 | Completa |
| E8 | GitHub Actions verde → rojo → verde | `E8_01` actionlint, `E8_02`–`E8_04` simulación local, `E8_05` historial de la simulación | YAML válido; simulación local verde → rojo (aserción 171) → verde | 5.8 | **Pendiente en GitHub** (solo simulación local) |
| E9 | Adaptación al PIA Eventos Nova | `E9_00` migraciones, `E9_01`/`E9_02` suite del equipo, `E9_03`–`E9_06` pruebas U5 y cobertura, `E9_07`/`E9_08` HTML, `junit_pia_u5.xml` | U5: 21 aprobadas + 1 xfail; suite del equipo: 1 306 pruebas, 1 fallo de entorno; cobertura combinada 98.82 % | 6 | Completa (local); integración al repositorio del equipo pendiente |
