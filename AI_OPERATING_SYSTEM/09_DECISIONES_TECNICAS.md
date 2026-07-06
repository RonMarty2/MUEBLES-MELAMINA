# 09 — REGISTRO DE DECISIONES TÉCNICAS

## Objetivo de este documento

Memoria de decisiones (formato ADR simplificado). **Antes de proponer un cambio, la IA debe
buscar aquí si ya se decidió y por qué.** Reabrir una decisión está permitido, pero citando
la decisión original y qué cambió en el contexto.

Formato de cada entrada:
- **D-xxx — Título** · Fecha · Estado (vigente / reemplazada por D-yyy)
- Contexto → Decisión → Alternativas descartadas → Consecuencias

---

## D-001 — La IA genera recetas JSON; un motor determinista genera todo lo demás
**Fecha:** 2026-07-05 · **Estado:** vigente

- **Contexto:** el usuario quiere pedir muebles en lenguaje natural y obtener 3D, tornillos,
  cortes y presupuesto; y poder usar IA local gratis o IA paga indistintamente.
- **Decisión:** la IA solo produce/modifica recetas JSON (esquema en 04). Piezas, herrajes,
  perforaciones y costos los calcula Python determinista validado por reglas R-xx.
- **Descartadas:** (a) que la IA genere directamente el script de SketchUp — alucina
  geometría y cada error cuesta placa real; (b) que la IA calcule el despiece — mismos
  riesgos, imposible de testear.
- **Consecuencias:** el sistema funciona incluso sin IA (receta manual); cambiar de
  proveedor de IA es editar `config.json`; toda mejora de calidad va al motor, no al prompt.

## D-002 — LM Studio como servidor de IA local (no Ollama)
**Fecha:** 2026-07-05 · **Estado:** vigente

- **Contexto:** el usuario ya usa LM Studio. Ollama era la alternativa del plan original.
- **Decisión:** LM Studio, vía su servidor compatible con API OpenAI (`localhost:1234/v1`).
- **Descartadas:** Ollama — equivalente técnico, pero migrar no aporta nada al usuario.
- **Consecuencias:** `cliente_ia.py` habla protocolo OpenAI; si el día de mañana se usa
  Ollama (también compatible), es solo cambiar la URL.

## D-003 — Salida a SketchUp por script Ruby generado, no plugin
**Fecha:** 2026-07-05 · **Estado:** vigente

- **Contexto:** hay que dibujar el mueble en SketchUp desde Python.
- **Decisión:** Python genera un archivo `.rb` autocontenido; el usuario lo ejecuta desde
  la consola Ruby de SketchUp (guía en README). Componentes nombrados con material
  asignado para que OpenCutList los lea.
- **Descartadas:** (a) plugin/extensión de SketchUp — mejor experiencia pero mucho más
  desarrollo; queda como evolución natural en la hoja de ruta; (b) generar archivo `.skp`
  directo — el formato es propietario y no hay escritor libre confiable.
- **Consecuencias:** flujo manual de 3 pasos en SketchUp (abrir consola, cargar script,
  ver mueble); aceptable para prototipo.

## D-004 — Un módulo de despiece por tipo de mueble
**Fecha:** 2026-07-05 · **Estado:** vigente

- **Decisión:** `despiece_escritorio.py` hoy; cada tipo futuro (placard, cocina) tendrá el
  suyo, compartiendo utilidades (p. ej. cálculo de cajones) vía funciones comunes.
- **Descartada:** un motor "genérico paramétrico universal" — sobreingeniería: cada tipo
  de mueble tiene reglas estructurales propias que un genérico termina llenando de `if`.
- **Consecuencias:** agregar un mueble nuevo no arriesga los existentes (procedimiento en 02).

## D-005 — CSV de cortes propio ADEMÁS de OpenCutList
**Fecha:** 2026-07-05 · **Estado:** vigente

- **Decisión:** OpenCutList es el optimizador oficial (dentro de SketchUp); el sistema
  además emite `lista_cortes.csv` simple.
- **Motivo:** el CSV sirve sin abrir SketchUp (mandarlo a la tienda que corta placas).
- **Descartada:** programar optimización de cortes propia — problema duro ya resuelto gratis.

## D-006 — Sin base de datos en v1; archivos + Git
**Fecha:** 2026-07-05 · **Estado:** vigente

- **Decisión:** recetas y salidas como archivos en `proyectos/`; precios en JSON editable.
- **Criterio de reapertura:** cuando exista gestión de clientes/pedidos u histórico de
  precios → SQLite. Si hay multiusuario/web → PostgreSQL.

## D-007 — Español en documentación, mensajes y dominio del código
**Fecha:** 2026-07-05 · **Estado:** vigente

- **Decisión:** documentación, errores y nombres del dominio (pieza, despiece, tapacanto)
  en español. El usuario es carpintero hispanohablante y debe poder leer todo.
- **Descartada:** inglés "por convención" — optimizaría para programadores que no son el
  usuario de este proyecto.

## D-008 — Primer mueble: escritorio gamer
**Fecha:** 2026-07-05 · **Estado:** vigente

- **Contexto:** elegido por el usuario (monitores, CPU, cables, cajones espaciosos).
- **Consecuencias:** las reglas R-14 a R-17 y medidas M-01 a M-15 se escribieron primero
  para este caso; los próximos tipos reutilizan la base (R-01 a R-13).

## D-009 — Visor 3D propio en HTML además de SketchUp
**Fecha:** 2026-07-05 · **Estado:** vigente

- **Contexto:** el usuario preguntó por una alternativa gratuita a SketchUp (no quiere
  pagar licencia). SketchUp Make 2017 es gratis pero solo para uso no comercial.
- **Decisión:** el sistema genera SIEMPRE dos visualizaciones: (a) el script Ruby para
  SketchUp/OpenCutList (D-003) y (b) `visor_3d.html`, un archivo autocontenido con la
  biblioteca libre three.js INCRUSTADA (funciona offline, doble clic y listo).
- **Descartadas:** (a) depender solo de SketchUp — ata el proyecto a una licencia;
  (b) cargar three.js desde internet (CDN) — probado y descartado: si no hay conexión el
  visor queda en blanco; (c) FreeCAD — libre pero con curva de aprendizaje alta.
- **Consecuencias:** camino 100 % gratuito garantizado: visor HTML + `lista_cortes.csv`
  (la tienda o un optimizador online reemplazan a OpenCutList). SketchUp queda como vía
  preferida cuando esté disponible. `three.min.js` (r128, licencia MIT) vive versionado
  en `software/salidas/recursos/`.

## D-010 — Interfaz principal: app de un solo archivo HTML (doble clic)
**Fecha:** 2026-07-05 · **Estado:** vigente

- **Contexto:** el usuario rechazó terminantemente el flujo por terminal ("NO QUIERO NADA
  DE .PY, ABRIR CMD"). Necesita abrir un archivo con doble clic y usar controles visuales.
- **Decisión:** la interfaz principal es **`ESCRITORIO_GAMER.html`** en la raíz del repo:
  un único archivo autocontenido (three.js incrustada) con panel de controles (sliders,
  selectores), vista 3D en vivo y pestañas de Cortes / Compras / Presupuesto /
  Perforaciones / Precios. Todo se recalcula al instante, sin instalar nada, sin internet.
  El motor de despiece está **portado 1:1 a JavaScript** dentro del archivo.
- **Descartadas:** (a) empaquetar el Python como .exe — pesado, antivirus lo bloquean, un
  binario por sistema operativo; (b) app de escritorio (Electron) — cientos de MB;
  (c) servidor web local — obliga a "levantar" algo, justo lo que el usuario no quiere.
- **Consecuencias / control de divergencia:** ahora hay DOS motores (Python y JS). El
  Python queda como referencia y para automatización futura (IA por API, CNC, más muebles).
  Para que no diverjan: ambos usan las mismas constantes, nombres de pieza y códigos de
  regla, y la app trae pruebas de paridad embebidas (abrir `ESCRITORIO_GAMER.html?test=1`)
  con los MISMOS números canónicos que `software/tests/test_sistema.py` (piezas 27,
  lateral 714×650, piso 364, frente 396×229, caja 550/199, 40 confirmats, total $620.90).
  Si se cambia una fórmula, se cambia en los dos motores en el mismo commit.
- **Build:** `ESCRITORIO_GAMER.html` se genera con `python software/app/construir.py`
  a partir de `software/app/app_fuente.html` + `software/salidas/recursos/three.min.js`.
  Editar SIEMPRE el fuente, nunca el archivo generado.

## D-011 — Segundo tipo de mueble: ropero/placard
**Fecha:** 2026-07-05 · **Estado:** vigente

- **Contexto:** el usuario pidió poder crear más tipos de mueble (ropero, mesa, TV).
  Elegimos ropero primero por ser el más pedido y porque introduce patrones nuevos
  (puertas, barral) que conviene resolver antes que los más simples.
- **Decisión:** siguiendo el procedimiento de `02_ARQUITECTURA.md`, se agregó:
  reglas propias en `11_REGLAS_Y_MEDIDAS_ROPERO.md` (R-18 a R-25, M-16 a M-23,
  H-12 a H-16); `nucleo/validador_ropero.py` y `nucleo/despiece_ropero.py`; sección
  `ropero` en `schema_receta.json` (oneOf por `tipo_mueble`). Los generadores de
  salida (SketchUp, cortes, presupuesto) **no se tocaron**: reciben el mismo objeto
  `Mueble` genérico sin importar el tipo (confirma que la frontera de módulo funciona).
- **Refactor asociado:** `validador.py` pasó de ser un módulo monolítico de
  escritorio a un **dispatcher** (`MODULOS_POR_TIPO`) que delega en
  `validador_<tipo>.py`. La lógica vieja de escritorio se movió sin cambios a
  `validador_escritorio.py`. Esto evita que agregar tipos futuros siga
  inflando un único archivo.
- **Reutilización:** el despiece de cajones del ropero (R-24) llama a las mismas
  funciones `confirmats_por_union` y `elegir_corredera` de `despiece_escritorio.py`
  en vez de duplicarlas — ambos tipos comparten la aritmética de cajón (R-05 a R-08).
- **Descartada:** un motor "genérico paramétrico" que cubra escritorio y ropero con
  una sola función — ya descartado en D-004 por la misma razón (reglas estructurales
  distintas por tipo terminan en un `if` infernal).
- **Consecuencias:** el patrón queda demostrado para el próximo tipo (mesa, mueble de
  TV, cocina): nuevo doc de reglas numerado, nuevo `validador_<tipo>.py`, nuevo
  `despiece_<tipo>.py`, sección nueva en el schema, sin tocar generadores de salida.

## D-012 — App con selector de mueble (una sola interfaz para todos los tipos)
**Fecha:** 2026-07-05 · **Estado:** vigente

- **Contexto:** con más de un tipo de mueble, el usuario pidió una única app (no un
  archivo HTML por mueble) con un selector arriba para cambiar de tipo.
- **Decisión:** `ESCRITORIO_GAMER.html` se renombra a **`DISENADOR_MUEBLES.html`**
  (D-010 sigue vigente: un solo archivo autocontenido, three.js incrustada, motor en
  JS). Arriba de los controles se agrega un selector "Escritorio gamer / Ropero"; el
  panel de controles y las pestañas de resultados cambian según el tipo elegido, pero
  el motor 3D, los generadores de CSV/RB y el layout general son compartidos.
- **Consecuencias:** el motor JS mantiene paridad con AMBOS motores Python
  (`despiece_escritorio.py` y `despiece_ropero.py`), verificada con pruebas embebidas
  `?test=1` (ver también D-010).

## D-013 — Uniones excéntricas (cam-lock) como alternativa al confirmat
**Fecha:** 2026-07-05 · **Estado:** vigente

- **Contexto:** el usuario relató una mala experiencia real con muebles de melamina que
  "se aflojaban solos" y quedaban imposibles de mover sin desarmarse. Causa raíz
  identificada: un tornillo recto atornillado al canto de aglomerado depende de que la
  rosca "muerda" partículas sueltas; mover el mueble ya armado tuerce la estructura como
  un paralelogramo y esa torsión se concentra en los tornillos, agrandando el agujero
  hasta que giran en el vacío (documentado como regla R-26 en
  `07_HERRAJES_Y_TORNILLERIA.md`).
- **Decisión:** se agrega `uniones.tipo` ("confirmat" | "excentrica") como campo común a
  ambos tipos de mueble. Con "excentrica", TODAS las uniones estructurales usan H-17
  (herraje excéntrico/cam-lock + espiga) en vez de H-01 (confirmat), misma cantidad
  calculada por `confirmats_por_union` — el nombre de la función no cambia porque la
  matemática de espaciado es la misma, solo cambia el herraje final.
- **Descartadas:** (a) que el sistema elija automáticamente según si el usuario "parece"
  ir a mudar el mueble — imposible de inferir con confianza, mejor que el usuario decida
  explícitamente; (b) ofrecer excéntrica solo en el ropero (que se percibe más "movible")
  — el escritorio también se mueve al limpiar/reacomodar, se ofrece en ambos.
- **Implementación:** `nucleo/uniones.py` (`herraje_union()`) evita duplicar la lógica
  entre `despiece_escritorio.py` y `despiece_ropero.py`; espejado en JS (`herrajeUnion()`
  en `app_fuente.html`).

## D-014 — Elevación para monitor (escritorio gamer)
**Fecha:** 2026-07-05 · **Estado:** vigente

- **Contexto:** pedido del usuario: "una elevación en el medio para el monitor y abajo
  un teclado". Decidido como opción DENTRO del escritorio gamer (no un mueble aparte),
  ver pregunta al usuario y su respuesta.
- **Decisión:** campo `elevacion_monitor` (incluir/ancho/profundidad) en la receta del
  escritorio. Estructuralmente: 2 patas verticales de 18 mm que se apoyan SOBRE la tapa
  principal (no reemplazan ninguna pieza existente) y sostienen una segunda tapa elevada
  110 mm arriba (M-25) — ese hueco es donde se desliza el teclado.
- **Descartada:** integrar la elevación como parte de la tapa principal (una tapa con
  escalón tallado) — requeriría cortes no rectangulares que la placa comercial y las
  herramientas de corte estándar no resuelven fácil; el diseño de "patas + tapa elevada"
  usa piezas 100% rectangulares, coherente con el resto del sistema.
- **Consecuencias:** es la primera pieza del escritorio que se apoya sobre otra pieza
  (no sobre el piso/zócalo) — el patrón queda disponible para reutilizar en otros
  "accesorios apoyados" futuros (bandeja de teclado corrediza, organizador, etc.)

## D-015 — Guía de armado paso a paso con resaltado 3D
**Fecha:** 2026-07-05 · **Estado:** vigente

- **Contexto:** el usuario, sin experiencia en carpintería, pidió instrucciones de armado
  y dijo textualmente "no sé nada y no quiero cometer errores".
- **Decisión:** nueva pestaña **🔧 Armado** en la app: pasos numerados en lenguaje simple;
  al tocar un paso, las piezas de ese paso se **iluminan en el 3D** (el resto se atenúa a
  15% de opacidad). Espejo en Python (`generador_instrucciones.py` →
  `instrucciones_armado.md`) para quien use el CLI o abra el proyecto generado.
- **Implementación:** cada mesh 3D se etiqueta con `userData.pieza`; `resaltarPiezas()` /
  `limpiarResaltado()` ajustan opacidad. El orden de pasos vive en
  `12_GUIA_DE_ARMADO.md` como fuente de verdad única.
- **Descartada:** dibujos 2D esquemáticos por paso — mucho más trabajo; queda para una
  fase futura si el resaltado 3D no alcanza.

## D-016 — Explicaciones en la app (íconos "?") y tapa con capa oculta cruda
**Fecha:** 2026-07-05 · **Estado:** vigente

- **Contexto:** el usuario no entendía qué significaba cada control, y al ver "2 placas"
  y "tapa capa inferior/superior" en la lista de cortes pensó que eran dos muebles. Además
  señaló, acertadamente, que no tiene sentido pagar una placa decorativa para esconderla
  abajo en la tapa doble.
- **Decisión:** (a) mapa `AYUDAS` con un ícono "?" junto a cada control que abre una
  explicación en lenguaje simple; (b) cajas explicativas arriba de las pestañas Cortes y
  Compras que explican qué es una placa (2600×1830 mm) y por qué se necesitan varias;
  (c) la capa oculta de la tapa doble ahora es **aglomerado crudo** (`mat_crudo` en Python,
  `matCrudo` en JS), separado en el presupuesto de la melamina decorativa — más barato,
  sin perder resistencia.
- **Consecuencias:** `generador_presupuesto.py` pasó de clasificar placas por *espesor* a
  clasificarlas por *categoría de material* (melamina/crudo/fondo), porque ahora dos
  piezas del mismo espesor (18 mm) pueden ser de materiales distintos y precios distintos.

## D-017 — Unidades cm/mm en la app (motor siempre en mm)
**Fecha:** 2026-07-05 · **Estado:** vigente

- **Contexto:** el usuario pidió ver las medidas en centímetros por resultarle más
  intuitivo que milímetros.
- **Decisión:** la app muestra **cm por defecto** con un botón para cambiar a mm
  (persistido en localStorage). El motor de cálculo (Python y JS) **sigue trabajando
  siempre en mm puertas adentro** — la unidad es puramente de presentación
  (`fmtNum`/`fmtMedida` en JS). **Excepción:** el espesor de las placas (18/25/36 mm)
  siempre se muestra en mm, incluso en modo cm, porque así se habla en el oficio (nadie
  dice "1,8 cm de espesor").
- **Descartada:** convertir el motor entero a trabajar en cm — perdería precisión en
  cálculos con decimales y complicaría la paridad con la tienda de corte (que siempre
  factura y corta en mm).

## D-018 — Niveles de calidad/durabilidad de herrajes
**Fecha:** 2026-07-05 · **Estado:** vigente

- **Contexto:** el usuario relató una mala experiencia real: muebles de melamina baratos
  cuyos rieles de cajón se salían o hacían bailar el cajón con el tiempo, y aclaró que
  construye para uso propio, no para vender, y necesita que dure.
- **Decisión:** campo común `calidad.nivel` ("economico" | "estandar" | "premium",
  defecto "estandar") en ambos tipos de mueble. Cambia el ARTÍCULO de corredera y bisagra
  especificado (no la geometría): económico = rodillo/PVC (H-05e, se desgasta); estándar =
  telescópica extracción total (H-05, la que ya existía); premium = soft-close de acero
  (H-18/H-19). El nivel premium además sugiere automáticamente unión excéntrica (R-26) si
  el usuario había dejado confirmat.
- **Implementación:** `nucleo/herrajes_calidad.py` centraliza la elección para Python;
  espejo `correderaCalidad()`/`bisagraCalidad()`/`unionSugerida()` en JS. Documentado en
  `12_GUIA_DE_ARMADO.md` con la tabla de qué gana cada nivel.
- **Descartada:** ocultar el nivel económico — aunque no se recomienda para uso propio,
  el usuario puede tener presupuesto ajustado en un mueble de menor uso; se deja disponible
  con su aviso de durabilidad explícito.

## D-019 — Armado con cámara enfocada, marcadores de tornillo y panel expandible
**Fecha:** 2026-07-05 · **Estado:** vigente

- **Contexto:** con la guía de armado ya en uso, el usuario reportó tres problemas
  concretos: el panel de armado era muy chico; no entendía bien el texto de los pasos; y
  sobre todo "no veo dónde se ponen los tornillos, bisagras, etc." — necesitaba algo
  mucho más visual, mostrando cada pieza individualmente y sus puntos de fijación.
- **Decisión:**
  1. **Botón "Agrandar/Achicar"** en la barra de pestañas: expande `#paneles` a 52vh
     (probado; 78vh dejaba muy chica la vista 3D — el balance importa más que el tamaño
     máximo). Persistido en localStorage.
  2. **Cámara que se enfoca en la pieza del paso activo** (`enfocarPiezas`): calcula la
     caja delimitadora (bounding box) en mm de las piezas del paso y centra/acerca la
     cámara ahí — reemplaza la vista del mueble completo mientras se sigue un paso.
  3. **Marcadores de tornillo geométricos** (`calcularMarcadoresTornillo`): en vez de
     depender del texto libre de `perforaciones` (pensado para lectura, no para
     coordenadas exactas por instancia), se calculan por **adyacencia real de las cajas
     delimitadoras** de las piezas del paso — dos piezas que comparten una cara con
     tolerancia de 3 mm reciben 1 o 2 marcadores (según R-09: 2 si la unión supera 300 mm)
     exactamente en el plano de contacto. Esto ubica los puntos donde realmente va la
     fijación, sin importar el tipo de mueble o el texto del paso.
  4. **Resaltado de cantos con tapacanto**: los bordes (`LineSegments`) de las piezas del
     paso activo se pintan naranja si esa pieza tiene `cantos` no vacío, dejando el resto
     en gris — responde directamente "¿se toma en cuenta el tapacanto?".
  5. La pieza activa se vuelve semitransparente (82% opacidad, `depthWrite: false`) para
     que los marcadores que caen en caras internas/traseras se vean "a través" de la
     pieza en vez de quedar completamente ocultos.
  6. Los avisos amarillos se ocultan mientras se usa la pestaña Armado (ya está toda esa
     información integrada en el panel), liberando espacio para el 3D.
- **Descartada:** usar las coordenadas de `perforaciones` (que son texto pensado para
  humanos, con etiquetas de pieza combinadas como "Laterales de cajonera") para ubicar
  marcadores — habría requerido reescribir esa estructura a algo estrictamente
  geométrico por instancia; el enfoque de adyacencia por bounding box da resultados
  correctos reutilizando los datos que ya existen (`pos`/`dim` de cada `Pieza`).
- **Consecuencias:** esta mejora vive solo en la app (JS); el generador Python de
  instrucciones no tiene contraparte visual 3D y no se tocó — sigue siendo la versión de
  texto para quien use el CLI o abra el proyecto generado.

## D-020 — Glosario visual de herrajes (qué tornillo es, con qué broca)
**Fecha:** 2026-07-05 · **Estado:** vigente

- **Contexto:** viendo "Tornillo 4×30" en la guía de armado, el usuario no entendió la
  notación (pensó que podía ser un error tipográfico por "4×3"), preguntó si era "cualquier
  tornillo", y si hacía falta un agujero guía y con qué broca — dudas legítimas de alguien
  sin experiencia en ferretería.
- **Decisión:** cada vez que un paso de armado menciona un herraje, la app busca
  coincidencias en un **glosario visual** (`GLOSARIO_HERRAJES`, por patrón de texto) y
  muestra una tarjeta con: nombre completo del herraje, una **ilustración SVG** (tornillo
  con diámetro y largo acotados, o un ícono de broca para herrajes sin medida simple como
  bisagras/confirmat/excéntrico), el **tamaño de broca exacto para el agujero guía**, y una
  nota aclarando qué lo hace distinto de un herraje "genérico" de ferretería.
- **Cobertura inicial:** tornillo aglomerado 4×30 y 4×16, confirmat 7×50, herraje
  excéntrico + espiga, bisagra cazoleta 35 mm, tarugo Ø8, clavo 1½". Ampliable agregando
  entradas al arreglo `GLOSARIO_HERRAJES` en `app_fuente.html`.
- **Descartada:** imágenes reales (fotos) de cada herraje — requeriría archivos externos,
  rompiendo la Decisión D-010 (un solo archivo autocontenido, sin depender de assets).
  Un dibujo SVG generado en código cumple el mismo propósito ilustrativo sin ese costo.
- **Consecuencias:** vive solo en la app (JS); no tiene contraparte en el generador Python
  de instrucciones (que es texto plano para el CLI).

---

## D-021 — Vista "explotada" tipo IKEA en el armado 3D

**Fecha:** 2026-07-05 · **Estado:** vigente

- **Contexto:** con las piezas del paso activo tocándose/superpuestas en la vista 3D en
  perspectiva, el marcador amarillo de tornillo se veía ambiguo — el usuario reportó que
  "parece que la perforación está en el medio de la unión", y pidió algo parecido a los
  manuales de armado de IKEA (piezas separadas, agujero claramente visible en cada una).
- **Decisión:** en vez de migrar a diagramas 2D planos (un renderer nuevo, mucho trabajo),
  se agrega una vista explotada **dentro del motor 3D actual**: al entrar a un paso, las
  piezas de ese paso se desplazan ~70 mm desde el centro común del grupo, a lo largo del
  vector que va del centro del grupo al centro de cada pieza (`vectorExplode` +
  `explotarPiezas`). Cada punto de tornillo (`calcularMarcadoresTornillo`, ahora con
  `{x,y,z,piezaA,piezaB}`) se dibuja **dos veces** — una en la cara de cada pieza ya
  separada — unidas por una línea punteada, dejando claro que es la misma unión vista
  desde los dos lados. `enfocarPiezas` amplió el margen de zoom (×2.9) para que las piezas
  separadas no queden cortadas fuera de cámara. `limpiarResaltado()` restaura todas las
  piezas a su posición original (`posBase`) al salir de la pestaña Armado.
- **Descartadas:** diagramas 2D estilo manual real de IKEA — requeriría un renderer nuevo
  separado del motor 3D existente, duplicando lógica de posicionamiento de piezas; se
  posterga indefinidamente a menos que la vista explotada resulte insuficiente.
- **Consecuencias:** cambio puramente visual — no toca ninguna cifra de despiece, precios
  ni validaciones (confirmado con la suite Python de 81 pruebas y la suite JS embebida de
  47 pruebas, ambas en verde sin cambios). Vive solo en `app_fuente.html` (JS); no aplica
  al generador Python de instrucciones en texto plano.

---

## D-022 — Planos acotados tipo IKEA para bisagras y correderas

**Fecha:** 2026-07-05 · **Estado:** vigente

- **Contexto:** la vista explotada D-021 resolvió la ambigüedad de tornillos entre piezas,
  pero el usuario mostró manuales reales de IKEA y señaló que seguía sin saber cómo colocar
  correderas y bisagras: en qué cara van, hacia qué dirección apuntan y a qué distancia de
  los bordes hay que marcar.
- **Decisión:** agregar en la pestaña Armado tarjetas SVG 2D acotadas, calculadas con las
  medidas reales del mueble actual, solo para herrajes donde la perspectiva 3D no comunica
  bien la cota: bisagras cazoleta y correderas de cajón. El glosario visual sigue diciendo
  "qué herraje es"; el nuevo plano dice "dónde y cómo colocarlo".
- **Reglas implementadas:** `posiciones_bisagras()` aplica R-22 y devuelve centros desde el
  borde superior de la puerta; P-04 fija la cazoleta Ø35 a 21,5 mm del canto y profundidad
  12-13 mm; `altura_corredera()` centraliza P-02 para que el eje de corredera en Python y JS
  coincida. La app muestra además herramientas mínimas (cinta, lápiz, escuadra, brocas y
  punta PH2) y notas de orientación ("cara interna", "brazo hacia el lateral", "frente a ras").
- **Consecuencias:** Python ahora emite perforaciones reales de cazoleta en roperos batientes
  y textos de corredera más explícitos. JS dibuja los planos y tiene pruebas de paridad para
  bisagras/correderas. `DISENADOR_MUEBLES.html` debe reconstruirse siempre que cambie
  `app_fuente.html`.
- **Ajuste posterior:** el primer SVG resultó demasiado esquemático. Se amplió el formato a
  página ancha tipo manual: corredera separada en riel fijo del mueble y riel móvil del cajón,
  puntos de tornillo 4×16 numerados, frente/fondo, advertencias de no retranquear/no inclinar;
  bisagra con cazoleta, brazo, placa base, tornillos, profundidad y errores comunes.

---

## D-023 — Botones "Anterior/Siguiente" siempre visibles + explicación de cómo se coloca el tapacanto

**Fecha:** 2026-07-06 · **Estado:** vigente

- **Contexto:** el usuario reportó dos problemas concretos en la pestaña Armado, con captura
  de un manual de IKEA como referencia de claridad: (1) en el panel sin agrandar, los botones
  "◀ Anterior" / "Siguiente ▶" quedaban cortados fuera de la pantalla — bug real de layout:
  `#contenido` tenía `flex:1; overflow:auto` pero sin `min-height:0`, así que nunca se achicaba
  para habilitar su propio scroll y el contenido se recortaba directamente contra el borde de
  la ventana del navegador en vez de quedar navegable dentro del panel. (2) preguntó
  explícitamente si el tapacanto se perfora o se pega con cola — el sistema marcaba el borde
  naranja pero nunca explicaba el método real de colocación (plancha caliente).
- **Decisión:** (a) se agregó `min-height:0` a `#contenido` y una franja de navegación
  `.nav-paso` con `position: sticky; bottom` para que los botones de paso queden siempre
  visibles y alcanzables, con o sin scroll, en modo normal y expandido. (b) se reescribió la
  nota de cantos con tapacanto explicando el método real: se activa con calor de una plancha
  de ropa (el tapacanto ya trae pegamento termofusible), nunca se perfora ni se pega con cola
  común, y se recorta el sobrante con cutter o lima. (c) se amplió la nota de los marcadores
  amarillos para conectar el dibujo 3D con la acción física: medir con cinta y escuadra sobre
  la pieza real, perforar primero (agujero guía) y recién después atornillar.
- **Descartada:** ocultar la lista de pasos o la caja explicativa para "ganar espacio" —
  perdía contexto; la solución de raíz era el bug de layout (`min-height:0`) más botones
  sticky, no esconder información.
- **Consecuencias:** cambio solo de UI/texto en `app_fuente.html`; no toca ninguna cifra de
  despiece. `DISENADOR_MUEBLES.html` reconstruido.

---

## D-024 — Diagrama visual didáctico genérico en TODOS los pasos de armado

**Fecha:** 2026-07-06 · **Estado:** vigente

- **Contexto:** los planos acotados de D-022 (bisagra/corredera) no eran lo que el usuario
  pedía — quiso decir que necesita un dibujo simple en **cada** paso de armado, no solo en
  esos dos, porque "no sé nada, soy torpe" y el texto solo no le alcanza para saber qué hacer
  con sus manos. De ~10-11 pasos por tipo de mueble, solo 2 tenían dibujo.
- **Decisión:** en vez de ilustrar cada paso a mano (carísimo de mantener), se generalizó el
  patrón de D-022 a un **renderer único y paramétrico**, `svgDiagramaPaso(datos)` en
  `software/app/app_fuente.html`, con un vocabulario visual chico y reusable (igual que IKEA
  reusa las mismas flechas/íconos en todo el manual):
  - **Layouts:** `apilado` (una pieza encima de otra, ej. tapa doble), `escuadra` (piezas en
    L/U, ej. armar una caja), `una-pieza` (una pieza sola con una acción).
  - **Acciones:** `atornillar-abajo`, `atornillar-adentro`, `encolar-prensar`, `clavar`,
    `insertar-deslizar`, `perforar-broca`, `colgar-apoyar` — cada una con su ícono/flecha.
  - Cajas reusables `cajaOrdenXY`/`cajaNoHacerXY` (mismo estilo que ya existía en D-022,
    ahora factorizadas) para el orden de pasos y los errores comunes.
  - `paso(...)` (dentro de `instruccionesArmadoJS`) ganó un 6to argumento opcional
    `diagrama = {layout, piezas, accion, fijacion, orden, noHacer}`, sin tocar los 5
    argumentos existentes — no afecta el texto que también usa `generador_instrucciones.py`
    (el dibujo, igual que el glosario de D-020, vive solo en la app JS).
  - Se completó el `diagrama` de los ~14 pasos con acción física clara (tapa doble, caja de
    cajonera/laterales del ropero, cajas de cajón, frentes, zócalo, apoyos verticales, tapa
    sobre apoyos, viga trasera, pasacables, elevación de monitor, regatones, fondo, barral,
    estante inferior, puertas corredizas). Bisagra y corredera siguen usando su plano
    acotado específico de D-022 (más preciso que cualquier plantilla genérica); los pasos
    sin acción física ("entendé los cortes", "terminación final") se quedan solo con texto.
- **Descartada:** una ilustración bespoke por paso (18 dibujos a mano) — mucho más trabajo
  de mantener y sin garantía de consistencia visual entre pasos.
- **Consecuencias:** cambio 100% visual en `app_fuente.html`; no toca ninguna cifra de
  despiece ni el motor Python. `DISENADOR_MUEBLES.html` reconstruido.

---

## D-025 — Indicador de scroll en el panel de controles (izquierda)

**Fecha:** 2026-07-06 · **Estado:** vigente

- **Contexto:** el usuario reportó que "no aparecen todas las opciones" en el panel
  izquierdo, y que solo las veía si hacía zoom out del navegador. Medido con Playwright a
  una resolución común de notebook (1366×768): el panel de controles mide ~1060 px de
  contenido real contra solo ~440 px visibles — el panel SÍ tenía scroll interno
  (`#controles { overflow-y: auto }`, ya existía), pero no había ninguna señal visible de
  que hubiera más opciones abajo, así que el usuario no sabía que debía desplazarse.
- **Decisión:** (a) scrollbar del panel estilizada para que se vea claramente (ancho 11px,
  color visible, también en Firefox vía `scrollbar-color`) en vez de depender de la barra
  fina/auto-oculta del sistema operativo; (b) un aviso `↓ desplazá para ver más opciones ↓`
  fijo (`position: sticky; bottom`) al pie del panel, que la propia app oculta/muestra según
  si ya se llegó al final (`actualizarIndicadorControles()`, disparado por `scroll` del panel,
  `resize` de la ventana y al cambiar de tipo de mueble); (c) se recortaron levemente los
  márgenes del panel (`.campo`, títulos `h2`, header) para que entre más contenido sin
  necesidad de scroll.
- **Descartada:** rediseñar el panel en pestañas/acordeón para que quepa todo sin scroll —
  cambio de navegación mucho más grande; el problema real no era "falta espacio" sino "no se
  nota que hay que bajar", así que alcanza con hacerlo evidente.
- **Consecuencias:** cambio de UI en `app_fuente.html` (CSS + HTML + JS de wiring);
  no toca ninguna cifra de despiece. `DISENADOR_MUEBLES.html` reconstruido.

---

## D-026 — Un paso por cajón (no todos juntos) + arreglo del salto tapa↔apoyos

**Fecha:** 2026-07-06 · **Estado:** vigente

- **Contexto:** con capturas de la vista explotada 3D, el usuario mostró que el paso "Armá
  las cajas de los cajones" resaltaba y separaba los 3 cajones **a la vez**, produciendo una
  vista saturada de piezas superpuestas y docenas de puntos amarillos — imposible de leer
  ("no son guías fáciles, son afirmaciones, no se ve didáctico... ¿no podemos separar cada
  etapa?"). Además, en el paso "Colocá la tapa sobre los apoyos", la lista de piezas
  resaltadas solo incluía la tapa (nunca los apoyos/lateral/cajonera sobre los que se
  apoya), así que `calcularMarcadoresTornillo` no tenía 2 piezas para detectar contacto: la
  unión tapa↔base nunca mostraba marcador ni se separaba — exactamente lo que el usuario
  reportó como "no veo la parte donde se une la tabla de arriba con la de abajo".
- **Decisión:** (a) los pasos que antes agrupaban TODOS los cajones ("Armá las cajas de los
  cajones", "Colocá las correderas...", "Atornillá los frentes...") ahora generan **un paso
  por cajón** (`Armá la caja del cajón N de T`, etc.), en un `for` sobre
  `cajonera.cantidad_cajones` (escritorio) / `cajones.cantidad_cajones` (ropero) — tanto en
  `instruccionesArmadoJS` (`app_fuente.html`) como en `generador_instrucciones.py` (Python,
  para paridad de texto). Cada paso resalta y explota SOLO las piezas de ese cajón. (b) "Colocá
  la tapa sobre los apoyos" ahora incluye los apoyos/lateral/cajonera en su lista de piezas
  resaltadas, así el contacto tapa↔base se detecta y se dibuja como cualquier otra unión. (c)
  se agregó un layout nuevo al diagrama genérico (D-024), `apoyado` (dos patas + una pieza
  arriba, sin piso), más fiel que reusar `escuadra` para este caso. (d) los textos de los
  pasos tocados se reescribieron en formato numerado imperativo ("1. Uní... 2. Pre-perforá...
  3. Clavá...") en vez de párrafos descriptivos, para que se lean como instrucciones y no como
  afirmaciones.
- **Descartada:** mantener un solo paso "por tipo de pieza" con un selector de "cuál cajón
  mirar" dentro del mismo paso — más complejo de programar y de entender que simplemente
  tener un paso por cajón en la lista.
- **Consecuencias:** el número de pasos totales aumenta con la cantidad de cajones (ej.
  10 → 16 pasos con 3 cajones en el escritorio de ejemplo). Se agregaron pruebas en
  `test_sistema.py` verificando que cajón 1 y cajón 2 tengan pasos separados y que un paso de
  un cajón no cite piezas de otro. No cambia ninguna cifra de despiece — motor Python sigue
  en verde. Se regeneraron los proyectos demo.

---

## Plantilla para nuevas decisiones

```
## D-xxx — Título corto
**Fecha:** AAAA-MM-DD · **Estado:** vigente

- **Contexto:** qué problema o pregunta apareció.
- **Decisión:** qué se decidió, en una o dos frases.
- **Descartadas:** qué alternativas se evaluaron y por qué no.
- **Consecuencias:** qué implica para el código, los docs o el usuario.
```

## Documentos relacionados

- Toda decisión que afecte herramientas actualiza `03_STACK_TECNOLOGICO.md`.
- Toda decisión que afecte el contrato actualiza `04_ESQUEMA_RECETA_JSON.md` y la versión.
