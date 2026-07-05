"""Genera la guía de armado paso a paso (instrucciones_armado.md).

Frontera de módulo (02_ARQUITECTURA.md): no recalcula nada; deriva del objeto
Mueble ya calculado. Produce pasos en orden lógico de construcción, en lenguaje
de principiante. La app tiene un espejo interactivo de esto (con resaltado 3D).
Orden y conceptos: AI_OPERATING_SYSTEM/12_GUIA_DE_ARMADO.md (D-015).

Cada paso: {n, titulo, texto, piezas:[nombres base], herraje, tip}.
`piezas` referencia nombres de pieza para poder resaltarlos en el 3D (la app).
"""


def _hay(mueble, prefijo):
    """¿Existe alguna pieza cuyo nombre empiece con `prefijo`?"""
    return any(p.nombre.startswith(prefijo) for p in mueble.piezas)


def _tapa_doble(mueble):
    return _hay(mueble, "Tapa capa inferior")


def instrucciones_escritorio(mueble, receta):
    pasos = []

    def paso(titulo, texto, piezas=None, herraje="", tip=""):
        pasos.append({"n": len(pasos) + 1, "titulo": titulo, "texto": texto,
                      "piezas": piezas or [], "herraje": herraje, "tip": tip})

    paso("Entendé las placas y ordená los cortes",
         "Cuando retires los cortes de la tienda, separalos y etiquetalos según la lista "
         "de cortes. Todas las piezas salieron de tableros grandes (placas). Verificá que "
         "las medidas coincidan antes de empezar.",
         tip="Apoyá siempre las piezas sobre cartón o goma para no rayar la melamina.")

    if _tapa_doble(mueble):
        paso("Armá la tapa doble (refuerzo anti-pandeo)",
             "La tapa lleva dos capas: abajo el aglomerado crudo (no se ve) y arriba la "
             "melamina decorativa (la que vas a ver y tocar). Poné cola en toda la capa de "
             "abajo, apoyá la de arriba bien alineada y atornillá desde abajo con tornillos "
             "4×30 cada ~30 cm. Dejá secar con peso encima.",
             piezas=["Tapa capa inferior (oculta)", "Tapa capa superior (visible)"],
             herraje="Tornillo aglomerado 4×30 + cola",
             tip="La cara linda va PARA ARRIBA. La capa cruda queda escondida abajo.")

    if _hay(mueble, "Lateral cajonera"):
        paso("Armá el cajón de la cajonera (la caja estructural)",
             "Uní los dos laterales de la cajonera con el piso, formando una U. Después "
             "cerrala por atrás con el fondo. Pre-perforá SIEMPRE antes de atornillar la "
             "melamina para que no reviente el canto.",
             piezas=["Lateral cajonera interno", "Lateral cajonera externo",
                     "Piso cajonera", "Fondo cajonera"],
             herraje="Confirmat 7×50 (o excéntrico) + clavos para el fondo",
             tip="Verificá la escuadra midiendo las dos diagonales: deben dar igual.")

    if _hay(mueble, "Lateral caja cajón"):
        paso("Armá las cajas de los cajones",
             "Cada cajón es una caja: dos laterales, un frente interno y un contrafrente, "
             "más un fondo de 3 mm por debajo. Armá todas las cajas primero.",
             piezas=["Lateral caja cajón", "Frente interno cajón", "Contrafrente cajón",
                     "Fondo cajón"],
             herraje="Confirmat + clavos",
             tip="Todas las cajas deben quedar iguales para que los cajones corran parejos.")
        paso("Colocá las correderas y meté los cajones",
             "Atornillá una guía de la corredera a cada lado del cajón y la otra al mueble, "
             "a la misma altura. Deslizá el cajón para probar que corre suave.",
             herraje="Corredera (según el nivel de calidad que elegiste)",
             tip="Si elegiste soft-close, el cajón se frena solo al cerrar: no lo fuerces.")
        paso("Atornillá los frentes de los cajones",
             "El frente visible (con el tirador) se atornilla desde ADENTRO del cajón, con "
             "tornillos 4×30. Dejá 3 mm de luz entre frentes para que no rocen.",
             piezas=["Frente cajón"], herraje="Tornillo aglomerado 4×30 + tirador")

    apoyos = ["Lateral izquierdo (pata panel)"]
    if _hay(mueble, "Parante soporte CPU"):
        apoyos += ["Parante soporte CPU", "Bandeja CPU"]
        texto_apoyo = ("Parás el lateral izquierdo y, al lado, el parante del soporte de "
                       "CPU. Entre ambos va la bandeja donde se apoya la CPU, a 10 cm del "
                       "piso para que ventile.")
    else:
        texto_apoyo = "Parás el lateral izquierdo, que es una de las patas del escritorio."
    paso("Parás los apoyos verticales", texto_apoyo, piezas=apoyos,
         herraje="Confirmat / excéntrico",
         tip="Todavía no aprietes del todo: primero presentá todo, después ajustás.")

    tapa = ["Tapa capa superior (visible)"] if _tapa_doble(mueble) else ["Tapa"]
    paso("Colocá la tapa sobre los apoyos",
         "Apoyá la tapa sobre la cajonera y el lateral (o el parante). Fijala desde abajo "
         "con escuadras o tornillos, cuidando que no asomen arriba.",
         piezas=tapa, herraje="Escuadra metálica 25 mm",
         tip="Revisá que el escritorio no se hamaque: si se mueve, revisá la escuadra.")

    if _hay(mueble, "Viga trasera"):
        paso("Poné la viga trasera (rigidez)",
             "Como tu escritorio es ancho, lleva una viga atrás, de canto, que evita que "
             "se hamaque. Atornillala a los dos apoyos y a la tapa.",
             piezas=["Viga trasera"], herraje="Confirmat / excéntrico")

    if getattr(mueble, "grommets", None):
        paso("Hacé los agujeros de pasacables",
             "Marcá y perforá los agujeros de la tapa con una broca copa del diámetro del "
             "grommet. Colocá los grommets (los aros plásticos) para que quede prolijo.",
             tip="Perforá con la cara buena hacia arriba y algo de apoyo abajo, sin astillar.")

    if _hay(mueble, "Tapa elevación monitor"):
        paso("Montá la elevación para el monitor",
             "Sobre la tapa, parás las dos patitas y encima la bandeja elevada. El monitor "
             "va arriba y el teclado se guarda deslizándolo en el hueco de abajo.",
             piezas=["Pata elevación monitor (izq)", "Pata elevación monitor (der)",
                     "Tapa elevación monitor"], herraje="Confirmat / excéntrico")

    paso("Niveladores y terminación final",
         "Colocá los regatones/niveladores en la base para que el escritorio no toque el "
         "piso y quede nivelado. Repasá que todos los cantos visibles tengan su tapacanto "
         "bien pegado. Apretá todas las uniones.",
         herraje="Regatón nivelador + tapacanto",
         tip="Nunca arrastres el escritorio ya armado: movelo entre dos, levantándolo (R-26).")
    return pasos


def instrucciones_ropero(mueble, receta):
    pasos = []

    def paso(titulo, texto, piezas=None, herraje="", tip=""):
        pasos.append({"n": len(pasos) + 1, "titulo": titulo, "texto": texto,
                      "piezas": piezas or [], "herraje": herraje, "tip": tip})

    paso("Entendé las placas y ordená los cortes",
         "Separá y etiquetá todas las piezas según la lista de cortes. Verificá medidas "
         "antes de empezar.",
         tip="Trabajá en un piso parejo y con espacio: el ropero es grande.")

    paso("Armá la base y el zócalo",
         "El zócalo va retranqueado (más adentro) del frente, para que no se vea al "
         "agacharse y separe el mueble del piso.",
         piezas=["Zócalo frontal"], herraje="Confirmat / excéntrico",
         tip="El ropero nunca debe apoyar la melamina directo al piso (humedad).")

    paso("Parás los laterales y armá la caja",
         "Uní los dos laterales con el piso y el techo, formando la caja principal. "
         "Pre-perforá antes de atornillar.",
         piezas=["Lateral izquierdo", "Lateral derecho", "Piso", "Techo (estante superior)"],
         herraje="Confirmat / excéntrico",
         tip="Medí las diagonales para verificar la escuadra antes de apretar todo.")

    paso("Cerrá el fondo",
         "El fondo de 3 mm va clavado por detrás. NO lo selles hermético: dejá que ventile "
         "para que la ropa no tome humedad.",
         piezas=["Fondo"], herraje="Clavos 1½\"")

    if _hay(mueble, "Divisor cajones"):
        paso("Armá la cajonera interior",
             "Colocá el divisor que separa la zona de cajones del resto, y armá el bloque "
             "de cajones (cajas + correderas + frentes), igual que en un escritorio.",
             piezas=["Divisor cajones", "Tapa de cajonera", "Lateral caja cajón",
                     "Frente cajón"],
             herraje="Corredera (según calidad) + tirador")

    if _hay(mueble, "Barral"):
        paso("Colocá el barral para colgar la ropa",
             "Atornillá los soportes del barral a los laterales, a la altura indicada, y "
             "apoyá el tubo. Si el ropero es ancho, lleva un soporte en el medio para que "
             "no se arquee.",
             piezas=["Barral colgador"], herraje="Barral tubular + soportes")

    if _hay(mueble, "Estante inferior"):
        paso("Colocá el estante inferior",
             "El estante de abajo (para zapatos) se apoya sobre tacos o rinconeras.",
             piezas=["Estante inferior (zapatos)"], herraje="Rinconera/taco")

    if _hay(mueble, "Puerta batiente"):
        paso("Colocá las puertas batientes",
             "Marcá y perforá las cazoletas de las bisagras en cada puerta, atornillá las "
             "bisagras y colgá las puertas. Regulá con los tornillos de la bisagra hasta que "
             "cierren parejas.",
             piezas=["Puerta batiente 1", "Puerta batiente 2"],
             herraje="Bisagra cazoleta (según calidad) + tirador",
             tip="Si elegiste soft-close, las puertas cierran solas sin golpe.")
    elif _hay(mueble, "Puerta corrediza"):
        paso("Colocá los rieles y las puertas corredizas",
             "Atornillá el riel de arriba y el de abajo. Colgá cada hoja en su riel; se "
             "solapan un poco para tapar la luz. Probá que deslicen suave.",
             piezas=["Puerta corrediza 1", "Puerta corrediza 2"],
             herraje="Riel corredizo (juego) + tirador")

    paso("Terminación final",
         "Repasá tapacantos, apretá todas las uniones y nivelá el mueble en su lugar "
         "definitivo. Un ropero cargado es MUY pesado: ubicalo antes de llenarlo.",
         tip="Fijá el ropero a la pared con un ángulo si es alto, para que no se vuelque.")
    return pasos


def instrucciones_armado(mueble, receta):
    """Punto de entrada: devuelve la lista de pasos según el tipo de mueble."""
    if receta["tipo_mueble"] == "ropero":
        return instrucciones_ropero(mueble, receta)
    return instrucciones_escritorio(mueble, receta)


def generar_instrucciones(mueble, receta, ruta_md):
    """Escribe instrucciones_armado.md."""
    pasos = instrucciones_armado(mueble, receta)
    lineas = [
        f"# Guía de armado paso a paso — {mueble.nombre}",
        "",
        f"Mueble de {mueble.dimensiones_texto()}.",
        "",
        "> **Regla de oro de la melamina:** pre-perforá SIEMPRE antes de atornillar, para "
        "que el canto no reviente (R-09). Y nunca arrastres el mueble ya armado (R-26).",
        "",
    ]
    for p in pasos:
        lineas.append(f"## Paso {p['n']}: {p['titulo']}")
        lineas.append("")
        lineas.append(p["texto"])
        if p["piezas"]:
            lineas.append("")
            lineas.append(f"- **Piezas:** {', '.join(p['piezas'])}")
        if p["herraje"]:
            lineas.append(f"- **Herraje:** {p['herraje']}")
        if p["tip"]:
            lineas.append(f"- 💡 {p['tip']}")
        lineas.append("")
    with open(ruta_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))
    return ruta_md
