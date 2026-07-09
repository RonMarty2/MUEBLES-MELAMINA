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
        n_caj = receta.get("cajonera", {}).get("cantidad_cajones", 1)
        for i in range(1, n_caj + 1):
            paso(f"Armá la caja del cajón {i} de {n_caj}",
                 "1. Uní los dos laterales de este cajón con el frente interno y el "
                 "contrafrente, formando una caja cerrada. 2. Pre-perforá siempre antes de "
                 "atornillar. 3. Al final, clavá por debajo el fondo de 3 mm.",
                 piezas=[f"Lateral caja cajón {i} (izq)", f"Lateral caja cajón {i} (der)",
                         f"Frente interno cajón {i}", f"Contrafrente cajón {i}",
                         f"Fondo cajón {i}"],
                 herraje="Confirmat + clavos",
                 tip="Armá esta caja igual que las demás, para que todos los cajones corran parejos.")
            paso(f"Colocá la corredera y meté el cajón {i} de {n_caj}",
                 "1. Atornillá una guía de la corredera a cada lado de esta caja. 2. Atornillá "
                 "la otra guía al mueble, a la misma altura (mirá el plano acotado de la app: "
                 "la línea central debe coincidir). 3. Probá que el cajón corra suave antes de "
                 "poner el frente.",
                 piezas=[f"Lateral caja cajón {i} (izq)", f"Lateral caja cajón {i} (der)"],
                 herraje="Corredera (según el nivel de calidad que elegiste)",
                 tip="Herramientas: cinta métrica, lápiz, escuadra, taladro con broca Ø2 mm y punta PH2. Si elegiste soft-close, no lo fuerces al cerrar.")
            paso(f"Atornillá el frente del cajón {i} de {n_caj}",
                 "1. Metié el cajón ya armado en su lugar, corriendo sobre la corredera. "
                 "2. Apoyá el frente por fuera, centrado, con 3 mm de luz respecto a los de al "
                 "lado. 3. Atornillalo desde ADENTRO del cajón, con tornillos 4×30 (nunca desde "
                 "afuera, se vería el tornillo).",
                 piezas=[f"Frente cajón {i}"], herraje="Tornillo aglomerado 4×30 + tirador")

    apoyos = ["Lateral izquierdo (pata panel)"]
    if _hay(mueble, "Lateral derecho (pata panel)"):
        apoyos.append("Lateral derecho (pata panel)")
    if _hay(mueble, "Parante soporte CPU"):
        apoyos += ["Parante soporte CPU", "Bandeja CPU"]
        texto_apoyo = ("Parás el lateral izquierdo y, al lado, el parante del soporte de "
                       "CPU. Entre ambos va la bandeja donde se apoya la CPU, a 10 cm del "
                       "piso para que ventile.")
    elif len(apoyos) > 1:
        texto_apoyo = "Parás los dos laterales (las patas panel del escritorio)."
    else:
        texto_apoyo = "Parás el lateral izquierdo, que es una de las patas del escritorio."
    paso("Parás los apoyos verticales", texto_apoyo, piezas=apoyos,
         herraje="Confirmat / excéntrico",
         tip="Todavía no aprietes del todo: primero presentá todo, después ajustás.")

    tapa = ["Tapa capa superior (visible)"] if _tapa_doble(mueble) else ["Tapa"]
    apoyos_tapa = list(apoyos)
    if _hay(mueble, "Lateral cajonera"):
        apoyos_tapa += ["Lateral cajonera interno", "Lateral cajonera externo"]
    paso("Colocá la tapa sobre los apoyos",
         "1. Apoyá la tapa encima de la cajonera y del lateral (o parante), bien alineada "
         "por los bordes. 2. Fijala desde ABAJO con escuadras metálicas o tornillos cortos, "
         "sin que ninguno asome arriba de la tapa. 3. Revisá que no se hamaque.",
         piezas=apoyos_tapa + tapa, herraje="Escuadra metálica 25 mm",
         tip="Si se mueve al empujarla, revisá que pusiste suficientes escuadras.")

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

    zocalos = ["Zócalo frontal"]
    if _hay(mueble, "Zócalo trasero"):
        zocalos.append("Zócalo trasero")
    paso("Armá la base y el zócalo",
         "El zócalo delantero va retranqueado (más adentro) del frente, para que no se vea "
         "al agacharse y separe el mueble del piso."
         + (" El zócalo trasero es la segunda línea de apoyo del piso: sin él, el piso "
            "cargado cede atrás (R-28)." if len(zocalos) > 1 else ""),
         piezas=zocalos, herraje="Confirmat / excéntrico",
         tip="El ropero nunca debe apoyar la melamina directo al piso (humedad).")

    caja_piezas = ["Lateral izquierdo", "Lateral derecho", "Piso", "Techo (estante superior)"]
    texto_caja = ("Uní los dos laterales con el piso y el techo, formando la caja principal. "
                  "Pre-perforá antes de atornillar.")
    if _hay(mueble, "Refuerzo bajo techo"):
        caja_piezas.append("Refuerzo bajo techo")
        texto_caja += (" El refuerzo de canto va pegado al fondo, debajo del techo: tu "
                       "ropero es ancho y sin él el techo se dobla por el medio con el "
                       "peso (R-27).")
    paso("Parás los laterales y armá la caja", texto_caja,
         piezas=caja_piezas, herraje="Confirmat / excéntrico",
         tip="Medí las diagonales para verificar la escuadra antes de apretar todo.")

    paso("Cerrá el fondo",
         "El fondo de 3 mm va clavado por detrás. Clavalo también a las líneas intermedias "
         "(zócalo trasero, refuerzo, divisor): el fondo bien clavado es lo que evita que el "
         "mueble se tuerza en paralelogramo al moverlo (R-29/R-26). NO lo selles hermético: "
         "dejá que ventile para que la ropa no tome humedad.",
         piezas=["Fondo"], herraje="Clavos 1½\"")

    if _hay(mueble, "Divisor cajones"):
        paso("Colocá el divisor de la cajonera",
             "1. Atornillá el divisor vertical que separa la zona de cajones del resto del "
             "ropero. 2. Cerrá arriba con la tapa de cajonera.",
             piezas=["Divisor cajones", "Tapa de cajonera"], herraje="Confirmat / excéntrico")
        n_caj_rop = receta.get("cajones", {}).get("cantidad_cajones", 1)
        for i in range(1, n_caj_rop + 1):
            paso(f"Armá la caja del cajón {i} de {n_caj_rop}",
                 "1. Uní los dos laterales de este cajón con el frente interno y el "
                 "contrafrente. 2. Pre-perforá siempre antes de atornillar. 3. Clavá el fondo "
                 "de 3 mm por debajo.",
                 piezas=[f"Lateral caja cajón {i} (izq)", f"Lateral caja cajón {i} (der)",
                         f"Frente interno cajón {i}", f"Contrafrente cajón {i}",
                         f"Fondo cajón {i}"],
                 herraje="Confirmat + clavos",
                 tip="Armá esta caja igual que las demás, para que todos los cajones corran parejos.")
            paso(f"Colocá la corredera y meté el cajón {i} de {n_caj_rop}",
                 "1. Atornillá una guía de la corredera a cada lado de esta caja. 2. Atornillá "
                 "la otra guía al divisor/lateral, a la misma altura (mirá el plano acotado de "
                 "la app). 3. Probá que corra suave.",
                 piezas=[f"Lateral caja cajón {i} (izq)", f"Lateral caja cajón {i} (der)"],
                 herraje="Corredera (según calidad)")
            paso(f"Atornillá el frente del cajón {i} de {n_caj_rop}",
                 "1. Metié el cajón en su lugar. 2. Apoyá el frente por fuera, centrado, con "
                 "3 mm de luz respecto a los de al lado. 3. Atornillalo desde ADENTRO del "
                 "cajón.",
                 piezas=[f"Frente cajón {i}"], herraje="Tornillo aglomerado 4×30 + tirador")

    if _hay(mueble, "Barral"):
        paso("Colocá el barral para colgar la ropa",
             "Atornillá los soportes del barral a los laterales, a la altura indicada, y "
             "apoyá el tubo. Si el ropero es ancho, lleva un soporte en el medio para que "
             "no se arquee.",
             piezas=["Barral colgador"], herraje="Barral tubular + soportes")

    if _hay(mueble, "Estante inferior"):
        est_piezas = ["Estante inferior (zapatos)"]
        texto_est = "El estante de abajo (para zapatos) se apoya sobre tacos o rinconeras."
        if _hay(mueble, "Apoyo central estante inferior"):
            est_piezas.append("Apoyo central estante inferior")
            texto_est += (" Parale el apoyo central al medio: el vano es ancho y sin él "
                          "el estante se dobla con el peso (R-27).")
        paso("Colocá el estante inferior", texto_est,
             piezas=est_piezas, herraje="Rinconera/taco")

    if _hay(mueble, "Puerta batiente"):
        paso("Colocá las puertas batientes",
             "Marcá los centros de las cazoletas en la cara interna de cada puerta siguiendo "
             "el plano acotado: distancias desde arriba/abajo y desde el canto lateral. Perforá "
             "con broca copa Ø35 solo 12-13 mm de profundidad (no atravieses la puerta), "
             "atornillá las bisagras y colgá las puertas. Regulá con los tornillos de la "
             "bisagra hasta que cierren parejas.",
             piezas=["Puerta batiente"],
             herraje="Bisagra cazoleta (según calidad) + tirador",
             tip="Herramientas: cinta métrica, lápiz, escuadra, broca copa/Forstner Ø35, tope de profundidad y punta PH2. Si elegiste soft-close, cierran solas sin golpe.")
    elif _hay(mueble, "Puerta corrediza"):
        paso("Colocá los rieles y las puertas corredizas",
             "Atornillá el riel de arriba y el de abajo. Colgá cada hoja en su riel; se "
             "solapan un poco para tapar la luz. Probá que deslicen suave.",
             piezas=["Puerta corrediza"],
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
