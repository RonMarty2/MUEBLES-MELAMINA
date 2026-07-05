# 07 — HERRAJES Y TORNILLERÍA

## Objetivo de este documento

Catálogo de los herrajes y fijaciones que el sistema usa, con código **H-xx**, criterio de
uso y regla de cantidad. `despiece_*.py` y `generador_presupuesto.py` calculan cantidades
siguiendo exactamente estas reglas; los precios unitarios viven en
`software/nucleo/precios.json` (editable por el usuario).

## Catálogo v1 (escritorio gamer)

| Código | Herraje | Uso | Regla de cantidad |
|---|---|---|---|
| H-01 | **Tornillo confirmat 7×50** | Unión estructural entre tableros de 18 | 2 por unión hasta 300 mm de largo de unión; +1 cada 150–200 mm extra (R-09) |
| H-02 | **Tarugo de madera Ø8×30 + cola vinílica** | Acompaña o reemplaza confirmat donde no debe verse cabeza | 2 por unión, mismas posiciones que H-01 |
| H-03 | **Tornillo aglomerado 4×50** | Alternativa a H-01 si no hay broca confirmat | Igual que H-01 |
| H-04 | **Tornillo aglomerado 4×30** | Fijar frente aplicado de cajón desde adentro; fijar correderas al mueble ya vienen con 4×16, ver H-05 | 4 por frente de cajón |
| H-05 | **Corredera telescópica 45 mm (par)** | Cajones | 1 par por cajón; largo según R-08; incluye tornillos 4×16 (12 por par si no) |
| H-06 | **Grommet pasacables Ø60 (u Ø80)** | Terminación de perforación en tapa | 1 por perforación (R-16) |
| H-07 | **Clavo 1½" o tornillo 3×16** | Fijar fondos de 3 mm | 1 cada 150 mm de perímetro |
| H-08 | **Tapacanto PVC 22 mm × 0,45 mm** | Cantos visibles generales | Metros = suma de cantos visibles × 1,10 (R-11) |
| H-09 | **Tapacanto PVC 22 mm × 2 mm** | Cantos de la tapa (alto impacto) | Perímetro visible de tapa × 1,10 |
| H-10 | **Regatón/nivelador atornillable** | Base de laterales y cajonera | 2 por lateral-panel, 4 por cajonera |
| H-11 | **Escuadra metálica 25 mm** | Refuerzo tapa↔viga y tapa↔laterales donde no conviene tornillo pasante | 1 cada 300 mm de unión oculta |

## Criterios de elección (los "por qué")

- **Confirmat vs. tornillo común (H-01 vs H-03):** el confirmat está diseñado para
  aglomerado: cuerpo cilíndrico grueso que no parte la placa y aguanta desarme. Requiere
  broca escalonada específica (barata). Si el usuario aún no la tiene, H-03 + pre-perforado
  funciona; el presupuesto contempla ambas variantes con un flag en `precios.json`.
- **Correderas telescópicas (H-05) y no comunes de PVC:** el pedido del usuario es "cajones
  espaciosos" (peso: periféricos, discos, consolas). Las telescópicas de extracción total
  soportan 25–35 kg y permiten ver el fondo del cajón. El descuento de 13 mm por lado (R-05)
  presupone exactamente este herraje.
- **Regatones (H-10):** la melamina apoyada directo al piso absorbe humedad por el canto y
  se hincha. Siempre separar del piso; además permiten nivelar.

## Perforaciones — posiciones que calcula el motor

El motor emite para cada unión la lista de perforaciones con: pieza, cara/canto,
coordenadas (x, y) desde la esquina inferior-izquierda de la pieza, diámetro y profundidad.

Convenciones:
- **P-01:** perforación de confirmat: pasante Ø4,5 en la pieza exterior; Ø3 × 40 de
  profundidad en el canto que recibe. Posiciones a 50 mm de cada borde de la unión y luego
  el paso de R-09.
- **P-02:** correderas: eje de la corredera a **mitad del alto de la caja del cajón**;
  del lado del mueble, misma altura relativa al piso del hueco. Fijación en las ranuras de
  las correderas (frontal y trasera como mínimo).
- **P-03:** pasacables: centro a 60 mm del borde trasero de la tapa (R-16), broca copa o
  caladora Ø según grommet.

## Lista de compras — formato de salida

`generador_presupuesto.py` agrupa por herraje, redondea a la unidad de venta (los
confirmat vienen ×50 o ×100; el tapacanto por metro; las correderas por par) y agrega la
columna "para qué es", para que comprar sea sin pensar:

```
| Artículo                        | Cantidad | Venta por | Para qué |
| Confirmat 7×50                  | 46       | caja ×50  | uniones estructura |
| Corredera telescópica 450 (par) | 3        | par       | cajones 1–3 |
```

## Buenas y malas prácticas

| ✅ | ❌ |
|---|---|
| Comprar 10 % extra de tornillería (se pierden, se doblan) | Comprar exacto y frenar el armado un sábado |
| Correderas de marca media (25 kg reales) | Las más baratas: se doblan con el cajón cargado |
| Broca confirmat si se harán varios muebles (ROI en 2 muebles) | Comprar herramientas para "algún día" (ver política en 03) |

## Documentos relacionados

- Reglas de unión y descuentos: `05_REGLAS_DE_CARPINTERIA.md`
- Precios editables: `software/nucleo/precios.json`
- Cómo se listan en presupuesto: `software/salidas/generador_presupuesto.py`
