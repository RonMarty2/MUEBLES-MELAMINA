"""
Decide si la prueba se está corriendo desde tu red local o desde afuera
(vía Tailscale), y ajusta el diagnóstico de red en consecuencia: el cuello
de botella cuando estás afuera casi siempre es la velocidad de SUBIDA de tu
conexión de casa (la que sube el video hacia vos), no la de tu celular.
"""

from . import nas_synology


def detectar_modo(config):
    """Prueba primero la IP local del NAS; si no responde, prueba la IP de
    Tailscale (si está configurada). Devuelve el modo y el host a usar para
    el resto de las pruebas de red."""
    jellyfin_url = config["jellyfin"]["url"]
    host_lan = _host_de_url(jellyfin_url)

    if _responde_http(jellyfin_url):
        return {"ok": True, "modo": "lan", "host_efectivo": host_lan}

    tailscale_ip = config.get("remote_access", {}).get("tailscale_ip")
    if tailscale_ip:
        url_tailscale = jellyfin_url.replace(host_lan, tailscale_ip)
        if _responde_http(url_tailscale):
            return {"ok": True, "modo": "tailscale", "host_efectivo": tailscale_ip}
        return {
            "ok": False,
            "motivo": "no respondió ni la IP local ni la IP de Tailscale — revisá que Jellyfin y Tailscale estén activos",
        }

    return {
        "ok": False,
        "motivo": "no respondió la IP local y no hay IP de Tailscale configurada en config.yaml",
    }


def _host_de_url(url):
    import urllib.parse
    return urllib.parse.urlparse(url).hostname


def _responde_http(url, timeout=4):
    try:
        import requests
        requests.get(f"{url.rstrip('/')}/System/Info/Public", timeout=timeout)
        return True
    except Exception:
        return False


def medir_subida_desde_nas(ssh_config):
    """Corre speedtest-cli DESDE el NAS (por SSH), no desde tu celular.
    La velocidad de subida real que importa para streaming remoto es la de
    tu conexión de casa, no la del lugar donde estás viendo el contenido."""
    conexion = nas_synology.conectar(ssh_config)
    if not conexion["ok"]:
        return conexion

    cliente = conexion["cliente"]
    try:
        codigo, salida, error = nas_synology.ejecutar_comando(
            cliente, "speedtest-cli --simple 2>/dev/null || python3 -m speedtest --simple 2>/dev/null"
        )
        if codigo != 0 or not salida.strip():
            return {
                "ok": False,
                "motivo": (
                    "speedtest-cli no está instalado en el NAS. Para medir la subida real de tu "
                    "conexión de casa, instalalo (ver README) o corré manualmente un test de "
                    "velocidad desde una PC conectada por cable en la misma red que el NAS."
                ),
            }

        subida_match = _buscar_linea(salida, "Upload")
        bajada_match = _buscar_linea(salida, "Download")
        return {
            "ok": True,
            "subida_mbps": subida_match,
            "bajada_mbps": bajada_match,
        }
    finally:
        cliente.close()


def _buscar_linea(salida, etiqueta):
    for linea in salida.splitlines():
        if linea.startswith(etiqueta):
            try:
                return float(linea.split(":")[1].strip().split()[0])
            except (IndexError, ValueError):
                return None
    return None


def evaluar_subida(subida_mbps, bitrate_max_mbps):
    if subida_mbps is None:
        return "amarillo", "no se pudo medir la velocidad de subida de tu casa"
    margen_seguro = bitrate_max_mbps * 1.3
    if subida_mbps >= margen_seguro:
        return "verde", f"tu conexión de casa sube a {subida_mbps} Mbps, de sobra para streaming remoto de hasta {bitrate_max_mbps} Mbps"
    elif subida_mbps >= bitrate_max_mbps:
        return "amarillo", f"tu conexión de casa sube a {subida_mbps} Mbps, justo en el límite — puede cortarse con archivos pesados"
    else:
        return "rojo", f"tu conexión de casa solo sube a {subida_mbps} Mbps — no alcanza para tus archivos de hasta {bitrate_max_mbps} Mbps, esta es la causa más probable de los cortes cuando ves contenido fuera de casa"
