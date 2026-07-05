# 05 — REGLAS DE CARPINTERÍA EN MELAMINA

## Objetivo de este documento

Reunir las reglas físicas y de oficio que el software aplica. Cada regla tiene un código
**R-xx** que el código fuente y los mensajes de error citan textualmente. Si una regla
cambia aquí, debe cambiar en `validador.py` / `despiece_*.py` **en el mismo commit**.

> Convención global: **todas las medidas en milímetros**. Espesor de estructura `e`
> (por defecto 18 mm).

## Material base

- **R-01 — Espesores estándar.** Estructura y frentes: melamina de **18 mm** (15 mm
  aceptable en interiores de cajón). Fondos y contrafondos: fibrofácil/MDF de **3 mm**
  (5,5 mm para muebles grandes). Tapas de escritorio: 25 mm o **doble placa de 18**
  encolada/atornillada (36 mm final, más económica y más rígida que 25).
- **R-02 — Descuento de espesores.** Toda medida interior = medida exterior − 2×e.
  Ejemplo: cajonera de 400 de ancho exterior → interior 400 − 36 = **364 mm**.
- **R-03 — La melamina no se pega, se atornilla.** Las uniones estructurales llevan
  tornillo + tarugo o confirmat (ver `07_HERRAJES_Y_TORNILLERIA.md`). La cola vinílica solo
  acompaña tarugos.

## Rigidez y pandeo

- **R-04 — Vano máximo sin apoyo.** Un tablero de 18 mm cargado horizontalmente (estante,
  tapa) no debe superar **800 mm de vano libre**. Soluciones en orden de preferencia:
  agregar apoyo vertical (parante/cajonera), viga trasera (R-13), o duplicar espesor
  (`doble_18`). Para tapas de escritorio gamer (monitores = peso concentrado), el defecto es
  `doble_18` en cuanto el vano supera 800.
- **R-13 — Viga/faldón trasero.** Si el vano libre entre apoyos supera **1200 mm**, además
  de la tapa reforzada va una **viga trasera de 18 mm × 300 mm de alto**, de canto, unida a
  ambos apoyos y a la tapa. Aporta rigidez lateral (evita el "paralelogramo").

## Cajones (sistema con correderas telescópicas)

- **R-05 — Descuento de correderas.** Ancho exterior de la caja del cajón = ancho interior
  del hueco − **26 mm** (13 mm por lado para corredera telescópica estándar de 45 mm).
  Consecuencia: hueco interior mínimo útil ≈ 264 + 26 → `cajonera.ancho` mínimo 300.
- **R-06 — Reparto de frentes.** Los frentes de cajón se reparten el alto útil de la
  cajonera con **luz de 3 mm entre frentes** y 3 mm en el borde superior. Alto de cada
  frente = (alto útil − 3×cantidad) / cantidad, redondeado a entero.
- **R-07 — Altos de frente razonables.** Frente mínimo **120 mm** (menos no deja cajón
  usable), máximo recomendado **350 mm** (más profundo se vuelve un pozo; para gamer,
  cajones espaciosos = frentes de 200–300 mm).
- **R-08 — Largo de corredera.** Corredera comercial más larga que quepa:
  largo ≤ profundidad interior de la cajonera − 20 mm, en medidas comerciales
  **250 / 300 / 350 / 400 / 450 / 500 / 550 / 600**. La caja del cajón mide de profundidad
  lo mismo que la corredera elegida.
- **R-12 — Anatomía de la caja de cajón.** 2 laterales (profundidad × alto de caja),
  frente y contrafrente interiores (van ENTRE los laterales: ancho caja − 2×e), fondo de
  3 mm aplicado por debajo (ancho caja − 2 mm × prof caja − 2 mm). Alto de caja = alto de
  frente − 30 mm (deja luz arriba y abajo). El frente aplicado (el que se ve) se atornilla
  desde adentro con tornillos 4×30.

## Uniones y tornillería (detalle en 07)

- **R-09 — Uniones de caja.** Tornillo confirmat 7×50 (o tornillo aglomerado 4×50 con
  tarugo 8 mm + cola): **2 por unión hasta 300 mm de ancho de pieza, luego 1 cada
  150–200 mm**. Pre-perforado obligatorio (broca 4,5 en la pieza pasante, 3 en el canto que
  recibe) para no reventar el aglomerado.
- **R-10 — Fondos.** El fondo de 3 mm va clavado/atornillado por detrás, 2 mm más chico
  que el exterior por lado. En cajones puede ir ranurado si hay fresadora (fase futura).
- **R-26 — Movilidad después de armado.** Ningún mueble de melamina armado con tornillos
  rectos es rígido: moverlo de un tirón concentra la torsión en los tornillos y agranda el
  agujero hasta que giran en el aire. Ver el detalle completo y las mitigaciones (viga
  trasera, herraje excéntrico H-17) en `07_HERRAJES_Y_TORNILLERIA.md`.

## Terminación

- **R-11 — Tapacanto.** Solo se cubren los **cantos visibles**: frente de laterales,
  estantes, tapa, frentes de cajón (los 4 cantos). PVC de 0,45 mm para uso normal; 2 mm en
  la tapa (bordes que reciben golpes). El generador de compras calcula metros lineales de
  cada tipo + 10 % de descarte.

## Reglas específicas del escritorio gamer

- **R-14 — Apoyos del escritorio.** El escritorio del prototipo se apoya en: lateral
  izquierdo de 18 mm (pata-panel) + la cajonera (que es estructural). Si
  `cajonera.posicion = "ninguna"`, ambos apoyos son laterales-panel.
- **R-15 — Toda pieza debe caber en placa.** Placa comercial de referencia:
  **2600 × 1830 mm** (ver `06_MEDIDAS_ESTANDAR.md`; también existe 2440×1220). El validador
  rechaza cualquier pieza que exceda 2560 × 1790 (margen de 20 mm por lado para escuadrado).
- **R-16 — Pasacables.** Perforaciones circulares en la tapa, Ø 60 mm (grommet comercial),
  centradas a **60 mm del borde trasero**, distribuidas uniformemente en el ancho útil.
  Nunca sobre la cajonera (ahí abajo no pasan cables).
- **R-17 — Soporte de CPU.** Bandeja lateral elevada **100 mm del piso** (limpieza y
  ventilación), ancho interior mínimo 200 mm (gabinete estándar ≤ 230), profundidad = la
  del escritorio − retranqueo. Formada por un parante interior + piso, del lado opuesto o
  contiguo a la cajonera según `posicion`.

## Buenas y malas prácticas de oficio (para la IA acompañante)

| ✅ | ❌ |
|---|---|
| Pre-perforar SIEMPRE antes de atornillar melamina | Atornillar directo "porque es rápido" → canto reventado |
| Cortar con la cara buena hacia arriba en sierra de mesa (o abajo en circular de mano) | Ignorar el lado del astillado |
| Verificar escuadra midiendo diagonales del mueble armado | Confiar solo en la escuadra de mano |
| Pedir los cortes a la tienda con la lista del sistema (cortes de fábrica = precisos) | Cortar a pulso placas enteras sin herramienta adecuada |

## Casos reales de error que estas reglas previenen

1. *Tapa simple de 18 en escritorio de 1600:* a los 6 meses queda "panzona" bajo los
   monitores → lo previene R-04.
2. *Cajón calculado sin descuento de correderas:* el cajón no entra o entra forzado y las
   correderas no corren → R-05.
3. *4 cajones en cajonera baja:* frentes de 90 mm donde no entra ni un cargador → R-07.
4. *Pieza de 2700 mm en el despiece:* no existe placa de la que sacarla → R-15.

## Documentos relacionados

- Medidas por defecto y ergonomía: `06_MEDIDAS_ESTANDAR.md`
- Qué herraje/tornillo exacto comprar: `07_HERRAJES_Y_TORNILLERIA.md`
- Cómo estas reglas llegan al código: `02_ARQUITECTURA.md` (validador y motor)
