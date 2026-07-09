# 11 — REGLAS Y MEDIDAS DEL ROPERO/PLACARD

## Objetivo de este documento

Extender el conocimiento de carpintería (05, 06, 07) al segundo tipo de mueble del
sistema: el ropero/placard. Sigue la misma convención de códigos citables — **R-1x**
(reglas de carpintería propias del ropero), **M-1x** (medidas/ergonomía) y reutiliza los
**H-xx** ya existentes sumando los que sean nuevos. Este documento asume ya leídos 05, 06
y 07: solo agrega lo específico de este mueble, no repite lo común (espesores, uniones,
tapacanto, descuentos de correderas si lleva cajones interiores).

## Qué es un "ropero" en este sistema (v1)

Un módulo único (ancho configurable) de piso a techo, con: 2 laterales, piso, techo,
fondo de 3 mm, una barra colgadora (barral) con estante superior, un estante inferior
opcional, y **puertas** (corredizas o batientes) o directamente sin puertas (placard
abierto tipo vestidor). Cajones interiores opcionales reutilizando la lógica de cajón ya
existente (R-05 a R-08, R-12 de `05_REGLAS_DE_CARPINTERIA.md`).

> Fase 1 del ropero (esta versión): **un solo módulo**. Roperos de varios cuerpos se arman
> repitiendo módulos uno al lado del otro (ver `10_HOJA_DE_RUTA.md`).

## Medidas estándar (M-1x)

| Código | Medida | Valor por defecto | Rango válido | Justificación |
|---|---|---|---|---|
| M-16 | Ancho del módulo | **900** | 600–1200 | Módulo manejable: más ancho, la puerta/estante se vence (R-04 aplica igual, vano 800) |
| M-17 | Profundidad | **580** | 550–620 | Percha de hombro a hombro ~480–520 mm + margen de puerta y bisagra |
| M-18 | Alto total | **2400** | 2000–2600 | De piso a cielorraso típico; si el techo es más bajo, se achica |
| M-19 | Altura del barral (desde el piso) | **1750** | 1700–1800 | Que un pantalón colgado (largo ~1000) no toque el piso, dejando estante arriba |
| M-20 | Separación barral–pared lateral | 50 mm a cada lado | fijo | Espacio para el gancho del perchero y el soporte del barral |
| M-21 | Alto libre sobre el barral (para el estante superior) | mínimo **280** | — | Para que quepan ropa de cama/valijas en el estante de arriba |
| M-22 | Zócalo (separación piso) | **100** | 80–120 | Igual criterio que regatones (R-10 de 07): la melamina no debe tocar el piso húmedo |
| M-23 | Estante inferior (opcional, bajo el nivel de calzado) | a 200–300 mm del piso | — | Para zapatos, dentro del mismo módulo si no hay cajones |
| M-24 | Alto de frente de cajón dentro del ropero | **250** (fijo) | 120–350 (mismo rango que R-07) | La cajonera del ropero es un **bloque acotado**, no reparte toda la altura del módulo entre los cajones (a diferencia de la cajonera del escritorio, que sí ocupa toda su altura de apoyo). Arriba del bloque queda espacio libre para un estante adicional |

## Reglas de carpintería (R-1x)

- **R-18 — Estructura del módulo.** 2 laterales (18 mm) de profundidad M-17 y alto M-18;
  piso y techo (18 mm) entre laterales (ancho interior = ancho exterior − 2×18, R-02);
  fondo de 3 mm clavado por detrás (R-10 de 05). El módulo se apoya sobre una base/zócalo
  de 18 mm retranqueada 30 mm (para que no se vea al agacharse), a la altura M-22.
- **R-19 — Barral.** Tubo redondo (no es placa; ver H-12) sostenido por 2 soportes
  atornillados a los laterales interiores, a la altura M-19, retranqueado M-20 de cada
  lateral. Si el ancho interior supera 1000 mm, agregar un soporte central (el tubo de
  barral se cimbra igual que un estante, mismo principio que R-04).
- **R-20 — Estante superior.** Apoyado sobre tacos o rinconeras a la altura
  `alto_total − zócalo − espesor_techo − M-21` como mínimo; mismo límite de vano sin
  apoyo que R-04 (800 mm). **Ojo:** un módulo de más de ~836 mm de ancho exterior YA
  excede ese vano (interior = ancho − 36), por eso existe R-27. (Corrección: una versión
  anterior de este doc afirmaba que nunca se excedía — era falso, el ancho máximo M-16 es
  1200 mm → vano de 1164 mm.)
- **R-21 — Puertas batientes.** Cada puerta = (ancho módulo interior de puertas ÷ n) −
  3 mm de holgura entre puertas y 3 mm a cada lateral (mismo criterio que R-06 aplicado
  horizontalmente). Alto de puerta = alto total − zócalo − 6 mm de holgura arriba/abajo.
  Máximo recomendado por hoja: **600 mm de ancho** (más ancha, pesa demasiado para las
  bisagras cazoleta estándar y se comba).
- **R-22 — Bisagras por puerta.** Según el alto de la puerta (H-13): hasta 1500 mm → 2
  bisagras; 1500–2100 mm → 3 bisagras; más de 2100 mm → 4 bisagras. Separadas 100 mm de
  cada extremo, el resto repartidas uniformemente. El motor devuelve los centros reales en
  mm medidos desde el borde superior de la hoja; la distancia lateral de la cazoleta se rige
  por P-04.
- **R-23 — Puertas corredizas.** Van sobre riel superior e inferior (H-14), NO llevan
  bisagras. Cada hoja se solapa **20 mm** con la contigua (para tapar la luz al deslizar):
  ancho de hoja = (ancho módulo ÷ n hojas) + solape/2 en los bordes de solape. Se
  necesitan mínimo 2 hojas (no hay corrediza de una sola tapa completa). Alto de hoja =
  alto del vano − 10 mm (juego de los rieles).
- **R-24 — Cajones interiores (opcionales).** Reutilizan íntegramente R-05 a R-08 y R-12
  de `05_REGLAS_DE_CARPINTERIA.md` (mismo descuento de correderas, mismo reparto de
  frentes). Se ubican en un sector del módulo definido por `cajones.ancho` (como la
  cajonera del escritorio), típicamente al lado opuesto del barral.
- **R-25 — Ventilación.** El fondo de 3 mm NO debe ser hermético en toda su superficie:
  dejar la unión perimetral sin sellar (no usar cola en el fondo, solo grapas/clavos
  espaciados) para que la ropa no tome humedad. No requiere pieza extra, es una nota de
  armado.
- **R-27 — Vano máximo de estante cargado = 800 mm.** Un estante horizontal de melamina
  18 mm cargado (ropa, cajas, zapatos) se pandea por el medio a partir de ~800 mm de vano
  libre. Cuando el ancho interior supera 800 mm, el motor agrega automáticamente:
  (a) **"Refuerzo bajo techo"**: travesaño de melamina de canto (80 mm de alto) pegado al
  fondo, a lo ancho, atornillado al techo y a los laterales (mismo principio constructivo
  que la viga trasera R-13 del escritorio); (b) si hay estante inferior de zapatos con ese
  vano: **"Apoyo central estante inferior"**, un parante corto al medio entre el piso y el
  estante. Orientación de carga: vano ≤ 600 mm → carga alta sin refuerzo; 600–800 mm →
  carga media (~25 kg distribuidos, el motor avisa); > 800 mm → refuerzo obligatorio.
- **R-28 — Zócalo trasero.** Además del zócalo frontal retranqueado (R-18), el piso lleva
  un **zócalo trasero** gemelo pegado al fondo: dos líneas de apoyo en vez de una. Sin él,
  el piso de un módulo ancho cargado cede hacia atrás. No lleva tapacanto (no se ve).
- **R-29 — El fondo trabaja como rigidizador.** El fondo de 3 mm bien clavado es la única
  defensa del módulo contra la deformación en paralelogramo (racking) al moverlo o al
  abrir/cerrar puertas con fuerza. Se clava no solo al perímetro sino también a TODAS las
  líneas intermedias que lo tocan: zócalo trasero (R-28), refuerzo bajo techo (R-27) y
  divisor de cajones si existe. El motor suma esos clavos a la lista de compras. Conecta
  con R-26 (nunca arrastrar el mueble armado).

## Herrajes nuevos (H-1x, extienden a 07_HERRAJES_Y_TORNILLERIA.md)

| Código | Herraje | Uso | Regla de cantidad |
|---|---|---|---|
| H-12 | **Barral tubular cromado Ø25 mm + 2 soportes** | Colgar ropa | 1 barral por módulo (largo = ancho interior − 2×M-20); +1 soporte central si ancho interior > 1000 (R-19) |
| H-13 | **Bisagra cazoleta 35 mm (codo según profundidad)** | Puertas batientes | Cantidad según R-22 |
| H-14 | **Riel corredizo superior + inferior (juego)** | Puertas corredizas | 1 juego (largo = ancho del módulo) cada 2–3 hojas que compartan el mismo riel |
| H-15 | **Tirador o manija** | Toda puerta o cajón | 1 por puerta, 1 por frente de cajón |
| H-16 | **Rinconera o taco de estante** | Sostener el estante superior | 4 por estante (una por esquina) |

## Ejemplo de receta (para referencia; el esquema formal está en 04 + `schema_receta.json`)

```json
{
  "version": "1.0",
  "tipo_mueble": "ropero",
  "nombre": "Ropero dormitorio principal",
  "dimensiones": { "ancho": 900, "profundidad": 580, "alto": 2400 },
  "material": { "color": "Blanco" },
  "puertas": { "tipo": "batiente", "cantidad": 2 },
  "cajones": { "incluir": true, "ancho": 400, "cantidad_cajones": 3 },
  "estante_inferior": { "incluir": false }
}
```

## Buenas y malas prácticas específicas del ropero

| ✅ | ❌ |
|---|---|
| Barral con soporte central si el módulo supera 1000 mm | Barral de 1200 mm apoyado solo en los extremos: a los meses queda arqueado |
| Puertas correderas cuando el cuarto tiene poco espacio de apertura | Puertas batientes de 700 mm de ancho: pesan y las bisagras ceden |
| Dejar el fondo sin sellar para ventilar | Encolar el fondo herméticamente: la ropa toma olor a humedad |

## Documentos relacionados

- Reglas y herrajes comunes (espesores, uniones, cajones, tapacanto): `05_REGLAS_DE_CARPINTERIA.md`, `07_HERRAJES_Y_TORNILLERIA.md`
- Medidas generales de placa: `06_MEDIDAS_ESTANDAR.md`
- Cómo se integra este tipo de mueble al motor: `02_ARQUITECTURA.md` (procedimiento para agregar tipos de mueble) y Decisión D-011 en `09_DECISIONES_TECNICAS.md`
