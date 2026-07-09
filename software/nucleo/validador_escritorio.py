"""Validación específica del escritorio_gamer.

Extraído de validador.py al agregar el ropero (D-011) para que cada tipo de
mueble tenga su propio archivo de reglas, sin mezclar. El dispatcher común
vive en validador.py. Reglas fuente: 05_REGLAS_DE_CARPINTERIA.md,
06_MEDIDAS_ESTANDAR.md.
"""

import copy

DEFECTOS = {
    "nombre": "Mueble sin nombre",
    "dimensiones": {"ancho": 1600, "profundidad": 700, "alto": 750},
    "tapa": {"tipo": None},  # se decide por R-04 según el vano
    "material": {"color": "Blanco", "espesor": 18, "espesor_fondo": 3},
    "uniones": {"tipo": "confirmat"},  # R-26: "excentrica" si se va a mover/mudar
    "calidad": {"nivel": "estandar"},  # D-018: economico | estandar | premium
    "cajonera": {"posicion": "derecha", "ancho": 400, "cantidad_cajones": 3},
    "soporte_cpu": {"incluir": True, "ancho": 250},
    "pasacables": {"cantidad": 2, "diametro": 60},
    "elevacion_monitor": {"incluir": False, "ancho": 800, "profundidad": 250},
    "forma": {"tipo": "recto", "lado": "derecha",   # R-31: "L" agrega un retorno
              "largo_retorno": 1000, "profundidad_retorno": 500},
}

LIMITES = {
    ("dimensiones", "ancho"): (900, 2400, "R-15/M-03", "debe salir de placa comercial"),
    ("dimensiones", "profundidad"): (500, 900, "M-02", "profundidad utilizable de escritorio"),
    ("dimensiones", "alto"): (700, 800, "M-01", "rango ergonómico de escritura"),
    ("cajonera", "ancho"): (300, 600, "R-05/M-07", "con correderas debe quedar cajón útil"),
    ("cajonera", "cantidad_cajones"): (1, 4, "R-07", "los frentes deben quedar usables"),
    ("soporte_cpu", "ancho"): (200, 350, "M-05", "ancho de gabinete ATX + ventilación"),
    ("pasacables", "cantidad"): (0, 4, "M-14", "cantidad razonable de grommets"),
    ("elevacion_monitor", "ancho"): (500, 1200, "M-25", "ancho razonable de la bandeja elevada"),
    ("elevacion_monitor", "profundidad"): (200, 350, "M-25", "apoyo suficiente para monitores"),
    ("forma", "largo_retorno"): (600, 1600, "M-26/R-31", "ala de la L usable y sana"),
    ("forma", "profundidad_retorno"): (400, 700, "M-27/R-31", "profundidad del ala de la L"),
}

OPCIONES = {
    ("tapa", "tipo"): (["simple_18", "doble_18", "simple_25"], "R-01/R-04"),
    ("material", "espesor"): ([15, 18], "R-01"),
    ("material", "espesor_fondo"): ([3], "R-01"),
    ("uniones", "tipo"): (["confirmat", "excentrica"], "R-26"),
    ("calidad", "nivel"): (["economico", "estandar", "premium"], "D-018"),
    ("cajonera", "posicion"): (["derecha", "izquierda", "ninguna"], "R-14"),
    ("pasacables", "diametro"): ([60, 80], "H-06"),
    ("forma", "tipo"): (["recto", "L"], "R-31"),
    ("forma", "lado"): (["derecha", "izquierda"], "R-31"),
}

CAMPOS_CONOCIDOS = {
    "": ["version", "tipo_mueble", "nombre", "dimensiones", "tapa", "material", "uniones",
         "calidad", "cajonera", "soporte_cpu", "pasacables", "elevacion_monitor", "forma"],
    "dimensiones": ["ancho", "profundidad", "alto"],
    "tapa": ["tipo"],
    "material": ["color", "espesor", "espesor_fondo"],
    "uniones": ["tipo"],
    "calidad": ["nivel"],
    "cajonera": ["posicion", "ancho", "cantidad_cajones"],
    "soporte_cpu": ["incluir", "ancho"],
    "pasacables": ["cantidad", "diametro"],
    "elevacion_monitor": ["incluir", "ancho", "profundidad"],
    "forma": ["tipo", "lado", "largo_retorno", "profundidad_retorno"],
}


def espesor_tapa(receta):
    """Espesor físico total de la tapa según su tipo."""
    return {"simple_18": 18, "doble_18": 36, "simple_25": 25}[receta["tapa"]["tipo"]]


def vano_libre(receta):
    """Luz horizontal sin apoyo bajo la tapa, entre los apoyos estructurales.

    Apoyos: lateral-panel (o parante del soporte CPU si existe, que está más
    adentro) de un lado, y la cajonera (o lateral-panel) del otro. Ver R-14.
    """
    d = receta["dimensiones"]
    e = receta["material"]["espesor"]
    izquierda = e
    if receta["soporte_cpu"]["incluir"]:
        izquierda = e + receta["soporte_cpu"]["ancho"] + e
    derecha = d["ancho"] - e
    if receta["cajonera"]["posicion"] != "ninguna":
        derecha = d["ancho"] - receta["cajonera"]["ancho"]
    return max(0, derecha - izquierda)


def normalizar(receta_cruda):
    """Completa la receta con los valores por defecto. Devuelve (receta, avisos)."""
    receta = copy.deepcopy(receta_cruda)
    avisos = []
    for clave, defecto in DEFECTOS.items():
        if isinstance(defecto, dict):
            seccion = receta.setdefault(clave, {})
            if isinstance(seccion, dict):
                for sub, valor in defecto.items():
                    if valor is not None:
                        seccion.setdefault(sub, valor)
        else:
            receta.setdefault(clave, defecto)

    if receta.get("tapa", {}).get("tipo") is None:
        receta.setdefault("tapa", {})
        if vano_libre(receta) > 800:
            receta["tapa"]["tipo"] = "doble_18"
            avisos.append(
                "Tapa reforzada automáticamente a doble placa de 18 mm (doble_18): "
                f"el vano libre es {vano_libre(receta)} mm y una placa simple de 18 "
                "se pandearía con el peso de los monitores (regla R-04)."
            )
        else:
            receta["tapa"]["tipo"] = "simple_18"
    return receta, avisos


def validar(receta):
    """Valida una receta YA normalizada. Devuelve lista de avisos o lanza
    RecetaInvalida (importada perezosamente para evitar import circular)."""
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
                    f'Campo desconocido "{donde}": no existe en el esquema de '
                    "escritorio_gamer (ver 04_ESQUEMA_RECETA_JSON.md). No inventar campos."
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
                f"{seccion}.{campo} = {valor} está fuera del rango {minimo}–{maximo} mm "
                f"({regla}: {motivo})."
            )

    for (seccion, campo), (opciones, regla) in OPCIONES.items():
        valor = receta[seccion][campo]
        if valor not in opciones:
            errores.append(
                f"{seccion}.{campo} = {valor!r} no es válido ({regla}). "
                f"Opciones: {', '.join(map(str, opciones))}."
            )
    if not isinstance(receta["soporte_cpu"]["incluir"], bool):
        errores.append("soporte_cpu.incluir debe ser true o false.")
    if errores:
        raise RecetaInvalida(errores)

    e = receta["material"]["espesor"]
    d = receta["dimensiones"]
    caj = receta["cajonera"]
    vano = vano_libre(receta)

    if receta["tapa"]["tipo"] == "simple_18" and vano > 800:
        errores.append(
            f"tapa.tipo = simple_18 con un vano libre de {vano} mm: una placa de 18 "
            "se pandea pasados los 800 mm (regla R-04). Usá doble_18 o simple_25, "
            "o achicá el escritorio."
        )

    if caj["posicion"] != "ninguna":
        alto_util = d["alto"] - espesor_tapa(receta) - e
        n = caj["cantidad_cajones"]
        alto_frente = (alto_util - 3 * n) // n
        if alto_frente < 120:
            errores.append(
                f"Con {n} cajones el frente de cada uno quedaría de {alto_frente} mm; "
                "el mínimo usable es 120 mm (regla R-07). Poné menos cajones."
            )
        elif alto_frente > 350:
            avisos.append(
                f"Cada frente de cajón quedará de {alto_frente} mm (más de 350 mm, R-07): "
                "cajones muy profundos se vuelven un pozo. Considerá agregar un cajón."
            )

    ocupado = e
    if receta["soporte_cpu"]["incluir"]:
        ocupado += receta["soporte_cpu"]["ancho"] + e
    if caj["posicion"] != "ninguna":
        ocupado += caj["ancho"]
    else:
        ocupado += e
    libre = d["ancho"] - ocupado
    if libre < 600:
        errores.append(
            f"Quedarían solo {libre} mm libres para las piernas; el mínimo es 600 mm "
            "(medida M-04). Agrandá el ancho, achicá la cajonera o sacá el soporte de CPU."
        )

    if d["ancho"] > 2560:
        errores.append(
            f"La tapa de {d['ancho']} mm no sale de una placa de 2600 mm con margen de "
            "escuadrado (regla R-15)."
        )

    # M-25: la elevación para monitor debe caber en la tapa con margen a los bordes.
    elev = receta["elevacion_monitor"]
    if elev["incluir"] and elev["ancho"] > d["ancho"] - 200:
        errores.append(
            f"La elevación para monitor de {elev['ancho']} mm no entra en una tapa de "
            f"{d['ancho']} mm dejando margen a los bordes (M-25). Achicala o agrandá el "
            "escritorio."
        )

    # R-31: forma en L — el retorno es un módulo autoportante (dos patas propias).
    forma = receta["forma"]
    if forma["tipo"] == "L":
        vano_ret = forma["largo_retorno"] - 100 - e  # entre pata esquina y pata extremo
        refuerzo = ""
        if vano_ret > 1200:
            refuerzo = " y una viga de canto (R-13)"
        elif vano_ret > 800:
            refuerzo = " y tapa doble (R-04)"
        avisos.append(
            f"Escritorio en L (lado {forma['lado']}): el retorno de "
            f"{forma['largo_retorno']}×{forma['profundidad_retorno']} mm se arma como un "
            f"módulo aparte con sus DOS patas{refuerzo}, y se une al escritorio con "
            "escuadras y tornillos (R-31). Para mudanzas se separa y viaja aparte (R-26)."
        )

    if errores:
        raise RecetaInvalida(errores)
    return avisos
