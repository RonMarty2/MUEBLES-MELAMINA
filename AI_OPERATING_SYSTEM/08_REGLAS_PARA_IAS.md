# 08 — REGLAS PARA LAS IAs (LM Studio, ChatGPT, Claude)

## Objetivo de este documento

Definir el protocolo exacto que cualquier IA conectada al sistema debe seguir para generar
y modificar recetas. Contiene el **system prompt oficial** que `cliente_ia.py` envía. Si el
esquema de receta cambia (04), este documento y el system prompt cambian en el mismo commit.

## Principio

La IA es un **traductor de intención a receta**, no una diseñadora libre. Su universo de
salida es el esquema de `04_ESQUEMA_RECETA_JSON.md`. Todo lo que no entre en el esquema se
responde en conversación, jamás inventando campos.

## System prompt oficial (v1)

Este bloque es el que `cliente_ia.py` envía como mensaje de sistema (mantener sincronizado
con `software/ia/cliente_ia.py`):

```
Sos el asistente de diseño de un software de muebles de melamina. Tu única salida válida
es una receta JSON que cumpla el esquema versión 1.0.

REGLAS ESTRICTAS:
1. Respondé SOLO con el JSON de la receta, sin texto antes ni después, sin ```.
2. Medidas en milímetros, números enteros.
3. Campos permitidos, defectos y límites:
   - tipo_mueble: "escritorio_gamer" (único tipo disponible)
   - dimensiones: ancho 900-2400 (defecto 1600), profundidad 500-900 (defecto 700),
     alto 700-800 (defecto 750)
   - tapa.tipo: "simple_18" | "doble_18" | "simple_25" (defecto "doble_18")
   - material: color (texto, defecto "Blanco"), espesor 15|18 (defecto 18),
     espesor_fondo 3|5.5→usar 3 (defecto 3)
   - cajonera: posicion "derecha"|"izquierda"|"ninguna" (defecto "derecha"),
     ancho 300-600 (defecto 400), cantidad_cajones 1-4 (defecto 3)
   - soporte_cpu: incluir true|false (defecto true), ancho 200-350 (defecto 250)
   - pasacables: cantidad 0-4 (defecto 2), diametro 60|80 (defecto 60)
4. Si el usuario pide un valor fuera de rango, usá el límite más cercano.
5. Si el usuario pide algo que estos campos no cubren, NO inventes campos: emití la
   receta con lo que sí se pueda y nada más.
6. Si te doy una receta anterior y un pedido de cambio, devolvé la receta COMPLETA con
   solo los campos afectados modificados.
7. Siempre incluí "version": "1.0" y "tipo_mueble".
```

## Protocolo de conversación (lo maneja `main.py`, no la IA)

1. `main.py` envía: system prompt + (receta anterior si existe) + pedido del usuario.
2. La IA devuelve JSON. `main.py` lo extrae (tolerando que algún modelo local desobedezca
   y envuelva en ``` ), lo valida con `validador.py`.
3. **Si la validación falla:** `main.py` reenvía a la IA el error textual con la
   instrucción "corregí la receta". Máximo 2 reintentos; luego reporta al usuario el error
   y la última receta para corrección manual.
4. Los avisos al usuario (límites aplicados, sugerencias) los genera el **software** a
   partir de la validación, citando reglas R-xx / M-xx — no se le pide a la IA que avise,
   porque los modelos chicos lo hacen mal.

## Diferencias por proveedor

| Proveedor | Config en `config.json` | Notas |
|---|---|---|
| **LM Studio** (defecto) | `url: http://localhost:1234/v1`, `api_key: "lm-studio"` | Activar "Start Server" en LM Studio. Modelo 7-8B instruct mínimo. Si el JSON sale mal formado seguido → probar modelo más grande antes de tocar código |
| **OpenAI** | `url: https://api.openai.com/v1` + clave | Mismo protocolo. Usar modelo económico: la tarea es simple |
| **Anthropic (Claude)** | `url: https://api.anthropic.com/v1` + clave, `formato: "anthropic"` | API distinta (headers y cuerpo); `cliente_ia.py` la adapta |

La elección de proveedor NUNCA cambia el resto del sistema (Decisión D-001/D-002).

## Cuándo escalar de IA local a IA paga

Escalar solo si, con un modelo local razonable (≥7B), pasa alguna de estas:
- Más del ~20 % de las recetas necesitan los 2 reintentos.
- Los pedidos de ajuste conversacional pierden campos de la receta anterior.

Y antes de pagar: probar un modelo local más grande. Registrar el resultado del
experimento en `09_DECISIONES_TECNICAS.md`.

## Rol de ChatGPT/Claude como consultores de desarrollo

Además de generar recetas, las IAs pagas pueden usarse puntualmente para desarrollar el
software. Protocolo para pedirles ayuda (lo aplica el usuario o la IA local al armar el
prompt):

1. Incluir SIEMPRE: el objetivo del proyecto (1 párrafo de `01_IDENTIDAD_Y_VISION.md`),
   el fragmento relevante de `02_ARQUITECTURA.md`, y el código/documento a modificar.
2. Pedir que la respuesta respete las fronteras de módulos (tabla de `02_ARQUITECTURA.md`).
3. Integrar la respuesta a mano, nunca pegar ciegamente: verificar que no invente
   dependencias nuevas ni contradiga reglas R-xx.
4. Si la respuesta propone cambiar la arquitectura: no aplicarla directo; registrar la
   propuesta en `09` y evaluarla.

## Malas prácticas detectadas y su corrección

| ❌ Problema típico | Corrección |
|---|---|
| El modelo local envuelve el JSON en ```json ... ``` | `main.py` ya lo tolera y extrae el JSON |
| El modelo "explica" antes del JSON | El extractor busca el primer `{`...último `}`; si no parsea, reintento con recordatorio de la regla 1 |
| El modelo inventa `"puertas": true` | El validador rechaza campos desconocidos y el error vuelve a la IA |
| El modelo convierte 1,6 m en "1.6" | Regla 2 del prompt + validación de enteros |

## Documentos relacionados

- Esquema que la IA debe cumplir: `04_ESQUEMA_RECETA_JSON.md`
- Código que implementa este protocolo: `software/ia/cliente_ia.py`, `software/main.py`
- Cuándo pagar una suscripción: `03_STACK_TECNOLOGICO.md` (política de compras)
