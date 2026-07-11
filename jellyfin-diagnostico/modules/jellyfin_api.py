"""
Habla con la API REST de Jellyfin para saber qué está pasando "adentro":
sesiones activas, si está transcodificando, y el historial reciente.

Todas las funciones devuelven un dict con al menos la clave "ok" (bool).
Si algo falla, "ok" es False y "motivo" explica por qué en criollo, para
que el reporte final pueda mostrar "no se pudo verificar: <motivo>" en vez
de reventar.
"""

import requests

TIMEOUT = 8


def _get(url, api_key=None, params=None):
    headers = {}
    if api_key:
        headers["X-Emby-Token"] = api_key
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        return {"ok": True, "data": resp.json()}
    except requests.exceptions.ConnectTimeout:
        return {"ok": False, "motivo": "tiempo de espera agotado conectando al servidor"}
    except requests.exceptions.ConnectionError:
        return {"ok": False, "motivo": "no se pudo conectar (¿está prendido el servidor? ¿la IP es correcta?)"}
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "?"
        if status == 401:
            return {"ok": False, "motivo": "API key inválida o vencida"}
        return {"ok": False, "motivo": f"el servidor respondió con error HTTP {status}"}
    except ValueError:
        return {"ok": False, "motivo": "el servidor respondió algo que no es JSON válido"}
    except Exception as e:
        return {"ok": False, "motivo": f"error inesperado: {e}"}


def check_reachable(base_url):
    """Prueba /System/Info/Public, que no necesita API key. Sirve para
    confirmar que la URL de Jellyfin es correcta antes de pedir la key."""
    return _get(f"{base_url.rstrip('/')}/System/Info/Public")


def get_system_info(base_url, api_key):
    return _get(f"{base_url.rstrip('/')}/System/Info", api_key=api_key)


def _fps_original_del_video(now_playing_item):
    """Busca el framerate del video original entre sus MediaStreams."""
    for stream in now_playing_item.get("MediaStreams", []):
        if stream.get("Type") == "Video" and stream.get("RealFrameRate"):
            return stream["RealFrameRate"]
    return None


def get_sessions(base_url, api_key):
    """Sesiones activas: quién está viendo qué, y si Jellyfin está
    transcodificando (traduciendo el video al vuelo) o mandándolo directo."""
    result = _get(f"{base_url.rstrip('/')}/Sessions", api_key=api_key)
    if not result["ok"]:
        return result

    sesiones = []
    for s in result["data"]:
        info = s.get("TranscodingInfo")
        item = s.get("NowPlayingItem") or {}
        sesion = {
            "usuario": s.get("UserName", "desconocido"),
            "cliente": s.get("Client", "desconocido"),
            "titulo": item.get("Name", "?"),
            "transcodificando": info is not None,
        }
        if info:
            fps_codificados = info.get("Framerate") or 0
            fps_original = _fps_original_del_video(item)
            velocidad_aprox = None
            if fps_codificados and fps_original:
                # Aproximación del "speed factor" que se ve en el panel de
                # Jellyfin (ej. "0.67x"): fps que logra codificar por segundo
                # real dividido los fps que necesita el video para ir fluido.
                # Menor a 1x = el servidor no llega a tiempo => cortes.
                velocidad_aprox = round(fps_codificados / fps_original, 2)
            sesion.update({
                "razon_transcodificacion": info.get("TranscodeReasons", []),
                "framerate_codificacion": fps_codificados,
                "fps_original": fps_original,
                "velocidad_aprox": velocidad_aprox,
                "video_codec": info.get("VideoCodec"),
                "audio_codec": info.get("AudioCodec"),
                "bitrate": info.get("Bitrate"),
                "is_video_direct": info.get("IsVideoDirect"),
                "is_audio_direct": info.get("IsAudioDirect"),
                "container": info.get("Container"),
            })
        sesiones.append(sesion)

    return {"ok": True, "sesiones": sesiones, "cantidad": len(sesiones)}


def get_activity_log(base_url, api_key, limit=20):
    result = _get(
        f"{base_url.rstrip('/')}/System/ActivityLog/Entries",
        api_key=api_key,
        params={"limit": limit},
    )
    if not result["ok"]:
        return result
    entradas = result["data"].get("Items", [])
    return {
        "ok": True,
        "entradas": [
            {"nombre": e.get("Name"), "tipo": e.get("Type"), "fecha": e.get("Date")}
            for e in entradas
        ],
    }


def find_sample_video_item(base_url, api_key):
    """Busca un ítem de video en las librerías para usarlo como muestra en
    la prueba de velocidad de descarga (módulo de red)."""
    result = _get(
        f"{base_url.rstrip('/')}/Items",
        api_key=api_key,
        params={
            "IncludeItemTypes": "Movie,Episode",
            "Recursive": "true",
            "Limit": 1,
            "SortBy": "Random",
        },
    )
    if not result["ok"]:
        return result
    items = result["data"].get("Items", [])
    if not items:
        return {"ok": False, "motivo": "no se encontró ningún video en tus librerías de Jellyfin"}
    item = items[0]
    return {"ok": True, "item_id": item["Id"], "nombre": item.get("Name", "?")}


def analizar_transcodificacion(sesiones_result):
    """Traduce las sesiones activas a un veredicto simple para el reporte."""
    if not sesiones_result["ok"]:
        return {"ok": False, "motivo": sesiones_result["motivo"]}

    activas = sesiones_result["sesiones"]
    transcodificando = [s for s in activas if s["transcodificando"]]

    alertas = []
    lento = False
    for s in transcodificando:
        razones = s.get("razon_transcodificacion", [])
        detalle = f"'{s['titulo']}' ({s['usuario']}) transcodifica"
        if razones:
            detalle += f" por: {', '.join(razones)}"
        velocidad = s.get("velocidad_aprox")
        if velocidad is not None and velocidad < 1.0:
            detalle += f" — va a {velocidad}x tiempo real (más lento de lo necesario, esto causa cortes)"
            lento = True
        alertas.append(detalle)

    return {
        "ok": True,
        "total_sesiones": len(activas),
        "transcodificando": len(transcodificando),
        "direct_play": len(activas) - len(transcodificando),
        "hay_transcodificacion_lenta": lento,
        "alertas": alertas,
    }
