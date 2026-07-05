"""Catálogo de herrajes según el nivel de calidad/durabilidad (D-018).

Ron construye para uso propio y necesita que dure. El campo calidad.nivel
("economico" | "estandar" | "premium") elige qué corredera y qué bisagra
especifica el sistema, sin cambiar la geometría del despiece. Referencia:
07_HERRAJES_Y_TORNILLERIA.md (H-05, H-13, H-18, H-19) y 12_GUIA_DE_ARMADO.md.

La cantidad la calcula el despiece; acá solo se elige el ARTÍCULO (código,
nombre, texto). El precio se resuelve por código en generador_presupuesto.py.
"""

from .modelos import Herraje

NIVELES = ["economico", "estandar", "premium"]
DISTANCIA_CAZOLETA_CANTO = 21.5  # P-04: centro de cazoleta Ø35 a canto de puerta


def posiciones_bisagras(alto_hoja):
    """R-22: centros de bisagras medidos desde el borde superior de la puerta."""
    if alto_hoja <= 1500:
        cantidad = 2
    elif alto_hoja <= 2100:
        cantidad = 3
    else:
        cantidad = 4

    if alto_hoja <= 200:
        return [alto_hoja // 2]

    tramo = alto_hoja - 200
    divisor = cantidad - 1
    return [100 + (tramo * i + divisor // 2) // divisor for i in range(cantidad)]


def altura_corredera(alto_caja):
    """P-02: centro de la corredera medido desde el canto inferior de la caja."""
    return alto_caja // 2


def corredera(nivel, largo_mm, cantidad):
    """Herraje de corredera de cajón según el nivel. cantidad = pares."""
    if nivel == "economico":
        return Herraje(
            "H-05e", f"Corredera de rodillo {largo_mm} mm (par, media extensión)",
            cantidad, "pares",
            "económica; se desgasta y con el tiempo el cajón baila (ver durabilidad)")
    if nivel == "premium":
        return Herraje(
            "H-18", f"Corredera telescópica soft-close {largo_mm} mm (par, acero 40 kg)",
            cantidad, "pares",
            "extracción total + cierre suave; no se afloja ni baila, dura años (R-08)")
    return Herraje(
        "H-05", f"Corredera telescópica {largo_mm} mm (par, extracción total)",
        cantidad, "pares",
        "un par por cajón (R-08); incluye tornillos 4×16")


def bisagra(nivel, cantidad):
    """Herraje de bisagra de puerta según el nivel."""
    if nivel == "premium":
        return Herraje(
            "H-19", "Bisagra cazoleta 35 mm con cierre suave (soft-close)",
            cantidad, "unidades",
            "cierra sola sin golpe; no se descuelga con el uso (R-22)")
    return Herraje(
        "H-13", "Bisagra cazoleta 35 mm", cantidad, "unidades",
        "cantidad según el alto de la puerta (R-22)")


def union_sugerida(nivel, tipo_union_elegido):
    """El nivel premium sugiere unión excéntrica si el usuario dejó confirmat.
    Devuelve (tipo_union_final, aviso_o_None)."""
    if nivel == "premium" and tipo_union_elegido == "confirmat":
        return "excentrica", (
            "Nivel premium: se usan uniones excéntricas (cam-lock) en vez de tornillo "
            "confirmat, porque no se aflojan al mover el mueble (R-26/D-018)."
        )
    return tipo_union_elegido, None
