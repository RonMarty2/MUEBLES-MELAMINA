"""
Diagnóstico de red entre el dispositivo donde corrés este script y el
servidor Jellyfin: ping, tipo de conexión (wifi/cable), y velocidad real
sostenida (iperf3 si está disponible, o una descarga de prueba desde el
propio Jellyfin si no).
"""

import platform
import re
import shutil
import subprocess
import time
import urllib.parse

from . import jellyfin_api

SISTEMA = platform.system()  # "Linux", "Windows", "Darwin"


def _extraer_host(url_o_host):
    """Acepta tanto 'http://192.168.1.50:8096' como '192.168.1.50'."""
    if "://" in url_o_host:
        return urllib.parse.urlparse(url_o_host).hostname
    return url_o_host.split(":")[0]


def ping_test(host, duracion_seg=60):
    """Hace ping durante ~60 segundos y devuelve min/max/promedio/jitter/%perdidos.

    Usa el comando `ping` del sistema operativo (no requiere permisos de
    administrador, a diferencia de librerías que arman paquetes ICMP crudos).
    """
    host = _extraer_host(host)
    cantidad = max(duracion_seg, 5)  # ~1 ping por segundo

    if SISTEMA == "Windows":
        cmd = ["ping", "-n", str(cantidad), host]
    else:
        cmd = ["ping", "-c", str(cantidad), "-i", "1", host]

    try:
        resultado = subprocess.run(
            cmd, capture_output=True, text=True, timeout=duracion_seg + 20
        )
    except FileNotFoundError:
        return {"ok": False, "motivo": "el comando 'ping' no está disponible en este sistema"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "motivo": "el ping tardó demasiado y se canceló"}

    salida = resultado.stdout
    return _parsear_ping(salida, cantidad)


def _parsear_ping(salida, cantidad_enviados):
    if SISTEMA == "Windows":
        perdidos_match = re.search(r"\((\d+)% loss\)", salida)
        stats_match = re.search(
            r"Minimum = (\d+)ms, Maximum = (\d+)ms, Average = (\d+)ms", salida
        )
        if not stats_match:
            return {"ok": False, "motivo": "no se pudo interpretar la salida de ping (¿el host respondió alguna vez?)"}
        minimo, maximo, promedio = (int(x) for x in stats_match.groups())
        perdidos_pct = int(perdidos_match.group(1)) if perdidos_match else None
        jitter = None  # Windows no reporta mdev/jitter nativamente
    else:
        perdidos_match = re.search(r"([\d.]+)% packet loss", salida)
        # Linux/Mac: "rtt min/avg/max/mdev = 0.123/0.456/0.789/0.012 ms"
        stats_match = re.search(
            r"[= ]([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)\s*ms", salida
        )
        if not stats_match:
            return {"ok": False, "motivo": "no se pudo interpretar la salida de ping (¿el host respondió alguna vez?)"}
        minimo, promedio, maximo, jitter = (float(x) for x in stats_match.groups())
        perdidos_pct = float(perdidos_match.group(1)) if perdidos_match else None

    return {
        "ok": True,
        "min_ms": minimo,
        "max_ms": maximo,
        "promedio_ms": promedio,
        "jitter_ms": jitter,
        "perdidos_pct": perdidos_pct,
        "muestras_enviadas": cantidad_enviados,
    }


def detectar_tipo_conexion():
    """Intenta averiguar si estás por Wi-Fi o cable. Es "mejor esfuerzo":
    si el SO no da esa info fácil, se reporta como desconocido en vez de
    fallar."""
    try:
        if SISTEMA == "Linux":
            return _detectar_conexion_linux()
        elif SISTEMA == "Darwin":
            return _detectar_conexion_mac()
        elif SISTEMA == "Windows":
            return _detectar_conexion_windows()
    except Exception as e:
        return {"ok": False, "motivo": f"error detectando tipo de conexión: {e}"}
    return {"ok": False, "motivo": "sistema operativo no reconocido"}


def _detectar_conexion_linux():
    import os

    base = "/sys/class/net"
    if not os.path.isdir(base):
        return {"ok": False, "motivo": "no se encontró /sys/class/net"}

    interfaces_activas = []
    for iface in os.listdir(base):
        operstate_path = f"{base}/{iface}/operstate"
        if not os.path.exists(operstate_path):
            continue
        with open(operstate_path) as f:
            estado = f.read().strip()
        if estado == "up" and iface != "lo":
            es_wifi = os.path.isdir(f"{base}/{iface}/wireless")
            interfaces_activas.append((iface, "wifi" if es_wifi else "cable"))

    if not interfaces_activas:
        return {"ok": False, "motivo": "no se encontró ninguna interfaz de red activa"}

    return {"ok": True, "interfaces": interfaces_activas}


def _detectar_conexion_mac():
    salida = subprocess.run(
        ["networksetup", "-listallhardwareports"], capture_output=True, text=True, timeout=10
    ).stdout
    tipo = "wifi" if "Wi-Fi" in salida else "desconocido"
    return {"ok": True, "interfaces": [("principal", tipo)]}


def _detectar_conexion_windows():
    salida = subprocess.run(
        ["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True, timeout=10
    ).stdout
    if "State" in salida and "connected" in salida.lower():
        return {"ok": True, "interfaces": [("wifi", "wifi")]}
    return {"ok": True, "interfaces": [("principal", "cable (probable)")]}


def verificar_iperf3_disponible():
    return shutil.which("iperf3") is not None


def instrucciones_iperf3(nas_host):
    return (
        "iperf3 no está corriendo del lado del servidor. Para medir el throughput\n"
        "real de tu red (no solo la latencia), instalá iperf3 en ambos lados:\n\n"
        f"  En el NAS (por SSH):  ver README, sección iperf3 en Synology\n"
        f"  En tu PC/celular:     instalá iperf3 (choco/brew/apt según tu SO)\n\n"
        f"Después, en el NAS corré:   iperf3 -s\n"
        f"Y en tu PC corré:           iperf3 -c {nas_host}\n\n"
        "Sin esto, la herramienta usa un método alternativo (descarga de prueba\n"
        "desde tu propio Jellyfin) que es menos preciso pero no requiere instalar nada."
    )


def correr_iperf3_cliente(nas_host, duracion_seg=10):
    if not verificar_iperf3_disponible():
        return {"ok": False, "motivo": "iperf3 no está instalado en este equipo"}
    try:
        resultado = subprocess.run(
            ["iperf3", "-c", nas_host, "-t", str(duracion_seg), "-J"],
            capture_output=True, text=True, timeout=duracion_seg + 20,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "motivo": "iperf3 tardó demasiado y se canceló"}

    if resultado.returncode != 0:
        return {
            "ok": False,
            "motivo": "no se pudo conectar al servidor iperf3 en el NAS (¿corriste 'iperf3 -s' allá?)",
        }

    import json
    try:
        datos = json.loads(resultado.stdout)
        mbps = datos["end"]["sum_received"]["bits_per_second"] / 1_000_000
        return {"ok": True, "mbps": round(mbps, 1), "metodo": "iperf3"}
    except (KeyError, json.JSONDecodeError):
        return {"ok": False, "motivo": "no se pudo interpretar la salida de iperf3"}


def medir_throughput_via_jellyfin(base_url, api_key, mb_a_descargar=100):
    """Cuando no hay iperf3: descarga un pedazo de un video real desde
    Jellyfin y mide la velocidad sostenida. Menos preciso que iperf3 (incluye
    la velocidad del disco del NAS, no solo la red) pero no requiere instalar
    nada y prueba el camino real que recorre tu streaming."""
    item = jellyfin_api.find_sample_video_item(base_url, api_key)
    if not item["ok"]:
        return item

    url = f"{base_url.rstrip('/')}/Items/{item['item_id']}/Download"
    headers = {"X-Emby-Token": api_key, "Range": f"bytes=0-{mb_a_descargar * 1024 * 1024}"}

    import requests
    try:
        inicio = time.time()
        bytes_leidos = 0
        with requests.get(url, headers=headers, stream=True, timeout=30) as resp:
            resp.raise_for_status()
            for chunk in resp.iter_content(chunk_size=1024 * 256):
                bytes_leidos += len(chunk)
                if bytes_leidos >= mb_a_descargar * 1024 * 1024:
                    break
        transcurrido = time.time() - inicio
    except Exception as e:
        return {"ok": False, "motivo": f"no se pudo descargar el archivo de prueba: {e}"}

    if transcurrido <= 0:
        return {"ok": False, "motivo": "la descarga fue demasiado rápida para medir con precisión"}

    mbps = (bytes_leidos * 8 / 1_000_000) / transcurrido
    return {
        "ok": True,
        "mbps": round(mbps, 1),
        "metodo": "descarga desde Jellyfin",
        "archivo_muestra": item["nombre"],
        "mb_descargados": round(bytes_leidos / 1024 / 1024, 1),
    }


def evaluar_capacidad_para_streaming(mbps_medidos, bitrate_max_mbps):
    """Compara la velocidad medida contra el bitrate de tus archivos y da
    un veredicto simple, con margen de seguridad de 30% (el streaming real
    tiene picos por encima del bitrate promedio)."""
    margen_seguro = bitrate_max_mbps * 1.3
    if mbps_medidos >= margen_seguro:
        return "verde", f"tu red sostiene {mbps_medidos} Mbps, con margen de sobra para tus archivos de hasta {bitrate_max_mbps} Mbps"
    elif mbps_medidos >= bitrate_max_mbps:
        return "amarillo", f"tu red sostiene {mbps_medidos} Mbps, justo por encima de tus {bitrate_max_mbps} Mbps — puede cortarse en los picos de bitrate"
    else:
        return "rojo", f"tu red solo sostiene {mbps_medidos} Mbps, por debajo de los {bitrate_max_mbps} Mbps que necesitan tus archivos — esta es una causa probable de los cortes"
