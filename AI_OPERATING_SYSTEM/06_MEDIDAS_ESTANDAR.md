# 06 — MEDIDAS ESTÁNDAR Y ERGONOMÍA

## Objetivo de este documento

Definir las medidas por defecto que la IA propone y los rangos que el validador acepta,
con su justificación ergonómica o comercial. Cada medida tiene código **M-xx** citable.

> Todas las medidas en **milímetros**.

## Formatos comerciales de placa

- **M-10 — Placa de melamina:** formato de referencia **2600 × 1830 × 18 mm**
  (mercado sudamericano; también circula 2440 × 1220). El generador de compras calcula la
  cantidad de placas estimada; el diagrama exacto lo da OpenCutList.
- **M-11 — Fondo (fibrofácil/MDF):** placa de 1830 × 2600 × 3 mm.
- **M-12 — Tapacanto PVC:** rollos; se compra por metro. 0,45 mm y 2 mm de espesor,
  ancho 22 mm (para canto de 18 mm).

## Escritorio (uso general y gamer)

| Código | Medida | Valor por defecto | Rango válido | Justificación |
|---|---|---|---|---|
| M-01 | Alto de tapa al piso | **750** | 700–800 | Estándar ergonómico para silla de 450 mm; escribir/mouse con codo a ~90° |
| M-02 | Profundidad | **700** | 500–900 | Gamer: monitor a ≥ 500 mm de los ojos + teclado + muñecas. Los 600 de oficina quedan cortos con monitores de 27"+ |
| M-03 | Ancho | **1600** | 900–2400 | 1600 = 2 monitores de 24–27" lado a lado; 1800–2000 para setup triple |
| M-04 | Espacio libre para piernas | ≥ **600 ancho × 650 alto** | — | El validador verifica que cajonera + soporte CPU dejen este hueco |
| M-05 | Soporte CPU (ancho interior) | **250** | 200–350 | Gabinete ATX típico: 210–230 de ancho; ventilación a los lados |
| M-06 | Altura bandeja CPU sobre piso | **100** | fijo en v1 | Limpieza, aspirado y ventilación inferior |
| M-25 | Elevación para monitor (ancho / prof. / alto libre) | 800 / 250 / **110** (alto libre fijo) | ancho 500–1200, prof. 200–350 | Bandeja apoyada sobre la tapa, con dos patas que dejan 110 mm libres abajo — suficiente para deslizar un teclado (25–35 mm) + la mano al tipear. El ancho debe dejar 200 mm de margen a los bordes de la tapa (validado) |
| M-26 | Retorno en L: largo del ala | **1000** | 600–1600 | Superficie útil lateral; >~900 exige tapa doble y >~1300 viga (R-04/R-13 aplicadas al retorno, R-31) |
| M-27 | Retorno en L: profundidad del ala | **500** | 400–700 | Apoyo cómodo para papeles o segundo monitor sin invadir el paso |

## Cajones de escritorio

| Código | Medida | Valor | Justificación |
|---|---|---|---|
| M-07 | Ancho de cajonera | **400** (300–600) | 400 da cajón útil de ~338 (R-05): entra papelería A4 (297 mm) y periféricos |
| M-08 | Frente de cajón | 120 mín / 200–300 ideal / 350 máx | Ver R-07. "Cajones espaciosos" del pedido gamer = apuntar a 220–300 |
| M-09 | Profundidad de cajonera | profundidad del escritorio − 100 | Retranqueo: los cajones no chocan las rodillas y queda paso de cables atrás |

## Pasacables y gestión de cables (setup gamer)

- **M-13 — Grommets:** Ø 60 mm estándar (u 80 para peinar varios cables gruesos), a 60 mm
  del borde trasero de la tapa (R-16).
- **M-14 — Cantidad por defecto: 2** (uno por zona de monitor). Con soporte CPU incluido,
  ubicar uno alineado con la CPU.
- **M-15 — Canaleta/bandeja portacables bajo tapa:** prevista como mejora futura
  (`10_HOJA_DE_RUTA.md`); en v1 se resuelve con canaleta comercial adhesiva (va a la lista
  de compras como opcional).

## Referencia rápida de otros muebles (para futuros tipos)

Estos valores todavía NO están implementados; se documentan para que la IA no improvise
cuando se agreguen los tipos (procedimiento en `02_ARQUITECTURA.md`):

- Placard: profundidad 550–600 (percha 480 + puerta), barral a 1700–1750, estante superior
  a ≥ 1800 del piso.
- Bajo mesada de cocina: alto 850–900 con mesada, profundidad 560–580, zócalo 100–120.
- Biblioteca/estantería: profundidad 250–350, estantes cada 280–350.

## Cómo usa esto la IA

1. El usuario no da una medida → usar el **valor por defecto** de la tabla.
2. El usuario da una medida dentro del rango → usarla tal cual.
3. Fuera del rango → emitir la receta en el límite más cercano **y avisar en la
   conversación** citando el código (p. ej. "te lo dejé en 800 de alto, que es el máximo
   ergonómico M-01; más alto te va a quedar incómodo para escribir").

## Documentos relacionados

- Reglas físicas que complementan estas medidas: `05_REGLAS_DE_CARPINTERIA.md`
- Límites aplicados por el esquema: `04_ESQUEMA_RECETA_JSON.md`
- Herrajes que estas medidas presuponen: `07_HERRAJES_Y_TORNILLERIA.md`
