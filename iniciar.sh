#!/bin/sh
# ============================================================
#  INICIAR - Abre el Disenador de Muebles en tu navegador.
#  En Mac/Linux: doble clic (o ejecutar ./iniciar.sh).
# ============================================================
DIR="$(cd "$(dirname "$0")" && pwd)"
ARCHIVO="$DIR/DISENADOR_MUEBLES.html"

if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$ARCHIVO"
elif command -v open >/dev/null 2>&1; then
  open "$ARCHIVO"
else
  echo "Abri manualmente el archivo DISENADOR_MUEBLES.html en tu navegador."
fi
