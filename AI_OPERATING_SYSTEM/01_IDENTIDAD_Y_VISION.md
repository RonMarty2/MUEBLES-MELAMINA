# 01 — IDENTIDAD Y VISIÓN

## Objetivo de este documento

Definir qué es el proyecto, para quién es, qué rol cumple cada IA involucrada y cuál es
la visión a largo plazo. Es el documento que da contexto a todos los demás.

## Qué estamos construyendo

Un software de **diseño automático de muebles de melamina** con este flujo:

1. El usuario pide un mueble en lenguaje natural: *"quiero un escritorio gamer para dos
   monitores, con cajones espaciosos y lugar para la CPU"*.
2. Una IA (local o de pago, es intercambiable) convierte ese pedido en una **receta JSON**
   con medidas por defecto razonables.
3. El usuario ajusta conversando: *"hacelo 20 cm más ancho"*, *"agregá un cajón"*. Cada
   ajuste produce una nueva versión de la receta.
4. El **motor determinista** (Python, sin IA) valida la receta contra reglas reales de
   carpintería y genera:
   - un script Ruby que dibuja el mueble en **SketchUp** como componentes 3D nombrados,
   - la **lista de cortes** (y vía OpenCutList, el diagrama de aprovechamiento de placa),
   - las **posiciones de tornillos, tarugos y perforaciones**,
   - la **lista de compras** (placas, herrajes, tornillos, tapacanto) con cantidades,
   - el **presupuesto** con precios editables por el usuario.

## Para quién es

**Usuario principal:** Ron — carpintero/emprendedor de muebles de melamina. No es
programador. Todo lo que el sistema le muestre debe estar en español claro, con medidas en
milímetros, y las instrucciones de uso deben asumir cero conocimiento de programación.

**Visión comercial:** si el prototipo funciona, esto puede convertirse en una plataforma
para que otros carpinteros o clientes finales diseñen muebles. Esa visión se documenta en
`10_HOJA_DE_RUTA.md`; hoy no condiciona el diseño más allá de mantener el código modular.

## El principio rector: la IA propone, el motor dispone

> **La IA nunca dibuja, nunca calcula cortes y nunca decide un tornillo.**
> La IA solo escribe y modifica recetas JSON. Todo lo físico (medidas de piezas,
> herrajes, perforaciones, costos) lo produce código Python determinista y testeado.

Justificación (registrada como Decisión D-001 en `09_DECISIONES_TECNICAS.md`):

- Las IAs alucinan números. Un error de 5 mm arruina una placa de melamina real que cuesta
  dinero real. El motor determinista da siempre el mismo resultado correcto.
- Una receta JSON es texto corto y estructurado: hasta un modelo local pequeño corriendo en
  LM Studio la genera bien. Diseñar geometría 3D directamente, no.
- Permite cambiar de IA sin tocar nada más: hoy LM Studio gratis, mañana una suscripción a
  ChatGPT o Claude, pasado mañana el modelo local nuevo de moda. El contrato (el JSON) no cambia.
- Permite usar el sistema **sin ninguna IA**: una receta escrita a mano o desde un formulario
  produce exactamente el mismo mueble.

## Rol de cada IA

| IA | Rol | Qué hace | Qué NO hace |
|----|-----|----------|-------------|
| **IA local (LM Studio)** | Compañera permanente y por defecto | Genera y modifica recetas; conversa con el usuario; consulta esta documentación | No dibuja, no calcula despieces, no inventa reglas de carpintería |
| **ChatGPT / Claude (API paga)** | Consultores especializados, opcionales | Lo mismo que la local pero con más capacidad; útiles para pedidos complejos o para mejorar el propio software | No son el cerebro obligatorio; el sistema funciona sin ellos |
| **Claude Code (esta IA)** | Director técnico del desarrollo | Escribe y mantiene el software y esta documentación; registra decisiones en 09 | No decide por el usuario: propone y espera confirmación en decisiones de producto |

Toda IA que participe debe seguir el protocolo de `08_REGLAS_PARA_IAS.md`.

## Comportamiento esperado de la IA acompañante

Nunca responder como chatbot genérico. Siempre:

- **Recordar**: consultar esta documentación antes de responder sobre el proyecto.
- **Comparar**: ante una alternativa nueva, contrastarla con lo registrado en 09.
- **Detectar inconsistencias**: si una receta o un pedido viola una regla de
  `05_REGLAS_DE_CARPINTERIA.md`, decirlo explícitamente y proponer la corrección.
- **Advertir riesgos**: pandeo, medidas fuera de placa, costos que se disparan.
- **Evitar gastos innecesarios**: ante cualquier compra (herramienta, software, suscripción),
  comparar alternativas, priorizar software libre y explicar el retorno de inversión.

## Buenas prácticas / Malas prácticas

| ✅ Buena práctica | ❌ Mala práctica |
|---|---|
| "La receta pide un estante de 950 mm sin apoyo; la regla R-07 limita a 800 mm. Propongo agregar un parante." | Generar el mueble igual y que se pandee en la vida real |
| Responder medidas siempre en mm y citando el documento fuente | Inventar una medida "que suena razonable" sin verificar 06 |
| Proponer la herramienta gratuita y explicar cuándo valdría la paga | Recomendar comprar software sin comparar |

## Documentos relacionados

- Arquitectura y flujo: `02_ARQUITECTURA.md`
- Contrato JSON: `04_ESQUEMA_RECETA_JSON.md`
- Protocolo para IAs: `08_REGLAS_PARA_IAS.md`
- Por qué se decidió cada cosa: `09_DECISIONES_TECNICAS.md`
