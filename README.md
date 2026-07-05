# MUEBLES-MELAMINA — Diseño automático de muebles de melamina

## Empezar en 30 segundos

**Descargá el archivo [`ESCRITORIO_GAMER.html`](ESCRITORIO_GAMER.html) y abrilo con doble
clic.** Eso es todo. No hay que instalar Python, ni Node, ni nada — es una sola página
que funciona en tu navegador (Chrome, Edge, Firefox), sin internet.

Adentro vas a ver: controles para configurar el escritorio (ancho, color, cajones,
soporte de CPU, pasacables…), el mueble en **3D en vivo** que se actualiza solo, y
pestañas con la **lista de cortes**, **lista de compras**, **presupuesto** y **dónde va
cada tornillo**. Botones para descargar la lista de cortes (CSV) y el script para
SketchUp cuando quieras construirlo de verdad.

---

## Cómo funciona por dentro (para quien tenga curiosidad)

La app no es un simulador: es el mismo motor de cálculo de carpintería que corre en
Python (`software/`), portado a JavaScript para que funcione sin instalar nada. Aplica
reglas reales — espesores de melamina, holguras de correderas, límites de pandeo — antes
de mostrarte el mueble. Si le pedís algo imposible de construir, te avisa por qué (con
la regla exacta) en vez de dibujarlo igual.

Todo el conocimiento de carpintería y las decisiones técnicas del proyecto viven en
[`AI_OPERATING_SYSTEM/`](AI_OPERATING_SYSTEM/00_INDICE.md).

## Pedirlo en palabras (opcional, con IA local gratis)

Si tenés **LM Studio** instalado:

1. Abrí LM Studio, cargá un modelo de 7B o más (ej. Llama 3.1 8B Instruct).
2. Pestaña **Developer → Start Server**, y en la configuración del servidor activá
   **CORS** (para que el navegador pueda hablarle).
3. En `ESCRITORIO_GAMER.html`, arriba a la izquierda, escribí tu pedido en la cajita
   ("hacelo de 1,80 con 2 cajones") y apretá **Pedir a la IA**.

Si no tenés LM Studio abierto, no pasa nada: usá los controles de la izquierda, hacen
exactamente lo mismo a mano.

## Construir el mueble de verdad

- **Lista de cortes:** botón **⬇ Cortes CSV** → llevás ese archivo a la tienda que corta
  melamina (se abre en Excel).
- **Ver en SketchUp (opcional):** botón **⬇ SketchUp** descarga un script `.rb`. En
  SketchUp: **Ventana → Consola Ruby** → escribís `load "ruta/al/archivo.rb"` → el mueble
  se dibuja solo. Instalá el plugin gratuito **OpenCutList** (Extension Warehouse) para
  el diagrama de cortes optimizado con el desperdicio calculado.
- **Tus precios:** pestaña **⚙️ Mis precios** dentro de la app — se guardan en tu
  navegador y el presupuesto se recalcula solo.
- **Guardar tu diseño:** botón **💾 Guardar** descarga un archivo `.json` chiquito con tu
  mueble; **📂 Abrir** lo vuelve a cargar otro día.

## Estructura del proyecto

| Archivo/Carpeta | Qué es |
|---|---|
| **`ESCRITORIO_GAMER.html`** | **La app. Doble clic y listo.** |
| `AI_OPERATING_SYSTEM/` | La memoria del proyecto: arquitectura, reglas de carpintería, medidas, decisiones. Empezá por `00_INDICE.md` |
| `proyectos/escritorio_gamer_demo/` | Un mueble de ejemplo ya generado, para ver el formato de las salidas |
| `software/` | El motor en Python (referencia técnica) + el código fuente de la app |

---

## Avanzado: el motor en Python (opcional, para desarrollo)

Esta sección es solo para quien quiera automatizar el sistema por línea de comandos
(por ejemplo, conectarlo a ChatGPT/Claude por API, o generar muebles en lote). Si solo
querés diseñar tu escritorio, no la necesitás — usá `ESCRITORIO_GAMER.html`.

```
cd software
python main.py --receta recetas/ejemplos/escritorio_gamer_base.json
```

Genera los mismos archivos (visor 3D, cortes, compras, presupuesto) en
`proyectos/<nombre>/`. Con IA por API: editá `software/config.json` (proveedor, url,
api_key) y corré `python main.py "tu pedido en palabras"`.

### Para desarrolladores / IAs que trabajen en este repo

- Leer `AI_OPERATING_SYSTEM/00_INDICE.md` ANTES de tocar nada.
- Hay **dos motores en paridad** (Decisión D-010): Python (`software/nucleo/`) y
  JavaScript (dentro de `ESCRITORIO_GAMER.html`, fuente en `software/app/app_fuente.html`).
  Si cambiás una fórmula, cambiala en los dos en el mismo commit.
- Pruebas del motor Python: `cd software && python tests/test_sistema.py`
- Pruebas de paridad del motor JS: abrir `ESCRITORIO_GAMER.html?test=1` en un navegador.
- Para reconstruir la app tras editar `software/app/app_fuente.html`:
  `python software/app/construir.py` (regenera `ESCRITORIO_GAMER.html` incrustando
  `software/salidas/recursos/three.min.js`). **Nunca editar `ESCRITORIO_GAMER.html`
  directamente** — se pierde en el próximo build.
- Toda decisión técnica se registra en `AI_OPERATING_SYSTEM/09_DECISIONES_TECNICAS.md`.
- Las reglas de carpintería (R-xx), medidas (M-xx) y herrajes (H-xx) citadas en el código
  están definidas en los documentos 05, 06 y 07.
