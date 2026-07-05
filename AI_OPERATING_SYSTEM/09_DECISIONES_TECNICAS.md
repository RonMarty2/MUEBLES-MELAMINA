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
