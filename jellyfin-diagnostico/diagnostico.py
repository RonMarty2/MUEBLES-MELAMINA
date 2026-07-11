#!/usr/bin/env python3
"""
Diagnóstico automatizado de por qué se corta/tartamudea Jellyfin: revisa
red, NAS y la propia API de Jellyfin, y arma un reporte con semáforo.

Uso:
    python diagnostico.py --full          (todo)
    python diagnostico.py --red           (solo red)
    python diagnostico.py --disco         (solo NAS/disco)
    python diagnostico.py --jellyfin      (solo Jellyfin)

Se pueden combinar flags, ej: --red --jellyfin
Agregá --remote o --local para forzar el modo si la detección automática
se equivoca.
"""

import argparse
import os
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules import jellyfin_api, nas_synology, red, remote, report  # noqa: E402

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")


def cargar_config():
    if not os.path.exists(CONFIG_PATH):
        print("No se encontró config.yaml. Corré primero:  python setup_wizard.py")
        sys.exit(1)
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def peor_color(colores):
    prioridad = {"rojo": 3, "amarillo": 2, "gris": 1, "verde": 0}
    return max(colores, key=lambda c: prioridad.get(c, 0)) if colores else "gris"


def diagnostico_red(config, modo, host_efectivo):
    print("\n🔎 Revisando la red...")
    detalles, recomendaciones, colores = [], [], []

    ping = red.ping_test(host_efectivo, duracion_seg=60)
    if ping["ok"]:
        detalles.append(
            f"Ping: mín {ping['min_ms']}ms / prom {ping['promedio_ms']}ms / máx {ping['max_ms']}ms, "
            f"{ping['perdidos_pct']}% paquetes perdidos"
        )
        if ping["perdidos_pct"] and ping["perdidos_pct"] > 2:
            colores.append("rojo")
            recomendaciones.append("Estás perdiendo paquetes de red — revisá cableado, señal Wi-Fi o interferencia.")
        elif ping["jitter_ms"] and ping["jitter_ms"] > 20:
            colores.append("amarillo")
            recomendaciones.append("El jitter es alto (conexión inestable) — probá acercar el router o usar cable.")
        else:
            colores.append("verde")
    else:
        detalles.append(f"Ping: no se pudo verificar ({ping['motivo']})")
        colores.append("gris")

    conexion = red.detectar_tipo_conexion()
    if conexion["ok"]:
        tipos = ", ".join(f"{iface} ({tipo})" for iface, tipo in conexion["interfaces"])
        detalles.append(f"Tu conexión: {tipos}")
        if any(tipo == "wifi" for _, tipo in conexion["interfaces"]):
            recomendaciones.append("Estás por Wi-Fi: si podés, usá cable Ethernet para el dispositivo que reproduce.")
    else:
        detalles.append(f"Tipo de conexión: no se pudo verificar ({conexion['motivo']})")

    bitrate_max = config["network"]["bitrate_max_mbps"]

    if red.verificar_iperf3_disponible():
        resultado_throughput = red.correr_iperf3_cliente(host_efectivo)
        if not resultado_throughput["ok"]:
            detalles.append(f"iperf3: {resultado_throughput['motivo']}")
            print(red.instrucciones_iperf3(host_efectivo))
            resultado_throughput = red.medir_throughput_via_jellyfin(config["jellyfin"]["url"], config["jellyfin"]["api_key"])
    else:
        resultado_throughput = red.medir_throughput_via_jellyfin(config["jellyfin"]["url"], config["jellyfin"]["api_key"])

    if resultado_throughput["ok"]:
        color_tp, mensaje_tp = red.evaluar_capacidad_para_streaming(resultado_throughput["mbps"], bitrate_max)
        detalles.append(f"Velocidad medida ({resultado_throughput['metodo']}): {mensaje_tp}")
        colores.append(color_tp)
    else:
        detalles.append(f"Velocidad sostenida: no se pudo medir ({resultado_throughput['motivo']})")
        colores.append("gris")

    if modo == "tailscale" and config.get("ssh", {}).get("enabled"):
        subida = remote.medir_subida_desde_nas(config["ssh"])
        if subida["ok"]:
            color_subida, mensaje_subida = remote.evaluar_subida(subida["subida_mbps"], bitrate_max)
            detalles.append(f"Subida de tu conexión de casa (medida desde el NAS): {mensaje_subida}")
            colores.append(color_subida)
        else:
            detalles.append(f"Subida desde casa: no se pudo medir ({subida['motivo']})")

    return {"nombre": "Red", "color": peor_color(colores), "detalles": detalles, "recomendaciones": recomendaciones}


def diagnostico_disco(config):
    print("\n🔎 Revisando el NAS...")
    detalles, recomendaciones, colores = [], [], []
    ssh_config = config.get("ssh", {})

    conexion = nas_synology.conectar(ssh_config)
    if not conexion["ok"]:
        detalles.append(f"No se pudo verificar el NAS por SSH: {conexion['motivo']}")
        return {"nombre": "Disco / NAS", "color": "gris", "detalles": detalles, "recomendaciones": recomendaciones}

    cliente = conexion["cliente"]
    try:
        cpu_ram = nas_synology.obtener_cpu_ram(cliente)
        if cpu_ram["ok"]:
            detalles.append(
                f"Carga de CPU (1 min): {cpu_ram['carga_1min']} | RAM usada: {cpu_ram['ram_usada_pct']}% de {cpu_ram['ram_total_mb']:.0f} MB"
            )
            if cpu_ram["ram_usada_pct"] and cpu_ram["ram_usada_pct"] > 90:
                colores.append("amarillo")
                recomendaciones.append("La RAM del NAS está casi al límite — cerrá apps/paquetes que no uses en el NAS.")
            else:
                colores.append("verde")
        else:
            detalles.append(f"CPU/RAM: no se pudo verificar ({cpu_ram['motivo']})")
            colores.append("gris")

        smart = nas_synology.obtener_smart_status(cliente)
        if smart["ok"]:
            for disco, info in smart["discos"].items():
                if not info["ok"]:
                    detalles.append(f"SMART {disco}: no se pudo verificar ({info['motivo']})")
                    colores.append("gris")
                    continue
                detalles.append(
                    f"SMART {disco}: salud {info['salud']}, temp {info['temperatura_c']}°C, "
                    f"sectores reasignados: {info['sectores_reasignados']}, pendientes: {info['sectores_pendientes']}"
                )
                if info["salud"] not in ("PASSED", "OK") or (info["sectores_reasignados"] or 0) > 0 or (info["sectores_pendientes"] or 0) > 0:
                    colores.append("rojo")
                    recomendaciones.append(f"El disco {disco} tiene señales de fallo (SMART) — hacé backup y considerá reemplazarlo.")
                elif info["temperatura_c"] and info["temperatura_c"] > 50:
                    colores.append("amarillo")
                    recomendaciones.append(f"El disco {disco} está caliente ({info['temperatura_c']}°C) — revisá la ventilación del NAS.")
                else:
                    colores.append("verde")
        else:
            detalles.append(f"SMART: no se pudo verificar ({smart['motivo']})")
            colores.append("gris")

        velocidad = nas_synology.medir_velocidad_lectura(cliente)
        bitrate_max_MBps = config["network"]["bitrate_max_mbps"] / 8
        if velocidad["ok"]:
            detalles.append(f"Velocidad de lectura secuencial de {velocidad['disco']}: {velocidad['mb_por_seg']:.0f} MB/s")
            if velocidad["mb_por_seg"] < bitrate_max_MBps * 3:
                colores.append("rojo")
                recomendaciones.append("El disco lee muy lento para streaming — revisá su estado o si hay procesos compitiendo por el disco.")
            else:
                colores.append("verde")
        else:
            detalles.append(f"Velocidad de disco: no se pudo verificar ({velocidad['motivo']})")
            colores.append("gris")

        procesos = nas_synology.procesos_pesados(cliente)
        if procesos["ok"] and procesos["sospechosos_conocidos"]:
            nombres = ", ".join(p["comando"] for p in procesos["sospechosos_conocidos"][:5])
            detalles.append(f"Procesos pesados corriendo ahora: {nombres}")
            colores.append("amarillo")
            recomendaciones.append("Hay backups/escaneos corriendo a la vez — reprogramalos fuera del horario en que ves contenido.")
        elif procesos["ok"]:
            detalles.append("No se detectaron procesos pesados conocidos corriendo en este momento.")
    finally:
        cliente.close()

    return {"nombre": "Disco / NAS", "color": peor_color(colores), "detalles": detalles, "recomendaciones": recomendaciones}


def diagnostico_jellyfin(config):
    print("\n🔎 Revisando Jellyfin...")
    detalles, recomendaciones, colores = [], [], []
    url, api_key = config["jellyfin"]["url"], config["jellyfin"]["api_key"]

    sesiones = jellyfin_api.get_sessions(url, api_key)
    analisis = jellyfin_api.analizar_transcodificacion(sesiones)
    if analisis["ok"]:
        detalles.append(
            f"Sesiones activas: {analisis['total_sesiones']} (direct play: {analisis['direct_play']}, transcodificando: {analisis['transcodificando']})"
        )
        for alerta in analisis["alertas"]:
            detalles.append(f"  {alerta}")
        if analisis["hay_transcodificacion_lenta"]:
            colores.append("rojo")
            recomendaciones.append("El servidor no llega a transcodificar en tiempo real — activá aceleración de hardware o bajá el bitrate máximo permitido en el cliente.")
        elif analisis["transcodificando"] > 0:
            colores.append("amarillo")
            recomendaciones.append("Hay transcodificación activa. Revisá el motivo arriba: si es 'bitrate excede el límite', subí el límite de bitrate remoto en el cliente (Jellyfin app -> Configuración de reproducción).")
        else:
            colores.append("verde")
    else:
        detalles.append(f"Sesiones: no se pudo verificar ({analisis['motivo']})")
        colores.append("gris")

    detalles.append(
        "Aceleración de hardware: no se puede confirmar por API. Revisá manualmente en "
        "Panel de administración -> Reproducción -> Aceleración de hardware de transcodificación."
    )

    return {"nombre": "Jellyfin / Transcodificación", "color": peor_color(colores), "detalles": detalles, "recomendaciones": recomendaciones}


def main():
    parser = argparse.ArgumentParser(description="Diagnóstico de cortes en Jellyfin")
    parser.add_argument("--full", action="store_true", help="Corre todos los módulos")
    parser.add_argument("--red", action="store_true", help="Solo diagnóstico de red")
    parser.add_argument("--disco", action="store_true", help="Solo diagnóstico de NAS/disco")
    parser.add_argument("--jellyfin", action="store_true", help="Solo diagnóstico de Jellyfin")
    parser.add_argument("--remote", action="store_true", help="Forzar modo remoto (Tailscale)")
    parser.add_argument("--local", action="store_true", help="Forzar modo local (LAN)")
    parser.add_argument("--html", action="store_true", help="Además del texto, genera un reporte HTML")
    args = parser.parse_args()

    correr_todo = args.full or not (args.red or args.disco or args.jellyfin)
    config = cargar_config()

    if args.remote:
        modo, host_efectivo = "tailscale", config.get("remote_access", {}).get("tailscale_ip") or config["jellyfin"]["url"]
    elif args.local:
        import urllib.parse
        modo, host_efectivo = "lan", urllib.parse.urlparse(config["jellyfin"]["url"]).hostname
    else:
        deteccion = remote.detectar_modo(config)
        if deteccion["ok"]:
            modo, host_efectivo = deteccion["modo"], deteccion["host_efectivo"]
            print(f"Modo detectado: {modo} (probando contra {host_efectivo})")
        else:
            print(f"No se pudo determinar el modo de red automáticamente: {deteccion['motivo']}")
            import urllib.parse
            modo, host_efectivo = "lan", urllib.parse.urlparse(config["jellyfin"]["url"]).hostname

    categorias = []
    if correr_todo or args.red:
        categorias.append(diagnostico_red(config, modo, host_efectivo))
    if correr_todo or args.disco:
        categorias.append(diagnostico_disco(config))
    if correr_todo or args.jellyfin:
        categorias.append(diagnostico_jellyfin(config))

    meta = {"fecha": __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "modo": modo}
    texto = report.generar_reporte_texto(categorias, meta)
    print("\n" + texto)

    ruta_log = report.guardar_log(texto, categorias, LOGS_DIR)
    print(f"Log guardado en: {ruta_log}")

    if args.html:
        ruta_html = ruta_log.replace(".txt", ".html")
        with open(ruta_html, "w", encoding="utf-8") as f:
            f.write(report.generar_reporte_html(categorias, meta))
        print(f"Reporte HTML guardado en: {ruta_html}")


if __name__ == "__main__":
    main()
