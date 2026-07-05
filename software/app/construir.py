"""Construye ESCRITORIO_GAMER.html (la app de doble clic) incrustando three.js.

Uso:  python software/app/construir.py

Toma software/app/app_fuente.html (la app con el marcador __THREE_JS__) y le
incrusta software/salidas/recursos/three.min.js, produciendo un único archivo
autocontenido en la raíz del repo. Así el usuario final solo necesita ese
archivo: doble clic y funciona sin internet ni instalaciones (Decisión D-010).
"""

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
FUENTE = RAIZ / "software" / "app" / "app_fuente.html"
THREE = RAIZ / "software" / "salidas" / "recursos" / "three.min.js"
SALIDA = RAIZ / "ESCRITORIO_GAMER.html"


def construir():
    src = FUENTE.read_text(encoding="utf-8")
    three = THREE.read_text(encoding="utf-8")
    if "__THREE_JS__" not in src:
        raise SystemExit("app_fuente.html no tiene el marcador __THREE_JS__")
    SALIDA.write_text(src.replace("__THREE_JS__", three), encoding="utf-8")
    print(f"✔ {SALIDA.name} generado ({SALIDA.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    construir()
