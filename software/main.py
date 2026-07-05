"""Punto de entrada del sistema. Orquesta el flujo completo:

    texto o receta -> validar -> despiece -> salidas (3D, cortes, compras)

Uso (detalles en el README):

  Con receta manual (no necesita IA):
      python main.py --receta recetas/ejemplos/escritorio_gamer_base.json

  Con IA (LM Studio abierto con el servidor activo, o proveedor de config.json):
      python main.py "quiero un escritorio gamer de 1,80 con 3 cajones"

  Ajustar un mueble ya generado:
      python main.py --receta proyectos/mi_escritorio/receta.json "hacelo más ancho"

  Carpeta de salida:  --salida proyectos/mi_escritorio
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from nucleo.validador import normalizar_y_validar, RecetaInvalida
from nucleo.despiece_escritorio import despiece_escritorio
from nucleo.despiece_ropero import despiece_ropero

DESPIECE_POR_TIPO = {
    "escritorio_gamer": despiece_escritorio,
    "ropero": despiece_ropero,
}
from salidas.generador_sketchup import generar_script_sketchup
from salidas.generador_visor_html import generar_visor_html
from salidas.generador_cortes import generar_lista_cortes, generar_perforaciones
from salidas.generador_presupuesto import generar_compras_y_presupuesto

RAIZ = Path(__file__).parent
REPO = RAIZ.parent


def nombre_carpeta(nombre):
    plano = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode()
    plano = re.sub(r"[^a-zA-Z0-9]+", "_", plano).strip("_").lower()
    return plano or "mueble"


def main():
    parser = argparse.ArgumentParser(
        description="Diseño automático de muebles de melamina",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    parser.add_argument("pedido", nargs="?", default=None,
                        help="pedido en lenguaje natural (usa la IA de config.json)")
    parser.add_argument("--receta", help="archivo JSON de receta (no requiere IA)")
    parser.add_argument("--salida", help="carpeta de salida (defecto: proyectos/<nombre>)")
    args = parser.parse_args()

    if not args.pedido and not args.receta:
        parser.error("indicá un pedido de texto o --receta archivo.json")

    # ------------------------------------------------ obtener la receta
    receta_anterior = None
    if args.receta:
        with open(args.receta, encoding="utf-8") as f:
            receta_anterior = json.load(f)

    if args.pedido:
        from ia.cliente_ia import pedir_receta_con_reintentos, ErrorIA
        with open(RAIZ / "config.json", encoding="utf-8") as f:
            config = json.load(f)
        print(f"→ Consultando IA ({config.get('proveedor')})...")
        try:
            receta, avisos = pedir_receta_con_reintentos(
                config, args.pedido, normalizar_y_validar, receta_anterior)
        except ErrorIA as e:
            print(f"\n✖ {e}", file=sys.stderr)
            return 1
    else:
        try:
            receta, avisos = normalizar_y_validar(receta_anterior)
        except RecetaInvalida as e:
            print("\n✖ La receta tiene errores:\n" + str(e), file=sys.stderr)
            return 1

    # ------------------------------------------------ despiece
    mueble = DESPIECE_POR_TIPO[receta["tipo_mueble"]](receta)
    avisos = avisos + mueble.avisos

    # ------------------------------------------------ salidas
    salida = Path(args.salida) if args.salida else \
        REPO / "proyectos" / nombre_carpeta(mueble.nombre)
    salida.mkdir(parents=True, exist_ok=True)

    with open(salida / "receta.json", "w", encoding="utf-8") as f:
        json.dump(receta, f, indent=2, ensure_ascii=False)

    generar_script_sketchup(mueble, salida / "mueble_sketchup.rb")
    generar_visor_html(mueble, salida / "visor_3d.html")
    generar_lista_cortes(mueble, salida / "lista_cortes.csv")
    generar_perforaciones(mueble, salida / "perforaciones.md")
    with open(RAIZ / "nucleo" / "precios.json", encoding="utf-8") as f:
        precios = json.load(f)
    generar_compras_y_presupuesto(
        mueble, precios, salida / "compras.md", salida / "presupuesto.md")

    # ------------------------------------------------ resumen
    print(f"\n✔ {mueble.nombre} — {mueble.dimensiones_texto()}")
    print(f"  {len(mueble.piezas)} piezas · {len(mueble.herrajes)} tipos de herraje")
    if avisos:
        print("\nAvisos:")
        for a in avisos:
            print(f"  • {a}")
    print(f"\nArchivos generados en {salida}/:")
    print("  visor_3d.html       → doble clic: ver el mueble en 3D (gratis, sin instalar nada)")
    print("  mueble_sketchup.rb  → cargar en SketchUp (consola Ruby) y usar OpenCutList")
    print("  lista_cortes.csv    → llevar a la tienda que corta placas")
    print("  perforaciones.md    → dónde va cada tornillo y perforación")
    print("  compras.md          → qué comprar")
    print("  presupuesto.md      → costo estimado (editá software/nucleo/precios.json)")
    print("  receta.json         → la receta (para ajustar: main.py --receta ... \"cambio\")")
    return 0


if __name__ == "__main__":
    sys.exit(main())
