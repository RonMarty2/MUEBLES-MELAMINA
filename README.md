# MUEBLES-MELAMINA — Diseño automático de muebles de melamina

Le pedís un mueble en palabras → el sistema te da: **el mueble en 3D, dónde va
cada tornillo, la lista de cortes, qué comprar y cuánto cuesta.**

```
"quiero un escritorio gamer de 1,60 con 3 cajones"
        ↓
  visor_3d.html      ← lo ves en 3D en tu navegador (gratis, doble clic)
  mueble_sketchup.rb ← lo dibuja en SketchUp (opcional) + OpenCutList
  lista_cortes.csv   ← la llevás a la tienda que corta placas
  perforaciones.md   ← dónde va cada tornillo, tarugo y broca
  compras.md         ← qué comprar exactamente (placas, herrajes, tapacanto)
  presupuesto.md     ← costo estimado con TUS precios
```

**Cómo funciona por dentro:** la IA (local con LM Studio, o ChatGPT/Claude si
algún día pagás una) solo escribe una "receta" JSON con las medidas. Un motor
en Python —matemática pura, sin IA— valida esa receta con reglas reales de
carpintería y genera todo lo demás. Por eso podés cambiar de IA cuando quieras
(o no usar ninguna) sin que nada se rompa. Todo el conocimiento del proyecto
vive en [`AI_OPERATING_SYSTEM/`](AI_OPERATING_SYSTEM/00_INDICE.md).

---

## Instalación (una sola vez)

1. **Python 3.10 o más nuevo** — [python.org/downloads](https://www.python.org/downloads/).
   En Windows, al instalar marcá ✅ "Add Python to PATH".
2. Descargá este proyecto (botón verde **Code → Download ZIP** en GitHub, o `git clone`).
3. No hay nada más que instalar. Sin dependencias, sin cuentas, sin pagos.

## Uso básico (sin IA — funciona ya mismo)

Abrí una terminal en la carpeta `software/` y corré:

```
python main.py --receta recetas/ejemplos/escritorio_gamer_base.json
```

Los archivos aparecen en `proyectos/escritorio_gamer_demo/`. Abrí
`visor_3d.html` con doble clic: ahí está tu escritorio en 3D. Arrastrá para
girar, rueda para zoom, clic en una pieza de la lista para resaltarla
(doble clic en el fondo para des-resaltar).

Para cambiar el mueble, editá el archivo de receta (es texto simple: ancho,
profundidad, cajones…) y volvé a correr el comando. La especificación completa
de la receta está en
[`AI_OPERATING_SYSTEM/04_ESQUEMA_RECETA_JSON.md`](AI_OPERATING_SYSTEM/04_ESQUEMA_RECETA_JSON.md).

## Uso con IA local (LM Studio) — pedirlo en palabras

1. Abrí **LM Studio**, descargá/cargá un modelo de 7B o más (ej. Llama 3.1 8B
   Instruct o Qwen 2.5 7B Instruct).
2. Pestaña **Developer → Start Server** (queda en `http://localhost:1234`).
3. En la terminal:

```
python main.py "quiero un escritorio gamer de 1,80 negro con 3 cajones grandes"
```

Para ajustar un mueble ya generado:

```
python main.py --receta ../proyectos/escritorio_gamer_demo/receta.json "hacelo 20 cm más ancho y sacale el soporte de CPU"
```

¿Querés usar ChatGPT o Claude en vez de la IA local? Editá
`software/config.json` (proveedor, url y api_key). Nada más cambia.

## Ver el mueble en SketchUp + lista de cortes optimizada (opcional)

> ¿No querés pagar SketchUp? No hace falta: el `visor_3d.html` es gratis para
> siempre, y la `lista_cortes.csv` la optimiza la tienda que corta las placas.
> Si igual querés SketchUp: **SketchUp Make 2017** es gratis para uso personal.

1. Abrí SketchUp con plantilla en milímetros.
2. Menú **Ventana → Consola Ruby**.
3. Escribí (con TU ruta real):
   `load "C:/Users/Ron/MUEBLES-MELAMINA/proyectos/escritorio_gamer_demo/mueble_sketchup.rb"`
4. El mueble se dibuja solo, pieza por pieza, con nombres y materiales.
5. Instalá el plugin gratuito **OpenCutList** (Ventana → Extension Warehouse,
   buscá "OpenCutList"). Menú **Extensiones → OpenCutList → Cortes**: ahí tenés
   la lista de cortes y el diagrama de placas con el desperdicio optimizado.

## Poné TUS precios

Editá `software/nucleo/precios.json` con los precios de tu zona (placa,
confirmats, correderas, tapacanto…). El presupuesto se recalcula en la próxima
corrida. Los valores que vienen son de ejemplo.

## Estructura del proyecto

| Carpeta | Qué hay |
|---|---|
| `AI_OPERATING_SYSTEM/` | La memoria del proyecto: arquitectura, reglas de carpintería, medidas estándar, decisiones. **Empezá por `00_INDICE.md`** |
| `software/` | El programa (Python). `main.py` es el punto de entrada |
| `software/recetas/` | Esquema de la receta JSON y ejemplos |
| `proyectos/` | Acá caen los muebles generados (uno por carpeta) |

## Para desarrolladores / IAs que trabajen en este repo

- Leer `AI_OPERATING_SYSTEM/00_INDICE.md` ANTES de tocar nada.
- Correr las pruebas: `cd software && python tests/test_sistema.py`
- Toda decisión técnica se registra en `AI_OPERATING_SYSTEM/09_DECISIONES_TECNICAS.md`.
- Las reglas de carpintería (R-xx), medidas (M-xx) y herrajes (H-xx) citadas en
  el código están definidas en los documentos 05, 06 y 07.
