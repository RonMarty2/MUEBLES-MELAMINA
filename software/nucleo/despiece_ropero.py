"""Motor de despiece del ropero/placard.

Frontera de módulo (02_ARQUITECTURA.md): matemática pura. Recibe una receta
YA validada y normalizada, devuelve un Mueble con piezas, herrajes y
perforaciones. Reglas aplicadas: R-18 a R-30 y M-16 a M-24 de
AI_OPERATING_SYSTEM/11_REGLAS_Y_MEDIDAS_ROPERO.md, más las de cajones
(R-05 a R-08, R-12) reutilizadas de 05_REGLAS_DE_CARPINTERIA.md.

R-30 (cuerpos): un ropero de 2-3 cuerpos son 2-3 módulos completos e
independientes (cada uno con sus laterales, piso, techo, fondo, zócalos y
refuerzos) construidos por separado y atornillados entre sí. Con 1 cuerpo,
los nombres de pieza quedan exactamente como siempre; con más, llevan el
sufijo " (cuerpo N)".

Sistema de coordenadas igual que despiece_escritorio.py: x=ancho, y=prof,
z=alto, origen en la esquina inferior izquierda frontal del mueble.
"""

import math

from .modelos import Pieza, Herraje, Perforacion, Mueble
from .validador_ropero import (ZOCALO, ALTO_BARRAL, RETRANQUEO_BARRAL,
                               ANCHO_MAX_PUERTA_BATIENTE, SOLAPE_CORREDIZA)
from .despiece_escritorio import confirmats_por_union, elegir_corredera
from .uniones import herraje_union
from .herrajes_calidad import (DISTANCIA_CAZOLETA_CANTO, altura_corredera,
                               corredera as corredera_calidad,
                               bisagra as bisagra_calidad, posiciones_bisagras,
                               union_sugerida)

ALTO_FRENTE_OBJETIVO = 250  # M-24: frente cómodo (rango real 120-350, R-07) para la
                             # cajonera del ropero, que NO reparte toda la altura del
                             # módulo (a diferencia del escritorio) sino un bloque acotado

VANO_MAX_ESTANTE = 800       # R-27: un estante de melamina 18 mm cargado se pandea por el
                             # medio a partir de ~800 mm de vano libre; más ancho que eso
                             # exige un refuerzo de canto (mismo principio que la viga R-13)
ALTO_REFUERZO = 80           # R-27: alto del travesaño de canto bajo el techo


def despiece_ropero(receta):
    """Receta validada de tipo ropero -> Mueble completo."""
    d = receta["dimensiones"]
    A_total, P, H = d["ancho"], d["profundidad"], d["alto"]
    e, ef = 18, 3
    color = receta["material"]["color"]
    mat = f"Melamina 18mm {color}"
    mat_fondo = "Fibrofácil 3mm"
    nivel = receta["calidad"]["nivel"]
    caj = receta["cajones"]
    puertas = receta["puertas"]

    n_cuerpos = receta["cuerpos"]["cantidad"]
    A = A_total // n_cuerpos          # ancho de CADA cuerpo (R-30)
    A_util = A * n_cuerpos            # ancho total efectivo

    alto_estructura = H - ZOCALO           # entre el zócalo y la parte superior
    alto_interior = alto_estructura - 2 * e  # entre piso y techo

    mueble = Mueble(nombre=receta["nombre"], receta=receta)
    piezas, herrajes, perfs, avisos = (
        mueble.piezas, mueble.herrajes, mueble.perforaciones, mueble.avisos,
    )

    tipo_union, aviso_union = union_sugerida(nivel, receta["uniones"]["tipo"])
    if aviso_union:
        avisos.append(aviso_union)
    if A_util != A_total:
        avisos.append(
            f"Ancho total ajustado a {A_util} mm ({n_cuerpos} cuerpos de {A} mm parejos).")

    confirmats = 0
    clavos = 0
    tc_fino = 0        # tapacanto 0,45mm
    bisagras_total = 0
    puertas_total = 0
    tiradores_cajones = 0
    rinconeras = 0
    tornillos_4x30 = 0  # unión entre cuerpos (R-30)
    corredera_info = None  # (largo_corr, n) del cuerpo con cajones

    def armar_cuerpo(k):
        """Construye el cuerpo k (1-based) completo, desplazado en x."""
        nonlocal confirmats, clavos, tc_fino, bisagras_total, puertas_total, \
            tiradores_cajones, rinconeras, corredera_info
        suf = "" if n_cuerpos == 1 else f" (cuerpo {k})"
        xo = (k - 1) * A                 # offset x del cuerpo
        con_cajones = caj["incluir"] and k == n_cuerpos  # cajones en el cuerpo derecho
        primero = k == 1                 # avisos comunes solo una vez

        # ---------------------------------------------------------- Laterales
        piezas.append(Pieza(f"Lateral izquierdo{suf}", P, alto_estructura, e, mat,
                            (xo, 0, ZOCALO), (e, P, alto_estructura),
                            cantos="canto frontal visible"))
        piezas.append(Pieza(f"Lateral derecho{suf}", P, alto_estructura, e, mat,
                            (xo + A - e, 0, ZOCALO), (e, P, alto_estructura),
                            cantos="canto frontal visible"))
        tc_fino += 2 * alto_estructura
        confirmats += 2 * confirmats_por_union(P)
        rinconeras += 4  # techo del cuerpo (H-16)

        # ---------------------------------------------------------- Piso, techo, fondo
        interior_ancho = A - 2 * e
        piezas.append(Pieza(f"Piso{suf}", P, interior_ancho, e, mat,
                            (xo + e, 0, ZOCALO), (interior_ancho, P, e)))
        piezas.append(Pieza(f"Techo (estante superior){suf}", P, interior_ancho, e, mat,
                            (xo + e, 0, H - e), (interior_ancho, P, e),
                            notas="Apoyado sobre rinconeras (H-16); actúa como estante superior (R-20)"))
        piezas.append(Pieza(f"Fondo{suf}", alto_estructura - 4, A - 4, ef, mat_fondo,
                            (xo + 2, P - ef, ZOCALO + 2), (A - 4, ef, alto_estructura - 4),
                            notas="Clavado sin sellar herméticamente, para ventilar (R-25). "
                                  "Clavado también a las líneas intermedias: es lo que evita "
                                  "que el mueble se tuerza en paralelogramo (R-29/R-26)"))
        clavos += math.ceil(2 * ((A - 4) + (alto_estructura - 4)) / 150)
        confirmats += 2 * confirmats_por_union(P)

        # ---------------------------------------------------------- Zócalos (R-18/R-28)
        piezas.append(Pieza(f"Zócalo frontal{suf}", interior_ancho, ZOCALO, e, mat,
                            (xo + e, 30, 0), (interior_ancho, e, ZOCALO),
                            notas="Retranqueado 30 mm del frente (R-18)"))
        confirmats += confirmats_por_union(interior_ancho)
        piezas.append(Pieza(f"Zócalo trasero{suf}", interior_ancho, ZOCALO, e, mat,
                            (xo + e, P - e - ef, 0), (interior_ancho, e, ZOCALO),
                            notas="Segunda línea de apoyo del piso: sin él, el piso cargado "
                                  "cede atrás (R-28). No lleva canto (no se ve)"))
        confirmats += confirmats_por_union(interior_ancho)
        clavos += math.ceil(interior_ancho / 150)  # R-29: fondo clavado al zócalo trasero

        # ---------------------------------------------------------- Refuerzo anti-pandeo (R-27)
        if interior_ancho > VANO_MAX_ESTANTE:
            piezas.append(Pieza(f"Refuerzo bajo techo{suf}", interior_ancho, ALTO_REFUERZO, e, mat,
                                (xo + e, P - e - ef, H - e - ALTO_REFUERZO),
                                (interior_ancho, e, ALTO_REFUERZO),
                                notas=f"De canto, pegado al fondo: evita que el techo de "
                                      f"{interior_ancho} mm se pandee (R-27)"))
            confirmats += confirmats_por_union(interior_ancho)
            clavos += math.ceil(interior_ancho / 150)  # R-29
            if primero:
                cada = "cada cuerpo" if n_cuerpos > 1 else "el interior"
                avisos.append(
                    f"En {cada} el vano es de {interior_ancho} mm (más de {VANO_MAX_ESTANTE} mm): "
                    "el techo lleva un refuerzo de canto y el piso apoya en zócalo delantero y "
                    "trasero, para que no se doblen por el medio con el peso (R-27/R-28). Sin "
                    "esto, el mueble se ve bien vacío pero cede cargado.")
        elif interior_ancho > 600 and primero:
            avisos.append(
                f"Estantes de {interior_ancho} mm de vano: carga media (~25 kg distribuidos). "
                "No apiles cosas muy pesadas en el medio del techo (R-27).")

        # ---------------------------------------------------------- Cajones (solo un cuerpo, R-24)
        ancho_barral_zona = interior_ancho
        x_zona_barral_ini = xo + e
        if con_cajones:
            C = caj["ancho"]
            x0 = xo + A - C  # bahía contra el lateral derecho del cuerpo
            PC = P - e - 20
            interior_caj = C - 2 * e

            piezas.append(Pieza(f"Divisor cajones{suf}", P, alto_interior, e, mat,
                                (x0, 0, ZOCALO + e), (e, P, alto_interior),
                                cantos="canto frontal visible"))
            tc_fino += alto_interior
            confirmats += confirmats_por_union(P)
            clavos += math.ceil(alto_interior / 150)  # R-29

            n = caj["cantidad_cajones"]
            alto_frente = ALTO_FRENTE_OBJETIVO
            alto_cajonera = n * (alto_frente + 3) + 3
            largo_corr = elegir_corredera(PC)
            ancho_caja = interior_caj - 26
            alto_caja = alto_frente - 30
            x_c = x0 + e + 13

            piezas.append(Pieza(f"Tapa de cajonera{suf}", P, interior_caj, e, mat,
                                (x0 + e, 0, ZOCALO + e + alto_cajonera),
                                (interior_caj, P, e),
                                notas="Cierra el bloque de cajones; arriba queda espacio libre"))
            confirmats += confirmats_por_union(interior_caj)

            donde = f" (en el cuerpo {k})" if n_cuerpos > 1 else ""
            avisos.append(
                f"Cajones del ropero{donde}: bloque de {n} frentes de {alto_frente} mm "
                f"({alto_cajonera} mm de alto total); caja {ancho_caja} × {largo_corr} × "
                f"{alto_caja} mm (R-05/R-24/M-24). Queda espacio libre arriba para un "
                "estante adicional."
            )

            for i in range(n):
                z_frente = ZOCALO + e + i * (alto_frente + 3)
                z_caja = z_frente + 15
                num = i + 1
                piezas.append(Pieza(f"Frente cajón {num}{suf}", C - 4, alto_frente, e, mat,
                                    (x0 + 2, 0, z_frente), (C - 4, e, alto_frente),
                                    cantos="4 cantos visibles",
                                    notas="Fijado desde adentro con 4 tornillos 4×30"))
                piezas.append(Pieza(f"Lateral caja cajón {num} (izq){suf}", largo_corr, alto_caja, e, mat,
                                    (x_c, 0, z_caja), (e, largo_corr, alto_caja)))
                piezas.append(Pieza(f"Lateral caja cajón {num} (der){suf}", largo_corr, alto_caja, e, mat,
                                    (x_c + ancho_caja - e, 0, z_caja), (e, largo_corr, alto_caja)))
                piezas.append(Pieza(f"Frente interno cajón {num}{suf}", ancho_caja - 2 * e, alto_caja, e, mat,
                                    (x_c + e, 0, z_caja), (ancho_caja - 2 * e, e, alto_caja)))
                piezas.append(Pieza(f"Contrafrente cajón {num}{suf}", ancho_caja - 2 * e, alto_caja, e, mat,
                                    (x_c + e, largo_corr - e, z_caja), (ancho_caja - 2 * e, e, alto_caja)))
                piezas.append(Pieza(f"Fondo cajón {num}{suf}", largo_corr - 2, ancho_caja - 2, ef, mat_fondo,
                                    (x_c + 1, 1, z_caja - ef), (ancho_caja - 2, largo_corr - 2, ef)))
                tc_fino += 2 * ((C - 4) + alto_frente)
                confirmats += 4 * confirmats_por_union(alto_caja)
                clavos += math.ceil(2 * ((ancho_caja - 2) + (largo_corr - 2)) / 150)
                eje_relativo = altura_corredera(alto_caja)
                eje = z_caja + eje_relativo
                perfs.append(Perforacion(
                    f"Divisor cajones / Lateral derecho{suf}", "cara interior", 0,
                    eje, 3.0, "10 mm",
                    f"eje corredera cajón {num}: centro a {eje_relativo} mm del canto inferior "
                    f"de la caja y a {eje} mm del piso del mueble (P-02); fijar con tornillos 4×16"))

            tiradores_cajones += n
            corredera_info = (largo_corr, n)
            ancho_barral_zona = (x0 - e) - (xo + e)  # lo que queda para el barral

        # ---------------------------------------------------------- Barral (R-19)
        largo_barral = ancho_barral_zona - 2 * RETRANQUEO_BARRAL
        piezas.append(Pieza(f"Barral colgador{suf}", largo_barral, 25, 25, "Tubo cromado",
                            (x_zona_barral_ini + RETRANQUEO_BARRAL, P // 2 - 12, ALTO_BARRAL),
                            (largo_barral, 25, 25),
                            notas="Tubo, no es corte de placa: comprar por metros (H-12)"))

        # ---------------------------------------------------------- Estante inferior (M-23)
        if receta["estante_inferior"]["incluir"]:
            piezas.append(Pieza(f"Estante inferior (zapatos){suf}", P - 20, ancho_barral_zona, e, mat,
                                (x_zona_barral_ini, 0, ZOCALO + 250), (ancho_barral_zona, P - 20, e),
                                notas="A 250 mm del piso, para calzado (M-23)"))
            confirmats += confirmats_por_union(ancho_barral_zona)
            rinconeras += 4
            if ancho_barral_zona > VANO_MAX_ESTANTE:
                x_apoyo = x_zona_barral_ini + ancho_barral_zona // 2 - e // 2
                piezas.append(Pieza(f"Apoyo central estante inferior{suf}", P - 40, 250 - e, e, mat,
                                    (x_apoyo, 10, ZOCALO + e), (e, P - 40, 250 - e),
                                    notas=f"Parado al medio del vano de {ancho_barral_zona} mm: "
                                          "sin él, el estante de zapatos se dobla (R-27)"))
                confirmats += 4

        # ---------------------------------------------------------- Puertas batientes del cuerpo (R-21)
        if puertas["tipo"] == "batiente":
            n_hojas = puertas["cantidad"] if n_cuerpos == 1 else 2  # R-30
            interior_p = A - 2 * e
            ancho_hoja = (interior_p - 3 * (n_hojas + 1)) // n_hojas
            alto_hoja = alto_estructura - 6
            pos_bisagras = posiciones_bisagras(alto_hoja)
            for i in range(n_hojas):
                x_hoja = xo + e + 3 + i * (ancho_hoja + 3)
                nombre_puerta = f"Puerta batiente {i + 1}{suf}"
                piezas.append(Pieza(nombre_puerta, alto_hoja, ancho_hoja, e, mat,
                                    (x_hoja, -e, ZOCALO + 3), (ancho_hoja, e, alto_hoja),
                                    cantos="4 cantos visibles"))
                lado_bisagra = "izquierdo" if i < n_hojas / 2 else "derecho"
                x_cazoleta = (DISTANCIA_CAZOLETA_CANTO if lado_bisagra == "izquierdo"
                              else ancho_hoja - DISTANCIA_CAZOLETA_CANTO)
                for pos_sup in pos_bisagras:
                    y_desde_abajo = alto_hoja - pos_sup
                    perfs.append(Perforacion(
                        nombre_puerta, "cara interior", x_cazoleta, y_desde_abajo,
                        35.0, "12-13 mm",
                        f"cazoleta bisagra: centro a {pos_sup} mm del borde superior y "
                        f"{DISTANCIA_CAZOLETA_CANTO} mm del canto {lado_bisagra}; "
                        "NO perforar pasante (P-04/R-22)"))
            bisagras_total += n_hojas * len(pos_bisagras)
            puertas_total += n_hojas
            if primero:
                por_cuerpo = " por cuerpo" if n_cuerpos > 1 else ""
                pos_txt = ", ".join(f"{p} mm" for p in pos_bisagras)
                avisos.append(
                    f"{n_hojas} puertas batientes{por_cuerpo} de {ancho_hoja}×{alto_hoja} mm, "
                    f"{len(pos_bisagras)} bisagras c/u (R-21/R-22). Centros desde borde "
                    f"superior: {pos_txt}; cazoleta Ø35 a {DISTANCIA_CAZOLETA_CANTO} mm "
                    "del canto (P-04).")

    for k in range(1, n_cuerpos + 1):
        armar_cuerpo(k)

    # ------------------------------------------------------------- Unión entre cuerpos (R-30)
    if n_cuerpos > 1:
        puntos_por_union = max(4, math.ceil(alto_estructura / 400))
        tornillos_4x30 = puntos_por_union * (n_cuerpos - 1)
        avisos.append(
            f"Los cuerpos se atornillan entre sí por los laterales que se tocan: "
            f"{puntos_por_union} tornillos 4×30 por unión (adelante/atrás, arriba/abajo y "
            "repartidos), prensando los laterales alineados antes de atornillar (R-30).")

    # ------------------------------------------------------------- Puertas corredizas (globales, R-23)
    if puertas["tipo"] == "corrediza":
        n = puertas["cantidad"]
        interior_total = A_util - 2 * e
        ancho_hoja = (interior_total // n) + SOLAPE_CORREDIZA
        alto_hoja = alto_estructura - 10
        for i in range(n):
            x_hoja = e + i * (interior_total // n) - (SOLAPE_CORREDIZA // 2 if i > 0 else 0)
            piezas.append(Pieza(f"Puerta corrediza {i + 1}", alto_hoja, ancho_hoja, e, mat,
                                (x_hoja, -20 if i % 2 == 0 else -40, ZOCALO + 5),
                                (ancho_hoja, e, alto_hoja),
                                cantos="4 cantos visibles",
                                notas=f"Riel {'delantero' if i % 2 == 0 else 'trasero'} (R-23)"))
        herrajes.append(Herraje("H-14", "Riel corredizo superior + inferior (juego)",
                                1, "juego", f"largo {A_util} mm, cruza todos los cuerpos (R-23)"))
        puertas_total += n
        avisos.append(f"{n} puertas corredizas de {ancho_hoja}×{alto_hoja} mm, solape {SOLAPE_CORREDIZA} mm (R-23).")
    elif puertas["tipo"] == "ninguna":
        avisos.append("Módulo sin puertas (placard abierto tipo vestidor).")

    # ------------------------------------------------------------- Herrajes generales
    herrajes.insert(0, herraje_union(tipo_union, confirmats))
    if bisagras_total:
        herrajes.append(bisagra_calidad(nivel, bisagras_total))
    if corredera_info:
        herrajes.append(corredera_calidad(nivel, corredera_info[0], corredera_info[1]))
    if puertas_total + tiradores_cajones:
        herrajes.append(Herraje("H-15", "Tirador", puertas_total + tiradores_cajones,
                                "unidades", "uno por puerta y por frente de cajón"))
    soportes_por_cuerpo = 3 if (A - 2 * e) > 1000 else 2
    herrajes.append(Herraje("H-12", "Barral tubular cromado Ø25 + soportes",
                            n_cuerpos, "juego(s)", f"{soportes_por_cuerpo} soportes por cuerpo (R-19)"))
    if tornillos_4x30:
        herrajes.append(Herraje("H-04", "Tornillo aglomerado 4×30", tornillos_4x30,
                                "unidades", "unir los cuerpos entre sí (R-30)"))
    herrajes.append(Herraje("H-07", "Clavos 1½\"", clavos, "unidades", "fijar el fondo (R-10)"))
    herrajes.append(Herraje("H-08", "Tapacanto PVC 0,45 mm",
                            round(tc_fino * 1.10 / 1000, 1), "metros", "cantos visibles (R-11)"))
    herrajes.append(Herraje("H-16", "Rinconera/taco de estante", rinconeras, "unidades",
                            "sostener el techo/estante superior (y el inferior si existe)"))

    return mueble
