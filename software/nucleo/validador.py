"""Dispatcher de validación por tipo de mueble.

Frontera de módulo (02_ARQUITECTURA.md): rechaza recetas imposibles o
peligrosas con mensajes claros en español citando reglas R-xx / M-xx.
NUNCA corrige valores en silencio: junta TODOS los errores y los reporta.

Cada tipo de mueble tiene su propio archivo de reglas (validador_<tipo>.py,
D-011) con sus DEFECTOS/LIMITES/OPCIONES/normalizar/validar. Este archivo
solo valida lo común (version, tipo_mueble conocido) y despacha al módulo
correcto. Fuente de las reglas comunes: 05_REGLAS_DE_CARPINTERIA.md.
"""

from . import validador_escritorio, validador_ropero

VERSION_SOPORTADA = "1.0"

MODULOS_POR_TIPO = {
    "escritorio_gamer": validador_escritorio,
    "ropero": validador_ropero,
}
TIPOS_SOPORTADOS = list(MODULOS_POR_TIPO.keys())


class RecetaInvalida(Exception):
    """Se lanza con la lista completa de errores de una receta."""

    def __init__(self, errores):
        self.errores = errores
        super().__init__("\n".join(f"- {e}" for e in errores))


def normalizar_y_validar(receta_cruda):
    """Punto de entrada estándar: devuelve (receta_completa, avisos).

    Valida lo común (version, tipo_mueble) y despacha la normalización y
    validación específicas al módulo del tipo de mueble correspondiente.
    """
    errores = []
    version = receta_cruda.get("version")
    if version != VERSION_SOPORTADA:
        errores.append(f'version = "{version}" no soportada; usá "{VERSION_SOPORTADA}".')

    tipo = receta_cruda.get("tipo_mueble")
    if tipo not in MODULOS_POR_TIPO:
        errores.append(
            f'tipo_mueble = "{tipo}" desconocido. '
            f"Disponibles: {', '.join(TIPOS_SOPORTADOS)}."
        )
    if errores:
        raise RecetaInvalida(errores)

    modulo = MODULOS_POR_TIPO[tipo]
    receta, avisos = modulo.normalizar(receta_cruda)
    avisos = avisos + modulo.validar(receta)
    return receta, avisos
