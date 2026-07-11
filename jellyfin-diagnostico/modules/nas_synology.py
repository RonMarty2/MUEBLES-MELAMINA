"""
Diagnóstico del NAS Synology por SSH: CPU/RAM, salud de los discos (SMART),
velocidad de lectura del disco, y si hay procesos pesados corriendo al
mismo tiempo que Jellyfin (backups, escaneos, etc).

Si no hay acceso SSH configurado, cada función se salta y el reporte final
lo indica en vez de fallar.
"""

import re

try:
    import paramiko
    PARAMIKO_DISPONIBLE = True
except ImportError:
    PARAMIKO_DISPONIBLE = False


def conectar(ssh_config):
    """Abre una conexión SSH usando los datos de config.yaml. Devuelve
    {"ok": True, "cliente": <SSHClient>} o {"ok": False, "motivo": ...}."""
    if not PARAMIKO_DISPONIBLE:
        return {"ok": False, "motivo": "falta instalar la librería paramiko (pip install paramiko)"}

    if not ssh_config.get("enabled"):
        return {"ok": False, "motivo": "acceso SSH no configurado (corré setup_wizard.py)"}

    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        if ssh_config.get("auth_method") == "password_prompt":
            import getpass
            contrasena = getpass.getpass(f"Contraseña SSH para {ssh_config['user']}@{ssh_config['host']}: ")
            cliente.connect(
                hostname=ssh_config["host"],
                port=ssh_config.get("port", 22),
                username=ssh_config["user"],
                password=contrasena,
                timeout=10,
            )
        else:
            cliente.connect(
                hostname=ssh_config["host"],
                port=ssh_config.get("port", 22),
                username=ssh_config["user"],
                key_filename=_expandir(ssh_config.get("key_path")),
                timeout=10,
            )
        return {"ok": True, "cliente": cliente}
    except paramiko.AuthenticationException:
        return {"ok": False, "motivo": "usuario/clave SSH rechazados por el NAS"}
    except Exception as e:
        return {"ok": False, "motivo": f"no se pudo conectar por SSH: {e}"}


def _expandir(ruta):
    import os
    return os.path.expanduser(ruta) if ruta else None


def ejecutar_comando(cliente, comando, con_sudo=False):
    cmd_final = f"sudo -n {comando}" if con_sudo else comando
    stdin, stdout, stderr = cliente.exec_command(cmd_final, timeout=20)
    salida = stdout.read().decode(errors="ignore")
    error = stderr.read().decode(errors="ignore")
    codigo = stdout.channel.recv_exit_status()
    return codigo, salida, error


def obtener_cpu_ram(cliente):
    """Usa /proc directamente en vez de 'top', porque el busybox top de
    DSM varía mucho de formato entre versiones y /proc es estable."""
    try:
        codigo, salida_load, _ = ejecutar_comando(cliente, "cat /proc/loadavg")
        codigo2, salida_mem, _ = ejecutar_comando(cliente, "cat /proc/meminfo")
        if codigo != 0 or codigo2 != 0:
            return {"ok": False, "motivo": "no se pudo leer /proc en el NAS"}

        carga_1min = float(salida_load.split()[0])

        mem = {}
        for linea in salida_mem.splitlines():
            m = re.match(r"(\w+):\s+(\d+)\s*kB", linea)
            if m:
                mem[m.group(1)] = int(m.group(2))

        total_kb = mem.get("MemTotal", 0)
        disponible_kb = mem.get("MemAvailable", mem.get("MemFree", 0))
        usado_pct = round((1 - disponible_kb / total_kb) * 100, 1) if total_kb else None

        return {
            "ok": True,
            "carga_1min": carga_1min,
            "ram_total_mb": round(total_kb / 1024, 0),
            "ram_usada_pct": usado_pct,
        }
    except Exception as e:
        return {"ok": False, "motivo": f"error leyendo CPU/RAM: {e}"}


def listar_discos(cliente):
    codigo, salida, error = ejecutar_comando(cliente, "lsblk -d -n -o NAME,TYPE 2>/dev/null")
    if codigo != 0 or not salida.strip():
        return {"ok": False, "motivo": f"no se pudo listar discos con lsblk: {error.strip() or 'sin salida'}"}
    discos = []
    for linea in salida.splitlines():
        partes = linea.split()
        if len(partes) == 2 and partes[1] == "disk":
            discos.append(f"/dev/{partes[0]}")
    if not discos:
        return {"ok": False, "motivo": "lsblk no reportó discos físicos"}
    return {"ok": True, "discos": discos}


def obtener_smart_status(cliente):
    """Intenta smartctl directo, y si falla por permisos, con sudo no
    interactivo. En muchos Synology el usuario admin necesita sudo (o
    directamente smartctl no está disponible sin instalar paquetes extra
    desde Package Center / Entware)."""
    discos_result = listar_discos(cliente)
    if not discos_result["ok"]:
        return discos_result

    reportes = {}
    for disco in discos_result["discos"]:
        reportes[disco] = _smart_de_un_disco(cliente, disco)

    return {"ok": True, "discos": reportes}


def _smart_de_un_disco(cliente, disco):
    for con_sudo in (False, True):
        codigo, salida, error = ejecutar_comando(cliente, f"smartctl -a {disco}", con_sudo=con_sudo)
        if codigo == 0 and salida.strip():
            return _parsear_smart(salida)
        if "not found" in error.lower() or "command not found" in error.lower():
            return {"ok": False, "motivo": "smartctl no está instalado en este NAS"}

    return {
        "ok": False,
        "motivo": "sin permisos para leer SMART (probá 'sudo smartctl -a %s' manualmente por SSH y revisá la config de sudo)" % disco,
    }


def _parsear_smart(salida):
    salud_match = re.search(r"SMART overall-health self-assessment test result:\s*(\w+)", salida)
    temp_match = re.search(r"Temperature_Celsius.*?(\d+)\s*$", salida, re.MULTILINE)
    reasignados_match = re.search(r"Reallocated_Sector_Ct.*?(\d+)\s*$", salida, re.MULTILINE)
    pendientes_match = re.search(r"Current_Pending_Sector.*?(\d+)\s*$", salida, re.MULTILINE)

    return {
        "ok": True,
        "salud": salud_match.group(1) if salud_match else "desconocida",
        "temperatura_c": int(temp_match.group(1)) if temp_match else None,
        "sectores_reasignados": int(reasignados_match.group(1)) if reasignados_match else None,
        "sectores_pendientes": int(pendientes_match.group(1)) if pendientes_match else None,
    }


def medir_velocidad_lectura(cliente, disco=None):
    """Lectura secuencial de prueba con dd (solo lectura, no toca datos).
    Si no se especifica disco, usa el primero que encuentre."""
    if disco is None:
        discos_result = listar_discos(cliente)
        if not discos_result["ok"]:
            return discos_result
        disco = discos_result["discos"][0]

    comando = f"dd if={disco} of=/dev/null bs=1M count=1024 2>&1"
    for con_sudo in (False, True):
        codigo, salida, _ = ejecutar_comando(cliente, comando, con_sudo=con_sudo)
        if codigo == 0 and salida.strip():
            velocidad = _parsear_velocidad_dd(salida)
            if velocidad:
                return {"ok": True, "disco": disco, "mb_por_seg": velocidad}

    return {"ok": False, "motivo": f"no se pudo medir velocidad de {disco} (sin permisos o dd no disponible)"}


def _parsear_velocidad_dd(salida):
    # GNU dd: "... copied, 2.3 s, 456 MB/s"   |   busybox dd: puede variar
    m = re.search(r",\s*([\d.]+)\s*s,\s*([\d.]+)\s*([MG])B/s", salida)
    if not m:
        return None
    valor = float(m.group(2))
    unidad = m.group(3)
    return valor * 1024 if unidad == "G" else valor


def procesos_pesados(cliente, umbral_cpu_pct=20):
    """Lista procesos que estén usando bastante CPU al momento de la
    prueba: si hay un backup o un escaneo de librería corriendo a la vez
    que ves algo en Jellyfin, ahí puede estar el cuello de botella."""
    codigo, salida, error = ejecutar_comando(cliente, "ps aux 2>/dev/null || ps -ef")
    if codigo != 0 or not salida.strip():
        return {"ok": False, "motivo": f"no se pudo ejecutar ps: {error.strip() or 'sin salida'}"}

    procesos = []
    lineas = salida.splitlines()[1:]  # saltar encabezado
    for linea in lineas:
        campos = linea.split(None, 10)
        if len(campos) < 11:
            continue
        try:
            cpu_pct = float(campos[2])
        except ValueError:
            continue
        if cpu_pct >= umbral_cpu_pct:
            procesos.append({"comando": campos[10][:80], "cpu_pct": cpu_pct})

    procesos.sort(key=lambda p: p["cpu_pct"], reverse=True)

    palabras_clave_conocidas = [
        "ffmpeg", "hyperbackup", "rsync", "synoindexd", "synocloudsyncd",
        "surveillance", "cloudsync", "backup",
    ]
    sospechosos = [
        p for p in procesos
        if any(palabra in p["comando"].lower() for palabra in palabras_clave_conocidas)
    ]

    return {"ok": True, "procesos_pesados": procesos, "sospechosos_conocidos": sospechosos}
