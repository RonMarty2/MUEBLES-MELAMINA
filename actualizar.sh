#!/bin/sh
# ============================================================
#  ACTUALIZAR - Descarga la ultima version del disenador.
#  En Mac/Linux: doble clic (o ejecutar ./actualizar.sh).
#  Necesita Git instalado.
# ============================================================
cd "$(dirname "$0")" || exit 1
echo "Buscando actualizaciones..."
echo ""
git pull
echo ""
echo "Listo. Ya tenes la ultima version."
