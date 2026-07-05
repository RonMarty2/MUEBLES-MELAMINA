"""Motor de despiece del ropero/placard.

Frontera de módulo (02_ARQUITECTURA.md): matemática pura. Recibe una receta
YA validada y normalizada, devuelve un Mueble con piezas, herrajes y
perforaciones. Reglas aplicadas: R-18 a R-25 y M-16 a M-23 de
AI_OPERATING_SYSTEM/11_REGLAS_Y_MEDIDAS_ROPERO.md, más las de cajones
(R-05 a R-08, R-12) reutilizadas de 05_REGLAS_DE_CARPINTERIA.md.

Sistema de coordenadas igual que despiece_escritorio.py: x=ancho, y=prof,
z=alto, origen en la esquina inferior izquierda frontal del módulo.
"""

import math

from .modelos import Pieza, Herraje, Perforacion, Mueble
from .validador_ropero import (ZOCALO, ALTO_BARRAL, RETRANQUEO_BARRAL,
                               ANCHO_MAX_PUERTA_BATIENTE, SOLAPE_CORREDIZA)
from .despiece_escritorio import confirmats_por_union, elegir_corredera
from .uniones import herraje_union
from .herrajes_calidad import (corredera as corredera_calidad,
                               bisagra as bisagra_calidad, union_sugerida)

ALTO_FRENTE_OBJETIVO = 250  # M-24: frente cómodo (rango real 120-350, R-07) para la
                             # cajonera del ropero, que NO reparte toda la altura del
                             # módulo (a diferencia del escritorio) sino un bloque acotado


def despiece_ropero(receta):
    """Receta validada de tipo ropero -> Mueble completo."""
    d = receta["dimensiones"]
    A, P, H = d["ancho"], d["profundidad"], d["alto"]
    e, ef = 18, 3
    color = receta["material"]["color"]
    mat = f"Melamina 18mm {color}"
    mat_fondo = "Fibrofácil 3mm"
    nivel = receta["calidad"]["nivel"]

    alto_estructura = H - ZOCALO           # entre el zócalo y la parte superior
    alto_interior = alto_estructura - 2 * e  # entre piso y techo

    mueble = Mueble(nombre=receta["nombre"], receta=receta)
    piezas, herrajes, perfs, avisos = (
        mueble.piezas, mueble.herrajes, mueble.perforaciones, mueble.avisos,
    )

    tipo_union, aviso_union = union_sugerida(nivel, receta["uniones"]["tipo"])
    if aviso_union:
        avisos.append(aviso_union)
    confirmats = 0
    clavos = 0
    tc_fino = 0  # tapacanto 0,45mm
    bisagras = 0
    rinconeras = 4  # un estante superior (techo) siempre lleva 4 (H-16)

    # --------------------------------------------------------------- Laterales
    piezas.append(Pieza("Lateral izquierdo", P, alto_estructura, e, mat,
                        (0, 0, ZOCALO), (e, P, alto_estructura),
                        cantos="canto frontal visible"))
    piezas.append(Pieza("Lateral derecho", P, alto_estructura, e, mat,
                        (A - e, 0, ZOCALO), (e, P, alto_estructura),
                        cantos="canto frontal visible"))
    tc_fino += 2 * alto_estructura
    confirmats += 2 * confirmats_por_union(P)  # techo y piso a cada lateral (aprox)

    # --------------------------------------------------------------- Piso, techo, fondo
    interior_ancho = A - 2 * e
    piezas.append(Pieza("Piso", P, interior_ancho, e, mat, (e, 0, ZOCALO), (interior_ancho, P, e)))
    piezas.append(Pieza("Techo (estante superior)", P, interior_ancho, e, mat,
                        (e, 0, H - e), (interior_ancho, P, e),
                        notas="Apoyado sobre rinconeras (H-16); actúa como estante superior (R-20)"))
    piezas.append(Pieza("Fondo", alto_estructura - 4, A - 4, ef, mat_fondo,
                        (2, P - ef, ZOCALO + 2), (A - 4, ef, alto_estructura - 4),
                        notas="Clavado sin sellar herméticamente, para ventilar (R-25)"))
    tc_fino += 0  # piso y techo no llevan canto visible (quedan tapados por puertas/zócalo)
    clavos += math.ceil(2 * ((A - 4) + (alto_estructura - 4)) / 150)
    confirmats += 2 * confirmats_por_union(P)  # piso y techo a los laterales

    # --------------------------------------------------------------- Zócalo frontal
    piezas.append(Pieza("Zócalo frontal", interior_ancho, ZOCALO, e, mat,
                        (e, 30, 0), (interior_ancho, e, ZOCALO),
                        notas="Retranqueado 30 mm del frente (R-18)"))
    confirmats += confirmats_por_union(interior_ancho)

    # --------------------------------------------------------------- Cajones (opcionales, R-24)
    caj = receta["cajones"]
    ancho_barral_zona = interior_ancho  # se reduce si hay cajones
    x_zona_barral_ini = e

    if caj["incluir"]:
        C = caj["ancho"]
        x0 = A - C  # igual patrón que despiece_escritorio: bahía contra el lateral derecho
        PC = P - e - 20  # deja margen frontal para el giro/cierre de la puerta
        interior_caj = C - 2 * e

        piezas.append(Pieza("Divisor cajones", P, alto_interior, e, mat,
                            (x0, 0, ZOCALO + e), (e, P, alto_interior),
                            cantos="canto frontal visible"))
        tc_fino += alto_interior
        confirmats += confirmats_por_union(P)

        n = caj["cantidad_cajones"]
        # La cajonera es un bloque acotado (M-24), NO reparte toda la altura del
        # módulo entre los cajones (a diferencia del escritorio, donde la cajonera
        # ES toda la altura de apoyo): evita frentes de 700+ mm imposibles de construir.
        alto_frente = ALTO_FRENTE_OBJETIVO
        alto_cajonera = n * (alto_frente + 3) + 3
        largo_corr = elegir_corredera(PC)
        ancho_caja = interior_caj - 26
        alto_caja = alto_frente - 30
        x_c = x0 + e + 13

        piezas.append(Pieza("Tapa de cajonera", P, interior_caj, e, mat,
                            (x0 + e, 0, ZOCALO + e + alto_cajonera),
                            (interior_caj, P, e),
                            notas="Cierra el bloque de cajones; arriba queda espacio libre"))
        confirmats += confirmats_por_union(interior_caj)

        avisos.append(
            f"Cajones del ropero: bloque de {n} frentes de {alto_frente} mm "
            f"({alto_cajonera} mm de alto total); caja {ancho_caja} × {largo_corr} × "
            f"{alto_caja} mm (R-05/R-24/M-24). Queda espacio libre arriba para un "
            "estante adicional."
        )

        for i in range(n):
            z_frente = ZOCALO + e + i * (alto_frente + 3)
            z_caja = z_frente + 15
            num = i + 1
            # y=0 (a ras del cuerpo, no sobresale): queda detrás de la puerta,
            # a diferencia del escritorio donde no hay puerta que lo tape.
            piezas.append(Pieza(f"Frente cajón {num}", C - 4, alto_frente, e, mat,
                                (x0 + 2, 0, z_frente), (C - 4, e, alto_frente),
                                cantos="4 cantos visibles",
                                notas="Fijado desde adentro con 4 tornillos 4×30"))
            piezas.append(Pieza(f"Lateral caja cajón {num} (izq)", largo_corr, alto_caja, e, mat,
                                (x_c, 0, z_caja), (e, largo_corr, alto_caja)))
            piezas.append(Pieza(f"Lateral caja cajón {num} (der)", largo_corr, alto_caja, e, mat,
                                (x_c + ancho_caja - e, 0, z_caja), (e, largo_corr, alto_caja)))
            piezas.append(Pieza(f"Frente interno cajón {num}", ancho_caja - 2 * e, alto_caja, e, mat,
                                (x_c + e, 0, z_caja), (ancho_caja - 2 * e, e, alto_caja)))
            piezas.append(Pieza(f"Contrafrente cajón {num}", ancho_caja - 2 * e, alto_caja, e, mat,
                                (x_c + e, largo_corr - e, z_caja), (ancho_caja - 2 * e, e, alto_caja)))
            piezas.append(Pieza(f"Fondo cajón {num}", largo_corr - 2, ancho_caja - 2, ef, mat_fondo,
                                (x_c + 1, 1, z_caja - ef), (ancho_caja - 2, largo_corr - 2, ef)))
            tc_fino += 2 * ((C - 4) + alto_frente)
            confirmats += 4 * confirmats_por_union(alto_caja)
            clavos += math.ceil(2 * ((ancho_caja - 2) + (largo_corr - 2)) / 150)
            perfs.append(Perforacion(
                "Divisor cajones / Lateral derecho", "cara interior", 0,
                z_caja + alto_caja // 2, 3.0, "10 mm",
                f"eje corredera cajón {num} (P-02)"))

        herrajes.append(corredera_calidad(nivel, largo_corr, n))
        herrajes.append(Herraje("H-15", "Tirador", n, "unidades", "uno por frente de cajón"))
        ancho_barral_zona = x0 - e - e  # lo que queda para el barral
    # --------------------------------------------------------------- Barral (R-19)
    largo_barral = ancho_barral_zona - 2 * RETRANQUEO_BARRAL
    piezas.append(Pieza("Barral colgador", largo_barral, 25, 25, "Tubo cromado",
                        (x_zona_barral_ini + RETRANQUEO_BARRAL, P // 2 - 12, ALTO_BARRAL),
                        (largo_barral, 25, 25),
                        notas="Tubo, no es corte de placa: comprar por metros (H-12)"))
    soportes_barral = 3 if ancho_barral_zona > 1000 else 2
    herrajes.append(Herraje("H-12", "Barral tubular cromado Ø25 + soportes",
                            1, "juego", f"{soportes_barral} soportes (R-19)"))

    # --------------------------------------------------------------- Estante inferior (M-23)
    if receta["estante_inferior"]["incluir"]:
        piezas.append(Pieza("Estante inferior (zapatos)", P - 20, ancho_barral_zona, e, mat,
                            (x_zona_barral_ini, 0, ZOCALO + 250), (ancho_barral_zona, P - 20, e),
                            notas="A 250 mm del piso, para calzado (M-23)"))
        confirmats += confirmats_por_union(ancho_barral_zona)
        rinconeras += 4

    # --------------------------------------------------------------- Puertas (R-21/R-23)
    puertas = receta["puertas"]
    if puertas["tipo"] == "batiente":
        n = puertas["cantidad"]
        ancho_hoja = (interior_ancho - 3 * (n + 1)) // n
        alto_hoja = alto_estructura - 6
        for i in range(n):
            x_hoja = e + 3 + i * (ancho_hoja + 3)
            piezas.append(Pieza(f"Puerta batiente {i + 1}", alto_hoja, ancho_hoja, e, mat,
                                (x_hoja, -e, ZOCALO + 3), (ancho_hoja, e, alto_hoja),
                                cantos="4 cantos visibles"))
        n_bis = 2 if alto_hoja <= 1500 else (3 if alto_hoja <= 2100 else 4)
        bisagras = n * n_bis
        herrajes.append(bisagra_calidad(nivel, bisagras))
        herrajes.append(Herraje("H-15", "Tirador", n, "unidades", "uno por puerta"))
        avisos.append(f"{n} puertas batientes de {ancho_hoja}×{alto_hoja} mm, {n_bis} bisagras c/u (R-21/R-22).")
    elif puertas["tipo"] == "corrediza":
        n = puertas["cantidad"]
        ancho_hoja = (interior_ancho // n) + SOLAPE_CORREDIZA
        alto_hoja = alto_estructura - 10
        for i in range(n):
            x_hoja = e + i * (interior_ancho // n) - (SOLAPE_CORREDIZA // 2 if i > 0 else 0)
            piezas.append(Pieza(f"Puerta corrediza {i + 1}", alto_hoja, ancho_hoja, e, mat,
                                (x_hoja, -20 if i % 2 == 0 else -40, ZOCALO + 5),
                                (ancho_hoja, e, alto_hoja),
                                cantos="4 cantos visibles",
                                notas=f"Riel {'delantero' if i % 2 == 0 else 'trasero'} (R-23)"))
        herrajes.append(Herraje("H-14", "Riel corredizo superior + inferior (juego)",
                                1, "juego", f"largo {A} mm (R-23)"))
        herrajes.append(Herraje("H-15", "Tirador", n, "unidades", "uno por puerta"))
        avisos.append(f"{n} puertas corredizas de {ancho_hoja}×{alto_hoja} mm, solape {SOLAPE_CORREDIZA} mm (R-23).")
    else:
        avisos.append("Módulo sin puertas (placard abierto tipo vestidor).")

    # --------------------------------------------------------------- Herrajes generales
    herrajes.insert(0, herraje_union(tipo_union, confirmats))
    herrajes.append(Herraje("H-07", "Clavos 1½\"", clavos, "unidades", "fijar el fondo (R-10)"))
    herrajes.append(Herraje("H-08", "Tapacanto PVC 0,45 mm",
                            round(tc_fino * 1.10 / 1000, 1), "metros", "cantos visibles (R-11)"))
    herrajes.append(Herraje("H-16", "Rinconera/taco de estante", rinconeras, "unidades",
                            "sostener el techo/estante superior (y el inferior si existe)"))

    return mueble
