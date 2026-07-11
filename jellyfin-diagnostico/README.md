# Diagnóstico Jellyfin

Herramienta para descubrir por qué se corta o tartamudea tu streaming de
Jellyfin (video y música), tanto en tu red local como cuando lo usás desde
afuera con Tailscale. Revisa tu red, tu NAS Synology y la propia
configuración de Jellyfin, y te entrega un reporte con semáforo
(🟢 bien / 🟡 revisar / 🔴 acá está el problema).

No hace falta que sepas de redes ni de Linux: un asistente interactivo te
va guiando paso a paso.

## Instalación

1. Necesitás Python 3.9 o más nuevo instalado en tu PC (no en el NAS).
2. Instalá las dependencias:

   ```bash
   cd jellyfin-diagnostico
   pip install -r requirements.txt
   ```

## Primer uso: el asistente de configuración

Corré esto una sola vez (o cuando cambie algo, como la IP del NAS):

```bash
python setup_wizard.py
```

Te va a preguntar, en orden:

1. **La dirección de tu Jellyfin** (ej. `http://192.168.1.50:8096`) — la prueba automáticamente.
2. **Tu API Key de Jellyfin** — si no tenés una, te dice exactamente dónde
   generarla (Panel de administración → Avanzado → API Keys).
3. **Acceso SSH a tu Synology** (opcional, pero permite revisar CPU, RAM y
   el estado de los discos) — si nunca lo activaste, te indica el paso
   exacto en DSM (Panel de Control → Terminal y SNMP → Habilitar SSH), y
   arma automáticamente una clave de acceso para que no tengas que escribir
   la contraseña cada vez.
4. **Cómo accedés desde afuera de tu casa** — si usás Tailscale, intenta
   detectar la IP del NAS automáticamente por SSH; si no puede, te dice
   dónde encontrarla en la app de Tailscale.

Al final, se genera un archivo `config.yaml` con todo lo que respondiste.
Ese archivo **no se sube a git** (contiene tus credenciales) — está en
`.gitignore`.

Si preferís armar `config.yaml` a mano en vez de usar el asistente, copiá
`config.example.yaml` y completá los campos: está todo comentado.

## Uso diario

Correr todo:

```bash
python diagnostico.py --full
```

Correr solo una parte:

```bash
python diagnostico.py --red        # solo red (ping, velocidad)
python diagnostico.py --disco      # solo NAS (CPU, RAM, discos)
python diagnostico.py --jellyfin   # solo Jellyfin (sesiones, transcodificación)
```

Se pueden combinar, ej. `python diagnostico.py --red --jellyfin`.

Agregá `--html` si además del texto en pantalla querés un reporte HTML
(se guarda junto al log).

El modo (red local vs. Tailscale) se detecta solo. Si te falla la
detección, podés forzarlo con `--local` o `--remote`.

Cada corrida se guarda con fecha y hora en `logs/`, y además se agrega una
fila a `logs/historial.csv` para poder comparar entre distintos días y ver
si un problema es constante o solo pasa en ciertos momentos.

## ¿Qué revisa cada módulo?

- **Red**: ping de 60 segundos (latencia, jitter, % de paquetes
  perdidos), si estás por Wi-Fi o cable, y la velocidad real sostenida
  entre tu dispositivo y el NAS (con `iperf3` si está instalado, o si no,
  descargando un video real desde tu propio Jellyfin y cronometrando).
  Si estás en modo Tailscale y hay SSH configurado, también mide la
  velocidad de **subida** de tu conexión de casa (la que realmente limita
  el streaming hacia afuera).

- **Disco / NAS** (necesita SSH): uso de CPU y RAM, estado S.M.A.R.T. de
  los discos (errores, temperatura, sectores dañados), velocidad de
  lectura secuencial del disco, y si hay procesos pesados corriendo en ese
  momento (backups, escaneos de librería, etc).

- **Jellyfin**: sesiones activas, si están en direct play o
  transcodificando, el motivo de la transcodificación, y si el servidor
  está transcodificando más lento de lo necesario (lo que causa cortes).
  La aceleración de hardware no se puede leer por API, así que el reporte
  te indica dónde revisarla a mano.

## iperf3 (opcional, para medir velocidad de red con más precisión)

Si no lo instalás, la herramienta igual funciona (usa una descarga de
prueba desde Jellyfin como alternativa). Si querés instalarlo:

- **En tu PC/celular con Termux**: `apt install iperf3` (Linux),
  `brew install iperf3` (Mac), o descargalo para Windows desde el sitio
  oficial de iperf3.
- **En el NAS Synology**: no viene instalado de fábrica. Se puede agregar
  vía Entware o un contenedor Docker si tenés Container Manager. Si te
  parece mucho lío, no hace falta: el método alternativo alcanza para
  diagnosticar la mayoría de los casos.

Para probar: en el NAS corré `iperf3 -s`, y en tu PC `iperf3 -c <IP del NAS>`.

## ¿Por qué me pide contraseña / clave SSH?

Solo si configuraste acceso SSH en el asistente. Si elegiste autenticarte
con clave, no te va a volver a pedir nada. Si elegiste usuario y
contraseña, te la va a pedir en cada corrida (nunca se guarda en ningún
archivo).

## Estructura del proyecto

```
config.example.yaml   # plantilla de configuración (comentada)
setup_wizard.py        # asistente interactivo, genera config.yaml
diagnostico.py          # programa principal
modules/
  red.py                # ping, wifi/cable, throughput
  nas_synology.py         # CPU, RAM, SMART, velocidad de disco (por SSH)
  jellyfin_api.py          # sesiones, transcodificación, API de Jellyfin
  remote.py                # detección LAN vs Tailscale, velocidad de subida
  report.py                # semáforo, reporte final, log histórico
logs/                     # se crea solo, con cada corrida
```
