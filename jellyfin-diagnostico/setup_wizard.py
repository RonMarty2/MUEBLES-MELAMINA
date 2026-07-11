#!/usr/bin/env python3
"""
Asistente de configuración. Te hace preguntas simples una por una y arma
config.yaml por vos — no hace falta que edites ningún archivo a mano.

Corré: python setup_wizard.py
"""

import getpass
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules import jellyfin_api, nas_synology  # noqa: E402

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
KEY_PATH_DEFAULT = os.path.expanduser("~/.ssh/id_ed25519_jellyfin_diag")


def preguntar(mensaje, default=None):
    sufijo = f" [{default}]" if default else ""
    respuesta = input(f"{mensaje}{sufijo}: ").strip()
    return respuesta or default


def si_no(mensaje, default_si=True):
    sufijo = " [S/n]" if default_si else " [s/N]"
    respuesta = input(f"{mensaje}{sufijo}: ").strip().lower()
    if not respuesta:
        return default_si
    return respuesta.startswith("s")


def titulo(texto):
    print("\n" + "=" * 60)
    print(texto)
    print("=" * 60)


def paso_jellyfin_url():
    titulo("PASO 1 — ¿Dónde está tu Jellyfin?")
    print("Necesito la dirección de tu servidor, tal como la escribís en el navegador.")
    print("Ejemplo: http://192.168.1.50:8096")
    while True:
        url = preguntar("Dirección de Jellyfin")
        if not url:
            continue
        if "://" not in url:
            url = f"http://{url}"
        print("Probando conexión...")
        resultado = jellyfin_api.check_reachable(url)
        if resultado["ok"]:
            print("✅ ¡Conectado! Jellyfin respondió correctamente.")
            return url
        print(f"❌ No respondió: {resultado['motivo']}")
        if not si_no("¿Querés intentar con otra dirección?"):
            print("Seguimos con esta de todas formas; podés corregirla luego en config.yaml.")
            return url


def paso_api_key(url):
    titulo("PASO 2 — API Key de Jellyfin")
    print("Esto le permite al script leer sesiones activas y el estado del servidor.")
    if not si_no("¿Ya tenés una API Key generada?", default_si=False):
        print("""
Para generarla:
  1. Entrá a Jellyfin desde el navegador con tu usuario administrador.
  2. Anda a: Panel de administración (ícono de engranaje) -> Avanzado -> API Keys.
  3. Tocá el botón "+" (Nueva API Key), ponele un nombre como "diagnostico".
  4. Copiá la clave larga que te muestra (no se vuelve a mostrar completa después).
""")
        input("Presioná Enter cuando la tengas copiada...")

    while True:
        api_key = preguntar("Pegá tu API Key acá")
        print("Probando la key...")
        resultado = jellyfin_api.get_system_info(url, api_key)
        if resultado["ok"]:
            print("✅ API Key válida.")
            return api_key
        print(f"❌ No funcionó: {resultado['motivo']}")
        if not si_no("¿Querés reintentar?"):
            print("Seguimos igual; vas a poder corregirla en config.yaml.")
            return api_key


def paso_ssh(jellyfin_host):
    titulo("PASO 3 — Acceso SSH a tu Synology (opcional pero recomendado)")
    print("Esto permite revisar CPU, RAM, discos (SMART) y procesos del NAS.")
    if not si_no("¿Querés configurar el acceso SSH ahora?"):
        return {"enabled": False, "host": "", "port": 22, "user": "", "key_path": KEY_PATH_DEFAULT}

    print("""
Si nunca activaste SSH en tu Synology:
  1. Abrí DSM (la interfaz web de tu NAS) desde el navegador.
  2. Andá a: Panel de Control -> Terminal y SNMP.
  3. Tildá "Habilitar servicio SSH". Dejá el puerto en 22 (o anotá el que uses).
  4. Aplicar.
""")
    input("Presioná Enter cuando esté activado (o si ya lo estaba)...")

    host = preguntar("IP de tu NAS en la red local", default=jellyfin_host)
    port = int(preguntar("Puerto SSH", default="22"))
    usuario = preguntar("Usuario SSH (el mismo que usás para entrar a DSM, no 'root')")

    print("\n¿Cómo preferís autenticarte?")
    print("  1) Con clave SSH (recomendado: más seguro, no pide contraseña cada vez)")
    print("  2) Con usuario y contraseña (se te va a pedir cada vez que corras el diagnóstico)")
    metodo = preguntar("Elegí 1 o 2", default="1")

    ssh_config = {"enabled": True, "host": host, "port": port, "user": usuario}

    if metodo == "2":
        ssh_config["key_path"] = ""
        ssh_config["auth_method"] = "password_prompt"
        print("\nListo. Cada vez que corras el diagnóstico te va a pedir la contraseña")
        print("(no se guarda en ningún archivo).")
        return ssh_config

    ssh_config["auth_method"] = "key"
    ssh_config["key_path"] = KEY_PATH_DEFAULT
    _configurar_clave_ssh(host, port, usuario)
    return ssh_config


def _configurar_clave_ssh(host, port, usuario):
    if os.path.exists(KEY_PATH_DEFAULT):
        print(f"Ya existe una clave en {KEY_PATH_DEFAULT}, la voy a usar.")
    else:
        print("Generando un par de claves SSH nuevo (no afecta ninguna otra clave que tengas)...")
        subprocess.run(
            ["ssh-keygen", "-t", "ed25519", "-f", KEY_PATH_DEFAULT, "-N", "", "-C", "diagnostico-jellyfin"],
            check=False,
        )

    pub_path = f"{KEY_PATH_DEFAULT}.pub"
    if not os.path.exists(pub_path):
        print("⚠️  No se pudo generar la clave automáticamente. Instalá 'openssh-client' e intentá de nuevo.")
        return

    if shutil.which("ssh-copy-id"):
        print(f"\nIntentando copiar la clave pública al NAS con ssh-copy-id (te va a pedir tu contraseña de {usuario}, una sola vez)...")
        subprocess.run(["ssh-copy-id", "-i", pub_path, "-p", str(port), f"{usuario}@{host}"], check=False)
    else:
        with open(pub_path) as f:
            clave_publica = f.read().strip()
        print(f"""
No encontré 'ssh-copy-id' en este equipo. Hacelo a mano, una sola vez:
  1. Conectate por SSH con contraseña:  ssh -p {port} {usuario}@{host}
  2. Una vez adentro, corré:
       mkdir -p ~/.ssh && chmod 700 ~/.ssh
       echo "{clave_publica}" >> ~/.ssh/authorized_keys
       chmod 600 ~/.ssh/authorized_keys
  3. Salí (exit) y volvé a correr este asistente, o probá directamente el diagnóstico.
""")
        input("Presioná Enter cuando lo hayas hecho...")


def paso_remoto(config_ssh):
    titulo("PASO 4 — Acceso remoto (fuera de tu red)")
    print("Contame cómo accedés a Jellyfin cuando no estás en tu casa.")
    print("  1) Solo uso Jellyfin en mi red local")
    print("  2) Uso Tailscale (VPN) desde el celular u otros dispositivos")
    opcion = preguntar("Elegí 1 o 2", default="2")

    if opcion != "2":
        return {"method": "lan", "tailscale_ip": ""}

    tailscale_ip = ""
    if config_ssh.get("enabled"):
        print("Buscando la IP de Tailscale del NAS por SSH...")
        conexion = nas_synology.conectar(config_ssh)
        if conexion["ok"]:
            cliente = conexion["cliente"]
            codigo, salida, _ = nas_synology.ejecutar_comando(cliente, "tailscale ip -4")
            cliente.close()
            if codigo == 0 and salida.strip():
                tailscale_ip = salida.strip().splitlines()[0]
                print(f"✅ Encontrada: {tailscale_ip}")

    if not tailscale_ip:
        print("""
No la pude detectar sola. La encontrás así:
  - En la app de Tailscale de tu celular, tocá el nombre del NAS: te muestra
    una IP que empieza con "100.".
  - O en https://login.tailscale.com/admin/machines (buscá el nombre de tu NAS).
""")
        tailscale_ip = preguntar("Pegá la IP de Tailscale del NAS (ej: 100.x.x.x)", default="")

    return {"method": "tailscale", "tailscale_ip": tailscale_ip or ""}


def generar_config_yaml(jellyfin_url, api_key, ssh_config, remoto_config):
    contenido = f"""# Generado por setup_wizard.py — podés editarlo a mano si necesitás ajustar algo.

jellyfin:
  url: "{jellyfin_url}"
  api_key: "{api_key or ''}"

ssh:
  enabled: {str(ssh_config.get('enabled', False)).lower()}
  host: "{ssh_config.get('host', '')}"
  port: {ssh_config.get('port', 22)}
  user: "{ssh_config.get('user', '')}"
  auth_method: "{ssh_config.get('auth_method', 'key')}"
  key_path: "{ssh_config.get('key_path', KEY_PATH_DEFAULT)}"

network:
  bitrate_min_mbps: 4
  bitrate_max_mbps: 15

remote_access:
  method: "{remoto_config.get('method', 'lan')}"
  tailscale_ip: "{remoto_config.get('tailscale_ip', '')}"
"""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(contenido)


def main():
    print("Este asistente te va a hacer unas pocas preguntas para armar tu configuración.")
    print("En cualquier momento podés cortar con Ctrl+C y volver a correrlo después.\n")

    if os.path.exists(CONFIG_PATH):
        if not si_no(f"Ya existe {CONFIG_PATH}. ¿Querés sobrescribirlo?", default_si=False):
            print("Cancelado. Tu config.yaml no fue modificado.")
            return

    jellyfin_url = paso_jellyfin_url()
    api_key = paso_api_key(jellyfin_url)

    import urllib.parse
    host = urllib.parse.urlparse(jellyfin_url).hostname
    ssh_config = paso_ssh(host)
    remoto_config = paso_remoto(ssh_config)

    generar_config_yaml(jellyfin_url, api_key, ssh_config, remoto_config)

    titulo("¡Listo!")
    print(f"Se guardó tu configuración en: {CONFIG_PATH}")
    print("Ahora podés correr:  python diagnostico.py --full")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelado por el usuario.")
