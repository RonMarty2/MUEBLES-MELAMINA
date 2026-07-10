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

## Carga y pandeo de superficies horizontales (R-04 / R-27)

Orientación práctica (no fórmula de ingeniería) para melamina de **18 mm** apoyada solo en
sus dos extremos, con carga distribuida — la base de R-04 (tapa) y R-27 (estantes ropero):

| Vano libre | Comportamiento cargado | Qué hace el motor |
|---|---|---|
| ≤ 600 mm | Carga alta sin problema (libros, cajas) | Nada extra |
| 600–800 mm | Carga media (~25 kg distribuidos); no apilar peso al medio | Aviso |
| > 800 mm | Se pandea seguro con el tiempo (la melamina "toma memoria") | Refuerzo automático: tapa doble (R-04), viga trasera (R-13), refuerzo de canto / apoyo central (R-27), zócalo doble (R-28) |

Principio: la melamina plana es débil; **de canto es rígida**. Todos los refuerzos del
motor son la misma idea: una tira de canto atornillada bajo la superficie que trabaja.

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
- **R-31 — Escritorio en L (retorno).** El ala de la L es un **módulo autoportante**: su
  propia tapa (doble si el vano entre patas supera 800, R-04; con viga de canto si supera
  1200, R-13) y **dos patas panel propias** — una en la esquina y otra en el extremo. La
  unión al escritorio principal (3 escuadras repartidas + tornillos 4×30, tapas a ras,
  prensar y nivelar antes de apretar) **rigidiza pero no carga peso**: la esquina nunca
  queda en el aire. Para mudanzas se sacan las escuadras de la unión y el retorno viaja
  aparte (R-26). Rangos: largo 600–1600 (M-26), profundidad 400–700 (M-27). Las formas en
  C y U son dos retornos con esta misma regla (pendiente en la hoja de ruta).

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

## Exportación de planos técnicos (nueva, D-038)

- **EXP-001 — Planos de perforación imprimibles.** El sistema puede generar, por tipo de
  pieza (agrupadas como en la pestaña Cortes), un plano 2D imprimible con: el contorno a
  escala con las cotas de largo × ancho, cada perforación real marcada con su distancia a
  los bordes, y una leyenda de diámetro/tipo de broca. Los puntos de perforación se calculan
  con la MISMA geometría que ya usa la vista 3D de armado (pasante/receptor de R-09/P-01),
  filtrados para que solo se dibuje una unión si las dos piezas aparecen juntas en algún
  paso real de armado — así no se inventan tornillos por simple cercanía geométrica (ej. la
  holgura de apertura de una puerta con bisagra, R-22). Todo dibujo lleva el aviso de que
  las cotas en NÚMEROS son la referencia real, no medir con regla sobre la pantalla/impresión.
  Implementado 100% en `app_fuente.html` (Vanilla JS + SVG), sin librerías externas, para
  mantener el archivo único de distribución.
- **UX-001 — Aislar y rayos-X (D-039).** Modo OPCIONAL (botón "🔍 Aislar y rayos-X" dentro de
  Armado): oculta por completo las piezas que no participan del paso activo — incluso las
  que ya estaban armadas — y deja las del paso semitransparentes para ver el interior
  (**VIS-002**). Es opt-in a propósito: por defecto sigue rigiendo el modo acumulativo (D-030)
  donde lo ya armado queda sólido, porque ESO es lo que el usuario pidió ("ir viendo como
  empieza con una tabla y terminamos en el mueble"); ocultarlo por defecto se lo hubiera
  sacado.
- **EST-002 — Guías de perforación en 3D.** Con el modo UX-001 activo, cada unión real del
  paso (misma detección pasante/receptor de R-09/D-033) dibuja un cilindro rojo
  semitransparente (`THREE.CylinderGeometry`, `0xff0000`, opacity 0.6) orientado con
  `quaternion.setFromUnitVectors` en el ángulo exacto de entrada de la broca, con el largo
  igual al espesor real de la pieza que se atraviesa (simula la profundidad de perforación).
- **UX-002 — Simulación cinemática: deslizar el cajón (D-041).** En el paso "Colocá la
  corredera y meté el cajón" aparece un control deslizante que mueve la caja del cajón + la
  mitad móvil del riel a lo largo del riel real (0 hasta el largo real de la corredera), para
  ver/probar que corre suave. El desplazamiento es relativo al valor anterior del control
  (no un reset absoluto), así funciona tanto si el cajón está en la mesada como ya insertado.
- **HER-001 — Tipos de corredera.** El sistema YA soporta corredera de rodillo (económica),
  telescópica estándar y telescópica soft-close (premium) — elegidos automáticamente por
  `calidad.nivel`, con su propio nombre de compra y holgura de 13 mm por lado (R-05). Una
  cuarta variante, "corredera oculta" (montaje por debajo, sin rieles laterales visibles), NO
  está modelada: requeriría geometría de caja distinta (hueco debajo del fondo en vez de
  holgura lateral) que este sistema todavía no calcula; agregarla es trabajo pendiente, no
  algo que se puede simular cambiando solo un número sin representar la pieza real.
- **EST-005 — Tornillos del frente de cajón (D-042).** El "Frente" (decorativo) se atornilla
  SIEMPRE desde ADENTRO del cajón: el tornillo atraviesa el "Frente interno" y se ancla en el
  Frente sin perforarlo del todo — esto ya estaba en el texto de la guía, y ahora también se
  dibuja en 3D (4 tornillos cerca de las esquinas, cabeza en la cara interior). Nunca se
  atornilla desde afuera del mueble (se vería la cabeza en la cara linda).
- **HER-002 — Tipo de tirador (D-042).** Selector "Tipo de tirador" en Cajonera: **Manija
  metálica** (agrega una malla de manija sobre la cara exterior del frente; se compra 1 por
  frente), **Corte uñero** (el frente se modela con un rebaje semicircular tallado en el canto
  superior mediante `THREE.Shape`+`THREE.ExtrudeGeometry`, en vez de comprar un tirador — la
  lista de cortes anota el rebaje en las notas de esa pieza), o **Sistema push** (frente liso,
  sin tirador ni rebaje).
- **EST-006 — Luz entre frentes de cajón: YA implementada.** Se verificó con datos reales
  (posiciones de piezas) que ya hay exactamente 3 mm de separación entre cada frente de cajón
  consecutivo (`altoFrente = (altoUtil - 3n)/n`, `zF = e + i*(altoFrente+3)`). No hacía falta
  ningún cambio.
- **EST-007 — Zócalo de 70 mm en la cajonera del escritorio: evaluado, no implementado.** El
  problema real que describe (melamina en contacto con el piso) ya está cubierto por los
  regatones (H-10, 07_HERRAJES): 4 por cajonera, mismo criterio que en el ropero (M-22). La
  cajonera del escritorio ES una de las dos patas del escritorio (corre de piso a tapa, igual
  que el lateral); levantarla 70 mm con un zócalo tipo mueble de cocina exigiría recortar
  también la otra pata para que el escritorio no quede desnivelado — una reestructuración
  grande del diseño de patas para un problema que ya tiene solución (regatones), no una
  corrección de un defecto real.
- **HER-003 — Escuadras 3D de la tapa (D-043).** La unión tapa↔apoyos usa escuadras
  metálicas (no tornillo confirmat pasante) — el texto y la lista de compras ya lo decían,
  pero el 3D no dibujaba nada ahí. Ahora se dibuja un cubo metálico (gris, no rojo — el rojo
  ya es el color de las guías de perforación de UX-001/EST-002, usarlo acá hubiera mezclado
  los dos significados) en cada punto real de apoyo, detectado comparando la altura y el
  solape de cada parante contra la CAPA que realmente toca (la inferior oculta, si la tapa es
  doble — no la visible que lista el paso).

## Documentos relacionados

- Medidas por defecto y ergonomía: `06_MEDIDAS_ESTANDAR.md`
- Qué herraje/tornillo exacto comprar: `07_HERRAJES_Y_TORNILLERIA.md`
- Cómo estas reglas llegan al código: `02_ARQUITECTURA.md` (validador y motor)
