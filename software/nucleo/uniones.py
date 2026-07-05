"""Utilidad compartida: elegir el herraje de unión estructural (R-26).

Both despiece_escritorio.py y despiece_ropero.py usan esto para no duplicar
la decisión confirmat vs. excéntrico. Ver 07_HERRAJES_Y_TORNILLERIA.md.
"""

from .modelos import Herraje


def herraje_union(tipo_union, cantidad):
    """Devuelve el Herraje correspondiente a la cantidad de uniones calculada
    (misma cantidad, cambia el artículo según R-26/H-01 vs H-17)."""
    if tipo_union == "excentrica":
        return Herraje("H-17", "Herraje excéntrico (cam-lock) + espiga Ø8", cantidad,
                       "unidades",
                       "uniones estructurales, no se afloja al mover el mueble (R-26)")
    return Herraje("H-01", "Confirmat 7×50", cantidad, "unidades",
                   "uniones estructurales (R-09)")
