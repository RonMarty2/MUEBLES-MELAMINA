# 03 — STACK TECNOLÓGICO

## Objetivo de este documento

Listar cada herramienta del proyecto, por qué se eligió, qué alternativas se descartaron y
bajo qué condiciones se reconsideraría. Ninguna herramienta entra al stack sin pasar por
este documento y por una decisión en `09_DECISIONES_TECNICAS.md`.

## Criterios de selección (en orden de prioridad)

1. **Gratis o libre** siempre que cubra la necesidad (el usuario evita gastos innecesarios).
2. **Corre local** en la PC del usuario (independencia de servicios de terceros).
3. **Simple de instalar y usar** para un no-programador.
4. **Estándar y con comunidad** (que la IA y los foros lo conozcan bien).

## El stack

| Herramienta | Rol | Costo |
|---|---|---|
| **Python 3.10+** | Motor de despiece, validación, generadores | Gratis |
| **three.js (incrustada)** | Visor 3D propio en el navegador (`visor_3d.html`), sin instalar nada | Gratis (MIT) |
| **SketchUp** (opcional) | Visualización 3D alternativa + OpenCutList | Make 2017 gratis (uso no comercial) |
| **Ruby (API de SketchUp)** | Lenguaje del script que dibuja dentro de SketchUp | Incluido en SketchUp |
| **OpenCutList** | Plugin de SketchUp: lista de cortes + diagrama de placa optimizado | Gratis (open source) |
| **JSON / JSON Schema** | Formato de receta y su validación de forma | Gratis (estándar) |
| **LM Studio** | Servidor de IA local (el usuario ya lo usa) | Gratis |
| **Git + GitHub** | Historial del código y la documentación | Gratis |
| **Markdown** | Toda la documentación y salidas legibles (compras, presupuesto) | Gratis (estándar) |

**Total de inversión en software: $0.** Las únicas erogaciones posibles son suscripciones
de IA de pago (opcionales, ver abajo) y hardware/herramientas físicas de carpintería.

## Justificación pieza por pieza

### Python (motor)
- Lenguaje más documentado del mundo para este tipo de herramientas; cualquier IA lo escribe
  y depura bien; corre en Windows/Mac/Linux sin drama.
- Solo biblioteca estándar + `jsonschema` (única dependencia externa, para validar recetas).
- **Descartado:** Node.js (nada que ofrezca aquí que Python no tenga, y el ecosistema
  CAD/CAM científico está en Python), C++ (complejidad injustificada para este volumen de cálculo).

### Visor 3D propio (three.js incrustada) — vía 100 % gratuita
- El sistema genera `visor_3d.html`: un archivo único que se abre con doble clic en
  cualquier navegador y muestra el mueble en 3D (girar, zoom, resaltar piezas).
- La biblioteca three.js (libre, MIT) va INCRUSTADA en el archivo: funciona sin internet
  y sin instalar nada. Copia versionada en `software/salidas/recursos/three.min.js`.
- Motivo: el usuario no quiere pagar licencias; esta vía garantiza visualización gratis
  para siempre (Decisión D-009).

### SketchUp + Ruby API (visualización alternativa + OpenCutList)
- Si hay SketchUp disponible (Make 2017 es gratis para uso no comercial), el `.rb`
  generado dibuja el mueble como componentes y habilita OpenCutList.
- **Descartados:**
  - *FreeCAD:* potente y libre, pero curva de aprendizaje alta.
  - *Fusion 360:* pago/limitado y nube obligatoria.
  - *three.js desde internet (CDN):* probado y descartado — sin conexión el visor
    quedaba en blanco; por eso va incrustada.

### OpenCutList (cortes)
- Plugin libre y gratuito, referencia mundial para carpinteros con SketchUp. Lee los
  componentes del modelo (nombre + material) y produce lista de cortes y diagrama de
  aprovechamiento de placa con porcentaje de desperdicio.
- Nuestro generador nombra los componentes y asigna materiales exactamente como OpenCutList
  espera, así el flujo es: ejecutar el `.rb` → abrir OpenCutList → listo.
- **Descartado:** escribir nuestro propio optimizador de cortes (problema matemáticamente
  duro — *bin packing 2D* — ya resuelto y gratis en OpenCutList). El CSV que generamos es
  respaldo informativo, no optimizador.

### LM Studio (IA local)
- El usuario ya lo usa. Expone un **servidor local compatible con la API de OpenAI**
  (`http://localhost:1234/v1`), de modo que nuestro `cliente_ia.py` usa el mismo código para
  LM Studio, OpenAI o cualquier proveedor compatible: solo cambian URL, clave y modelo en
  `config.json`.
- Modelos recomendados para generar recetas (tarea corta y estructurada): cualquier modelo
  instruccional de 7–8B cuantizado que entre en la RAM/GPU del usuario (p. ej. familia
  Llama 3.1 8B o Qwen 2.5 7B Instruct). Si las recetas salen mal formadas, subir de tamaño
  de modelo antes que tocar el código.
- **Ollama** es equivalente e igual de válido; no se migra porque LM Studio ya está en uso
  y no aporta diferencia (D-002).

### IAs de pago (OpenAI / Anthropic) — cuándo pagar
- **No son necesarias para operar.** Pagar solo si: (a) el modelo local falla seguido con
  pedidos complejos, o (b) se quiere conversación más natural. Antes de pagar, probar un
  modelo local más grande. El cliente soporta ambas por configuración, así que probar una
  suscripción un mes y cancelarla no rompe nada — ese es el retorno de inversión a evaluar.

### Git + GitHub
- Historial completo de código Y documentación: la "memoria" del proyecto es el repo mismo.
- Regla: la documentación se actualiza en el mismo commit que el código que la afecta.

### Base de datos: ninguna (por ahora)
- Las recetas y salidas son archivos en `proyectos/`; los precios, un JSON editable. Con un
  usuario y decenas de muebles, archivos + Git es más simple y transparente que una DB.
- **SQLite** entra cuando exista catálogo de clientes/pedidos o histórico de precios
  (fase futura, ver 10). **PostgreSQL** solo si esto se vuelve plataforma multiusuario.
  Registrado como D-006 para no re-discutirlo cada mes.

## Política de compras (resumen operativo)

Ante cualquier propuesta de compra (software o herramienta física), la IA debe responder con:
1. ¿Qué problema concreto resuelve que hoy no esté resuelto?
2. Alternativa gratuita/libre y qué se pierde con ella.
3. Costo total (incluye suscripción anualizada) vs. beneficio medible.
4. Recomendación explícita, con la opción "no comprar todavía" siempre sobre la mesa.

## Documentos relacionados

- Por qué la arquitectura usa estas piezas: `02_ARQUITECTURA.md`
- Decisiones formales y descartes: `09_DECISIONES_TECNICAS.md`
- Configuración de IAs: `08_REGLAS_PARA_IAS.md`
