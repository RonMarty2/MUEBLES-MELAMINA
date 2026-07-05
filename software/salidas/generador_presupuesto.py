"""Genera la lista de compras y el presupuesto en Markdown.

Frontera de módulo (02_ARQUITECTURA.md): no recalcula piezas ni herrajes;
solo agrupa, redondea a unidades de venta y aplica los precios de
nucleo/precios.json (editable por el usuario).
"""

import math

# Herraje H-xx -> (clave en precios.json, cómo redondear)
MAPA_PRECIOS = {
    "H-01": "confirmat_7x50",
    "H-04": "tornillo_4x30",
    "H-05": "corredera_telescopica_par",
    "H-06": "grommet_60",
    "H-07": "clavos",
    "H-08": "tapacanto_045",
    "H-09": "tapacanto_2",
    "H-10": "regaton",
    "H-11": "escuadra_25",
    "H-12": "barral_juego",
    "H-13": "bisagra_35",
    "H-14": "riel_corredizo_juego",
    "H-15": "tirador",
    "H-16": "rinconera",
    "H-17": "herraje_excentrico",
}

AREA_PLACA_M2 = 2.6 * 1.83  # placa comercial 2600×1830 (M-10)


def _estimar_placas(mueble, factor_desperdicio):
    """Placas necesarias por espesor: área de piezas × desperdicio / placa.

    Es una ESTIMACIÓN para presupuestar; el diagrama exacto lo da OpenCutList.
    """
    areas = {}
    for p in mueble.piezas:
        m = p.material.lower()
        if "melamina" not in m and "fibrof" not in m:
            continue  # herrajes tipo barral (tubo) no son piezas de placa
        areas.setdefault(p.espesor, 0.0)
        areas[p.espesor] += (p.largo / 1000) * (p.ancho / 1000)
    placas = {}
    for espesor, area in areas.items():
        placas[espesor] = max(1, math.ceil(area * factor_desperdicio / AREA_PLACA_M2))
    return areas, placas


def generar_compras_y_presupuesto(mueble, precios, ruta_compras, ruta_presupuesto):
    mon = precios.get("moneda", "$")
    factor = precios.get("factor_desperdicio_placa", 1.25)
    areas, placas = _estimar_placas(mueble, factor)

    filas = []       # (artículo, cantidad_texto, para_qué, costo o None)
    total = 0.0
    faltantes = []

    # --- Placas -------------------------------------------------------------
    for espesor, cant in sorted(placas.items(), reverse=True):
        clave = "placa_melamina_18" if espesor >= 15 else "placa_fondo_3"
        item = precios.get(clave, {})
        precio = item.get("precio")
        nombre = (f"Placa melamina {espesor} mm" if espesor >= 15
                  else f"Placa fibrofácil {espesor} mm")
        costo = precio * cant if precio is not None else None
        detalle = (f"{areas[espesor]:.2f} m² de piezas + {int((factor - 1) * 100)}% "
                   "de desperdicio estimado (el diagrama exacto lo da OpenCutList)")
        filas.append((nombre, f"{cant} placa(s) {item.get('unidad_venta', '')}", detalle, costo))
        if costo is None:
            faltantes.append(clave)
        else:
            total += costo

    # --- Servicio de corte ----------------------------------------------------
    corte = precios.get("servicio_corte_por_placa")
    if corte:
        n_placas = sum(placas.values())
        filas.append(("Servicio de corte en tienda", f"{n_placas} placa(s)",
                      "llevá la lista_cortes.csv: cortes de fábrica = precisos", corte * n_placas))
        total += corte * n_placas

    # --- Herrajes -------------------------------------------------------------
    for h in mueble.herrajes:
        clave = MAPA_PRECIOS.get(h.codigo)
        item = precios.get(clave, {}) if clave else {}
        precio = item.get("precio")
        por_venta = item.get("unidades_por_venta", 1)
        if h.unidad == "metros":
            unidades_venta = math.ceil(h.cantidad)
            cantidad_texto = f"{unidades_venta} m (necesitás {h.cantidad} m)"
        else:
            unidades_venta = math.ceil(h.cantidad / por_venta)
            envase = item.get("unidad_venta", h.unidad)
            cantidad_texto = (f"{unidades_venta} × {envase} (necesitás {int(h.cantidad)} {h.unidad})"
                              if por_venta > 1 else f"{int(h.cantidad)} {h.unidad}")
        costo = precio * unidades_venta if precio is not None else None
        filas.append((h.nombre, cantidad_texto, h.para_que, costo))
        if costo is None:
            faltantes.append(h.codigo)
        else:
            total += costo

    # --- compras.md -------------------------------------------------------------
    lineas = [
        f"# Lista de compras — {mueble.nombre}",
        "",
        f"Mueble de {mueble.dimensiones_texto()}.",
        "",
        "| Artículo | Cantidad a comprar | Para qué |",
        "|---|---|---|",
    ]
    lineas += [f"| {a} | {c} | {p} |" for a, c, p, _ in filas]
    lineas += [
        "",
        "> Consejo (07_HERRAJES): comprá ~10 % extra de tornillería — ya está",
        "> incluido en el tapacanto, no en tornillos: redondeá para arriba.",
        "",
    ]
    with open(ruta_compras, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))

    # --- presupuesto.md -----------------------------------------------------------
    lineas = [
        f"# Presupuesto estimado — {mueble.nombre}",
        "",
        f"Precios tomados de `software/nucleo/precios.json` (**editalos con los",
        "valores de tu zona**; los iniciales son de ejemplo).",
        "",
        "| Artículo | Cantidad | Costo |",
        "|---|---|---:|",
    ]
    for a, c, _, costo in filas:
        costo_texto = f"{mon} {costo:,.2f}" if costo is not None else "— (sin precio)"
        lineas.append(f"| {a} | {c} | {costo_texto} |")
    lineas += [
        f"| **TOTAL estimado** | | **{mon} {total:,.2f}** |",
        "",
        "El total NO incluye: mano de obra, flete, ni herramientas.",
        "",
    ]
    if faltantes:
        lineas.append(f"> Sin precio cargado para: {', '.join(faltantes)}. "
                      "Agregalos en precios.json.")
    with open(ruta_presupuesto, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))
    return ruta_compras, ruta_presupuesto
