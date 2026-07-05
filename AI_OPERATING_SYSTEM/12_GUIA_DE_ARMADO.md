# 12 — GUÍA DE ARMADO Y CONCEPTOS PARA PRINCIPIANTES

## Objetivo de este documento

Ser la fuente de verdad del **orden de armado** de cada mueble y de los **conceptos
básicos** que un usuario sin experiencia en carpintería necesita para no equivocarse.
Nace de un caso real: el usuario abrió la app, vio la lista de cortes y no entendió por
qué necesitaba "2 placas" ni por qué la tapa aparecía en "2 capas" (lo confundió con dos
muebles). Este documento — y su espejo interactivo en la app (pestaña 🔧 Armado) —
existen para que eso no vuelva a pasar.

## Conceptos que TODO usuario nuevo debe tener claros

- **Una "placa" es un tablero comercial grande**, no una pieza a medida: **2600 × 1830 mm**
  (como una puerta grande). Vos comprás el tablero entero; la tienda corta tus piezas de
  ahí adentro. Un mueble mediano casi nunca entra en un solo tablero — por eso la lista de
  compras pide varios.
- **La "tapa doble" no son dos muebles**: es la superficie de arriba armada con **dos
  placas pegadas** (36 mm en vez de 18 mm) para que no se pandee con peso (monitores,
  libros). Se arma UNA vez, encolando y atornillando las dos capas entre sí.
- **La capa oculta de la tapa doble es aglomerado CRUDO, no melamina decorativa**
  (Decisión D-016): no tiene sentido pagar una cara linda para esconderla abajo. Solo la
  capa de arriba (la que se ve y se toca) lleva melamina con color y tapacanto.
- **Unidades:** el motor de cálculo siempre trabaja puertas adentro en milímetros (evita
  errores de redondeo). La app le muestra al usuario **cm por defecto** (más intuitivo
  para medidas de mueble) con un botón para pasar a mm — **excepto el espesor de las
  placas**, que siempre se expresa en mm (18 mm, 36 mm) porque así se habla en el oficio;
  nadie dice "1,8 cm de espesor" (D-017).

## Orden de armado — Escritorio gamer

1. Entender las placas y ordenar los cortes recibidos de la tienda.
2. Armar la tapa doble si corresponde (encolar + atornillar 4×30 en grilla; capa linda
   arriba, capa cruda abajo).
3. Armar la caja de la cajonera (2 laterales + piso + fondo).
4. Armar las cajas de los cajones (2 laterales + frente interno + contrafrente + fondo).
5. Colocar correderas y probar que los cajones corran.
6. Atornillar los frentes visibles de los cajones desde adentro.
7. Parar los apoyos verticales (lateral izquierdo, y el parante + bandeja del soporte de
   CPU si corresponde).
8. Apoyar la tapa sobre los apoyos y fijarla con escuadras.
9. Viga trasera si el escritorio es ancho (evita el "hamaqueo").
10. Perforar y colocar los pasacables.
11. Montar la elevación para monitor si se pidió (D-014).
12. Regatones, tapacantos y ajuste final. **Nunca arrastrar el mueble ya armado** (R-26).

## Orden de armado — Ropero/placard

1. Entender las placas y ordenar los cortes.
2. Zócalo/base retranqueada.
3. Parar los laterales, piso y techo (caja principal).
4. Cerrar el fondo (sin sellar hermético, para ventilar — R-25).
5. Divisor + cajonera interior, si se pidió (mismo patrón que el escritorio).
6. Barral y sus soportes.
7. Estante inferior, si se pidió.
8. Puertas: bisagras (batientes) o rieles (corredizas), reguladas hasta cerrar parejas.
9. Terminación: tapacantos, ajuste final, nivelación y fijación a la pared si es alto.

## Nivel de calidad de herrajes (D-018)

El usuario relató una mala experiencia con muebles de melamina baratos: correderas que
se salen o hacen bailar el cajón con el tiempo. Causa: correderas de **rodillo/PVC** (media
extensión), pensadas para uso liviano, se desgastan rápido. El sistema ofrece 3 niveles,
elegibles por el usuario, que **no cambian la geometría del mueble**, solo el herraje
especificado:

| Nivel | Corredera | Bisagra | Cuándo conviene |
|---|---|---|---|
| Económico | Rodillo/PVC (H-05e) | Cazoleta común (H-13) | Mueble de uso muy esporádico o presupuesto muy ajustado |
| Estándar | Telescópica extracción total (H-05) | Cazoleta común (H-13) | Uso normal — es el punto de partida del sistema |
| **Premium** | Telescópica soft-close, acero 40 kg (H-18) | Cazoleta soft-close (H-19) | **Recomendado para muebles propios que deben durar años** (D-018) |

El nivel **premium** además sugiere automáticamente cambiar las uniones estructurales a
**excéntricas** (R-26) si el usuario había dejado confirmat, porque es la combinación que
más tiempo aguanta sin aflojarse.

## Cómo se arma un cajón, en detalle (para quien nunca armó uno)

Un cajón tiene DOS partes independientes:
1. **La caja** (estructura interna, no se ve): 2 laterales + frente interno + contrafrente
   + fondo de 3 mm. Se arma como una cajita cerrada.
2. **El frente visible** (el que tiene el tirador): se atornilla a la caja **desde
   adentro**, después de que la caja ya corre sobre sus correderas. Así el frente queda
   perfectamente alineado con los demás.

Las correderas van de a pares: una guía atornillada a cada costado de la caja, la otra
pareja atornillada al mueble a la misma altura (eje a la mitad del alto de la caja, P-02).

## Documentos relacionados

- Reglas físicas y de unión: `05_REGLAS_DE_CARPINTERIA.md` (R-26 movilidad y aflojamiento)
- Catálogo de herrajes por nivel: `07_HERRAJES_Y_TORNILLERIA.md` (H-05e, H-18, H-19)
- Decisiones: `09_DECISIONES_TECNICAS.md` (D-015 a D-018)
- Implementación: `software/salidas/generador_instrucciones.py` (motor Python) y
  `instruccionesArmadoJS` en `software/app/app_fuente.html` (motor JS de la app)
