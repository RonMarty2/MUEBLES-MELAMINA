# 02 — ARQUITECTURA

## Objetivo de este documento

Describir el flujo completo del sistema, la responsabilidad exacta de cada módulo y las
fronteras que ningún cambio puede cruzar sin registrar una decisión en
`09_DECISIONES_TECNICAS.md`.

## Diagrama de flujo

```
┌──────────────────────────────────────────────────────────────────────┐
│  USUARIO: "quiero un escritorio gamer de 1,80 con 3 cajones"         │
└──────────────┬───────────────────────────────────────────────────────┘
               ▼
┌──────────────────────────────┐   El proveedor se elige en config.json.
│  CAPA IA  (software/ia/)     │   LM Studio local, OpenAI o Anthropic:
│  cliente_ia.py               │   todos hablan el mismo protocolo
│                              │   (API estilo OpenAI /v1/chat/completions).
│  Entrada: texto del usuario  │   La IA recibe el system prompt de
│  Salida:  receta JSON        │   08_REGLAS_PARA_IAS.md + el esquema.
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│  RECETA JSON                 │   Contrato central del sistema.
│  (schema_receta.json)        │   Especificación: 04_ESQUEMA_RECETA_JSON.md
│                              │   Versionada con campo "version".
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│  VALIDADOR (nucleo/          │   1º validación de forma (JSON Schema).
│  validador.py)               │   2º validación de carpintería (reglas R-xx
│                              │      de 05_REGLAS_DE_CARPINTERIA.md).
│  Rechaza con mensajes claros │   Si algo falla, el error vuelve a la IA
│  en español                  │   para que corrija la receta, o al usuario.
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│  MOTOR DE DESPIECE           │   Matemática pura, sin IA:
│  (nucleo/despiece_*.py)      │   • piezas exactas (descuenta espesores)
│  Un módulo por tipo de       │   • herrajes y tornillos con cantidades
│  mueble.                     │   • posiciones de perforación
│  Hoy: despiece_escritorio.py │   Salida: objeto Mueble (modelos.py)
└──────────────┬───────────────┘
               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  GENERADORES DE SALIDA (software/salidas/)                          │
│                                                                     │
│  generador_visor_html.py → visor_3d.html  (visor 3D propio, gratis, │
│                           offline: three.js incrustada; D-009)      │
│  generador_sketchup.py  → mueble_sketchup.rb (script Ruby; SketchUp │
│                           lo ejecuta y dibuja componentes nombrados │
│                           con material asignado → OpenCutList los   │
│                           lee automáticamente)                      │
│  generador_cortes.py    → lista_cortes.csv (respaldo sin SketchUp)  │
│                           + perforaciones.md (tornillos y brocas)   │
│  generador_presupuesto.py → compras.md + presupuesto.md             │
│                           (precios desde nucleo/precios.json,       │
│                            editable por el usuario)                 │
└─────────────────────────────────────────────────────────────────────┘
```

## Responsabilidades y fronteras (lo que NO se puede mezclar)

| Módulo | Responsabilidad única | Prohibido |
|---|---|---|
| `ia/cliente_ia.py` | Conectarse a un proveedor de IA y obtener/ajustar recetas | Calcular medidas de piezas; tocar archivos de salida |
| `recetas/schema_receta.json` | Definir la forma válida de una receta | Contener reglas de carpintería (esas van en el validador) |
| `nucleo/validador.py` | Rechazar recetas imposibles o peligrosas | Corregir silenciosamente valores (debe avisar, no adivinar) |
| `nucleo/despiece_*.py` | Convertir receta válida → piezas + herrajes + perforaciones | Leer/escribir archivos; hablar con IAs; formatear salidas |
| `nucleo/modelos.py` | Estructuras de datos compartidas (Pieza, Herraje, Mueble…) | Lógica de ningún mueble concreto |
| `salidas/generador_*.py` | Formatear el objeto Mueble a un archivo concreto | Recalcular medidas (usan lo que el motor ya calculó) |
| `main.py` | Orquestar el flujo y la línea de comandos | Contener lógica de negocio |

**Regla de oro:** los datos fluyen en una sola dirección
(texto → receta → mueble → archivos). Ningún generador de salida modifica el mueble;
ningún despiece lee texto del usuario.

## Por qué esta arquitectura (resumen; detalle en 09)

- **JSON como contrato (D-001):** desacopla la IA del motor. Cualquier IA, formulario web
  futuro o edición manual produce el mismo resultado.
- **Un módulo de despiece por tipo de mueble (D-004):** un escritorio, un placard y un
  bajo mesada comparten piezas (laterales, cajones) pero no estructura. Cada tipo tiene su
  módulo que reutiliza funciones comunes (p. ej. `despiece_cajon()`); agregar un mueble
  nuevo nunca toca los existentes.
- **Script Ruby en vez de plugin de SketchUp (D-003):** un `.rb` generado se ejecuta desde
  la consola Ruby de SketchUp sin instalar nada. Cuando el flujo madure puede convertirse
  en plugin/extensión (fase futura, ver 10).
- **CSV de cortes además de OpenCutList (D-005):** respaldo utilizable sin SketchUp
  (mandárselo por WhatsApp al que corta las placas, por ejemplo).

## Cómo se agrega un tipo de mueble nuevo (procedimiento estándar)

1. Documentar sus medidas estándar en `06_MEDIDAS_ESTANDAR.md` y reglas nuevas en `05`.
2. Extender `schema_receta.json` con el nuevo `tipo_mueble` y sus parámetros.
3. Crear `nucleo/despiece_<tipo>.py` reutilizando las funciones comunes.
4. Agregar validaciones específicas en `validador.py`.
5. Los generadores de salida **no se tocan**: trabajan sobre el objeto `Mueble` genérico.
6. Registrar la decisión y ejemplos en `09` y actualizar `00_INDICE.md` si hay docs nuevos.

## Manejo de errores (política global)

- Todo error que llegue al usuario debe estar **en español, decir qué está mal, dónde y
  cómo corregirlo**. Ejemplo: `"El cajón 3 tendría 95 mm de alto útil; el mínimo práctico
  es 60 mm de interior + estructura (regla R-12). Reducí la cantidad de cajones o aumentá
  el alto de la cajonera."`
- El validador junta **todos** los errores de una receta y los reporta juntos (no de a uno).
- Errores de conexión con la IA nunca rompen el flujo con receta manual: `main.py --receta
  archivo.json` no requiere IA.

## Documentos relacionados

- Contrato JSON: `04_ESQUEMA_RECETA_JSON.md`
- Reglas que aplica el validador: `05_REGLAS_DE_CARPINTERIA.md`
- Justificación de herramientas: `03_STACK_TECNOLOGICO.md`
- Registro de decisiones: `09_DECISIONES_TECNICAS.md`
