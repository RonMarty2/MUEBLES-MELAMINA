"""Genera la lista de cortes en CSV y la lista de perforaciones en Markdown.

Frontera de módulo (02_ARQUITECTURA.md): solo formatea lo que el motor ya
calculó. El CSV sirve para llevar a la tienda que corta placas (D-005); el
diagrama optimizado lo da OpenCutList dentro de SketchUp.
"""

import csv


def generar_lista_cortes(mueble, ruta_csv):
    """CSV: una fila por pieza, agrupando piezas idénticas."""
    grupos = {}
    for p in mueble.piezas:
        clave = (p.largo, p.ancho, p.espesor, p.material, p.nombre.rstrip("0123456789 ()izqder"))
        if clave in grupos:
            grupos[clave]["cantidad"] += 1
            grupos[clave]["nombres"].append(p.nombre)
        else:
            grupos[clave] = {"pieza": p, "cantidad": 1, "nombres": [p.nombre]}

    with open(ruta_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Pieza", "Cantidad", "Largo (mm)", "Ancho (mm)",
                    "Espesor (mm)", "Material", "Tapacanto", "Notas"])
        for g in grupos.values():
            p = g["pieza"]
            nombre = g["nombres"][0] if g["cantidad"] == 1 else \
                p.nombre.split(" cajón")[0].split(" (")[0] + f" (×{g['cantidad']})"
            w.writerow([nombre, g["cantidad"], p.largo, p.ancho,
                        p.espesor, p.material, p.cantos, p.notas])
    return ruta_csv


def generar_perforaciones(mueble, ruta_md):
    """Markdown con las perforaciones/marcados para el taller."""
    lineas = [
        f"# Perforaciones y marcado — {mueble.nombre}",
        "",
        f"Mueble de {mueble.dimensiones_texto()}.",
        "",
        "Coordenadas medidas desde la esquina inferior-izquierda de la cara",
        "indicada de cada pieza. Convenciones P-xx en",
        "`AI_OPERATING_SYSTEM/07_HERRAJES_Y_TORNILLERIA.md`.",
        "",
        "| Pieza | Cara | X (mm) | Y (mm) | Broca Ø | Profundidad | Para qué |",
        "|---|---|---|---|---|---|---|",
    ]
    for pf in mueble.perforaciones:
        lineas.append(
            f"| {pf.pieza} | {pf.cara} | {pf.x} | {pf.y} | {pf.diametro} mm "
            f"| {pf.profundidad} | {pf.para_que} |"
        )
    lineas += [
        "",
        "> Regla de oro: **pre-perforar SIEMPRE** antes de atornillar melamina",
        "> (R-09). Confirmat: broca escalonada o Ø4,5 pasante + Ø3 en el canto.",
        "",
    ]
    with open(ruta_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))
    return ruta_md
