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
3. Campos permitidos, defectos y límites:
   - tipo_mueble: "escritorio_gamer" (único tipo disponible)
   - dimensiones: ancho 900-2400 (defecto 1600), profundidad 500-900 (defecto 700),
     alto 700-800 (defecto 750)
   - tapa.tipo: "simple_18" | "doble_18" | "simple_25" (defecto "doble_18")
   - material: color (texto, defecto "Blanco"), espesor 15|18 (defecto 18),
     espesor_fondo 3 (defecto 3)
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
