"""Cliente de IA: convierte texto del usuario en recetas JSON.

Frontera de módulo (02_ARQUITECTURA.md): habla con el proveedor configurado
y devuelve una receta cruda (dict). NO valida (eso es validador.py) ni
calcula nada. El protocolo completo está en 08_REGLAS_PARA_IAS.md.

Proveedores (config.json):
- "lmstudio": servidor local de LM Studio (API compatible OpenAI). Gratis.
- "openai":   API de OpenAI (requiere clave).
- "anthropic": API de Anthropic/Claude (requiere clave; formato propio).

Sin dependencias externas: usa urllib de la biblioteca estándar.
"""

import json
import urllib.request
import urllib.error

# Mantener sincronizado con 08_REGLAS_PARA_IAS.md (system prompt oficial v1).
SYSTEM_PROMPT = """Sos el asistente de diseño de un software de muebles de melamina. Tu única salida válida
es una receta JSON que cumpla el esquema versión 1.0.

REGLAS ESTRICTAS:
1. Respondé SOLO con el JSON de la receta, sin texto antes ni después, sin ```.
2. Medidas en milímetros, números enteros.
3. Elegí tipo_mueble según el pedido: "escritorio_gamer" o "ropero".
4. Campos permitidos, defectos y límites POR TIPO:

   escritorio_gamer:
   - dimensiones: ancho 900-2400 (defecto 1600), profundidad 500-900 (defecto 700),
     alto 700-800 (defecto 750)
   - tapa.tipo: "auto" | "simple_18" | "doble_18" | "simple_25" (defecto "auto")
   - material: color (texto, defecto "Blanco"), espesor 15|18 (defecto 18),
     espesor_fondo 3 (defecto 3)
   - cajonera: posicion "derecha"|"izquierda"|"ninguna" (defecto "derecha"),
     ancho 300-600 (defecto 400), cantidad_cajones 1-4 (defecto 3)
   - soporte_cpu: incluir true|false (defecto true), ancho 200-350 (defecto 250)
   - pasacables: cantidad 0-4 (defecto 2), diametro 60|80 (defecto 60)
   - elevacion_monitor: incluir true|false (defecto false), ancho 500-1200 (defecto 800),
     profundidad 200-350 (defecto 250)
   - forma: tipo "recto"|"L" (defecto "recto"), lado "derecha"|"izquierda",
     largo_retorno 600-1600 (defecto 1000), profundidad_retorno 400-700 (defecto 500).
     "Escritorio en L" -> tipo "L" (R-31); el retorno es un módulo con patas propias.

   ropero:
   - dimensiones: ancho TOTAL 600-3600 (defecto 900), profundidad 550-620 (defecto 580),
     alto 2000-2600 (defecto 2400)
   - cuerpos: cantidad 1-3 (defecto 1). Cada cuerpo debe quedar entre 600 y 1200 de ancho
     (R-30). "Ropero de dos cuerpos" -> cantidad 2. Si piden más de 1200 de ancho total,
     elegí la cantidad de cuerpos que deje cada cuerpo en rango.
   - material: color (texto, defecto "Blanco")
   - puertas: tipo "batiente"|"corrediza"|"ninguna" (defecto "batiente"),
     cantidad 2-4 (defecto 2; con cuerpos>1 las batientes son 2 por cuerpo automáticas)
   - cajones: incluir true|false (defecto false), ancho 300-600 (defecto 400),
     cantidad_cajones 1-4 (defecto 3)
   - estante_inferior: incluir true|false (defecto false)

   Común a ambos tipos:
   - uniones.tipo: "confirmat"|"excentrica" (defecto "confirmat"; usar "excentrica" si
     el usuario menciona que va a mover/mudar el mueble)

5. Si el usuario pide un valor fuera de rango, usá el límite más cercano.
6. Si el usuario pide algo que estos campos no cubren (ej. una forma en U, una mesa,
   un mueble de TV), NO inventes campos ni tipo_mueble: emití la receta más parecida
   que sí se pueda con lo existente.
7. Si te doy una receta anterior y un pedido de cambio, devolvé la receta COMPLETA con
   solo los campos afectados modificados.
8. Siempre incluí "version": "1.0" y "tipo_mueble".
"""


class ErrorIA(Exception):
    """Problemas de conexión o de respuesta del proveedor de IA."""


def extraer_json(texto):
    """Tolera modelos que desobedecen y envuelven el JSON en ``` o lo explican:
    toma del primer '{' al último '}' (ver 08, malas prácticas típicas)."""
    inicio = texto.find("{")
    fin = texto.rfind("}")
    if inicio == -1 or fin <= inicio:
        raise ErrorIA(
            "La IA no devolvió JSON. Respuesta recibida:\n" + texto[:400])
    try:
        return json.loads(texto[inicio:fin + 1])
    except json.JSONDecodeError as e:
        raise ErrorIA(f"La IA devolvió JSON mal formado ({e}). "
                      f"Texto:\n{texto[inicio:fin + 1][:400]}")


def _post(url, cuerpo, cabeceras, timeout=120):
    datos = json.dumps(cuerpo).encode("utf-8")
    pedido = urllib.request.Request(url, data=datos, headers=cabeceras, method="POST")
    try:
        with urllib.request.urlopen(pedido, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        raise ErrorIA(
            f"No pude conectar con la IA en {url}: {e}.\n"
            "Si usás LM Studio: abrilo, cargá un modelo y activá el servidor "
            "(pestaña 'Developer' → Start Server). También podés trabajar sin IA: "
            "python main.py --receta archivo.json")


def pedir_receta(config, pedido_usuario, receta_anterior=None):
    """Devuelve la receta cruda (dict) que propuso la IA para el pedido."""
    proveedor = config.get("proveedor", "lmstudio")
    url = config.get("url", "http://localhost:1234/v1")
    modelo = config.get("modelo", "")
    clave = config.get("api_key", "lm-studio")

    contenido = pedido_usuario
    if receta_anterior:
        contenido = (
            "Receta actual:\n" + json.dumps(receta_anterior, ensure_ascii=False)
            + "\n\nPedido de cambio del usuario: " + pedido_usuario
        )

    if proveedor == "anthropic":
        respuesta = _post(
            url.rstrip("/") + "/messages",
            {
                "model": modelo,
                "max_tokens": 1024,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": contenido}],
            },
            {
                "Content-Type": "application/json",
                "x-api-key": clave,
                "anthropic-version": "2023-06-01",
            },
        )
        texto = respuesta["content"][0]["text"]
    else:  # lmstudio y openai comparten protocolo
        respuesta = _post(
            url.rstrip("/") + "/chat/completions",
            {
                "model": modelo,
                "temperature": 0.2,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": contenido},
                ],
            },
            {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {clave}",
            },
        )
        texto = respuesta["choices"][0]["message"]["content"]

    return extraer_json(texto)


def pedir_receta_con_reintentos(config, pedido_usuario, validar_fn,
                                receta_anterior=None, max_reintentos=2):
    """Protocolo de 08: si la validación falla, se reenvía el error a la IA
    para que corrija. validar_fn(receta_cruda) -> (receta, avisos) o lanza."""
    pedido = pedido_usuario
    ultima_receta = None
    ultimo_error = None
    for intento in range(1 + max_reintentos):
        receta_cruda = pedir_receta(config, pedido, receta_anterior)
        ultima_receta = receta_cruda
        try:
            return validar_fn(receta_cruda)
        except Exception as e:  # RecetaInvalida
            ultimo_error = e
            pedido = (
                pedido_usuario
                + "\n\nTu receta anterior tenía estos errores; corregila:\n" + str(e)
            )
            receta_anterior = receta_cruda
    raise ErrorIA(
        f"La IA no logró una receta válida tras {max_reintentos + 1} intentos.\n"
        f"Últimos errores:\n{ultimo_error}\n\n"
        "Última receta (podés corregirla a mano y usar --receta):\n"
        + json.dumps(ultima_receta, indent=2, ensure_ascii=False))
