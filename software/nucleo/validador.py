"""Validador de recetas.

Frontera de módulo (02_ARQUITECTURA.md): rechaza recetas imposibles o
peligrosas con mensajes claros en español citando reglas R-xx / M-xx.
NUNCA corrige valores en silencio: junta TODOS los errores y los reporta.

La normalización (aplicar valores por defecto) también vive acá porque el
resto del sistema debe recibir siempre una receta completa.
Fuente de las reglas: AI_OPERATING_SYSTEM/05_REGLAS_DE_CARPINTERIA.md
y 06_MEDIDAS_ESTANDAR.md. Defectos: 04_ESQUEMA_RECETA_JSON.md.
"""

import copy

VERSION_SOPORTADA = "1.0"
TIPOS_SOPORTADOS = ["escritorio_gamer"]

DEFECTOS = {
    "nombre": "Mueble sin nombre",
    "dimensiones": {"ancho": 1600, "profundidad": 700, "alto": 750},
    "tapa": {"tipo": None},  # se decide por R-04 según el vano
    "material": {"color": "Blanco", "espesor": 18, "espesor_fondo": 3},
    "cajonera": {"posicion": "derecha", "ancho": 400, "cantidad_cajones": 3},
    "soporte_cpu": {"incluir": True, "ancho": 250},
    "pasacables": {"cantidad": 2, "diametro": 60},
}

LIMITES = {
    # campo: (mínimo, máximo, código de regla, explicación corta)
    ("dimensiones", "ancho"): (900, 2400, "R-15/M-03", "debe salir de placa comercial"),
    ("dimensiones", "profundidad"): (500, 900, "M-02", "profundidad utilizable de escritorio"),
    ("dimensiones", "alto"): (700, 800, "M-01", "rango ergonómico de escritura"),
    ("cajonera", "ancho"): (300, 600, "R-05/M-07", "con correderas debe quedar cajón útil"),
    ("cajonera", "cantidad_cajones"): (1, 4, "R-07", "los frentes deben quedar usables"),
    ("soporte_cpu", "ancho"): (200, 350, "M-05", "ancho de gabinete ATX + ventilación"),
    ("pasacables", "cantidad"): (0, 4, "M-14", "cantidad razonable de grommets"),
}

OPCIONES = {
    ("tapa", "tipo"): (["simple_18", "doble_18", "simple_25"], "R-01/R-04"),
    ("material", "espesor"): ([15, 18], "R-01"),
    ("material", "espesor_fondo"): ([3], "R-01"),
    ("cajonera", "posicion"): (["derecha", "izquierda", "ninguna"], "R-14"),
    ("pasacables", "diametro"): ([60, 80], "H-06"),
}

CAMPOS_CONOCIDOS = {
    "": ["version", "tipo_mueble", "nombre", "dimensiones", "tapa", "material",
         "cajonera", "soporte_cpu", "pasacables"],
    "dimensiones": ["ancho", "profundidad", "alto"],
    "tapa": ["tipo"],
    "material": ["color", "espesor", "espesor_fondo"],
    "cajonera": ["posicion", "ancho", "cantidad_cajones"],
    "soporte_cpu": ["incluir", "ancho"],
    "pasacables": ["cantidad", "diametro"],
}


class RecetaInvalida(Exception):
    """Se lanza con la lista completa de errores de una receta."""

    def __init__(self, errores):
        self.errores = errores
        super().__init__("\n".join(f"- {e}" for e in errores))


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
    izquierda = e  # cara interna del lateral izquierdo
    if receta["soporte_cpu"]["incluir"]:
        izquierda = e + receta["soporte_cpu"]["ancho"] + e  # cara interna del parante CPU
    derecha = d["ancho"] - e  # cara interna del lateral derecho
    if receta["cajonera"]["posicion"] != "ninguna":
        derecha = d["ancho"] - receta["cajonera"]["ancho"]  # cara externa cajonera
    return max(0, derecha - izquierda)


def normalizar(receta_cruda):
    """Completa la receta con los valores por defecto documentados en 04.

    Devuelve (receta_completa, avisos). No valida: eso es validar().
    """
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

    # Defecto inteligente de la tapa (R-04): doble_18 si el vano supera 800.
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
    """Valida una receta YA normalizada. Lanza RecetaInvalida con todos los
    errores juntos, o devuelve una lista de avisos (no bloqueantes)."""
    errores = []
    avisos = []

    # --- Forma general -----------------------------------------------------
    if receta.get("version") != VERSION_SOPORTADA:
        errores.append(
            f'version = "{receta.get("version")}" no soportada; usá "{VERSION_SOPORTADA}".'
        )
    if receta.get("tipo_mueble") not in TIPOS_SOPORTADOS:
        errores.append(
            f'tipo_mueble = "{receta.get("tipo_mueble")}" desconocido. '
            f"Disponibles: {', '.join(TIPOS_SOPORTADOS)}."
        )

    # Campos desconocidos (la IA no debe inventar campos; ver 08).
    for seccion, permitidos in CAMPOS_CONOCIDOS.items():
        objeto = receta if seccion == "" else receta.get(seccion, {})
        if not isinstance(objeto, dict):
            errores.append(f'"{seccion}" debe ser un objeto.')
            continue
        for campo in objeto:
            if campo not in permitidos:
                donde = f"{seccion}.{campo}" if seccion else campo
                errores.append(
                    f'Campo desconocido "{donde}": no existe en el esquema 1.0 '
                    "(ver 04_ESQUEMA_RECETA_JSON.md). No inventar campos."
                )
    if errores:
        raise RecetaInvalida(errores)

    # --- Rangos numéricos ---------------------------------------------------
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

    # --- Opciones cerradas ----------------------------------------------------
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

    # --- Reglas de carpintería (05) y ergonomía (06) -------------------------
    e = receta["material"]["espesor"]
    d = receta["dimensiones"]
    caj = receta["cajonera"]
    vano = vano_libre(receta)

    # R-04: tapa simple de 18 con vano grande = pandeo.
    if receta["tapa"]["tipo"] == "simple_18" and vano > 800:
        errores.append(
            f"tapa.tipo = simple_18 con un vano libre de {vano} mm: una placa de 18 "
            "se pandea pasados los 800 mm (regla R-04). Usá doble_18 o simple_25, "
            "o achicá el escritorio."
        )

    # R-06/R-07: reparto de frentes de cajón.
    if caj["posicion"] != "ninguna":
        alto_util = d["alto"] - espesor_tapa(receta) - e  # menos tapa y piso cajonera
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

    # M-04: espacio libre para las piernas.
    ocupado = e  # lateral izquierdo
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

    # R-15: ninguna dimensión de pieza puede exceder la placa (margen 20 mm/lado).
    if d["ancho"] > 2560:
        errores.append(
            f"La tapa de {d['ancho']} mm no sale de una placa de 2600 mm con margen de "
            "escuadrado (regla R-15)."
        )

    if errores:
        raise RecetaInvalida(errores)
    return avisos


def normalizar_y_validar(receta_cruda):
    """Punto de entrada estándar: devuelve (receta_completa, avisos)."""
    receta, avisos = normalizar(receta_cruda)
    avisos += validar(receta)
    return receta, avisos
