"""Validación específica del ropero/placard.

Reglas fuente: AI_OPERATING_SYSTEM/11_REGLAS_Y_MEDIDAS_ROPERO.md (R-18 a
R-25, M-16 a M-23) y las comunes de 05_REGLAS_DE_CARPINTERIA.md (cajones:
R-05 a R-08, R-12).
"""

import copy
import math

ZOCALO = 100          # M-22
ALTO_BARRAL = 1750     # M-19
RETRANQUEO_BARRAL = 50  # M-20
ALTO_LIBRE_SOBRE_BARRAL_MIN = 280  # M-21
ANCHO_MAX_PUERTA_BATIENTE = 600    # R-21
SOLAPE_CORREDIZA = 20  # R-23

DEFECTOS = {
    "nombre": "Mueble sin nombre",
    "dimensiones": {"ancho": 900, "profundidad": 580, "alto": 2400},
    "material": {"color": "Blanco", "espesor": 18, "espesor_fondo": 3},
    "puertas": {"tipo": "batiente", "cantidad": 2},
    "cajones": {"incluir": False, "ancho": 400, "cantidad_cajones": 3},
    "estante_inferior": {"incluir": False},
}

LIMITES = {
    ("dimensiones", "ancho"): (600, 1200, "M-16", "módulo manejable sin vencerse (R-04)"),
    ("dimensiones", "profundidad"): (550, 620, "M-17", "percha de hombro a hombro + margen de puerta"),
    ("dimensiones", "alto"): (2000, 2600, "M-18", "rango de piso a cielorraso típico"),
    ("puertas", "cantidad"): (2, 4, "R-21/R-23", "cantidad de hojas del módulo"),
    ("cajones", "ancho"): (300, 600, "R-05/R-24", "con correderas debe quedar cajón útil"),
    ("cajones", "cantidad_cajones"): (1, 4, "R-07/R-24", "los frentes deben quedar usables"),
}

OPCIONES = {
    ("material", "espesor"): ([15, 18], "R-01"),
    ("material", "espesor_fondo"): ([3], "R-01"),
    ("puertas", "tipo"): (["batiente", "corrediza", "ninguna"], "R-21/R-23"),
}

CAMPOS_CONOCIDOS = {
    "": ["version", "tipo_mueble", "nombre", "dimensiones", "material",
         "puertas", "cajones", "estante_inferior"],
    "dimensiones": ["ancho", "profundidad", "alto"],
    "material": ["color", "espesor", "espesor_fondo"],
    "puertas": ["tipo", "cantidad"],
    "cajones": ["incluir", "ancho", "cantidad_cajones"],
    "estante_inferior": ["incluir"],
}


def normalizar(receta_cruda):
    """Completa la receta con los valores por defecto. Devuelve (receta, avisos)."""
    receta = copy.deepcopy(receta_cruda)
    avisos = []
    for clave, defecto in DEFECTOS.items():
        if isinstance(defecto, dict):
            seccion = receta.setdefault(clave, {})
            if isinstance(seccion, dict):
                for sub, valor in defecto.items():
                    seccion.setdefault(sub, valor)
        else:
            receta.setdefault(clave, defecto)
    return receta, avisos


def validar(receta):
    from .validador import RecetaInvalida

    errores = []
    avisos = []

    for seccion, permitidos in CAMPOS_CONOCIDOS.items():
        objeto = receta if seccion == "" else receta.get(seccion, {})
        if not isinstance(objeto, dict):
            errores.append(f'"{seccion}" debe ser un objeto.')
            continue
        for campo in objeto:
            if campo not in permitidos:
                donde = f"{seccion}.{campo}" if seccion else campo
                errores.append(
                    f'Campo desconocido "{donde}": no existe en el esquema de ropero '
                    "(ver 11_REGLAS_Y_MEDIDAS_ROPERO.md). No inventar campos."
                )
    if errores:
        raise RecetaInvalida(errores)

    for (seccion, campo), (minimo, maximo, regla, motivo) in LIMITES.items():
        valor = receta[seccion][campo]
        if not isinstance(valor, int) or isinstance(valor, bool):
            errores.append(
                f"{seccion}.{campo} = {valor!r}: debe ser un número entero en milímetros."
            )
        elif not (minimo <= valor <= maximo):
            errores.append(
                f"{seccion}.{campo} = {valor} está fuera del rango {minimo}–{maximo} "
                f"({regla}: {motivo})."
            )

    for (seccion, campo), (opciones, regla) in OPCIONES.items():
        valor = receta[seccion][campo]
        if valor not in opciones:
            errores.append(
                f"{seccion}.{campo} = {valor!r} no es válido ({regla}). "
                f"Opciones: {', '.join(map(str, opciones))}."
            )
    for seccion in ("cajones", "estante_inferior"):
        if not isinstance(receta[seccion]["incluir"], bool):
            errores.append(f"{seccion}.incluir debe ser true o false.")
    if errores:
        raise RecetaInvalida(errores)

    d = receta["dimensiones"]
    e = receta["material"]["espesor"]
    puertas = receta["puertas"]
    caj = receta["cajones"]

    # R-19: barral con soporte central si el interior supera 1000mm; aviso, no error.
    ancho_interior = d["ancho"] - 2 * e
    if ancho_interior > 1000:
        avisos.append(
            f"Ancho interior de {ancho_interior} mm: se agrega soporte central de barral "
            "para que no se arquee (R-19)."
        )

    # R-20/M-21: espacio libre sobre el barral, entre la ropa colgada y el techo.
    gap_sobre_barral = d["alto"] - ZOCALO - e - ALTO_BARRAL
    if gap_sobre_barral < 50:
        errores.append(
            f"Con {d['alto']} mm de alto, el barral (a {ALTO_BARRAL} mm) casi toca el "
            f"techo del módulo (quedan {gap_sobre_barral} mm libres). Aumentá el alto "
            "del ropero (R-20)."
        )
    elif gap_sobre_barral < ALTO_LIBRE_SOBRE_BARRAL_MIN:
        avisos.append(
            f"Quedan solo {gap_sobre_barral} mm libres sobre el barral (recomendado "
            f"{ALTO_LIBRE_SOBRE_BARRAL_MIN} mm para guardar ropa de cama/valijas, M-21)."
        )

    # R-21: puertas batientes, ancho de hoja no debe superar 600mm.
    if puertas["tipo"] == "batiente":
        ancho_vano = d["ancho"] - 2 * e
        ancho_hoja = (ancho_vano - 3 * (puertas["cantidad"] + 1)) // puertas["cantidad"]
        if ancho_hoja > ANCHO_MAX_PUERTA_BATIENTE:
            errores.append(
                f"Con {puertas['cantidad']} puertas batientes, cada hoja quedaría de "
                f"{ancho_hoja} mm; el máximo recomendado es {ANCHO_MAX_PUERTA_BATIENTE} mm "
                "(R-21): la hoja pesa demasiado para las bisagras. Agregá una puerta más "
                "o usá puertas corredizas."
            )
        elif ancho_hoja < 250:
            errores.append(
                f"Con {puertas['cantidad']} puertas batientes, cada hoja quedaría de "
                f"{ancho_hoja} mm: muy angosta para ser práctica. Reducí la cantidad "
                "de puertas."
            )

    # R-24 + M-04-like: si hay cajones, deben entrar en el ancho del módulo junto al barral.
    if caj["incluir"]:
        libre_para_barral = ancho_interior - caj["ancho"]
        if libre_para_barral < 350:
            errores.append(
                f"Con una sección de cajones de {caj['ancho']} mm, solo quedarían "
                f"{libre_para_barral} mm para el barral; no entra ropa colgada de forma "
                "práctica (mínimo 350 mm). Achicá los cajones o agrandá el módulo."
            )

    if errores:
        raise RecetaInvalida(errores)
    return avisos
