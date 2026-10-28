# Evidencias E1–E9

Cada carpeta contiene los **registros reales** de las ejecuciones (`*.log`, `*.diff`, `*.txt`, `*.xml`) y su representación en
imagen (`*.png`). Los registros empiezan con una cabecera con fecha y hora (CST), directorio, versión de Python y el comando
exacto, y terminan con el código de salida. Las imágenes se generaron con `herramientas/renderizar_registros.py` a partir de
esos mismos archivos, sin modificar el texto; cuando una imagen muestra solo un tramo, su título indica las líneas incluidas.
Las capturas de `htmlcov` son capturas del navegador (Chromium) de los reportes HTML de cobertura.

- **27/10/2026:** primera sesión. Estos registros se conservan sin cambios.
- **28/10/2026:** revisión correctiva. Los registros nuevos llevan `20261028` en el nombre. `junit_lab.xml` y `junit_pia_u5.xml`
  corresponden a la ejecución final del 28/10/2026 y son la fuente de las matrices CSV.

Entorno: contenedor Linux, Python 3.13.18. Para Eventos Nova se usó una base PostgreSQL 16 local y efímera (el CI del equipo usa 18).

| ID | Objetivo | Archivos principales | Resultado observado | Estado |
|---|---|---|---|---|
| E1 | Instalación y prueba inicial | `E1_01`–`E1_05` (27/10); `E1_06` revalidación (28/10) | 27/10: 13/13, 98 %, 7 avisos de Ruff, `pytest` directo sin `src`; corregido. 28/10: 69 aprobadas + 1 xfail | Completa |
| E2 | Pruebas unitarias y casos CSV | `E2_01`, `E2_02` | 16/16; 15/15 (CP01–CP15) | Completa |
| E3 | TDD Red–Green–Refactor | `E3_01`–`E3_07` | RED `DID NOT RAISE ValueError`; GREEN; suite completa; historial de Git | Completa |
| E4 | Persistencia | `E4_01`; `E4_02` (28/10) | 8/8; una prueba temporal que no libera el motor hace fallar la suite | Completa |
| E5 | Pasarela simulada | `E5_01`; `E5_02` (28/10) | 7 + 1 xfail; con `--runxfail` el xfail falla en la aserción del estado (causa documentada) | Completa |
| E6 | Autorización | `E6_01` | 20/20 | Completa |
| E7 | Ruff, cobertura y HTML | `E7_01`–`E7_06` (27/10); `E7_07`–`E7_11` (28/10); `junit_lab.xml` | Ruff sin errores; 69 + 1 xfail; líneas y ramas 100 %; HTML generado | Completa |
| E8 | GitHub Actions verde → rojo → verde | `E8_01` actionlint; `E8_02`–`E8_05` simulación local | YAML válido; simulación local verde → rojo → verde | **Pendiente en GitHub** (guía de pendientes, P-03) |
| E9 | Eventos Nova | `E9_00`–`E9_08` (27/10); `E9_09`–`E9_20` (28/10); `junit_pia_u5.xml` | 28/10: diagnóstico del ZIP v1; RED/GREEN U5-H1; 22/22; suite del equipo 1 306 con 1 fallo de entorno; cobertura combinada 98.83 % | Completa (local); integración en el repositorio del equipo pendiente |

Registros del 28/10/2026 en E9: `E9_09`/`E9_10` diagnóstico del ZIP v1; `E9_11` RED; `E9_12` GREEN; `E9_13` suite del equipo;
`E9_14` cobertura combinada; `E9_15` pruebas U5; `E9_16` cobertura de U5; `E9_17` Ruff; `E9_18` mensaje cuando falta el código;
`E9_19`/`E9_20` reportes HTML.
