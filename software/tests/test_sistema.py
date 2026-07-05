"""Pruebas del núcleo. Correr con:  python tests/test_sistema.py
(desde la carpeta software/). No requiere instalar nada.
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from nucleo.validador import (normalizar_y_validar, RecetaInvalida,
                              espesor_tapa, vano_libre)
from nucleo.despiece_escritorio import (despiece_escritorio,
                                        confirmats_por_union, elegir_corredera)

OK = 0
FALLAS = []


def prueba(nombre, condicion, detalle=""):
    global OK
    if condicion:
        OK += 1
    else:
        FALLAS.append(f"{nombre} {detalle}")
        print(f"  ✖ {nombre} {detalle}")


RECETA_BASE = {
    "version": "1.0",
    "tipo_mueble": "escritorio_gamer",
    "nombre": "Test",
    "dimensiones": {"ancho": 1600, "profundidad": 700, "alto": 750},
    "material": {"color": "Negro"},
    "cajonera": {"posicion": "derecha", "ancho": 400, "cantidad_cajones": 3},
    "soporte_cpu": {"incluir": True, "ancho": 250},
    "pasacables": {"cantidad": 2, "diametro": 60},
}


def receta(**cambios):
    r = json.loads(json.dumps(RECETA_BASE))
    for clave, valor in cambios.items():
        if isinstance(valor, dict) and clave in r:
            r[clave].update(valor)
        else:
            r[clave] = valor
    return r


# ---------------------------------------------------------------- normalizar
print("Normalización y defectos…")
r, avisos = normalizar_y_validar({"version": "1.0", "tipo_mueble": "escritorio_gamer"})
prueba("receta mínima válida", r["dimensiones"]["ancho"] == 1600)
prueba("defecto tapa doble_18 con vano grande (R-04)", r["tapa"]["tipo"] == "doble_18")
prueba("aviso de tapa reforzada emitido", any("R-04" in a for a in avisos))
prueba("espesor doble_18 = 36", espesor_tapa(r) == 36)

# ---------------------------------------------------------------- validaciones
print("Validaciones que deben rechazar…")
casos_invalidos = [
    ("ancho fuera de rango", receta(dimensiones={"ancho": 3000}), "R-15"),
    ("cajonera angosta", receta(cajonera={"ancho": 250}), "R-05"),
    ("profundidad fuera de rango", receta(dimensiones={"profundidad": 450}), "M-02"),
    ("tapa simple con vano grande", receta(tapa={"tipo": "simple_18"}), "R-04"),
    ("campo inventado", receta(puertas=True), "Campo desconocido"),
    ("sin lugar para piernas",
     receta(dimensiones={"ancho": 1200}, cajonera={"ancho": 500}), "M-04"),
    ("version desconocida", receta(version="9.9"), "version"),
]
for nombre, r_mala, texto_esperado in casos_invalidos:
    try:
        normalizar_y_validar(r_mala)
        prueba(f"rechaza: {nombre}", False, "(no lanzó error)")
    except RecetaInvalida as e:
        prueba(f"rechaza: {nombre}", texto_esperado in str(e),
               f"(error no menciona {texto_esperado}: {e})")

# ---------------------------------------------------------------- aritmética
print("Aritmética del despiece (verificada a mano)…")
r, _ = normalizar_y_validar(RECETA_BASE)
m = despiece_escritorio(r)
piezas = {p.nombre: p for p in m.piezas}

# Tapa doble: 2 capas de 1600×700×18
prueba("tapa en dos capas", "Tapa capa superior" in piezas and "Tapa capa inferior" in piezas)
prueba("medida tapa", piezas["Tapa capa superior"].largo == 1600
       and piezas["Tapa capa superior"].ancho == 700)

# Laterales: alto = 750 − 36 = 714; profundidad = 700 − 50 = 650
# (Pieza ordena corte como largo ≥ ancho: largo=714, ancho=650)
lat = piezas["Lateral izquierdo (pata panel)"]
prueba("alto de apoyo 714 (750−36)", lat.largo == 714, f"(dio {lat.largo})")
prueba("prof panel 650 (700−50)", lat.ancho == 650, f"(dio {lat.ancho})")

# R-07 aviso: con 1 solo cajón el frente pasa de 350 → aviso, no error
_, avisos_1caj = normalizar_y_validar(receta(cajonera={"cantidad_cajones": 1}))
prueba("aviso R-07 con 1 cajón gigante", any("R-07" in a for a in avisos_1caj))

# Piso cajonera: interior = 400 − 2×18 = 364 (R-02)
prueba("interior cajonera 364 (R-02)", piezas["Piso cajonera"].ancho == 364,
       f"(dio {piezas['Piso cajonera'].ancho})")

# Cajones: alto útil = 714 − 18 = 696 → frente = (696 − 9) / 3 = 229 (R-06)
f1 = piezas["Frente cajón 1"]
prueba("frente cajón 229 (R-06)", f1.ancho == 229, f"(dio {f1.ancho})")
prueba("ancho frente 396 (400−4)", f1.largo == 396, f"(dio {f1.largo})")

# Caja: ancho = 364 − 26 = 338 (R-05); corredera para PC=600 → 550 (R-08)
prueba("corredera 550 para prof.interior 600 (R-08)", elegir_corredera(600) == 550)
lat_caja = piezas["Lateral caja cajón 1 (izq)"]
prueba("prof caja = corredera 550", lat_caja.largo == 550, f"(dio {lat_caja.largo})")
prueba("alto caja 199 (229−30, R-12)", lat_caja.ancho == 199, f"(dio {lat_caja.ancho})")
fi = piezas["Frente interno cajón 1"]
prueba("frente interno 302 (338−36)", fi.largo == 302, f"(dio {fi.largo})")

# Confirmats por unión (R-09)
prueba("R-09: unión 300 → 2", confirmats_por_union(300) == 2)
prueba("R-09: unión 600 → 4", confirmats_por_union(600) == 4)

# Sin viga con 1600 (vano 914 < 1200); con viga a 2000
prueba("sin viga a 1600", "Viga trasera" not in piezas)
r2, _ = normalizar_y_validar(receta(dimensiones={"ancho": 2000}))
m2 = despiece_escritorio(r2)
prueba("viga a 2000 (R-13)", any(p.nombre == "Viga trasera" for p in m2.piezas))
prueba("vano libre coherente", vano_libre(r2) == 2000 - 400 - (18 + 250 + 18))

# Espejo con cajonera izquierda: mismas piezas, posiciones espejadas
r3, _ = normalizar_y_validar(receta(cajonera={"posicion": "izquierda"}))
m3 = despiece_escritorio(r3)
prueba("espejo conserva cantidad de piezas", len(m3.piezas) == len(m.piezas))
lat3 = {p.nombre: p for p in m3.piezas}["Lateral izquierdo (pata panel)"]
prueba("espejo mueve el lateral", lat3.pos[0] == 1600 - 18, f"(dio {lat3.pos[0]})")

# Sin cajonera ni CPU: dos patas panel
r4, _ = normalizar_y_validar(receta(cajonera={"posicion": "ninguna"},
                                    soporte_cpu={"incluir": False}))
m4 = despiece_escritorio(r4)
nombres4 = [p.nombre for p in m4.piezas]
prueba("variante sin cajonera tiene 2 patas panel",
       "Lateral derecho (pata panel)" in nombres4)
prueba("variante sin cajonera no tiene cajones",
       not any("cajón" in n for n in nombres4))

# ---------------------------------------------------------------- salidas
print("Generadores de salida…")
from salidas.generador_sketchup import generar_script_sketchup
from salidas.generador_visor_html import generar_visor_html
from salidas.generador_cortes import generar_lista_cortes, generar_perforaciones
from salidas.generador_presupuesto import generar_compras_y_presupuesto

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    generar_script_sketchup(m, tmp / "m.rb")
    rb = (tmp / "m.rb").read_text(encoding="utf-8")
    prueba("rb: define todas las piezas", rb.count("nombre:") == len(m.piezas))
    prueba("rb: usa milímetros", ".mm" in rb and "start_operation" in rb)
    prueba("rb: interpolación ruby intacta", "#{PIEZAS.length}" in rb)

    generar_visor_html(m, tmp / "v.html")
    html = (tmp / "v.html").read_text(encoding="utf-8")
    prueba("html: contiene datos del mueble", "Piso cajonera" in html
           and '"piezas"' in html)

    generar_lista_cortes(m, tmp / "c.csv")
    csv_texto = (tmp / "c.csv").read_text(encoding="utf-8-sig")
    prueba("csv: cabecera y filas", "Largo (mm)" in csv_texto
           and "Piso cajonera" in csv_texto)

    generar_perforaciones(m, tmp / "p.md")
    prueba("perforaciones: incluye pasacables",
           "pasacables" in (tmp / "p.md").read_text(encoding="utf-8"))

    with open(Path(__file__).parent.parent / "nucleo" / "precios.json",
              encoding="utf-8") as f:
        precios = json.load(f)
    generar_compras_y_presupuesto(m, precios, tmp / "co.md", tmp / "pr.md")
    prueba("presupuesto: tiene total",
           "TOTAL estimado" in (tmp / "pr.md").read_text(encoding="utf-8"))

# ---------------------------------------------------------------- extractor IA
print("Extractor de JSON de la IA…")
from ia.cliente_ia import extraer_json, ErrorIA
prueba("extrae JSON limpio", extraer_json('{"a": 1}') == {"a": 1})
prueba("extrae JSON con ``` y charla",
       extraer_json('Claro! ```json\n{"a": 1}\n``` listo') == {"a": 1})
try:
    extraer_json("no hay json acá")
    prueba("rechaza texto sin JSON", False)
except ErrorIA:
    prueba("rechaza texto sin JSON", True)

# ---------------------------------------------------------------- resultado
print()
if FALLAS:
    print(f"✖ {len(FALLAS)} pruebas fallaron de {OK + len(FALLAS)}.")
    sys.exit(1)
print(f"✔ {OK} pruebas pasaron.")
