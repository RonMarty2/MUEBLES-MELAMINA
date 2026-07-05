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
