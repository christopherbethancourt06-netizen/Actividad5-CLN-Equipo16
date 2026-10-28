"""Convierte registros de terminal (*.log, *.diff, *.txt) en imágenes PNG para insertarlas en el reporte.

El texto NO se modifica: se escapa como HTML y se muestra con fuente monoespaciada; la barra superior indica el archivo de
origen. Las imágenes son representaciones de registros reales guardados en evidencias/, no capturas de pantalla de otro equipo.
Uso:  python herramientas/renderizar_registros.py <salida_dir> <archivo1>[:inicio-fin] [...]   (requiere Playwright + Chromium)
Con «:inicio-fin» se muestra solo ese intervalo de líneas (numeradas desde 1) y el título lo indica; el registro completo
permanece en evidencias/."""
import html
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

PLANTILLA = """<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;background:#ffffff;font-family:'DejaVu Sans',sans-serif}}
.v{{width:1180px;border:1px solid #2b2b2b;border-radius:8px;overflow:hidden;margin:8px}}
.b{{background:#2d2d2d;color:#e6e6e6;padding:7px 12px;font-size:13px;display:flex;gap:8px;align-items:center}}
.p{{width:11px;height:11px;border-radius:50%;display:inline-block}}
pre{{margin:0;background:#1e1e1e;color:#d4d4d4;padding:12px 14px;font:13px/1.38 'DejaVu Sans Mono',monospace;
white-space:pre-wrap;word-break:break-all;overflow-wrap:anywhere;overflow:hidden}}
.ok{{color:#6ad47a}} .bad{{color:#ff6b6b}} .cmd{{color:#7cc7ff}} .warn{{color:#f2c94c}} .meta{{color:#9a9a9a}}
</style></head><body><div class="v"><div class="b"><span class="p" style="background:#ff5f56"></span>
<span class="p" style="background:#ffbd2e"></span><span class="p" style="background:#27c93f"></span>
<span>&nbsp;{titulo}</span></div><pre>{texto}</pre></div></body></html>"""


def colorear(linea: str) -> str:
    e = html.escape(linea)
    if linea.startswith('# Registro:'):
        return f'<span class="meta">{e}</span>'
    if linea.startswith(('$ ', '==> ')):
        return f'<span class="cmd">{e}</span>'
    if any(k in linea for k in ('FAILED', 'Error', 'ERROR', 'FALLÓ', 'error:', 'DID NOT RAISE', 'código de salida: 1',
                                'código de salida: 2')) or linea.startswith(('-   ', '- ')):
        return f'<span class="bad">{e}</span>'
    if any(k in linea for k in ('XFAIL', 'xfailed', 'Warning')):
        return f'<span class="warn">{e}</span>'
    if any(k in linea for k in ('PASSED', ' passed', 'All checks passed', 'APROBADAS', 'reached', 'OK: cumple',
                                'código de salida: 0')) or linea.startswith(('+   ', '+ ')):
        return f'<span class="ok">{e}</span>'
    return e


def renderizar(salida: Path, archivos):
    salida.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pag = nav.new_page(viewport={'width': 1200, 'height': 600}, device_scale_factor=1.5)
        for arg in archivos:
            ruta, _, rango = arg.partition(':')
            a = Path(ruta)
            lineas = a.read_text(encoding='utf-8', errors='replace').rstrip('\n').split('\n')
            titulo, sufijo = a.name, ''
            if rango:
                ini, fin = (int(x) for x in rango.split('-'))
                total = len(lineas)
                fin = min(fin, total)
                partes = lineas[:min(2, ini - 1)]                 # se conserva la cabecera (fecha y comando)
                if ini > 3:
                    partes.append(f'[... líneas 3 a {ini - 1} omitidas en la imagen; ver el registro completo ...]')
                partes += lineas[ini - 1:fin]
                if fin < total:
                    partes.append(f'[... líneas {fin + 1} a {total} omitidas en la imagen; ver el registro completo ...]')
                lineas, titulo, sufijo = partes, f'{a.name} (líneas {ini}–{fin} de {total})', f'_l{ini}-{fin}'
            pag.set_content(PLANTILLA.format(titulo=html.escape(titulo),
                                             texto='\n'.join(colorear(x) for x in lineas)))
            destino = salida / (a.stem + sufijo + '.png')
            pag.locator('.v').screenshot(path=str(destino))
            print(destino)
        nav.close()


if __name__ == '__main__':
    renderizar(Path(sys.argv[1]), sys.argv[2:])
