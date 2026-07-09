"""Motor de despiece del escritorio gamer.

Frontera de módulo (02_ARQUITECTURA.md): matemática pura. Recibe una receta
YA validada y normalizada, devuelve un Mueble con piezas, herrajes y
perforaciones. No lee archivos, no habla con IAs, no formatea salidas.

Reglas aplicadas: R-xx de 05_REGLAS_DE_CARPINTERIA.md, M-xx de
06_MEDIDAS_ESTANDAR.md, H-xx/P-xx de 07_HERRAJES_Y_TORNILLERIA.md.

Sistema de coordenadas (ver modelos.py): x = ancho, y = profundidad,
z = alto. El mueble se calcula con la cajonera a la DERECHA y el soporte de
CPU a la izquierda; si la receta pide cajonera a la izquierda, se espeja todo
en x al final.
"""

import math

from .modelos import Pieza, Herraje, Perforacion, Mueble
from .validador_escritorio import espesor_tapa, vano_libre
from .uniones import herraje_union
from .herrajes_calidad import (altura_corredera,
                               corredera as corredera_calidad, union_sugerida)

RETRANQUEO_FRONTAL = 50      # las patas/paneles entran 50 mm respecto del frente
ALTURA_BANDEJA_CPU = 100     # M-06
LARGOS_CORREDERA = [250, 300, 350, 400, 450, 500, 550, 600]  # R-08
VANO_MAXIMO_SIN_VIGA = 1200  # R-13
ALTO_LIBRE_ELEVACION_MONITOR = 110  # M-25: deja pasar un teclado (25-35mm) + mano


def confirmats_por_union(largo_union):
    """R-09: 2 confirmats hasta 300 mm de unión, luego 1 cada 200 mm."""
    if largo_union <= 300:
        return 2
    return 2 + math.ceil((largo_union - 300) / 200)


def elegir_corredera(profundidad_interior):
    """R-08: la corredera comercial más larga que quepa con 20 mm de margen."""
    candidatas = [l for l in LARGOS_CORREDERA if l <= profundidad_interior - 20]
    return candidatas[-1] if candidatas else LARGOS_CORREDERA[0]


def despiece_escritorio(receta):
    """Receta validada de tipo escritorio_gamer -> Mueble completo."""
    d = receta["dimensiones"]
    A, P, H = d["ancho"], d["profundidad"], d["alto"]
    e = receta["material"]["espesor"]
    ef = receta["material"]["espesor_fondo"]
    color = receta["material"]["color"]
    t = espesor_tapa(receta)
    alto_apoyo = H - t
    prof_panel = P - RETRANQUEO_FRONTAL

    mat = f"Melamina {e}mm {color}"
    mat_fondo = f"Fibrofácil {ef}mm"
    mat_crudo = f"Aglomerado crudo {e}mm"  # capa oculta de la tapa doble (no se ve)
    nivel = receta["calidad"]["nivel"]

    mueble = Mueble(nombre=receta["nombre"], receta=receta)
    piezas, herrajes, perfs, avisos = (
        mueble.piezas, mueble.herrajes, mueble.perforaciones, mueble.avisos,
    )

    # Nivel premium sugiere unión excéntrica aunque el usuario haya dejado confirmat.
    tipo_union, aviso_union = union_sugerida(nivel, receta["uniones"]["tipo"])
    if aviso_union:
        avisos.append(aviso_union)

    confirmats = 0
    escuadras_mm = 0          # mm de unión oculta que llevan escuadras (H-11)
    clavos = 0
    tapacanto_fino_mm = 0     # H-08 (0,45 mm)
    tapacanto_grueso_mm = 0   # H-09 (2 mm)
    regatones = 0
    tornillos_frente = 0      # H-04 (4×30)

    # ------------------------------------------------------------------ Tapa
    if receta["tapa"]["tipo"] == "doble_18":
        # Capa de abajo en aglomerado CRUDO (no se ve, es más barato) y solo la
        # capa de arriba lleva melamina decorativa + tapacanto visible.
        piezas.append(Pieza("Tapa capa inferior (oculta)", A, P, 18, mat_crudo,
                            (0, 0, H - 36), (A, P, 18),
                            notas="Aglomerado crudo: va escondida abajo, no necesita ser decorativa"))
        piezas.append(Pieza("Tapa capa superior (visible)", A, P, 18, mat,
                            (0, 0, H - 18), (A, P, 18),
                            cantos="4 cantos visibles (banda de 2 mm)"))
        tapacanto_grueso_mm += 2 * (A + P)  # solo la capa visible lleva tapacanto
        avisos.append(
            "Tapa doble: la capa de arriba es melamina decorativa (la que ves) y la de "
            "abajo es aglomerado crudo más barato (va escondida). Se encolan y atornillan "
            "desde abajo con 4×30 en grilla de ~300 mm. Así tenés una tapa rígida de 36 mm "
            "pagando una sola cara decorativa."
        )
        tornillos_frente += math.ceil(A / 300) * math.ceil(P / 300)
    else:
        piezas.append(Pieza("Tapa", A, P, t, mat,
                            (0, 0, H - t), (A, P, t),
                            cantos="4 cantos visibles (banda de 2 mm)"))
        tapacanto_grueso_mm += 2 * (A + P)

    # ------------------------------------------------- Elevación para monitor (M-25)
    elev = receta["elevacion_monitor"]
    if elev["incluir"]:
        ancho_elev, prof_elev = elev["ancho"], elev["profundidad"]
        x_elev = (A - ancho_elev) // 2
        y_elev = P - prof_elev
        z_apoyo = H  # se apoya sobre la cara superior de la tapa principal

        piezas.append(Pieza("Pata elevación monitor (izq)", prof_elev, ALTO_LIBRE_ELEVACION_MONITOR, e, mat,
                            (x_elev, y_elev, z_apoyo), (e, prof_elev, ALTO_LIBRE_ELEVACION_MONITOR),
                            cantos="canto frontal visible"))
        piezas.append(Pieza("Pata elevación monitor (der)", prof_elev, ALTO_LIBRE_ELEVACION_MONITOR, e, mat,
                            (x_elev + ancho_elev - e, y_elev, z_apoyo),
                            (e, prof_elev, ALTO_LIBRE_ELEVACION_MONITOR),
                            cantos="canto frontal visible"))
        piezas.append(Pieza("Tapa elevación monitor", ancho_elev, prof_elev, e, mat,
                            (x_elev, y_elev, z_apoyo + ALTO_LIBRE_ELEVACION_MONITOR),
                            (ancho_elev, prof_elev, e),
                            cantos="4 cantos visibles",
                            notas=f"Deja {ALTO_LIBRE_ELEVACION_MONITOR} mm libres abajo para deslizar el teclado"))
        tapacanto_fino_mm += 2 * ALTO_LIBRE_ELEVACION_MONITOR
        tapacanto_grueso_mm += 2 * (ancho_elev + prof_elev)
        n_conf_elev = confirmats_por_union(prof_elev)
        confirmats += 2 * n_conf_elev  # patas <-> tapa elevada
        confirmats += 2 * 2            # patas <-> tapa principal (2 tornillos c/u desde abajo)
        avisos.append(
            f"Elevación para monitor: bandeja de {ancho_elev}×{prof_elev} mm a "
            f"{ALTO_LIBRE_ELEVACION_MONITOR} mm sobre la tapa (M-25), suficiente para "
            "deslizar el teclado debajo."
        )

    # ------------------------------------------------- Apoyos verticales
    piezas.append(Pieza("Lateral izquierdo (pata panel)", prof_panel, alto_apoyo, e, mat,
                        (0, RETRANQUEO_FRONTAL, 0), (e, prof_panel, alto_apoyo),
                        cantos="canto frontal visible"))
    tapacanto_fino_mm += alto_apoyo
    regatones += 2
    escuadras_mm += prof_panel  # unión tapa-lateral

    x_izq_interior = e  # cara interna del apoyo izquierdo del vano

    # ------------------------------------------------- Soporte de CPU (R-17)
    cpu = receta["soporte_cpu"]
    if cpu["incluir"]:
        w_cpu = cpu["ancho"]
        x_parante = e + w_cpu
        piezas.append(Pieza("Parante soporte CPU", prof_panel, alto_apoyo, e, mat,
                            (x_parante, RETRANQUEO_FRONTAL, 0),
                            (e, prof_panel, alto_apoyo),
                            cantos="canto frontal visible"))
        piezas.append(Pieza("Bandeja CPU", prof_panel, w_cpu, e, mat,
                            (e, RETRANQUEO_FRONTAL, ALTURA_BANDEJA_CPU),
                            (w_cpu, prof_panel, e),
                            cantos="canto frontal visible",
                            notas=f"A {ALTURA_BANDEJA_CPU} mm del piso (M-06): ventilación y limpieza"))
        tapacanto_fino_mm += alto_apoyo + w_cpu
        regatones += 2
        escuadras_mm += prof_panel
        # Uniones bandeja ↔ lateral y bandeja ↔ parante (P-01)
        n_conf = confirmats_por_union(prof_panel)
        confirmats += 2 * n_conf
        for lado, pieza_nombre in (("Lateral izquierdo (pata panel)", "lateral"),
                                   ("Parante soporte CPU", "parante")):
            for i in range(n_conf):
                y_pos = 50 + i * max(1, (prof_panel - 100) // max(1, n_conf - 1)) if n_conf > 1 else prof_panel // 2
                perfs.append(Perforacion(
                    lado, "cara (por fuera)", y_pos, ALTURA_BANDEJA_CPU + e // 2,
                    4.5, "pasante",
                    f"confirmat bandeja CPU al {pieza_nombre} (P-01)"))
        x_izq_interior = x_parante + e

    # ------------------------------------------------- Cajonera (estructural)
    caj = receta["cajonera"]
    con_cajonera = caj["posicion"] != "ninguna"
    if con_cajonera:
        C = caj["ancho"]
        PC = P - 100                       # M-09: retranqueo frontal + paso de cables
        x0 = A - C
        y0 = RETRANQUEO_FRONTAL
        interior = C - 2 * e               # R-02

        piezas.append(Pieza("Lateral cajonera interno", PC, alto_apoyo, e, mat,
                            (x0, y0, 0), (e, PC, alto_apoyo),
                            cantos="canto frontal visible"))
        piezas.append(Pieza("Lateral cajonera externo", PC, alto_apoyo, e, mat,
                            (A - e, y0, 0), (e, PC, alto_apoyo),
                            cantos="canto frontal visible"))
        piezas.append(Pieza("Piso cajonera", PC, interior, e, mat,
                            (x0 + e, y0, 0), (interior, PC, e)))
        piezas.append(Pieza("Fondo cajonera", alto_apoyo - 4, C - 4, ef, mat_fondo,
                            (x0 + 2, y0 + PC, 2), (C - 4, ef, alto_apoyo - 4),
                            notas="Clavado por detrás (R-10)"))
        tapacanto_fino_mm += 2 * alto_apoyo + interior
        regatones += 4
        escuadras_mm += 2 * PC  # unión tapa ↔ laterales cajonera
        clavos += math.ceil(2 * ((C - 4) + (alto_apoyo - 4)) / 150)

        # Piso ↔ laterales (P-01)
        n_conf = confirmats_por_union(PC)
        confirmats += 2 * n_conf
        for lado in ("Lateral cajonera interno", "Lateral cajonera externo"):
            for i in range(n_conf):
                y_pos = 50 + (i * (PC - 100) // (n_conf - 1) if n_conf > 1 else PC // 2)
                perfs.append(Perforacion(
                    lado, "cara (por fuera)", y_pos, e // 2, 4.5, "pasante",
                    "confirmat piso cajonera (P-01)"))

        # ---------------------------------------------------------- Cajones
        n = caj["cantidad_cajones"]
        alto_util = alto_apoyo - e                       # sobre el piso de la cajonera
        alto_frente = (alto_util - 3 * n) // n           # R-06
        largo_corr = elegir_corredera(PC)                # R-08
        ancho_caja = interior - 26                       # R-05
        alto_caja = alto_frente - 30                     # R-12
        x_caja = x0 + e + 13

        avisos.append(
            f"Cajones: {n} frentes de {alto_frente} mm de alto (R-06), caja de "
            f"{ancho_caja} × {largo_corr} × {alto_caja} mm, correderas telescópicas "
            f"de {largo_corr} mm (R-05/R-08)."
        )

        for i in range(n):
            z_frente = e + i * (alto_frente + 3)
            z_caja = z_frente + 15
            num = i + 1
            piezas.append(Pieza(f"Frente cajón {num}", C - 4, alto_frente, e, mat,
                                (x0 + 2, y0 - e, z_frente), (C - 4, e, alto_frente),
                                cantos="4 cantos visibles",
                                notas="Se fija desde adentro con 4 tornillos 4×30 (H-04)"))
            piezas.append(Pieza(f"Lateral caja cajón {num} (izq)", largo_corr, alto_caja, e, mat,
                                (x_caja, y0, z_caja), (e, largo_corr, alto_caja)))
            piezas.append(Pieza(f"Lateral caja cajón {num} (der)", largo_corr, alto_caja, e, mat,
                                (x_caja + ancho_caja - e, y0, z_caja),
                                (e, largo_corr, alto_caja)))
            piezas.append(Pieza(f"Frente interno cajón {num}", ancho_caja - 2 * e, alto_caja, e, mat,
                                (x_caja + e, y0, z_caja),
                                (ancho_caja - 2 * e, e, alto_caja)))
            piezas.append(Pieza(f"Contrafrente cajón {num}", ancho_caja - 2 * e, alto_caja, e, mat,
                                (x_caja + e, y0 + largo_corr - e, z_caja),
                                (ancho_caja - 2 * e, e, alto_caja)))
            piezas.append(Pieza(f"Fondo cajón {num}", largo_corr - 2, ancho_caja - 2, ef, mat_fondo,
                                (x_caja + 1, y0 + 1, z_caja - ef),
                                (ancho_caja - 2, largo_corr - 2, ef),
                                notas="Clavado por debajo de la caja (R-10)"))
            tapacanto_fino_mm += 2 * ((C - 4) + alto_frente)
            confirmats += 4 * confirmats_por_union(alto_caja)
            clavos += math.ceil(2 * ((ancho_caja - 2) + (largo_corr - 2)) / 150)
            tornillos_frente += 4
            eje_relativo = altura_corredera(alto_caja)
            eje = z_caja + eje_relativo
            perfs.append(Perforacion(
                "Lateral cajonera interno / externo", "cara interior", 0, eje, 3.0, "10 mm",
                f"eje corredera cajón {num}: centro a {eje_relativo} mm del canto inferior "
                f"de la caja y a {eje} mm del piso del mueble (P-02); "
                f"fijar con tornillos 4×16 en agujeros de la corredera"))

    else:
        piezas.append(Pieza("Lateral derecho (pata panel)", prof_panel, alto_apoyo, e, mat,
                            (A - e, RETRANQUEO_FRONTAL, 0), (e, prof_panel, alto_apoyo),
                            cantos="canto frontal visible"))
        tapacanto_fino_mm += alto_apoyo
        regatones += 2
        escuadras_mm += prof_panel

    # ------------------------------------------------- Viga trasera (R-13)
    x_der_interior = (A - caj["ancho"]) if con_cajonera else (A - e)
    vano = x_der_interior - x_izq_interior
    if vano > VANO_MAXIMO_SIN_VIGA:
        y_viga = P - RETRANQUEO_FRONTAL - e
        piezas.append(Pieza("Viga trasera", vano, 300, e, mat,
                            (x_izq_interior, y_viga, alto_apoyo - 300),
                            (vano, e, 300),
                            notas="De canto, unida a ambos apoyos y a la tapa (R-13)"))
        confirmats += 2 * confirmats_por_union(300)
        escuadras_mm += vano
        avisos.append(
            f"Se agregó viga trasera de {vano} × 300 mm: el vano libre supera los "
            f"{VANO_MAXIMO_SIN_VIGA} mm (regla R-13) y sin ella el mueble cimbra."
        )

    # ------------------------------------------------- Pasacables (R-16)
    pas = receta["pasacables"]
    if pas["cantidad"] > 0:
        zona_ini, zona_fin = x_izq_interior, x_der_interior
        paso = (zona_fin - zona_ini) // (pas["cantidad"] + 1)
        for k in range(pas["cantidad"]):
            cx = zona_ini + paso * (k + 1)
            perfs.append(Perforacion(
                "Tapa" if receta["tapa"]["tipo"] != "doble_18" else "Tapa (ambas capas)",
                "cara superior", cx, P - 60, pas["diametro"], "pasante",
                f"pasacables {k + 1}: broca copa Ø{pas['diametro']} a 60 mm del borde "
                "trasero (R-16); colocar grommet (H-06)"))

    # ------------------------------------------------- Espejar si cajonera izquierda
    if caj["posicion"] == "izquierda":
        for p in piezas:
            x, y, z = p.pos
            dx, dy, dz = p.dim
            p.pos = (A - x - dx, y, z)
        avisos.append("Mueble espejado: cajonera a la izquierda, soporte CPU a la derecha.")

    # ------------------------------------------------- Retorno en L (R-31)
    # Módulo autoportante: su tapa (doble si el vano lo exige, R-04), sus DOS patas
    # (esquina y extremo) y su viga si supera 1200 (R-13). La unión al escritorio
    # (escuadras + tornillos) rigidiza pero no carga peso: la esquina nunca queda
    # en el aire, y para mudanzas el retorno se separa y viaja aparte (R-26).
    forma = receta["forma"]
    if forma["tipo"] == "L":
        largo_ret = forma["largo_retorno"]
        prof_ret = forma["profundidad_retorno"]
        lado_der = forma["lado"] == "derecha"
        x_ret = (A - prof_ret) if lado_der else 0  # franja x que ocupa el retorno
        y_fin = 0                                   # se une al frente del escritorio
        y_ini = -largo_ret                          # y crece hacia el usuario en negativo

        vano_ret = largo_ret - 100 - e              # entre pata esquina y pata extremo
        tapa_ret_doble = vano_ret > 800             # R-04 aplicada al retorno
        t_ret = 36 if tapa_ret_doble else 18
        alto_apoyo_ret = H - t_ret

        if tapa_ret_doble:
            piezas.append(Pieza("Tapa retorno capa inferior (oculta)", largo_ret, prof_ret, 18,
                                mat_crudo, (x_ret, y_ini, H - 36), (prof_ret, largo_ret, 18),
                                notas="Aglomerado crudo: va escondida abajo (R-04 en el retorno)"))
            piezas.append(Pieza("Tapa retorno capa superior (visible)", largo_ret, prof_ret, 18,
                                mat, (x_ret, y_ini, H - 18), (prof_ret, largo_ret, 18),
                                cantos="3 cantos visibles (banda de 2 mm; el de la unión no se ve)"))
            tornillos_frente += math.ceil(largo_ret / 300) * math.ceil(prof_ret / 300)
        else:
            piezas.append(Pieza("Tapa retorno", largo_ret, prof_ret, 18, mat,
                                (x_ret, y_ini, H - 18), (prof_ret, largo_ret, 18),
                                cantos="3 cantos visibles (banda de 2 mm; el de la unión no se ve)"))
        tapacanto_grueso_mm += 2 * largo_ret + prof_ret

        # Patas del retorno: paneles perpendiculares al ala, retranqueados 50 del lado abierto
        x_pata = (x_ret + RETRANQUEO_FRONTAL) if lado_der else x_ret
        prof_pata_ret = prof_ret - RETRANQUEO_FRONTAL
        piezas.append(Pieza("Pata retorno (esquina)", prof_pata_ret, alto_apoyo_ret, e, mat,
                            (x_pata, y_fin - 50 - e, 0), (prof_pata_ret, e, alto_apoyo_ret),
                            cantos="canto lateral visible",
                            notas="Sostiene la esquina de la L: sin ella la unión carga todo (R-31)"))
        piezas.append(Pieza("Pata retorno (extremo)", prof_pata_ret, alto_apoyo_ret, e, mat,
                            (x_pata, y_ini + 50, 0), (prof_pata_ret, e, alto_apoyo_ret),
                            cantos="canto lateral visible"))
        tapacanto_fino_mm += 2 * alto_apoyo_ret
        regatones += 4
        escuadras_mm += 2 * prof_pata_ret     # tapa retorno ↔ sus patas
        escuadras_mm += 900                   # unión retorno ↔ escritorio (3 escuadras, R-31)
        tornillos_frente += 6                 # tornillos 4×30 de la unión (R-31)

        if vano_ret > VANO_MAXIMO_SIN_VIGA:
            x_viga = (x_ret + prof_ret - e) if lado_der else x_ret
            piezas.append(Pieza("Viga retorno", vano_ret, 300, e, mat,
                                (x_viga, y_ini + 50 + e, alto_apoyo_ret - 300),
                                (e, vano_ret, 300),
                                notas="De canto por el lado de la pared, unida a ambas patas "
                                      "y a la tapa del retorno (R-13)"))
            confirmats += 2 * confirmats_por_union(300)
            escuadras_mm += vano_ret

        avisos.append(
            f"Retorno en L (lado {forma['lado']}): {largo_ret}×{prof_ret} mm, "
            + ("tapa doble por el vano (R-04), " if tapa_ret_doble else "tapa simple, ")
            + ("con viga de canto (R-13), " if vano_ret > VANO_MAXIMO_SIN_VIGA else "")
            + "dos patas propias y unión con 3 escuadras + tornillos 4×30 al escritorio (R-31).")

    # ------------------------------------------------- Herrajes (07)
    herrajes.append(herraje_union(tipo_union, confirmats))
    herrajes.append(Herraje("H-04", "Tornillo aglomerado 4×30",
                            tornillos_frente, "unidades",
                            "fijar frentes de cajón desde adentro y laminar tapa doble"))
    if con_cajonera:
        herrajes.append(corredera_calidad(nivel, largo_corr, caj["cantidad_cajones"]))
    if pas["cantidad"] > 0:
        herrajes.append(Herraje("H-06", f"Grommet pasacables Ø{pas['diametro']}",
                                pas["cantidad"], "unidades",
                                "terminación de las perforaciones de la tapa (R-16)"))
    herrajes.append(Herraje("H-07", "Clavos 1½\" (o tornillo 3×16)",
                            clavos, "unidades", "fijar fondos de 3 mm (R-10)"))
    herrajes.append(Herraje("H-08", "Tapacanto PVC 22×0,45 mm",
                            round(tapacanto_fino_mm * 1.10 / 1000, 1), "metros",
                            "cantos visibles generales (R-11, incluye 10% de descarte)"))
    herrajes.append(Herraje("H-09", "Tapacanto PVC 22×2 mm",
                            round(tapacanto_grueso_mm * 1.10 / 1000, 1), "metros",
                            "cantos de la tapa, alto impacto (R-11)"))
    herrajes.append(Herraje("H-10", "Regatón nivelador atornillable",
                            regatones, "unidades",
                            "separar la melamina del piso y nivelar"))
    herrajes.append(Herraje("H-11", "Escuadra metálica 25 mm con tornillos 4×16",
                            math.ceil(escuadras_mm / 300), "unidades",
                            "fijar la tapa a los apoyos sin tornillos a la vista"))

    # ------------------------------------------------- Chequeo final R-15
    for p in piezas:
        if p.largo > 2560 or p.ancho > 1790:
            avisos.append(
                f"⚠ ATENCIÓN: la pieza '{p.nombre}' ({p.largo}×{p.ancho}) no sale de "
                "una placa de 2600×1830 con margen (R-15). Revisar la receta."
            )

    return mueble
