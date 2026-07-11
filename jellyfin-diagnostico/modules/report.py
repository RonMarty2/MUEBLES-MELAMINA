"""
Junta los resultados de los demás módulos en un reporte con semáforo
(🟢🟡🔴⚪) por categoría, un diagnóstico en lenguaje simple de la causa más
probable, y recomendaciones concretas. También guarda cada corrida en
logs/ con fecha y hora para poder comparar entre días.

El resto del programa arma una lista de "categorías" con esta forma:
    {"nombre": "Red", "color": "verde"|"amarillo"|"rojo"|"gris",
     "detalles": ["línea 1", "línea 2", ...],
     "recomendaciones": ["línea 1", ...]}
report.py no sabe nada de ping, SSH ni Jellyfin: solo renderiza.
"""

import csv
import os
from datetime import datetime

EMOJI = {"verde": "🟢", "amarillo": "🟡", "rojo": "🔴", "gris": "⚪"}
PRIORIDAD = {"rojo": 3, "amarillo": 2, "gris": 1, "verde": 0}


def generar_reporte_texto(categorias, meta):
    lineas = []
    lineas.append("=" * 60)
    lineas.append("DIAGNÓSTICO JELLYFIN — " + meta.get("fecha", ""))
    lineas.append(f"Modo: {meta.get('modo', 'desconocido')}")
    lineas.append("=" * 60)
    lineas.append("")

    for cat in categorias:
        emoji = EMOJI.get(cat["color"], "⚪")
        lineas.append(f"{emoji} {cat['nombre']}")
        for detalle in cat.get("detalles", []):
            lineas.append(f"   - {detalle}")
        if cat.get("recomendaciones"):
            lineas.append("   Recomendaciones:")
            for rec in cat["recomendaciones"]:
                lineas.append(f"     > {rec}")
        lineas.append("")

    causa = diagnosticar_causa_principal(categorias)
    lineas.append("-" * 60)
    lineas.append("DIAGNÓSTICO PRINCIPAL")
    lineas.append("-" * 60)
    lineas.append(causa)
    lineas.append("")

    return "\n".join(lineas)


def generar_reporte_html(categorias, meta):
    filas = []
    for cat in categorias:
        color_css = {"verde": "#2e7d32", "amarillo": "#f9a825", "rojo": "#c62828", "gris": "#757575"}[cat["color"]]
        detalles_html = "".join(f"<li>{d}</li>" for d in cat.get("detalles", []))
        recs_html = ""
        if cat.get("recomendaciones"):
            recs_html = "<p><b>Recomendaciones:</b></p><ul>" + "".join(
                f"<li>{r}</li>" for r in cat["recomendaciones"]
            ) + "</ul>"
        filas.append(
            f'<div style="border-left:6px solid {color_css}; padding:8px 16px; margin-bottom:16px;">'
            f'<h3>{EMOJI.get(cat["color"], "⚪")} {cat["nombre"]}</h3>'
            f'<ul>{detalles_html}</ul>{recs_html}</div>'
        )

    causa = diagnosticar_causa_principal(categorias).replace("\n", "<br>")

    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Diagnóstico Jellyfin</title></head>
<body style="font-family: sans-serif; max-width: 800px; margin: 40px auto;">
<h1>Diagnóstico Jellyfin — {meta.get('fecha', '')}</h1>
<p>Modo: {meta.get('modo', 'desconocido')}</p>
{''.join(filas)}
<h2>Diagnóstico principal</h2>
<p>{causa}</p>
</body></html>"""


def diagnosticar_causa_principal(categorias):
    peor = max(categorias, key=lambda c: PRIORIDAD.get(c["color"], 0))
    if PRIORIDAD.get(peor["color"], 0) == 0:
        return "Todo lo revisado está en buen estado. Si los cortes persisten, probá correr el diagnóstico en el momento exacto en que ocurre el corte, para capturar el estado real de ese instante."

    detalle_principal = peor["detalles"][0] if peor.get("detalles") else ""
    return f"La causa más probable de tus cortes está en: {peor['nombre']}.\n{detalle_principal}"


def guardar_log(reporte_texto, categorias, carpeta_logs):
    os.makedirs(carpeta_logs, exist_ok=True)
    ahora = datetime.now()
    marca = ahora.strftime("%Y%m%d_%H%M%S")

    ruta_txt = os.path.join(carpeta_logs, f"diagnostico_{marca}.txt")
    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write(reporte_texto)

    ruta_csv = os.path.join(carpeta_logs, "historial.csv")
    existe = os.path.exists(ruta_csv)
    with open(ruta_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(["timestamp", "categoria", "color"])
        for cat in categorias:
            writer.writerow([ahora.isoformat(timespec="seconds"), cat["nombre"], cat["color"]])

    return ruta_txt
