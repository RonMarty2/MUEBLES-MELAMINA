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

ANCHO_MIN_CUERPO = 600   # M-16 / R-30
ANCHO_MAX_CUERPO = 1200  # M-16 / R-30

DEFECTOS = {
    "nombre": "Mueble sin nombre",
    "dimensiones": {"ancho": 900, "profundidad": 580, "alto": 2400},
    "material": {"color": "Blanco", "espesor": 18, "espesor_fondo": 3},
    "uniones": {"tipo": "confirmat"},  # R-26: "excentrica" si se va a mover/mudar
    "calidad": {"nivel": "estandar"},  # D-018: economico | estandar | premium
    "cuerpos": {"cantidad": 1},        # R-30: módulos independientes atornillados entre sí
    "puertas": {"tipo": "batiente", "cantidad": 2},
    "cajones": {"incluir": False, "ancho": 400, "cantidad_cajones": 3,
                "tipo_tirador": "manija"},  # HER-002: manija | unero | push
    "estante_inferior": {"incluir": False},
}

LIMITES = {
    # ancho TOTAL; el rango real por cuerpo (600-1200, R-30) se valida aparte en validar()
    ("dimensiones", "ancho"): (600, 3600, "M-16", "hasta 3 cuerpos de 1200 mm (R-30)"),
    ("dimensiones", "profundidad"): (550, 620, "M-17", "percha de hombro a hombro + margen de puerta"),
    ("dimensiones", "alto"): (2000, 2600, "M-18", "rango de piso a cielorraso típico"),
    ("cuerpos", "cantidad"): (1, 3, "R-30", "módulos independientes atornillados entre sí"),
    ("puertas", "cantidad"): (2, 4, "R-21/R-23", "cantidad de hojas del módulo"),
    ("cajones", "ancho"): (300, 600, "R-05/R-24", "con correderas debe quedar cajón útil"),
    ("cajones", "cantidad_cajones"): (1, 4, "R-07/R-24", "los frentes deben quedar usables"),
}

OPCIONES = {
    ("material", "espesor"): ([15, 18], "R-01"),
    ("material", "espesor_fondo"): ([3], "R-01"),
    ("uniones", "tipo"): (["confirmat", "excentrica"], "R-26"),
    ("calidad", "nivel"): (["economico", "estandar", "premium"], "D-018"),
    ("puertas", "tipo"): (["batiente", "corrediza", "ninguna"], "R-21/R-23"),
    ("cajones", "tipo_tirador"): (["manija", "unero", "push"], "HER-002"),
}

CAMPOS_CONOCIDOS = {
    "": ["version", "tipo_mueble", "nombre", "dimensiones", "material", "uniones",
         "calidad", "cuerpos", "puertas", "cajones", "estante_inferior"],
    "dimensiones": ["ancho", "profundidad", "alto"],
    "material": ["color", "espesor", "espesor_fondo"],
    "uniones": ["tipo"],
    "calidad": ["nivel"],
    "cuerpos": ["cantidad"],
    "puertas": ["tipo", "cantidad"],
    "cajones": ["incluir", "ancho", "cantidad_cajones", "tipo_tirador"],
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
    n_cuerpos = receta["cuerpos"]["cantidad"]

    # R-30: el ancho TOTAL se reparte entre cuerpos; cada cuerpo debe ser un módulo sano.
    ancho_cuerpo = d["ancho"] // n_cuerpos
    if not (ANCHO_MIN_CUERPO <= ancho_cuerpo <= ANCHO_MAX_CUERPO):
        sugerencia = ("agregá un cuerpo" if ancho_cuerpo > ANCHO_MAX_CUERPO
                      else "sacá un cuerpo o agrandá el ancho total")
        errores.append(
            f"Con {n_cuerpos} cuerpo(s) y {d['ancho']} mm de ancho total, cada cuerpo "
            f"quedaría de {ancho_cuerpo} mm; el rango sano por cuerpo es "
            f"{ANCHO_MIN_CUERPO}–{ANCHO_MAX_CUERPO} mm (R-30/M-16): {sugerencia}."
        )
        raise RecetaInvalida(errores)
    if n_cuerpos > 1:
        avisos.append(
            f"Ropero de {n_cuerpos} cuerpos: {n_cuerpos} módulos independientes de "
            f"{ancho_cuerpo} mm que se arman por separado y se atornillan entre sí (R-30). "
            "Ventaja: se muda por partes sin desarmar (R-26)."
        )

    # R-19: barral con soporte central si el interior (POR CUERPO) supera 1000mm; aviso.
    ancho_interior = ancho_cuerpo - 2 * e
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
    # Con cuerpos>1 las hojas son 2 por cuerpo automáticas (R-30), siempre en rango.
    if puertas["tipo"] == "batiente" and n_cuerpos == 1:
        ancho_vano = ancho_cuerpo - 2 * e
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
    elif puertas["tipo"] == "batiente" and n_cuerpos > 1:
        avisos.append(
            f"Con {n_cuerpos} cuerpos, las puertas batientes son 2 hojas por cuerpo "
            f"({2 * n_cuerpos} en total); la cantidad elegida se ignora (R-30)."
        )

    # R-24 + M-04-like: si hay cajones, van en UN cuerpo y deben convivir con su barral.
    if caj["incluir"]:
        libre_para_barral = ancho_interior - caj["ancho"]
        if libre_para_barral < 350:
            errores.append(
                f"Con una sección de cajones de {caj['ancho']} mm, solo quedarían "
                f"{libre_para_barral} mm para el barral en ese cuerpo; no entra ropa "
                "colgada de forma práctica (mínimo 350 mm). Achicá los cajones o "
                "agrandá el módulo."
            )

    if errores:
        raise RecetaInvalida(errores)
    return avisos
